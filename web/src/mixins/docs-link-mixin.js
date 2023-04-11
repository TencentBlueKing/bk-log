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

const linkMap = {
  logExtract: '产品白皮书/integrations-logs/log_simple_format.md', // 日志清洗
  docCenter: '产品白皮书/intro/README.md', // 文档中心
  logArchive: '产品白皮书/tools/log_archive.md', // 日志归档
  logCollection: '产品白皮书/integrations-logs/logs_overview.md', // 日志采集接入
  bkBase: '基础计算平台/产品白皮书/intro/intro.md', // 基础计算平台
  queryString: '产品白皮书/data-visualization/query_string.md', // 查询语句语法
};

export default {
  methods: {
    handleGotoLink(id) {
      const link = linkMap[id];
      if (link) {
        console.log(link);
        this.$http.request('docs/getDocLink', {
          query: {
            md_path: link,
          },
        }).then((res) => {
          window.open(res.data, '_blank');
        })
          .catch(() => false);
      }
    },
  },
};
