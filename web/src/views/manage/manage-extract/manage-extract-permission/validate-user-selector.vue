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
      :placeholder="placeholder"
      :disabled="disabled"
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
    placeholder: {
      type: String,
      default: '',
    },
    api: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      type: false,
    },
  },
  data() {
    return {
      isError: false,
    };
  },
  methods: {
    validateInitValue() {
      if (this.value.length) {
        this.isError = false;
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
          this.list.forEach((user) => {
            if ((user.displayname === item || user.username === item) && !users.includes(user.username)) {
              users.push(user.username);
            }
          });
        }
      });
      this.$emit('change', users);
      return [];
    },
  },
};
</script>

<style lang="scss" scoped>
  .validate-user-selector :deep(.is-error .user-selector-container) {
    border-color: #ff5656;
  }
</style>
