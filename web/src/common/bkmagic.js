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
 * @file 引入 bk-magic-vue 组件
 * @author <>
 */

import Vue from 'vue';

// 全量引入
// import './fully-import'

// 按需引入
import './demand-import';

const Message = Vue.prototype.$bkMessage;

export const messageError = (message, delay = 3000, ellipsisLine = 0) => {
  Message({
    message,
    delay,
    ellipsisLine,
    theme: 'error',
  });
};

export const messageSuccess = (message, delay = 3000, ellipsisLine = 0) => {
  Message({
    message,
    delay,
    ellipsisLine,
    theme: 'success',
  });
};

export const messageInfo = (message, delay = 3000, ellipsisLine = 0) => {
  Message({
    message,
    delay,
    ellipsisLine,
    theme: 'primary',
  });
};

export const messageWarn = (message, delay = 3000, ellipsisLine = 0) => {
  Message({
    message,
    delay,
    ellipsisLine,
    theme: 'warning',
  });
};

Vue.prototype.messageError = messageError;
Vue.prototype.messageSuccess = messageSuccess;
Vue.prototype.messageInfo = messageInfo;
Vue.prototype.messageWarn = messageWarn;
