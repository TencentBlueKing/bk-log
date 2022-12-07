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
import hashlib
import json
import re
import time
from copy import deepcopy
from multiprocessing.pool import ThreadPool
from urllib import parse

from requests import Response
from retrying import Retrying, RetryError

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import translation
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from opentelemetry.context import attach, get_current
from requests.exceptions import ReadTimeout

from apps.utils.log import logger
from apps.exceptions import ApiResultError, ApiRequestError, PermissionError
from apps.utils.local import get_request_id, get_request, get_request_username, activate_request
from apps.utils.time_handler import timestamp_to_datetime
from apps.api.exception import DataAPIException
from apps.api.modules.utils import add_esb_info_before_request
from apps.utils.function import ignored


def add_common_info_before_request(params):
    """
    统一请求模块必须带上的参数
    """
    if "bk_app_code" not in params:
        params["bk_app_code"] = settings.APP_CODE
    if "bk_app_secret" not in params:
        params["bk_app_secret"] = settings.SECRET_KEY
    if "bk_username" not in params:
        params["bk_username"] = get_request_username()
    return params


class DataResponse(object):
    """response for data api request"""

    def __init__(self, request_response, request_id):
        """
        初始化一个请求结果
        @param request_response: 期待是返回的结果字典
        """
        self.response = request_response
        self.request_id = request_id

    def is_success(self):
        return bool(self.response.get("result", False))

    @property
    def message(self):
        return self.response.get("message", None)

    @property
    def code(self):
        return self.response.get("code", None)

    @property
    def data(self):
        return self.response.get("data", None)

    @property
    def errors(self):
        return self.response.get("errors", None)


class DataApiRetryClass(object):
    def __init__(self, stop_max_attempt_number=1, wait_random_min=0, wait_random_max=1000):
        self.stop_max_attempt_number = stop_max_attempt_number
        self.wait_random_min = wait_random_min
        self.wait_random_max = wait_random_max
        self.fail_exceptions = []
        self.fail_check_functions = []

    def add_exceptions(self, exceptions: list):
        self.fail_exceptions.extend(exceptions)

    def add_fail_check_functions(self, fail_check_functions: list):
        """
        添加检查result是否失败的函数, 参数默认接受result对象
        函数语义为函数结果是否为True, 为False则重试
        eg: fail_check_functions=[
            lambda x: x.json()["result"]
        ],
        可以使用 check_result_is_true 这个默认函数
        eg: fail_check_functions=[check_result_is_true]
        """
        self.fail_check_functions.extend(fail_check_functions)

    @property
    def retry_on_exception(self):
        def wraps(exception):
            for fail_exception in self.fail_exceptions:
                if isinstance(exception, fail_exception):
                    return False
            # retry_on_exception 默认 Retrying.always_reject=True
            return True

        return wraps

    @property
    def retry_on_result(self):
        """result为请求的返回结果"""

        def wraps(result):
            for fail_check_func in self.fail_check_functions:
                # 如果函数判断为: False, 需要重试; True, 不需要重试
                if not fail_check_func(result):
                    return True
            # retry_on_result 默认 Retrying.never_reject=False
            return False

        return wraps

    @staticmethod
    def create_retry_obj(
        exceptions: list = None,
        fail_check_functions: list = None,
        stop_max_attempt_number=1,
        wait_random_min=0,
        wait_random_max=1000,
    ):
        retry_obj = DataApiRetryClass(
            stop_max_attempt_number=stop_max_attempt_number,
            wait_random_min=wait_random_min,
            wait_random_max=wait_random_max,
        )
        if exceptions:
            retry_obj.add_exceptions(exceptions)
        if fail_check_functions:
            retry_obj.add_fail_check_functions(fail_check_functions)
        return retry_obj


def check_result_is_true(result: Response) -> bool:
    """通用的根据result结果重试判断函数"""
    try:
        return result.json()["result"]
    except Exception:
        return False


