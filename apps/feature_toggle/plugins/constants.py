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

# 创建bkdata data_id 特性开关
FEATURE_BKDATA_DATAID = "feature_bkdata_dataid"

# 是否开启ITSM特性开关
FEATURE_COLLECTOR_ITSM = "collect_itsm"
ITSM_SERVICE_ID = "itsm_service_id"
SCENARIO_BKDATA = "scenario_bkdata"
# 是否使用数据平台超级token
BKDATA_SUPER_TOKEN = "bkdata_super_token"
# AIOPS相关配置
BKDATA_CLUSTERING_TOGGLE = "bkdata_aiops_toggle"
# es相关配置
BKLOG_ES_CONFIG = "bklog_es_config"
# 新人指引相关配置
USER_GUIDE_CONFIG = "user_guide_config"
# 采集下发的时候，是否自动安装采集器
IS_AUTO_DEPLOY_PLUGIN = "is_auto_deploy_plugin"
BCS_COLLECTOR = "bcs_collector"
BCS_DEPLOYMENT_TYPE = "bcs_deployment_type"
CHECK_COLLECTOR_CUSTOM_CONFIG = "check_collector_custom_config"
