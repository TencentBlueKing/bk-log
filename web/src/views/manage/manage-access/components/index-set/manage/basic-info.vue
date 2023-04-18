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
        <div class="description-row">
          <dt class="description-term">{{ $t('索引集名称') }}</dt>
          <dd class="description-definition">{{ indexSetData.index_set_name || '--' }}</dd>
          <dt class="description-term">{{ $t('所属集群') }}</dt>
          <dd class="description-definition">{{ indexSetData.storage_cluster_name || '--' }}</dd>
        </div>
        <div class="description-row">
          <dt class="description-term">{{ $t('数据分类') }}</dt>
          <dd class="description-definition">{{ categoryMap[indexSetData.category_id] || '--' }}</dd>
          <dt class="description-term">{{ $t('创建人') }}</dt>
          <dd class="description-definition">{{ indexSetData.created_by || '--' }}</dd>
        </div>
        <div class="description-row">
          <dt class="description-term">{{ $t('数据源') }}</dt>
          <dd class="description-definition">{{ scenarioMap[indexSetData.scenario_id] || '--' }}</dd>
          <dt class="description-term">{{ $t('创建时间') }}</dt>
          <dd class="description-definition">{{ indexSetData.created_at.slice(0, 19) || '--' }}</dd>
        </div>
      </dl>
    </section>
    <section class="partial-content" style="margin-bottom: 20px;">
      <div class="main-title">
        {{ $t('采集项') }}
      </div>
      <bk-table
        v-bkloading="{ isLoading: tableLoading1 }"
        auto-scroll-to-top
        :data="pagedIndexesList"
        :max-height="526"
        :pagination="indexesPagination"
        @page-change="handleIndexesPageChange"
        @page-limit-change="handleIndexesLimitChange">
        <bk-table-column :label="$t('索引')" prop="result_table_id"></bk-table-column>
        <bk-table-column :label="$t('状态')">
          <template slot-scope="{ row }">
            <div :class="['status-text', row.stat.health]">
              {{ healthMap[row.stat.health] }}
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('主分片')">
          <template slot-scope="{ row }">
            {{ row.stat.pri }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('副本分片')">
          <template slot-scope="{ row }">
            {{ row.stat.rep }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('文档计数')">
          <template slot-scope="{ row }">
            {{ row.stat['docs.count'] }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('存储大小')">
          <template slot-scope="{ row }">
            {{ getFileSize(row.stat['store.size']) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="150">
          <template slot-scope="{ row }">
            <bk-button
              theme="primary"
              text
              :disabled="pagedIndexesList.length === 1"
              @click="removeIndex(row)">
              {{ $t('删除') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </section>
    <section class="partial-content">
      <div class="main-title">
        {{ $t('操作记录') }}
      </div>
      <bk-table
        v-bkloading="{ isLoading: tableLoading2 }"
        class="king-table"
        auto-scroll-to-top
        :data="recordsData"
        :max-height="526"
        :pagination="recordsPagination"
        @page-change="handleRecordsPageChange"
        @page-limit-change="handleRecordsLimitChange">
        <bk-table-column :label="$t('操作日期')" width="200">
          <template slot-scope="{ row }">
            {{ row.created_at.slice(0, 19) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作内容')" prop="content"></bk-table-column>
        <bk-table-column :label="$t('操作人')" prop="created_by" width="160"></bk-table-column>
        <bk-table-column :label="$t('操作结果')" width="140">
          <template slot-scope="{ row }">
            <div :class="['status-text', row.result && 'success-status']">
              {{ row.result ? $t('成功') : $t('失败') }}
            </div>
          </template>
        </bk-table-column>
      </bk-table>
    </section>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { formatFileSize } from '@/common/util';

export default {
  props: {
    indexSetData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tableLoading1: true, // 采集项
      indexesData: [],
      // 健康状态，文案待定，先不国际化
      healthMap: {
        green: this.$t('健康'),
        yellow: this.$t('部分故障'),
        red: this.$t('严重故障'),
      },
      indexesPagination: {
        current: 1,
        limit: 10,
        count: 0,
      },
      tableLoading2: true, // 操作记录
      recordsData: [],
      recordsPagination: {
        current: 1,
        limit: 10,
        count: 0,
      },
    };
  },
  computed: {
    ...mapState(['spaceUid', 'bkBizId']),
    ...mapState('collect', ['scenarioMap']),
    pagedIndexesList() {
      const start = (this.indexesPagination.current - 1) * this.indexesPagination.limit;
      const end = start + this.indexesPagination.limit;
      return this.indexesData.slice(start, end);
    },
    categoryMap() {
      const map = {};
      this.$store.state.globals.globalsData.category.forEach((child) => {
        child.children.forEach((item) => {
          map[item.id] = item.name;
        });
      });
      return map;
    },
  },
  created() {
    this.fetchIndexes();
    this.fetchRecords();
  },
  methods: {
    async fetchIndexes() {
      try {
        // 获取索引列表
        const res = await this.$http.request('indexSet/indexes', {
          params: {
            index_set_id: this.indexSetData.index_set_id,
          },
        });
        this.indexesData = res.data.list;
        this.indexesPagination.count = res.data.total;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading1 = false;
      }
    },
    handleIndexesPageChange(page) {
      this.indexesPagination.current = page;
    },
    handleIndexesLimitChange(limit) {
      this.indexesPagination.limit = limit;
      this.indexesPagination.current = 1;
    },
    // 移除索引（采集项）
    removeIndex(row) {
      this.$bkInfo({
        title: `${this.$t('确认删除索引')}【${row.result_table_id}】`,
        maskClose: true,
        confirmLoading: true,
        width: 600,
        confirmFn: async () => {
          try {
            const scenarioId = this.$route.name.split('-')[0];
            const requestBody = {
              scenario_id: scenarioId,
              index_set_name: this.indexSetData.index_set_name,
              category_id: this.indexSetData.category_id,
              indexes: this.indexSetData.indexes.filter(item => item.result_table_id !== row.result_table_id),
              view_roles: [], // 兼容后端历史遗留代码
              space_uid: this.spaceUid,
            };
            if (this.$route.name.includes('track')) { // 全链路追踪
              requestBody.is_trace_log = true;
            }
            if (this.scenarioId === 'es') {
              Object.assign(requestBody, {
                time_field: this.indexSetData.time_field,
                time_field_type: this.indexSetData.time_field_type,
                time_field_unit: this.indexSetData.time_field_unit,
                storage_cluster_id: this.indexSetData.storage_cluster_id,
              });
            }
            const res = await this.$http.request('/indexSet/update', {
              params: {
                index_set_id: this.$route.params.indexSetId,
              },
              data: requestBody,
            });
            this.indexesData.splice(this.indexesData.findIndex(item => item === row), 1);
            this.indexesPagination.count -= 1;
            this.$store.commit('collect/updateCurIndexSet', res.data);
            this.messageSuccess(this.$t('删除成功'));
          } catch (e) {
            console.warn(e);
          }
        },
      });
    },
    async fetchRecords() {
      try {
        // 获取操作记录数据
        this.tableLoading2 = true;
        const res = await this.$http.request('indexSet/getOperationRecord', {
          query: {
            bk_biz_id: this.bkBizId,
            record_type: 'index_set',
            record_object_id: this.indexSetData.index_set_id,
            page: this.recordsPagination.current,
            pagesize: this.recordsPagination.limit,
          },
        });
        this.recordsData = res.data.list;
        this.recordsPagination.count = res.data.total;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading2 = false;
      }
    },
    handleRecordsPageChange(page) {
      this.recordsPagination.current = page;
      this.fetchRecords();
    },
    handleRecordsLimitChange(limit) {
      this.recordsPagination.limit = limit;
      this.recordsPagination.current = 1;
      this.fetchRecords();
    },
    getFileSize(size) {
      return formatFileSize(size);
    },
  },
};
</script>

<style lang="scss" scoped>
  .description-list {
    font-size: 12px;
    line-height: 16px;

    .description-row {
      display: flex;
      align-items: center;
    }

    .description-term {
      width: 120px;
      height: 40px;
      padding-right: 20px;
      text-align: right;
      color: #63656e;
    }

    .description-definition {
      width: 200px;
      height: 40px;
      color: #313238;
    }
  }

  .king-table {
    :deep(.bk-table-body) {
      .cell {
        padding-top: 8px;
        padding-bottom: 8px;
      }
    }
  }

  .status-text {
    color: #ea3636;

    &.success-status {
      color: #2dcb56;;
    }

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
</style>
