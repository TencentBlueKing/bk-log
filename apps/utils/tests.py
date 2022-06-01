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
import json
import os

import requests
import urllib3
from django.conf import settings
from django.http import SimpleCookie
from django.test import Client, TestCase

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JSON_CONTENT = "application/json"
PAAS_USERNAME = os.environ.get("PAAS_ADMIN_USER")
PAAS_PASSWORD = os.environ.get("PAAS_ADMIN_PASS")


class MyTestClient(Client):
    def __init__(self):
        super(MyTestClient, self).__init__()
        self.check_environ()
        login_cookies = mock_login()
        simple_cookies = SimpleCookie()
        for key, value in login_cookies.items():
            simple_cookies[key] = value
        self.cookies = simple_cookies

    @staticmethod
    def check_environ():
        to_check_var = ["APP_CODE", "APP_TOKEN", "BK_PAAS_HOST", "PAAS_ADMIN_USER", "PAAS_ADMIN_PASS"]
        for var in to_check_var:
            if not os.environ.get(var):
                raise NotImplementedError(f"环境变量{var}未设置")

    @staticmethod
    def assert_response(response):
        """
        断言请求是否正确返回
        :param response:
        :return: 返回数据中的data字段
        """
        assert response.status_code == 200
        json_response = json.loads(response.content)
        try:
            assert json_response.get("result")
        except AssertionError as e:
            print("[RESPONSE ERROR]:%s" % response.content)
            raise e

        return json_response["data"]

    @staticmethod
    def transform_data(data, content_type=JSON_CONTENT):
        """
        根据content_type转化请求参数
        :param data:
        :param content_type:
        :return:
        """
        if content_type == JSON_CONTENT:
            data = json.dumps(data)
        return data

    def get(self, path, data=None, secure=True, **extra):
        response = super(MyTestClient, self).get(path, data=data, secure=secure, **extra)

        return self.assert_response(response)

    def post(self, path, data=None, content_type=JSON_CONTENT, follow=False, secure=True, **extra):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).post(
            path, data=data, content_type=JSON_CONTENT, follow=follow, secure=secure, **extra
        )
        return self.assert_response(response)

    def patch(self, path, data=None, content_type=JSON_CONTENT, follow=False, secure=True, **extra):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).patch(
            path, data=data, content_type=JSON_CONTENT, follow=follow, secure=secure, **extra
        )
        return self.assert_response(response)

    def put(self, path, data=None, content_type=JSON_CONTENT, follow=False, secure=True, **extra):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).put(
            path, data=data, content_type=JSON_CONTENT, follow=follow, secure=secure, **extra
        )
        return self.assert_response(response)

    def delete(self, path, data=None, content_type=JSON_CONTENT, follow=False, secure=True, **extra):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).delete(
            path, data=data, content_type=JSON_CONTENT, follow=follow, secure=secure, **extra
        )
        return self.assert_response(response)


def mock_login():
    """
    模拟登录
    """
    # 获取csrftoken
    login_url = f"{settings.BK_PAAS_HOST}/login/"
    session = requests.session()
    session.verify = False
    res = session.get(url=login_url)
    bklogin_csrftoken = res.cookies["bklogin_csrftoken"]

    # 更新请求头部，发出登录请求
    session.headers.update(
        {"Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": bklogin_csrftoken, "referer": login_url}
    )
    session.post(
        url=login_url,
        data="username={}&password={}&csrfmiddlewaretoken={}".format(PAAS_USERNAME, PAAS_PASSWORD, bklogin_csrftoken),
    )
    return session.cookies


class MyTestCase(TestCase):
    client_class = MyTestClient
    # client = MyTestClient()
    client = Client()
    recursion_type = [dict, list]
    string_type = [str]

    def runTest(self):  # pylint: disable=invalid-name
        print(self)

    def assertDataStructure(
        self, result_data, expected_data, value_eq=False, list_exempt=False
    ):  # pylint: disable=invalid-name
        """
        将数据的结构以及类型进行断言验证
        :param result_data: 后台返回的数据
        :param expected_data: 希望得到的数据
        :param value_eq: 是否对比值相等
        :param list_exempt: 是否豁免列表的比对
        """
        result_data_type = type(result_data)

        # 判断类型是否一致
        self.assertEqual(result_data_type, type(expected_data))

        # 判断类型是否为字典
        if result_data_type is dict:
            # 將传入的预给定信息，将键值分别取出
            for expected_key, expected_value in expected_data.items():
                # 判断键是否存在
                self.assertTrue(expected_key in result_data.keys(), msg="key:[%s] is expected" % expected_key)

                result_value = result_data[expected_key]

                # 返回None时忽略 @todo一刀切需要调整
                if expected_value is None or result_value is None:
                    return

                # 取出后台返回的数据result_data，判断是否与给定的类型相符
                result_value_type = type(result_value)
                expected_value_type = type(expected_value)
                self.assertEqual(
                    result_value_type,
                    expected_value_type,
                    msg="type error! Expect [%s] to be [%s], but got [%s]"
                    % (expected_key, expected_value_type, result_value_type),
                )

                if value_eq:
                    self.assertEqual(result_value, expected_value)

                # 判断该类型是否为字典或者列表
                if expected_value_type in self.recursion_type:
                    # 进行递归
                    self.assertDataStructure(result_value, expected_value, value_eq=value_eq, list_exempt=list_exempt)

        #  判断类型是否为列表
        elif result_data_type is list:
            # 列表不为空且不进行列表比对的豁免
            if result_data and expected_data and not list_exempt:

                if value_eq:
                    # 比对列表内的值是否相等
                    self.assertListEqual(result_data, expected_data)
                else:
                    # 否则认为列表里所有元素的数据结构都是一致的
                    _expected_data = expected_data[0]
                    for _data in result_data:
                        if type(_data) in self.recursion_type:
                            self.assertDataStructure(_data, _expected_data, value_eq=value_eq, list_exempt=list_exempt)

        # 判断值是否一致
        elif value_eq:
            self.assertEqual(result_data, expected_data)

    def assertListEqual(self, list1, list2, msg=None, is_sort=False):  # pylint: disable=invalid-name
        if is_sort:
            list1.sort()
            list2.sort()
        super(MyTestCase, self).assertListEqual(list1, list2, msg=msg)
