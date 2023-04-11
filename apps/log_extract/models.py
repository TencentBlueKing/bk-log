# coding=utf-8
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
import operator
from datetime import datetime
from functools import reduce
from typing import List

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from pipeline.service import task_service
from apps.utils.log import logger
from apps.models import (
    OperateRecordModel,
    SoftDeleteModel,
    JsonField,
    MultiStrSplitByCommaFieldText,
    OperateRecordModelManager,
    EncryptionField,
)
from apps.log_extract.constants import ExtractLinkType, PIPELINE_TIME_FORMAT


class Strategies(SoftDeleteModel):
    """用户策略表"""

    strategy_id = models.AutoField(_("策略ID"), primary_key=True, default=None)
    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    strategy_name = models.TextField(_("策略名称"))
    user_list = MultiStrSplitByCommaFieldText(_("用户ID"))
    select_type = models.CharField(_("目标选择类型"), max_length=16)
    modules = JsonField(_("模块列表"))
    visible_dir = MultiStrSplitByCommaFieldText(_("目录列表"))
    file_type = MultiStrSplitByCommaFieldText(_("文件类型"))
    operator = models.CharField(_("作业执行人"), max_length=64, default="")

    class Meta:
        ordering = ["-updated_at"]


class TasksManager(OperateRecordModelManager):
    search_fields = ["ip_list", "file_path", "created_by", "remark"]

    def search(self, keyword):
        if keyword:
            filter_query = [Q(**{f"{field}__icontains": keyword}) for field in self.search_fields]
            filter_q = reduce(operator.or_, filter_query)
            return self.filter(filter_q)
        return self


