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
  <bk-table
    class="skeleton-table"
    :data="renderList"
    :show-header="false"
    :outer-border="false"
    v-if="columnField.length">
    <bk-table-column width="30"></bk-table-column>
    <template v-for="(field, index) in columnField">
      <bk-table-column
        :min-width="(!isLoading || isOriginalField) ? field.minWidth : 0"
        :width="(!isLoading || isOriginalField) ? field.width : 'auto'"
        :key="index">
        <!-- eslint-disable-next-line vue/no-unused-vars -->
        <template slot-scope="props">
          <div class="cell-bar" :style="`width:${getRandom()}%`"></div>
        </template>
      </bk-table-column>
    </template>
    <bk-table-column v-if="!isLoading" width="84"></bk-table-column>
  </bk-table>
</template>

<script>
export default {
  props: {
    visibleFields: {
      type: Array,
      required: true,
    },
    // 用于初次loading
    isLoading: {
      type: Boolean,
      default: false,
    },
    // 是否原始日志
    isOriginalField: {
      type: Boolean,
      default: false,
    },
    isPageOver: {
      type: Boolean,
      required: false,
    },
  },
  data() {
    return {
      throttle: false, // 滚动节流
      loaderLen: 12, // 骨架行数
    };
  },
  computed: {
    renderList() {
      return new Array(this.loaderLen).fill('');
    },
    columnField() {
      return this.isOriginalField ? [
        { width: 160, minWidth: 0, field_name: 'time' },
        { width: '', minWidth: 0, field_name: 'log' },
      ] : this.visibleFields;
    },
  },
  created() {
    if (this.isLoading) this.loaderLen = 12;
    const ele = document.querySelector('.result-scroll-container');
    if (ele) ele.addEventListener('scroll', this.handleScroll);
  },
  beforeDestroy() {
    const ele = document.querySelector('.result-scroll-container');
    if (ele) ele.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    getRandom() { // 骨架占位随机长度
      return Math.floor(Math.random() * (20 - 100) + 100);
    },
    handleScroll() {
      if (this.throttle || this.isLoading) {
        return;
      }

      const el = document.querySelector('.result-scroll-container');
      if (el.scrollHeight - el.offsetHeight - el.scrollTop < 100) {
        this.throttle = true;
        setTimeout(() => {
          this.loaderLen = this.loaderLen + 24;
          el.scrollTop = el.scrollTop - 100;
          this.throttle = false;
        }, 100);
      }
    },
  },
};
</script>

<style lang="scss">
  .skeleton-table {
    &:before {
      z-index: -1;
    }

    .cell {
      padding-top: 14px;
      width: 100%;
    }

    .cell-bar {
      position: relative;
      height: 12px;
      background-color: #e9e9e9;
    }

    :deep(.bk-table-empty-text) {
      padding: 0;
      width: 100%;
    }
  }
</style>
