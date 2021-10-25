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
  <div class="td-log-container">
    <!-- eslint-disable vue/no-v-html -->
    <span
      :class="['field-container', 'add-to', { 'active': hasClickEvent }]"
      @click.stop="handleClickContent"
      v-html="content"
      v-bk-tooltips="{ content: $t('查看调用链'), disabled: !hasClickEvent, delay: 500 }"
    ></span>
    <!--eslint-enable-->
    <template v-if="content !== '--'">
      <span class="icon-search-container" v-bk-tooltips.top="$t('检索')">
        <i class="icon bk-icon icon-search" @click.stop="$emit('iconClick', 'search', content)"></i>
      </span>
      <span class="icon-search-container" v-bk-tooltips.top="$t('复制')">
        <i class="icon log-icon icon-copy" @click.stop="$emit('iconClick','copy', content)"></i>
      </span>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    content: {
      type: [String, Number],
      required: true,
    },
    hasClickEvent: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    handleClickContent() {
      if (this.hasClickEvent) this.$emit('contentClick');
    },
  },
};
</script>

<style lang="scss" scoped>
  .td-log-container {
    position: relative;
    padding: 10px 15px 10px 0;
    white-space: pre-line;
    line-height: 14px;

    .field-container {
      white-space: pre-wrap;
      tab-size: 3;
      &.active:hover {
        color: #3a84ff;
        cursor: pointer;
      }
    }

    .icon-search-container {
      display: none;
      justify-content: center;
      align-items: center;
      vertical-align: bottom;
      width: 14px;
      height: 14px;
      margin-left: 5px;
      cursor: pointer;
      background: #3a84ff;

      .icon {
        font-size: 12px;
        font-weight: bold;
        color: #fff;
        background: #3a84ff;
        transform: scale(.6);

        &.icon-copy {
          font-size: 14px;
          transform: scale(1);
        }
      }
    }

    &:hover {
      .icon-search-container {
        display: inline-flex;
      }
    }
  }
</style>
