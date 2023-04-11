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

// 是否有权限
const checkAllowed = [{
  action_id: 'view_business',
  is_allowed: true,
}, {
  action_id: 'view_business',
  is_allowed: false,
  // 'is_allowed': true
}];

// 权限申请数据
const getApplyData = {
  apply_url: 'https://www.qq.com',
  apply_data: {
    system_id: 'bk_log_search',
    system_name: '日志平台',
    actions: [{
      id: 'view_business',
      name: '业务查看',
      related_resource_types: [{
        system_id: 'bk_cmdb',
        system_name: '配置平台',
        type: 'business',
        type_name: '业务',
        instances: [
          [
            {
              type: 'business',
              type_name: '业务',
              id: '2',
              name: '蓝鲸',
            },
          ],
        ],
      }],
    }, {
      id: 'create_collection',
      name: '采集新建',
      related_resource_types: [{
        system_id: 'bk_cmdb',
        system_name: '配置平台',
        type: 'business',
        type_name: '业务',
        instances: [
          [
            {
              type: 'business',
              type_name: '业务',
              id: '2',
              name: '蓝鲸',
            },
          ],
        ],
      }],
    }],
  },
};
/**
 * 用户组列表
 */
const list = {
  message: '',
  code: 0,
  data: [
    {
      group_id: 1,
      group_name: '运维',
      group_type: 'custom',
      space_uid: 1,
      is_editable: false,
      users: ['admin', 'zhangyuting'],
      created_at: '2019-10-10 11:11:11',
      created_by: 'user',
      updated_at: '2019-10-10 11:11:11',
      updated_by: 'user',
    },
  ],
  result: true,
};

/**
 * 创建用户组
 */
const create = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

/**
 * 删除用户组
 */
const remove = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

/**
 * 编辑用户组
 */
const update = {
  message: '',
  code: 0,
  data: '',
  result: true,
};

export default {
  checkAllowed, getApplyData,
  list, create, remove, update,
};
