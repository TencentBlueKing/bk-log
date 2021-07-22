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
  <section class="collection-item-container">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="!collectProject || isAllowedCreate === null || isTableLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="operateHandler({}, 'add')">
        {{ $t('新建采集项') }}
      </bk-button>
      <div class="collect-search fr">
        <bk-input
          :placeholder="$t('dataManage.Search_index_name')"
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="keyword"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="collect-list">
      <bk-table
        class="collect-table"
        :empty-text="$t('btn.vacancy')"
        :data="collectList"
        :size="size"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('dataSource.collector_config_name')" min-width="90">
          <template slot-scope="props">
            <span
              class="text-active"
              v-cursor="{ active: !(props.row.permission && props.row.permission.view_collection) }"
              @click="operateHandler(props.row, 'view')">{{ props.row.collector_config_name }}</span>
            <span
              v-if="!props.row.table_id"
              class="table-mark mark-mini mark-default">
              {{ $t('dataSource.collector_config_unfinished') }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.table_id')" min-width="80">
          <template slot-scope="props">
            <span
              :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.table_id ? props.row.table_id_prefix + props.row.table_id : '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.storage_cluster_name')" min-width="70">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.storage_cluster_name || '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.collector_scenario_name')" min-width="50">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.collector_scenario_name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.category_name')" min-width="50">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">{{ props.row.category_name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :class-name="'td-status'" :label="$t('dataSource.es_host_state')" min-width="55">
          <template slot-scope="props">
            <bk-popover placement="bottom" :always="true" v-if="needGuide && props.$index === 0">
              <div @click.stop="operateHandler(props.row, 'status')">
                <span
                  v-if="['prepare', 'pending', 'unknown', 'running'].includes(props.row.status)"
                  class="status status-running">
                  <i class="bk-icon icon-refresh"></i>
                  {{ props.row.status_name || '--' }}
                </span>
                <span
                  v-else-if="props.row.status === 'stop'"
                  class="text-disabled">
                  {{ props.row.status_name || '--' }}
                </span>
                <span
                  v-else-if="props.row.status === 'terminated'"
                  class="text-disabled cursor-disabled">
                  {{ props.row.status_name || '--' }}
                </span>
                <span v-else :class="['status', 'status-' + props.row.status, { 'cursor-disabled': !loadingStatus }]">
                  <span v-if="props.row.status">
                    <i class="bk-icon icon-circle-shape"></i>
                    {{ props.row.status_name || '--' }}
                  </span>
                  <span class="status status-running" v-if="props.row.status === ''">
                    <i class="bk-icon icon-refresh"></i>
                  </span>
                </span>
              </div>
              <div slot="content" style="padding: 7px 6px;">
                <span style="color: #d2d5dd;">
                  {{ $t('dataSource.click_view') }}
                </span>{{ $t('dataSource.es_host_state') }}
              </div>
            </bk-popover>
            <div
              v-else
              v-cursor="{
                active: !(props.row.permission &&
                  props.row.permission.view_collection) &&
                  props.row.status !== 'terminated'
              }"
              @click.stop="operateHandler(props.row, 'status')">
              <span
                v-if="['prepare', 'pending', 'unknown', 'running'].includes(props.row.status)"
                class="status status-running">
                <i class="bk-icon icon-refresh"></i>
                {{ props.row.status_name || '--' }}
              </span>
              <span
                v-else-if="props.row.status === 'stop'"
                class="text-disabled">
                {{ props.row.status_name || '--' }}
              </span>
              <span
                v-else-if="props.row.status === 'terminated'"
                class="text-disabled cursor-disabled">
                {{ props.row.status_name || '--' }}
              </span>
              <span v-else :class="['status', 'status-' + props.row.status, { 'cursor-disabled': !loadingStatus }]">
                <span v-if="props.row.status">
                  <i class="bk-icon icon-circle-shape"></i>
                  {{ props.row.status_name || '--' }}
                </span>
                <span class="status status-running" v-if="props.row.status === ''">
                  <i class="bk-icon icon-refresh"></i>
                </span>
              </span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_by')" min-width="55">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">{{ props.row.updated_by }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_at')" width="190">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">{{ props.row.updated_at }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="245">
          <div class="collect-table-operate" slot-scope="props">
            <!-- 启用状态下 且存在 index_set_id 才能检索 -->
            <bk-button
              theme="primary" text
              class="king-button"
              :disabled="!props.row.is_active || !props.row.index_set_id"
              v-cursor="{ active: !(props.row.permission && props.row.permission.search_log) }"
              @click="operateHandler(props.row, 'search')">
              {{ $t('nav.retrieve') }}
            </bk-button>
            <bk-button
              theme="primary" text
              class="king-button"
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <bk-button
              theme="primary" text
              :disabled="!props.row.subscription_id"
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
              @click.stop="operateHandler(props.row, 'field')">
              {{ $t('btn.Field') }}
            </bk-button>
            <bk-dropdown-menu ref="dropdown" align="right">
              <i
                class="bk-icon icon-more"
                style="margin-left: 5px; font-size: 14px; font-weight: bold;"
                slot="dropdown-trigger">
              </i>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-if="props.row.is_active">
                  <a
                    href="javascript:void(0);"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{ $t('btn.block') }}
                  </a>
                  <a
                    href="javascript:void(0);"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'stop')">{{ $t('btn.block') }}</a>
                </li>
                <li v-else>
                  <a
                    href="javascript:void(0);"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{ $t('btn.start') }}
                  </a>
                  <a
                    href="javascript:void(0);"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'start')">{{ $t('btn.start') }}</a>
                </li>
                <li>
                  <a
                    href="javascript:void(0);"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.is_active ||
                      !collectProject">
                    {{ $t('btn.delete') }}
                  </a>
                  <a
                    href="javascript:void(0);"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'delete')">{{ $t('btn.delete') }}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </div>
        </bk-table-column>
      </bk-table>
    </section>
  </section>
