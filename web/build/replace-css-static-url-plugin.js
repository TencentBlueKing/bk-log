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
 * @file 替换 asset css 中的 BK_STATIC_URL，__webpack_public_path__ 没法解决 asset 里静态资源的 url
 * @author <>
 */

import { extname } from 'path';

export default class ReplaceCSSStaticUrlPlugin {
  // eslint-disable-next-line no-unused-vars
  apply(compiler, callback) {
    // emit: 在生成资源并输出到目录之前
    compiler.hooks.emit.tapAsync('ReplaceCSSStaticUrlPlugin', (compilation, callback) => {
      const assets = Object.keys(compilation.assets);
      const assetsLen = assets.length;
      for (let i = 0; i < assetsLen; i++) {
        const fileName = assets[i];
        if (extname(fileName) !== '.css') {
          continue;
        }

        const asset = compilation.assets[fileName];

        const minifyFileContent = asset.source().toString()
          .replace(
            /\{\{\s*BK_STATIC_URL\s*\}\}/g,
            () => '../',
          );
        // 设置输出资源
        compilation.assets[fileName] = {
          // 返回文件内容
          source: () => minifyFileContent,
          // 返回文件大小
          size: () => Buffer.byteLength(minifyFileContent, 'utf8'),
        };
      }

      callback();
    });
  }
}
