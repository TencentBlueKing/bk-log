# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bkm_ipchooser.handlers import config_handler, host_handler, topo_handler, template_handler, dynamic_group_handler
from bkm_ipchooser.serializers import host_sers, topo_sers, template_sers, config_sers, dynamic_group_sers

try:
    from rest_framework.decorators import list_route, detail_route
except ImportError:
    # 兼容新版本 DRF 缺失 list_route, detail_route 的情况
    from rest_framework.decorators import action as viewset_action

    def list_route(**kwargs):
        kwargs["detail"] = False
        return viewset_action(**kwargs)

    def detail_route(**kwargs):
        kwargs["detail"] = True
        return viewset_action(**kwargs)


IP_CHOOSER_VIEW_TAGS = ["ipchooser"]


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # To not perform the csrf check previously happening
        return


class CommonViewSet(GenericViewSet):
    # TODO: 根据实际系统权限模型补充
    permission_classes = ()

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def params_valid(self, serializer, params=None):
        """
        校验参数是否满足 serializer 规定的格式，支持传入serializer
        """
        # 校验request中的参数
        if not params:
            if self.request.method in ["GET"]:
                params = self.request.query_params
            else:
                params = self.request.data

        _serializer = serializer(data=params)
        _serializer.is_valid(raise_exception=True)
        return dict(_serializer.data)

    @property
    def validated_data(self):
        """
        校验的数据
        """
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data

        # 从 esb 获取参数
        bk_username = self.request.META.get("HTTP_BK_USERNAME")
        bk_app_code = self.request.META.get("HTTP_BK_APP_CODE")

        data = data.copy()
        data.setdefault("bk_username", bk_username)
        data.setdefault("bk_app_code", bk_app_code)

        serializer = self.serializer_class or self.get_serializer_class()
        return self.params_valid(serializer, data)

    def finalize_response(self, request, response, *args, **kwargs):
        # 目前仅对 Restful Response 进行处理
        if isinstance(response, Response):
            response.data = {"result": True, "data": response.data, "code": 0, "message": ""}
            response.status_code = status.HTTP_200_OK

        # 返回响应头禁用浏览器的类型猜测行为
        response.headers["x-content-type-options"] = ("X-Content-Type-Options", "nosniff")
        return super(CommonViewSet, self).finalize_response(request, response, *args, **kwargs)


