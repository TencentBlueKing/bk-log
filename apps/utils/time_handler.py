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
"""
时间处理模块
"""
import datetime  # noqa
import time  # noqa
import pytz  # noqa

import arrow  # noqa
from django.conf import settings  # noqa
from django.utils import timezone  # noqa
from rest_framework import serializers  # noqa

# 默认时间戳乘数
DEFAULT_MULTIPLICATOR = 1
# dtEventTimeStamp时间戳乘数
DTEVENTTIMESTAMP_MULTIPLICATOR = 1000
# INFLUXDB时间戳乘数
INFLUXDB_MULTIPLICATOR = 1000000000

# 一周时间
WEEK_DELTA_TIME = 7 * 24 * 60 * 60
DAY = 86400

SHOW_TZ = False
FMT_LENGTH = None if SHOW_TZ else 16


def timeformat_to_timestamp(timeformat, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    时间格式 -> 时间戳
    :param timeformat:
    :param time_multiplicator: 时间倍数
    :return:
    """
    if not timeformat:
        return None
    if type(timeformat) in [str]:
        # 时间字符串转时间戳
        timestamp = int(time.mktime(time.strptime(timeformat, "%Y-%m-%d %H:%M:%S")))
    else:
        # type(timeformat) is datetime
        # datetime 转时间戳
        timestamp = int(timeformat.strftime("%s"))
    return int(timestamp * time_multiplicator)


def timestamp_to_timeformat(timestamp, time_multiplicator=DEFAULT_MULTIPLICATOR):
    timestamp = int(timestamp / time_multiplicator)
    timestamp = time.localtime(timestamp)
    timeformat = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)
    tzformat = api_time_local(timeformat, get_dataapi_tz())
    return tzformat


def datetime_to_timestamp(datetime):
    time_str = str(datetime.astimezone(pytz.timezone(get_dataapi_tz())))[:19]
    # time_str = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return timeformat_to_timestamp(time_str)


def timestamp_to_datetime(from_timestamp, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    timestamp -> aware datetime
    """
    utc_tz = pytz.timezone("UTC")
    utc_dt = utc_tz.localize(datetime.datetime.utcfromtimestamp(int(from_timestamp) / time_multiplicator))
    return utc_dt


def generate_influxdb_time_range(start_timestamp, end_timestamp):
    """
    生成influxdb需要的时间段
    """
    if end_timestamp > time.time():
        end_timestamp = time.time()
    if start_timestamp < time.time() - DAY * 30:
        start_timestamp = time.time() - DAY * 30
    return int(start_timestamp) * INFLUXDB_MULTIPLICATOR, int(end_timestamp) * INFLUXDB_MULTIPLICATOR


def time_format(l_time, is_tz=False):
    """
    把时间戳列表根据时间间隔转为转为可读的时间格式
    @param {datetime} l_time 时间戳列表
    @param {Boolean} is_tz 是否显示时区
    """
    if l_time:
        difference = l_time[-1] - l_time[0]
        count = len(l_time)
        if count > 1:
            frequency = difference / (count - 1)
            if difference < DAY and frequency < DAY:
                start = 11
                end = None if is_tz else FMT_LENGTH
            elif frequency < DAY <= difference:
                start = 5
                end = None if is_tz else FMT_LENGTH
            elif difference >= DAY and frequency >= DAY:
                start = 5
                end = 10
            else:
                start = None
                end = None if is_tz else FMT_LENGTH
            formated_time = [timestamp_to_timeformat(t)[start:end] for t in l_time]
        else:
            formated_time = [timestamp_to_timeformat(l_time[0])]
    else:
        formated_time = []
    return formated_time


def format_datetime(o_datetime):
    """
    格式化日志对象展示格式

    @param {datetime} o_dateitime
    """
    return o_datetime.strftime("%Y-%m-%d %H:%M:%S%z")


def get_dataapi_tz():
    """
    获取当前dataapi系统的时区
    """
    return settings.DATAAPI_TIME_ZONE


def get_delta_time():
    """
    获取app时间与dataapi时间差
    """
    sys_offset = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime("%z")
    dataapi_offset = datetime.datetime.now(pytz.timezone(settings.DATAAPI_TIME_ZONE)).strftime("%z")
    return (int(dataapi_offset) - int(sys_offset)) / 100 * 3600


def get_pizza_timestamp():
    return time.time() + get_delta_time()


def get_active_timezone_offset():
    """
    获取当前用户时区偏移量
    """
    tz = str(timezone.get_current_timezone())
    offset = datetime.datetime.now(pytz.timezone(tz)).strftime("%z")
    return offset


def strftime_local(aware_time, fmt="%Y-%m-%d %H:%M:%S"):
    """
    格式化aware_time为本地时间
    """
    if not aware_time:
        # 当时间字段允许为NULL时，直接返回None
        return None
    if timezone.is_aware(aware_time):
        # translate to time in local timezone
        aware_time = timezone.localtime(aware_time)
    return aware_time.strftime(fmt)


def api_time_local(s_time, from_zone=settings.DATAAPI_TIME_ZONE, fmt="%Y-%m-%d %H:%M:%S"):
    """
    将时间字符串根据源时区转为用户时区
    """
    if s_time is None:
        return None
    s_time = datetime.datetime.strptime(s_time, fmt)
    local = pytz.timezone(from_zone)
    s_time = local.localize(s_time)
    return strftime_local(s_time)


def localtime_to_timezone(d_time, to_zone):
    """
    将时间字符串根据源时区转为用户时区
    @param {datetime} d_time 时间
    @param {String} to_zone 时区
    """
    zone = pytz.timezone(to_zone)
    return d_time.astimezone(zone)


class SelfDRFDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None
        return strftime_local(value)


class AfterRequest(object):
    def __init__(self, time_fields=None, time_format="%Y-%m-%d %H:%M:%S"):
        if time_fields is None:
            time_fields = []
        self.time_fields = time_fields
        self.time_format = time_format
        self.from_zone = settings.DATAAPI_TIME_ZONE

    def easy_dict(self, response_result):
        data = response_result["data"]
        if data is None:
            return response_result
        for field in self.time_fields:
            try:
                data[field] = api_time_local(data[field], self.from_zone, fmt=self.time_format)
            except KeyError:
                continue
        return response_result

    def easy_list(self, response_result):
        data = response_result["data"]
        self._easy_list(data)
        return response_result

    def easy_list_from_dict_results(self, response_result):
        """
        从字典字段 results 中获取列表，再进行替换，这里需要兼容接口是否进行分页操作，主要提供给 DRF 接口使用
        """
        if type(response_result["data"]) is list:
            self._easy_list(response_result["data"])
        else:
            self._easy_list(response_result["data"]["results"])
        return response_result

    def after_list_deploy_info(self, response_result):
        """
        定制化回调 - 调用 Flow.list_deploy_info 获取最近部署历史，需要处理时间字段
        """
        self.time_fields = ["created_at"]
        self.easy_list_from_dict_results(response_result)

        if type(response_result["data"]) is list:
            data = response_result["data"]
        else:
            data = response_result["data"]["results"]

        for _d in data:
            logs = _d["logs"]
            for _l in logs:
                _l["time"] = api_time_local(_l["time"], self.from_zone, fmt=self.time_format)

        return response_result

    def after_get_latest_deploy_info(self, response_result):
        """
        定制化回调 - 调用 Flow.get_latest_deploy_info 获取最近部署历史，需要处理时间字段
        """
        self.time_fields = ["created_at"]
        self.easy_dict(response_result)

        if response_result["data"] is None:
            return response_result

        logs = response_result["data"]["logs"]
        for _l in logs:
            _l["time"] = api_time_local(_l["time"], self.from_zone, fmt=self.time_format)

        return response_result

    def _easy_list(self, data):
        """
        从定义的时间字段中，把内容替换掉
        """
        for _d in data:
            for field in self.time_fields:
                try:
                    _d[field] = api_time_local(_d[field], self.from_zone, fmt=self.time_format)
                except KeyError:
                    continue


def time_to_string(t):
    """
    传入一个标准时间，返回其字符串形式
    :param t: 时间
    :return: 时间字符串
    """
    return t.strftime("%Y-%m-%d %H:%M:%S")


def date_to_string(d):
    """
    传入一个标准日期，返回其字符串形式
    :param d: 日期
    :return: 日期字符串
    """
    return d.strftime("%Y-%m-%d")


def string_to_time(t_str):
    """
    传入一个字符串，返回其标准时间格式
    :param t_str: 时间字符串
    :return: 时间
    """
    return datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")


def string_to_date(d_str):
    """
    传入一个字符串，返回其标准日期格式
    :param d_str: 日期字符串
    :return: 日期
    """
    return datetime.datetime.strptime(d_str, "%Y-%m-%d")


def generate_time_range(time_range, start_time, end_time, local_time_zone):
    """
    生成起止时间
    """
    if time_range == "customized":
        _start_time, _end_time = _customize_time_range(start_time, end_time, local_time_zone)
    elif time_range == "5m":
        _start_time = arrow.now(local_time_zone).shift(minutes=-5)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "15m":
        _start_time = arrow.now(local_time_zone).shift(minutes=-15)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "30m":
        _start_time = arrow.now(local_time_zone).shift(minutes=-30)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "1h":
        _start_time = arrow.now(local_time_zone).shift(hours=-1)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "4h":
        _start_time = arrow.now(local_time_zone).shift(hours=-4)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "12h":
        _start_time = arrow.now(local_time_zone).shift(hours=-12)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "1d":
        _start_time = arrow.now(local_time_zone).shift(days=-1)
        _end_time = arrow.now(local_time_zone)
    elif time_range == "36m":
        _start_time = arrow.now(local_time_zone).shift(months=-36)
        _end_time = arrow.now(local_time_zone)
    else:
        _start_time, _end_time = _customize_time_range(start_time, end_time, local_time_zone)
    return _start_time, _end_time


def _customize_time_range(start_time, end_time, local_time_zone):
    """
    自定义时间
    """
    # 尝试还原HTML空格转义
    if isinstance(start_time, str):
        start_time = start_time.replace("&nbsp;", " ")
    if isinstance(end_time, str):
        end_time = end_time.replace("&nbsp;", " ")

    if start_time:
        _start_time = arrow.get(start_time, tzinfo=local_time_zone)
    else:
        _start_time = arrow.now(local_time_zone).shift(minutes=-15)
    # end time
    if end_time:
        _end_time = arrow.get(end_time, tzinfo=local_time_zone)
    else:
        _end_time = arrow.now(local_time_zone)

    return _start_time, _end_time


def format_user_time_zone(user_datetime, time_zone):
    """
    将返回时间格式化为用户对应时区
    @param user_datetime {datetime} 具体时间
    @param time_zone {string} 时区
    """
    return arrow.get(user_datetime).to(time_zone).strftime(settings.BKDATA_DATETIME_FORMAT)
