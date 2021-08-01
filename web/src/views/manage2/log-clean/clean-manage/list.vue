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
  <section class="log-clean-container">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="isTableLoading"
        @click="handleCreate">
        {{ $t('新增') }}
      </bk-button>
      <div class="clean-search fr">
        <bk-input
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="keyword"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="log-clean-list">
      <bk-table
        class="clean-table"
        :data="cleanList"
        :size="size"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('migrate.collectionItemName')">
          <template slot-scope="props">
            {{ props.row.collector_config_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logClean.etlConfig')">
          <template slot-scope="props">
            {{ props.row.format }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logClean.storageIndex')">
          <template slot-scope="props">
            {{ props.row.storage }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_by')">
          <template slot-scope="props">
            {{ props.row.updated_by }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_at')">
          <template slot-scope="props">
            {{ props.row.updated_at }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="200">
          <div class="collect-table-operate" slot-scope="props">
            <!-- 检索 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click="operateHandler">
              {{ $t('nav.retrieve') }}
            </bk-button>
            <!-- 编辑 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <!-- 删除 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'delete')">
              {{ $t('btn.delete') }}
            </bk-button>
          </div>
        </bk-table-column>
      </bk-table>
    </section>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'clean-list',
  data() {
    return {
      isTableLoading: true,
      keyword: '',
      size: 'small',
      pagination: {
        current: 1,
        count: 100,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      cleanList: [
        {
          collector_config_id: 1,
          collector_config_name: '采集',
          format: 'JSON',
          storage: '正则',
          updated_by: 'zijia',
          updated_at: '2020-07-30 15:00',
        },
      ],
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
    }),
  },
  mounted() {
    this.search();
  },
  methods: {
    search() {
      this.param = this.keyword;
      this.handlePageChange(1);
    },
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      this.pagination.current = page;
      this.requestData();
    },
    /**
     * 分页限制
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handleLimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.limit = page;
        this.requestData();
      }
    },
    requestData() {
      this.$http.request('clean/cleanList', {
        query: {
          bk_biz_id: this.bkBizId,
          // keyword: this.param,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
        },
      }).then((res) => {
        console.log(res);
        // this.pagination.count = data.total;
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    handleCreate() {
      this.$router.push({
        name: 'clean-create',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    operateHandler(row, operateType) {
      if (operateType === 'edit') {
        this.$router.push({
          name: 'clean-edit',
          params: {
            collectorId: row.collector_config_id,
          },
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
        return;
      }
      if (operateType === 'delete') {
        // if (!this.collectProject) return;
        this.$bkInfo({
          type: 'warning',
          title: this.$t('logClean.Confirm_delete'),
          confirmFn: () => {
            this.requestDeleteClenItem(row);
          },
        });
        return;
      }
    },
    requestDeleteClenItem(row) {
      this.$http.request('clean/deleteClean', {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.cleanList.length <= 1
            ? (this.pagination.current > 1 ? this.pagination.current - 1 : 1)
            : this.pagination.current;
          this.handlePageChange(page);
        }
      })
        .catch(() => {});
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .log-clean-container {
    padding: 20px 60px;
    .top-operation {
      margin-bottom: 20px;
      @include clearfix;
      .bk-button {
        width: 120px;
      }
    }
    .clean-search {
      width: 360px;
    }
    .clean-table {
      overflow: visible;
      .text-disabled {
        color: #c4c6cc;
      }
      .text-active {
        color: #3a84ff;
        cursor: pointer;
      }
      .filter-column {
        .cell {
          display: flex;
        }
      }
    }

    .bk-table-body-wrapper {
      overflow: visible;
    }

    .is-last .cell {
      overflow: visible;
    }
  }
</style>
