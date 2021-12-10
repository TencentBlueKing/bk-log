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
  <div class="favorite-popper-content" :style="popperStyle" v-bkloading="{ isLoading }">
    <div class="title">{{ $t('收藏描述：') }}</div>
    <div class="content">
      <bk-input v-model.trim="value" maxlength="50"></bk-input>
      <div class="icon-container" @click="add">
        <span class="bk-icon icon-check-line"></span>
      </div>
      <div class="icon-container" @click="$emit('close')">
        <span class="bk-icon icon-close-line-2"></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isLoading: {
      type: Boolean,
      required: true,
    },
    panelWidth: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      value: '',
    };
  },
  computed: {
    popperStyle() {
      return {
        width: `${this.panelWidth - 37}px`,
      };
    },
  },
  methods: {
    add() {
      if (this.value) {
        this.$emit('add', this.value);
      } else {
        this.messageWarn(this.$t('请输入内容'));
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .favorite-popper-content {
    width: 363px;
    padding: 9px 2px;

    .title {
      margin-bottom: 7px;
      font-size: 12px;
      line-height: 20px;
      color: #63656e;
    }

    .content {
      display: flex;
      align-items: center;

      .icon-container {
        flex-shrink: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        margin-left: 4px;
        border: 1px solid #c4c6cc;
        cursor: pointer;
        transition: border-color .3s;

        &:hover {
          border-color: #3a84ff;
          transition: border-color .3s;
        }

        .bk-icon {
          font-size: 20px;
          font-weight: bold;

          &.icon-check-line {
            color: #2dcb56;
          }

          &.icon-close-line-2 {
            color: #ea3636;
          }
        }
      }
    }
  }
</style>
