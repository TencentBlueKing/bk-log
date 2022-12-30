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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlencode

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils import timezone

from apps.api import CmsiApi
from apps.log_clustering.constants import (
    LogColShowTypeEnum,
    SubscriptionTypeEnum,
    YearOnYearChangeEnum,
)
from apps.log_clustering.handlers.pattern import PatternHandler
from apps.log_clustering.models import ClusteringSubscription
from apps.log_clustering.serializers import PatternSearchSerlaizer
from apps.log_clustering.utils.wechat_robot import WeChatRobot
from apps.log_search.handlers.search.search_handlers_esquery import (
    SearchHandler as SearchHandlerEsquery,
)
from apps.log_search.serializers import SearchAttrSerializer
from apps.utils.drf import custom_params_valid

robot_api = WeChatRobot()


def get_start_and_end_time(freq: dict, last_run_at: datetime) -> dict:
    """
    return: {
        "is_run_time": 是否运行时间,
        "start_time": 开始时间,
        "end_time": 结束时间,
        "interval": 间隔,
    }
    """
    result = {
        "is_run_time": False,
        "start_time": None,
        "end_time": None,
        "interval": None,
    }
    time_fmt = "%Y-%m-%d %H:%M:%S"
    now = datetime.today()

    # 按天, 周
    if freq["type"] in [2, 3]:
        # 未到运行时间
        if now.isoweekday() not in freq["week_list"] or now.time().strftime("%H:%M:%S") != freq["run_time"]:
            return result
        end_time = datetime.strptime(f"{now.year}-{now.month}-{now.day} {freq['run_time']}", time_fmt)
    else:
        # 未到运行时间
        if now.minute % freq["run_time"]["minutes"] != 0:
            return result
        end_time = now.strftime(time_fmt)

    # 按发送频率
    if freq.get("data_range"):
        start_time = end_time - timedelta(**{freq["data_range"]["time_level"]: freq["data_range"]["number"]})
    elif last_run_at:
        start_time = timezone.localtime(last_run_at)
    else:
        start_time = end_time = timedelta(minutes=30)

    interval = end_time - start_time
    if interval.days:
        interval = f"{interval.days}天"
    else:
        hour = interval.seconds / 60 / 60
        interval = f"{int(hour)}小时" if hour > 1 else f"{int(hour * 60)}分钟"

    result["is_run_time"] = True
    result["start_time"] = start_time.strftime(time_fmt)
    result["end_time"] = end_time.strftime(time_fmt)
    result["interval"] = interval

    return result


def query_logs(time_config: dict, index_set_id: int, pattern_level: str, signature: str) -> dict:
    params = {
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
        "addition": [{"field": f"__dist_{pattern_level}", "operator": "is", "value": signature}],
        "size": 1,
    }

    data = custom_params_valid(serializer=SearchAttrSerializer, params=params)
    search_handler = SearchHandlerEsquery(index_set_id, data)
    result = search_handler.search()
    if not result.get("list", []):
        return {}

    return {signature: result["list"][0]["log"]}


def query_patterns(config: ClusteringSubscription, time_config: dict):
    query_params = {
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
        "keyword": "*",
        "size": 10000,
        "pattern_level": config.pattern_level,
        "show_new_pattern": config.is_show_new_pattern,
        "year_on_year_hour": config.year_on_year_hour,
        "group_by": config.group_by or [],
    }

    query_data = custom_params_valid(serializer=PatternSearchSerlaizer, params=query_params)

    result = PatternHandler(config.index_set_id, query_data).pattern_search()

    return result


def clean_pattern(config: ClusteringSubscription, time_config: dict, data: list) -> tuple:
    # 按同比进行过滤
    if config.year_on_year_change == YearOnYearChangeEnum.RISE.value:
        result = [i for i in data if i["year_on_year_percentage"] > 0]
    elif config.year_on_year_change == YearOnYearChangeEnum.DECLINE.value:
        result = [i for i in data if i["year_on_year_percentage"] < 0]
    else:
        result = data

    # 区分是否为新增
    patterns = []
    new_patterns = []
    for _data in result:
        if _data["is_new_class"]:
            new_patterns.append(_data)
        else:
            patterns.append(_data)

    # 截取显示长度
    patterns = patterns[: config.size]
    new_patterns = new_patterns[: config.size]

    if config.log_col_show_type == LogColShowTypeEnum.LOG.value:
        # 查询pattern对应的log, 将pattern替换为log
        log_map = {}
        with ThreadPoolExecutor() as ex:
            tasks = [
                ex.submit(query_logs, time_config, config.index_set_id, p["pattern_level"], p["signature"])
                for p in new_patterns + patterns
            ]
            for feature in as_completed(tasks):
                log_map.update(feature.result())

        # 将pattern替换为log
        for _data in patterns:
            _data["pattern"] = log_map.get(_data["signature"]) or _data["pattern"]
        for _data in new_patterns:
            _data["pattern"] = log_map.get(_data["signature"]) or _data["pattern"]

    return new_patterns, patterns


