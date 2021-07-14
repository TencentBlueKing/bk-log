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

const getTableData = {
  from: 1583829446891921,
  to: 1583829446946151,
  tag: {
    service: 'service111',
  },
  parentId: '111',
  traceId: '111',
  spanId: '111',
  span: 'span111',
  return_code: '40001',
  children: [{
    from: 1583829446892421,
    to: 1583829446946051,
    tag: {
      service: 'service222',
    },
    traceId: '222',
    spanId: '222',
    span: 'span111',
    return_code: '40001',
    children: [{
      from: 1583829446891921,
      to: 1583829446946151,
      tag: {
        service: 'service333',
      },
      traceId: '222',
      spanId: '333',
      span: 'span111',
      return_code: '40001',
      children: [{
        from: 1583829446899921,
        to: 1583829446944151,
        tag: {
          service: 'service444',
        },
        traceId: '222',
        spanId: '444',
        span: 'span111',
        return_code: '40001',
      }],
    }],
  }, {
    from: 1583829446901921,
    to: 1583829446942151,
    tag: {
      service: 'service22222222',
    },
    traceId: '222222',
    spanId: '2222222',
    span: 'span111',
    return_code: '40001',
  }],
};

const getTableField = {
  fields: [{
    field_type: 'text',
    field_name: 'tag.service',
    field_alias: '',
    is_display: true,
    is_editable: true,
    tag: 'metric',
    es_doc_values: false,
    description: '服务',
  }, {
    field_type: 'long',
    field_name: 'spanId',
    field_alias: '',
    is_display: true,
    is_editable: true,
    tag: 'dimension',
    es_doc_values: true,
    description: 'spanId',
  }, {
    field_type: 'long',
    field_name: 'span',
    field_alias: '',
    is_display: false,
    is_editable: true,
    tag: 'dimension',
    es_doc_values: true,
    description: 'spanssssssssssssss fdsfds fdsa sssssss',
  }, {
    field_type: 'long',
    field_name: 'return_code',
    field_alias: '',
    is_display: true,
    is_editable: true,
    tag: 'dimension',
    es_doc_values: true,
    description: '返回码',
  }],
  display_fields: ['tag.service', 'spanId', 'return_code'],
  sort_list: [['dtEventTimeStamp', 'desc'], ['gseIndex', 'desc'], ['iterationIndex', 'desc']],
  context_search_usable: true,
  realtime_search_usable: true,
  ip_topo_switch: true,
};

const getLogList = [{
  tag: {
    service: '服务111',
  },
  spanId: 'spanId111',
  span: 'span111',
  return_code: 'return_code111',
}, {
  tag: {
    service: '服务111222',
  },
  spanId: 'spanId111',
  span: 'span111',
  return_code: 'return_code111',
}, {
  tag: {
    service: '服务111333',
  },
  spanId: 'spanId111',
  span: 'span111',
  return_code: 'return_code111',
}, {
  tag: {
    service: '服务111444',
  },
  spanId: 'spanId111',
  span: 'span111',
  return_code: 'return_code111',
}];

export default {
  getTableData,
  getTableField,
  getLogList,
};
