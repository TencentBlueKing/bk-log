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


const LogCollectionView = {
  name: 'LogCollection',
  template: '<router-view></router-view>',
};
const IndexSetView = {
  name: 'IndexSet',
  template: '<router-view :key="Date.now()"></router-view>',
};
const CustomReportView = {
  name: 'CustomReportView',
  template: '<router-view></router-view>',
};
const ExtractLinkView = {
  name: 'ExtractLinkView',
  template: '<router-view></router-view>',
};
const LogCleanView = {
  name: 'LogCleanView',
  template: '<router-view></router-view>',
};
const LogCleanTempView = {
  name: 'LogCleanTempView',
  template: '<router-view></router-view>',
};
const DashboardTempView = {
  name: 'DashboardTempView',
  template: '<router-view></router-view>',
};
const TraceTempView = {
  name: 'TraceTempView',
  template: '<router-view></router-view>',
};

const page403 = () => import(/* webpackChunkName: 'page403' */'@/views/403');
const retrieve = () => import(/* webpackChunkName: 'logRetrieve' */'@/views/retrieve');
const dashboard = () => import(/* webpackChunkName: 'dashboard' */'@/views/dashboard');
const trace = () => import(/* webpackChunkName: 'logTrace' */'@/views/trace');
const traceDetaid = () => import(/* webpackChunkName: 'logTraceDetail' */'@/views/trace/trace-explore');

// 管理端
const Manage = () => import(/* webpackChunkName: 'manage' */'@/views/manage');
// ---- 日志接入 ---- 日志采集（采集项）
const CollectionItem = () => import(
  /* webpackChunkName: 'collection-item' */
  '@/views/manage/manage-access/log-collection/collection-item');
// ---- 日志接入 ---- 日志采集（采集项）---- 管理(查看)采集项
const ManageCollection = () => import(
  /* webpackChunkName: 'manage-collection' */
  '@/views/manage/manage-access/log-collection/collection-item/manage-collection'
);
// ---- 日志接入 ---- 日志采集（采集项）---- 新建、编辑、停用、启用、字段提取
const AccessSteps = () => import(
  /* webpackChunkName: 'access-steps' */
  // '@/views/manage/manage-access/log-collection/collection-item/access-steps'
  '@/components/collection-access'
);
// ---- 日志接入 ---- 日志采集索引集、数据平台、第三方ES接入 ---- 索引集列表
const IndexList = () => import(
  /* webpackChunkName: 'index-set' */
  '@/views/manage/manage-access/components/index-set/list'
);
// ---- 日志接入 ---- 日志采集索引集、数据平台、第三方ES接入---- 管理索引集
const ManageIndex = () => import(
  /* webpackChunkName: 'mange-index' */
  '@/views/manage/manage-access/components/index-set/manage'
);
// ---- 日志接入 ---- 日志采集索引集、数据平台、第三方ES接入 ---- 新建索引集
const CreateIndex = () => import(
  /* webpackChunkName: 'create-index' */
  '@/views/manage/manage-access/components/index-set/create'
);
// ---- 日志接入 ---- 自定义上报 ---- 自定义上报列表
const CustomReportList = () => import(
  /* webpackChunkName: 'create-index' */
  '@/views/manage/manage-access/custom-report/list'
);
// ---- 日志接入 ---- 自定义上报 ---- 自定义上报新建/编辑
const CustomReportCreate = () => import(
  /* webpackChunkName: 'create-index' */
  '@/views/manage/manage-access/custom-report/create'
);
// ---- 日志接入 ---- 自定义上报 ---- 自定义上报详情
const CustomReportDetail = () => import(
  /* webpackChunkName: 'create-index' */
  '@/views/manage/manage-access/custom-report/detail'
);
// ---- 全链路跟踪 ---- 采集跟踪
const CollectionTrack = () => import(
  /* webpackChunkName: 'collection-track' */
  '@/views/manage/trace-track/collection-track'
);
// ---- 全链路跟踪 ---- SDK跟踪
const SdkTrack = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/trace-track/sdk-track'
);
// ---- 日志清洗 ---- 清洗列表
const cleanList = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-clean/clean-manage/list'
);
// ---- 日志清洗 ---- 新增/编辑 清洗
const cleanCreate = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-clean/clean-manage/create'
);
// ---- 日志清洗 ---- 新增/编辑 清洗
const cleanTempCreate = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-clean/clean-template/create'
);
// ---- 模板清洗 ---- 清洗模版
const cleanTemplate = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-clean/clean-template/list'
);
// ---- 日志归档 ---- 归档仓库
const ArchiveRepository = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-archive/archive-repository/list'
);
// ---- 日志归档 ---- 归档列表
const ArchiveList = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-archive/archive-list/list'
);
// ---- 日志归档 ---- 归档回溯
const ArchiveRestore = () => import(
  /* webpackChunkName: 'sdk-track' */
  '@/views/manage/log-archive/archive-restore/list'
);
// ---- 日志提取 ---- 提取配置
const ExtractPermission = () => import(
  /* webpackChunkName: 'manage-extract-permission' */
  '@/views/manage/manage-extract/manage-extract-permission'
);
// ---- 日志提取 ---- 提取任务
const extract = () => import(
  /* webpackChunkName: 'logExtract' */
  '@/views/extract/index'
);
// ---- 日志提取 ---- 提取任务列表
const extractHome = () => import(
  /* webpackChunkName: 'extract-home' */
  '@/views/extract/home'
);
// ---- 日志提取 ---- 新建/克隆提取任务
const extractCreate = () => import(
  /* webpackChunkName: 'extract-create' */
  '@/views/extract/create'
);
// ---- 日志提取 ---- 链路管理列表
const ExtractLinkList = () => import(
  /* webpackChunkName: 'extract-link-manage' */
  '@/views/manage/manage-extract/extract-link-manage/extract-link-list'
);
// ---- 日志提取 ---- 链路管理创建/编辑
const ExtractLinkCreate = () => import(
  /* webpackChunkName: 'extract-link-manage' */
  '@/views/manage/manage-extract/extract-link-manage/extract-link-create'
);
// ---- ES集群 ---- 集群信息
const ClusterMess = () => import(
  /* webpackChunkName: 'es-cluster-mess' */
  '@/views/manage/es-cluster-status/es-cluster-mess'
);
// ---- 管理 ---- 采集链路管理
const DataLinkConf = () => import(
  /* webpackChunkName: 'manage-data-link-conf' */
  '@/views/manage/manage-data-link/manage-data-link-conf'
);

