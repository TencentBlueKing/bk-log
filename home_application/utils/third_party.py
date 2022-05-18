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
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
import logging

import settings

from apps.api import (
    BkItsmApi,
    CCApi,
    JobApi,
    NodeApi,
    BKLoginApi,
    IAMApi,
    MonitorApi,
    BkDataDatabusApi,
)

from apps.utils.local import activate_request
from apps.utils.thread import generate_request
from apps.exceptions import ApiResultError

from home_application.constants import (
    DEFAULT_SYSTEM_ID,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_BK_DATA_ID,
)

try:
    from blueapps.utils.esbclient import get_client_by_user
except Exception:  # pylint: disable=broad-except
    pass

logger = logging.getLogger()


class ThirdParty(object):
    @staticmethod
    def call_api(module: str) -> bool:
        try:
            kwargs = THIRD_PARTY_CHECK_API[module].get("kwargs", {})
            _ = THIRD_PARTY_CHECK_API[module]["method"](kwargs)
            return True
        except ApiResultError:
            return True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to check {module}, err: {e}")
        return False

    @staticmethod
    def check_paas() -> bool:
        if settings.IS_K8S_DEPLOY_MODE:
            activate_request(generate_request())
            from apps.api import BKPAASApi

            try:
                _ = BKPAASApi.get_app_info()
                return True
            except ApiResultError:
                return True
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"failed to check paas, err: {e}")
        else:
            try:
                client = get_client_by_user(user_or_username=settings.SYSTEM_USE_API_ACCOUNT)
                _ = client.bk_paas.get_app_info()
                return True
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"failed to check paas, err: {e}")

        return False


THIRD_PARTY_CHECK_API = {
    "cc": {"method": CCApi.get_app_list},
    "itsm": {"method": BkItsmApi.get_services},
    "job": {"method": JobApi.get_public_script_list, "kwargs": {"bk_biz_id": settings.BLUEKING_BK_BIZ_ID}},
    "bk_user": {
        "method": BKLoginApi.get_user,
    },
    "nodeman": {
        "method": NodeApi.get_subscription_task_status,
        "kwargs": {"subscription_id": DEFAULT_SUBSCRIPTION_ID},
    },
    "iam": {"method": IAMApi.share_system_info, "kwargs": {"system_id": DEFAULT_SYSTEM_ID}},
    "monitor": {
        "method": MonitorApi.search_alarm_strategy_v3,
        "kwargs": {
            "page": DEFAULT_PAGE,
            "page_size": DEFAULT_PAGE_SIZE,
            "bk_biz_id": settings.BLUEKING_BK_BIZ_ID,
        },
    },
    "bk_data": {"method": BkDataDatabusApi.get_cleans, "kwargs": {"raw_data_id": DEFAULT_BK_DATA_ID}},
}
