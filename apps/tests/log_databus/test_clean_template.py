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
from django.test import TestCase

from apps.log_databus.exceptions import CleanTemplateRepeatException, CleanTemplateNotExistException
from apps.log_databus.handlers.clean import CleanTemplateHandler
from apps.tests.log_databus.test_clean import TestClean

CREATE_PARAMS = {
    "name": "test",
    "clean_type": "bk_log_text",
    "etl_params": {"retain_original_text": True, "separator": " "},
    "etl_fields": [
        {
            "field_name": "user",
            "alias_name": "",
            "field_type": "long",
            "description": "字段描述",
            "is_analyzed": True,
            "is_dimension": True,
            "is_time": True,
            "is_delete": True,
        }
    ],
    "bk_biz_id": 706,
}


class TestCleanTemplate(TestCase):
    def test_create(self):
        create_result = self._test_create()
        self.assertEqual(create_result["name"], CREATE_PARAMS["name"])
        self.assertEqual(create_result["clean_type"], CREATE_PARAMS["clean_type"])
        self.assertEqual(create_result["etl_params"], CREATE_PARAMS["etl_params"])
        self.assertEqual(create_result["etl_fields"], CREATE_PARAMS["etl_fields"])
        self.assertEqual(create_result["bk_biz_id"], CREATE_PARAMS["bk_biz_id"])

    def test_create_failed(self):
        TestClean._init_project_info()
        self._test_create()
        with self.assertRaises(CleanTemplateRepeatException) as context:
            CleanTemplateHandler().create_or_update(params=CREATE_PARAMS)
        self.assertTrue("该业务 [706]test 已存在该模板test" in str(context.exception))

    def test_update(self):
        create_result = self._test_create()
        create_result["clean_type"] = "bk_log_json"
        create_result["etl_fields"] = [
            {
                "field_name": "test1",
                "alias_name": "",
                "field_type": "long",
                "description": "字段描述",
                "is_analyzed": True,
                "is_dimension": True,
                "is_time": True,
                "is_delete": True,
            }
        ]
        create_result["etl_params"] = {"retain_original_text": False, "separator": " "}
        update_result = CleanTemplateHandler(clean_template_id=create_result["clean_template_id"]).create_or_update(
            params=create_result
        )
        self.assertEqual(update_result["name"], create_result["name"])
        self.assertEqual(update_result["clean_type"], create_result["clean_type"])
        self.assertEqual(update_result["etl_params"], create_result["etl_params"])
        self.assertEqual(update_result["etl_fields"], create_result["etl_fields"])
        self.assertEqual(update_result["bk_biz_id"], create_result["bk_biz_id"])

    def test_retrieve(self):
        create_result = self._test_create()
        retrieve_result = CleanTemplateHandler(clean_template_id=create_result["clean_template_id"]).retrieve()
        self.assertEqual(retrieve_result["name"], create_result["name"])
        self.assertEqual(retrieve_result["clean_type"], create_result["clean_type"])
        self.assertEqual(retrieve_result["etl_params"], create_result["etl_params"])
        self.assertEqual(retrieve_result["etl_fields"], create_result["etl_fields"])
        self.assertEqual(retrieve_result["bk_biz_id"], create_result["bk_biz_id"])

    def test_destroy(self):
        create_result = self._test_create()
        destroy_result = CleanTemplateHandler(clean_template_id=create_result["clean_template_id"]).destroy()
        self.assertEqual(destroy_result, create_result["clean_template_id"])

    def test_CleanTemplateNotExistException(self):
        with self.assertRaises(CleanTemplateNotExistException) as context:
            CleanTemplateHandler(1)
        self.assertTrue("清洗模板1不存在" in str(context.exception))

    @classmethod
    def _test_create(cls):
        clean_template = CleanTemplateHandler()
        create_result = clean_template.create_or_update(params=CREATE_PARAMS)
        return create_result
