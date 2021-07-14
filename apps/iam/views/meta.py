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
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.iam import Permission, ActionEnum, ResourceEnum


class MetaViewSet(APIViewSet):

    # 权限豁免
    permission_classes = ()

    @action(methods=["GET"], detail=False)
    def get_system_info(self, request, *args, **kwargs):
        """
        @api {get} /iam/meta/get_system_info/ 01_获取系统信息
        @apiName get_system_info
        @apiGroup 99_IAM
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":{
            },
            "result":true
        }
        """
        result = Permission().get_system_info()
        return Response(result)

    @action(methods=["POST"], detail=False)
    def check_allowed(self, request, *args, **kwargs):
        """
        @api {post} /iam/meta/check_allowed/ 02_检查当前用户对该动作是否有权限
        @apiName check_allowed
        @apiGroup 99_IAM
        @apiParam {Array(String)}  action_ids 动作ID列表
        @apiParam {Array(Object)}  resources 资源列表
        @apiParam {string}  resources.type 资源类型
        @apiParam {string}  resources.id 资源ID
        @apiParamExample {Json} 请求参数:
        {
            action_ids: [
                "view_business",
                "create_collection"
            ],
            resources: [
                {
                    "type": "business",
                    "id": "2"
                }
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data": [
                {
                    "action_id": "view_business",
                    "is_allowed": true,
                },
                {
                    "action_id": "view_business",
                    "is_allowed": false,
                }
            ],
            "result":true
        }
        """
        action_ids = request.data.get("action_ids", [])
        resources = request.data.get("resources", [])

        result = []
        client = Permission()
        resources = client.batch_make_resource(resources)
        for action_id in action_ids:
            is_allowed = client.is_allowed(action_id, resources)
            result.append({"action_id": action_id, "is_allowed": is_allowed})

        return Response(result)

    @action(methods=["POST"], detail=False)
    def get_apply_data(self, request, *args, **kwargs):
        """
        @api {post} /iam/meta/get_apply_data/ 03_获取权限申请数据
        @apiName get_apply_data
        @apiGroup 99_IAM
        @apiParam {Array(String)}  action_ids 动作ID列表
        @apiParam {Array(Object)}  resources 资源列表
        @apiParam {string}  resources.type 资源类型
        @apiParam {string}  resources.id 资源ID
        @apiParamExample {Json} 请求参数:
        {
            action_ids: [
                "view_business",
                "create_collection"
            ],
            resources: [
                {
                    "type": "business",
                    "id": "2"
                }
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
          "result": true,
          "data": {
            "apply_data": {
              "system_id": "bk_log_search",
              "system_name": "日志平台",
              "actions": [
                {
                  "id": "view_business",
                  "name": "业务访问",
                  "related_resource_types": [
                    {
                      "system_id": "bk_cmdb",
                      "system_name": "配置平台",
                      "type": "business",
                      "type_name": "业务",
                      "instances": [
                        [
                          {
                            "type": "business",
                            "type_name": "业务",
                            "id": "2",
                            "name": "蓝鲸"
                          }
                        ]
                      ]
                    }
                  ]
                },
                {
                  "id": "create_collection",
                  "name": "采集新建",
                  "related_resource_types": [
                    {
                      "system_id": "bk_cmdb",
                      "system_name": "配置平台",
                      "type": "business",
                      "type_name": "业务",
                      "instances": [
                        [
                          {
                            "type": "business",
                            "type_name": "业务",
                            "id": "2",
                            "name": "蓝鲸"
                          }
                        ]
                      ]
                    }
                  ]
                }
              ]
            },
            "apply_url": "http://xxx.com:80/o/bk_iam/apply-custom-perm"
          },
          "code": 0,
          "message": ""
        }
        """
        action_ids = request.data.get("action_ids", [])
        resources = request.data.get("resources", [])
        client = Permission()
        resources = client.batch_make_resource(resources)
        apply_data, apply_url = client.get_apply_data(action_ids, resources)
        return Response({"apply_data": apply_data, "apply_url": apply_url})

    @action(methods=["GET"], detail=False)
    def test(self, request, *args, **kwargs):
        client = Permission("xxx")
        client.is_allowed(ActionEnum.VIEW_BUSINESS, [ResourceEnum.BUSINESS.create_instance(2)], raise_exception=True)
