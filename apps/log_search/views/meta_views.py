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
import copy

from django.conf import settings
from django.template import engines
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.response import Response

from apps.utils.context_processors import mysetting
from apps.utils.drf import list_route
from apps.exceptions import LanguageDoseNotSupported, ValidationError
from apps.generic import APIViewSet
from apps.log_search.constants import TimeEnum, FILTER_KEY_LIST
from apps.log_search.handlers.meta import MetaHandler
from apps.log_search.models import GlobalConfig, Scenario
from apps.log_search.serializers import ProjectSerializer
from apps.utils.local import get_request_username
from apps.utils.db import get_toggle_data


class MetaViewSet(APIViewSet):
    serializer_class = serializers.Serializer

    @list_route(methods=["GET"], url_path="mine")
    def list_user(self, request):
        """
        @api {get} /meta/mine/ 获取我的信息
        @apiName list_meta_mine
        @apiGroup 01_Meta
        @apiSuccess {String} username 用户名
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "username": "admin"
            },
            "result": true
        }
        """
        return Response(MetaHandler.get_user())

    @list_route(methods=["GET"], url_path="spaces/mine")
    def list_spaces_mine(self, request):
        """
        @api {get} /meta/spaces/mine/ 获取我的项目空间
        @apiName list_meta_spaces_mine
        @apiGroup 01_Meta
        @apiSuccess {Int} id 空间自增ID
        @apiSuccess {String} space_uid 空间唯一标识
        @apiSuccess {String} space_type_id 空间类型ID
        @apiSuccess {String} space_id 空间ID
        @apiSuccess {String} space_name 空间名称
        @apiSuccess {String} space_code 空间编号
        @apiSuccess {Int} bk_biz_id 业务ID
        @apiSuccess {String} status 空间状态
        @apiSuccess {String} time_zone 空间所在时区
        @apiSuccess {String} permission 空间权限
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": 11,
                    "space_type_id": "bkcc",
                    "space_id": "2",
                    "space_name": "蓝鲸",
                    "status": "normal",
                    "space_code": "2",
                    "space_uid": "bkcc__2",
                    "bk_biz_id": 2,
                    "time_zone": "Asia/Shanghai",
                    "permission": {"view_business": True},
                }
            ],
            "result": true
        }
        """
        return Response(MetaHandler.get_user_spaces(get_request_username()))

    @list_route(methods=["GET"], url_path="projects")
    def list_projects(self, request):
        """
        @api {get} /meta/projects/ 获取项目列表
        @apiName list_meta_projects
        @apiGroup 01_Meta
        @apiSuccess {Int} project_id 项目ID
        @apiSuccess {String} project_name 项目名称
        @apiSuccess {Int} bk_biz_id 业务ID
        @apiSuccess {String} bk_app_code 接入的来源APP_CODE
        @apiSuccess {String} time_zone 项目所在时区
        @apiSuccess {String} description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "project_id": 1,
                    "project_name": "业务名称",
                    "bk_biz_id": 1,
                    "bk_app_code": "bk_log",
                    "time_zone": "Asia/Shanghai",
                    "description": "项目描述",
                }
            ],
            "result": true
        }
        """
        return Response(ProjectSerializer(MetaHandler.get_projects(), many=True).data)

    @list_route(methods=["GET"], url_path="index_html_environment")
    def get_index_settings(self, request):
        """
         @api {get} /meta/index_html_environment/ 获取首页环境变量
         @apiName get_index_html_environment
         @apiGroup 01_Meta
         @apiSuccess {Str} RUN_MODE 版本环境
         @apiSuccess {Str} ENVIRONMENT 运行环境
         @apiSuccess {Str} APP_CODE 应用码
         @apiSuccessExample {json} 成功返回:
         {
            "message":"",
            "code":0,
            "data":{
                "RUN_MODE":"test",
                "ENVIRONMENT":"test",
                "APP_CODE":"test"
            },
            "result":true
        }
        """
        my_setting = copy.copy(mysetting(request))
        [my_setting.pop(key) for key in FILTER_KEY_LIST]
        data = get_toggle_data()
        return Response({**my_setting, **data})

    @list_route(methods=["GET"], url_path="projects/mine")
    def list_projects_mine(self, request):
        """
        @api {get} /meta/projects/mine/ 获取我的项目
        @apiName list_meta_projects_mine
        @apiGroup 01_Meta
        @apiSuccess {Int} project_id 项目ID
        @apiSuccess {String} project_name 项目名称
        @apiSuccess {Int} bk_biz_id 业务ID
        @apiSuccess {String} bk_app_code 接入的来源APP_CODE
        @apiSuccess {String} time_zone 项目所在时区
        @apiSuccess {String} description 描述
        @apiSuccess {Bool} project_manage 是否有项目管理权限（有权限才显示：管理、监控两个模块）
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "project_id": 1,
                    "project_name": "业务名称",
                    "bk_biz_id": 1,
                    "bk_app_code": "bk_log",
                    "time_zone": "Asia/Shanghai",
                    "description": "项目描述",
                    "project_manage": true
                }
            ],
            "result": true
        }
        """
        return Response(MetaHandler.get_user_projects(get_request_username()))

    @list_route(methods=["GET"], url_path="msg_type")
    def msg_type(self, requests):
        """
        @api {get} /meta/msg_type/ 获取通知列表
        @apiName list_meta_msg_type
        @apiGroup 01_Meta
        @apiSuccess {String} type 类型
        @apiSuccess {String} label 名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "type": "weixin",
                    "label": "微信",
                },
                {
                    "type": "mail",
                    "label": "邮件",
                },
                {
                    "type": "sms",
                    "label": "短信",
                },
                {
                    "type": "voice",
                    "label": "语音",
                }
            ],
            "result": true
        }
        """
        return Response(MetaHandler.get_msg_type())

    @list_route(methods=["GET"], url_path="scenario")
    def scenario(self, request):
        """
        @api {get} /meta/scenario/ 获取接入场景
        @apiName list_index_set_scenario
        @apiGroup 01_Meta
        @apiSuccess {String} scenario_id 接入场景
        @apiSuccess {String} scenario_name 接入场景名称
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "scenario_id": "bkdata",
                    "scenario_name": "数据平台"
                },
                {
                    "scenario_id": "es",
                    "scenario_name": "ES"
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        return Response(Scenario.get_scenarios())

    @list_route(methods=["GET"], url_path="globals")
    def globals(self, request):
        """
        @api {get} /meta/globals/ 获取全局配置
        @apiName list_globals_config
        @apiGroup 01_Meta
        @apiSuccess {Json} data 公共配置
        @apiSuccess {Json} data.category 数据分类（二级分类）
        @apiSuccess {Json} data.data_encoding 编码格式
        @apiSuccess {Json} data.data_delimiter 分隔符列表
        @apiSuccess {Json} data.storage_duration_time 数据保存时间
        @apiSuccess {Json} data.collector_scenario 采集场景：行日志、段日志、window event
        @apiSuccess {String} data.is_active 是否可选 （没有这个key也是可选）
        @apiSuccess {String} data.default 是否默认选项 （没有这个key则为否）
        @apiSuccess {String} data.category.id 标识
        @apiSuccess {String} data.category.name 名称
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "category": [
                    {
                        "id": "host",
                        "name": "主机",
                        "children": [
                            {
                                "id": "host_os",
                                "name": "操作系统"
                            }
                        ]
                    },
                    {
                        "id": "app",
                        "name": "应用",
                        "children": [
                            {
                                "id": "app_service",
                                "name": "服务场景"
                            }
                        ]
                    }
                ],
                "data_encoding": [
                    {
                        "id": "utf-8",
                        "name": "UTF-8"
                    }
                ],
                "data_delimiter": [
                    {
                        "id": "|",
                        "name": "|"
                    }
                ],
                "storage_duration_time": [
                    {
                        "id": "1",
                        "name": "一天",
                        "default": true
                    }
                ],
                "time_field_type": [
                    {
                        "id": "date"
                        "name": "date"
                    }
                ],
                "time_field_unit": [
                    {
                        "id": "second"
                        "name": "second"
                    }
                ]
            }
            "code": 0,
            "message": ""
        }
        """
        return Response(GlobalConfig.get_configs())

    @list_route(methods=["GET"], url_path="biz_maintainer")
    def biz_maintainer(self, request):
        """
        @api {get} /meta/biz_maintainer/ 获取用户列表
        @apiName biz_maintainer
        @apiGroup 01_Meta
        @apiSuccess {String} data.bk_biz_name 业务名称
        @apiSuccess {String} data.maintainer 运维人员列表
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "bk_biz_name": "业务名称",
                "maintainer": ["a", "b"]
            },
            "result": true
        }
        """
        space_uid = request.GET.get("space_uid", "")
        data = MetaHandler.get_biz_maintainer(space_uid)
        return Response(data)

    @list_route(methods=["GET"], url_path="footer_html")
    def footer_html(self, request):
        """
        获取footer的html代码，用于前端渲染
        """
        footer_template = """
        <div class="footer-content" style="position: fixed; bottom: 15px; left: 0;
            display: flex; flex-flow: column; align-items: center;
            width: 100%; line-height: 20px; font-size: 12px; color: #FFF;">
            <div>
                {% for link in links %}{% if not forloop.first %} | {% endif %}<a href="{{ link.link | default:default_link }}" target="_blank" style="color: #9BC1FF;">{{ link.text }}</a>{% endfor %}
            </div>
            <div>{{ copyright }} {% if saas_version %}V{{ saas_version }}{% endif %}{% if backend_version %}(V{{ backend_version }}){% endif %}</div>
        </div>
        """  # noqa
        django_engine = engines["django"]
        template = django_engine.from_string(footer_template.strip())

        if translation.get_language() == "en":
            links = settings.FOOTER_CONFIG["footer"][0]["en"]
        else:
            links = settings.FOOTER_CONFIG["footer"][0]["zh"]

        saas_version = None
        backend_version = None

        for config in GlobalConfig.objects.filter(config_id__in=["SAAS_VERSION", "BACKEND_VERSION"]):
            if config.config_id == "SAAS_VERSION":
                saas_version = config.configs
            else:
                backend_version = config.configs

        return Response(
            template.render(
                {
                    "default_link": settings.BK_PAAS_HOST,
                    "links": links,
                    "saas_version": saas_version,
                    "backend_version": backend_version,
                    "copyright": settings.FOOTER_CONFIG["copyright"],
                }
            )
        )

    @list_route(methods=["GET"], url_path="user_guide")
    def get_user_guide(self, request):
        """
        @api {get} /meta/user_guide/ 获取新人指引
        @apiName user_guide
        @apiGroup 01_Meta
        @apiSuccess {Int} current_step 当前浏览步骤
        @apiSuccess {List} step_list 步骤列表
        @apiSuccess {Str} step_list.title 标题
        @apiSuccess {Str} step_list.content 内容
        @apiSuccess {Str} step_list.target 目标节点
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":{
                "default":{
                    "current_step":1,
                    "step_list":[
                        {
                            "title":"组件库和图标",
                            "content":"从基础组件、自定义业务组件、图标库中拖拽组件或图标到画布区域进行页面编排组装",
                            "target":"#bizSelector"
                        }
                    ]
                }
            },
            "result":true
        }
        """
        username = get_request_username()
        if not username:
            raise ValidationError(_("username 不能为空"))
        return Response(MetaHandler.get_user_guide(username=username))

    @list_route(methods=["POST"], url_path="update_user_guide")
    def update_user_guide(self, request):
        """
        @api {post} /meta/update_user_guide/ 更新新人指引
        @apiName update_user_guide
        @apiGroup 01_Meta
        @apiParamExample {json} 成功请求
        {
            "search":1
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "username": "test"
            },
            "result": true
        }
        """
        username = get_request_username()
        if not username:
            raise ValidationError(_("username 不能为空"))
        MetaHandler.update_user_guide(username=username, user_guide_dict=request.data)
        return Response({"username": username})


class LanguageViewSet(APIViewSet):
    serializer_class = serializers.Serializer

    def list(self, request, *args, **kwargs):
        """
        @api {get} /meta/language/ 获取语言列表
        @apiName list_meta_language
        @apiGroup 01_Meta
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": "zh-cn",
                    "name": "简体中文",
                },
                {
                    "id": "en",
                    "name": "English",
                }
            ],
            "result": true
        }
        """
        return Response([{"id": lang[0], "name": lang[1]} for lang in settings.LANGUAGES])

    def create(self, request, *args, **kwargs):
        """
        @api {POST} /meta/language/ 修改语言
        @apiName change_language
        @apiParam {String} language 语言
        @apiGroup 01_Meta
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "language": "zh-cn"
            },
            "result": true
        }
        """
        lang = request.data.get("language")
        if not lang:
            raise ValidationError(_("请选择语言"))

        if lang not in dict(settings.LANGUAGES):
            raise LanguageDoseNotSupported()
        if hasattr(request, "session"):
            request.session[settings.LANGUAGE_SESSION_KEY] = lang
        response = Response({"language": lang})
        response.set_cookie(key=settings.LANGUAGE_COOKIE_NAME, value=lang, max_age=TimeEnum.ONE_YEAR_SECOND.value)
        return response


class MenuViewSet(APIViewSet):
    serializer_class = serializers.Serializer

    def list(self, request, *args, **kwargs):
        """
        @api {get} /meta/menu/?space_uid=$space_uid 获取模块列表
        @apiName list_menu
        @apiGroup 01_Meta
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": "search",
                    "name": "检索",
                },
                {
                    "id": "monitor",
                    "name": "监控",
                },
                {
                    "id": "manage"
                    "name": "管理",
                    "children": [
                        {
                            "id": "manage_index_set",
                            "name": "索引集管理"
                        }
                    ]
                }
            ],
            "result": true
        }
        """
        # 判断是不是项目管理人员
        space_uid = request.GET.get("space_uid")
        if not space_uid:
            raise ValidationError(errors=_("space_uid 不能为空"))
        return Response(MetaHandler.get_menus(space_uid, request.user.is_superuser))
