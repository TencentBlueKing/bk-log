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
 * 数据源相关接口
 */

const list = {
  url: '/databus/storage/',
  method: 'get',
};
const logList = {
  url: '/databus/storage/log_cluster/',
  method: 'get',
};

const scenario = {
  url: '/meta/scenario/',
  method: 'get',
};

const create = {
  url: '/databus/storage/?bk_biz_id=:bk_biz_id',
  method: 'post',
};

const deleteEs = {
  url: '/databus/storage/:cluster_id/?bk_biz_id=:bk_biz_id',
  method: 'delete',
};

const remove = {
  url: '/source/:source_id/',
  method: 'delete',
};

const update = {
  url: '/databus/storage/:cluster_id/?bk_biz_id=:bk_biz_id',
  method: 'put',
};

const info = {
  url: '/databus/storage/:cluster_id/?bk_biz_id=:bk_biz_id',
  method: 'get',
};

const connectivityDetect = {
  url: '/esb/databus/storage/connectivity_detect/',
  method: 'post',
};

// 连通性测试之后获取集群中各节点属性
const getNodeAttrs = {
  url: '/databus/storage/node_attrs/',
  method: 'post',
};

const connectionStatus = {
  url: '/databus/storage/batch_connectivity_detect/',
  method: 'post',
};
// 数据采集相关接口
const getCollectList = {
  url: '/databus/collectors/',
  method: 'get',
};
/**
 * 轮询-批量获取采集项订阅状态
 */
const getCollectStatus = {
  url: '/databus/collectors/batch_subscription_status/',
  method: 'get',
};

const createCollection = {
  url: '/databus/storage/',
  method: 'post',
};
const deleteCollection = {
  url: '/collectors/:collector_config_id/',
  method: 'delete',
};
const startCollection = {
  url: '/collectors/:collector_config_id/start/',
  method: 'post',
};
const stopCollection = {
  url: '/collectors/:collector_config_id/stop/',
  method: 'post',
};
// 采集下发 列表&轮询共用同一接口
const getIssuedClusterList = {
  url: '/databus/collectors/:collector_config_id/task_status/',
  method: 'get',
};

/**
 * 采集配置相关接口
 */

const detailsList = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'get',
};

// 物理索引
const getIndexes = {
  url: '/databus/collectors/:collector_config_id/indices_info/',
  method: 'get',
};

const collectList = {
  url: '/databus/collectors/:collector_config_id/subscription_status/',
  method: 'get',
};

const retryList = {
  url: '/databus/collectors/:collector_config_id/retry/',
  method: 'post',
};

const dataList = {
  url: '/esb/databus/collectors/:collector_config_id/tail/',
  method: 'get',
};

// 采集下发 - 重试
const issuedRetry = {
  url: '/databus/collectors/:collector_config_id/subscription_run/',
  method: 'post',
};

export {
  list,
  logList,
  remove,
  create,
  deleteEs,
  update,
  info,
  connectivityDetect,
  getNodeAttrs,
  connectionStatus,
  getCollectList,
  getCollectStatus,
  createCollection,
  deleteCollection,
  // updataCollection,
  startCollection,
  stopCollection,
  // detailCollection,
  getIssuedClusterList,
  detailsList,
  getIndexes,
  collectList,
  retryList,
  dataList,
  issuedRetry,
  scenario,
};
