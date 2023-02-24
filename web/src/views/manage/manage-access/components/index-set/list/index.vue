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
  <section class="index-set-container" data-test-id="logIndexSet_section_logIndexSetBox">
    <bk-alert
      v-if="searchParams.is_trace_log === '0'"
      class="alert-info"
      type="info"
      :title="alertText"></bk-alert>
    <div class="operate-box">
      <bk-button
        theme="primary"
        style="width: 120px;"
        data-test-id="logIndexSetBox_button_newIndexSet"
        :disabled="!collectProject || isTableLoading || isAllowedCreate === null"
        :loading="isCreateLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="addIndexSet">
        {{ $t('新建索引集') }}
      </bk-button>
      <bk-input
        style="width: 300px;"
        data-test-id="logIndexSetBox_input_searchIndexSet"
        :right-icon="'bk-icon icon-search'"
        v-model="searchParams.keyword"
        @enter="reFilter"
        :placeholder="$t('请输入索引集名称')">
      </bk-input>
    </div>
    <bk-table
      :empty-text="$t('暂无内容')"
      :data="indexSetList"
      :pagination="pagination"
      data-test-id="logIndexSetBox_table_indexSetTable"
      v-bkloading="{ isLoading: isTableLoading }"
      @page-limit-change="handleLimitChange"
      @page-change="handlePageChange">
      <bk-table-column :label="$t('索引集')">
        <template slot-scope="{ row }">
          <!-- <bk-button
            class="indexSet-name"
            text
            @click="manageIndexSet('manage', row)">
            {{ row.index_set_name }}
          </bk-button> -->
          <span
            class="indexSet-name"
            v-cursor="{ active: !(row.permission && row.permission[authorityMap.MANAGE_INDICES_AUTH]) }"
            :title="row.index_set_name"
            @click="manageIndexSet('manage', row)">
            {{ row.index_set_name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t('采集项')"
        prop="index_set_id"
        min-width="200">
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
            v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_INDICES_AUTH]) }"
            @click="manageIndexSet('search', props.row)">{{ $t('检索') }}
          </bk-button>
          <bk-button
            theme="primary" text style="margin-right: 4px;"
            v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices_v2) }"
            :disabled="!props.row.is_editable"
            @click="manageIndexSet('edit', props.row)">
            <span v-bk-tooltips.top="{
              content: `${$t('内置索引集')}, ${$t('不可编辑')}`,
              disabled: props.row.is_editable
            }">{{ $t('编辑') }}</span>
          </bk-button>
          <bk-button
            theme="primary" text
            v-cursor="{ active: !(props.row.permission && props.row.permission.manage_indices_v2) }"
            :disabled="!props.row.is_editable || !collectProject"
            @click="manageIndexSet('delete', props.row)">
            <span v-bk-tooltips.top="{
              content: `${$t('内置索引集')}, ${$t('不可删除')}`,
              disabled: props.row.is_editable
            }">{{ $t('删除') }}</span>
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </section>
</template>

<script>
import { projectManages } from '@/common/util';
import { mapGetters } from 'vuex';
import * as authorityMap from '../../../../../../common/authority-map';

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
      spaceUid: 'spaceUid',
    }),
    authorityMap() {
      return authorityMap;
    },
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    alertText() {
      const textMap = {
        log: this.$t('索引集允许用户可以跨多个采集的索引查看日志。'),
        es: this.$t('如果日志已经存储在Elasticsearch，可以在“集群管理”中添加Elasticsearch集群，就可以通过创建索引集来使用存储中的日志数据。'),
        bkdata: this.$t('通过新建索引集添加计算平台中的Elasticsearch的索引，就可以在日志平台中进行检索、告警、可视化等。'),
      };
      return textMap[this.scenarioId];
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
          action_ids: [authorityMap.CREATE_INDICES_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
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
      query.space_uid = this.spaceUid;
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
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.getIndexSetList();
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
            action_ids: [authorityMap.CREATE_INDICES_AUTH],
            resources: [{
              type: 'space',
              id: this.spaceUid,
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
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    async manageIndexSet(type, row) {
      if (!(row.permission?.[authorityMap.MANAGE_INDICES_AUTH])) {
        try {
          this.isTableLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: [authorityMap.MANAGE_INDICES_AUTH],
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
            spaceUid: this.$store.state.spaceUid,
          },
        });
      } else if (type === 'search') { // 检索
        this.$router.push({
          name: 'retrieve',
          params: {
            indexId: row.index_set_id ? row.index_set_id : row.bkdata_index_set_ids[0],
          },
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      }  else if (type === 'edit') { // 编辑索引集
        this.$store.commit('collect/updateCurIndexSet', row);
        this.$router.push({
          name: this.$route.name.replace('list', 'edit'),
          params: {
            indexSetId: row.index_set_id,
          },
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      } else if (type === 'delete') { // 删除索引集
        this.$bkInfo({
          subTitle: this.$t('当前索引集为{n}，确认要删除？', { n: row.index_set_name }),
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
    padding: 20px 24px;

    .alert-info {
      margin-bottom: 20px;
    }

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

    .indexSet-name {
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      color: #3a84ff;
      width: 100%;
      text-overflow: ellipsis;
      cursor: pointer;
    }
  }
</style>
