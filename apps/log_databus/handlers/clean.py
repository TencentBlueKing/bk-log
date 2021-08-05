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
from apps.log_databus.exceptions import CleanTemplateNotExistException, CleanTemplateRepeatException
from apps.log_databus.models import CleanTemplate, BKDataClean
from apps.log_databus.utils.bkdata_clean import BKDataCleanUtils
from apps.models import model_to_dict


class CleanHandler(object):
    def __init__(self, collector_config_id):
        self.collector_config_id = collector_config_id

    def refresh(self, raw_data_id, bk_biz_id):
        bkdata_clean_utils = BKDataCleanUtils(raw_data_id=raw_data_id)
        bkdata_clean_utils.update_or_create_clean(collector_config_id=self.collector_config_id, bk_biz_id=bk_biz_id)
        return [bkdata_clean.result_table_name for bkdata_clean in BKDataClean.objects.filter(raw_data_id=raw_data_id)]


class CleanTemplateHandler(object):
    def __init__(self, clean_template_id=None):
        self.clean_template_id = clean_template_id
        self.data = None
        if clean_template_id:
            try:
                self.data = CleanTemplate.objects.get(clean_template_id=self.clean_template_id)
            except CleanTemplate.DoesNotExist:
                raise CleanTemplateNotExistException()

    def retrieve(self):
        return model_to_dict(self.data)

    def create_or_update(self, params: dict):
        model_fields = {
            "name": params["name"],
            "clean_type": params["clean_type"],
            "etl_params": params["etl_params"],
            "etl_fields": params["etl_fields"],
            "bk_biz_id": params["bk_biz_id"],
        }
        if self._check_clean_template_exist(name=model_fields["name"], bk_biz_id=model_fields["bk_biz_id"]):
            raise CleanTemplateRepeatException(
                CleanTemplateRepeatException.MESSAGE.format(
                    bk_biz_id=model_fields["bk_biz_id"], name=model_fields["name"]
                )
            )
        if not self.data:
            return model_to_dict(CleanTemplate.objects.create(**model_fields))

        for key, value in model_fields.items():
            setattr(self.data, key, value)
        self.data.save()
        return model_to_dict(self.data)

    def destroy(self):
        return self.data.delete()

    def _check_clean_template_exist(self, name: str, bk_biz_id: int):
        """
        judge the same bk_biz_id and same name clean_template exist
        """
        if not self.data:
            return CleanTemplate.objects.filter(name=name, bk_biz_id=bk_biz_id).exists()

        return (
            CleanTemplate.objects.filter(name=name, bk_biz_id=bk_biz_id)
            .exclude(clean_template_id=self.clean_template_id)
            .exists()
        )
