# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
import math

from django.conf import settings
from django.db import transaction
from rest_framework.reverse import reverse

from apps.api import BkItsmApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import FEATURE_COLLECTOR_ITSM, ITSM_SERVICE_ID
from apps.utils.log import logger
from apps.log_databus.constants import CollectItsmStatus
from apps.log_databus.exceptions import CollectItsmTokenIllega, CollectItsmHasApply, CollectItsmNotExists
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.models import CollectorConfig
from apps.log_search.constants import CollectorScenarioEnum
from apps.models import model_to_dict
from apps.utils.local import get_request, get_request_username


class ItsmHandler(object):
    ITSM_TRUE = "true"
    ITSM_FALSE = "false"

    @transaction.atomic
    def apply_itsm_ticket(self, collect_config_id, params: dict):
        collect_config = CollectorConfig.objects.get(collector_config_id=collect_config_id)
        params.update(
            {
                "title": collect_config.generate_itsm_title(),
                "bk_biz_id": collect_config.bk_biz_id,
                "collector_detail": self._generate_collector_detail_itsm_form(collect_config),
                "capacity_formula": self._generate_capacity_formula(params),
            }
        )
        if not collect_config.can_apply_itsm():
            raise CollectItsmHasApply
        sn = self.create_ticket(params)
        collect_config.set_itsm_applying(sn)
        return self.collect_itsm_status(collect_config_id)

    def collect_itsm_status(self, collect_config_id):
        collect_config = CollectorConfig.objects.get(collector_config_id=collect_config_id)
        ret = {
            "collect_itsm_status": collect_config.itsm_ticket_status,
            "collect_itsm_status_display": CollectItsmStatus.get_choice_label(collect_config.itsm_ticket_status),
            "ticket_url": settings.ITSM_LOG_DISPLAY_ROLE,
        }
        if collect_config.has_apply_itsm():
            ticket_info = self.ticket_status(collect_config.itsm_ticket_sn)
            ticket_detail_info = self.ticket_info(collect_config.itsm_ticket_sn)
            apply_info = {field.get("key"): field.get("value") for field in ticket_detail_info.get("fields", [])}
            ret.update({"ticket_url": ticket_info["ticket_url"]})
            ret.update(apply_info)
        return ret

    def get_log_itsm_service_id(self) -> int:
        params = {"display_role": settings.ITSM_LOG_DISPLAY_ROLE, "display_type": "API", "no_request": True}
        result = BkItsmApi.get_services(params)
        if not result:
            raise CollectItsmNotExists
        return result[0].get("id")

    def create_ticket(self, apply_params):
        params = {
            "service_id": FeatureToggleObject.toggle(FEATURE_COLLECTOR_ITSM).feature_config.get(
                ITSM_SERVICE_ID, settings.COLLECTOR_ITSM_SERVICE_ID
            ),
            "creator": get_request_username(),
            "fields": [{"key": param_key, "value": param_value} for param_key, param_value in apply_params.items()],
            "meta": {"callback_url": self._generate_callback_url()},
        }
        result = BkItsmApi.create_ticket(params)
        return result["sn"]

    def ticket_info(self, sn: str):
        return BkItsmApi.get_ticket_info({"sn": sn})

    def ticket_status(self, sn: str):
        return BkItsmApi.get_ticket_status({"sn": sn})

    def _generate_callback_url(self) -> str:
        return reverse("collect_itsm_cb-collect-itsm-callback", request=get_request())

    def verify_token(self, token: str, raise_exception=True) -> bool:
        result = BkItsmApi.token_verify({"token": token})
        if not result["is_passed"]:
            if raise_exception:
                raise CollectItsmTokenIllega
        return result["is_passed"]

    def clean_failed_ticket_callback(self):
        fail_ticket_sn_list = BkItsmApi.callback_failed_ticket()
        current_ticket_sn_list = CollectorConfig.objects.filter(
            itsm_ticket_status=CollectItsmStatus.APPLYING.value
        ).values_list("itsm_ticket_sn", flat=True)
        bklog_itsm_sn_list = set(fail_ticket_sn_list) | set(current_ticket_sn_list)
        if not bklog_itsm_sn_list:
            return
        ticket_approval_result = BkItsmApi.ticket_approval_result({"sn": list(bklog_itsm_sn_list)})
        for ticket_info in ticket_approval_result:
            try:
                self.update_collect_itsm_status(ticket_info)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"clean failed itsm cb fail => [{e}]")
                continue

    def update_collect_itsm_status(self, ticket_info: dict):
        collector_process = CollectorConfig.objects.get(itsm_ticket_sn=ticket_info.get("sn"))
        ticket_detail_info = self.ticket_info(ticket_info.get("sn"))
        collector_process.set_can_use_es_cluster(self._get_can_use_es_cluster(ticket_detail_info))
        if self._ticket_is_finish(ticket_info):
            if self._ticket_approve_result(ticket_detail_info):
                collector_process.set_itsm_success()
                self._create_task(collector_process.collector_config_id)
                return
            collector_process.set_itsm_fail()

    def _get_can_use_es_cluster(self, ticket_info: dict):
        return self._get_detail_ticket_info_field("can_use_independent_es_cluster", ticket_info)

    def _create_task(self, collect_id):
        collect_handler = CollectorHandler(collector_config_id=collect_id)

        if not collect_handler.data.is_active:
            collect_handler.data.is_active = True
            collect_handler.data.save()
        data = model_to_dict(collect_handler.data)
        if data["itsm_ticket_status"] not in [CollectItsmStatus.SUCCESS_APPLY.value]:
            return
        collect_handler.update_or_create(data)

    def _ticket_is_finish(self, ticket_info: dict):
        return "RUNNING" != ticket_info["current_status"]

    def _ticket_approve_result(self, ticket_info: dict):
        value = self._get_detail_ticket_info_field("approval_result", ticket_info)
        return value == self.ITSM_TRUE

    def _get_detail_ticket_info_field(self, key: str, ticket_info: dict):
        for field in ticket_info.get("fields", []):
            if field.get("key") == key:
                return field.get("value")
        return ""

    def _generate_collector_detail(self, collector: CollectorConfig):
        form_value = [
            {"label": "名称：", "scheme": "base_text_scheme", "value": collector.collector_config_name},
            {"label": "备注说明：", "scheme": "base_text_scheme", "value": collector.description},
            {
                "label": "日志类型：",
                "scheme": "base_text_scheme",
                "value": str(CollectorScenarioEnum.get_choice_label(collector.collector_scenario_id)),
            },
            {"label": "日志字符集：", "scheme": "base_text_scheme", "value": collector.data_encoding},
        ]
        paths = [
            {"label": f"日志路径-{index}：", "scheme": "base_text_scheme", "value": path}
            for index, path in enumerate(collector.params.get("paths", []), 1)
        ]
        form_value.extend(paths)
        return form_value

    def _generate_collector_detail_itsm_form(
        self, collector: CollectorConfig
    ):  # pylint: disable=function-name-too-long
        form_detail = {
            "config": {},
            "schemes": {
                "base_text_scheme": {
                    "type": "text",
                    "attrs": {"styles": {"label": ["border"], "value": ["highlight", "border"]}},
                }
            },
            "form_data": [
                {
                    "label": "",
                    "scheme": "base_text_scheme",
                    "value": collector.collector_config_name,
                    "children": self._generate_collector_detail(collector),
                }
            ],
        }
        return json.dumps(form_detail)

    def _generate_capacity_formula(self, params):
        single_host_log_volume = params["single_host_log_volume"]
        expect_host_size = params["expect_host_size"]
        log_keep_days = params["log_keep_days"]
        formula_result = self._capacity_formula(single_host_log_volume, expect_host_size, log_keep_days)
        form_detail = {
            "config": {},
            "schemes": {
                "base_text_scheme": {
                    "type": "text",
                    "attrs": {"styles": {"label": ["border"], "value": ["highlight", "border"]}},
                }
            },
            "form_data": [
                {"label": "", "scheme": "base_text_scheme", "value": "单机日志增量 * 主机数量 * 存储转化率 * 分片数 * （日志保留天数 + 1）"},
                {
                    "label": "",
                    "scheme": "base_text_scheme",
                    "value": f"{single_host_log_volume} "
                    f"* {expect_host_size} "
                    f"* 1.5 * 2 * "
                    f"{log_keep_days + 1}  "
                    f"= {formula_result}(GB)",
                },
            ],
        }
        return json.dumps(form_detail)

    def _capacity_formula(self, single_host_log_volume, expect_host_size, log_keep_days):
        return math.ceil(single_host_log_volume * expect_host_size * (log_keep_days + 1) * 1.5 * 2)