def send_wechat(config: ClusteringSubscription, time_config: dict):
    result = query_patterns(config, time_config)
    # 企业微信只发送新增
    new_patterns, _ = clean_pattern(config, time_config, result)

    # 根据结果发送信息
    count_list = [i["count"] for i in result]
    content = (
        "【日志平台】{title} \n"
        "通知内容：近{interval}新增 pattern 统计 \n"
        "业务名称：{bk_biz_name} \n"
        "索引集名称：{index_set_name} \n"
        "日志分析：新增 pattern ({count})个，日志总共出现 ({total_num}) 条；"
        "最多的 pattern 日志数量为 {max_num} 条({percentage}%) \n"
        "新增日志/Pattern示例：\n"
        "{patterns} \n"
        "日志详情：[跳转到日志检索页面]({log_search_url})".format(
            count=len(result),
            bk_biz_name=config.bk_biz_name,
            index_set_name=config.index_set_name,
            percentage=max([i["percentage"] for i in result]),
            interval=time_config["interval"],
            total_num=sum(count_list),
            max_num=max(count_list),
            title=config.title,
            patterns="\n".join([json.dumps(pattern["pattern"]).replace('"', "") for pattern in new_patterns]),
            log_search_url=generate_log_search_url(config, time_config),
        )
    )

    send_params = {"chatid": config.receivers[0]["id"], "msgtype": "markdown", "markdown": {"content": content}}
    robot_api.send_msg(send_params)


def generate_log_search_url(config: ClusteringSubscription, time_config: dict) -> str:
    params = {
        "spaceUid": f"bkcc__{config.bk_biz_id}",
        "bizId": config.bk_biz_id,
        "keyword": "*",
        "start_time": time_config["start_time"],
        "end_time": time_config["end_time"],
    }

    url = f"{settings.LOG_SEARCH_SAAS_URL}/#/retrieve/{config.index_set_id}?{urlencode(params)}"
    return url


def generate_mail_table_trs(patterns: list) -> str:

    trs = []
    for i in patterns:
        td = [i["signature"], i["count"], i["percentage"], i["year_on_year_count"], i["pattern"]] + [
            g for g in i["group"] if g
        ]
        trs.append(f"<tr>{''.join([f'<td>{i}</td>' for i in td])}</tr>")

    return "".join(trs)


def send_mail(config: ClusteringSubscription, time_config: dict):
    result = query_patterns(config, time_config)
    new_patterns, patterns = clean_pattern(config, time_config, result)

    content = """
    <p>{start_time}-{end_time} {title}</p>
    <p>业务名称:   {bk_biz_name}</p>
    <p>索引集名称: {index_set_name}</p>
    <p>日志分析：Pattern ({count})个，日志总共出现 ({total_num}) 条</p>
    <p>日志详情：<a href='{log_search_url}'>跳转到日志检索页面<a/></p>
    """.format(
        title=config.title,
        bk_biz_name=config.bk_biz_name,
        count=len(result),
        total_num=sum([i["count"] for i in result]),
        index_set_name=config.index_set_name,
        start_time=time_config["start_time"],
        end_time=time_config["end_time"],
        log_search_url=generate_log_search_url(config, time_config),
    )
    table_headers = ["数据指纹", "数量", "占比", "同比数量", "Pattern"] + config.group_by
    thead_html = f"<tr>{''.join([f'<td>{i}</td>' for i in table_headers])}</tr>"

    new_pattern_trs = generate_mail_table_trs(new_patterns)
    pattern_trs = generate_mail_table_trs(patterns)
    new_pattern_table = f"<p>新增Pattern/Log示例：</p><table>{thead_html}{new_pattern_trs}</table>"
    pattern_table = f"<p>非新增Pattern/Log示例：</p><table>{thead_html}{pattern_trs}</table>"

    mail_tpl = """
        <style>
            table {
                width: 1200px;
                border: 1px solid #000000;
                border-collapse: collapse;
            }
            th {
                text-align: left;
            }
            th, td {
                border: 1px solid #000000;
                text-align: center;
                font-size: 14px;
                padding: 3px;
                min-width: 60px;
            }
        </style>
        %s%s%s
    """ % (
        content,
        new_pattern_table if new_pattern_trs else "",
        pattern_table if pattern_trs else "",
    )

    # 根据结果发送邮件
    send_params = {
        "receivers": ",".join([r["id"] for r in config.receivers]),
        "content": mail_tpl,
        "title": config.title,
    }
    CmsiApi.send_mail(send_params)


@periodic_task(run_every=crontab(minute="*/1"))
def send_subscription_task():
    subscription_configs = ClusteringSubscription.objects.all()

    with ThreadPoolExecutor() as ex:
        for configs in subscription_configs:
            time_config = get_start_and_end_time(configs.frequency, configs.last_run_at)
            is_run_time = time_config["is_run_time"]
            # 未到运行时间
            if not is_run_time:
                continue

            if configs.subscription_type == SubscriptionTypeEnum.WECHAT.value:
                ex.submit(send_wechat, configs, time_config)

            if configs.subscription_type == SubscriptionTypeEnum.EMAIL.value:
                ex.submit(send_mail, configs, time_config)
