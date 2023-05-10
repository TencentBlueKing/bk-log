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

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from apps.utils.drf import list_route

from apps.generic import ModelViewSet
from apps.log_extract import serializers, exceptions
from apps.log_extract.exceptions import TaskFileLinkNotExist
from apps.log_extract.handlers.link import LinkHandler
from apps.log_extract.handlers.tasks import TasksHandler
from apps.log_extract.models import Tasks
from apps.log_extract.serializers import DownloadFileSerializer


class TasksViewSet(ModelViewSet):
    model = Tasks
    lookup_field = "task_id"
    http_method_names = ["head", "get", "post", "patch"]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "list": serializers.TaskListSerializer,
            "retrieve": serializers.TaskListSerializer,
            "partial_update": serializers.TaskPartialUpdateSerializer,
            "link_list": None,
        }
        return action_serializer_map.get(self.action, serializers.TasksSerializer)

    def list(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/tasks/?bk_biz_id=${bk_biz_id}&page=${page}&pagesize=${pagesize} 21_tasks-任务列表
        @apiName list_task_records
        @apiGroup 18_extract
        @apiDescription 分页显示任务列表
        @apiParam  {Int} bk_biz_id 业务ID
        @apiParam  {Int} page 显示页数
        @apiParam {Int} pagesize 单页记录数
        @apiParam {String} keyword 搜索关键字
        @apiSuccess {Int} total 分页条数
        @apiSuccess {List(json)} list 分页内容
        @apiSuccess {Int} list.task_id 下载任务ID
        @apiSuccess {Int} list.bk_biz_id 业务ID
        @apiSuccess {String} list.preview_directory 预览目录
        @apiSuccess {String} list.preview_ip 预览ip
        @apiSuccess {String} list.preview_time_range 预览时间
        @apiSuccess {String} list.preview_is_search_child 预览是否检索子目录
        @apiSuccess {List[Dcit]} list.ip_list 下载目标
        @apiSuccess {List} list.file_path 文件路径
        @apiSuccess {String} list.download_status 任务状态
        @apiSuccess {String} download_status_display 任务状态展示
        @apiSuccess {Data} list.create_at 创建时间
        @apiSuccess {String} list.create_by 创建人
        @apiSuccess {String} list.remark 备注
        @apiSuccess {String} list.task_process_info 任务过程信息
        @apiSuccess {String} timeout 轮询时间上限
        @apiSuccessExample {json} 成功返回:
        {
         "result": true,
         "data": {
             "total": 2,
             "list":[{
                 "task_id": 1,
                 "bk_biz_id": 251,
                 "preview_directory": "/data/data/",
                 "preview_ip": "1.123.31.12",
                 "preview_time_range": "1d", -> ["1d", "1w", "1m", "all"]
                 "preview_is_search_child": false,
                 "ip_list": ["x.x.x.x"],
                 "file_path": ["/data/home/a.log", "/data/home/b.log","/data/home/c.log"],
                 "download_status": "packing",
                 "download_status_display": "正在打包",
                 "create_time": "2020-06-04 11:19:30",
                 "create_by": "your_username",
                 },
                 {
                 "task_id": 2,
                 "bk_biz_id": 251,
                 "preview_directory": "/data/data/",
                 "preview_ip": "1.123.31.12",
                 "preview_time_range": "1d", -> ["1d", "1w", "1m", "all"]
                 "preview_is_search_child": false,
                 "ip_list": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
                 "file_path": ["/data/home/d.log","/data/home/e.log",],
                 "download_status": "downloadable",
                 "download_status_display": "可下载",
                 "create_time": "2020-06-04 11:21:34",
                 "create_by": "your_username",
                 }],
             "time_out": 10
         },
         "code": 0,
         "message": ""
         }
        """
        if not request.query_params.get("page") or not request.query_params.get("pagesize"):
            raise ValueError(_("分页参数不能为空"))
        data = self.params_valid(serializers.ListTaskSerializer)
        return TasksHandler().list(self, bk_biz_id=data["bk_biz_id"], keyword=data["keyword"])

    def create(self, request, *args, **kwargs):
        """
        @api {post} /log_extract/tasks/ 22_tasks-创建下载任务
        @apiName create_download_task
        @apiGroup 18_extract
        @apiDescription 点击开始下载后创建下载任务
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List[Dict]} ip_list 目标文件所在的业务机器IP
        @apiParam {List} files 目标文件路径
        @apiParam {String} remark 备注
        @apiParam {String} preview_directory 预览目录
        @apiParam {String} preview_ip 预览ip
        @apiParam {String} preview_time_range 预览时间
        @apiParam {String} preview_is_search_child 预览是否选择子目录
        @apiParam {String} preview_start_time 预览开始时间
        @apiParam {String} preview_end_time 预览结束时间
        @apiParam {String} [filter_type] 过滤类型(match_word, line_range, tail_line, match_range)
        @apiParam {Dict} [filter_content] 过滤参数
        @apiSuccess {List(json)} data 返回数据
        @apiSuccess {Int} data.task_id 下载任务ID
        @apiParamExample {json} 请求样例1:
        {
            "bk_biz_id": 123,
            "remark": "这是一个备注",
            "preview_directory": "/data/test/data",
            "preview_ip: "1.23.1.1",
            "preview_time_range": "1d", -> ["1d", "1w", "1m", "all"]
            "preview_is_search_child": false,
            "preview_start_time": "2020-01-02 xx:xx",
            "preview_end_time": "2020-01-02 xx:xx",
            "ip_list": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
            "files": ["/dir/file_1","/dir/file_2"],
            "filter_type": "line_range",
            "filter_content": {
                "start_line": 1,
                "end_line": 2
                }
        }
        @apiParamExample {json} 请求样例2:
        {
            "bk_biz_id": 123,
            "ip": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
            "remark": "这是一个备注",
            "files": ["/dir/file_1","/dir/file_2"]
            "filter_type": "match_word",
            "filter_content": {
                "keyword": "error",
                "keyword_type: "keyword_or" -> ["keyword_or", "keyword_and", "keyword_not"]
                }
        }
        @apiParamExample {json} 请求样例3:
        {
            "bk_biz_id": 123,
            "ip": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
            "remark": "这是一个备注",
            "files": ["/dir/file_1","/dir/file_2"]
            "filter_type": "tail_line",
            "filter_type_display": "获取最新n行",
            "filter_content": {
                "line_num": 2
                }
        }
        @apiParamExample {json} 请求样例4:
        {
            "bk_biz_id": 123,
            "remark": "这是一个备注",
            "ip": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
            "files": ["/dir/file_1","/dir/file_2"]
            "filter_type": "match_range",
            "filter_type_display": "按关键字范围过滤行",
            "filter_content": {
                "start": "word_1",
                "end": "word_2"
                }
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "task_id": 1
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(serializers.CreateTaskSerializer)
        return Response(
            TasksHandler().create(
                bk_biz_id=data.get("bk_biz_id"),
                ip_list=data.get("ip_list"),
                request_file_list=data.get("file_path"),
                filter_type=data.get("filter_type"),
                filter_content=data.get("filter_content"),
                remark=data.get("remark"),
                preview_directory=data.get("preview_directory"),
                preview_ip_list=data.get("preview_ip_list"),
                preview_time_range=data.get("preview_time_range"),
                preview_is_search_child=data.get("preview_is_search_child"),
                preview_start_time=data.get("preview_start_time"),
                preview_end_time=data.get("preview_end_time"),
                link_id=data.get("link_id"),
            )
        )

    def destroy(self, request, *args, **kwargs):
        raise exceptions.TaskDeleteNotAllowed

    @list_route()
    def download(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/tasks/download/ 23_tasks_下载文件
        @apiName download
        @apiGroup 18_extract
        @apiDescription 通过该API会直接下载文件
        @apiParam  {Int} task_id 下载任务ID
        @apiParam {Int} bk_biz_id 业务ID
        @apiParamExample  {type} 请求示例:
        {
            "task_id": 1
        }
        @apiSuccessExample {json} 成功返回:
            无返回值，用户访问该API后重定向到下载链接直接下载文件

        """
        data = self.params_valid(serializers.DownloadSerializer)
        download_url = TasksHandler().download(task_id=data["task_id"])
        return redirect(download_url) if data.get("is_url") is None else Response(download_url)

    @list_route(methods=["post"])
    def recreate(self, request, *args, **kwargs):
        """
        @api {post} /log_extract/tasks/recreate/ 24_tasks-重新创建下载任务
        @apiName recreate
        @apiGroup 18_extract
        @apiParam  {Int} task_id 下载任务ID
        @apiSuccess {Int} task_id 下载任务ID
        @apiParamExample {json} 请求示例:
        {
            "task_id" : 1
        }
        @apiSuccessExample  {json} 成功返回:
        {
            "result": true,
            "data": {
                "task_id": 2
            }
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(serializers.RecreateTaskSerializer)

        return Response(TasksHandler().recreate(task_id=data["task_id"]))

    @list_route(methods=["get"])
    def polling(self, request, *args, **kwargs):
        # action 用户首页轮询任务进度时调用
        """
        @api {get} /log_extract/tasks/polling/ 25_tasks-轮询下载进度
        @apiName polling_download_status
        @apiGroup 18_extract
        @apiDescription 获取文件的下载状态

        @apiParam  {List} task_list 下载任务ID

        @apiSuccess {Int} task_id 下载任务ID
        @apiSuccess {String} download_status 任务下载状态标识
        @apiSuccess {String} download_status_display 任务下载状态内容
        @apiSuccess {String} task_process_info 任务过程信息
        @apiSuccess {String} remark 备注

        @apiParamExample {json} 请求示例:
        {
            "task_list": [1221,1222]
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [{
                "task_id": 1221,
                "download_status": "PACKING",
                "download_status_display": "正在打包",
                "remark": "",
                "task_process_info": ""
            },
            {
                "task_id": 1222,
                "download_status": "UPLOADING",
                "download_status_display": "上传中",
                "remark": "",
                "task_process_info": ""
            }]
            "code": 0,
            "message": ""
        }

        """
        data = self.params_valid(serializers.TaskPollingSerializer)
        return Response(TasksHandler().get_polling_result(task_list=data["task_list"]))

    def retrieve(self, request, *args, task_id=None, **kwargs):
        """
        @api {get} /log_extract/tasks/${task_id}/ 26_tasks-任务详情
        @apiName retrieve_task_details
        @apiGroup 18_extract
        @apiDescription 获取文件的下载详情
        @apiParam  {Int} task_id 任务ID
        @apiSuccess {Int} bk_biz_id 业务ID
        @apiSuccess {List[Dict]} ip_list 下载目标
        @apiSuccess {List} file_paths 原文件名
        @apiSuccess {String} download_status 任务状态
        @apiSuccess {Data} create_time 创建时间
        @apiSuccess {String} create_by 创建人
        @apiSuccess {String} start_time 任务开始时间
        @apiSuccess {String} end_time 任务结束时间
        @apiSuccess {String} preview_directory 预览目录
        @apiSuccess {String} preview_ip 预览ip
        @apiSuccess {String} preview_time_range 预览时间
        @apiSuccess {String} preview_is_search_child 预览是否检索子目录
        @apiSuccess {String} task_process_info 过程信息
        @apiSuccess {Array[Dict]} task_step_status 任务过程状态
        @apiSuccess {String} task_step_status.finish_time 过程结束时间
        @apiSuccess {String} task_step_status.id 过程id
        @apiSuccess {Int} task_step_status.loop 过程执行次数
        @apiSuccess {String} task_step_status.name 过程名称
        @apiSuccess {String} task_step_status.name_display 展示过程名称
        @apiSuccess {String} task_step_status.start_time 过程结束时间
        @apiSuccess {String} task_step_status.state 过程状态
        @apiSuccess {String} task_step_status.state_display 过程状态展示

        @apiParamExample {json} 请求示例:
        {
            "task_id": 1
        }

        @apiSuccessExample {json} 成功返回:
        {
         "result": true,
         "data": {
             "bk_biz_id": 251,
             "ip_list": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "x.x.x.x", "bk_cloud_id": 1}],
             "file_path": [
                 "/data/home/a.log",
                 "/data/home/b.log",
                 "/data/home/c.log",
                 ]
             "download_status": "PACKING",
             "download_status_display": "正在打包",
             "create_time": "2020-06-04 11:19:30",
             "create_by": "your_username",
             "start_time": "2020-06-04 11:19:32"
             "end_time": "--" (此时任务未结束),
             "preview_directory": "/data/data/",
             "preview_ip": "1.123.31.12",
             "preview_time_range": "1d", -> ["1d", "1w", "1m", "all"]
             "preview_is_search_child": false,
             "task_step_status": [{
                 finish_time: "2020-09-14 02:33:20"
                 id: "42b253f70c2e3201adac9bfb01539e3d"
                 loop: 1
                 name: "packing"
                 name_display: "文件打包中"
                 retry: 0
                 skip: false
                 start_time: "2020-09-14 02:33:16"
                 state: "FINISHED", // {"CREATED": 为执行,
                                         "RUNNING"： 执行中,
                                         "FAILED": 失败,
                                         "SUSPENDED": 暂停,
                                         "REVOKED": 已经终止,
                                         "FINISHED": 已经终止
                                         }
                 state_display: "xxx"
             }]
         },
         "code": 0,
         "message": ""
         }
        """

        return TasksHandler().retrieve(self)

    def partial_update(self, request, *args, **kwargs):
        """
        @api {patch} /log_extract/tasks/${task_id}/ 27_tasks-任务部分更新
        @apiName partial_update_task
        @apiGroup 18_extract
        @apiDescription 部分更新任务字段
        @apiParamExample {json} 请求示例:
        {
            "remark": "test"
        }

        @apiSuccessExample {json} 成功返回:
        {
         "result": true,
         "data": {
         },
         "code": 0,
         "message": ""
         }
        """
        return TasksHandler().partial_update(self, *args, **kwargs)

    @list_route()
    def link_list(self, request):
        """
        @api {post} /log_extract/tasks/link_list/ 28_tasks-提取链路列表
        @apiName link_list
        @apiGroup 18_extract
        @apiSuccess {List{Dict}} link 链路
        @apiSuccess {Int} link.link_id 链路id
        @apiSuccess {String} link.show_name 链路展示
        @apiSuccessExample  {json} 成功返回:
        {
            "result": true,
            "data": [{
                "link_id": 1,
                "show_name": "腾讯云cos链路 -> huabei"
            }]
            "code": 0,
            "message": ""
        }
        """
        return Response(LinkHandler().list())

    @list_route()
    def download_file(self, request):
        """
        @api {get} /log_extract/tasks/download/ 29_tasks-提取本地文件下载
        @apiName download
        @apiGroup 18_extract
        @apiParam  {String} target_file 加密的文件名
        """
        data = self.params_valid(DownloadFileSerializer)
        target_file = data.get("target_file")
        target_file_dir = os.path.join(settings.EXTRACT_SAAS_STORE_DIR, target_file)
        if not os.path.isfile(target_file_dir):
            raise TaskFileLinkNotExist
        with open(target_file_dir, "rb") as f:
            content = f.read()
        response = HttpResponse(content=content)
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = 'attachment;filename="{}"'.format(target_file)
        return response
