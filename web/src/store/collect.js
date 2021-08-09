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

import vue from 'vue';

export default {
  namespaced: true,
  state: {
    curCollect: {},
    curIndexSet: {},
    scenarioMap: null,
  },
  getters: {
    curCollect: state => state.curCollect,
  },
  mutations: {
    setCurCollect(state, collect) {
      vue.set(state, 'curCollect', collect);
    },
    updateCurCollect(state, collect) {
      for (const key in collect) {
        // eslint-disable-next-line no-prototype-builtins
        if (state.curCollect.hasOwnProperty(key)) {
          state.curCollect[key] = collect[key];
        } else {
          vue.set(state.curCollect, key, collect[key]);
        }
      }
    },
    updateCurIndexSet(state, payload) {
      state.curIndexSet = payload;
    },
    updateScenarioMap(state, payload) {
      state.scenarioMap = payload;
    },
  },
  actions: {},
};
