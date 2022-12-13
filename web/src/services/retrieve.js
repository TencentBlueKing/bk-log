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

const getIndexSetList = {
  url: '/search/index_set/',
  method: 'get',
};

const getLogTableHead = {
  url: '/search/index_set/:index_set_id/fields/',
  method: 'get',
};
const getLogTableList = {
  url: '/search/index_set/:index_set_id/search/',
  method: 'post',
};
const getLogChartList = {
  url: '/search/index_set/:index_set_id/aggs/date_histogram/',
  method: 'post',
};

const getFilterBiz = {
  url: '/bizs/',
  method: 'get',
};
// IP快选 选择业务接口调整
const getIpBusinessList = {
  url: '/search/index_set/:index_set_id/bizs/',
  method: 'get',
};
const getIpTree = {
  url: '/bizs/:bk_biz_id/topo/',
  method: 'get',
};
const getOperators = {
  url: '/search/index_set/operators/',
  method: 'get',
};
const getCloudAreaList = {
  url: '/search/index_set/$index_set_id/:tailf/',
  method: 'post',
};
const downloadLog = {
  url: '/search/index_set/:index_set_id/export/',
  method: 'post',
};
const exportAsync = {
  url: '/search/index_set/:index_set_id/async_export/',
  method: 'post',
};
const getRealTimeLog = {
  url: '/search/index_set/:index_set_id/tail_f/',
  method: 'post',
};
const getContentLog = {
  url: '/search/index_set/:index_set_id/context/',
  method: 'post',
};
const saveTitleInfo = {
  url: '/search/index_set/:index_set_id/config/',
  method: 'post',
};
const getHistoryList = {
  url: '/search/index_set/:index_set_id/history/',
  method: 'get',
};
const getRetrieveFavorite = {
  url: '/search/favorite/',
  method: 'get',
};
const postRetrieveFavorite = {
  url: '/search/favorite/',
  method: 'post',
};
const deleteRetrieveFavorite = {
  url: '/search/favorite/:id/',
  method: 'delete',
};
const postFieldsConfig = {
  url: '/search/index_set/:index_set_id/config/',
  method: 'post',
};
const getWebConsoleUrl = {
  url: '/search/index_set/:index_set_id/bcs_web_console/',
  method: 'get',
};
const getSearchHistory = {
  url: '/search/index_set/:index_set_id/history/',
  method: 'get',
};
const getExportHistoryList = {
  url: '/search/index_set/:index_set_id/export_history/?bk_biz_id=:bk_biz_id&page=:page&pagesize=:pagesize&show_all=:show_all',
  method: 'get',
};
const getFieldsListConfig = {
  url: '/search/index_set/:index_set_id/list_config/',
  method: 'get',
};
const createFieldsConfig = {
  url: '/search/index_set/:index_set_id/create_config/',
  method: 'post',
};
const updateFieldsConfig = {
  url: '/search/index_set/:index_set_id/update_config/',
  method: 'post',
};
const deleteFieldsConfig = {
  url: '/search/index_set/:index_set_id/delete_config/',
  method: 'post',
};

export {
  getIndexSetList,
  getLogTableHead,
  getLogTableList,
  getLogChartList,
  getFilterBiz,
  getIpTree,
  getOperators,
  getCloudAreaList,
  downloadLog,
  exportAsync,
  getRealTimeLog,
  getContentLog,
  saveTitleInfo,
  getIpBusinessList,
  getHistoryList,
  getRetrieveFavorite,
  postRetrieveFavorite,
  deleteRetrieveFavorite,
  postFieldsConfig,
  getWebConsoleUrl,
  getSearchHistory,
  getExportHistoryList,
  getFieldsListConfig,
  createFieldsConfig,
  updateFieldsConfig,
  deleteFieldsConfig,
};
