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
  <section class="log-archive-repository" data-test-id="archive_section_storehouseContainer">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        data-test-id="storehouseContainer_button_addNewStoreHouse"
        @click="handleCreate">
        {{ $t('新建') }}
      </bk-button>
      <div class="repository-search fr">
        <bk-input
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          data-test-id="storehouseContainer_input_searchTableItem"
          @enter="handleSearch">
        </bk-input>
      </div>
    </section>
    <section class="log-repository-table" data-test-id="storehouseContainer_section_tableList">
      <bk-table
        class="repository-table"
        :data="tableDataPaged"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('logArchive.esID')" width="120">
          <template slot-scope="props">
            {{ props.row.cluster_id }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.repositoryName')">
          <template slot-scope="props">
            {{ props.row.repository_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('ES集群')">
          <template slot-scope="props">
            {{ props.row.cluster_name }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('logArchive.repositoryType')"
          prop="type"
          class-name="filter-column"
          column-key="type"
          :filters="repositoryFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ repoTypeMap[props.row.type] }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('来源')"
          prop="cluster_source_type"
          class-name="filter-column"
          column-key="cluster_source_type"
          :filters="sourceFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ props.row.cluster_source_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('创建人')">
          <template slot-scope="props">
            {{ props.row.creator }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('创建时间')">
          <template slot-scope="props">
            {{ props.row.create_time }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="160">
          <div class="repository-table-operate" slot-scope="props">
            <!-- 编辑 -->
            <!-- <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_es_source) }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button> -->
            <!-- 删除 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_ES_SOURCE_AUTH]) }"
              @click.stop="operateHandler(props.row, 'delete')">
              {{ $t('删除') }}
            </bk-button>
          </div>
        </bk-table-column>
      </bk-table>
    </section>
    <!-- 新增/编辑归档仓库 -->
    <RepositorySlider
      v-if="isRenderSlider"
      :show-slider.sync="showSlider"
      :edit-cluster-id="editClusterId"
      @updated="handleUpdated"
    />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import RepositorySlider from './repository-slider.vue';
import * as authorityMap from '../../../../common/authority-map';

export default {
  name: 'ArchiveRepository',
  components: {
    RepositorySlider,
  },
  data() {
    return {
      isTableLoading: false,
      isRenderSlider: true,
      showSlider: false,
      keyword: '',
      editClusterId: null, // 编辑ES源ID,
      dataList: [],
      tableDataOrigin: [], // 原始数据
      tableDataSearched: [], // 搜索过滤数据
      tableDataPaged: [], // 前端分页
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      params: {
        keyword: '',
      },
      filterConditions: {
        type: '',
        cluster_source_type: '',
      },
      repoTypeMap: {
        hdfs: 'HDFS',
        fs: this.$t('logArchive.sharedDirectory'),
        cos: 'COS',
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      globalsData: 'globals/globalsData',
    }),
    authorityMap() {
      return authorityMap;
    },
    repositoryFilters() {
      const target = [];
      Object.keys(this.repoTypeMap).map((item) => {
        target.push({
          text: this.repoTypeMap[item],
          value: item,
        });
      });
      return target;
    },
    sourceFilters() {
      const { es_source_type } = this.globalsData;
      const target = [];
      // eslint-disable-next-line camelcase
      es_source_type && es_source_type.forEach((data) => {
        target.push({
          text: data.name,
          value: data.id,
        });
      });
      return target;
    },
  },
  created() {
    this.getTableData();
  },
  methods: {
    handleSearch() {
      if (this.params.keyword) {
        this.tableDataSearched = this.tableDataOrigin.filter((item) => {
          if (item.repository_name) {
            return (item.repository_name + item.cluster_name).includes(this.params.keyword);
          }
        });
      } else {
        this.tableDataSearched = this.tableDataOrigin;
      }
      this.pagination.current = 1;
      this.pagination.count = this.tableDataSearched.length;
      this.computePageData();
    },
    getTableData() {
      this.isTableLoading = true;
      this.$http.request('archive/getRepositoryList', {
        query: {
          bk_biz_id: this.bkBizId,
        },
      }).then((res) => {
        const { data } = res;
        if (!data.length) {
          return;
        }
        this.tableDataOrigin = data;
        this.tableDataSearched = data;
        this.pagination.count = data.length;
        this.computePageData();
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    // 根据分页数据过滤表格
    computePageData() {
      const { current, limit } = this.pagination;
      const start = (current - 1) * limit;
      const end = this.pagination.current * this.pagination.limit;
      this.tableDataPaged = this.tableDataSearched.slice(start, end);
    },
    handleFilterChange(data) {
      Object.keys(data).forEach((item) => {
        this.tableDataSearched = this.tableDataOrigin.filter((repo) => {
          this.filterConditions[item] = Object.values(data)[0][0];
          const { type, cluster_source_type: clusterType } = this.filterConditions;
          if (!type && !clusterType) {
            return true;
          }
          if (type && clusterType) {
            return repo.type === type && repo.cluster_source_type === clusterType;
          }
          return repo.type === type || repo.cluster_source_type === clusterType;
        });
      });
      this.pagination.current = 1;
      this.pagination.count = this.tableDataSearched.length;
      this.computePageData();
    },
    async handleCreate() {
      this.editClusterId = null;
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
        this.computePageData();
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
        this.computePageData();
      }
    },
    handleUpdated() {
      this.showSlider = false;
      this.pagination.count = 1;
      this.getTableData();
    },
    operateHandler(row, operateType) {
      if (!(row.permission?.[authorityMap.MANAGE_ES_SOURCE_AUTH])) {
        return this.getOptionApplyData({
          action_ids: [authorityMap.MANAGE_ES_SOURCE_AUTH],
          resources: [{
            type: 'es_source',
            id: row.cluster_id,
          }],
        });
      }

      // if (operateType === 'edit') {
      //   this.editClusterId = row.cluster_id;
      //   this.showSlider = true;
      //   return;
      // }

      if (operateType === 'delete') {
        this.$bkInfo({
          type: 'warning',
          subTitle: `${this.$t('当前仓库名称为')} ${row.repository_name}，${this.$t('确认要删除')}`,
          confirmFn: () => {
            this.requestDeleteRepo(row);
          },
        });
      }
    },
    requestDeleteRepo(row) {
      this.$http.request('archive/deleteRepository', {
        data: {
          cluster_id: row.cluster_id,
          snapshot_repository_name: row.repository_name,
        },
      }).then((res) => {
        if (res.result) {
          this.messageSuccess(this.$t('删除成功'));
          if (this.tableDataPaged.length <= 1) {
            this.pagination.current = this.pagination.current > 1 ? this.pagination.current - 1 : 1;
          }
          const deleteIndex = this.tableDataSearched.findIndex((item) => {
            return item.repository_name === row.repository_name;
          });
          this.tableDataSearched.splice(deleteIndex, 1);
          this.computePageData();
        }
      })
        .catch(() => {});
    },
    async getOptionApplyData(paramData) {
      try {
        this.isTableLoading = true;
        const res = await this.$store.dispatch('getApplyData', paramData);
        this.$store.commit('updateAuthDialogData', res.data);
      } catch (err) {
        console.warn(err);
      } finally {
        this.isTableLoading = false;
      }
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