</template>

<script>
import { projectManages } from '@/common/util';
import { mapGetters } from 'vuex';

export default {
  name: 'collection-item',
  data() {
    return {
      keyword: '',
      count: 0,
      size: 'small',
      needGuide: false,
      timer: null,
      timerNum: 0,
      loadingStatus: false,
      isTableLoading: true,
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      collectList: [],
      collectorIdStr: '',
      collectProject: projectManages(this.$store.state.topMenu, 'collection-item'),
      param: '',
      isAllowedCreate: null,
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
    }),
  },
  created() {
    this.checkCreateAuth();
  },
  mounted() {
    this.needGuide = !localStorage.getItem('needGuide');
    this.timerNum = 0;
    this.search();
  },
  destroyed() {
    this.timerNum = -1;
    this.stopStatusPolling();
  },
  methods: {
    search() {
      this.param = this.keyword;
      this.handlePageChange(1);
    },
    async checkCreateAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: ['create_collection'],
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
    // 表格操作
    async operateHandler(row, operateType) { // type: [view, status , search, edit, field, start, stop, delete]
      if (operateType === 'status' && (!this.loadingStatus || row.status === 'terminated')) return; // 已停用禁止操作
      if (operateType === 'status' && (!row.status || row.status === 'prepare')) {
        return this.operateHandler(row, 'edit');
      }
      if (operateType === 'add') { // 新建权限控制
        if (!this.isAllowedCreate) {
          return this.getOptionApplyData({
            action_ids: ['create_collection'],
            resources: [{
              type: 'biz',
              id: this.bkBizId,
            }],
          });
        }
      } else if (operateType === 'view') { // 查看权限
        if (!(row.permission?.view_collection)) {
          return this.getOptionApplyData({
            action_ids: ['view_collection'],
            resources: [{
              type: 'collection',
              id: row.collector_config_id,
            }],
          });
        }
      } else if (operateType === 'search') { // 检索权限
        if (!(row.permission?.search_log)) {
          return this.getOptionApplyData({
            action_ids: ['search_log'],
            resources: [{
              type: 'indices',
              id: row.index_set_id,
            }],
          });
        }
      } else if (!(row.permission?.manage_collection)) { // 管理权限
        return this.getOptionApplyData({
          action_ids: ['manage_collection'],
          resources: [{
            type: 'collection',
            id: row.collector_config_id,
          }],
        });
      }

      // running、prepare 状态不能启用、停用
      if (operateType === 'start' || operateType === 'stop') {
        if (!this.loadingStatus || row.status === 'running' || row.status === 'prepare' || !this.collectProject) return;
        if (operateType === 'stop') {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('retrieve.Confirm_disable'),
            confirmFn: () => {
              this.toggleCollect(row, operateType);
            },
          });
        } else {
          this.toggleCollect(row, operateType);
        }
        return;
      }
      // running 状态不能删除
      if (operateType === 'delete') {
        if (!this.collectProject) return;
        if (!row.is_active && row.status !== 'running') {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('retrieve.Confirm_delete'),
            confirmFn: () => {
              this.requestDeleteCollect(row);
            },
          });
        }
        return;
      }

      const params = {};
      const query = {};
      const routeMap = {
        add: 'collectAdd',
        view: 'manage-collection',
        status: 'manage-collection',
        edit: 'collectEdit',
        field: 'collectField',
        search: 'retrieve',
      };
      const targetRoute = routeMap[operateType];
      // 查看详情 - 如果处于未完成状态，应该跳转到编辑页面
      if (targetRoute === 'manage-collection') {
        if (!row.table_id) {
          return this.operateHandler(row, 'edit');
        }
      }
      if (targetRoute === 'manage-collection' || targetRoute === 'collectEdit' || targetRoute === 'collectField') {
        params.collectorId = row.collector_config_id;
      }
      if (operateType === 'status') {
        query.type = 'collectionStatus';
      }
      if (operateType === 'search') {
        if (!row.index_set_id) return;
        params.indexId = row.index_set_id;
      }
      this.$store.commit('collect/setCurCollect', row);
      this.$router.push({
        name: targetRoute,
        params,
        query: {
          ...query,
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
      this.stopStatusPolling();
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
    // 轮询
    startStatusPolling() {
      this.timerNum += 1;
      const timerNum = this.timerNum;
      this.stopStatusPolling();
      this.timer = setTimeout(() => {
        timerNum === this.timerNum && this.collectorIdStr && this.requestCollectStatus(true);
      }, 10000);
    },
    stopStatusPolling() {
      clearTimeout(this.timer);
    },
    requestData() {
      this.isTableLoading = true;
      Promise.all([this.requestCollectList()]).then(() => {
        if (this.collectorIdStr) {
          this.requestCollectStatus();
        }
      })
        .catch(() => {})
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    requestCollectList() {
      return new Promise((resolve, reject) => {
        this.$http.request('collect/getCollectList', {
          query: {
            bk_biz_id: this.bkBizId,
            keyword: this.param,
            page: this.pagination.current,
            pagesize: this.pagination.limit,
          },
        }).then((res) => {
          const data = res.data;
          if (data && data.list) {
            const idList = [];
            data.list.forEach((row) => {
              row.status = '';
              row.status_name = '';
              idList.push(row.collector_config_id);
            });
            this.collectList.splice(0, this.collectList.length, ...data.list);
            this.pagination.count = data.total;
            this.collectorIdStr = idList.join(',');
            if (this.needGuide) {
              setTimeout(() => {
                localStorage.setItem('needGuide', 'false');
                this.needGuide = false;
              }, 3000);
            }
          }
          resolve(res);
        })
          .catch((err) => {
            reject(err);
          });
      });
    },
    requestCollectStatus(isPrivate) {
      const timerNum = this.timerNum;
      this.$http.request('collect/getCollectStatus', {
        query: {
          collector_id_list: this.collectorIdStr,
        },
      }).then((res) => {
        if (timerNum === this.timerNum) {
          this.statusHandler(res.data || []);
          this.startStatusPolling();
        }
        if (!isPrivate) {
          this.loadingStatus = true;
        }
      })
        .catch(() => {
          if (isPrivate) {
            this.stopStatusPolling();
          }
        });
    },
    // 启用 || 停用
    toggleCollect(row, type) {
      const { isActive, status, statusName } = row;
      row.status = 'running';
      row.status_name = '部署中';
      this.$http.request(`collect/${type === 'start' ? 'startCollect' : 'stopCollect'}`, {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          row.is_active = !row.is_active;
          this.startStatusPolling();
          this.$router.push({
            name: type === 'start' ? 'collectStart' : 'collectStop',
            params: {
              collectorId: row.collector_config_id || '',
            },
            query: {
              projectId: window.localStorage.getItem('project_id'),
            },
          });
        }
      })
        .catch(() => {
          row.is_active = isActive;
          row.status = status;
          row.status_name = statusName;
        });
    },
    // 删除
    requestDeleteCollect(row) {
      this.$http.request('collect/deleteCollect', {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.collectList.length <= 1
            ? (this.pagination.current > 1 ? this.pagination.current - 1 : 1)
            : this.pagination.current;
          this.handlePageChange(page);
        }
      })
        .catch(() => {});
    },
    statusHandler(data) {
      data.forEach((item) => {
        this.collectList.forEach((row) => {
          if (row.collector_config_id === item.collector_id) {
            row.status = item.status.toLowerCase();
            row.status_name = item.status_name;
          }
        });
      });
    },
  },
};
</script>

