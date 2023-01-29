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

// 监控策略列表
const list = {
  message: '',
  code: 0,
  data: {
    total: 100,
    took: 0.29,
    list: [
      {
        policy_id: 1,
        policy_name: '登陆异常',
        monitor_id: 'smart',
        monitor_name: '智能监控',
        space_uid: 1,
        index_set_id: 1,
        index_set_name: '索引集名称',
        additions: '检索条件',
        level: '轻微',
        notice_id: 1,
        is_active: '是否可用',
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
        policy_status: 1,
        policy_status_name: '运行中',
      },
    ],
  },
  result: true,
};

// 监控创建
const create = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 监控删除
const remove = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 监控启动
const start = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 监控策略-停止
const stop = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 监控更新
const updata = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 监控更新
const particulars = {
  message: '',
  code: 0,
  data: {
    policy_name: '登陆异常',
    monitor_id: 'smart',
    monitor_name: '智能监控',
    space_uid: 1,
    index_set_id: 1,
    index_set_name: '索引集名称',
    additions: '检索条件',
    level: '告警等级',
    notice_config: {
      notice_type: ['weixin', 'mail'],
      alarm_begin_time: '2019-01-01 11:11:11',
      alarm_end_time: '2019-01-02 11:11:11',
      notice_roles: [1, 2, 3],
    },
    monitor_config: {
      config_method: 'gte',
      config_threshold: 10,
      config_range: 5,
      converge_check_window: 6,
      converge_count: 1,
      converge_alarm_window: 6,
    },
    is_active: false,
  },
  result: true,
};

// 获取类型
const type = {
  message: '',
  code: 0,
  data: [
    {
      monitor_id: 'smart',
      monitor_name: '智能监控',
      properties: {
        converge_check_window: {
          field_alias: '周期',
          field_type: 'int',
          choices: [
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 5],
            [6, 6],
            [7, 7],
            [8, 8],
            [9, 9],
            [10, 10],
            [20, 20],
          ],
        },
        converge_count: {
          field_alias: '算法',
          field_type: 'int',
          choices: [
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 5],
          ],
        },
        converge_alarm_window: {
          field_alias: '收敛',
          field_type: 'int',
          choices: [
            [0, 0],
            [1, 1],
            [6, 6],
            [12, 12],
            [24, 24],
          ],
        },
        model_id: {
          field_alias: '监控模型',
          field_type: 'string',
          choices: [
            ['anomaly_detection', '异常检测场景'],
          ],
        },
      },
      created_at: '2019-10-10 11:11:11',
      created_by: 'user',
      updated_at: '2019-10-10 11:11:11',
      updated_by: 'user',
    },
    {
      monitor_id: 'aa',
      monitor_name: 'yuzhi监控',
    },
  ],
  result: true,
};

// 获取告警级别
const levels = {
  message: '',
  code: 0,
  data: [
    {
      id: 1,
      name: '致命',
      color: '#EA3636',
    },
    {
      id: 2,
      name: '预警',
      color: '#FF9C01',
    },
    {
      id: 3,
      name: '提醒',
      color: '#FFD000',
    },
  ],
  result: true,
};

// 获取告警记录
const alarm = {
  message: '',
  code: 0,
  data: {
    total: 100,
    took: 0.29,
    list: [
      {
        policy_id: 1,
        policy_name: '登陆异常',
        monitor_id: 'smart',
        monitor_name: '智能监控',
        additions: '检索条件',
        content: '告警内容',
        level: '告警等级',
        notice_time: '告警时间',
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
      },
    ],
  },
  result: true,
};

// 屏蔽策略列表
const shields = {
  message: '',
  code: 0,
  data: {
    total: 100,
    took: 0.29,
    list: [
      {
        policy_id: 1,
        policy_name: '登陆异常',
        monitor_id: 'smart',
        monitor_name: '智能监控',
        additions: '检索条件',
        content: '告警内容',
        level: '告警等级',
        policy_time: '屏蔽时间',
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
      },
    ],
  },
  result: true,
};

// 屏蔽类型
const shieldsType = {
  message: '',
  code: 0,
  data: [
    {
      id: 1,
      name: '单次',
    },
    {
      id: 2,
      name: '每天',
    },
    {
      id: 3,
      name: '每周',
    },
    {
      id: 4,
      name: '每月',
    },
  ],
  result: true,
};

// 新增屏蔽策略
const addShields = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

// 删除屏蔽策略
const removeShields = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

// 获取屏蔽策略详情
const shieldsInfo = {
  message: '',
  code: 0,
  data: {
    shield_id: 1,
    space_uid: 11,
    shield_type: 1,
    begin_time: '2019-10-10 10:00:00',
    end_time: '2019-10-10 12:00:00',
    cycle_config: null,
    reason: '屏蔽原因',
    policies: [
      {
        policy_id: 1,
        policy_name: '策略名称',
      },
    ],
    created_at: '2019-10-10 11:11:11',
    created_by: 'user',
    updated_at: '2019-10-10 11:11:11',
    updated_by: 'user',
  },
  result: true,
};

// 更新屏蔽策略
const updateShields = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

export default {
  list,
  create,
  remove,
  start,
  updata,
  stop,
  type,
  alarm,
  levels,
  particulars,
  shields,
  shieldsType,
  addShields,
  removeShields,
  shieldsInfo,
  updateShields,
};
