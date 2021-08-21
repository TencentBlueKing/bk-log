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
        <bk-table-column :label="$t('logArchive.indexName')" width="300">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.startStopTime')" min-width="200">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.remain')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.size')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.archiveStatus')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.isRestore')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="130">
          <div class="state-table-operate" slot-scope="props">
            <!-- 重试 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'restore')">
              {{ $t('configDetails.retry') }}
            </bk-button>
            <!-- 编辑 -->
          </div>
        </bk-table-column>
      </bk-table>
    </section>
  </section>
</template>

<script>
export default {
  name: 'archive-state',
  data() {
    return {
      isTableLoading: false,
      dataList: [{ name: 'log' }],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
    };
  },
  methods: {
    search() {
      this.pagination.current = 1;
      this.requestData();
    },
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
      // this.$http.request('clean/cleanTemplate', {
      //   query: {
      //     ...this.params,
      //     bk_biz_id: this.bkBizId,
      //     page: this.pagination.current,
      //     pagesize: this.pagination.limit,
      //   },
      // }).then((res) => {
      //   const { data } = res;
      //   this.pagination.count = data.total;
      //   this.templateList = data.list;
      // })
      //   .catch((err) => {
      //     console.warn(err);
      //   })
      //   .finally(() => {
      //     this.isTableLoading = false;
      //   });
    },
    operateHandler(row, operateType) {
      console.log(row, operateType);
    //   if (operateType === 'edit') {
    //     this.$router.push({
    //       name: 'clean-template-edit',
    //       params: {
    //         templateId: row.clean_template_id,
    //       },
    //       query: {
    //         projectId: window.localStorage.getItem('project_id'),
    //       },
    //     });
    //     return;
    //   }
    //   if (operateType === 'delete') {
    //     this.$bkInfo({
    //       type: 'warning',
    //       title: this.$t('logClean.Confirm_delete_temp'),
    //       confirmFn: () => {
    //         this.requestDeleteTemp(row);
    //       },
    //     });
    //     return;
    //   }
    // },
    // requestDeleteTemp(row) {
    //   this.$http.request('clean/deleteTemplate', {
    //     params: {
    //       clean_template_id: row.clean_template_id,
    //     },
    //   }).then((res) => {
    //     if (res.result) {
    //       const page = this.templateList.length <= 1
    //         ? (this.pagination.current > 1 ? this.pagination.current - 1 : 1)
    //         : this.pagination.current;
    //       this.messageSuccess(this.$t('删除成功'));
    //       if (page !== this.pagination.current) {
    //         this.handlePageChange(page);
    //       } else {
    //         this.requestData();
    //       }
    //     }
    //   })
    //     .catch(() => {});
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