class DataAPI(object):
    """Single API for DATA"""

    HTTP_STATUS_OK = 200

    def __init__(
        self,
        method,
        url,
        module,
        description="",
        default_return_value=None,
        before_request=None,
        after_request=None,
        max_response_record=5000,
        max_query_params_record=5000,
        method_override=None,
        url_keys=None,
        header_keys=None,
        after_serializer=None,
        cache_time=0,
        default_timeout=60,
        data_api_retry_cls=None,
    ):
        """
        初始化一个请求句柄
        @param {string} method 请求方法, GET or POST，大小写皆可
        @param {string} url 请求地址
        @param {string} module 对应的模块，用于后续查询标记
        @param {string} description 中文描述
        @param {object} default_return_value 默认返回值，在请求失败情形下将返回该值
        @param {function} before_request 请求前的回调
        @param {function} after_request 请求后的回调
        @param {serializer} after_serializer 请求后的清洗
        @param {int} max_response_record 最大记录返回长度，如果为None将记录所有内容
        @param {int} max_query_params_record 最大请求参数记录长度，如果为None将记录所有的内容
        @param {string} method_override 重载请求方法，注入到 header（X-HTTP-METHOD-OVERRIDE）
        @param {array.<string>} url_keys 请求地址中存在未赋值的 KEYS
        @param {int} cache_time 缓存时间
        @param {int} default_timeout 默认超时时间
        @param {DataApiRetryClass} data_api_retry_cls 超时配置
        """
        self.url = url
        self.module = module
        self.method = method
        self.default_return_value = default_return_value

        self.before_request = before_request
        self.after_request = after_request

        self.after_serializer = after_serializer

        self.description = description
        self.max_response_record = max_response_record
        self.max_query_params_record = max_query_params_record

        self.method_override = method_override
        self.url_keys = url_keys
        common_headers = [
            "X-Bk-App-Code",
            "X-Bk-App-Secret",
        ]
        self.header_keys = common_headers
        if header_keys:
            self.header_keys = header_keys + common_headers

        self.cache_time = cache_time
        self.default_timeout = default_timeout
        self.data_api_retry_cls = data_api_retry_cls

    def __call__(
        self,
        params=None,
        files=None,
        raw=False,
        timeout=None,
        raise_exception=True,
        request_cookies=True,
        data_api_retry_cls=None,
    ):
        """
        调用传参

        @param {Boolean} raw 是否返回原始内容
        """
        if params is None:
            params = {}

        timeout = timeout or self.default_timeout

        # 重试操作
        if data_api_retry_cls:
            self.data_api_retry_cls = data_api_retry_cls

        request_id = get_request_id()
        try:
            response = self._send_request(params, timeout, request_id, request_cookies)
            if raw:
                return response.response

            # 统一处理返回内容，根据平台既定规则，断定成功与否
            if raise_exception and not response.is_success():
                raise ApiResultError(
                    self.get_error_message(response.message), code=response.code, errors=response.errors
                )

            return response.data
        except DataAPIException as e:
            raise ApiRequestError(e.error_message, request_id)

    def get_error_message(self, error_message):
        url_path = ""
        with ignored(Exception):
            url_path = parse.urlparse(parse.unquote(self.url)).path

        message = _("[{module}-API]{error_message}").format(module=self.module, error_message=error_message)
        logger.exception(message + f" url => {self.url}")
        if url_path:
            message += f" path => {url_path}"
        return message

    def _send_request(self, params, timeout, request_id, request_cookies):

        # 请求前的参数清洗处理
        if self.before_request is not None:
            params = self.before_request(params)

        params = add_common_info_before_request(params)

        # 是否有默认返回，调试阶段可用
        if self.default_return_value is not None:
            return DataResponse(self.default_return_value, request_id)

        # 缓存
        with ignored(Exception):
            cache_key = self._build_cache_key(params)
            if self.cache_time:
                result = self._get_cache(cache_key)
                if result is not None:
                    # 有缓存时返回
                    return DataResponse(result, request_id)

        response = None
        error_message = ""
        bk_username = ""
        # 发送请求
        # 开始时记录请求时间
        start_time = time.time()
        try:
            try:
                if self.data_api_retry_cls:
                    raw_response = Retrying(
                        stop_max_attempt_number=self.data_api_retry_cls.stop_max_attempt_number,
                        wait_random_min=self.data_api_retry_cls.wait_random_min,
                        wait_random_max=self.data_api_retry_cls.wait_random_max,
                        retry_on_exception=self.data_api_retry_cls.retry_on_exception,
                        retry_on_result=self.data_api_retry_cls.retry_on_result,
                    ).call(self._send, params, timeout, request_id, request_cookies)
                else:
                    raw_response = self._send(params, timeout, request_id, request_cookies)
            except ReadTimeout as e:
                raise DataAPIException(self, self.get_error_message(str(e)))
            except RetryError as e:
                if e.last_attempt.has_exception:
                    raise DataAPIException(self, self.get_error_message(str(e)))
                raw_response = e.last_attempt.value
            except Exception as e:  # pylint: disable=W0703
                raise DataAPIException(self, self.get_error_message(str(e)))

            # http层面的处理结果
            if raw_response.status_code != self.HTTP_STATUS_OK:
                request_response = {
                    "result": False,
                    "message": f"[{raw_response.status_code}]" + (raw_response.text or raw_response.reason),
                    "code": raw_response.status_code,
                }
                response = DataResponse(request_response, request_id)
                raise DataAPIException(self, self.get_error_message(request_response["message"]), response=raw_response)

            # 结果层面的处理结果
            try:
                response_result = raw_response.json()
            except Exception:  # pylint: disable=broad-except
                error_message = "data api response not json format url->[{}] content->[{}]".format(
                    self.url,
                    raw_response.text,
                )
                logger.exception(error_message)

                raise DataAPIException(self, _("返回数据格式不正确，结果格式非json."), response=raw_response)
            else:
                # 只有正常返回才会调用 after_request 进行处理
                if "result" not in response_result:
                    # 说明返回不是蓝鲸标准
                    response_result["result"] = True
                if response_result.get("result"):
                    # 请求完成后的清洗处理
                    if self.after_request is not None:
                        response_result = self.after_request(response_result)

                    if self.after_serializer is not None:
                        serializer = self.after_serializer(data=response_result)
                        serializer.is_valid(raise_exception=True)
                        response_result = serializer.validated_data

                if self.cache_time:
                    self._set_cache(cache_key, response_result)

                response = DataResponse(response_result, request_id)
                return response
        finally:
            # 最后记录时间
            end_time = time.time()
            # 判断是否需要记录,及其最大返回值
            bk_username = params.get("bk_username", "")

            if response is not None:
                response_result = response.is_success()
                response_data = json.dumps(response.data)[: self.max_response_record]

                for _param in settings.SENSITIVE_PARAMS:
                    params.pop(_param, None)

                try:
                    params = json.dumps(params)[: self.max_query_params_record]
                except TypeError:
                    params = ""

                # 防止部分平台不规范接口搞出大新闻
                if response.code is None:
                    response.response["code"] = "00"
                # message不符合规范，不为string的处理
                if type(response.message) not in [str]:
                    response.response["message"] = str(response.message)
                response_code = response.code
            else:
                response_data = ""
                response_code = -1
                response_result = False
            response_message = response.message if response is not None else error_message
            response_errors = response.errors if response is not None else ""

            # 增加流水的记录
            _info = {
                "request_datetime": timestamp_to_datetime(start_time),
                "url": self.url,
                "module": self.module,
                "method": self.method,
                "method_override": self.method_override,
                "query_params": params,
                "response_result": response_result,
                "response_code": response_code,
                "response_data": response_data,
                "response_message": response_message[:1023],
                "response_errors": response_errors,
                "cost_time": (end_time - start_time),
                "request_id": request_id,
                "request_user": bk_username,
            }

            _log = _("[BKLOGAPI] {info}").format(
                info=" && ".join([" {}=>{} ".format(_k, _v) for _k, _v in list(_info.items())])
            )
            if response_result:
                logger.info(_log)
            else:
                logger.exception(_log)

    def _build_cache_key(self, params):
        """
        缓存key的组装方式，保证URL和参数相同的情况下返回是一致的
        :param params:
        :return:
        """
        # 缓存
        cache_str = "url_{url}__params_{params}".format(url=self.build_actual_url(params), params=json.dumps(params))
        hash_md5 = hashlib.new("md5")
        hash_md5.update(cache_str.encode("utf-8"))
        cache_key = hash_md5.hexdigest()
        return cache_key

    def _set_cache(self, cache_key, data):
        """
        获取缓存
        :param cache_key:
        :return:
        """
        cache.set(cache_key, data, self.cache_time)

    def _send(self, params, timeout, request_id, request_cookies):
        """
        发送和接受返回请求的包装
        @param params: 请求的参数,预期是一个字典
        @return: requests response
        """

        # 增加request id
        session = requests.session()
        session.headers.update({"X-DATA-REQUEST-ID": request_id})

        # headers 申明重载请求方法
        if self.method_override is not None:
            session.headers.update({"X-METHOD-OVERRIDE": self.method_override})
            # params['X_HTTP_METHOD_OVERRIDE'] = self.method_override

        session.headers.update({"blueking-language": translation.get_language(), "request-id": get_request_id()})

        if self.header_keys:
            headers = {key: params.get(key) for key in self.header_keys if key in params}
            for key in self.header_keys:
                params.pop(key, None)
            session.headers.update(**headers)

        url = self.build_actual_url(params)

        # 发出请求并返回结果
        query_params = {"bklog_request_id": request_id}
        non_file_data, file_data = self._split_file_data(params)
        if self.method.upper() == "GET":
            params.update(query_params)
            return session.request(method=self.method, url=url, params=params, verify=False, timeout=timeout)
        if self.method.upper() == "DELETE":
            session.headers.update({"Content-Type": "application/json; charset=utf-8"})
            return session.request(
                method=self.method,
                url=url,
                data=json.dumps(non_file_data),
                params=query_params,
                verify=False,
                timeout=timeout,
            )
        if self.method.upper() in ["PUT", "PATCH", "POST"]:
            if not file_data:
                session.headers.update({"Content-Type": "application/json; charset=utf-8"})
                params = json.dumps(non_file_data)
            else:
                params = non_file_data

            if request_cookies:
                local_request = None
                try:
                    local_request = get_request()
                except Exception:  # pylint: disable=broad-except
                    pass

                if local_request and local_request.COOKIES:
                    session.cookies.update(local_request.COOKIES)
            return session.request(
                method=self.method,
                url=url,
                data=params,
                params=query_params,
                files=file_data,
                verify=False,
                timeout=timeout,
            )
        raise ApiRequestError("request method error => [{method}]".format(method=self.method))

    def build_actual_url(self, params):
        if self.url_keys is not None:
            kvs = {_k: params[_k] for _k in self.url_keys}
            url = self.url.format(**kvs)
        else:
            url = self.url
        return url

    @staticmethod
    def _split_file_data(data):
        file_data = {}
        non_file_data = {}
        for k, v in list(data.items()):
            if hasattr(v, "read"):
                # 一般认为含有read属性的为文件类型
                file_data[k] = v
            else:
                non_file_data[k] = v
        return non_file_data, file_data

    @staticmethod
    def _get_cache(cache_key):
        """
        获取缓存
        :param cache_key:
        :return:
        """
        if cache.get(cache_key):
            return cache.get(cache_key)

    def bulk_request(
        self,
        params=None,
        get_data=lambda x: x["info"],
        get_count=lambda x: x["count"],
        limit=settings.BULK_REQUEST_LIMIT,
    ):
        """
        并发请求接口，用于需要分页多次请求的情况
        :param params: 请求参数
        :param get_data: 获取数据函数
        :param get_count: 获取总数函数
        :param limit: 一次请求数量
        :return: 请求结果
        """
        params = params or {}

        # 请求第一次获取总数
        request_params = {"page": {"start": 0, "limit": limit}, "no_request": True}
        request_params.update(params)
        result = self.__call__(request_params)
        count = get_count(result)
        data = get_data(result)
        start = limit

        # 如果第一次没拿完，根据请求总数并发请求
        pool = ThreadPool()
        futures = []
        request = None
        with ignored(Exception):
            request = get_request()
        while start < count:
            request_params = {"page": {"limit": limit, "start": start}, "no_request": True}
            request_params.update(params)
            # request_params["requests"] = get_request()
            futures.append(
                pool.apply_async(
                    self.thread_activate_request,
                    args=(request_params,),
                    kwds={"request": request, "context": get_current()},
                )
            )

            start += limit

        pool.close()
        pool.join()

        # 取值
        for future in futures:
            data.extend(get_data(future.get()))

        return data

    def thread_activate_request(
        self,
        params=None,
        files=None,
        raw=False,
        timeout=None,
        raise_exception=True,
        request_cookies=True,
        request=None,
        context=None,
    ):
        """
        处理并发请求无法activate_request的封装
        """
        if request:
            activate_request(request)
        attach(context)
        return self.__call__(
            params=params,
            files=files,
            raw=raw,
            timeout=timeout,
            raise_exception=raise_exception,
            request_cookies=request_cookies,
        )


