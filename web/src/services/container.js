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
 * 容器日志接口
 */

// 新建容器日志
const create = {
  url: '/databus/collectors/',
  method: 'post',
};

// 更新容器日志
const update = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'put',
};

// 获取容器日志详情
const getDetail = {
  url: '/databus/collectors/:collector_config_id/',
  method: 'get',
};

// 获取namespace列表
const getNameSpace = {
  url: '/databus/collectors/list_namespace/',
  method: 'get',
};

// 获取 集群-node树或集群-namespace-pod列表
const getPodTree = {
  url: '/databus/collectors/list_topo/',
  method: 'get',
};

// 获取node 标签列表
const getNodeLabelList = {
  url: '/databus/collectors/get_labels/',
  method: 'get',
};

// 获取标签命中的结果
const getHitResult = {
  url: '/databus/collectors/match_labels/',
  method: 'post',
};

// 获取workload类型
const getWorkLoadType = {
  url: '/databus/collectors/list_workload_type/',
  method: 'get',
};

// 获取workload name
const getWorkLoadName = {
  url: '/databus/collectors/get_workload/',
  method: 'get',
};

// 获取bcs集群列表
const getBcsList = {
  url: '/databus/collectors/list_bcs_clusters/',
  method: 'get',
};

// yaml判断
const yamlJudgement = {
  url: '/databus/collectors/validate_container_config_yaml/',
  method: 'post',
};

// ui配置转yaml base64
const containerConfigsToYaml = {
  url: 'databus/collectors/container_configs_to_yaml/',
  method: 'post',
};

// 预览
const getLabelHitView = {
  url: '/databus/collectors/preview_containers/',
  method: 'post',
};

export {
  create,
  update,
  getDetail,
  getNameSpace,
  getPodTree,
  getNodeLabelList,
  getHitResult,
  getWorkLoadType,
  getWorkLoadName,
  getBcsList,
  yamlJudgement,
  containerConfigsToYaml,
  getLabelHitView,
};
