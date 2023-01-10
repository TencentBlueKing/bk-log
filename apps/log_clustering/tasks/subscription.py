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
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlencode

import pytz
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from jinja2 import Environment, FileSystemLoader

from apps.api import CmsiApi
from apps.log_clustering.constants import (
    FrequencyTypeEnum,
    LogColShowTypeEnum,
    SubscriptionTypeEnum,
    YearOnYearChangeEnum,
)
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.handlers.pattern import PatternHandler
from apps.log_clustering.models import ClusteringConfig, ClusteringSubscription
from apps.log_clustering.utils.wechat_robot import WeChatRobot
from apps.log_measure.utils.metric import MetricUtils
from apps.log_search.exceptions import IndexSetDoseNotExistException
from apps.log_search.handlers.search.search_handlers_esquery import (
    SearchHandler as SearchHandlerEsquery,
)
from apps.log_search.models import LogIndexSet
from bkm_space import api

robot_api = WeChatRobot()


def validate_end_time(freq: dict, end_time: datetime):
    if end_time.isoweekday() in freq["week_list"]:
        return end_time
    end_time = end_time + timedelta(days=1)
    return validate_end_time(freq, end_time)


def get_start_and_end_time(freq: dict, last_run_at: datetime, time_zone: pytz.timezone) -> dict:
    """
    return: {
        "is_run_time": 是否运行时间,
        "start_time": 开始时间,
        "end_time": 结束时间,
        "interval": 间隔,
    }
    # 频率&发送范围存储格式示例
    {
        "type": 1,
        "day_list": [],
        "run_time": "10",
        "week_list": [1, 2, 3, 4, 5, 6, 7],
        "data_range": {
            "number": 30,
            "time_level": "minutes"
        }
    }
    """
    result = {
        "is_run_time": False,
        "start_time": None,
        "end_time": None,
        "interval": None,
        "last_run_at": None,
    }

    time_fmt = "%Y-%m-%d %H:%M:%S"
    now = timezone.now().astimezone(time_zone)

    if not last_run_at:
        if freq["type"] in [FrequencyTypeEnum.DAY.value, FrequencyTypeEnum.WEEK.value]:
            run_time = freq["run_time"].split(":")
            end_time = datetime(now.year, now.month, now.day, tzinfo=time_zone) + timedelta(
                hours=int(run_time[0]), minutes=int(run_time[1]), seconds=int(run_time[2])
            )
            end_time = end_time.astimezone(time_zone)
            end_time = validate_end_time(freq, end_time)
        else:
            run_time = int(freq["run_time"])
            if now.minute % run_time != 0:
                m_offset = run_time - now.minute % run_time
                if now.minute + m_offset == 60:
                    end_time = now + timedelta(hours=1, seconds=-now.second, microseconds=-now.microsecond)
                else:
                    end_time = now + timedelta(minutes=m_offset, seconds=-now.second, microseconds=-now.microsecond)
            else:
                end_time = now + timedelta(seconds=-now.second, microseconds=now.microsecond)
    else:
        last_run_at = last_run_at.astimezone(time_zone)
        if freq["type"] in [FrequencyTypeEnum.DAY.value, FrequencyTypeEnum.WEEK.value]:
            end_time = last_run_at + timedelta(days=1)
            end_time = validate_end_time(freq, end_time)
        else:
            end_time = last_run_at + timedelta(minutes=int(freq["run_time"]))

    if freq.get("data_range"):
        # 按发送频率
        start_time = end_time - timedelta(**{freq["data_range"]["time_level"]: freq["data_range"]["number"]})
    elif last_run_at:
        # 按周期频率
        start_time = timezone.localtime(last_run_at)
    else:
        # 首次执行
        start_time = end_time - timedelta(minutes=30)

    interval = end_time - start_time
    if interval.days:
        interval = _("{}天").format(interval.days)
    else:
        hour = interval.seconds / 60 / 60
        interval = _("{}小时").format(int(hour)) if hour > 1 else _("{}分钟").format(int(hour * 60))

    if not now >= end_time:
        return result

    result["is_run_time"] = True
    result["start_time"] = start_time.strftime(time_fmt)
    result["end_time"] = end_time.strftime(time_fmt)
    result["interval"] = interval
    result["last_run_at"] = end_time

    return result


