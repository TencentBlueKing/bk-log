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

// 使用方法
// const res = await this.$http.request('/traceDetail/getTableField', {
//     data: { display_fields: newFieldsList },
//     mock: true,
//     timeout: 500
// })

import retrieve from './retrieve';
import source from './source';
import indexSet from './indexSet';
import meta from './meta';
import monitor from './monitor';
import auth from './auth';
import plugins from './plugins';
import resultTables from './result-tables';
import biz from './biz';
import collect from './collect';
import particulars from './particulars';
import trace from './trace';
import traceDetail from './trace-detail';
import extract from './extract';
import extractManage from './extract-manage';

const getTest = {
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
        bk_biz_name: '业务名称',
        result_table_id: '结果表',
        time_field: '时间字段',
        apply_status: 'pending',
        apply_status_name: '审核状态名称',
        created_at: '2019-10-10 11:11:11',
        created_by: 'user',
        updated_at: '2019-10-10 11:11:11',
        updated_by: 'user',
      },
    ],
  },
  result: true,
};
const getMyProjectList = {
  message: '',
  code: 0,
  data: [
    {
      space_uid: 1,
      space_name: '业务名称',
      bk_biz_id: 1,
      bk_app_code: 'bk_log',
      time_zone: 'Asia/Shanghai',
      description: '项目描述',
    },
  ],
  result: true,
};

export default {
  example: {
    getTest,
  },
  project: {
    getMyProjectList,
  },
  retrieve,
  indexSet,
  source,
  meta,
  monitor,
  auth,
  plugins,
  resultTables,
  biz,
  particulars,
  collect,
  traceDetail,
  trace,
  extract,
  extractManage,
};
