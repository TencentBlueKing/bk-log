# -*- coding: utf-8 -*-
import time
import logging
import json

from bk_monitor.api.http import http_get, http_post
from bk_monitor.exceptions import MonitorReportResultException
from bk_monitor.constants import ErrorEnum

logger = logging.getLogger("bk_monitor")


class Client(object):
    """api请求client"""

    def __init__(self, bk_app_code, bk_app_secret, bk_username, monitor_host=None, report_host=None):
        self._bk_app_code = bk_app_code
        self._bk_app_secret = bk_app_secret
        self._bk_username = bk_username
        self._operator = bk_username
        self._monitor_host = monitor_host
        self._report_host = report_host

    def _call_esb_api(self, http_func, path, data, timeout=None):
        headers = {}
        data.update(
            {
                "bk_app_code": self._bk_app_code,
                "bk_app_secret": self._bk_app_secret,
                "bk_username": self._bk_username,
                "operator": self._operator,
            }
        )
        return self._call_api(http_func, self._monitor_host, path, data, headers, timeout=timeout)

    def _call_api(self, http_func, host, path, data, headers, timeout=None):
        url = "{host}{path}".format(host=host, path=path)

        begin = time.time()

        _data = http_func(url, data, headers=headers, timeout=timeout)

        logger.debug("do http request: method=`%s`, url=`%s`, data=`%s`", http_func.__name__, url, json.dumps(data))
        logger.info(
            "http request took %s ms, method=`%s`, url=`%s`", int((time.time() - begin) * 1000), http_func.__name__, url
        )

        if not _data.get("result"):
            raise MonitorReportResultException(
                ErrorEnum.REQUEST_RESPONSE_CODE_ERROR, _data.get("message", "monitor api fail")
            )
        _d = _data.get("data")

        return _d

    def get_data_id(self, data):
        path = "metadata_get_data_id/"
        return self._call_esb_api(http_get, path, data)

    def create_data_id(self, data):
        path = "metadata_create_data_id/"
        return self._call_esb_api(http_post, path, data)

    def modify_data_id(self, data):
        path = "metadata_modify_data_id/"
        return self._call_esb_api(http_post, path, data)

    def create_event_group(self, data):
        path = "metadata_create_event_group/"
        return self._call_esb_api(http_post, path, data)

    def create_time_series_group(self, data):
        path = "metadata_create_time_series_group/"
        return self._call_esb_api(http_post, path, data)

    def custom_report(self, data):
        path = "v2/push/"
        return self._call_api(http_post, self._report_host, path, data, {}, timeout=None)

    def save_alarm_strategy(self, data):
        path = "save_alarm_strategy/"
        return self._call_esb_api(http_post, path, data)

    def delete_alarm_strategy(self, data):
        path = "delete_alarm_strategy/"
        return self._call_esb_api(http_post, path, data)

    def delete_notice_group(self, data):
        path = "delete_notice_group/"
        return self._call_esb_api(http_post, path, data)

    def save_notice_group(self, data):
        path = "save_notice_group/"
        return self._call_esb_api(http_post, path, data)

    def get_ts_data(self, data):
        path = "get_ts_data/"
        return self._call_esb_api(http_post, path, data)

    def unify_query(self, data):
        path = "time_series/unify_query/"
        return self._call_esb_api(http_post, path, data)