def query_logs(config: ClusteringSubscription, time_config: dict, pattern: dict, clustering_field) -> dict:
    addition = config.addition if config.addition else []
    params = {
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
        "keyword": config.query_string or "*",
        "addition": addition.append(
            {"field": f"__dist_{pattern['pattern_level']}", "operator": "is", "value": pattern["signature"]}
        ),
        "host_scopes": config.host_scopes if config.host_scopes else {},
        "size": 1,
    }

    result = SearchHandlerEsquery(config.index_set_id, params).search()
    if not result.get("list", []):
        return {}

    return {pattern["signature"]: result["list"][0][clustering_field]}


def query_patterns(config: ClusteringSubscription, time_config: dict):
    params = {
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
        "keyword": config.query_string or "*",
        "addition": config.addition if config.addition else [],
        "host_scopes": config.host_scopes if config.host_scopes else {},
        "size": 10000,
        "pattern_level": config.pattern_level,
        "show_new_pattern": config.is_show_new_pattern,
        "year_on_year_hour": config.year_on_year_hour,
        "group_by": config.group_by if config.group_by else [],
    }

    result = PatternHandler(config.index_set_id, params).pattern_search()

    return result


def clean_pattern(config: ClusteringSubscription, time_config: dict, data: list, clustering_config) -> dict:
    patterns = []
    new_patterns = []
    for _data in data:
        # 按同比进行过滤
        if (
            config.year_on_year_change == YearOnYearChangeEnum.RISE.value
            and _data["year_on_year_percentage"] < 0
            or config.year_on_year_change == YearOnYearChangeEnum.DECLINE.value
            and _data["year_on_year_percentage"] > 0
        ):
            continue

        # 区分是否为新增
        if _data["is_new_class"]:
            new_patterns.append(_data)
        else:
            patterns.append(_data)

    # 截取显示长度

    pattern_count = [p["count"] for p in patterns]
    new_pattern_count = [p["count"] for p in new_patterns]
    result = {
        "patterns": {
            "pattern_count": len(patterns),
            "log_count": sum(pattern_count) if pattern_count else 0,
            "data": patterns[: config.log_display_count],
            "max_num": max(new_pattern_count) if new_pattern_count else 0,
            "percentage": round(max([p["percentage"] for p in patterns]), 2),
        },
        "new_patterns": {
            "pattern_count": len(new_patterns),
            "log_count": sum(new_pattern_count) if pattern_count else 0,
            "data": new_patterns[: config.log_display_count],
            "max_num": max(new_pattern_count) if new_pattern_count else 0,
            "percentage": round(max([p["percentage"] for p in new_patterns]), 2),
        },
    }

    if config.log_col_show_type == LogColShowTypeEnum.LOG.value and (patterns or new_patterns):
        # 查询pattern对应的log, 将pattern替换为log
        log_map = {}
        with ThreadPoolExecutor() as ex:
            tasks = [
                ex.submit(query_logs, config, time_config, pattern, clustering_config.clustering_fields)
                for pattern in result["new_patterns"]["data"] + result["patterns"]["data"]
            ]
            for feature in as_completed(tasks):
                log_map.update(feature.result())

        # 将pattern替换为log
        for _data in result["patterns"]["data"]:
            _data["pattern"] = log_map.get(_data["signature"]) or _data["pattern"]

        for _data in result["new_patterns"]["data"]:
            _data["pattern"] = log_map.get(_data["signature"]) or _data["pattern"]

    return result


