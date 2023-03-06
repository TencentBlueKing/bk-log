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
  <div class="text-filter-detail">
    <div class="title">
      <span class="bk-icon icon-work-manage"></span>
      <h2 class="text">{{$t('文本过滤')}}</h2>
    </div>
    <div class="content" v-if="data.filter_type === 'match_word'">
      <span>{{$t('关键字过滤')}}：</span>
      <span class="match">{{data.filter_content.keyword}}</span>
    </div>
    <div class="content" v-else-if="data.filter_type === 'match_range'">
      <i18n path="关键字范围: 从匹配{0}开始到匹配{1}之间的所有行">
        <span class="match">{{data.filter_content.start}}</span>
        <span class="match">{{data.filter_content.end}}</span>
      </i18n>
    </div>
    <div class="content" v-else-if="data.filter_type === 'tail_line'">
      <span>{{$t('最新行数')}}：</span>
      <span class="match">{{data.filter_content.line_num}}</span>
    </div>
    <div class="content" v-else-if="data.filter_type === 'line_range'">
      <i18n path="按行过滤: 从第{0}行到第{1}行">
        <span class="match"> {{data.filter_content.start_line}} </span>
        <span class="match"> {{data.filter_content.end_line}} </span>
      </i18n>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
  .text-filter-detail {
    padding: 14px 20px 10px;
    font-size: 15px;
    line-height: 40px;
    color: #63656e;

    .title {
      display: flex;
      align-items: center;

      .bk-icon {
        margin-right: 6px;
        font-size: 14px;
      }

      .text {
        color: #313238;
        margin: 0;
        font-size: 16px;
        font-weight: 500;
        line-height: 20px;
        padding: 10px 0;
      }
    }

    .content {
      border-top: 1px solid #dcdee5;

      .match {
        color: #2dcb56;
      }
    }
  }
</style>
