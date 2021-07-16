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
 * @file postcss 基本配置
 * @author <>
 */

const createResolver = require('postcss-import-webpack-resolver');
const baseConf = require('./build/webpack.base.conf.js');

// https://github.com/michael-ciniawsky/postcss-load-config
module.exports = {
  plugins: {
    // 把 import 的内容转换为 inline
    // @see https://github.com/postcss/postcss-import#postcss-import
    'postcss-import': {
      // 使用 webpack 配置里的 resolve.alias
      // https://github.com/krambuhl/postcss-import-webpack-resolver#postcss-import-webpack-resolver
      resolve: createResolver({
        alias: baseConf.default.resolve.alias,
        modules: ['src', 'node_modules'],
      }),
    },

    // mixins，本插件需要放在 postcss-simple-vars 和 postcss-nested 插件前面
    // @see https://github.com/postcss/postcss-mixins#postcss-mixins-
    'postcss-mixins': {},

    // 用于在 URL ( )上重新定位、内嵌或复制。
    // @see https://github.com/postcss/postcss-url#postcss-url
    'postcss-url': {
      url: 'rebase',
    },

    // cssnext 已经不再维护，推荐使用 postcss-preset-env
    'postcss-preset-env': {
      // see https://github.com/csstools/postcss-preset-env#options
      stage: 0,
      autoprefixer: {
        grid: true,
      },
    },
    // 这个插件可以在写 nested 样式时省略开头的 &
    // @see https://github.com/postcss/postcss-nested#postcss-nested-
    'postcss-nested': {},

    // 将 @at-root 里的规则放入到根节点
    // @see https://github.com/OEvgeny/postcss-atroot#postcss-at-root-
    'postcss-atroot': {},

    // 提供 @extend 语法
    // @see https://github.com/jonathantneal/postcss-extend-rule#postcss-extend-rule-
    'postcss-extend-rule': {},

    // 变量相关
    // @see https://github.com/jonathantneal/postcss-advanced-variables#postcss-advanced-variables-
    'postcss-advanced-variables': {
      // variables 属性内的变量为全局变量
    },

    // 类似于 stylus，直接引用属性而不需要变量定义
    // @see https://github.com/simonsmith/postcss-property-lookup#postcss-property-lookup-
    'postcss-property-lookup': {},
  },
};
