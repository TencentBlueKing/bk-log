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
  <div class="log-slog-content">
    <bk-table height="100%" :border="true" :data="logList">
      <bk-table-column
        v-for="(field, index) in logFields" :key="index"
        :label="field.field_alias || field.field_name"
        :min-width="field.field_name === 'log' ? 300 : 100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{tableRowDeepView(row, field.field_name, field.field_type)}}</span>
        </div>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';

export default {
  mixins: [tableRowDeepViewMixin],
  props: {
    isShowLog: {
      type: Boolean,
      required: true,
    },
    logList: {
      type: Array,
      required: true,
    },
    logFields: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
  .log-slog-content {
    width: 100%;
    height: calc(100vh - 60px);
    padding: 30px;
  }
</style>
