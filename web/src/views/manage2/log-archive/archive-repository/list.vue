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
  <section class="log-archive-repository">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        @click="handleCreate">
        {{ $t('新建') }}
      </bk-button>
      <div class="repository-search fr">
        <bk-input
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="log-repository-table">
      <bk-table
        class="repository-table"
        :data="dataList"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column label="ID" width="80">
          <template slot-scope="props">
            {{ props.row.id }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.repositoryName')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('ES集群')">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('logArchive.repositoryType')"
          prop="repositoryType"
          class-name="filter-column"
          column-key="repositoryType"
          :filters="repositoryFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('来源')"
          prop="source"
          class-name="filter-column"
          column-key="source"
          :filters="sourceFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('状态')">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('创建人')">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('创建时间')">
          <template slot-scope="props">
            {{ props.row.es }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="160">
          <div class="repository-table-operate" slot-scope="props">
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
    <!-- 新增/编辑归档仓库 -->
    <RepositorySlider
      v-if="isRenderSlider"
      :show-slider.sync="showSlider"
    />
  </section>
</template>

<script>
import RepositorySlider from './repository-slider.vue';

export default {
  name: 'archive-repository',
  components: {
    RepositorySlider,
  },
  data() {
    return {
      isTableLoading: false,
      isRenderSlider: true,
      showSlider: false,
      keyword: '',
      dataList: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      params: {
        keyword: '',
        etl_config: '',
      },
    };
  },
  computed: {
    repositoryFilters() {
      return [];
    },
    sourceFilters() {
      return [];
    },
  },
  methods: {
    search() {
      this.pagination.current = 1;
      this.requestData();
    },
    handleFilterChange(data) {
      Object.keys(data).forEach((item) => {
        this.params[item] = data[item].join('');
      });
      this.pagination.current = 1;
      this.search();
    },
    handleCreate() {
      this.showSlider = true;
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
      // this.isTableLoading = true;
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

  .log-archive-repository {
    padding: 20px 24px;
    .top-operation {
      margin-bottom: 20px;
      @include clearfix;
      .bk-button {
        width: 120px;
      }
    }
    .repository-search {
      width: 320px;
    }
    .repository-table {
      .filter-column {
        .cell {
          display: flex;
        }
      }
    }
  }
</style>
