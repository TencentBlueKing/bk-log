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

import i18n from '@/language/i18n';

export const fieldTypeMap = {
  any: {
    name: i18n.t('不限'),
    icon: 'bk-icon icon-check-line',
  },
  number: {
    name: i18n.t('数字'),
    icon: 'log-icon icon-number',
  },
  integer: {
    name: i18n.t('数字'),
    icon: 'log-icon icon-number',
  },
  double: {
    name: i18n.t('数字'),
    icon: 'log-icon icon-number',
  },
  keyword: {
    name: i18n.t('字符串'),
    icon: 'log-icon icon-string',
  },
  long: {
    name: i18n.t('数字'),
    icon: 'log-icon icon-number',
  },
  text: {
    name: i18n.t('文本'),
    icon: 'log-icon icon-text',
  },
  date: {
    name: i18n.t('时间'),
    icon: 'bk-icon icon-clock',
  },
  boolean: {
    name: i18n.t('布尔'),
    icon: 'log-icon icon-boolean',
  },
  conflict: {
    name: i18n.t('冲突字段'),
    icon: 'bk-icon icon-exclamation-triangle',
  },
  __virtual__: {
    name: i18n.t('该字段为平台补充 不可检索'),
    icon: 'log-icon icon-ext',
  },
};

export const SPACE_TYPE_MAP = {
  bkcc: {
    name: i18n.t('业务'),
    dark: {
      color: '#478EFC',
      backgroundColor: '#2B354D',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#CDE8FB',
    },
  },
  default: {
    name: i18n.t('监控空间'),
    dark: {
      color: '#B3B3B3',
      backgroundColor: '#333333',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#DEDEDE',
    },
  },
  bkci: {
    name: i18n.t('研发项目'),
    dark: {
      color: '#F85959',
      backgroundColor: '#4C3232',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#F8D8D4',
    },
  },
  bcs: {
    name: i18n.t('容器项目'),
    dark: {
      color: '#FC943B',
      backgroundColor: '#453921',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#FFF2C9',
    },
  },
  paas: {
    name: i18n.t('PaaS应用'),
    dark: {
      color: '#2BB950',
      backgroundColor: '#223B2B',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#D8EDD9',
    },
  },
  bksaas: {
    name: i18n.tc('PaaS应用'),
    dark: {
      color: '#2BB950',
      backgroundColor: '#223B2B',
    },
    light: {
      color: '#63656E',
      backgroundColor: '#D8EDD9',
    },
  },
};
