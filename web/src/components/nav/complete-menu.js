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

// 支持的完整的菜单
export default [{
  name: '检索',
  id: 'retrieve',
}, {
  name: '仪表盘',
  id: 'dashboard',
  children: [{
    id: 'create-dashboard',
    name: '新建仪表盘',
  }, {
    id: 'create-folder',
    name: '新建目录',
  }, {
    id: 'import-dashboard',
    name: '导入仪表盘',
  }],
}, {
  name: '日志提取',
  id: 'extract',
}, {
  name: '调用链',
  id: 'trace',
}, {
  name: '监控策略',
  id: 'monitor',
}, {
  name: '管理',
  id: 'manage',
  children: [{
    id: 'manage-access',
    name: '日志接入',
    children: [{
      id: 'log-collection',
      name: '日志采集',
    }, {
      id: 'bk-data-collection',
      name: '数据平台',
    }, {
      id: 'es-collection',
      name: '第三方ES接入',
    }, {
      id: 'custom-collection',
      name: '自定义接入',
    }],
  }, {
    id: 'trace-track',
    name: '全链路追踪',
    children: [{
      id: 'collection-track',
      name: '采集接入',
    }, {
      id: 'bk-data-track',
      name: '数据平台接入',
    }, {
      id: 'sdk-track',
      name: 'SDK接入',
    }],
  }, {
    id: 'manage-extract',
    name: '日志提取',
    children: [{
      id: 'manage-log-extract',
      name: '提取配置',
    }, {
      id: 'extract-link-manage',
      name: '链路管理',
    }],
  }, {
    id: 'log-archive',
    name: '日志归档',
    children: [{
      id: 'log-archive-conf',
      name: '日志归档',
    }],
  }, {
    id: 'es-cluster-status',
    name: 'ES集群',
    children: [{
      id: 'es-cluster-manage',
      name: '集群列表',
    }],
  }, {
    id: 'manage-data-link',
    name: '管理',
    children: [{
      id: 'manage-data-link-conf',
      name: '采集链路管理',
    }],
  }],
}];
