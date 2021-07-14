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

"""
项目同步
1. 从CC拉取业务列表及人员信息
2. 更新项目信息
3. 更新用户组信息
"""
from celery.schedules import crontab  # noqa
from celery.task import periodic_task  # noqa
from django.conf import settings  # noqa

from apps.utils.log import logger  # noqa
from apps.log_search.handlers.biz import BizHandler  # noqa
from apps.log_search.models import ProjectInfo  # noqa
from apps.utils.db import array_chunk  # noqa
from apps.utils.lock import share_lock  # noqa


@periodic_task(run_every=crontab(minute="*/1"), queue="sync")
@share_lock()
def sync():
    if settings.USING_SYNC_BUSINESS:
        # 同步CMDB业务信息
        sync_projects()
        return True
    return False


def sync_projects():
    """
    同步CMDB业务信息
    """
    businesses = BizHandler.list()
    if not businesses:
        logger.error("[log_search][tasks]get business error")
        return False

    objs = []
    # 项目信息
    projects = ProjectInfo.get_cmdb_projects()

    # 用户组
    for business in businesses:
        bk_biz_id = int(business["bk_biz_id"])
        if not projects.get(bk_biz_id):
            objs.append(
                ProjectInfo(
                    project_name=business["bk_biz_name"],
                    bk_biz_id=business["bk_biz_id"],
                    bk_app_code=settings.APP_CODE,
                    time_zone=business.get("time_zone", settings.TIME_ZONE),
                )
            )
        else:
            has_deleted = ProjectInfo.objects.filter(bk_biz_id=bk_biz_id, is_deleted=True)
            if has_deleted:
                has_deleted.update(is_deleted=False)

            # 增加修改project_name
            ProjectInfo.objects.filter(bk_biz_id=bk_biz_id).exclude(project_name=business["bk_biz_name"]).update(
                project_name=business["bk_biz_name"]
            )
            del projects[int(business["bk_biz_id"])]

    if objs:
        chunks = array_chunk(objs)
        for chunk in chunks:
            ProjectInfo.objects.bulk_create(chunk)
        logger.info("[log_search][tasks]sync business nums: {}".format(len(objs)))

    if projects:
        ProjectInfo.objects.filter(project_id__in=projects.values()).delete()

    logger.info(
        "[sync_projects] businesses=>{}, sync=>{}, delete=>{}".format(len(businesses), len(objs), len(projects))
    )
    return True
