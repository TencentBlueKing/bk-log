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
 * @file cluster all
 * @author  <>
 */

import faker from 'faker';
import chalk from 'chalk';

export async function response(getArgs, postArgs, req) {
  console.log(chalk.cyan('req', req.method));
  console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)));
  console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)));
  const invoke = getArgs.invoke;
  if (invoke === 'userInfo') {
    return {
      code: 0,
      message: '获取用户信息成功',
      data: {
        chinese_name: faker.name.findName(),
        avatar_url: '',
        bkpaas_user_id: '023cc1ef9c8b4a90a7',
        username: 'hieiwang',
        permissions: [],
        latest_project_id: '846e8195d9ca4097b354ed190acce4b1',
        latest_project_code: 'bcs1',
      },
    };
  }
  return {
    code: 0,
    data: {},
  };
}
