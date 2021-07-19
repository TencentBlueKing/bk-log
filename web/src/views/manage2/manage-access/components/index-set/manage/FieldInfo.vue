<template>
  <div class="field-info-container">
    <bk-table v-bkloading="{ isLoading: tableLoading }" :data="fieldsData">
      <bk-table-column :label="$t('字段名')" prop="field_name"></bk-table-column>
      <bk-table-column :label="$t('中文名')">
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
