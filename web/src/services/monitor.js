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

/**
 * 监控策略
 */

// 监控策略列表
const list = {
  url: '/monitor/policy/',
  method: 'get',
};

// 创建监控策略
const create = {
  url: '/monitor/policy/',
  method: 'post',
};

// 删除监控策略
const remove = {
  url: '/monitor/policy/:policy_id/',
  method: 'delete',
};

// 监控策略启动
const start = {
  url: '/monitor/policy/:policy_id/start/',
  method: 'post',
};

// 监控策略停止
const stop = {
  url: '/monitor/policy/:policy_id/stop/',
  method: 'post',
};

// 编辑监控策略
const updata = {
  url: '/monitor/policy/:policy_id/',
  method: 'put',
};

// 监控策略详情
const particulars = {
  url: '/monitor/policy/:policy_id/',
  method: 'get',
};

// 获取监控类型列表
const type = {
  url: '/monitor/',
  method: 'get',
};

// 获取告警等级
const levels = {
  url: '/monitor/alarm/levels/',
  method: 'get',
};

// 获取告警记录
const alarm = {
  url: '/monitor/alarm/',
  method: 'get',
};

// 获取屏蔽策略列表
const shields = {
  url: '/monitor/shields/',
  method: 'get',
};

// 获取屏蔽类型
const shieldsType = {
  url: '/monitor/shields/type/',
  method: 'get',
};

// 新增屏蔽策略
const addShields = {
  url: '/monitor/shields/',
  method: 'post',
};

// 删除屏蔽策略
const removeShields = {
  url: '/monitor/shields/:shield_id/',
  method: 'delete',
};

// 获取屏蔽策略详情
const shieldsInfo = {
  url: '/monitor/shields/:shield_id/',
  method: 'get',
};

// 更新屏蔽策略
const updateShields = {
  url: '/monitor/shields/:shield_id/',
  method: 'put',
};

// 获取索引集
const index = {
  url: '/monitor/index_set/',
  method: 'get',
};

export {
  list,
  create,
  remove,
  start,
  updata,
  stop,
  type,
  particulars,
  levels,
  alarm,
  shields,
  shieldsType,
  addShields,
  removeShields,
  shieldsInfo,
  updateShields,
  index,
};
