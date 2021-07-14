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

const getTaskList = {
  total: 100,
  list: [{
    bk_biz_id: '001',
    ip_list: [],
    file_path: ['/data/home/xxx.log'],
    download_status: 'PACKING',
    download_status_display: '打包中',
    create_time: '2020-06-04 11:19:30',
    creator: 'arman',
  }, {
    bk_biz_id: '002',
    ip_list: [],
    file_path: ['/data/home/xxx.log'],
    download_status: 'PACKING',
    download_status_display: '打包中',
    create_time: '2020-06-04 11:19:30',
    creator: 'arman',
  }, {
    bk_biz_id: '003',
    ip_list: [],
    file_path: ['/data/home/xxx.log', '/data/home/yyy.log'],
    download_status: 'DOWNLOADABLE',
    download_status_display: '可下载',
    create_time: '2020-06-04 11:19:30',
    creator: 'arman',
  }, {
    bk_biz_id: '004',
    ip_list: [],
    file_path: ['/data/home/xxx.log', '/data/home/yyy.log'],
    download_status: 'REDOWNLOADABLE',
    download_status_display: '可重新下载',
    create_time: '2020-06-04 11:19:30',
    creator: 'arman',
  }, {
    bk_biz_id: '004',
    ip_list: [],
    file_path: ['/data/home/xxx.log', '/data/home/yyy.log', '/data/home/yyy.log'],
    download_status: 'EXPIRED',
    download_status_display: '已过期',
    create_time: '2020-06-04 11:19:30',
    creator: 'arman',
  }],
};

const getTopoIpList = [{
  id: 0,
  default: 0,
  name: '蓝鲸',
  bk_inst_id: 2,
  bk_inst_name: '蓝鲸',
  bk_obj_id: 'biz',
  bk_obj_name: '业务',
  child: [{
    ip: '',
    bk_cloud_id: 0,
    id: 1,
    default: 0,
    name: 'PaaS平台',
    bk_inst_id: 9,
    bk_inst_name: 'PaaS平台',
    bk_obj_id: 'set',
    bk_obj_name: '集群',
  }, {
    ip: '',
    bk_cloud_id: 0,
    id: 2,
    default: 0,
    name: 'PaaS平台',
    bk_inst_id: 9,
    bk_inst_name: 'PaaS平台',
    bk_obj_id: 'set',
    bk_obj_name: '集群',
  }, {
    id: 3,
    default: 0,
    name: 'PaaS平台',
    bk_inst_id: 9,
    bk_inst_name: 'PaaS平台',
    bk_obj_id: 'set',
    bk_obj_name: '集群',
  }, {
    ip: '',
    bk_cloud_id: 0,
    id: 4,
    default: 0,
    name: 'PaaS平台',
    bk_inst_id: 9,
    bk_inst_name: 'PaaS平台',
    bk_obj_id: 'set',
    bk_obj_name: '集群',
  }],
}];

// 文件浏览策略，可选择的目录文件路径
const getAvailableExplorerPath = [{
  visible_dir: '/data/user01/log1',
  file_type: '.log',
}, {
  visible_dir: '/data/user01/log2',
  file_type: '.txt',
}];

// 预览用户在业务机器中的可下载的文件
const getExplorerList = [{
  ip: '',
  path: 'xx/xx/xx1',
  mtime: '2020-02-20 20:02:02',
  size: '0',
}, {
  ip: '',
  path: 'xx/xx/dir',
  mtime: '2020-02-20 02:04:22',
  size: '0',
}, {
  ip: '',
  path: 'xx/xx/xx2/',
  mtime: '2020-02-20 02:04:22',
  size: '1KB',
}];

// 点击开始下载后创建下载任务
const createDownloadTask = {
  task_id: 1,
};

export default {
  getTaskList,
  getTopoIpList,
  getAvailableExplorerPath,
  getExplorerList,
  createDownloadTask,
};
