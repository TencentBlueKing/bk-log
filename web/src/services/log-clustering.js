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
 * 通知列表
 */
const getConfig = {
  url: '/clustering_config/:index_set_id/config/',
  method: 'get',
};

const getDefaultConfig = {
  url: '/clustering_config/default_config/',
  method: 'get',
};

const changeConfig = {
  url: '/clustering_config/:index_set_id/create_or_update/',
  method: 'post',
};

const preview = {
  url: '/clustering_config/preview/',
  method: 'post',
};

const clusterSearch = {
  url: '/pattern/:index_set_id/search/',
  method: 'post',
};

const closeClean = {
  url: '/databus/collectors/:collector_config_id/close_clean/',
  method: 'post',
};

const updateStrategies = {
  url: '/clustering_monitor/:index_set_id/update_strategies/',
  method: 'post',
};

const getFingerLabels = {
  url: '/pattern/:index_set_id/labels/',
  method: 'post',
};

const getNewClsStrategy = {
  url: '/clustering_monitor/:index_set_id/get_new_cls_strategy/',
  method: 'get',
};

const updateNewClsStrategy = {
  url: '/clustering_monitor/:index_set_id/update_new_cls_strategy/',
  method: 'post',
};

const checkRegexp = {
  url: '/clustering_config/check_regexp/',
  method: 'post',
};
// 标签编辑
const editLabel = {
  url: '/pattern/:index_set_id/label/ ',
  method: 'post',
};

export {
  getConfig,
  getDefaultConfig,
  changeConfig,
  preview,
  clusterSearch,
  closeClean,
  updateStrategies,
  getFingerLabels,
  getNewClsStrategy,
  updateNewClsStrategy,
  checkRegexp,
  editLabel,
};
