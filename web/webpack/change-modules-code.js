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

const { resolve } = require('path');
const { readFile, access, writeFile } = require('fs/promises');
const { constants } = require('fs');

class ChangeCode {
  /**
   * @description: 修改echarts
   * @param {*}
   * @return {*}
   */
  static async changeEchartsCode() {
    const codeUrl = resolve(process.cwd(), 'src/monitor-ui/node_modules/echarts/lib/layout/barGrid.js');
    const exists = await access(codeUrl, constants.R_OK | constants.W_OK)
      .then(() => true)
      .catch(() => false);
    if (!exists) return;
    let chunk = await readFile(codeUrl, 'utf-8');
    chunk = chunk
      .replace(
        'height = (height <= 0 ? -1 : 1) * barMinHeight;',
        'height = height ? (height < 0 ? -1 : 1) * barMinHeight : 0;',
      )
      .replace(
        'width = (width < 0 ? -1 : 1) * barMinHeight;',
        'width = width ? (width < 0 ? -1 : 1) * barMinHeight : 0;',
      );
    await writeFile(codeUrl, chunk, 'utf-8').catch((e) => {
      console.error(e.message || 'change echarts code error');
      process.exit(0);
    });
  }
}
ChangeCode.changeEchartsCode();