const routes = [
  {
    path: '',
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
    component: DashboardTempView,
    redirect: '/dashboard/default-dashboard',
    children: [
      {
        path: 'default-dashboard',
        name: 'default-dashboard',
        component: dashboard,
      },
      {
        path: 'create-dashboard',
        name: 'create-dashboard',
        meta: {
          needBack: true,
          backName: 'default-dashboard',
        },
        component: dashboard,
      },
      {
        path: 'import-dashboard',
        name: 'import-dashboard',
        meta: {
          needBack: true,
          backName: 'default-dashboard',
        },
        component: dashboard,
      },
      {
        path: 'create-folder',
        name: 'create-folder',
        meta: {
          needBack: true,
          backName: 'default-dashboard',
        },
        component: dashboard,
      },
    ],
  },
  {
    path: '/trace',
    name: 'trace',
    component: TraceTempView,
    redirect: '/trace/trace-list',
    children: [
      {
        path: 'trace-list',
        name: 'trace-list', // 调用链列表
        component: trace,
      },
      {
        path: 'trace-detail',
        name: 'trace-detail', // 调用链详情
        component: traceDetaid,
      },
      {
        path: '/notTraceIndex',
        name: 'notTraceIndex',
        component: page403,
        meta: {
          needBack: true,
          backName: 'trace',
        },
      },
    ],
  },
  {
    path: '/manage',
    name: 'manage',
    component: Manage,
    redirect: '/manage/log-collection/collection-item',
    children: [
      {
        path: 'collect', // 日志采集 支持监控跳转兼容旧版本管理端
        redirect: '/manage/log-collection/collection-item',
      },
      {
        path: 'log-collection',
        name: 'log-collection', // 日志接入 - 日志采集
        component: LogCollectionView,
        redirect: '/manage/log-collection/collection-item',
        children: [
          {
            path: 'collection-item',
            name: 'collection-item', // 采集项列表
            component: CollectionItem,
          },
          {
            path: 'collection-item/manage/:collectorId',
            name: 'manage-collection', // 管理(查看)采集项
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: ManageCollection,
          },
          {
            // =================== 采集项新建、编辑等操作，尽量复用旧代码
            path: 'collection-item/add',
            name: 'collectAdd',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            path: 'collection-item/edit/:collectorId',
            name: 'collectEdit',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            path: 'collection-item/field/:collectorId',
            name: 'collectField',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            path: 'collection-item/storage/:collectorId',
            name: 'collectStorage',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            path: 'collection-item/start/:collectorId',
            name: 'collectStart',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            path: 'collection-item/stop/:collectorId',
            name: 'collectStop',
            meta: {
              needBack: true,
              backName: 'collection-item',
            },
            component: AccessSteps,
          },
          {
            // ===================
            path: 'log-index-set', // 索引集
            name: 'log-index-set',
            component: IndexSetView,
            redirect: '/manage/log-collection/log-index-set/list',
            children: [
              {
                path: 'list',
                name: 'log-index-set-list',
                component: IndexList,
              },
              {
                path: 'manage/:indexSetId',
                name: 'log-index-set-manage',
                meta: {
                  needBack: true,
                  backName: 'log-index-set-list',
                },
                component: ManageIndex,
              },
              {
                path: 'create',
                name: 'log-index-set-create',
                meta: {
                  needBack: true,
                  backName: 'log-index-set-list',
                },
                component: CreateIndex,
              },
              {
                path: 'edit/:indexSetId',
                name: 'log-index-set-edit',
                meta: {
                  needBack: true,
                  backName: 'log-index-set-list',
                },
                component: CreateIndex,
              },
            ],
          },
        ],
      },
      {
        path: 'bk-data-collection', // 日志接入 - 数据平台
        name: 'bk-data-collection',
        component: IndexSetView,
        redirect: '/manage/bk-data-collection/list',
        children: [
          {
            path: 'list',
            name: 'bkdata-index-set-list',
            component: IndexList,
          },
          {
            path: 'manage/:indexSetId',
            name: 'bkdata-index-set-manage',
            meta: {
              needBack: true,
              backName: 'bkdata-index-set-list',
            },
            component: ManageIndex,
          },
          {
            path: 'create',
            name: 'bkdata-index-set-create',
            meta: {
              needBack: true,
              backName: 'bkdata-index-set-list',
            },
            component: CreateIndex,
          },
          {
            path: 'edit/:indexSetId',
            name: 'bkdata-index-set-edit',
            meta: {
              needBack: true,
              backName: 'bkdata-index-set-list',
            },
            component: CreateIndex,
          },
        ],
      },
      {
        path: 'es-collection', // 日志接入 - 第三方ES接入
        name: 'es-collection',
        component: IndexSetView,
        redirect: '/manage/es-collection/list',
        children: [
          {
            path: 'list',
            name: 'es-index-set-list',
            component: IndexList,
          },
          {
            path: 'manage/:indexSetId',
            name: 'es-index-set-manage',
            meta: {
              needBack: true,
              backName: 'es-index-set-list',
            },
            component: ManageIndex,
          },
          {
            path: 'create',
            name: 'es-index-set-create',
            meta: {
              needBack: true,
              backName: 'es-index-set-list',
            },
            component: CreateIndex,
          },
          {
            path: 'edit/:indexSetId',
            name: 'es-index-set-edit',
            meta: {
              needBack: true,
              backName: 'es-index-set-list',
            },
            component: CreateIndex,
          },
        ],
      },
      {
        path: 'custom-report',
        name: 'custom-report', // 日志接入 - 自定义上报
        component: CustomReportView,
        redirect: '/manage/custom-report/list',
        children: [
          {
            path: 'list',
            name: 'custom-report-list', // 日志接入 - 自定义上报列表
            component: CustomReportList,
          },
          {
            path: 'create',
            name: 'custom-report-create', // 日志接入 - 自定义上报新建
            meta: {
              needBack: true,
              backName: 'custom-report-list',
            },
            component: CustomReportCreate,
          },
          {
            path: 'edit/:collectorId',
            name: 'custom-report-edit', // 日志接入 - 自定义上报编辑
            meta: {
              needBack: true,
              backName: 'custom-report-list',
            },
            component: CustomReportCreate,
          },
          {
            path: 'detail/:collectorId',
            name: 'custom-report-detail', // 日志接入 - 自定义上报详情
            meta: {
              needBack: true,
              backName: 'custom-report-list',
            },
            component: CustomReportDetail,
          },
        ],
      },
      {
        path: 'collection-track',
        name: 'collection-track', // 全链路追踪 - 采集接入
        component: CollectionTrack,
      },
      {
        path: 'bk-data-track', // 全链路追踪 - 数据平台接入
        name: 'bk-data-track',
        component: IndexSetView,
        redirect: '/manage/bk-data-track/list',
        children: [
          {
            path: 'list',
            name: 'bkdata-track-list',
            component: IndexList,
          },
          {
            path: 'manage/:indexSetId',
            name: 'bkdata-track-manage',
            meta: {
              needBack: true,
              backName: 'bkdata-track-list',
            },
            component: ManageIndex,
          },
          {
            path: 'create',
            name: 'bkdata-track-create',
            meta: {
              needBack: true,
              backName: 'bkdata-track-list',
            },
            component: CreateIndex,
          },
          {
            path: 'edit/:indexSetId',
            name: 'bkdata-track-edit',
            meta: {
              needBack: true,
              backName: 'bkdata-track-list',
            },
            component: CreateIndex,
          },
        ],
      },
      {
        path: 'sdk-track',
        name: 'sdk-track', // 全链路追踪 - SDK接入
        component: SdkTrack,
      },
      {
        path: 'clean-list',
        name: 'clean-list', // 日志清洗
        component: LogCleanView,
        redirect: '/manage/clean-list/list',
        children: [
          {
            path: 'list',
            name: 'log-clean-list', // 日志清洗 - 清洗列表
            component: cleanList,
          },
          {
            path: 'create',
            name: 'clean-create', // 日志清洗 - 新建清洗
            meta: {
              needBack: true,
              backName: 'log-clean-list',
            },
            component: cleanCreate,
          },
          {
            path: 'edit/:collectorId',
            name: 'clean-edit', // 日志清洗 - 编辑清洗
            meta: {
              needBack: true,
              backName: 'log-clean-list',
            },
            component: cleanCreate,
          },
        ],
      },
      {
        path: 'clean-templates',
        name: 'clean-templates', // 日志清洗模板
        component: LogCleanTempView,
        redirect: '/manage/clean-templates/list',
        children: [
          {
            path: 'list',
            name: 'log-clean-templates', // 日志清洗 - 清洗模板
            component: cleanTemplate,
          },
          {
            path: 'create',
            name: 'clean-template-create', // 日志清洗 - 新增模板
            meta: {
              needBack: true,
              backName: 'log-clean-templates',
            },
            component: cleanTempCreate,
          },
          {
            path: 'edit/:templateId',
            name: 'clean-template-edit', // 日志清洗 - 编辑模板
            meta: {
              needBack: true,
              backName: 'log-clean-templates',
            },
            component: cleanTempCreate,
          },
        ],
      },
      {
        path: 'archive-repository',
        name: 'archive-repository', // 日志归档 - 归档仓库
        component: ArchiveRepository,
      },
      {
        path: 'archive-list',
        name: 'archive-list', // 日志归档 - 归档列表
        component: ArchiveList,
      },
      {
        path: 'archive-restore',
        name: 'archive-restore', // 日志归档 - 归档回溯
        component: ArchiveRestore,
      },
      {
        path: 'manage-log-extract',
        name: 'manage-log-extract', // 日志提取 - 提取配置
        component: ExtractPermission,
      },
      {
        path: 'log-extract-task',
        name: 'log-extract-task', // 日志提取 - 提取任务
        component: extract,
        redirect: '/manage/log-extract-task',
        children: [
          {
            path: '',
            name: 'extract-home', // 日志提取 - 提取任务
            component: extractHome,
          },
          {
            path: 'extract-create',
            name: 'extract-create', // 日志提取 - 新建提取任务
            meta: {
              needBack: true,
              backName: 'log-extract-task',
            },
            component: extractCreate,
          },
          {
            path: 'extract-clone',
            name: 'extract-clone', // 日志提取 - 克隆提取任务
            meta: {
              needBack: true,
              backName: 'log-extract-task',
            },
            component: extractCreate,
          },
        ],
      },
      {
        path: 'extract-link-manage',
        name: 'extract-link-manage', // 日志提取 - 链路管理
        component: ExtractLinkView,
        redirect: '/manage/extract-link-manage/list',
        children: [
          {
            path: 'list',
            name: 'extract-link-list',
            component: ExtractLinkList,
          },
          {
            path: 'edit/:linkId',
            name: 'extract-link-edit',
            meta: {
              needBack: true,
              backName: 'extract-link-list',
            },
            component: ExtractLinkCreate,
          },
          {
            path: 'create',
            name: 'extract-link-create',
            meta: {
              needBack: true,
              backName: 'extract-link-list',
            },
            component: ExtractLinkCreate,
          },
        ],
      },
      {
        path: 'es-cluster-manage',
        name: 'es-cluster-manage', // ES集群 - 集群信息
        component: ClusterMess,
      },
      {
        path: 'manage-data-link-conf',
        name: 'manage-data-link-conf', // 管理 - 采集链路管理
        component: DataLinkConf,
      },
    ],
  },
  // {
  //   path: '/notTraceIndex',
  //   name: 'notTraceIndex',
  //   component: page403,
  // },
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
