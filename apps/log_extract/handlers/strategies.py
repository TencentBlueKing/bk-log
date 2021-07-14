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
from django.db import transaction

from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.log_search.handlers.meta import MetaHandler
from apps.log_extract import exceptions
from apps.log_extract.models import Strategies
from apps.utils.local import get_request_username
from apps.decorators import user_operation_record


class StrategiesHandler:
    def __init__(self, strategy_id=None):
        super().__init__()
        self.strategy_id = strategy_id
        if strategy_id:
            try:
                self.strategy = Strategies.objects.get(strategy_id=self.strategy_id)
            except Strategies.DoesNotExist:
                raise exceptions.StrategyDoesNotExist(
                    exceptions.StrategyDoesNotExist.MESSAGE.format(strategy_id=self.strategy_id)
                )
        else:
            self.strategy = None

    @transaction.atomic()
    def update_or_create(
        self, strategy_name, user_list, bk_biz_id, select_type, modules, visible_dir, file_type, operator
    ):
        # 更新策略后，策略名称可以和更新策略前一致，但不可以和其他strategy_id对应下的策略同名
        is_strategy_name_existed = Strategies.objects.filter(strategy_name=strategy_name, bk_biz_id=bk_biz_id)

        # 当前时策略更新请求
        if self.strategy_id:
            is_strategy_name_existed = is_strategy_name_existed.exclude(strategy_id=self.strategy_id)

        if is_strategy_name_existed:
            raise exceptions.StrategyNameExisted(exceptions.StrategyNameExisted.MESSAGE.format(strategy_name))

        # operator必须是原来的执行人或自己
        user = MetaHandler.get_user()
        operators = [user["operator"]]
        if self.strategy_id:
            operators.append(self.strategy.operator)
        if operator not in operators:
            raise exceptions.StrategyOperatorNotAllow()

        defaults = {
            "strategy_name": strategy_name,
            "user_list": user_list,
            "bk_biz_id": bk_biz_id,
            "select_type": select_type,
            "modules": modules,
            "visible_dir": visible_dir,
            "file_type": file_type,
            "operator": operator,
        }
        obj, created = Strategies.objects.update_or_create(strategy_id=self.strategy_id, defaults=defaults)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": bk_biz_id,
            "record_type": UserOperationTypeEnum.LOG_EXTRACT_STRATEGY,
            "record_object_id": obj.strategy_id,
            "action": UserOperationActionEnum.CREATE if created else UserOperationActionEnum.UPDATE,
            "params": defaults,
        }
        user_operation_record.delay(operation_record)

    @transaction.atomic()
    def delete_strategies(self):
        self.strategy.delete()

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.strategy.bk_biz_id,
            "record_type": UserOperationTypeEnum.LOG_EXTRACT_STRATEGY,
            "record_object_id": self.strategy.strategy_id,
            "action": UserOperationActionEnum.DESTROY,
            "params": "",
        }
        user_operation_record.delay(operation_record)

        return True