DRF_DATAAPI_CONFIG = [
    "description",
    "default_return_value",
    "before_request",
    "after_request",
    "max_response_record",
    "max_query_params_record",
    "default_timeout",
    "custom_headers",
    "output_standard",
    "request_auth",
    "cache_time",
]


class DRFActionAPI(object):
    def __init__(self, detail=True, url_path=None, method=None, **kwargs):
        """
        资源操作申明，类似 DRF 中的 detail_route、list_route，透传 DataAPI 配置
        """
        self.detail = detail
        self.url_path = url_path
        self.method = method

        for k in list(kwargs.keys()):
            if k not in DRF_DATAAPI_CONFIG:
                raise Exception(
                    "Not support {k} config, SUPPORT_DATAAPI_CONFIG:{conf}".format(k=k, conf=DRF_DATAAPI_CONFIG)
                )

        self.dataapi_kwargs = kwargs


class DataDRFAPISet(object):
    """
    For djangorestframework api set in the backend
    """

    BASE_ACTIONS = {
        "list": DRFActionAPI(detail=False, method="get"),
        "create": DRFActionAPI(detail=False, method="post"),
        "update": DRFActionAPI(method="put"),
        "partial_update": DRFActionAPI(method="patch"),
        "delete": DRFActionAPI(method="delete"),
        "retrieve": DRFActionAPI(method="get"),
    }

    def __init__(self, url, module, primary_key, custom_config=None, url_keys=None, **kwargs):
        """
        申明具体某一资源的 restful-api 集合工具，透传 DataAPI 配置

        @param {String} url 资源路径
        @param {String} primary_key 资源ID
        @param {Dict} custom_config 给请求资源增添额外动作，支持定制化配置
            {
                'start': DRFActionAPI(detail=True, method='post')
            }
        @params kwargs 支持 DRF_DATAAPI_CONFIG 定义的配置项，参数说明请求参照 DataAPI
        @paramExample
            DataDRFAPISet(
                url= 'http://example.com/insts/',
                primary_key='inst_id',
                module='meta',
                description='inst操作集合',
                custom_config={
                    'start': {detail=True, 'method': 'post'}
                }
            )
        @returnExample 返回实例具有以下方法
            inst.create          ---- POST {http://example.com/insts/}
            inst.list            ---- GET {http://example.com/insts/}
            inst.retrieve        ---- GET {http://example.com/insts/:inst_id/}
            inst.update          ---- PUT {http://example.com/insts/:inst_id/}
            inst.partial_update  ---- PATCH {http://example.com/insts/:inst_id/}
            inst.start           ---- POST {http://example.com/insts/:inst_id/}start/
        """
        self.url = url
        self.url_keys = url_keys
        self.custom_config = custom_config
        self.module = module
        self.primary_key = primary_key

        for k in list(kwargs.keys()):
            if k not in DRF_DATAAPI_CONFIG:
                raise Exception(
                    "Not support {k} config, SUPPORT_DATAAPI_CONFIG:{conf}".format(k=k, conf=DRF_DATAAPI_CONFIG)
                )

        self.dataapi_kwargs = kwargs

    def to_url(self, action_name, action, is_standard=False):
        target_url_keys = self.url_keys[:] if self.url_keys else []
        if action.detail:
            target_url = "{root_path}{{{pk}}}/".format(root_path=self.url, pk=self.primary_key)
            target_url_keys.append(self.primary_key)
        else:
            target_url = "{root_path}".format(root_path=self.url)

        if not is_standard:
            sub_path = action.url_path if action.url_path else action_name
            target_url += "{sub_path}/".format(sub_path=sub_path)

        return target_url, target_url_keys

    def __getattr__(self, key):
        """
        通过 ins.create 调用DRF方法，会在该函数进行分发
        """
        action, url, url_keys = None, "", []
        if key in self.BASE_ACTIONS:
            action = self.BASE_ACTIONS[key]
            url, url_keys = self.to_url(key, action, is_standard=True)

        if self.custom_config is not None and key in self.custom_config:
            action = self.custom_config[key]
            url, url_keys = self.to_url(key, self.custom_config[key])

        if key in self.custom_config and key in self.BASE_ACTIONS:
            action = self.custom_config[key]
            url, url_keys = self.to_url(key, self.custom_config[key], is_standard=True)

        if action is None:
            raise Exception("请求方法%s不存在" % key)

        method = action.method

        dataapi_kwargs = {
            "method": method,
            "url": url,
            "url_keys": url_keys,
            "module": self.module,
        }
        dataapi_kwargs.update(self.dataapi_kwargs)
        dataapi_kwargs.update(action.dataapi_kwargs)

        return DataAPI(**dataapi_kwargs)


