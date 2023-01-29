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

import { formatDate } from '@/common/util';

export default {
  computed: {
    // 是否转换日期类型字段格式
    isFormatDate() {
      return this.$store.state.isFormatDate;
    },
  },
  methods: {
    /**
     * 获取 row[key] 内容
     * @example return row.a.b || row['a.b']
     * @param {Object} row
     * @param {String} key
     * @param {String} fieldType
     * @param {Boolean} isFormatDate
     * @return {String|Number}
     */
    tableRowDeepView(row, key, fieldType, isFormatDate = this.isFormatDate) {
      const keyArr = key.split('.');
      let data;

      try {
        if (keyArr.length === 1) {
          data = row[key];
        } else {
          for (let index = 0; index < keyArr.length; index++) {
            const item = keyArr[index];

            if (index === 0) {
              data = row[item];
              continue;
            }

            if (data === undefined) {
              break;
            }

            if (data[item]) {
              data = data[item];
            } else {
              // 如果 x.y 不存在 返回 x['y.z'] x['y.z.z.z'] ...
              const validKey = keyArr.splice(index, keyArr.length - index).join('.');
              data = data[validKey];
              break;
            }
          }
        }
      } catch (e) {
        console.warn('List data analyses error：', e);
        data = '--';
      }

      if (isFormatDate && fieldType === 'date') {
        return formatDate(Number(data)) || data || '--';
      }

      if (Array.isArray(data)) {
        return data.toString();
      }

      if (typeof data === 'object' && data !== null) {
        return JSON.stringify(data);
      }

      return (data || data === 0) ? data : '--';
    },
  },
};
