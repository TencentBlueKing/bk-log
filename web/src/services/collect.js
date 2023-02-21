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

// 获取存储集群
const getStorage = {
  url: '/databus/storage/cluster_groups/',
  method: 'get',
};
// 获取全局配置
const globals = {
  url: '/meta/globals/',
  method: 'get',
};
// 采集项-创建
const addCollection = {
  url: '/databus/collectors/',
  method: 'post',
};
// 采集项-更新
const updateCollection = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'put',
};

// 采集项-更新
const onlyUpdateCollection = {
  url: '/databus/collectors/:collector_config_id/only_update/',
  method: 'post',
};

// 采集项-只创建配置
const onlyCreateCollection = {
  url: '/databus/collectors/only_create/',
  method: 'post',
};
// 创建采集ITSM单据
const applyItsmTicket = {
  url: '/databus/collect_itsm/:collector_config_id/apply_itsm_ticket/',
  method: 'post',
};
// 查询采集ITSM状态
const queryItsmTicket = {
  url: '/databus/collect_itsm/:collector_config_id/',
  method: 'get',
};

// 字段提取&清洗
const fieldCollection = {
  url: '/databus/collectors/:collector_config_id/update_or_create_clean_config/',
  method: 'post',
};
// 字段提取-预览
const getEtlPreview = {
  url: '/databus/collectors/:collector_config_id/etl_preview/',
  method: 'post',
};
// 字段提取-时间校验
const getCheckTime = {
  url: '/databus/collectors/:collector_config_id/etl_time/',
  method: 'post',
};
// 采集项-详情
const details = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'get',
};

// 采集列表-列表
const getCollectList = {
  url: '/databus/collectors/',
  method: 'get',
};
// 采集列表-列表（全量）
const getAllCollectors = {
  url: '/databus/collectors/list_collectors/',
  method: 'get',
};
// 采集插件列表
const getCollectorPlugins = {
  url: '/databus/collector_plugins/',
  method: 'get',
};
// 采集列表-状态
const getCollectStatus = { // 轮询-批量获取采集项订阅状态
  url: '/databus/collectors/batch_subscription_status/',
  method: 'get',
};
// 采集列表-启用
const startCollect = {
  url: '/databus/collectors/:collector_config_id/start/',
  method: 'post',
};
// 采集列表-停用
const stopCollect = {
  url: '/databus/collectors/:collector_config_id/stop/',
  method: 'post',
};
// 采集列表-删除
const deleteCollect = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'delete',
};

// 采集下发-topo树
const getBizTopo = {
  url: '/bizs/:bk_biz_id/topo/',
  method: 'get',
};
// 日志提取无鉴权topo树
const getExtractBizTopo = {
  url: '/log_extract/strategies/topo/',
  method: 'get',
};
// 采集下发-by 静态topo or input
const getHostByIp = {
  url: '/bizs/:bk_biz_id/host_instance_by_ip/',
  method: 'post',
};
// 采集下发-by 动态topo
const getHostByNode = {
  url: '/bizs/:bk_biz_id/host_instance_by_node/',
  method: 'post',
};
// 采集下发-服务模板topo
const getTemplateTopo = {
  url: '/bizs/:bk_biz_id/template_topo/',
  method: 'get',
};
// 采集下发-by 根据服务模板或集群模板获取实例
const getHostByTemplate = {
  url: '/bizs/:bk_biz_id/get_nodes_by_template/',
  method: 'get',
};
// 采集下发-列表&轮询共用同一接口
const getIssuedClusterList = {
  url: '/databus/collectors/:collector_config_id/task_status/',
  method: 'get',
};
// 采集下发-重试(批量)
const retry = {
  url: '/databus/collectors/:collector_config_id/retry/',
  method: 'post',
};
// 段日志调试
const regexDebug = {
  url: '/databus/collectors/:collector_id/regex_debug/',
  method: 'post',
};
// 采集下发-任务执行详情(更多)
const executDetails = {
  url: '/databus/collectors/:collector_id/task_detail/',
};
// 获取节点agent数量
const getNodeAgentStatus = {
  url: '/bizs/:bk_biz_id/list_agent_status/',
  method: 'post',
};
// 获取动态分组列表
const getDynamicGroupList = {
  url: '/bizs/:bk_biz_id/list_dynamic_group/',
  method: 'get',
};
// 获取动态分组表格数据
const getDynamicGroup = {
  url: '/bizs/:bk_biz_id/get_dynamic_group/',
  method: 'post',
};
// 获取预检查创建采集项的参数
const getPreCheck = {
  url: '/databus/collectors/pre_check/?bk_biz_id=:bk_biz_id&collector_config_name_en=:collector_config_name_en',
  method: 'get',
};

const createWeWork = {
  url: '/esb_api/wework/create_chat/',
  method: 'post',
};

// 采集项一键检测 - 开启检测
const runCheck = {
  url: '/databus/check_collector/run_check_collector/',
  method: 'post',
};

// 采集项一键检测 - 获取检测信息
const getCheckInfos = {
  url: '/databus/check_collector/get_check_collector_infos/',
  method: 'post',
};

// oplt_log 查看token请求
const reviewToken = {
  url: '/databus/collectors/:collector_config_id/report_token/',
  method: 'get',
};

export {
  getStorage,
  globals,
  addCollection,
  updateCollection,
  onlyUpdateCollection,
  onlyCreateCollection,
  applyItsmTicket,
  queryItsmTicket,
  fieldCollection,
  getEtlPreview,
  getCheckTime,
  details,
  getCollectList,
  getAllCollectors,
  getCollectorPlugins,
  getCollectStatus,
  startCollect,
  stopCollect,
  deleteCollect,
  getExtractBizTopo,
  getBizTopo,
  getHostByIp,
  getNodeAgentStatus,
  getHostByNode,
  getTemplateTopo,
  getHostByTemplate,
  getIssuedClusterList,
  retry,
  regexDebug,
  executDetails,
  getDynamicGroupList,
  getDynamicGroup,
  getPreCheck,
  createWeWork,
  runCheck,
  getCheckInfos,
  reviewToken,
};