class ProxyDataAPI(object):
    """
    代理DataAPI，会根据settings.RUN_VER到sites.{run_ver}.api.proxy_modules找到对应的api
    """

    def __init__(self, description=""):
        self.description = description


class BaseApi(object):
    """
    api基类，支持ProxyDataAPI代理类API
    """

    def __getattribute__(self, item):
        attr = super(BaseApi, self).__getattribute__(item)
        if isinstance(attr, ProxyDataAPI):
            # 代理类的DataApi，各个版本需要重载有差异的方法

            module_path, module_name = self.__module__.rsplit(".", 1)  # pylint: disable=unused-variable
            class_name = self.__class__.__name__

            module_str = "apps.api.sites.{run_ver}.{mod}.{api}".format(
                run_ver=settings.RUN_VER, mod=module_name, api=class_name
            )
            try:
                mod = import_string(module_str)()
                attr = getattr(mod, item)
            except (ImportError, AttributeError) as e:
                raise NotImplementedError("{}.{} is not implemented. \nerror message: {}".format(module_str, item, e))
        return attr


class PassThroughAPI(DataAPI):
    """
    直接透传API
    """

    def __init__(
        self, module, method, url_prefix, sub_url, supported_api=list()
    ):  # pylint: disable=dangerous-default-value  # noqa
        is_supported = False
        for d_api in supported_api:
            if d_api["method"] == method and re.match(d_api.get("url_regex"), sub_url):
                url = "".join([url_prefix, sub_url])
                api_kwargs = deepcopy(d_api)
                api_kwargs.pop("url_regex")
                api_kwargs.update({"method": method, "url": url, "module": module})
                if "before_request" not in api_kwargs:
                    api_kwargs["before_request"] = add_esb_info_before_request
                super(PassThroughAPI, self).__init__(**api_kwargs)
                is_supported = True
                break
        if not is_supported:
            logger.error("【API ERROR】%s 暂不支持透传" % sub_url)
            raise PermissionError(
                "非法请求，模块【{module}】，方法【{method}】，接口【{sub_url}】".format(module=module, method=method, sub_url=sub_url)
            )


