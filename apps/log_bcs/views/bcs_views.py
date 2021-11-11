from rest_framework import serializers

from apps.generic import APIViewSet
from apps.utils.drf import detail_route


class BcsViewSet(APIViewSet):
    lookup_field = "bk_biz_id"
    serializer_class = serializers.Serializer

    @detail_route(methods=["POST"])
    def open_bcs_log(self, request, bk_biz_id):
        pass

    @detail_route(methods=["GET"])
    def list_cluster(self, request, bk_biz_id):
        """
        @api {get} /bcs/list_cluster/$bk_biz_id bcs集群列表
        @apiName list_bcs_cluster
        @apiGroup Bcs
        @apiDescription 拉取业务下的bcs集群列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Int} snapshots.indices.store_size 存储大小 单位Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
               {
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        pass
