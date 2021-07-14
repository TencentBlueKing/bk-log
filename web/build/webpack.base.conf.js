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
 * @file webpack base conf
 * @author v_adongtang <v_adongtang@tentcent.com>
 */

import webpack from 'webpack';
import { VueLoaderPlugin } from 'vue-loader';
import friendlyFormatter from 'eslint-friendly-formatter';

import { resolve, assetsPath } from './util';
import config from './config';

const isProd = process.env.NODE_ENV === 'production';

export default {
  output: {
    path: isProd ? config.build.assetsRoot : config.dev.assetsRoot,
    filename: '[name].js',
    publicPath: isProd ? config.build.assetsPublicPath : config.dev.assetsPublicPath,
  },

  resolve: {
    // 指定以下目录寻找第三方模块，避免 webpack 往父级目录递归搜索，
    // 默认值为 ['node_modules']，会依次查找./node_modules、../node_modules、../../node_modules
    modules: [resolve('src'), resolve('node_modules')],
    extensions: ['.ts', '.js', '.vue', '.json'],
    alias: {
      vue$: 'vue/dist/vue.esm.js',
      '@': resolve('src'),
    },
  },

  module: {
    noParse: [
      /\/node_modules\/jquery\/dist\/jquery\.min\.js$/,
      /\/node_modules\/echarts\/dist\/echarts\.min\.js$/,
    ],
    rules: [
      {
        test: /\.(js|vue)$/,
        loader: 'eslint-loader',
        enforce: 'pre',
        include: [resolve('src'), resolve('test'), resolve('static')],
        exclude: /node_modules/,
        options: {
          formatter: friendlyFormatter,
        },
      },
      {
        test: /\.vue$/,
        use: {
          loader: 'vue-loader',
          options: {
            transformAssetUrls: {
              video: 'src',
              source: 'src',
              img: 'src',
              image: 'xlink:href',
            },
          },
        },
      },
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
        }, {
          loader: 'ts-loader',
          options: {
            transpileOnly: true,
            appendTsSuffixTo: ['\\.vue$'],
            happyPackMode: false,
          },
        }],
      },
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            include: [resolve('src')],
            cacheDirectory: './webpack_cache/',
            // 确保 JS 的转译应用到 node_modules 的 Vue 单文件组件
            exclude: file => (
              /node_modules/.test(file) && !/\.vue\.js/.test(file)
            ),
          },
        },
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: assetsPath('images/[name].[hash:7].[ext]'),
        },
      },
      {
        test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: assetsPath('media/[name].[hash:7].[ext]'),
          },
        },
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: assetsPath('fonts/[name].[hash:7].[ext]'),
          },
        },
      },
    ],
  },

  plugins: [
    new VueLoaderPlugin(),
    // moment 优化，只提取本地包
    new webpack.ContextReplacementPlugin(/moment\/locale$/, /zh-cn/),
  ],
};
