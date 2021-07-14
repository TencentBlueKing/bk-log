<!--
  - Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for BK-LOG 蓝鲸日志平台:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div class="validate-user-selector">
    <bk-user-selector
      :value="value"
      style="width: 400px;"
      :class="isError && 'is-error'"
      :api="api"
      :exclude="!allowCreate"
      :placeholder="placeholder"
      @change="handleChange"
      @blur="handleBlur">
    </bk-user-selector>
  </div>
</template>

<script>
import BkUserSelector from '@blueking/user-selector';

export default {
  components: {
    BkUserSelector,
  },
  model: {
    event: 'change',
  },
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    allowCreate: {
      type: Boolean,
      required: true,
    },
    placeholder: {
      type: String,
      default: '',
    },
    api: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isError: false,
    };
  },
  created() {
    this.validateInitValue();
  },
  methods: {
    validateInitValue() {
      if (this.value.length) {
        if (this.allowCreate) {
          // 可以自定义用户情况下有用户就正确
          this.isError = false;
        } else {
          // 有用户存在于人员列表中，才算是通过校验
          // 外部版人员选择器数据源来源接口
          // for (const user of this.value) {
          //     if (this.list.length && this.list.find(item => item.username === user)) {
          //         this.isError = false
          //         return
          //     }
          // }
          // // 虽然有用户，但是用户不存在人员列表中，用户无效
          // this.isError = true
          // this.$emit('change', [])
          this.isError = false;
        }
      } else {
        this.isError = true;
      }
    },
    handleChange(val) {
      const realVal = val.filter(item => item !== undefined);
      this.isError = !realVal.length;
      this.$emit('change', realVal);
    },
    handleBlur() {
      this.isError = !this.value.length;
    },
    pasteFn(val) {
      const users = [...this.value];
      val.split(';').forEach((item) => {
        item = item.trim();
        if (item) {
          if (this.allowCreate) { // tencent 版本
            if (item.match(/^[0-9]*$/) && !users.includes(item)) {
              users.push(item);
            }
          } else { // 内部版
            this.list.forEach((user) => {
              if ((user.displayname === item || user.username === item) && !users.includes(user.username)) {
                users.push(user.username);
              }
            });
          }
        }
      });
      this.$emit('change', users);
      return [];
    },
  },
};
</script>

<style lang="scss" scoped>
  .validate-user-selector /deep/ .is-error .user-selector-container {
    border-color: #ff5656;
  }
</style>
