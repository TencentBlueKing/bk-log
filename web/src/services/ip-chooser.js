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
 * log-ip-selector
 */

// 批量获取含各节点主机数量的拓扑树
const trees = {
  url: '/ipchooser/topo/trees/',
  method: 'post',
};

// 根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息
const queryHosts = {
  url: '/ipchooser/topo/query_hosts/',
  method: 'post',
};

// 查询多个节点拓扑路径
const queryPath = {
  url: '/ipchooser/topo/query_path/',
  method: 'post',
};

// 获取多个拓扑节点的主机Agent状态统计信息
const agentStatistics = {
  url: '/ipchooser/topo/agent_statistics/',
  method: 'post',
};

// 根据多个拓扑节点与搜索条件批量分页查询所包含的主机ID信息
const queryHostIdInfos = {
  url: '/ipchooser/topo/query_host_id_infos/',
  method: 'post',
};

// 根据主机关键信息获取机器详情信息
const details = {
  url: '/ipchooser/host/details/',
  method: 'post',
};

// 检查节点
const check = {
  url: '/ipchooser/host/check/',
  method: 'post',
};

// 全局配置列表
const globalConfig = {
  url: '/ipchooser/config/global/',
  method: 'get',
};

// 拉取配置
const getConfig = {
  url: '/ipchooser/config/batch_get/',
  method: 'post',
};

// 更新配置
const updateConfig = {
  url: '/ipchooser/config/update_config/',
  method: 'post',
};

// 拉取动态分组列表
const dynamicGroups = {
  url: '/ipchooser/dynamic_group/groups/',
  method: 'post',
};

// 获取动态分组下节点
const executeDynamicGroup = {
  url: '/ipchooser/dynamic_group/execute/',
  method: 'post',
};

// 获取动态分组下所有主机的Agent状态
const groupAgentStatistics = {
  url: '/ipchooser/dynamic_group/agent_statistics/',
  method: 'post',
};

// 拉取模板列表
const templates = {
  url: '/ipchooser/template/templates/',
  method: 'post',
};

// 获取模板下各个节点
const templateNodes = {
  url: '/ipchooser/template/nodes/',
  method: 'post',
};

// 获取模板下各个主机
const templateHosts = {
  url: '/ipchooser/template/hosts/',
  method: 'post',
};

// 获取服务模板/集群模板Agent统计状态
const templateAgentStatistics = {
  url: '/ipchooser/template/agent_statistics/',
  method: 'post',
};

export {
  trees,
  queryHosts,
  queryPath,
  agentStatistics,
  queryHostIdInfos,
  details,
  check,
  globalConfig,
  getConfig,
  updateConfig,
  dynamicGroups,
  executeDynamicGroup,
  groupAgentStatistics,
  templates,
  templateNodes,
  templateHosts,
  templateAgentStatistics,
};