<style lang="scss">
  @import '../../../../../scss/mixins/clearfix';
  @import '../../../../../scss/conf';
  @import '../../../../../scss/devops-common.scss';

  .collection-item-container {
    padding: 20px 60px;

    .top-operation {
      margin-bottom: 20px;

      @include clearfix;

      .bk-button {
        width: 120px;
      }
    }

    .collect-search {
      width: 360px;
    }

    .collect-table {
      overflow: visible;

      .text-disabled {
        color: #c4c6cc;
      }

      .text-active {
        color: #3a84ff;
        cursor: pointer;
      }
    }

    .bk-table-body-wrapper {
      overflow: visible;
    }

    .is-last .cell {
      overflow: visible;
    }

    .td-status .cursor-disabled {
      cursor: not-allowed;
    }

    .table-mark {
      margin-left: 4px;
      display: inline-block;
      padding: 0 2px;
      height: 17px;
      line-height: 17px;
      border-radius: 2px;
      font-size: 10px;
      background: #979ba5;
      color: #fff;
    }

    .status {
      cursor: pointer;

      &.status-running i {
        display: inline-block;
        animation: button-icon-loading 1s linear infinite;
      }

      &.status-success i {
        color: $iconSuccessColor;
      }

      &.status-failed i {
        color: $iconFailColor;
      }
    }

    .bk-dropdown-list a.text-disabled:hover {
      color: #c4c6cc;
      cursor: not-allowed;
    }

    .collect-table-operate {
      display: flex;
      justify-content: space-around;
    }

    .bk-dropdown-trigger {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }
</style>
