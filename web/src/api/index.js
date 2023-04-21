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
 * @file axios 封装
 * @author  <>
 */

import Vue from 'vue';
import axios from 'axios';
import store from '@/store';
import { bus } from '@/common/bus';
import { messageError } from '@/common/bkmagic';
import CachedPromise from './cached-promise';
import RequestQueue from './request-queue';
import HttpRequst from './_httpRequest';
import mockList from '@/mock/index.js';
import serviceList from '@/services/index.js';
import { context, trace } from '@opentelemetry/api';
import { makeMessage } from '@/common/util';
import i18n from '@/language/i18n';

const baseURL = window.AJAX_URL_PREFIX || '/api/v1';
// axios 实例
const axiosInstance = axios.create({
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
  xsrfCookieName: 'bklog_csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
  baseURL,
});

/**
 * request interceptor
 */
axiosInstance.interceptors.request.use((config) => {
  // 绝对路径不走 mock
  if (!/^(https|http)?:\/\//.test(config.url)) {
    // const prefix = config.url.indexOf('?') === -1 ? '?' : '&';
    config.url = config.url;
  }
  return config;
}, error => Promise.reject(error));

/**
 * response interceptor
 */
axiosInstance.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error),
);

const http = {
  $request: new HttpRequst(axiosInstance, { mockList, serviceList }),
  queue: new RequestQueue(),
  cache: new CachedPromise(),
  cancelRequest: requestId => http.queue.cancel(requestId),
  cancelCache: requestId => http.cache.delete(requestId),
  cancel: requestId => Promise.all([http.cancelRequest(requestId), http.cancelCache(requestId)]),
};

// const methodsWithoutData = ['delete', 'get', 'head', 'options']
// const methodsWithData = ['post', 'put', 'patch']
// const allMethods = [...methodsWithoutData, ...methodsWithData]

Object.defineProperty(http, 'request', {
  get() {
    return getRequest('request');
  },
});

/**
 * 获取 http 不同请求方式对应的函数
 *
 * @param {string} http method 与 axios 实例中的 method 保持一致
 *
 * @return {Function} 实际调用的请求函数
 */
function getRequest(method) {
  // if (methodsWithData.includes(method)) {
  //     return (url, data, config) => getPromise(method, url, data, config)
  // }
  // return (url, config) => getPromise(method, url, null, config)
  return (url, data, config) => getPromise(method, url, data, config);
}

/**
 * 实际发起 http 请求的函数，根据配置调用缓存的 promise 或者发起新的请求
 *
 * @param {method} http method 与 axios 实例中的 method 保持一致
 * @param {string} 请求地址
 * @param {Object} 需要传递的数据, 仅 post/put/patch 三种请求方式可用
 * @param {Object} 用户配置，包含 axios 的配置与本系统自定义配置
 *
 * @return {Promise} 本次http请求的Promise
 */
async function getPromise(method, url, data, userConfig = {}) {
  const config = initConfig(method, url, userConfig);
  let promise;
  if (config.cancelPrevious) {
    await http.cancel(config.requestId);
  }

  if (config.clearCache) {
    http.cache.delete(config.requestId);
  } else {
    promise = http.cache.get(config.requestId);
  }

  if (config.fromCache && promise) {
    return promise;
  }

  // promise = new Promise(async (resolve, reject) => {
  //   const axiosRequest = http.$request.request(url, data, config);

  //   try {
  //     const response = await axiosRequest;
  //     Object.assign(config, response.config || {});
  //     handleResponse({ config, response, resolve, reject });
  //   } catch (error) {
  //     Object.assign(config, error.config);
  //     reject(error);
  //   }
  // }).catch(error => handleReject(error, config))
  //   .finally(() => {
  //   // console.log('finally', config)
  //   });

  promise = new Promise(async (resolve, reject) => {
    context.with(trace.setSpan(context.active(), config.span), async () => {
      try {
        const axiosRequest = http.$request.request(url, data, config);
        const response = await axiosRequest;
        Object.assign(config, response.config || {});
        handleResponse({ config, response, resolve, reject });
      } catch (error) {
        Object.assign(config, error.config);
        reject(error);
      }
    });
  }).catch(error => handleReject(error, config))
    .finally(() => {
    // console.log('finally', config)
    });

  // 添加请求队列
  http.queue.set(config);
  // 添加请求缓存
  http.cache.set(config.requestId, promise);

  return promise;
}

/**
 * 处理 http 请求成功结果
 *
 * @param {Object} 请求配置
 * @param {Object} cgi 原始返回数据
 * @param {Function} promise 完成函数
 * @param {Function} promise 拒绝函数
 */