class GrafanaDataAPI(DataAPI):
    def __init__(self, with_org_id=False, *args, **kwargs):
        super(GrafanaDataAPI, self).__init__(*args, **kwargs)
        self.with_org_id = with_org_id

    def __call__(self, params=None, files=None, raw=False, timeout=None, raise_exception=True):
        url = self.build_actual_url(params)

        if isinstance(self.method, tuple):
            method = self.method[0]
        else:
            method = self.method

        requests_params = {
            "method": method,
            "url": url,
            "headers": {"X-WEBAUTH-USER": "admin"},
            "timeout": timeout,
        }

        # 对于非Admin API，通过参数在请求头注入org_id
        if self.with_org_id:
            if "org_id" not in params:
                raise ApiRequestError(_("请求缺少org_id"))

            requests_params["headers"]["X-Grafana-Org-Id"] = str(params["org_id"])
            del params["org_id"]

        if method in ["PUT", "POST", "PATCH"]:
            requests_params["json"] = params
        elif method in ["GET", "HEAD", "DELETE"]:
            requests_params["params"] = params

        r = requests.request(**requests_params)

        result = r.status_code in [200, 204]
        if result:
            data = r.json()
            message = ""
        else:
            data = None
            message = r.json()["message"]

        return {"result": result, "code": r.status_code, "message": message, "data": data}
