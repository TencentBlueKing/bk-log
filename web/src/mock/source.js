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

const list = {};

// 删除数据源
const remove = {};

// 新增数据源
const create = {};

const connectivityDetect = {};

const update = {};

const info = {};

const getCollectList = {};

const getCollectStatus = {};

// 业务topo
const getBizTopo = {};

const createCollection = {};

const deleteCollection = {};
const updataCollection = {};

const startCollection = {};

const stopCollection = {};

const detailCollection = {};

const getIssuedClusterList = {};

const issuedRetry = {};

export default {
  list,
  remove,
  create,
  update,
  info,
  connectivityDetect,
  getCollectList,
  getCollectStatus,
  getBizTopo,
  createCollection,
  deleteCollection,
  updataCollection,
  startCollection,
  stopCollection,
  detailCollection,
  getIssuedClusterList,
  issuedRetry,
};
