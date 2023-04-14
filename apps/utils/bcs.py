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
from django.utils.functional import cached_property
from kubernetes import client as k8s_client
from kubernetes.client import V1ContainerImage
from kubernetes.dynamic import client as dynamic_client
from kubernetes.dynamic.exceptions import ResourceNotFoundError, NotFoundError

from apps.utils.log import logger
from config.domains import BCS_APIGATEWAY_ROOT


# patch for k8s CoreV1Api list_node API
# error: v1_container_image: ValueError: Invalid value for names, must not be None
# details: https://github.com/kubernetes-client/python/issues/895
# patch start
def _v1_container_image_names(self, names):
    self._names = names


V1ContainerImage.names = V1ContainerImage.names.setter(_v1_container_image_names)
# patch end


class Bcs:
    API_KEY_TYPE = "authorization"
    API_KEY_PREFIX = "Bearer"
    API_KEY_CONTENT = settings.BCS_API_GATEWAY_TOKEN
    SERVER_ADDRESS_PATH = "clusters"
    BKLOG_CONFIG_NAMESPACE = "default"
    BKLOG_CONFIG_GROUP = "bk.tencent.com"
    BKLOG_CONFIG_VERSION = settings.BKLOG_CONFIG_VERSION
    BKLOG_CONFIG_API_VERSION = settings.BKLOG_CONFIG_API_VERSION
    BKLOG_CONFIG_KIND = settings.BKLOG_CONFIG_KIND
    BKLOG_CONFIG_PLURAL = "bklogconfigs"
    BCS_CLUSTER_NAME_KEY = "bk_bcs_cluster_id"

    def __init__(self, cluster_id: str):
        self._cluster_id = cluster_id

    @property
    def k8s_config(self):
        bcs_apigateway_host = settings.BCS_APIGATEWAY_HOST if settings.IS_K8S_DEPLOY_MODE else BCS_APIGATEWAY_ROOT
        return k8s_client.Configuration(
            host=f"{bcs_apigateway_host}{self.SERVER_ADDRESS_PATH}/{self._cluster_id}",
            api_key={self.API_KEY_TYPE: self.API_KEY_CONTENT},
            api_key_prefix={self.API_KEY_TYPE: self.API_KEY_PREFIX},
        )

    @cached_property
    def k8s_client(self):
        return k8s_client.ApiClient(self.k8s_config)

    @cached_property
    def dynamic_client(self):
        return dynamic_client.DynamicClient(self.k8s_client)

    @cached_property
    def api_instance_core_v1(self):
        return k8s_client.CoreV1Api(self.k8s_client)

    @cached_property
    def api_instance_apps_v1(self):
        return k8s_client.AppsV1Api(self.k8s_client)

    @cached_property
    def api_instance_batch_v1(self):
        return k8s_client.BatchV1Api(self.k8s_client)

    @cached_property
    def crd_api(self):
        return k8s_client.CustomObjectsApi(self.k8s_client)

    def save_bklog_config(self, bklog_config_name: str, bklog_config: dict, labels=None):
        # 补充bcs cluster id
        ext_meta = bklog_config.get("extMeta", {})
        ext_meta[self.BCS_CLUSTER_NAME_KEY] = self._cluster_id
        bklog_config["extMeta"] = ext_meta
        resource_body = {
            "apiVersion": self.BKLOG_CONFIG_API_VERSION,
            "kind": self.BKLOG_CONFIG_KIND,
            "metadata": {
                "name": bklog_config_name,
                "namespace": self.BKLOG_CONFIG_NAMESPACE,
                "labels": {"app.kubernetes.io/managed-by": "bk-log", **(labels if labels else {})},
            },
            #  https://github.com/TencentBlueKing/bk-log-sidecar/blob/master/api/v1alpha1/bklogconfig_types.go
            "spec": bklog_config,
        }
        self.ensure_resource(
            bklog_config_name,
            resource_body,
            self.BKLOG_CONFIG_API_VERSION,
            self.BKLOG_CONFIG_KIND,
            self.BKLOG_CONFIG_NAMESPACE,
        )

    def delete_bklog_config(self, *bklog_config_names: str):
        for bklog_config_name in bklog_config_names:
            try:
                self.crd_api.delete_namespaced_custom_object(
                    self.BKLOG_CONFIG_GROUP,
                    self.BKLOG_CONFIG_VERSION,
                    self.BKLOG_CONFIG_NAMESPACE,
                    self.BKLOG_CONFIG_PLURAL,
                    bklog_config_name,
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"delete bklog config crd [{bklog_config_name}] error => {e}")

    def list_bklog_config(self):
        return self.crd_api.list_namespaced_custom_object(
            self.BKLOG_CONFIG_GROUP, self.BKLOG_CONFIG_VERSION, self.BKLOG_CONFIG_NAMESPACE, self.BKLOG_CONFIG_PLURAL
        )

    def ensure_resource(self, resource_name: str, resource_body: dict, api_version: str, kind: str, namespace=None):
        try:

            d_client = self.dynamic_client
            resource = d_client.resources.get(api_version=api_version, kind=kind)
        except ResourceNotFoundError:
            # 如果找不到crd，则直接退出
            logger.info(f"{api_version}/{kind} resource crd not found in k8s cluster, will not create any resource")
            raise

        try:
            action = "update"
            # 检查是否已存在,存在则更新
            data = d_client.get(resource=resource, name=resource_name, namespace=namespace)
            resource_body["metadata"]["resourceVersion"] = data["metadata"]["resourceVersion"]
            d_client.replace(resource=resource, body=resource_body)
        except NotFoundError:
            # 不存在则新增
            action = "create"
            d_client.create(resource, body=resource_body, namespace=namespace)

        logger.info("[%s] datasource [%s]", action, resource_name)
