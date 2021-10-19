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
  <bk-popover class="bk-select-dropdown"
              ref="selectDropdown"
              trigger="click"
              placement="bottom-start"
              theme="light bk-select-dropdown"
              animation="slide-toggle"
              :offset="-1"
              :distance="16">
    <slot name="trigger">
      <bk-input
        style="width: 669px;"
        data-test-id="addNewExtraction_input_specifyFolder"
        :class="isError && 'is-error'"
        v-model="showValue"
        @change="handleChange">
      </bk-input>
    </slot>
    <div slot="content" class="bk-select-dropdown-content" style="width: 671px;height: 224px;">
      <div class="bk-select-search-wrapper" style="height: 32px;">
        <i class="left-icon bk-icon icon-search"></i>
        <input class="bk-select-search-input" type="text" :placeholder="$t('输入关键字搜索')" v-model="searchValue">
      </div>
      <div class="bk-options-wrapper" style="max-height: 190px;">
        <ul class="bk-options bk-options-single" style="max-height: 190px;">
          <li class="bk-option" v-for="option in filesSearchedPath" :key="option" @click="handleSelectOption(option)">
            <div class="bk-option-content">{{option}}</div>
          </li>
        </ul>
      </div>
      <div class="bk-select-empty" v-if="!filesSearchedPath.length">{{$t('暂无选项')}}</div>
    </div>
  </bk-popover>
</template>

<script>
export default {
  model: {
    event: 'change',
  },
  props: {
    value: {
      type: String,
      required: true,
    },
    availablePaths: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isError: false,
      showValue: '',
      searchValue: '',
    };
  },
  computed: {
    filesSearchedPath() {
      return this.availablePaths.filter(item => item.toLowerCase().includes(this.searchValue.toLowerCase()));
    },
  },
  watch: {
    availablePaths() {
      this.showValue && this.handleChange(this.showValue);
    },
    value(val) {
      this.showValue = val;
    },
  },
  methods: {
    handleChange(val) {
      if (this.validate(val)) {
        this.$emit('change', val);
      } else {
        this.$emit('change', '');
      }
    },
    handleSelectOption(val) {
      this.validate(val);
      this.showValue = val;
      this.$emit('change', val);
      this.$emit('update:select', val);
      this.$refs.selectDropdown.hideHandler();
    },
    validate(val) {
      let isAvailable = false;
      for (const path of this.availablePaths) {
        if (val.startsWith(path)) {
          isAvailable = true;
          break;
        }
      }
      const isValidated = isAvailable && !/\.\//.test(val);
      this.isError = !isValidated;
      return isValidated;
    },
  },
};
</script>
