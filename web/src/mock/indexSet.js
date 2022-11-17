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

// 索引集列表
const list = {
  message: '',
  code: 0,
  data: {
    total: 100,
    took: 0.29,
    list: [
      {
        index_set_id: 1,
        index_set_name: '登陆日志',
        space_uid: 1,
        source_id: 1,
        source_name: 'ES集群',
        scenario_id: 'es',
        scenario_name: '用户ES',
        orders: 1,
        view_roles: [1, 2, 3],
        view_roles_list: [
          {
            role_id: 1,
            role_name: '运维',
          },
          {
            role_id: 2,
            role_name: '产品',
          },
        ],
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
      },
    ],
  },
  result: true,
};

const info = {
  message: '',
  code: 0,
  data: {
    index_set_id: 1,
    index_set_name: '登陆日志',
    space_uid: 1,
    source_id: 1,
    source_name: 'ES集群',
    scenario_id: 'es',
    scenario_name: '用户ES',
    orders: 1,
    view_roles: [1, 2, 3],
    view_roles_list: [
      {
        role_id: 1,
        role_name: '运维',
      },
      {
        role_id: 2,
        role_name: '产品',
      },
    ],
    created_at: '2019-10-10 11:11:11',
    created_by: 'user',
    updated_at: '2019-10-10 11:11:11',
    updated_by: 'user',
  },
  result: true,
};

// 创建索引集
const create = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

const update = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

// 删除索引集
const remove = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

// 索引列表
const index = {
  message: '',
  code: 0,
  data: {
    total: 100,
    took: 0.29,
    list: [
      {
        index_id: 1,
        index_set_id: 1,
        bk_biz_id: 1,
        bk_biz_name: '蓝鲸',
        result_table_id: '1',
        result_table_name_alias: '32_log_error*',
        time_field: '时间字段',
        apply_status: 'pending',
        apply_status_name: '已授权',
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
      },
    ],
  },
  result: true,
};

// 创建索引
const createIndex = {
  message: 'success',
  code: 0,
  data: '',
  result: true,
};

// 删除索引
const removeIndex = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

export default {
  list,
  info,
  create,
  update,
  remove,
  index,
  removeIndex,
  createIndex,
};
