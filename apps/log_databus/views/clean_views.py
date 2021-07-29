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
from apps.generic import ModelViewSet

# from apps.log_databus.models import BKDataClean, CleanTemplate
from apps.utils.drf import detail_route


class CleanViewSet(ModelViewSet):
    """
    清洗列表
    """

    lookup_field = "collector_config_id"
    # model = BKDataClean

    def get_permissions(self):
        pass

    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/clean/?page=$page&pagesize=$pagesize&bk_biz_id=$bk_biz_id 1_清洗-列表
        @apiName list_clean
        @apiGroup 22_clean
        @apiDescription 清洗列表，获取入库列表及基础清洗合集
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} page 页数
        @apiParam {Int} pagesize 每页数量
        @apiSuccess {Int} count 总数
        @apiSuccess {Int} total_page 总页数
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "count": 10,
                "total_page": 1,
                "results": [
                {
                    "collector_config_id":1,
                    "collector_config_name":"test",
                    "bk_data_id": 10,
                    "result_table_id":"test",
                    "updated_by":"test",
                    "updated_at":"2021-07-24 17:42:32+0800"
                }
            ]
            },
            "result": true
        }
        """
        pass

    @detail_route(methods=["GET"])
    def refresh(self, request, *args, collector_config_id=None, **kwarg):
        """
        @api {get} /databus/cleans/$collector_config_id/?bk_biz_id=$bk_biz_id&bk_data_id=$bk_data_id 2_高级清洗-刷新
        @apiName refresh_clean
        @apiGroup 22_clean
        @apiDescription 刷新高级清洗
        @apiParam {Int} bk_biz_id 业务id
        @apiParam {Int} bk_data_id 数据源id
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "result": True,
                "log_set_index_id": 1
            },
            "result": true
        }
        @apiSuccessExample {json} 成功返回(未找到对应记录)
        {
            "message": "",
            "code": 0,
            "data": {
                "result": False,
                "log_set_index_id": null,
            },
            "result": true
        }
        """


class CleanTemplateViewSet(ModelViewSet):
    """
    清洗模板
    """

    lookup_field = "clean_template_id"
    # model = CleanTemplate

    def get_permissions(self):
        pass

    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/clean_template/?page=$page&pagesize=$pagesize&bk_biz_id=$bk_biz_id 1_清洗模板-列表
        @apiName list_clean_template
        @apiGroup 23_clean_template
        @apiDescription 获取清洗模板列表
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 成功返回
            {
                "message":"",
                "code":0,
                "data":{
                    "count":10,
                    "total_page":1,
                    "results":[
                        {
                            "clean_template_id": 1,
                            "clean_type":"bk_log_text",
                            "etl_params":{
                                "retain_original_text":true,
                                "separator":" "
                            },
                            "etl_fields":[
                                {
                                    "field_name":"tag_number",
                                    "type":"float",
                                    "tag":"dimension",
                                    "default_value":null,
                                    "is_config_by_user":true,
                                    "description":"",
                                    "unit":"",
                                    "alias_name":"",
                                    "option":{
                                        "time_zone":"",
                                        "time_format":"",
                                        "field_index":1,
                                        "es_type":"integer",
                                        "real_path":"bk_separator_object.tag_number"
                                    },
                                    "is_built_in":false,
                                    "is_time":false,
                                    "field_type":"int",
                                    "is_analyzed":false,
                                    "is_delete":false,
                                    "is_dimension":true,
                                    "_nums":1,
                                    "field_index":1,
                                    "value":"14836"
                                }
                            ]
                        }
                    ]
                },
                "result":true
            }
        """
        pass

    def retrieve(self, request, *args, clean_template_id=None, **kwargs):
        """
        @api {get} /databus/clean_template/$clean_template_id/?bk_biz_id=$bk_biz_id 2_清洗模板-详情
        @apiName retrieve_clean_template
        @apiGroup 23_clean_template
        @apiDescription 清洗模板详情
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 成功返回
        {
            "message":"",
            "code":0,
            "data":{
                "clean_template_id":1,
                "clean_type":"bk_log_text",
                "etl_params":{
                    "retain_original_text":true,
                    "separator":" "
                },
                "etl_fields":[
                    {
                        "field_name":"tag_number",
                        "type":"float",
                        "tag":"dimension",
                        "default_value":null,
                        "is_config_by_user":true,
                        "description":"",
                        "unit":"",
                        "alias_name":"",
                        "option":{
                            "time_zone":"",
                            "time_format":"",
                            "field_index":1,
                            "es_type":"integer",
                            "real_path":"bk_separator_object.tag_number"
                        },
                        "is_built_in":false,
                        "is_time":false,
                        "field_type":"int",
                        "is_analyzed":false,
                        "is_delete":false,
                        "is_dimension":true,
                        "_nums":1,
                        "field_index":1,
                        "value":"14836"
                    }
                ]
            },
            "result":true
        }
        """
        pass

    def update(self, request, *args, clean_template_id=None, **kwargs):
        """
        @api {put} /databus/clean_template/$clean_template_id/ 4_清洗模板-更新
        @apiName update_clean_template
        @apiGroup 23_clean_template
        @apiDescription 更新清洗模板
        @apiParamExample {json} 成功请求
        {
            "clean_type":"bk_log_text",
            "etl_params":{
                "retain_original_text":true,
                "separator":" "
            },
            "etl_fields":[
                {
                    "field_name":"tag_number",
                    "type":"float",
                    "tag":"dimension",
                    "default_value":null,
                    "is_config_by_user":true,
                    "description":"",
                    "unit":"",
                    "alias_name":"",
                    "option":{
                        "time_zone":"",
                        "time_format":"",
                        "field_index":1,
                        "es_type":"integer",
                        "real_path":"bk_separator_object.tag_number"
                    },
                    "is_built_in":false,
                    "is_time":false,
                    "field_type":"int",
                    "is_analyzed":false,
                    "is_delete":false,
                    "is_dimension":true,
                    "_nums":1,
                    "field_index":1,
                    "value":"14836"
                }
            ]
        }
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": True,
            "result": true
        }
        """
        pass

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/clean_template/ 3_清洗模板-新建
        @apiName create_clean_template
        @apiGroup 23_clean_template
        @apiDescription 新建清洗模板
        @apiParamExample {json} 成功请求
        {
            "clean_type":"bk_log_text",
            "etl_params":{
                "retain_original_text":true,
                "separator":" "
            },
            "etl_fields":[
                {
                    "field_name":"tag_number",
                    "type":"float",
                    "tag":"dimension",
                    "default_value":null,
                    "is_config_by_user":true,
                    "description":"",
                    "unit":"",
                    "alias_name":"",
                    "option":{
                        "time_zone":"",
                        "time_format":"",
                        "field_index":1,
                        "es_type":"integer",
                        "real_path":"bk_separator_object.tag_number"
                    },
                    "is_built_in":false,
                    "is_time":false,
                    "field_type":"int",
                    "is_analyzed":false,
                    "is_delete":false,
                    "is_dimension":true,
                    "_nums":1,
                    "field_index":1,
                    "value":"14836"
                }
            ]
        }
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": True,
            "result": true
        }
        """
        pass

    def destroy(self, request, *args, **kwargs):
        """
        @api {delete} /databus/clean_template/$clean_template_id/ 5_清洗模板-删除
        @apiName destry_clean_template
        @apiGroup 23_clean_template
        @apiDescription 删除清洗模板
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": True,
            "result": true
        }
        """
        pass
