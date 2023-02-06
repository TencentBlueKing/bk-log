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

import Vue from 'vue';
import VueI18n from 'vue-i18n';
import jsCookie from 'js-cookie';
import { locale, lang } from 'bk-magic-vue';
// import en from './lang/en';
// import zh from './lang/zh';
import { logEnJson } from './lang/en/index';

Vue.use(VueI18n);

const localLanguage = jsCookie.get('blueking_language') || 'zh-cn';
// 等组件语言升级后删掉这代码
if (localLanguage === 'en') {
  locale.use(lang.enUS);
}
const i18n = new VueI18n({
  // 语言标识
  locale: localLanguage,
  fallbackLocale: 'zh-cn',
  // this.$i18n.locale 通过切换locale的值来实现语言切换
  messages: {
    // 中文语言包
    // 'zh-cn': Object.assign(lang.zhCN, zh),
    'zh-cn': Object.assign(lang.zhCN),
    // 英文语言包
    // en: Object.assign(lang.enUS, en),
    en: Object.assign(lang.enUS, logEnJson),
  },
});
locale.i18n((key, value) => i18n.t(key, value));

export default i18n;
