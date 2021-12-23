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
 * @file main store
 * @author  <>
 */

import Vue from 'vue';
import Vuex from 'vuex';

import retrieve from './retrieve';
import collect from './collect';
import globals from './globals';
import http from '@/api';
import { unifyObjectStyle } from '@/common/util';

Vue.use(Vuex);

const store = new Vuex.Store({
  // 模块
  modules: {
    retrieve,
    collect,
    globals,
  },
  // 公共 store
  state: {
    userMeta: {}, // /meta/mine
    pageLoading: true,
    authDialogData: null,
    // 是否将unix时间戳格式化
    isFormatDate: true,
    // 当前运行环境
    runVersion: '',
    // 系统当前登录用户
    user: {},
    // 是否作为iframe被嵌套
    asIframe: false,
    iframeQuery: {},
    // 当前项目及Id
    project: {},
    projectId: '',
    indexId: '',
    traceIndexId: '',
    // 业务Id
    bkBizId: '',
    bkBizList: [],
    // 我的项目列表
    myProjectList: [],
    currentMenu: {},
    currentMenuItem: {},
    topMenu: [],
    menuList: [],
    // 数据接入权限
    menuProject: [],
    errorPage: ['notTraceIndex'],
    // 全局配置
    globalsData: {},
    activeTopMenu: {},
    activeManageNav: {},
    activeManageSubNav: {},
    // -- id, id对应数据
    collectDetail: [0, {}],
    // 清除table表头宽度缓存
    clearTableWidth: 0,
    showRouterLeaveTip: false,
    // 新人指引
    userGuideData: {},
    curCustomReport: null,
  },
  // 公共 getters
  getters: {
    runVersion: state => state.runVersion,
    user: state => state.user,
    project: state => state.project,
    projectId: state => state.projectId,
    indexId: state => state.indexId,
    traceIndexId: state => state.traceIndexId,
    bkBizId: state => state.bkBizId,
    bkBizList: state => state.bkBizList,
    myProjectList: state => state.myProjectList,
    pageLoading: state => state.pageLoading,
    globalsData: state => state.globalsData,
    // -- 返回数据
    collectDetail: state => state.collectDetail[1],
    asIframe: state => state.asIframe,
    iframeQuery: state => state.iframeQuery,
    accessUserManage: state => Boolean(state.topMenu.find(item => item.id === 'manage')?.
      children.some(item => (item.id === 'permissionGroup' && item.project_manage === true))),
  },
  // 公共 mutations
  mutations: {
    updateUserMeta(state, payload) {
      state.userMeta = payload;
    },
    /**
     * 设置初始化 loading 是否显示
     */
    setPageLoading(state, loading) {
      state.pageLoading = loading;
    },
    updateAuthDialogData(state, payload) {
      state.authDialogData = payload;
    },
    updateIsFormatDate(state, payload) {
      state.isFormatDate = payload;
    },
    /**
     * 更新当前运行环境
     * @param {Object} state store state
     * @param {String} runVersion 运行环境
     */
    updateRunVersion(state, runVersion) {
      state.runVersion = runVersion;
    },
    /**
     * 更新当前用户 user
     *
     * @param {Object} state store state
     * @param {Object} user user 对象
     */
    updateUser(state, user) {
      state.user = Object.assign({}, user);
    },
    /**
     * 更新当前路由对应导航
     */
    updateCurrentMenu(state, current) {
      Vue.set(state, 'currentMenu', current);
    },
    updateCurrentMenuItem(state, item) {
      Vue.set(state, 'currentMenuItem', item);
    },
    updateProject(state, projectId) {
      state.project = state.myProjectList.find(item => item.project_id === projectId) || {};
      state.projectId = projectId;
      state.bkBizId = state.project.bk_biz_id;
    },
    updateMyProjectList(state, projectList) {
      state.myProjectList = [...projectList];
    },
    updateBkBizList(state, bizList) {
      state.bkBizList = bizList;
    },
    updateIndexId(state, indexId) {
      state.indexId = indexId;
    },
    updateTraceIndexId(state, indexId) {
      state.traceIndexId = indexId;
    },
    updateMenuList(state, menuList) {
      state.menuList.splice(0, state.menuList.length, ...menuList);
    },
    updateActiveTopMenu(state, payload) {
      state.activeTopMenu = payload;
    },
    updateActiveManageNav(state, payload) {
      state.activeManageNav = payload;
    },
    updateActiveManageSubNav(state, payload) {
      state.activeManageSubNav = payload;
    },
    updateMenuProject(state, menuProject) {
      state.menuProject.splice(0, state.menuProject.length, ...menuProject);
    },
    updateTopMenu(state, topMenu) {
      state.topMenu.splice(0, state.topMenu.length, ...topMenu);
    },
    updateGlobalsData(state, globalsData) {
      state.globalsData = globalsData;
      Vue.set(state, 'globalsData', globalsData);
    },
    // -- 代码调整 collectDetail: [id, 数据]
    updateCollectDetail(state, collectDetail) {
      const data = collectDetail[1];
      data.params.paths = data.params.paths.map(item => ({ value: item }));
      state.collectDetail = data;
    },
    updateAsIframe(state, asIframe) {
      state.asIframe = asIframe;
    },
    updateIframeQuery(state, iframeQuery) {
      Object.assign(state.iframeQuery, iframeQuery);
    },
    updateClearTableWidth(state, clearTableWidth) {
      state.clearTableWidth += clearTableWidth;
    },
    updateRouterLeaveTip(state, isShow) {
      state.showRouterLeaveTip = isShow;
    },
    setUserGuideData(state, userGuideData) {
      state.userGuideData = userGuideData;
    },
  },
  actions: {
    /**
     * 获取用户信息
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object} config 请求的配置
     *
     * @return {Promise} promise 对象
     */
    userInfo({ commit }, params, config = {}) {
      return http.request('userInfo/getUserInfo', { query: params, config }).then((response) => {
        const userData = response.data || {};
        commit('updateUser', userData);
        return userData;
      });
    },

    /**
     * 获取业务列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object} config 请求的配置
     *
     * @return {Promise} promise 对象
     */
    getBkBizList({ commit }) {
      return http.request('biz/list', {}).then((response) => {
        const bizList = response.data || [];
        commit('updateBkBizList', bizList);
        return bizList;
      })
        .catch((err) => {
          console.warn(err);
        });
    },

    /**
     * 获取菜单列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object} config 请求的配置
     *
     * @return {Promise} promise 对象
     */
    getMenuList({}, projectId) {
      return http.request('meta/menu', {
        query: {
          project_id: projectId,
        },
      });
    },
    getGlobalsData({ commit }) {
      return http.request('collect/globals', { query: {} }).then((response) => {
        const globalsData = response.data || {};
        commit('updateGlobalsData', globalsData);
        return globalsData;
      });
    },
    // -- 代码调整
    getCollectDetail({ commit, state }, data) {
      // 判断是否有该id的缓存数据
      if (state.collectDetail[0] !== data.collector_config_id) {
        commit('updateCollectDetail', [data.collector_config_id, data || {}]);
        return data;
      }
    },
    // 判断有无权限
    checkAllowed(context, paramData) {
      return new Promise(async (resolve, reject) => {
        try {
          const checkRes = await http.request('auth/checkAllowed', {
            data: paramData,
          });
          for (const item of checkRes.data) {
            if (item.is_allowed === false) { // 无权限
              resolve({
                isAllowed: false,
              });
              return;
            }
          }
          // 有权限
          resolve({
            isAllowed: true,
          });
        } catch (err) {
          // 请求出错
          reject(err);
        }
      });
    },
    // 已知无权限，需要获取信息
    getApplyData(context, paramData) {
      return http.request('auth/getApplyData', {
        data: paramData,
      });
    },
    // 判断有无权限，无权限获取相关信息
    checkAndGetData(context, paramData) {
      return new Promise(async (resolve, reject) => {
        try {
          const checkRes = await http.request('auth/checkAllowed', {
            data: paramData,
          });
          for (const item of checkRes.data) {
            if (item.is_allowed === false) { // 无权限
              const applyDataRes = await http.request('auth/getApplyData', {
                data: paramData,
              });
              resolve({
                isAllowed: false,
                data: applyDataRes.data,
              });
              return;
            }
          }
          // 有权限
          resolve({
            isAllowed: true,
          });
        } catch (err) {
          // 请求出错
          reject(err);
        }
      });
    },
  },
});

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * 需要对单独的请求做配置的话，无论是 get 还是 post，store.dispatch 都需要三个参数，例如：
 * store.dispatch('example/btn1', {btn: 'btn1'}, {fromCache: true})
 * 其中第二个参数指的是请求本身的参数，第三个参数指的是请求的配置，如果请求本身没有参数，那么
 * 第二个参数也必须占位，store.dispatch('example/btn1', {}, {fromCache: true})
 * 在 store 中需要如下写法：
 * btn1 ({ commit, state, dispatch }, params, config) {
 *     return http.get(`/app/index?invoke=btn1`, params, config)
 * }
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
  const { type, payload } = unifyObjectStyle(_type, _payload);

  const action = { type, payload, config };
  const entry = store._actions[type];
  if (!entry) {
    if (NODE_ENV !== 'production') {
      console.error(`[vuex] unknown action type: ${type}`);
    }
    return;
  }

  store._actionSubscribers.forEach(sub => sub(action, store.state));

  return entry.length > 1
    ? Promise.all(entry.map(handler => handler(payload, config)))
    : entry[0](payload, config);
};

export default store;
