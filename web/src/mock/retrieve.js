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

// function returnList(data, num) {
//   const arr = [];
//   for (let i = 0; i < num; i++) {
//     arr.push(Object.assign(JSON.parse(JSON.stringify(data)), { gseIndex: 152300 + i }));
//   }
//   return arr;
// }
// let logNum = 152300;
// function returnRealTimeLog(data) {
//   logNum = logNum - Math.ceil(Math.random() * 25);
//   const arr = [];
//   for (let i = 0; i < 50; i++) {
//     arr.push(Object.assign(
//       JSON.parse(JSON.stringify(data)),
//       { gseIndex: logNum, log: `is_cluster</em>-COMMON: ok${logNum}` },
//     ));
//     logNum = logNum + 1;
//   }
//   return arr;
// }
const getIndexSetList = {};
const getLogTableHead = {};
const getLogTableList = {};

const getFilterBiz = {};
const getIpTree = {};
const getOperators = {};
const getCloudAreaList = {};
const downloadLog = {};
const getRealTimeLog = {};
const getContentLog = {};

export default {
  getIndexSetList,
  getLogTableHead,
  getLogTableList,
  getFilterBiz,
  getIpTree,
  getOperators,
  getCloudAreaList,
  downloadLog,
  getRealTimeLog,
  getContentLog,
};
