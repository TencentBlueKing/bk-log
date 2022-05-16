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

from django.conf import settings
from kubernetes import client as k8s_client
from kubernetes.dynamic import client as dynamic_client
from kubernetes.dynamic.exceptions import ResourceNotFoundError, NotFoundError

from apps.utils.log import logger
from config.domains import BCS_APIGATEWAY_ROOT


class Bcs:
    API_KEY_TYPE = "authorization"
    API_KEY_PREFIX = "Bearer"
    API_KEY_CONTENT = settings.BCS_API_GATEWAY_TOKEN
    SERVER_ADDRESS_PATH = "clusters"

    def __init__(self, cluster_id: str):
        self._cluster_id = cluster_id

    @property
    def k8s_config(self):
        return k8s_client.Configuration(
            host=f"{BCS_APIGATEWAY_ROOT}/{self.SERVER_ADDRESS_PATH}/{self._cluster_id}",
            api_key={self.API_KEY_TYPE: self.API_KEY_CONTENT},
            api_key_prefix={self.API_KEY_TYPE: self.API_KEY_PREFIX},
        )

    @property
    def k8s_client(self):
        return k8s_client.ApiClient(self.k8s_config)

    @property
    def dynamic_client(self):
        return dynamic_client.DynamicClient(self.k8s_client)

    def ensure_resource(self, resource_name: str, resource_body: dict, api_version: str, kind: str):
        try:
            d_client = self.dynamic_client
            resource = d_client.resources.get(
                api_version=api_version,
                kind=kind,
            )
            action = "update"
            # 检查是否已存在,存在则更新
            data = d_client.get(resource=resource, name=resource_name)
            resource_body["metadata"]["resourceVersion"] = data["metadata"]["resourceVersion"]
            d_client.replace(resource=resource, body=resource_body)
        except NotFoundError:
            # 不存在则新增
            action = "create"
            d_client.create(resource, body=resource_body)
        except ResourceNotFoundError:
            # 如果找不到crd，则直接退出
            logger.debug("dataid resource crd not found in k8s cluster, will not create any dataid resource")
            return False
        except Exception as e:  # pylint: disable=broad-except
            # 异常捕获
            logger.error("unexpected error in ensure resource:{}".format(e))
            return False

        logger.info(
            "[%s] datasource [%s]",
            action,
            resource_name,
        )
        return True
