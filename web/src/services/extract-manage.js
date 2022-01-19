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

const getStrategyList = {
  url: '/log_extract/strategies/',
  method: 'get',
};

const createStrategy = {
  url: '/log_extract/strategies/',
  method: 'post',
};

const updateStrategy = {
  url: '/log_extract/strategies/:strategy_id/',
  method: 'put',
};

const deleteStrategy = {
  url: '/log_extract/strategies/:strategy_id/',
  method: 'delete',
};

// 日志提取链路列表
const getLogExtractLinks = {
  url: '/log_extract/links/',
  method: 'get',
};

// 日志提取链路详情
const getLogExtractLinkDetail = {
  url: '/log_extract/links/:link_id/',
  method: 'get',
};

// 新增日志提取链路
const createLogExtractLink = {
  url: '/log_extract/links/',
  method: 'post',
};

// 更新日志提取链路
const updateLogExtractLink = {
  url: '/log_extract/links/:link_id/',
  method: 'put',
};

// 删除日志提取链路
const deleteLogExtractLink = {
  url: '/log_extract/links/:link_id/',
  method: 'delete',
};

export {
  getStrategyList,
  createStrategy,
  updateStrategy,
  deleteStrategy,
  getLogExtractLinks,
  getLogExtractLinkDetail,
  createLogExtractLink,
  updateLogExtractLink,
  deleteLogExtractLink,
};
