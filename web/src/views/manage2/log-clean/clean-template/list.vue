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
  <section class="clean-template-container">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="isTableLoading"
        @click="handleCreate">
        {{ $t('新建') }}
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
    <section class="clean-template-list">
      <bk-table
        class="clean-table"
        :data="templateList"
        :size="size"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('logClean.templateName')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logClean.etlConfig')">
          <template slot-scope="props">
            {{ props.row.format }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="200">
          <div class="collect-table-operate" slot-scope="props">
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
  name: 'clean-template',
  data() {
    return {
      isTableLoading: false,
      keyword: '',
      size: 'small',
      pagination: {
        current: 1,
        count: 100,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      templateList: [
        {
          clean_template_id: 1,
          name: '采集',
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
    handleCreate() {
      this.$router.push({
        name: 'clean-template-create',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
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
      this.$http.request('clean/cleanTemplate', {
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
    operateHandler(row, operateType) {
      if (operateType === 'edit') {
        this.$router.push({
          name: 'clean-template-edit',
          params: {
            templateId: row.clean_template_id,
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
          title: this.$t('logClean.Confirm_delete_temp'),
          confirmFn: () => {
            this.requestDeleteTemp(row);
          },
        });
        return;
      }
    },
    requestDeleteTemp(row) {
      this.$http.request('clean/deleteTemplate', {
        params: {
          clean_template_id: row.clean_template_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.templateList.length <= 1
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

  .clean-template-container {
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
  }
</style>
