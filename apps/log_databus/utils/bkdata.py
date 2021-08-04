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
from apps.api import BkDataDatabusApi
from apps.log_databus.models import BKDataClean


class BKDataCleanUtils:
    """
    bk data clean utils class:
        - to get bkdata_clean
        - to flush Quánxiàn Authority
    """

    def __init__(self, raw_data_id):
        self.raw_data_id = raw_data_id

    def get_bkdata_clean(self):
        return BkDataDatabusApi.get_config_db_list(params={"raw_data_id": self.raw_data_id})

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
    def insert_db(cls, insert_objs, collector_config_id: int, bk_biz_id: int):
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
                )
                for insert_obj in insert_objs
            ]
        )

    @classmethod
    def delete_db(cls, delete_objs):
        BKDataClean.objects.filter(id__in=[delete_obj.id for delete_obj in delete_objs]).delete()

    def update_or_create_clean(self, collector_config_id: int, bk_biz_id: int):
        cleans = self.get_bkdata_clean()
        db_cleans = BKDataClean.objects.filter(raw_data_id=self.raw_data_id)
        cleans_dict, db_cleans_dict = self.get_dict(cleans=cleans, db_cleans=db_cleans)
        insert_model, delete_model = self.get_update_model(clean_dict=cleans_dict, db_clean_dict=db_cleans_dict)
        self.insert_db(insert_objs=insert_model, collector_config_id=collector_config_id, bk_biz_id=bk_biz_id)
        self.delete_db(delete_objs=delete_model)
