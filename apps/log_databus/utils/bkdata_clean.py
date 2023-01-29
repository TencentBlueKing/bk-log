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
from blueapps.utils.unique import uniqid
from django.core.cache import cache

from apps.api import BkDataDatabusApi
from apps.utils.log import logger
from apps.log_databus.constants import DEFAULT_TIME_FORMAT, DEFAULT_CATEGORY_ID, MAX_SYNC_CLEAN_TTL
from apps.log_databus.models import BKDataClean
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import Scenario
from bkm_space.utils import bk_biz_id_to_space_uid


class BKDataCleanUtils:
    """
    bk data clean utils class:
        - to get bkdata_clean
        - to flush Quánxiàn Authority
    """

    def __init__(self, raw_data_id):
        self.raw_data_id = raw_data_id

    def get_bkdata_clean(self):
        config_db_list = BkDataDatabusApi.get_config_db_list(params={"raw_data_id": self.raw_data_id})
        return [config_db for config_db in config_db_list if config_db["storage_type"].lower() == "es"]

    @classmethod
    def get_dict(cls, cleans, db_cleans):
        cleans_dict = {clean["result_table_id"]: clean for clean in cleans}
        db_cleans_dict = {db_clean.result_table_id: db_clean for db_clean in db_cleans}
        return cleans_dict, db_cleans_dict

    @classmethod
    def get_update_model(cls, clean_dict: dict, db_clean_dict: dict):
        clean_dict_set = set(clean_dict.keys())
        db_clean_dict_set = set(db_clean_dict.keys())
        insert_set = clean_dict_set - db_clean_dict_set
        delete_set = db_clean_dict_set - clean_dict_set
        insert_objs = [clean_dict[insert_set_obj] for insert_set_obj in insert_set]
        delete_objs = [db_clean_dict[delete_set_obj] for delete_set_obj in delete_set]
        return insert_objs, delete_objs

    @classmethod
    def insert_objs(cls, insert_objs, collector_config_id: int, bk_biz_id: int, index_set_dict: dict):
        BKDataClean.objects.bulk_create(
            [
                BKDataClean(
                    status=insert_obj["status"],
                    status_en=insert_obj["status_en"],
                    result_table_id=insert_obj["result_table_id"],
                    result_table_name=insert_obj["result_table_name"],
                    result_table_name_alias=insert_obj["result_table_name_alias"],
                    raw_data_id=insert_obj["raw_data_id"],
                    data_name=insert_obj["data_name"],
                    data_alias=insert_obj["data_alias"],
                    data_type=insert_obj["data_type"],
                    storage_type=insert_obj["storage_type"],
                    storage_cluster=insert_obj["storage_cluster"],
                    collector_config_id=collector_config_id,
                    bk_biz_id=bk_biz_id,
                    log_index_set_id=index_set_dict[insert_obj["result_table_id"]]["index_set_id"],
                    updated_by=insert_obj["created_by"],
                    is_authorized=not bool(index_set_dict[insert_obj["result_table_id"]]["bkdata_auth_url"]),
                )
                for insert_obj in insert_objs
            ]
        )
        logger.info("insert BKDataClean collector_config_id {}".format(insert_objs))

    @classmethod
    def delete_objs(cls, delete_objs):
        del_ids = [delete_obj.id for delete_obj in delete_objs]
        BKDataClean.objects.filter(id__in=del_ids).delete()
        logger.info("delete BKDataClean {}".format(del_ids))

    @classmethod
    def create_index_set(cls, insert_objs, bk_biz_id: int, category_id=DEFAULT_CATEGORY_ID):
        index_set_dict = {}
        for insert_obj in insert_objs:
            index_set = IndexSetHandler.create(
                index_set_name=insert_obj["result_table_name"],
                space_uid=bk_biz_id_to_space_uid(bk_biz_id),
                storage_cluster_id=None,
                scenario_id=Scenario.BKDATA,
                indexes=[
                    {
                        "bk_biz_id": bk_biz_id,
                        "result_table_id": insert_obj["result_table_id"],
                        "time_field": "",
                        "time_format": DEFAULT_TIME_FORMAT,
                    }
                ],
                category_id=category_id,
                view_roles=[],
                username=insert_obj["created_by"],
            )
            index_set_dict[insert_obj["result_table_id"]] = {
                "index_set_id": index_set.index_set_id,
                "bkdata_auth_url": index_set.bkdata_auth_url,
            }
            logger.info("create index_set {}".format(insert_obj["result_table_name"]))
        return index_set_dict

    @classmethod
    def delete_index_set(cls, delete_objs):
        for delete_obj in delete_objs:
            IndexSetHandler(index_set_id=delete_obj.log_index_set_id).delete()
            logger.info("delete index_set {}".format(delete_obj.log_index_set_id))

    def update_or_create_clean(self, collector_config_id: int, bk_biz_id: int, category_id: str):
        cleans = self.get_bkdata_clean()
        db_cleans = BKDataClean.objects.filter(raw_data_id=self.raw_data_id)
        cleans_dict, db_cleans_dict = self.get_dict(cleans=cleans, db_cleans=db_cleans)
        insert_objs, delete_objs = self.get_update_model(clean_dict=cleans_dict, db_clean_dict=db_cleans_dict)
        index_set_dict = self.create_index_set(insert_objs=insert_objs, bk_biz_id=bk_biz_id, category_id=category_id)
        self.insert_objs(
            insert_objs=insert_objs,
            collector_config_id=collector_config_id,
            bk_biz_id=bk_biz_id,
            index_set_dict=index_set_dict,
        )
        self.delete_index_set(delete_objs=delete_objs)
        self.delete_objs(delete_objs=delete_objs)
        logger.info(
            "complete whole clean sync collector_config_id: {collector_config_id} bk_biz_id:{bk_biz_id}".format(
                collector_config_id=collector_config_id, bk_biz_id=bk_biz_id
            )
        )

    @staticmethod
    def lock_sync_clean(bk_biz_id: int):
        token = uniqid()
        return cache.set(
            BKDataCleanUtils._generate_sync_key(bk_biz_id=bk_biz_id), token, timeout=MAX_SYNC_CLEAN_TTL, nx=True
        )

    @staticmethod
    def unlock_sync_clean(bk_biz_id: int):
        cache.delete(BKDataCleanUtils._generate_sync_key(bk_biz_id=bk_biz_id))

    @staticmethod
    def _generate_sync_key(bk_biz_id: int):
        return "sync_clean_{bk_biz_id}".format(bk_biz_id=bk_biz_id)
