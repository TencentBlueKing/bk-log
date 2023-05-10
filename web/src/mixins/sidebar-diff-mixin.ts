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

import { deepClone, deepEqual } from '../common/util';

export default {
  data () {
    return {
      _initCloneData_: null,// 初始化时的formData
      _isChange_: false,
      _isDataInit_: false,
    };
  },
  computed: {
    // 监听的formData对象 如果有多个监听则不使用mixin的默认值 自行在组件内设置计算属性
    _watchFormData_({ formData }) {
      return { formData };
    }
  },
  watch: {
    _watchFormData_: {
      deep: true,
      handler(newVal: object) {
        // 已经修改过 或 未初始化formData的值时不对比
        if (this._isChange_ || !this._isDataInit_) return;
        // 对比是否进行过修改
        if (!deepEqual(newVal, this._initCloneData_)) this._isChange_ = true;
      }
    },
  },
  methods: {
    /**
     * 侧边栏离开，二次确认
     * @returns {Boolean} 是否编辑过
     */
    $isSidebarClosed(): Promise<boolean> {
      const _this = this;
      return new Promise((resolve, reject) => {
        if (this._isChange_) { // 已编辑
          this.$bkInfo({
            extCls: 'sideslider-close-cls',
            title: this.$t('确认离开当前页？'),
            subTitle: this.$t('离开将会导致未保存信息丢失'),
            okText: this.$t('离开'),
            confirmFn () {
              resolve(true);
              _this._isChange_ = false;
              _this._isDataInit_ = false;
            },
            cancelFn () {
              resolve(false);
            }
          });
        } else { // 未编辑
          resolve(true);
          _this._isChange_ = false;
          _this._isDataInit_ = false;
        }
      });
    },
    /**
     * @desc: 初始化对比时的formData值
     */
    initSidebarFormData(): void {
      // 从计算属性中获取所需要对比的key列表
      this._initCloneData_ = Object.keys(this._watchFormData_).reduce((pre:object, cur:string)=> {
        pre[cur] = deepClone(this[cur]);
        return pre;
      }, {});
      this._isDataInit_ = true;
    },
        /**
     * @desc: 是否改变过侧边弹窗的数据
     * @returns {Boolean} true为没改 false为改了 触发二次弹窗
     */
    async handleCloseSidebar(): Promise<boolean> {
      return await this.$isSidebarClosed();
    },
  }
};
