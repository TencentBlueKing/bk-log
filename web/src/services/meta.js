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
 * 通知列表
 */
const type = {
  url: '/meta/msg_type/',
  method: 'get',
};

// 支持的语言列表
const language = {
  url: '/meta/language/',
  method: 'get',
};

// 修改语言
const updateLanguage = {
  url: '/meta/language/',
  method: 'post',
};

// 获取接入场景
const scenario = {
  url: '/meta/scenario/',
  method: 'get',
};

// 获取菜单列表吧
const menu = {
  url: '/meta/menu/',
  method: 'get',
};

// 根据业务id获取业务名、运维人员id信息
const getMaintainerApi = {
  url: '/meta/biz_maintainer/',
  method: 'get',
};

const footer = {
  url: '/meta/footer_html/',
  method: 'get',
};

// 获取新人指引
const getUserGuide = {
  url: '/meta/user_guide/',
  method: 'get',
};

// 更新新人指引
const updateUserGuide = {
  url: '/meta/update_user_guide/',
  method: 'post',
};

export {
  type,
  language,
  updateLanguage,
  scenario,
  menu,
  footer,
  getMaintainerApi,
  getUserGuide,
  updateUserGuide,
};
