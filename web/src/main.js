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

import './public-path';
import Vue from 'vue';
import App from './App';
import router from './router';
import store from './store';
import http from './api';
import { bus } from './common/bus';
import i18n from '@/language/i18n';
import methods from './plugins/methods';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import cursor from '@/directives/cursor';
import LogButton from '@/components/log-button';
import docsLinkMixin from '@/mixins/docs-link-mixin';
import { renderHeader } from './common/util';
import './common/global';
import './static/icons/log-icons.css';
// 接入OTLP
import { WebTracerProvider } from '@opentelemetry/web';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { ZoneContextManager } from '@opentelemetry/context-zone';

const provider = new WebTracerProvider();
provider.register({
  contextManager: new ZoneContextManager(),
});
registerInstrumentations({
  instrumentations: [new XMLHttpRequestInstrumentation(
    {
      // propagateTraceHeaderCorsUrls: new RegExp('.*'),
    },
  )],
});
const tracer = provider.getTracer('bk-log');
Vue.prototype.$renderHeader = renderHeader;
Vue.prototype.tracer = tracer;

try {
  const id = window.TAM_AEGIS_KEY;
  if (id) {
    const aegis = new window.Aegis({
      id, // 项目key
      reportApiSpeed: true, // 接口测速
      reportAssetSpeed: true, // 静态资源测速
      spa: true,
    });
    window.__aegisInstance = aegis;
    Vue.config.errorHandler = function (err, vm, info) {
      aegis.error(`Error: ${err.toString()}\nInfo: ${info}`);
    };
  }
} catch (e) {
  console.warn('前端监控接入出错', e);
}

router.onError((err) => {
  const pattern = /Loading (CSS chunk|chunk) (\d)+ failed/g;
  const isChunkLoadFailed = err.message.match(pattern);
  const targetPath = router.history.pending.fullPath;
  if (isChunkLoadFailed) {
    router.replace(targetPath);
  }
});

Vue.component('VueJsonPretty', VueJsonPretty);
Vue.component('LogButton', LogButton);
Vue.directive('cursor', cursor);
Vue.mixin(docsLinkMixin);
Vue.use(methods);

if (process.env.NODE_ENV === 'development') {
  http.request('meta/getEnvConstant').then((res) => {
    const data = res.data;
    Object.keys(data).forEach((key) => {
      window[key] = data[key];
    });
    window.FEATURE_TOGGLE = JSON.parse(data.FEATURE_TOGGLE);
    window.FEATURE_TOGGLE_WHITE_LIST = JSON.parse(data.FEATURE_TOGGLE_WHITE_LIST);
    window.bus = bus;
    window.mainComponent = new Vue({
      el: '#app',
      router,
      store,
      i18n,
      components: {
        App,
      },
      template: '<App/>',
    });
    Vue.config.devtools = true;
  });
} else {
  window.bus = bus;
  window.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    i18n,
    components: {
      App,
    },
    template: '<App/>',
  });
  Vue.config.devtools = true;
}
