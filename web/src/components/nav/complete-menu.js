/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import i18n from '@/language/i18n';

export const menuArr = [
  {
    name: i18n.t('检索'),
    id: 'retrieve',
    level: 1,
  },
  {
    name: i18n.t('仪表盘'),
    id: 'dashboard',
    level: 1,
    dropDown: true,
    children: [{
      id: 'create_dashboard',
      name: i18n.t('新建仪表盘'),
      level: 2,
      isDashboard: true,
      project_manage: true,
    }, {
      id: 'create_folder',
      name: i18n.t('新建目录'),
      level: 2,
      isDashboard: true,
      project_manage: true,
    }, {
      id: 'import_dashboard',
      name: i18n.t('导入仪表盘'),
      level: 2,
      isDashboard: true,
      project_manage: true,
    }],
  },
  {
    name: i18n.t('日志提取'),
    id: 'extract',
    level: 1,
  },
  {
    name: i18n.t('调用链'),
    id: 'trace',
    level: 1,
  },
  {
    name: i18n.t('监控策略'),
    id: 'monitor',
    level: 1,
    children: [
      {
        name: i18n.t('告警策略'),
        id: 'alarmStrategy',
        level: 2,
        children: [
          {
            name: i18n.t('新建'),
            id: 'addstrategy',
            level: 3,
          },
          {
            name: i18n.t('编辑'),
            id: 'editstrategy',
            level: 3,
          },
        ],
      },
    ],
  },
  {
    name: i18n.t('管理'),
    id: 'manage',
    level: 1,
    dropDown: true,
    children: [
      {
        name: i18n.t('数据接入'),
        id: 'manage',
        level: 2,
        children: [
          {
            name: i18n.t('采集接入'),
            id: 'collectAccess',
            level: 3,
            children: [
              {
                name: i18n.t('新建采集'),
                id: 'collectAdd',
                level: 4,
              },
              {
                name: i18n.t('编辑采集项'),
                id: 'collectEdit',
                level: 4,
              },
              {
                name: i18n.t('启用采集项'),
                id: 'collectStart',
                level: 4,
              },
              {
                name: i18n.t('停用采集项'),
                id: 'collectStop',
                level: 4,
              },
              {
                name: i18n.t('字段清洗'),
                id: 'collectField',
                level: 4,
              },
              {
                name: i18n.t('配置详情'),
                id: 'allocation',
                level: 4,
                children: [
                  {
                    name: i18n.t('数据采样'),
                    id: 'jsonFormat',
                    level: 5,
                  },
                ],
              },
            ],
          },
          {
            name: i18n.t('ES源接入'),
            id: 'esAccess',
            level: 3,
          },
        ],
      },
      {
        name: i18n.t('索引集管理'),
        id: 'indexSet',
        level: 2,
        children: [
          {
            name: i18n.t('新建索引集'),
            id: 'addIndexSet',
            level: 3,
          },
          {
            name: i18n.t('编辑索引集'),
            id: 'editIndexSet',
            level: 3,
          },
        ],
      },
      {
        name: i18n.t('链路配置'),
        id: 'linkConfiguration',
        level: 2,
      },
      {
        name: i18n.t('用户组配置'),
        id: 'permissionGroup',
        level: 2,
      },
      {
        name: i18n.t('v3迁移'),
        id: 'migrate',
        level: 2,
      },
      {
        name: i18n.t('日志提取配置'),
        id: 'manageExtract',
        level: 2,
      },
    ],
  },
];
