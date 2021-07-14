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
  <section>
    <bk-container :col="12" class="operate-box">
      <bk-row>
        <bk-col :span="3">
          <bk-button
            theme="primary" style="width: 120px;"
            :disabled="!collectProject || isTableLoading || isAllowedCreate === null"
            v-cursor="{ active: isAllowedCreate === false }"
            @click="addIndexSet">
            {{ $t('btn.newBtn') }}
          </bk-button>
        </bk-col>
        <bk-col :span="9" class="table-search-box">
          <bk-input
            :placeholder="$t('btn.search')"
            :right-icon="'bk-icon icon-search'"
            v-model="searchParams.keyword"
            @enter="reFilter">
          </bk-input>
          <bk-select
            v-model="searchParams.scenario_id"
            searchable
            :clearable="true"
            :placeholder="$t('btn.select')"
            @change="reFilter">
            <bk-option
              v-for="(option, index) in dataSourceList"
              :key="index"
              :id="option.scenario_id"
              :name="option.scenario_name">
            </bk-option>
          </bk-select>
        </bk-col>
      </bk-row>
    </bk-container>
    <bk-table
      :empty-text="$t('btn.vacancy')"
      :data="indexSetList"
      :size="size"
      :pagination="pagination"
      v-bkloading="{ isLoading: isTableLoading }"
      @page-limit-change="handlelimitChange"
      @page-change="handlePageChange">
      <bk-table-column :label="$t('indexSetList.index_set')" prop="index_set_name"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.index')" prop="index_set_id">
        <template slot-scope="props">
          <span v-for="(item, index) in props.row.indexes" :key="index">{{ item.result_table_id }}；</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('configDetails.dataClassify')" prop="category_name"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.dataOrigin')" prop="scenario_name"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.clusterName')">
        <template slot-scope="props">
          <div>{{props.row.storage_cluster_name || '--'}}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('retrieve.status')" prop="apply_status_name"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.created_time')" prop="created_at"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.creator')" prop="created_by"></bk-table-column>
      <bk-table-column :label="$t('indexSetList.jurisdiction')" v-if="accessUserManage">
        <template slot-scope="props">
          <span v-for="(item, index) in props.row.view_roles_list" :key="index">{{ item.role_name }}；</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('indexSetList.operation')" width="150">
        <template slot-scope="props">
          <bk-button theme="primary" text
                     v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices) }"
                     @click="manageIndexSet('edit', props.row)">{{ $t('btn.edit') }}
          </bk-button>
          <bk-button theme="primary" text
                     v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices) }"
                     @click="manageIndexSet('delete', props.row)" :disabled="!collectProject">{{ $t('btn.delete') }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </section>
</template>

<script>
import { projectManage } from '@/common/util';
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'indexSet',
  components: {},
  mixins: [],
  props: {},
  data() {
    return {
      dataSourceList: [],
      searchParams: {
        scenario_id: '',
        keyword: '',
        show_more: true,
      },
      indexSetList: [],
      size: 'small',
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      isTableLoading: true,
      isAllowedCreate: null,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      projectId: 'projectId',
      accessUserManage: 'accessUserManage',
    }),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    collectProject() {
      return projectManage(this.menuProject, 'manage', 'indexSet');
    },
  },
  created() {
    this.checkCreateAuth();
    this.getDataSourceList();
    this.getIndexSetList();
  },
  methods: {
    async checkCreateAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: ['create_indices'],
          resources: [{
            type: 'biz',
            id: this.bkBizId,
          }],
        });
        this.isAllowedCreate = res.isAllowed;
      } catch (err) {
        console.warn(err);
        this.isAllowedCreate = false;
      }
    },
    /**
             * 获取数据源
             */
    getDataSourceList() {
      this.$http.request('/source/scenario', {
        query: {
          bk_biz_id: this.bkBizId,
        },
      }).then((res) => {
        this.dataSourceList = res.data;
      });
    },
    /**
             * 获取索引集列表
             */
    getIndexSetList() {
      const query = JSON.parse(JSON.stringify(this.searchParams));
      query.page = this.pagination.current;
      query.pagesize = this.pagination.limit;
      query.project_id = this.projectId;
      this.$http.request('/indexSet/list', {
        query,
      }).then((res) => {
        this.indexSetList = res.data.list;
        this.pagination.count = res.data.total;
        this.isTableLoading = false;
      });
    },
    /**
             * 分页变换
             * @param  {Number} page 当前页码
             * @return {[type]}      [description]
             */
    handlePageChange(page) {
      this.pagination.current = page;
      this.getIndexSetList();
    },
    /**
             * 分页限制
             * @param  {Number} page 当前页码
             * @return {[type]}      [description]
             */
    handlelimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.limit = page;
        this.getIndexSetList();
      }
    },
    /**
             * 筛选条件变更，重新获取列表
             */
    reFilter() {
      this.pagination.page = 1;
      this.isTableLoading = true;
      this.getIndexSetList();
    },
    /**
             * 跳转新增页面
             */
    async addIndexSet() {
      if (this.isAllowedCreate === false) {
        try {
          this.isTableLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: ['create_indices'],
            resources: [{
              type: 'biz',
              id: this.bkBizId,
            }],
          });
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.isTableLoading = false;
        }
        return;
      }

      this.$router.push({
        name: 'addIndexSet',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    async manageIndexSet(type, row) {
      // eslint-disable-next-line camelcase
      if (!(row.permission?.manage_indices)) {
        try {
          this.isTableLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: ['manage_indices'],
            resources: [{
              type: 'indices',
              id: row.index_set_id,
            }],
          });
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.isTableLoading = false;
        }
        return;
      }

      if (type === 'edit') { // 编辑索引集
        this.$router.push({
          name: 'editIndexSet',
          params: {
            id: row.index_set_id,
          },
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      } else if (type === 'delete') { // 删除索引集
        this.$bkInfo({
          title: this.$t('shield.isdelete'),
          maskClose: true,
          confirmFn: () => {
            this.$bkLoading({
              opacity: 0.6,
            });
            this.$http.request('/indexSet/remove', {
              params: {
                index_set_id: row.index_set_id,
              },
            }).then(() => {
              this.getIndexSetList();
            })
              .finally(() => {
                this.$bkLoading.hide();
              });
          },
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/clearfix';
  @import '../../scss/conf';

  section {
    padding: 20px 60px;

    .operate-box {
      margin-left: -20px;
      margin-right: -20px;
      margin-bottom: 20px;

      @include clearfix;

      .table-search-box {
        @include clearfix;

        > * {
          float: right;
          max-width: 250px;
          min-width: 180px;
          margin-left: 10px;
          background: #fff;
        }
      }
    }
  }
</style>
