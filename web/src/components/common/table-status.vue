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
  <div class="table-status-container failed" v-if="isError">
    <i class="bk-icon icon-close-circle-shape icon-fai"></i>
    <span class="text">{{$t('失败')}}</span>
  </div>
  <div class="table-status-container success" v-else>
    <i class="bk-icon icon-check-circle-shape icon-sec"></i>
    <span class="text">{{$t('成功')}}</span>
  </div>
</template>

<script>
export default {
  props: {
    isError: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
  .table-status-container {
    display: flex;
    align-items: center;

    &.success .bk-icon {
      color: #2dcb56;
    }

    &.failed .bk-icon {
      color: #ea3636;
    }

    .text {
      color: #63656e;
      margin-left: 2px;
    }
  }
</style>