def generate_log_search_url(config: ClusteringSubscription, time_config: dict) -> str:
    params = {
        "spaceUid": config.space_uid,
        "keyword": config.query_string or "*",
        "addition": config.addition if config.addition else [],
        "host_scopes": config.host_scopes if config.host_scopes else {},
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
    }

    url = f"{settings.LOG_SEARCH_SAAS_URL}/#/retrieve/{config.index_set_id}?{urlencode(params)}"
    return url


def render_template(template: str, params: dict) -> str:
    loader = FileSystemLoader(searchpath=os.path.join(settings.BASE_DIR, "templates", "clustering_subscription"))
    env = Environment(loader=loader)
    template = env.get_template(template)
    content = template.render(**params)
    return content


def send_wechat(params: dict, receivers: list):
    tpl_name = "clustering_wechat_en.md" if params["language"] == "en" else "clustering_wechat.md"
    content = render_template(tpl_name, params)
    send_params = {
        "chatid": "|".join([receiver["id"] for receiver in receivers]),
        "msgtype": "markdown",
        "markdown": {"content": content},
    }
    robot_api.send_msg(send_params)
    ClusteringSubscription.objects.filter(id=params["id"]).update(last_run_at=params["time_config"]["last_run_at"])


def send_mail(params: dict, receivers: list):
    tpl_name = "clustering_mail_en.html" if params["language"] == "en" else "clustering_mail.html"
    content = render_template(tpl_name, params)
    send_params = {
        "receivers": ",".join([r["id"] for r in receivers]),
        "content": content,
        "title": params["title"],
    }
    CmsiApi.send_mail(send_params)
    ClusteringSubscription.objects.filter(id=params["id"]).update(last_run_at=params["time_config"]["last_run_at"])


def send(config: ClusteringSubscription, time_config: dict, bk_biz_name: str, language: str):
    result = query_patterns(config, time_config)

    clustering_config = ClusteringConfig.objects.filter(index_set_id=config.index_set_id).first()
    if not clustering_config:
        raise ClusteringConfigNotExistException()

    all_patterns = clean_pattern(config, time_config, result, clustering_config)

    log_index_set = LogIndexSet.objects.filter(index_set_id=config.index_set_id).first()
    if not log_index_set:
        raise IndexSetDoseNotExistException()

    params = {
        "subscription_id": config.id,
        "language": language,
        "title": config.title,
        "time_config": time_config,
        "bk_biz_name": bk_biz_name,
        "index_set_name": log_index_set.index_set_name,
        "log_search_url": generate_log_search_url(config, time_config),
        "table_headers": [_("数据指纹"), _("数量"), _("占比"), _("同比数量"), "Pattern"],
        "all_patterns": all_patterns,
        "log_col_show_type": config.log_col_show_type.capitalize(),
        "group_by": config.group_by,
        "percentage": round(max([i["percentage"] for i in result]), 2),
        "clustering_fields": clustering_config.clustering_fields,
    }

    if config.subscription_type == SubscriptionTypeEnum.WECHAT.value:
        if all_patterns["new_patterns"]:
            send_wechat(params, config.receivers)

    elif config.subscription_type == SubscriptionTypeEnum.EMAIL.value:
        if all_patterns["patterns"] or all_patterns["new_patterns"]:
            send_mail(params, config.receivers)


@periodic_task(run_every=crontab(minute="*/1"))
def send_subscription_task():
    subscription_configs = ClusteringSubscription.objects.all()

    with ThreadPoolExecutor() as ex:
        for config in subscription_configs:
            # 查询空间信息
            space = api.SpaceApi.get_space_detail(space_uid=config.space_uid)

            time_zone = pytz.timezone(space.properties.get("time_zone", "") or settings.TIME_ZONE)
            time_config = get_start_and_end_time(config.frequency, config.last_run_at, time_zone)
            is_run_time = time_config["is_run_time"]

            # 未到运行时间
            if not is_run_time:
                continue

            language = space.properties.get("language", "") or translation.get_language()
            bk_biz_name = MetricUtils.get_instance().get_biz_name(space.bk_biz_id)
            ex.submit(send, config, time_config, bk_biz_name, language)
