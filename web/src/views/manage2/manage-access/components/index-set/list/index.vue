<template>
  <section class="index-set-container">
    <div class="operate-box">
      <bk-button
        theme="primary" style="width: 120px;"
        :disabled="!collectProject || isTableLoading || isAllowedCreate === null"
        :loading="isCreateLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="addIndexSet">
        {{ $t('新建索引集') }}
      </bk-button>
      <bk-input
        style="width: 300px;"
        :right-icon="'bk-icon icon-search'"
        v-model="searchParams.keyword"
        @enter="reFilter"
        :placeholder="$t('请输入索引集名称')">
      </bk-input>
    </div>
    <bk-table
      :empty-text="$t('btn.vacancy')"
      :data="indexSetList"
      :pagination="pagination"
      v-bkloading="{ isLoading: isTableLoading }"
      @page-limit-change="handleLimitChange"
      @page-change="handlePageChange">
      <bk-table-column :label="$t('索引集')">
        <template slot-scope="{ row }">
          <bk-button text @click="manageIndexSet('manage', row)">{{ row.index_set_name }}</bk-button>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('采集项')" prop="index_set_id" min-width="200">
        <template slot-scope="props">
          <span>{{ props.row.indexes.map(item => item.result_table_id).join('; ') }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('集群名')">
        <template slot-scope="props">
          <div>{{ props.row.storage_cluster_name || '--' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('状态')" prop="apply_status_name">
        <template slot-scope="{ row }">
          <div
            :class="['status-text', row.apply_status === 'normal' && 'success-status']">
            {{ row.apply_status_name || '--' }}
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('创建时间')">
        <template slot-scope="props">
          <div>{{ props.row.created_at.slice(0, 19) || '--' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('创建人')" prop="created_by"></bk-table-column>
      <bk-table-column :label="$t('操作')" width="150">
        <template slot-scope="props">
          <bk-button
            theme="primary" text style="margin-right: 4px;"
            v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices) }"
            @click="manageIndexSet('edit', props.row)">{{ $t('编辑') }}
          </bk-button>
          <bk-button
            theme="primary" text
            v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices) }"
            @click="manageIndexSet('delete', props.row)" :disabled="!collectProject">{{ $t('删除') }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </section>
</template>

<script>
import { projectManage } from '@/common/util';
import { mapGetters } from 'vuex';

export default {
  name: 'IndexSetList',
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      searchParams: {
        scenario_id: scenarioId,
        is_trace_log: this.$route.name.includes('track') ? '1' : '0',
        keyword: '',
        show_more: true,
      },
      indexSetList: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      isTableLoading: true,
      isCreateLoading: false, // 新建索引集
      isAllowedCreate: null,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      projectId: 'projectId',
    }),
    collectProject() {
      return projectManage(this.$store.state.topMenu, 'collection-item');
    },
  },
  created() {
    this.checkCreateAuth();
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
    handleLimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.current = 1;
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
          this.isCreateLoading = true;
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
          this.isCreateLoading = false;
        }
        return;
      }

      this.$router.push({
        name: this.$route.name.replace('list', 'create'),
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    async manageIndexSet(type, row) {
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

      if (type === 'manage') { // 管理索引集
        this.$store.commit('collect/updateCurIndexSet', row);
        this.$router.push({
          name: this.$route.name.replace('list', 'manage'),
          params: {
            indexSetId: row.index_set_id,
          },
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      } else if (type === 'edit') { // 编辑索引集
        this.$store.commit('collect/updateCurIndexSet', row);
        this.$router.push({
          name: this.$route.name.replace('list', 'edit'),
          params: {
            indexSetId: row.index_set_id,
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
  @import '../../../../../../scss/mixins/clearfix';
  @import '../../../../../../scss/conf';

  .index-set-container {
    padding: 20px 60px;

    .operate-box {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .status-text {
      color: #ea3636;

      &.success-status {
        color: #2dcb56;;
      }
    }
  }
</style>
