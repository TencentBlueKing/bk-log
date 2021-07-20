# -*- coding: utf-8 -*-
import arrow

from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _

from apps.generic import APIViewSet
from apps.utils.drf import detail_route
from apps.bk_log_admin.handlers.index_set import IndexSetHandler
from apps.bk_log_admin.serializers import UserSearchHistoryOperationStatisticSerializer
from apps.bk_log_admin.serializers import UserSearchHistorySerializer
from apps.bk_log_admin import constants
from apps.exceptions import ValidationError


class IndexSetViewSet(APIViewSet):
    @detail_route(methods=["get"], url_path="history/date_histogram")
    def date_histogram(self, request, pk=None):
        """
        @api {get} /admin/index_set/$index_set_id/history/date_histogram/
        02_获取检索结果按照提供粒度转为直方图
        @apiName date_histogram
        @apiDescription 获取检索结果按照提供粒度转为直方图
        @apiGroup 60_admin
        @apiParam {int} index_set_id 索引集id
        @apiParam {Datetime} start_time 起始时间
        @apiParam {Datetime} end_time 结束时间
        @apiParam {Datetime} index_set_id 结束时间
        @apiSuccess {List} labels 标签
        @apiSuccess {List} values 返回数值
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "labels": [
                    "2021-02-27 00:00:00+00:00",
                    "2021-02-28 00:00:00+00:00",
                    "2021-03-01 00:00:00+00:00"
                ],
                "values": [
                    0,
                    3,
                    1
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(UserSearchHistoryOperationStatisticSerializer)
        return Response(IndexSetHandler().get_date_histogram(pk, data))

    @detail_route(methods=["get"], url_path="history/user_terms")
    def user_terms(self, request, pk=None):
        """
        @api {get} /admin/index_set/$index_set_id/history/user_terms/
        03_获取检索结果按照用户使用频次聚合
        @apiName user_terms
        @apiDescription 获取检索结果按照用户使用频次聚合
        @apiGroup 60_admin
        @apiParam {int} index_set_id 索引集id
        @apiParam {Datetime} start_time 起始时间
        @apiParam {Datetime} end_time 结束时间
        @apiParam {Datetime} index_set_id 结束时间
        @apiSuccess {List} labels 标签
        @apiSuccess {List} values 返回数值
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "labels": [
                    "samuel",
                    "samuelsheng"
                ],
                "values": [
                    1,
                    3
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(UserSearchHistoryOperationStatisticSerializer)
        return Response(IndexSetHandler().get_user_terms(pk, data))

    @detail_route(methods=["get"], url_path="history/duration_terms")
    def duration_terms(self, request, pk=None):
        """
        @api {get} /admin/index_set/$index_set_id/history/duration_terms/
        04_获取检索结果按照使用时间段聚合
        @apiName duration_terms
        @apiDescription 获取检索结果按照使用时间段聚合
        @apiGroup 60_admin
        @apiParam {int} index_set_id 索引集id
        @apiParam {Datetime} start_time 起始时间
        @apiParam {Datetime} end_time 结束时间
        @apiParam {Datetime} index_set_id 结束时间
        @apiSuccess {List} labels 标签
        @apiSuccess {List} values 返回数值
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "labels": [
                    "samuel",
                    "samuelsheng"
                ],
                "values": [
                    1,
                    3
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(UserSearchHistoryOperationStatisticSerializer)
        return Response(IndexSetHandler().get_duration_terms(pk, data))

    @detail_route(methods=["GET"], url_path="history")
    def list_user_set_history(self, request, pk=None):
        """
        @api {get} /admin/index_set/$index_set_id/history/?page=&pagesize=&start_time=&end_time= 05_获取用户检索历史
        @apiName user_search_index_set_history
        @apiGroup 60_admin
        @apiDescription 根据索引集id获取用户检索历史
        @apiParam {Int} index_set_id 索引集id
        @apiParam {Datetime} start_time 开始时间
        @apiParam {Datetime} end_time 结束时间
        @apiParam {Int} page 页数
        @apiParam {Int} pagesize 每页数量
        @apiSuccess {Int} total 总数
        @apiSuccess {List} list 检索历史列表
        @apiSuccess {Int} list.id search_history_id
        @apiSuccess {Int} list.index_set_id 索引集id
        @apiSuccess {Float} list.duration 耗时
        @apiSuccess {String} list.created_by 创建者
        @apiSuccess {Datetime} list.created_at 创建时间
        @apiSuccess {Object} list.params 检索条件
        @apiSuccessExample {json} 成功返回:
        {
            "result":true,
            "data":{
                "total":10,
                "list":[
                    {
                        "id":25,
                        "index_set_id":1,
                        "duration":723,
                        "created_by":"samuelsheng",
                        "created_at":"2021-02-03T02:03:41.928070Z",
                        "params":{
                            "keyword":"dtEventTimeStamp : 1612317781873",
                            "host_scopes":{
                                "modules":[

                                ],
                                "ips":""
                            },
                            "addition":[

                            ]
                        },
                        "query_string":""
                    }
                ]
            },
            "code":0,
            "message":""
        }
        """
        data = self.params_valid(UserSearchHistorySerializer)
        start_time = arrow.get(data["start_time"])
        end_time = arrow.get(data["end_time"])
        if (end_time - start_time).days >= constants.HISTORY_MAX_DAYS:
            raise ValidationError(_(f"查询时间段目前只支持{constants.HISTORY_MAX_DAYS}天"))
        return IndexSetHandler().list_user_set_history(
            start_time=start_time, end_time=end_time, request=request, view=self, pk=pk
        )
