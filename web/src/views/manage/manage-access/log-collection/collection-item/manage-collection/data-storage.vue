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
  <div class="data-storage-container">
    <section class="partial-content">
      <div class="main-title">
        {{ $t('基础信息') }}
      </div>
      <dl class="description-list">
        <dt class="description-term">{{ $t('集群名称') }}</dt>
        <dd class="description-definition">{{ collectorData.storage_cluster_name || '--' }}</dd>
        <dt class="description-term">{{ $t('索引集名称') }}</dt>
        <dd class="description-definition">{{ collectorData.table_id_prefix + collectorData.table_id || '--' }}</dd>
        <dt class="description-term">{{ $t('过期时间') }}</dt>
        <dd class="description-definition">{{ collectorData.retention || '--' }}</dd>
        <dt class="description-term">{{ $t('分裂规则') }}</dt>
        <dd class="description-definition">{{ collectorData.index_split_rule || '--' }}</dd>
      </dl>
    </section>
    <section class="partial-content" style="margin-bottom: 20px;">
      <div class="main-title">
        {{ $t('物理索引') }}
      </div>
      <bk-table v-bkloading="{ isLoading: tableLoading1 }" :data="indexesData">
        <bk-table-column :label="$t('索引')" prop="index" min-width="180"></bk-table-column>
        <bk-table-column :label="$t('状态')" prop="health">
          <template slot-scope="{ row }">
            <div :class="['status-text', row.health]">
              {{ healthMap[row.health] }}
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('主分片')" prop="pri"></bk-table-column>
        <bk-table-column :label="$t('副本分片')" prop="rep"></bk-table-column>
        <bk-table-column :label="$t('文档计数')">
          <template slot-scope="{ row }">
            {{ row['docs.count'] }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('存储大小')">
          <template slot-scope="{ row }">
            {{ getFileSize(row['store.size']) }}
          </template>
        </bk-table-column>
        <div slot="empty">
          <empty-status empty-type="empty" />
        </div>
      </bk-table>
    </section>
    <section class="partial-content">
      <div class="main-title">
        {{ $t('字段信息') }}
      </div>
      <bk-table v-bkloading="{ isLoading: tableLoading2 }" :data="fieldsData">
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
            <span v-if="row.field_name === timeField" class="log-icon icon-date-picker"></span>
          </template>
        </bk-table-column>
        <div slot="empty">
          <empty-status empty-type="empty" />
        </div>
      </bk-table>
    </section>
  </div>
</template>

<script>
import { formatFileSize } from '@/common/util';
import EmptyStatus from '@/components/empty-status';
export default {
  components: {
    EmptyStatus,
  },
  props: {
    collectorData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tableLoading1: true,
      indexesData: [],
      // 健康状态，文案待定，先不国际化
      healthMap: {
        green: this.$t('健康'),
        yellow: this.$t('部分故障'),
        red: this.$t('严重故障'),
      },
      tableLoading2: true,
      timeField: '',
      fieldsData: [],
    };
  },
  created() {
    this.fetchIndexes();
    this.fetchFields();
  },
  methods: {
    getFileSize(size) {
      return formatFileSize(size);
    },
    async fetchIndexes() {
      try {
        const res = await this.$http.request('source/getIndexes', {
          params: {
            collector_config_id: this.collectorData.collector_config_id,
          },
        });
        this.indexesData = res.data;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading1 = false;
      }
    },
    async fetchFields() {
      try {
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: {
            index_set_id: this.collectorData.index_set_id,
          },
        });
        this.timeField = res.data.time_field;
        this.fieldsData = res.data.fields;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading2 = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .description-list {
    display: flex;
    flex-flow: wrap;
    font-size: 12px;
    line-height: 16px;

    .description-term {
      width: 120px;
      height: 40px;
      padding-right: 20px;
      text-align: right;
      color: #979ba5;
    }

    .description-definition {
      width: calc(100% - 200px);
      height: 40px;
      color: #63656e;
    }
  }

  .status-text {
    &.green {
      color: #2dcb56;;
    }

    &.yellow {
      color: #ff9c01;;
    }

    &.red {
      color: #ea3636;;
    }
  }

  .icon-date-picker {
    font-size: 16px;
    color: #979ba5;
  }
</style>
