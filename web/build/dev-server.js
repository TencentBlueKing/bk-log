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
 * @file dev server
 * @author <>
 */

import path from 'path';
import express from 'express';
import open from 'open';
import webpack from 'webpack';
import webpackDevMiddleware from 'webpack-dev-middleware';
import webpackHotMiddleware from 'webpack-hot-middleware';
import proxyMiddleware from 'http-proxy-middleware';
import bodyParser from 'body-parser';
// import history from 'connect-history-api-fallback'
import cors from 'cors';

import devConf from './webpack.dev.conf';
import ajaxMiddleware from './ajax-middleware';
import config from './config';
import checkVer from './check-versions';

checkVer();

const port = process.env.PORT || config.dev.localDevPort;

const autoOpenBrowser = !!config.dev.autoOpenBrowser;

const proxyTable = config.dev.proxyTable;

const app = express();
const compiler = webpack(devConf);

const devMiddleware = webpackDevMiddleware(compiler, {
  publicPath: devConf.output.publicPath,
  quiet: true,
});

const hotMiddleware = webpackHotMiddleware(compiler, {
  log: false,
  heartbeat: 2000,
});

Object.keys(proxyTable).forEach((context) => {
  let options = proxyTable[context];
  if (typeof options === 'string') {
    options = {
      target: options,
    };
  }
  app.use(proxyMiddleware(context, options));
});

// app.use(history({
//     verbose: false,
//     rewrites: [
//         {
//             // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
//             // 兼容 /router/10.121.23.12 这样以 IP 结尾的 url
//             from: /(\d+\.)*\d+$/,
//             to: '/'
//         },
//         {
//             // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
//             // 兼容 /router/0.aaa.bbb.ccc.1234567890/ddd/eee
//             from: /\/+.*\..*\//,
//             to: '/'
//         }
//     ]
// }))

const allowedOrigins = [`http://localhost:${port}`, `${config.dev.localDevUrl}:${port}`];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin) {
      return callback(null, true);
    }
    if (allowedOrigins.indexOf(origin) === -1) {
      const msg = 'The CORS policy for this site does not allow access from the specified Origin.';
      return callback(new Error(msg), false);
    }
    return callback(null, true);
  },
  methods: ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'],
  credentials: true,
}));

app.use(devMiddleware);

app.use(hotMiddleware);

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({
  extended: true,
}));

app.use(ajaxMiddleware);

const staticPath = path.posix.join(config.dev.assetsPublicPath, config.dev.assetsSubDirectory);
app.use(staticPath, express.static('./static'));

const url = `${config.dev.localDevUrl}:${port}`;

let _resolve;
const readyPromise = new Promise((resolve) => {
  _resolve = resolve;
});

console.log('> Starting dev server...');
devMiddleware.waitUntilValid(() => {
  console.log(`> Listening at ${url}\n`);
  if (autoOpenBrowser) {
    open(url);
  }
  _resolve();
});

const server = app.listen(port);

export default {
  ready: readyPromise,
  close: () => {
    server.close();
  },
};
