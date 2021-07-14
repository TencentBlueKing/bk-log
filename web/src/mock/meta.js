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


const users = {
  message: '',
  code: 0,
  data: [
    {
      username: 'admin',
      chname: 'admin',
      language: 'zh-cn',
      time_zone: 'Asia/Shanghai',
    },
    {
      username: 'zhang',
      chname: 'zhangyuting',
      language: 'zh-cn',
      time_zone: 'Asia/Shanghai',
    },
  ],
  result: true,
};

const type = {
  message: '',
  code: 0,
  data: [
    {
      type: 'weixin',
      label: '微信',
    },
    {
      type: 'mail',
      label: '邮件',
    },
    {
      type: 'sms',
      label: '短信',
    },
    {
      type: 'voice',
      label: '语音',
    },
  ],
  result: true,
};

const language = {
  message: '',
  code: 0,
  data: [
    {
      id: 'zh-hans',
      name: '中文',
    },
    {
      id: 'en',
      name: '英文',
    },
  ],
  result: true,
};

const updateLanguage = {
  message: '',
  code: 0,
  data: [],
  result: true,
};

// 获取接入场景
const scenario = {
  message: '',
  code: 0,
  data: [],
  result: true,
};

export default {
  users,
  type,
  language,
  updateLanguage,
  scenario,
};
