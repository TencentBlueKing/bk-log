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
  <section class="collect-access-wrapper">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="!collectProject || isAllowedCreate === null || isTableLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="operateHandler({}, 'add')">
        {{ $t('btn.newBtn') }}
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
        @page-limit-change="handlelimitChange">
        <bk-table-column :label="$t('dataSource.collector_config_name')" min-width="90">
          <template slot-scope="props">
            <span class="text-active"
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
                <span style="color: #d2d5dd;">{{$t('dataSource.click_view')}}</span>{{$t('dataSource.es_host_state')}}
              </div>
            </bk-popover>
            <div
              v-else
              v-cursor="{ active: !(props.row.permission &&
                props.row.permission.view_collection) &&
                props.row.status !== 'terminated' }"
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
              :disabled="!props.row.is_active || !props.row.index_set_id"
              v-cursor="{ active: !(props.row.permission && props.row.permission.search_log) }"
              @click="operateHandler(props.row, 'search')">
              {{ $t('nav.retrieve') }}
            </bk-button>
            <!-- 第二次逻辑调整 -->
            <bk-button
              theme="primary" text
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('btn.edit') }}
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
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{$t('btn.block')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'stop')">{{$t('btn.block')}}</a>
                </li>
                <li v-else>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{$t('btn.start')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'start')">{{$t('btn.start')}}</a>
                </li>
                <li>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.is_active ||
                      !collectProject">
                    {{$t('btn.delete')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                    @click.stop="operateHandler(props.row, 'delete')">{{$t('btn.delete')}}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
            <!-- 第二次逻辑调整 - END -->

            <!-- 第一次调整的逻辑， 备用 - START -->
            <!-- 无采集状态下不能进行除检索之外的任何操作， 停用状态下只能进行删除和启用操作
                        <tempalte v-if="!props.row.status || props.row.status === 'terminated'">
                            <bk-button theme="primary" text disabled>{{ '编辑' || $t('btn.delete') }}</bk-button>
                            <bk-button theme="primary" text disabled>{{ '字段提取' || $t('btn.delete') }}</bk-button>
                            <bk-dropdown-menu ref="dropdown" align="right">
                                <i
                                class="bk-icon icon-more"
                                 style="margin-left: 5px;
                                 font-size: 14px;
                                 font-weight:bold;"
                                 slot="dropdown-trigger">
                                 </i>
                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                    <li
                                     v-if="props.row.is_active"><a href="javascript:;" class="text-disabled">停用</a></li>
                                    <li v-else>
                                      <a
                                      href="javascript:;"
                                      :class="{ 'text-disabled': !props.row.status }"
                                       @click.stop="operateHandler(props.row, 'start')">
                                       启用
                                       </a>
                                      </li>
                                    <li>
                                      <a
                                      href="javascript:;"
                                      :class="{ 'text-disabled': !props.row.status }"
                                       @click.stop="operateHandler(props.row, 'delete')">
                                       删除
                                       </a>
                                    </li>
                                </ul>
                            </bk-dropdown-menu>
                        </tempalte>
                        <tempalte v-else>
                           所有status下都可以进行编辑
                            <bk-button
                            theme="primary"
                             text
                              @click.stop="operateHandler(props.row, 'edit')">{{ $t('btn.edit') }}</bk-button>
                            subscription_id 存在才能进行提取
                            <bk-button
                            theme="primary"
                            text
                            :disabled="!props.row.subscription_id"
                            @click.stop="operateHandler(props.row, 'field')">{{ $t('btn.Field') }}</bk-button>
                            所有status下都可以进行编辑
                            <bk-button
                            theme="primary"
                             text
                              @click.stop="operateHandler(props.row, 'edit')">
                              {{ '编辑' || $t('btn.edit') }}
                            </bk-button>
                            subscription_id 存在才能进行提取
                            <bk-button
                            theme="primary"
                            text
                            :disabled="!props.row.subscription_id"
                            @click.stop="operateHandler(props.row, 'field')">
                            {{ '字段提取' || $t('btn.delete') }}
                            </bk-button>

                            <bk-dropdown-menu ref="dropdown" align="right">
                                <i
                                class="bk-icon icon-more"
                                style="margin-left: 5px; font-size: 14px; font-weight:bold;"
                                slot="dropdown-trigger"></i>
                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                    running状态 不能启用、停用、删除
                                    <li v-if="props.row.is_active">
                                        <a
                                        href="javascript:;"
                                        :class="{ 'text-disabled': props.row.status === 'running' }"
                                         @click.stop="operateHandler(props.row, 'stop')">{{$t('btn.block')}}</a>
                                    </li>
                                    <li v-else>
                                        <a
                                        href="javascript:;"
                                        :class="{ 'text-disabled': props.row.status === 'running' }"
                                         @click.stop="operateHandler(props.row, 'start')">{{$t('btn.start')}}</a>
                                    </li>
                                    <li>
                                        <a
                                        href="javascript:;"
                                        :class="{
                                          'text-disabled': props.row.status === 'running' || !props.row.is_active }"
                                        @click.stop="operateHandler(props.row, 'delete')">{{$t('btn.delete')}}</a>
                                    </li>
                                </ul>
                            </bk-dropdown-menu>
                        </tempalte> -->
            <!-- 第一次调整的逻辑， 备用 - END -->
          </div>
        </bk-table-column>
      </bk-table>
    </section>
  </section>
</template>

<script>
import { projectManage } from '@/common/util';
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'access-collect',
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
      param: '',
      isAllowedCreate: null,
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
    }),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    collectProject() {
      return projectManage(this.menuProject, 'manage', 'manage');
    },
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
        // eslint-disable-next-line camelcase
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
        // eslint-disable-next-line camelcase
        if (!(row.permission?.search_log)) {
          return this.getOptionApplyData({
            action_ids: ['search_log'],
            resources: [{
              type: 'indices',
              id: row.index_set_id,
            }],
          });
        }
      // eslint-disable-next-line camelcase
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
              this.requesToggleCollect(row, operateType);
            },
          });
        } else {
          this.requesToggleCollect(row, operateType);
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
              this.requesDeleteCollect(row);
            },
          });
        }
        return;
      }

      const params = {};
      // 查看详情 - 如果处于未完成状态，应该跳转到编辑页面
      if (operateType === 'view') {
        if (!row.table_id) {
          this.operateHandler(row, 'edit');
          return;
        }
      }
      // 检索
      if (operateType === 'search') {
        if (!row.index_set_id) return;
        params.indexId = row.index_set_id || '';
      }
      const routerArr = [
        { type: 'view', name: 'allocation' },
        { type: 'status', name: 'allocation' },
        { type: 'search', name: 'retrieve' },
        { type: 'add', name: 'collectAdd' },
        { type: 'edit', name: 'collectEdit' },
        { type: 'field', name: 'collectField' },
      ];
      const current = routerArr.find(item => item.type === operateType);
      if (current) {
        if (operateType === 'view' || operateType === 'status' || operateType === 'edit' || operateType === 'field') {
          params.collectorId = row.collector_config_id || '';
        }
        if (operateType === 'search') {
          params.indexId = row.index_set_id;
        }
        params.collectProject = this.collectProject;
        this.$router.push({
          name: current.name,
          params,
          hash: operateType === 'status' ? '#hisitory' : '',
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      }
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
    handlelimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.limit = page;
        this.requestData();
      }
    },
    // 轮询
    startStatusPolling() {
      this.timerNum += 1;
      const { timerNum } = this;
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
      this.$http.request('collect/getCollectList', {
        query: {
          bk_biz_id: this.bkBizId,
          keyword: this.param,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
        },
      }).then((res) => {
        const { data } = res;
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
        if (this.collectorIdStr) {
          this.requestCollectStatus();
        }
      })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    requestCollectStatus(isPrivate) {
      const { timerNum } = this;
      this.$http.request('collect/getCollectStatus', {
        // mock: true,
        // manualSchema: true,
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
    requesToggleCollect(row, type) {
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
    requesDeleteCollect(row) {
      this.$http.request('collect/deleteCollect', {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.collectList.length <= 1
            ? (this.pagination.current > 1
              ? this.pagination.current - 1 : 1) : this.pagination.current;
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
  @import '../../scss/mixins/clearfix';
  @import '../../scss/conf';
  @import '../../scss/devops-common.scss';

  .collect-access-wrapper {
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
      // &.mark-mini {
      //     padding: 0 12px;
      //     line-height: 32px;
      //     border-radius: 4px;
      //     transform: scale(0.5)
      // }
      // &.mark-default {
      //     background: #979BA5;
      //     color: #FFF;
      // }
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