class IpChooserTopoViewSet(CommonViewSet):
    URL_BASE_NAME = "ipchooser_topo"

    @swagger_auto_schema(
        operation_summary=_("批量获取含各节点主机数量的拓扑树"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=topo_sers.TreesRequestSer(),
        responses={status.HTTP_200_OK: topo_sers.TreesResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=topo_sers.TreesRequestSer)
    def trees(self, request, *args, **kwargs):
        return Response(topo_handler.TopoHandler.trees(scope_list=self.validated_data["scope_list"]))

    @swagger_auto_schema(
        operation_summary=_("查询多个节点拓扑路径"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=topo_sers.QueryPathRequestSer(),
        responses={status.HTTP_200_OK: topo_sers.QueryPathResponseSer()},
    )
    @list_route(methods=["POST"], detail=False, serializer_class=topo_sers.QueryPathRequestSer)
    def query_path(self, request, *args, **kwargs):
        return Response(
            topo_handler.TopoHandler.query_path(
                scope_list=self.validated_data["scope_list"], node_list=self.validated_data["node_list"]
            )
        )

    @swagger_auto_schema(
        operation_summary=_("根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=topo_sers.QueryHostsRequestSer(),
        responses={status.HTTP_200_OK: topo_sers.QueryHostsResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=topo_sers.QueryHostsRequestSer)
    def query_hosts(self, request, *args, **kwargs):
        return Response(
            topo_handler.TopoHandler.query_hosts(
                scope_list=self.validated_data["scope_list"],
                readable_node_list=self.validated_data["node_list"],
                conditions=self.validated_data["conditions"],
                start=self.validated_data["start"],
                page_size=self.validated_data["page_size"],
            )
        )

    @swagger_auto_schema(
        operation_summary=_("根据多个拓扑节点与搜索条件批量分页查询所包含的主机 ID 信息"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=topo_sers.QueryHostIdInfosRequestSer(),
        responses={status.HTTP_200_OK: topo_sers.QueryHostIdInfosResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=topo_sers.QueryHostIdInfosRequestSer)
    def query_host_id_infos(self, request, *args, **kwargs):
        return Response(
            topo_handler.TopoHandler.query_host_id_infos(
                scope_list=self.validated_data["scope_list"],
                readable_node_list=self.validated_data["node_list"],
                conditions=self.validated_data["conditions"],
                start=self.validated_data["start"],
                page_size=self.validated_data["page_size"],
            )
        )

    @list_route(methods=["POST"], serializer_class=topo_sers.AgentStatisticsRequestSer)
    def agent_statistics(self, request, *args, **kwargs):
        return Response(
            topo_handler.TopoHandler.agent_statistics(
                scope_list=self.validated_data["scope_list"], node_list=self.validated_data["node_list"]
            )
        )


class IpChooserHostViewSet(CommonViewSet):
    URL_BASE_NAME = "ipchooser_host"
    pagination_class = None

    @swagger_auto_schema(
        operation_summary=_("根据用户手动输入的`IP`/`IPv6`/`主机名`/`host_id`等关键字信息获取真实存在的机器信息"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=host_sers.HostCheckRequestSer(),
        responses={status.HTTP_200_OK: host_sers.HostCheckResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=host_sers.HostCheckRequestSer)
    def check(self, request, *args, **kwargs):
        return Response(
            host_handler.HostHandler.check(
                scope_list=self.validated_data["scope_list"],
                ip_list=self.validated_data["ip_list"],
                ipv6_list=self.validated_data["ipv6_list"],
                key_list=self.validated_data["key_list"],
            )
        )

    @swagger_auto_schema(
        operation_summary=_("根据主机关键信息获取机器详情信息"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=host_sers.HostDetailsRequestSer(),
        responses={status.HTTP_200_OK: host_sers.HostDetailsResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=host_sers.HostDetailsRequestSer)
    def details(self, request, *args, **kwargs):
        return Response(
            host_handler.HostHandler.details(
                scope_list=self.validated_data["scope_list"], host_list=self.validated_data["host_list"]
            )
        )


class IpChooserTemplateViewSet(CommonViewSet):
    URL_BASE_NAME = "ipchooser_template"
    pagination_class = None

    @swagger_auto_schema(
        operation_summary=_("拉取模板列表"),
        tags=IP_CHOOSER_VIEW_TAGS,
        request_body=template_sers.ListTemplateSer(),
        responses={status.HTTP_200_OK: template_sers.ListTemplateResponseSer()},
    )
    @list_route(methods=["POST"], serializer_class=template_sers.ListTemplateSer)
    def templates(self, request, *args, **kwargs):
        return Response(
            template_handler.TemplateHandler(
                scope_list=self.validated_data["scope_list"],
                template_type=self.validated_data["template_type"],
            ).list_templates(template_id_list=self.validated_data["template_id_list"])
        )

    @list_route(methods=["POST"], serializer_class=template_sers.ListNodeSer)
    def nodes(self, request, *args, **kwargs):
        return Response(
            template_handler.TemplateHandler(
                scope_list=self.validated_data["scope_list"],
                template_type=self.validated_data["template_type"],
                template_id=self.validated_data["id"],
            ).list_nodes(start=self.validated_data["start"], page_size=self.validated_data["page_size"])
        )

    @list_route(methods=["POST"], serializer_class=template_sers.ListHostSer)
    def hosts(self, request, *args, **kwargs):
        return Response(
            template_handler.TemplateHandler(
                scope_list=self.validated_data["scope_list"],
                template_type=self.validated_data["template_type"],
                template_id=self.validated_data["id"],
            ).list_hosts(start=self.validated_data["start"], page_size=self.validated_data["page_size"])
        )

    @list_route(methods=["POST"], serializer_class=template_sers.AgentStatisticsSer)
    def agent_statistics(self, request, *args, **kwargs):
        return Response(
            template_handler.TemplateHandler(
                scope_list=self.validated_data["scope_list"], template_type=self.validated_data["template_type"]
            ).agent_statistics(template_id_list=self.validated_data["template_id_list"])
        )


class IpChooserConfigViewSet(CommonViewSet):
    URL_BASE_NAME = "ipchooser_config"
    pagination_class = None

    @list_route(methods=["GET"], url_path="global")
    def global_config(self, request, *args, **kwargs):
        return Response(config_handler.ConfigHandler().get_global_settings())

    @list_route(methods=["POST"], serializer_class=config_sers.BatchGetSer)
    def batch_get(self, request, *args, **kwargs):
        return Response(
            config_handler.ConfigHandler(username=request.user.username).batch_get(
                module_list=self.validated_data["module_list"]
            )
        )

    @list_route(methods=["POST"], serializer_class=config_sers.UpdateSer)
    def update_config(self, request, *args, **kwargs):
        return Response(
            config_handler.ConfigHandler(username=request.user.username).update(
                config=self.validated_data["settings_map"]
            )
        )

    @list_route(methods=["POST"], serializer_class=config_sers.BatchDeleteSer)
    def batch_delete(self, request, *args, **kwargs):
        return Response(
            config_handler.ConfigHandler(username=request.user.username).batch_delete(
                module_list=self.validated_data["module_list"]
            )
        )


class IpChooserDynamicGroupViewSet(CommonViewSet):
    URL_BASE_NAME = "ipchooser_dynamic_group"
    pagination_class = None

    @list_route(methods=["POST"], url_path="groups", serializer_class=dynamic_group_sers.ListDynamicGroupSer)
    def dynamic_groups(self, request, *args, **kwargs):
        return Response(
            dynamic_group_handler.DynamicGroupHandler(scope_list=self.validated_data["scope_list"]).list(
                dynamic_group_list=self.validated_data["dynamic_group_list"]
            )
        )

    @list_route(methods=["POST"], url_path="execute", serializer_class=dynamic_group_sers.ExecuteDynamicGroupSer)
    def execute_dynamic_group(self, request, *args, **kwargs):
        return Response(
            dynamic_group_handler.DynamicGroupHandler(scope_list=self.validated_data["scope_list"]).execute(
                dynamic_group_id=self.validated_data["id"],
                start=self.validated_data["start"],
                page_size=self.validated_data["page_size"],
            )
        )

    @list_route(methods=["POST"], serializer_class=dynamic_group_sers.AgentStatistiscSer)
    def agent_statistics(self, request, *args, **kwargs):
        return Response(
            dynamic_group_handler.DynamicGroupHandler(scope_list=self.validated_data["scope_list"]).agent_statistics(
                dynamic_group_list=self.validated_data["dynamic_group_list"],
            )
        )
