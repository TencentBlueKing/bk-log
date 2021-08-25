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
  <section class="archive-state-list">
    <section>
      <bk-table
        class="state-table"
        :data="dataList"
        v-bkloading="{ isLoading: isTableLoading }"
        :outer-border="false"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('logArchive.indexName')" min-width="300">
          <template slot-scope="props">
            {{ props.row.index_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.startStopTime')" min-width="200">
          <template slot-scope="props">
            {{ `${props.row.start_time} - ${props.row.end_time}` }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.remain')">
          <template slot-scope="props">
            {{ props.row.expired_time }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.size')">
          <template slot-scope="props">
            {{ getFileSize(props.row.store_size) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.archiveStatus')">
          <template slot-scope="props">
            {{ stateMap[props.row.state] }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.isRestore')">
          <template slot-scope="props">
            {{ props.row.is_stored ? $t('common.yes') : $t('common.no') }}
          </template>
        </bk-table-column>
        <!-- <bk-table-column :label="$t('dataSource.operation')" width="130">
          <div class="state-table-operate" slot-scope="props">
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'restore')">
              {{ $t('configDetails.retry') }}
            </bk-button>
          </div>
        </bk-table-column> -->
      </bk-table>
    </section>
  </section>
</template>

<script>
import { formatFileSize } from '@/common/util';

export default {
  name: 'archive-state',
  props: {
    archiveConfigId: {
      type: Object,
      default: '',
    },
  },
  data() {
    return {
      isTableLoading: false,
      dataList: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      stateMap: {
        SUCCESS: this.$t('成功'),
        FAIL: this.$t('失败'),
      },
    };
  },
  created() {
    this.requestData();
  },
  methods: {
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.requestData();
      }
    },
    /**
     * 分页限制
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handleLimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.current = 1;
        this.pagination.limit = page;
        this.requestData();
      }
    },
    requestData() {
      this.isTableLoading = true;
      this.$http.request('archive/archiveConfig', {
        query: {
          page: 0,
          pagesize: 1,
        },
        params: {
          archive_config_id: this.archiveConfigId,
        },
      }).then((res) => {
        const { data } = res;
        if (data.indices.length) {
          // this.dataList = data.snapshots;
          // TODO
          const list = [];
          // const state = data.snapshots[0].state;
          data.indices.forEach((item) => {
            list.push({
              ...item,
            });
          });
          this.dataList.splice(this.dataList.length, 0, ...list);
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    operateHandler() {},
    getFileSize(size) {
      return formatFileSize(size);
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .archive-state-list {
    .state-table {
      th.is-first,
      td.is-first {
        padding-left: 80px;
      }
      .filter-column {
        .cell {
          display: flex;
        }
      }
    }
  }
</style>
