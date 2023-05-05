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

// 获取采集项清洗缓存
const getCleanStash = {
  url: '/databus/collectors/:collector_config_id/clean_stash/',
  method: 'get',
};

// 更新采集项清洗缓存
const updateCleanStash = {
  url: '/databus/collectors/:collector_config_id/create_clean_stash/',
  method: 'post',
};

// 获取清洗列表
const cleanList = {
  url: '/databus/clean/',
  method: 'get',
};

// 刷新高级清洗
const refreshClean = {
  url: '/databus/clean/:collector_config_id/refresh/',
  method: 'get',
};

// 同步计算平台结果表
const sync = {
  url: '/databus/clean/sync/',
  method: 'get',
};

// 删除清洗项
const deleteClean = {};

// 获取清洗模板列表
const cleanTemplate = {
  url: '/databus/clean_template/',
  method: 'get',
};

// 清洗模板-详情
const templateDetail = {
  url: '/databus/clean_template/:clean_template_id/',
  method: 'get',
};

// 清洗模板-新建
const createTemplate = {
  url: '/databus/clean_template/',
  method: 'post',
};

// 清洗模板-更新
const updateTemplate = {
  url: '/databus/clean_template/:clean_template_id/',
  method: 'put',
};

// 清洗模板-删除
const deleteTemplate = {
  url: '/databus/clean_template/:clean_template_id/',
  method: 'delete',
};

// 预览提取结果
const getEtlPreview = {
  url: '/databus/clean_template/etl_preview/',
  method: 'post',
};

// 清洗清洗列表-删除
const deleteParsing = {
  url: '/databus/clean/:collector_config_id/destroy_clean/',
  method: 'delete',
};

export {
  getCleanStash,
  updateCleanStash,
  cleanList,
  refreshClean,
  sync,
  deleteClean,
  cleanTemplate,
  templateDetail,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  getEtlPreview,
  deleteParsing,
};
