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

import { random } from '@/components/monitor-echarts/utils';

export default {
  namespaced: true,
  state: {
    chartKey: random(10), // 复用监控的图表，改变key重新请求图表
    cacheDatePickerValue: [],
    cacheTimeRange: '',
    displayRetrieve: false,
    filedSettingConfigID: 1,
  },
  mutations: {
    updateChartKey(state) {
      state.chartKey = random(10);
    },
    updateCachePickerValue(state, payload) {
      state.cacheDatePickerValue = payload;
    },
    updateCacheTimeRange(state, payload) {
      state.cacheTimeRange = payload;
    },
    updateDisplayRetrieve(state, display) {
      state.displayRetrieve = display;
    },
    updateFiledSettingConfigID(state, payload) {
      state.filedSettingConfigID = payload;
    },
  },
  actions: {},
};
