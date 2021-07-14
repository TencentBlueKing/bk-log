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

export default  {
  name: '', // 图表名称
  series: [
    {
      dimensions: {
        bk_target_ip: '127.0.0.1',
      },
      target: 'MEAN(used)[bk_target_ip: 127.0.0.1]',
      threshold: { // 阈值
        value: 100,
        name: '阈值',
      },
      unit: '%', // 单位
      datapoints: [
        [622, 1450754160000],
        [365, 1450754220000],
      ],
    },
    {
      dimensions: {
        bk_target_ip: '127.0.0.1',
      },
      target: 'MEAN(used)[bk_target_ip: 127.0.0.1]',
      threshold: { // 阈值
        value: 100,
        name: '阈值',
      },
      unit: '%', // 单位
      datapoints: [
        [622, 1450754160000],
        [365, 1450754220000],
      ],
    },
  ],
};
