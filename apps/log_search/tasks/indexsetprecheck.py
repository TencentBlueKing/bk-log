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

from typing import List, Dict
from apps.utils.log import logger
from apps.log_search.models import LogIndexSetData, LogIndexSet, Scenario
from apps.api import BkDataMetaApi, TransferApi
from celery.task import periodic_task
from celery.schedules import crontab


class IndexSetPreCheckIns(object):
    @classmethod
    def pre_check_indexset(cls):
        # 初始化数据库内容进入内存
        # 分析出需要分析的索引集
        index_set_rt_map: dict = cls._set_index_set_rt_map()
        # 根据bizid和场景去拉取
        need_to_fetch_biz_scenario_list: list = cls._analyse_need_to_fetch_biz(index_set_rt_map)
        schema_dict_template: dict = cls._fetch_schema(need_to_fetch_biz_scenario_list)
        new_need_to_check_index_set: dict = cls._mark_field_for_need_to_check_index_set(
            index_set_rt_map, schema_dict_template
        )
        ret_dict: dict = cls._analyse_log_set(new_need_to_check_index_set)
        cls._update_pre_check_ret_to_db(ret_dict)

        logger.info(
            "[index_set_pre_check] index_set_rt_map=>{index_set_rt_map}, "
            "ret_dict_except=>{ret_dict_except}".format(
                index_set_rt_map=len(index_set_rt_map),
                ret_dict_except=",".join([key for (key, item) in ret_dict.items() if not item.get("ret")]),
            )
        )
        return True

    @classmethod
    def _set_index_set_rt_map(cls) -> Dict:
        """
        初始化数据库数据: 获取超过一条索引的索引集数据
        """
        index_set_rt_map: dict = {}
        all_log_index_set_data_obj = (
            LogIndexSetData.objects.filter(is_deleted=False)
            .order_by("index_id")
            .values("index_id", "index_set_id", "bk_biz_id", "result_table_id")
        )
        all_log_index_set_obj = LogIndexSet.objects.filter(is_deleted=False).values(
            "index_set_id", "index_set_name", "scenario_id"
        )

        for item in all_log_index_set_obj:
            index_set_id: int = item.get("index_set_id")
            scenario_id: str = item.get("scenario_id")

            tmp_detail_list: List = []
            for _item in all_log_index_set_data_obj:
                _index_set_id: int = _item.get("index_set_id")
                if index_set_id == _index_set_id:
                    _item.update({"scenario_id": scenario_id})
                    tmp_detail_list.append(_item)

            if len(tmp_detail_list) > 1:
                index_set_rt_map.update({index_set_id: tmp_detail_list})
            return index_set_rt_map

    @classmethod
    def _analyse_need_to_fetch_biz(cls, need_to_check_index_set) -> List:
        need_to_fetch_biz_scenario_list: list = []
        for k, v in need_to_check_index_set.items():
            detail_list: List = v
            for item in detail_list:
                bk_biz_id: int = item.get("bk_biz_id")
                scenario_id: str = item.get("scenario_id")
                tmp: tuple = (bk_biz_id, scenario_id)
                if tmp not in need_to_fetch_biz_scenario_list:
                    need_to_fetch_biz_scenario_list.append(tmp)
        return need_to_fetch_biz_scenario_list

    # fetch
    @classmethod
    def _fetch_schema(cls, need_to_fetch_biz_scenario_list: list) -> dict:
        schema_dict_template: dict = {"bkdata": {}, "log": {}}
        fetch_ret_list_log: list = []
        fetch_ret_list_bkdata: list = []

        for item in need_to_fetch_biz_scenario_list:
            bk_biz_id: int = item[0]
            scenario_id: str = item[1]
            if scenario_id in [Scenario.LOG]:
                ret: dict = cls._fetch_from_meta(bk_biz_id)
                fetch_ret_list_log.extend(ret)
            elif scenario_id in [Scenario.BKDATA]:
                ret: dict = cls._fetch_from_bkdata(bk_biz_id)
                fetch_ret_list_bkdata.extend(ret)
            else:
                continue
        # 将log拉取到的内容放入字典里面
        for table_info_log in fetch_ret_list_log:
            ret_table_id: str = table_info_log.get("table_id")
            field_list: list = table_info_log.get("field_list")
            schema_dict_template["log"].update({ret_table_id: field_list})

        # 将bkdata拉取到的内容放入到字典里面
        for table_info_bkdata in fetch_ret_list_bkdata:
            ret_table_id: str = table_info_bkdata.get("result_table_id")
            field_list: list = table_info_bkdata.get("field_list")
            schema_dict_template["bkdata"].update({ret_table_id: field_list})

        return schema_dict_template

    # 从meta拉取
    @classmethod
    def _fetch_from_meta(cls, bk_biz_id: int) -> dict:
        transfer_api_response: Dict = TransferApi.list_result_table({"bk_biz_id": bk_biz_id})
        return transfer_api_response

    @classmethod
    def _fetch_from_bkdata(cls, bk_biz_id: int) -> dict:
        meta_api_response: Dict = BkDataMetaApi.result_tables({"bk_biz_id": bk_biz_id})
        return meta_api_response

    @classmethod
    def _find_field_in_log_fetch_result(cls, table_id: str, fetch_ret_dict_log: dict):
        field_list: list = fetch_ret_dict_log.get(table_id, None)
        return field_list

    @classmethod
    def _find_field_in_bkdata_fetch_result(cls, result_table_id: str, fetch_ret_dict_bkdata: dict):
        field_list = fetch_ret_dict_bkdata.get(result_table_id, None)
        return field_list

    # 找到对应的field
    @classmethod
    def _mark_field_for_need_to_check_index_set(cls, need_to_check_index_set: dict, schema_dict_template) -> dict:  # pylint: disable=function-name-too-long
        for k, v in need_to_check_index_set.items():
            # index_set_id: int = k
            need_to_check_list: list = v
            for item in need_to_check_list:
                result_table_id: str = item.get("result_table_id")
                scenario_id: str = item.get("scenario_id")
                if scenario_id == Scenario.LOG:
                    fields: list = cls._find_field_in_log_fetch_result(result_table_id, schema_dict_template["log"])
                    if fields:
                        item.update({"fields": fields})
                elif scenario_id == Scenario.BKDATA:
                    fields: list = cls._find_field_in_bkdata_fetch_result(
                        result_table_id, schema_dict_template["bkdata"]
                    )
                    if fields:
                        item.update({"fields": fields})
                else:
                    continue
        return need_to_check_index_set

    # 根据拉取的schema 分析索引集的schema情况
    @classmethod
    def _analyse_log_set(cls, need_to_check_index_set: dict) -> dict:
        ret_dict: dict = {}
        for k, v in need_to_check_index_set.items():
            index_set_id: int = k
            index_set_data_list: list = v
            ret = cls._analyser(index_set_data_list)
            ret_dict.update({index_set_id: ret})
        return ret_dict

    @classmethod
    def _analyser(cls, detail_list: List):
        if len(detail_list) >= 1:
            mark_point_index_set_data: dict = detail_list[0]
            mark_point_index_set_data_fields: list = mark_point_index_set_data.get("fields")
            mark_point_index_set_data_field_names: list = [
                x.get("field_name") for x in mark_point_index_set_data_fields
            ]
            mark_point_index_set_data_field_names = sorted(mark_point_index_set_data_field_names)

            diff_tag: bool = True
            diff_message_list: list = []
            for item in detail_list:
                fields_list = item.get("fields")
                if fields_list:
                    tmp_field_name_list: list = []
                    for field in fields_list:
                        field_name = field.get("field_name")
                        tmp_field_name_list.append(field_name)
                    sorted_tmp_field_name_list: list = sorted(tmp_field_name_list)
                    if sorted_tmp_field_name_list == mark_point_index_set_data_field_names:
                        continue
                    else:
                        diff_tag = False
                        add_list: list = [
                            x for x in sorted_tmp_field_name_list if x not in mark_point_index_set_data_field_names
                        ]
                        minus_list: list = [
                            y for y in mark_point_index_set_data_field_names if y not in sorted_tmp_field_name_list
                        ]
                        ret_message = "{} add fields {}, lack of fields {}".format(
                            item.get("result_table_id"), ",".join(add_list), ",".join(minus_list)
                        )
                        diff_message_list.append(ret_message)
            return {
                "ret": diff_tag,
                "ret_data": "refer to the {}, {}".format(
                    mark_point_index_set_data.get("result_table_id"), "; ".join(diff_message_list)
                ),
            }

        else:
            return {"ret": True, "ret_data": ""}

    @classmethod
    def _update_pre_check_ret_to_db(cls, ret_dict: dict):
        for k, v in ret_dict.items():
            index_set_id: int = k
            pre_check_tag: bool = v.get("ret", True)
            pre_check_msg: str = v.get("ret_data", "")
            LogIndexSet.objects.filter(index_set_id=index_set_id).update(
                **{"pre_check_tag": pre_check_tag, "pre_check_msg": pre_check_msg}
            )


@periodic_task(run_every=crontab(hour="*/12"), queue="pre_check_index_set")
def index_set_pre_check():
    IndexSetPreCheckIns.pre_check_indexset()
    return None
