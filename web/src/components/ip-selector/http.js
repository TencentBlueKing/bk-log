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

import http from '@/api';
import store from '@/store';

function getResData(httpPromise) {
  return new Promise((resolve, reject) => {
    httpPromise.then((res) => {
      resolve(res.data);
    }).catch((err) => {
      reject(err);
    });
  });
}

// 获取 TOPO 树
export function getTopoTree() {
  const originPromise = http.request('collect/getBizTopo', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    query: {
      instance_type: 'host',
      remove_empty_nodes: false,
    },
  });
  return getResData(originPromise);
}

// 静态拓扑根据 IP 获取实例
export function getHostInstanceByIp(params) {
  const originPromise = http.request('collect/getHostByIp', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    data: {
      ip_list: params.ip_list,
    },
  });
  return getResData(originPromise);
}

// 动态拓扑根据节点获取（HOST）实例
export function getHostInstanceByNode(params) {
  const originPromise = http.request('collect/getHostByNode', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    data: {
      node_list: params.node_list,
    },
  });
  return getResData(originPromise);
}

// 动态拓扑根据节点获取（SERVICE）实例，暂不需要
export function getServiceInstanceByNode() {
  console.log('getServiceInstanceByNode');
}

// 获取服务模板或集群模板
export function getTemplate(params) {
  const originPromise = http.request('collect/getTemplateTopo', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    query: {
      template_type: params.bk_obj_id, // SERVICE_TEMPLATE SET_TEMPLATE
    },
  });
  return getResData(originPromise);
}

// 根据选择的模板获取节点
export function getNodesByTemplate(params) {
  const originPromise = http.request('collect/getHostByTemplate', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    query: {
      bk_inst_ids: params.bk_inst_ids.join(','), // [1,2,3]
      template_type: params.bk_obj_id, // SERVICE_TEMPLATE SET_TEMPLATE
    },
  });
  return getResData(originPromise);
}

// 获取节点对应agent数量及异常状态agent数量
export function getNodeAgentStatus(data) {
  const originPromise = http.request('collect/getNodeAgentStatus', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    data: {
      node_list: data,
    },
  });
  return getResData(originPromise);
}

// 获取动态分组列表
export function getDynamicGroupList() {
  const originPromise = http.request('collect/getDynamicGroupList', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
  });
  return getResData(originPromise);
}

// 获取动态分组表格数据
export function getDynamicGroup(data) {
  const originPromise = http.request('collect/getDynamicGroup', {
    params: {
      bk_biz_id: store.getters.bkBizId,
    },
    data: {
      dynamic_group_id_list: data,
    },
  });
  return getResData(originPromise);
}
