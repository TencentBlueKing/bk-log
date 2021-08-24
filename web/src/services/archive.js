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

// 获取集群快照仓库列表
const getRepositoryList = {
  url: '/databus/storage/list_repository/',
  method: 'get',
};

// 新增归档仓库
const createRepository = {
  url: '/meta/esb/create_es_snapshot_repository/',
  method: 'post',
};

// 删除归档仓库
const deleteRepository = {
  url: '/meta/esb/delete_es_snapshot_repository/',
  method: 'post',
};

// 归档列表
const getArchiveList = {
  url: '/databus/archive/',
  method: 'get',
};

// 新建归档
const createArchive = {
  url: '/databus/archive/',
  method: 'post',
};

// 编辑归档
const editArchive = {
  url: '/databus/archive/:archive_config_id',
  method: 'put',
};

// 删除归档
const deleteArchive = {
  url: '/databus/archive/:archive_config_id/',
  method: 'delete',
};

// 归档配置详情
const archiveConfig = {
  url: '/databus/archive/:archive_config_id/',
  method: 'get',
};

// 回溯列表
const restoreList = {
  url: '/databus/restore/',
  method: 'get',
};

// 全量获取归档列表
const getAllArchives = {
  url: '/databus/archive/list_archive/',
  method: 'get',
};

// 新建回溯
const createRestore = {
  url: '/databus/restore/',
  method: 'post',
};

// 编辑回溯
const editRestore = {
  url: '/databus/restore/:restore_config_id/',
  method: 'put',
};

// 删除回溯
const deleteRestore = {
  url: '/databus/restore/:restore_config_id/',
  method: 'delete',
};

// 异步获取回溯状态
const getRestoreStatus = {
  url: '/databus/restore/batch_get_state/',
  method: 'post',
};

export {
  getRepositoryList,
  createRepository,
  deleteRepository,
  getArchiveList,
  createArchive,
  deleteArchive,
  archiveConfig,
  restoreList,
  getAllArchives,
  editArchive,
  createRestore,
  deleteRestore,
  getRestoreStatus,
  editRestore,
};
