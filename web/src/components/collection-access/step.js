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

export const stepsConf = {
  // 采集新增或编辑未完成，itsm
  itsm: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],

  // 采集新增
  add: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 采集修改
  edit: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 采集修改
  editFinish: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 字段提取
  field: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 存储
  storage: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 容器日志
  container: [
    { title: window.mainComponent.$t('采集配置'), icon: '' },
    { title: window.mainComponent.$t('字段清洗'), icon: '' },
    { title: window.mainComponent.$t('存储'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 开始采集
  start: [
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
  // 停止采集
  stop: [
    { title: window.mainComponent.$t('采集下发'), icon: '' },
    { title: window.mainComponent.$t('完成'), icon: '' },
  ],
};

export const finishRefer = {
  add: 5,
  edit: 5,
  editFinish: 5,
  field: 5,
  storage: 5,
  container: 5,
  start: 2,
  stop: 2,
};
