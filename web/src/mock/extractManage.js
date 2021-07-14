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

const getStrategyList = [{
  strategy_id: 1,
  strategy_name: '105业务',
  created_by: 'ADMIN',
  created_at: '2020-06-21 03:09:43',
  user_list: ['48568920'],
  visible_dir: [
    '/data/log/cc/',
    '/data/cc/',
  ],
  file_type: [
    '.log',
  ],
  select_type: 'topo',
  modules: [{
    bk_inst_id: 2,
    bk_inst_name: '蓝鲸',
    bk_obj_id: 'biz',
    bk_obj_name: '业务',
  }],
}, {
  strategy_id: 2,
  strategy_name: '10fd业务',
  created_by: 'ADMIN',
  created_at: '2020-06-21 03:09:43',
  user_list: ['48568920', '4894869'],
  visible_dir: [
    '/data/log/cc/',
    '/data/cc/',
  ],
  file_type: [
    '.log', '.vue',
  ],
  select_type: 'topo',
  modules: [{
    bk_inst_id: 3,
    bk_inst_name: '作业平台',
    bk_obj_id: 'set',
    bk_obj_name: '集群',
  }, {
    bk_inst_id: 50,
    bk_inst_name: 'appengine',
    bk_obj_id: 'module',
    bk_obj_name: '模块',
  }],
}];

export default {
  getStrategyList,
};
