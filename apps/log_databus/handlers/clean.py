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
from apps.log_databus.constants import AsyncStatus
from apps.log_databus.exceptions import CleanTemplateNotExistException, CleanTemplateRepeatException
from apps.log_databus.models import CleanTemplate, BKDataClean
from apps.log_databus.tasks.bkdata import sync_clean
from apps.log_databus.utils.bkdata_clean import BKDataCleanUtils
from apps.models import model_to_dict
from apps.utils.log import logger


class CleanHandler(object):
    def __init__(self, collector_config_id):
        self.collector_config_id = collector_config_id

    def refresh(self, raw_data_id, bk_biz_id):
        bkdata_clean_utils = BKDataCleanUtils(raw_data_id=raw_data_id)
        bkdata_clean_utils.update_or_create_clean(collector_config_id=self.collector_config_id, bk_biz_id=bk_biz_id)
        result_table_names = BKDataClean.objects.filter(raw_data_id=raw_data_id).values_list(
            "result_table_name", flat=True
        )
        if not result_table_names:
            return []
        return result_table_names

    @classmethod
    def sync(cls, bk_biz_id: int, polling: bool):
        """
        to sync clean from bkdata and to create or delete log_index_set
        @param bk_biz_id int biz_id
        @param polling bool is polling request or not
        """
        lock_able = BKDataCleanUtils.lock_sync_clean(bk_biz_id=bk_biz_id)
        if lock_able and polling:
            BKDataCleanUtils.unlock_sync_clean(bk_biz_id=bk_biz_id)
            return AsyncStatus.DONE
        if lock_able and not polling:
            sync_clean.delay(bk_biz_id=bk_biz_id)
        return AsyncStatus.RUNNING


class CleanTemplateHandler(object):
    def __init__(self, clean_template_id=None):
        self.clean_template_id = clean_template_id
        self.data = None
        if clean_template_id:
            try:
                self.data = CleanTemplate.objects.get(clean_template_id=self.clean_template_id)
            except CleanTemplate.DoesNotExist:
                raise CleanTemplateNotExistException(
                    CleanTemplateNotExistException.MESSAGE.format(clean_template_id=clean_template_id)
                )

    def retrieve(self):
        return model_to_dict(self.data)

    def create_or_update(self, params: dict):
        model_fields = {
            "name": params["name"],
            "clean_type": params["clean_type"],
            "etl_params": params["etl_params"],
            "etl_fields": params["etl_fields"],
            "bk_biz_id": params["bk_biz_id"],
        }
        if self._check_clean_template_exist(name=model_fields["name"], bk_biz_id=model_fields["bk_biz_id"]):
            raise CleanTemplateRepeatException(
                CleanTemplateRepeatException.MESSAGE.format(
                    bk_biz_id=model_fields["bk_biz_id"], name=model_fields["name"]
                )
            )
        if not self.data:
            clean_template = CleanTemplate.objects.create(**model_fields)
            logger.info("create clean template {}".format(clean_template.clean_template_id))
            return model_to_dict(clean_template)

        for key, value in model_fields.items():
            setattr(self.data, key, value)
        self.data.save()
        logger.info("update clean template {}".format(self.data.clean_template_id))
        return model_to_dict(self.data)

    def destroy(self):
        clean_template_id = self.data.clean_template_id
        self.data.delete()
        logger.info("delete clean template {}".format(clean_template_id))
        return clean_template_id

    def _check_clean_template_exist(self, name: str, bk_biz_id: int):
        """
        judge the same bk_biz_id and same name clean_template exist
        """
        qs = CleanTemplate.objects.filter(name=name, bk_biz_id=bk_biz_id)
        if self.data:
            qs = qs.exclude(clean_template_id=self.clean_template_id)
        return qs.exists()
