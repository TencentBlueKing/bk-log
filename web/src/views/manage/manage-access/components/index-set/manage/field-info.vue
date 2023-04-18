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
  <div class="field-info-container">
    <bk-table v-bkloading="{ isLoading: tableLoading }" :data="fieldsData">
      <bk-table-column :label="$t('字段名')" prop="field_name"></bk-table-column>
      <bk-table-column :label="$t('别名')">
        <template slot-scope="{ row }">
          {{ row.field_alias || '--' }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('数据类型')" prop="field_type"></bk-table-column>
      <bk-table-column :label="$t('分词')" width="80">
        <template slot-scope="{ row }">
          <bk-checkbox disabled :value="row.is_analyzed"></bk-checkbox>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('时间')" width="80">
        <template slot-scope="{ row }">
          <span
            v-if="row.field_name === timeField"
            class="log-icon icon-date-picker"
            style="font-size: 16px;color: #979ba5;">
          </span>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
export default {
  props: {
    indexSetData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tableLoading: true,
      timeField: '',
      fieldsData: [],
    };
  },
  created() {
    this.fetchFields();
  },
  methods: {
    async fetchFields() {
      try {
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: {
            index_set_id: this.indexSetData.index_set_id,
          },
        });
        this.timeField = res.data.time_field;
        this.fieldsData = res.data.fields;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
  },
};
</script>
