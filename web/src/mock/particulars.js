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

const collectList = {
  message: '',
  code: 0,
  data: {
    contents: [
      {
        is_label: false,
        label_name: '',
        bk_obj_name: '集群',
        node_path: '蓝鲸/test1/PaaS平台',
        bk_obj_id: 'set',
        child: [
          {
            status: 'FAILED',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
          {
            status: 'FAILED',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
          {
            status: 'SUCCESS',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
          {
            status: 'SUCCESS',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
          {
            status: 'SUCCESS',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
          {
            status: 'PENDING',
            ip: '',
            bk_cloud_id: 0,
            instance_name: '',
            plugin_version: '1.1',
            instance_id: '',
            bk_supplier_id: 0,
            create_time: '2019-08-24T18:47:27',
          },
        ],
        bk_inst_id: 6,
        bk_inst_name: 'PaaS平台',
      },
    ],
  },
  result: true,
};
const detailsList = {
  message: '',
  code: 0,
  data: {
    collector_scenario_id: 'row',
    collector_config_name: '我叫access的',
    category_id: 'os',
    category_name: '主机-操作系统',
    target_nodes: [
      {
        id: 12,
      },
      {
        bk_inst_id: 33,   // 节点实例ID
        bk_obj_id: 'module',  // 节点对象ID
      },
      {
        ip: '',
        bk_cloud_id: 0,
        bk_supplier_id: 0,
      },
    ],
    data_encoding: 'utf-8',
    bk_data_name: '存储索引名',
    description: '这是一个描述',
    params: {
      paths: ['/log/abc'],
      conditions: {
        type: 'separator',
        match_type: 'include',
        match_content: 'delete',
        separator: '|',
        separator_filters: [
          {
            fieldindex: 2,
            word: '32',
            op: '=',
            logic_op: 'or',
          },
          {
            fieldindex: 2,
            word: '32',
            op: '=',
            logic_op: 'and',
          },
          {
            fieldindex: 2,
            word: '32',
            op: '=',
            logic_op: 'and',
          },
        ],
      },
    },
    storage_cluster_id: 'default',
    storage_expires: 1,
    created_at: '创建时间',
    created_by: '创建人',
    updated_at: '更新时间',
    updated_by: '更新人',
    subscription_info: {
      collector_id: 1,
      subscription_id: 1,
      status: 'FAILED',
      status_name: '部分失败',
      total: 11,
      success: 11,
      failed: 0,
      pending: 0,
    },
  },
  result: true,
};

const retryList = {
  message: '',
  code: 0,
  data: {
    task_id: 23768,
  },
  result: true,
};

const dataList = {
  message: '',
  code: 0,
  data: [
    {
      _bizid_: 0,
      _cloudid_: 0,
      _dstdataid_: 2012,
      _errorcode_: 0,
      _gseindex_: 2069,
      _path_: '/tmp/bkc.log',
      _private_: {},
      _server_: '',
      _srcdataid_: 2012,
      _time_: '2019-08-07 10:15:03',
      _type_: 0,
      _utctime_: '2019-08-07 02:15:03',
      _value_: [
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
      ],
      _worldid_: -1,
    },
    {
      _bizid_: 0,
      _cloudid_: 0,
      _dstdataid_: 2012,
      _errorcode_: 0,
      _gseindex_: 2069,
      _path_: '/tmp/bkc.log',
      _private_: {},
      _server_: '127.0.0.1',
      _srcdataid_: 2012,
      _time_: '2019-08-07 10:15:03',
      _type_: 0,
      _utctime_: '2019-08-07 02:15:03',
      _value_: [
        '[127.0.0.1]20190807-101502 INFO|38|ok-_watch-watch_tsdbproxy-main tsdbproxy is running',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
        '[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch',
      ],
      _worldid_: -1,
    },
  ],
  result: true,
};

export default {
  detailsList,
  collectList,
  retryList,
  dataList,
};