function handleResponse({ config, response, resolve, reject }) {
  const { code } = response;
  if (code === '9900403') {
    reject({ message: response.message, code, data: response.data || {} });
    store.commit('updateAuthDialogData', {
      apply_url: response.data.apply_url,
      apply_data: response.permission,
    });
  } else if (code !== 0 && config.globalError) {
    reject({ message: response.message, code, data: response.data || {} });
  } else {
    resolve(config.originalResponse ? response : response.data, config);
  }
  http.queue.delete(config.requestId);
}

/**
 * 处理 http 请求失败结果
 *
 * @param {Object} Error 对象
 * @param {config} 请求配置
 *
 * @return {Promise} promise 对象
 */
function handleReject(error, config) {
  if (axios.isCancel(error)) {
    return Promise.reject(error);
  }
  // const service = getHttpService(url, serviceList);
  // const ajaxUrl = service ? service.url : '';
  // console.error('Request error UrlPath：', ajaxUrl);
  const traceparent = config.span._spanContext.traceId;

  http.queue.delete(config.requestId);

  // 捕获 http status 错误
  if (config.globalError && error.response) {
    // status 是 httpStatus
    const { status, data } = error.response;
    const nextError = { message: error.message, response: error.response };
    // 弹出登录框不需要出 bkMessage 提示
    if (status === 401) {
      // 窗口登录，页面跳转交给平台返回302
      const handleLoginExpire = () => {
        window.location.href = `${window.BK_PLAT_HOST.replace(/\/$/g, '')}/login/`;
      };
      const loginData = error.response.data;
      if (loginData.has_plain) {
        try {
          window.LoginModal.$props.loginUrl = loginData.login_url;
          window.LoginModal.show();
        } catch (_) {
          handleLoginExpire();
        }
      } else {
        handleLoginExpire();
      }
      return Promise.reject(nextError);
    } if (status === 500) {
      nextError.message = i18n.t('系统出现异常');
    } else if (data && data.message) {
      nextError.message = data.message;
    }
    const resMessage = makeMessage(nextError.message, traceparent);
    config.catchIsShowMessage && messageError(resMessage);
    console.error(nextError.message);
    return Promise.reject(nextError);
  }

  // 捕获业务 code 错误
  const { code } = error;
  if (code === '9900403') {
    return Promise.reject(new Error(error.message));
  }

  if (config.globalError && code !== 0) {
    const message = error.message || i18n.t('系统出现异常');
    if (code !== 0 && code !== '0000' && code !== '00') {
      if (code === 4003) {
        bus.$emit('show-apply-perm', error.data);
      } else if (code === 4005) {
        bus.$emit('show-apply-perm-modal', error.data);
      } else if (code === '3621602') {
        return 1;
      } else {
        const resMessage = makeMessage(message, traceparent);
        config.catchIsShowMessage && messageError(resMessage);
      }
    }
    return Promise.reject(new Error(message));
  }

  const resMessage = makeMessage(error.message, traceparent);
  config.catchIsShowMessage && messageError(resMessage);
  console.error(error.message);
  return Promise.reject(error);
}

/**
 * 初始化本系统 http 请求的各项配置
 *
 * @param {string} http method 与 axios 实例中的 method 保持一致
 * @param {string} 请求地址, 结合 method 生成 requestId
 * @param {Object} 用户配置，包含 axios 的配置与本系统自定义配置
 *
 * @return {Promise} 本次 http 请求的 Promise
 */
function initConfig(method, url, userConfig) {
  const defaultConfig = {
    ...getCancelToken(),
    // http 请求默认 id
    requestId: `${method}_${url}`,
    // 是否全局捕获异常
    globalError: true,
    // 是否直接复用缓存的请求
    fromCache: false,
    // 是否在请求发起前清楚缓存
    clearCache: false,
    // 响应结果是否返回原始数据
    originalResponse: true,
    // 当路由变更时取消请求
    cancelWhenRouteChange: true,
    // 取消上次请求
    cancelPrevious: true,
    // 接口报错是否弹bkMessage弹窗
    catchIsShowMessage: true,
    span: trace.getTracer('bk-log').startSpan('api'),
  };
  return Object.assign(defaultConfig, userConfig);
}

/**
 * 生成 http 请求的 cancelToken，用于取消尚未完成的请求
 *
 * @return {Object} {cancelToken: axios 实例使用的 cancelToken, cancelExcutor: 取消http请求的可执行函数}
 */
function getCancelToken() {
  let cancelExcutor;
  const cancelToken = new axios.CancelToken((excutor) => {
    cancelExcutor = excutor;
  });
  return {
    cancelToken,
    cancelExcutor,
  };
}

// function getHttpService(url, serverList) {
//   const splitor = url.split('/').filter(f => f);

//   let _service = splitor[1]
//     ? serverList[splitor[0]][splitor[1]]
//     : serverList[splitor[0]];
//   if (typeof _service === 'function') {
//     _service = _service(url, serverList);
//   }
//   return _service;
// }

Vue.prototype.$http = http;

export default http;
