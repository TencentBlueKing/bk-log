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
  <div class="retrieve-input" v-bk-clickoutside="hiddenHistory">
    <bk-input
      class="king-input-retrieve"
      :value="value"
      type="text"
      @change="handleChange"
      @focus="handleFocus"
      @enter="handleEnter"
      data-test-id="frontPageSearch_input_phrasesSearch"
    ></bk-input>
    <!-- 首页搜索ICON -->
    <span
      v-cursor="{ active: isSearchAllowed === false }"
      class="bk-icon icon-search"
      @click="handleEnter"
    ></span>
    <!-- 历史搜索记录 -->
    <ul
      class="retrieve-history"
      v-show="showHistory && historyList.length"
      @click.stop>
      <li v-for="item in historyList" :key="item.id">
        <span
          v-bk-overflow-tips="{ placement: 'right' }"
          class="text text-overflow-hidden"
          @click="retrieveHistory(item)">
          {{ item.query_string.slice(8) }}
        </span>
      </li>
    </ul>
  </div>
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
    showHistory: {
      type: Boolean,
      required: true,
    },
    historyList: {
      type: Array,
      required: true,
    },
    isSearchAllowed: {
      type: Boolean,
      default: null,
    },
  },
  methods: {
    hiddenHistory() {
      this.$emit('update:showHistory', false);
    },
    handleChange(val) {
      this.$emit('change', val);
    },
    handleFocus() {
      this.$emit('focus');
    },
    handleEnter() {
      this.$emit('retrieve');
    },
    retrieveHistory(item) {
      this.$emit('retrieve', item.params);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .retrieve-input {
    position: relative;
    margin-top: 18px;

    .king-input-retrieve {
      :deep(.bk-form-input) {
        height: 48px;
        border-color: #fff;
      }
    }

    .icon-search {
      position: absolute;
      top: 14px;
      right: 14px;
      z-index: 1;
      color: #979ba5;
      cursor: pointer;
      font-size: 20px;

      &:hover {
        color: #3a84ff;
      }
    }

    .retrieve-history {
      position: absolute;
      z-index: 1;
      width: 100%;
      max-height: 268px;
      overflow: auto;
      margin-top: 4px;
      padding: 6px 0;
      background: #fff;
      box-shadow: 0 2px 6px 0 rgba(0, 0, 0, .1);
      border-radius: 2px;
      border: 1px solid #dcdee5;

      @include scroller(#CCC);

      li {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 10px;
        font-size: 12px;
        line-height: 32px;
        color: #63656e;
        transition: color, background .2s;

        .text {
          flex-grow: 1;
        }

        &:hover {
          cursor: pointer;
          color: #3a84ff;
          background: #eaf3ff;
          transition: color, background .2s;
        }
      }
    }
  }
</style>
