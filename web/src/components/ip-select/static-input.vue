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
  <div class="static-input">
    <bk-input
      class="static-input-text"
      :ext-cls="inputError ? 'input-error' : ''"
      :placeholder="$t('retrieve.Please_enter')"
      v-model="text"
      @focus="handleFocus"
      @keydown.native="handleInputKeydown"
      @change="handleSearch"
      :type="'textarea'"
      :rows="10">
    </bk-input>
    <p v-if="inputError" class="input-error-text">
      {{$t('retrieve.IPFormatErrorText')}}
    </p>
    <slot></slot>
    <div class="static-input-btn" @click="handleChecked">
      {{$t('retrieve.Add_list')}}
    </div>
  </div>
</template>
<script>
import { debounce } from 'throttle-debounce';

export default {
  name: 'static-input',
  props: {
    defaultText: String,
  },
  data() {
    return {
      ipMatch: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])(\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])){3}$/,
      text: '',
      handleSearch() {

      },
      inputError: false,
    };
  },
  watch: {
    defaultText: {
      handler(v) {
        this.text = (`${v}`).trim().replace(/(\r|\n){2,}/gm, '\n');
      },
      immediate: true,
    },
  },
  created() {
    this.handleSearch = debounce(300, this.handleKeywordChange);
  },
  methods: {
    handleFocus() {
      this.inputError = false;
    },
    handleInputKeydown(e) {
      if (e.key === 'enter') {
        return true;
      }
      if (e.ctrlKey || e.shilftKey || e.metaKey) {
        return true;
      }
      // eslint-disable-next-line no-useless-escape
      if (!e.key.match(/[0-9\.\s\|\,\;]/) && !e.key.match(/(backspace|enter|ctrl|shift|tab)/mi)) {
        e.preventDefault();
      }
    },
    handleChecked() {
      if (this.text && this.text.length) {
        const ipList = this.text.split(/[\r\n]+/gm);
        const errList = new Set();
        const goodList = new Set();
        ipList.forEach((ip) => {
          ip = ip.trim();
          if (ip.match(this.ipMatch)) {
            goodList.add(ip);
          } else {
            ip.length > 0 && errList.add(ip);
          }
        });
        if (errList.size > 0) {
          this.text = Array.from(errList).join('\n');
          this.inputError = true;
          return;
        }
        if (goodList.size > 0 || errList.size > 0) {
          // this.$emit('checked', 'static-ip', Array.from(goodList).join('\n'), this.text)
          this.$emit('checked', 'static-ip', { goodList: Array.from(goodList), errList: Array.from(errList) }, this.text);
        }
      }
    },
    handleKeywordChange(v) {
      this.$emit('change-input', v);
    },
  },
};
</script>
<style lang="scss" scoped>
  .static-input {
    &-text {
      margin: 10px 0;
    }

    &-btn {
      width: 200px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #3a84ff;
      border-radius: 2px;
      color: #3a84ff;
      cursor: pointer;

      &:hover {
        background: #3a84ff;
        color: #fff;
      }
    }

    .input-error-text {
      color: #ff5656;
      margin: -10px 0 10px;
    }
  }
</style>

<style lang="scss">
  .input-error .bk-textarea-wrapper {
    border-color: #ff5656;
  }
</style>
