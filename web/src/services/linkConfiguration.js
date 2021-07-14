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
 * 链路配置相关接口
 */

// 链路列表
const getLinkList = {
  url: '/databus/data_link/',
  method: 'get',
};
// 链路详情
const getLinkDetail = {
  url: '/databus/data_link/:data_link_id/',
  method: 'get',
};
// 创建链路
const createLink = {
  url: '/databus/data_link/',
  method: 'post',
};
// 更新链路
const updateLink = {
  url: '/databus/data_link/:data_link_id/',
  method: 'put',
};
// 删除链路
const deleteLink = {
  url: '/databus/data_link/:data_link_id/',
  method: 'delete',
};

// 集群列表
const getClusterList = {
  url: '/databus/data_link/get_cluster_list/',
  method: 'get',
};

export {
  getLinkList,
  getLinkDetail,
  createLink,
  updateLink,
  deleteLink,
  getClusterList,
};
