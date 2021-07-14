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
 * @file router 配置
 * @author  <>
 */

import Vue from 'vue';
import VueRouter from 'vue-router';

import http from '@/api';
import page404 from '@/views/404';

Vue.use(VueRouter);

const page403 = () => import(/* webpackChunkName: 'page403' */'@/views/403');
const retrieve = () => import(/* webpackChunkName: 'logRetrieve' */'@/views/retrieve2');
const dashboard = () => import(/* webpackChunkName: 'dashboard' */'@/views/dashboard');
const extract = () => import(/* webpackChunkName: 'logExtract' */'@/views/extract');
const trace = () => import(/* webpackChunkName: 'logTrace' */'@/views/trace');

const manage = () => import(/* webpackChunkName: 'logManage' */'@/views/manage');
const indexSet = () => import(/* webpackChunkName: 'logIndexSet' */'@/views/manage/indexSet');
const addIndexSet = () => import(/* webpackChunkName: 'logAddIndexSet' */'@/views/manage/indexSet/addIndexSet');
const collectAccess = () => import(/* webpackChunkName: 'logCollectAccess' */'@/views/manage/collectAccess');
const esAccess = () => import(/* webpackChunkName: 'logEsAccess' */'@/views/manage/esAccess');
const dataAccess = () => import(/* webpackChunkName: 'logAccessStep' */'@/components/data-Access');
// const addDataSource = () =>
// import(/* webpackChunkName: 'logAddDataSource' */'@/views/manage/dataSource/addDataSource')
const allocation = () => import(/* webpackChunkName: 'logPermissionGroup' */'@/views/manage/esSource/allocation');
const jsonFormat = () => import(/* webpackChunkName: 'logPermissionGroup' */'@/views/manage/esSource/jsonFormat');
// const handleCollection = () => import('@/views/manage/collection/handleCollection')
// const addCollection = () => import(/* webpackChunkName: 'addCollection' */'@/views/manage/collection/addCollection')
const migrate = () => import(/* webpackChunkName: 'migrate' */'@/views/manage/migrate');
const manageExtract = () => import(/* webpackChunkName: 'manageExtract' */'@/views/manage/extract');
const linkConfiguration = () => import(/* webpackChunkName: 'linkConfiguration' */'@/views/manage/link');

const routes = [
  {
    path: '/',
    redirect: 'retrieve',
  },
  {
    path: '/retrieve/:indexId?',
    name: 'retrieve',
    component: retrieve,
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: dashboard,
  },
  {
    path: '/extract',
    name: 'extract',
    component: extract,
  },
  {
    path: '/trace/:indexId?',
    name: 'trace',
    component: trace,
  },
  {
    path: '/manage',
    component: manage,
    children: [
      {
        path: '',
        name: 'manage',
        // alias: '/dataSource',
        redirect: 'collect',
      },
      // 采集接入
      {
        path: 'collect',
        name: 'collectAccess',
        component: collectAccess,
      },
      {
        path: 'collect/add',
        name: 'collectAdd',
        component: dataAccess,
      },
      {
        path: 'collect/edit/:collectorId',
        name: 'collectEdit',
        component: dataAccess,
      },
      {
        path: 'collect/field/:collectorId',
        name: 'collectField',
        component: dataAccess,
      },
      {
        path: 'collect/start/:collectorId',
        name: 'collectStart',
        component: dataAccess,
      },
      {
        path: 'collect/stop/:collectorId',
        name: 'collectStop',
        component: dataAccess,
      },
      {
        path: 'collect/allocation/:collectorId',
        name: 'allocation',
        component: allocation,
      },
      {
        path: 'collect/jsonFormat/:collectorId',
        name: 'jsonFormat',
        component: jsonFormat,
      },
      // es采集
      {
        path: 'esAccess',
        name: 'esAccess',
        component: esAccess,
      },
      // 索引集
      {
        path: 'indexSet',
        name: 'indexSet',
        component: indexSet,
      },
      {
        path: 'indexSet/addIndexSet',
        name: 'addIndexSet',
        component: addIndexSet,
      },
      {
        path: 'indexSet/editIndexSet/:id',
        name: 'editIndexSet',
        component: addIndexSet,
      },
      {
        path: 'link',
        name: 'linkConfiguration',
        component: linkConfiguration,
      },
      // {
      //     path: 'dataSource/addDataSource',
      //     name: 'addDataSource',
      //     component: addDataSource
      // },
      // v3迁移
      {
        path: 'migrate',
        name: 'migrate',
        component: migrate,
      },
      {
        path: 'extract',
        name: 'manageExtract',
        component: manageExtract,
      },
    ],
  },
  {
    path: '/notTraceIndex',
    name: 'notTraceIndex',
    component: page403,
  },
  {
    path: '*',
    name: 'page404',
    component: page404,
  },
];

const router = new VueRouter({
  routes,
});

const cancelRequest = async () => {
  const allRequest = http.queue.get();
  const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange);
  await http.cancel(requestQueue.map(request => request.requestId));
};

router.beforeEach(async (to, from, next) => {
  await cancelRequest();
  next();
});

export default router;
