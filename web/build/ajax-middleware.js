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
 * @file ajax handler for dev
 * @author  <>
 */

import path from 'path';
import fs from 'fs';
import url from 'url';
import queryString from 'querystring';
import chalk from 'chalk';

const requestHandler = (req) => {
  const pathName = req.path || '';

  const mockFilePath = `${path.join(__dirname, '../mock/ajax', pathName)}.js`;
  if (!fs.existsSync(mockFilePath)) {
    return false;
  }

  console.log(chalk.magenta('Ajax Request Path: ', pathName));

  delete require.cache[require.resolve(mockFilePath)];
  const mockDataHandler = require(mockFilePath);
  return mockDataHandler;
};

export default async function ajaxMiddleWare(req, res, next) {
  let query = url.parse(req.url).query;

  if (!query) {
    return next();
  }

  query = queryString.parse(query);

  if (!query.isAjax) {
    return next();
  }

  const postData = req.body || '';
  const mockDataHandler = requestHandler(req);
  let data = await mockDataHandler.response(query, postData, req);

  if (data.statusCode) {
    res.status(data.statusCode).end();
    return;
  }

  let contentType = req.headers['Content-Type'];

  // 返回值未指定内容类型，默认按 JSON 格式处理返回
  if (!contentType) {
    contentType = 'application/json;charset=UTF-8';
    req.headers['Content-Type'] = contentType;
    res.setHeader('Content-Type', contentType);
    data = JSON.stringify(data || {});
  }

  res.end(data);

  return next();
}