class Tasks(OperateRecordModel):
    """任务记录 一个"下载"行为记作一个"Task" """

    objects = TasksManager()
    task_id = models.AutoField(_("任务记录id"), primary_key=True)
    bk_biz_id = models.IntegerField(_("业务id"), db_index=True)
    ip_list = MultiStrSplitByCommaFieldText(_("业务机器ip"))
    file_path = MultiStrSplitByCommaFieldText(_("文件列表"))

    filter_type = models.CharField(_("过滤类型"), max_length=16, null=True, blank=True)
    filter_content = JsonField(_("过滤内容"), null=True, blank=True)

    download_status = models.CharField(_("当前文件下载状态"), max_length=64, null=True, blank=True)
    expiration_date = models.DateTimeField(_("任务过期时间"), default=None)
    pipeline_id = models.CharField(_("流水线ID"), max_length=128, null=True, blank=True, db_index=True)
    pipeline_components_id = JsonField(_("流水线组件ID"), null=True, blank=True)

    job_task_id = models.BigIntegerField(_("文件分发ID"), null=True, blank=True)

    # 调创建上传任务的API
    cstone_upload_ticket = models.BigIntegerField(_("上传票据"), null=True, blank=True)
    cstone_upload_random = models.TextField(_("上传随机值"), null=True, blank=True)

    # 创建中转服务器到云石的上传任务
    job_upload_task_id = models.BigIntegerField(_("任务上传ID"), null=True, blank=True)  # 查询上传脚本的执行结果, 执行结果里有云石返回的task_id
    cstone_upload_task_id = models.BigIntegerField(_("云石上传ID"), null=True, blank=True)  # 用于查询中转服务器到云石的上传情况

    # 云石上待下载的文件路径
    cstone_file_path = models.CharField(_("云石文件路径"), default=None, max_length=64, null=True, blank=True)
    # 等到上传完毕后，调创建下载链接的API
    cstone_download_task_id = models.BigIntegerField(_("云石任务ID"), null=True, blank=True)
    cstone_download_bk_biz_id = models.BigIntegerField(_("云石下载业务ID"), null=True, blank=True)
    cstone_download_ticket = models.BigIntegerField(_("下载票据"), null=True, blank=True)  # 根据票据向云石网盘发起下载请求
    cstone_download_random = models.TextField(_("下载随机值"), null=True, blank=True)
    task_process_info = models.TextField(_("任务过程信息"), null=True, blank=True)
    remark = models.TextField(_("备注"), null=True, blank=True)

    preview_directory = models.CharField(_("预览目录"), null=True, blank=True, max_length=255)
    preview_ip = models.TextField(_("预览地址ip"), null=True, blank=True)
    preview_time_range = models.CharField(_("预览日期"), max_length=10, null=True, blank=True)
    preview_is_search_child = models.BooleanField(_("预览是否搜索子目录"), default=False, blank=True)
    preview_start_time = models.CharField(_("预览开始日期"), null=True, blank=True, max_length=20)
    preview_end_time = models.CharField(_("预览结束日期"), null=True, blank=True, max_length=20)

    ex_data = JsonField(_("额外数据"), null=True, blank=True)
    cos_file_name = models.CharField(_("cos对象文件名称"), null=True, blank=True, max_length=255)
    link_id = models.IntegerField(_("链路id"), null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def get_link_type(self):
        try:
            return ExtractLink.objects.get(link_id=self.link_id).link_type
        except ExtractLink.DoesNotExist:
            return ""

    def get_extract(self):
        from apps.log_extract.handlers.extract import ExtractLinkFactory

        return ExtractLinkFactory.get_link(self.get_link_type())()

    def get_link(self):
        return ExtractLink.objects.filter(link_id=self.link_id).first()

    def total_elapsed(self):
        try:
            task_status = task_service.get_state(self.pipeline_id)
        except Exception:  # pylint: disable=broad-except
            # 存在多主机，单主机日志下载的情况，因此有可能有些pipeline节点未执行
            logger.info("pipeline任务不存在，pipeline_id=>[{}]".format(self.pipeline_id))
            return "0s"

        component_status_list = []
        if "activities" not in self.pipeline_components_id:
            return "0s"
        for component_id, component_info in self.pipeline_components_id["activities"].items():
            # 这里有可能有些pipeline组件并未执行
            try:
                task_status["children"][component_id]["name"] = component_info["name"]
                component_status_list.append(task_status["children"][component_id])
            except KeyError:
                pass
        return f"{self._cal_total_time(component_status_list)}s"

    def _cal_total_time(self, components: List[dict]):
        return sum(
            [
                (
                    datetime.strptime(component["finish_time"], PIPELINE_TIME_FORMAT)
                    - datetime.strptime(component["start_time"], PIPELINE_TIME_FORMAT)
                ).seconds
                for component in components
                if component["finish_time"] is not None
            ]
        )

    total_elapsed.short_description = _("总耗时")

    def ip_num(self):
        return len(self.ip_list)

    ip_num.short_description = _("IP数量")

    def download_file_detail(self):
        all_file_size = sum(int(ip.get("all_origin_file_size", 0)) for ip in self.ex_data.values())
        all_file_num = sum(int(ip.get("file_count", 0)) for ip in self.ex_data.values())
        all_pack_file_size = sum(int(ip.get("all_pack_file_size", 0)) for ip in self.ex_data.values())
        ret = [
            _("下载文件总大小: {all_pack_file_size}kb").format(all_pack_file_size=all_pack_file_size),
            _("下载原始文件原始总大小: {all_file_size}kb").format(all_file_size=all_file_size),
            _("下载文件总数量: {all_file_num}kb").format(all_file_num=all_file_num),
        ]

        return " ".join(ret)

    download_file_detail.short_description = _("下载文件统计")


class ExtractLink(OperateRecordModel):
    name = models.CharField(_("链路名称"), max_length=255)
    link_id = models.AutoField(_("链路id"), primary_key=True)
    link_type = models.CharField(_("链路类型"), max_length=20, default=ExtractLinkType.COMMON.value)
    operator = models.CharField(_("执行人"), max_length=255)
    op_bk_biz_id = models.IntegerField(_("执行bk_biz_id"))
    qcloud_secret_id = EncryptionField(_("腾讯云SecretId"), default="", null=True, blank=True, help_text=_("内网链路不需要填写"))
    qcloud_secret_key = EncryptionField(_("腾讯云SecretKey"), default="", null=True, blank=True, help_text=_("内网链路不需要填写"))
    qcloud_cos_bucket = models.CharField(
        _("腾讯云Cos桶名称"), max_length=255, default="", blank=True, help_text=_("内网链路不需要填写")
    )
    qcloud_cos_region = models.CharField(
        _("腾讯云Cos区域"), max_length=255, default="", blank=True, help_text=_("内网链路不需要填写")
    )
    is_enable = models.BooleanField(_("是否启用"), default=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, blank=True, db_index=True, null=True)

    class Meta:
        verbose_name = _("提取链路 (第一次配置链路之后 需要重新部署saas && 暂时只支持linux及安装了cgwin的系统)")
        verbose_name_plural = _("提取链路 (第一次配置链路之后 需要重新部署saas && 暂时只支持linux及安装了cgwin的系统)")


class ExtractLinkHost(models.Model):
    target_dir = models.CharField(_("挂载目录"), max_length=255, default="")
    bk_cloud_id = models.IntegerField(_("主机云区域id"))
    ip = models.GenericIPAddressField(_("主机ip"))
    link = models.ForeignKey(ExtractLink, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("链路中转机")
        verbose_name_plural = _("链路中转机")
