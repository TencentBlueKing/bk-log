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

export default {
  data () {
    return {
      _initDataStr_: ''// 初始化状态
    };
  },
  methods: {
    /**
     * 侧边栏离开，二次确认
     * @returns {Boolean} 是否编辑过
     */
    $isSidebarClosed (targetData: object): Promise<boolean> {
      const isEqual = this._initDataStr_ === JSON.stringify(targetData);
      return new Promise((resolve, reject) => {
        if (isEqual) { // 未编辑
          resolve(true);
        } else {// 已编辑
          this.$bkInfo({
            extCls: 'sideslider-close-cls',
            title: this.$t('确认离开当前页？'),
            subTitle: this.$t('离开将会导致未保存信息丢失'),
            okText: this.$t('离开'),
            confirmFn () {
              resolve(true);
            },
            cancelFn () {
              resolve(false);
            }
          });
        }
      });
    },
    initSidebarFormData (data: object): void {
      this._initDataStr_ = JSON.stringify(data);
    }
  }
};
