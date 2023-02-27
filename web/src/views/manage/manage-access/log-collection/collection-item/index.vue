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
  <section
    class="collection-item-container"
    data-test-id="logCollection_div_logCollectionBox">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="!collectProject || isAllowedCreate === null || isTableLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="operateHandler({}, 'add')"
        data-test-id="logCollectionBox_button_addNewCollectionItem">
        {{ $t('新建采集项') }}
      </bk-button>
      <div class="collect-search fr">
        <bk-input
          data-test-id="logCollectionBox_input_searchCollectionItems"
          :placeholder="$t('搜索名称、存储索引名')"
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          @change="handleSearchChange"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="collect-list">
      <bk-table
        class="collect-table"
        data-test-id="logCollectionBox_table_logCollectionTable"
        v-bkloading="{ isLoading: isTableLoading }"
        ref="collectTable"
        :empty-text="$t('暂无内容')"
        :data="collectList"
        :size="size"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column
          v-if="checkcFields('bk_data_id')"
          :label="$t('数据ID')"
          min-width="60">
          <template slot-scope="props">
            <span>
              {{ props.row.bk_data_id || '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('名称')" min-width="90">
          <template slot-scope="props">
            <span
              class="text-active"
              v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.VIEW_COLLECTION_AUTH]) }"
              @click="operateHandler(props.row, 'view')">
              {{ props.row.collector_config_name }}
            </span>
            <span
              v-if="!props.row.table_id"
              class="table-mark mark-mini mark-default">
              {{ $t('未完成') }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('table_id')"
          :label="$t('存储名')"
          min-width="80">
          <template slot-scope="props">
            <span
              :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.table_id ? props.row.table_id_prefix + props.row.table_id : '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('storage_cluster_name')"
          :label="$t('存储集群')"
          min-width="70">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.storage_cluster_name || '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('collector_scenario_name')"
          :label="$t('日志类型')"
          min-width="50"
          class-name="filter-column"
          prop="collector_scenario_id"
          column-key="collector_scenario_id"
          :filters="checkcFields('collector_scenario_name') ? scenarioFilters : []"
          :filter-method="scenarioFiltersMethod"
          :filter-multiple="false">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.collector_scenario_name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('category_name')"
          :label="$t('数据类型')"
          min-width="50"
          class-name="filter-column"
          prop="category_id"
          column-key="category_id"
          :filters="checkcFields('category_name') ? categoryFilters : []"
          :filter-method="categoryFiltersMethod"
          :filter-multiple="false">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.category_name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('retention')"
          :label="$t('过期时间')"
          min-width="50">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">
              {{ props.row.retention ? `${props.row.retention}${$t('天')}` : '--' }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('es_host_state')"
          :class-name="'td-status'"
          :label="$t('采集状态')"
          min-width="55">
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
                <span
                  v-else
                  :class="['status', 'status-' + props.row.status, { 'cursor-disabled': !loadingStatus }]">
                  <span v-if="props.row.status">
                    <i class="icon-circle"></i>
                    {{ props.row.status_name || '--' }}
                  </span>
                  <span class="status status-running" v-if="props.row.status === ''">
                    <i class="bk-icon icon-refresh"></i>
                  </span>
                </span>
              </div>
              <div slot="content" style="padding: 7px 6px;">
                <span style="color: #d2d5dd;">
                  {{ $t('点击查看') }}
                </span>{{ $t('采集状态') }}
              </div>
            </bk-popover>
            <div
              v-else
              v-cursor="{
                active: !(props.row.permission &&
                  props.row.permission[authorityMap.VIEW_COLLECTION_AUTH]) &&
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
                  <i class="icon-circle"></i>
                  {{ props.row.status_name || '--' }}
                </span>
                <span class="status status-running" v-if="props.row.status === ''">
                  <i class="bk-icon icon-refresh"></i>
                </span>
              </span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('updated_by')"
          :label="$t('更新人')"
          min-width="55">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">{{ props.row.updated_by }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('updated_at')"
          :label="$t('更新时间')"
          width="190">
          <template slot-scope="props">
            <span :class="{ 'text-disabled': props.row.status === 'stop' }">{{ props.row.updated_at }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" class-name="operate-column" width="160">
          <div class="collect-table-operate" slot-scope="props">
            <!-- 检索 -->
            <!-- 启用状态下 且存在 index_set_id 才能检索 -->
            <span
              class="king-button"
              v-bk-tooltips.top="{
                content: getDisabledTipsMessage(props.row, 'search'),
                disabled: !props.row.status
                  || !(!props.row.is_active || (!props.row.index_set_id && !props.row.bkdata_index_set_ids.length)),
                delay: 500,
              }">
              <bk-button
                theme="primary"
                text
                :disabled="!props.row.is_active || (!props.row.index_set_id && !props.row.bkdata_index_set_ids.length)"
                v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.SEARCH_LOG_AUTH]) }"
                @click="operateHandler(props.row, 'search')">
                {{ $t('检索') }}
              </bk-button>
            </span>
            <!-- 编辑 -->
            <bk-button
              theme="primary"
              text
              class="king-button"
              v-cursor="{
                active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
              }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <span v-bk-tooltips.top="{
              content: getDisabledTipsMessage(props.row, 'clean'),
              disabled: !props.row.status || props.row.table_id,
              delay: 500,
            }">
              <!-- 前往清洗 -->
              <bk-button
                theme="primary"
                text
                class="king-button"
                :disabled="!props.row.table_id"
                v-cursor="{
                  active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                }"
                @click.stop="operateHandler(props.row, 'clean')">
                {{ $t('前往清洗') }}
              </bk-button>
            </span>
            <bk-dropdown-menu ref="dropdown" align="right">
              <i
                class="bk-icon icon-more"
                style="margin-left: 5px; font-size: 14px; font-weight: bold;"
                slot="dropdown-trigger">
              </i>
              <ul class="bk-dropdown-list collection-operation-list" slot="dropdown-content">
                <!-- 查看详情 -->
                <li>
                  <a
                    href="javascript:;"
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.VIEW_COLLECTION_AUTH])
                    }"
                    @click="operateHandler(props.row, 'view')">
                    {{ $t('详情') }}
                  </a>
                </li>

                <li v-if="props.row.is_active">
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{$t('停用')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                    }"
                    @click.stop="operateHandler(props.row, 'stop')">{{$t('停用')}}</a>
                </li>
                <li v-else>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.status === 'prepare' ||
                      !collectProject">
                    {{$t('启用')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                    }"
                    @click.stop="operateHandler(props.row, 'start')">{{$t('启用')}}</a>
                </li>
                <li>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.status ||
                      props.row.status === 'running' ||
                      props.row.is_active ||
                      !collectProject"
                    v-bk-tooltips.top="{
                      content: getDisabledTipsMessage(props.row, 'delete'),
                      disabled: !props.row.status,
                      delay: 500,
                    }">
                    {{$t('删除')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                    }"
                    @click.stop="operateHandler(props.row, 'delete')">{{$t('删除')}}</a>
                </li>
                <!-- 存储设置 -->
                <li>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.table_id"
                    v-bk-tooltips.top="{
                      content: getDisabledTipsMessage(props.row, 'storage'),
                      disabled: !props.row.status || props.row.table_id,
                      delay: 500,
                    }">
                    {{$t('存储设置')}}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                    }"
                    @click.stop="operateHandler(props.row, 'storage')">{{$t('存储设置')}}</a>
                </li>
                <!-- 克隆 -->
                <li>
                  <a
                    href="javascript:;"
                    class="text-disabled"
                    v-if="!props.row.table_id"
                    v-bk-tooltips.top="{
                      content: getDisabledTipsMessage(props.row, 'clone'),
                      disabled: !props.row.status || props.row.table_id,
                      delay: 500,
                    }">
                    {{ $t('克隆') }}
                  </a>
                  <a
                    href="javascript:;"
                    v-else
                    v-cursor="{
                      active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                    }"
                    @click.stop="operateHandler(props.row, 'clone')">{{ $t('克隆') }}</a>
                </li>
                <li v-if="enableCheckCollector && props.row.environment === 'linux'">
                  <a href="javascript:;" @click.stop="handleShowReport(props.row)">
                    {{ $t('一键检测') }}
                  </a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </div>
        </bk-table-column>
        <bk-table-column type="setting">
          <bk-table-setting-content
            :fields="columnSetting.fields"
            :selected="columnSetting.selectedFields"
            :size="columnSetting.size"
            @setting-change="handleSettingChange">
          </bk-table-setting-content>
        </bk-table-column>
        <div slot="empty">
          <empty-status :empty-type="emptyType" @operation="handleOperation" />
        </div>
      </bk-table>
    </section>
    <collection-report-view
      v-model="reportDetailShow"
      :check-record-id="checkRecordId"
      @closeReport="() => reportDetailShow = false"
    />
  </section>
</template>

<script>
import { projectManages, clearTableFilter } from '@/common/util';
import collectedItemsMixin from '@/mixins/collected-items-mixin';
import { mapGetters } from 'vuex';
import * as authorityMap from '../../../../../common/authority-map';
import CollectionReportView from '../../components/collection-report-view';
import EmptyStatus from '../../../../../components/empty-status';

export default {
  name: 'CollectionItem',
  components: {
    CollectionReportView,
    EmptyStatus,
  },
  mixins: [collectedItemsMixin],
  data() {
    const settingFields = [
      // 数据ID
      {
        id: 'bk_data_id',
        label: this.$t('数据ID'),
      },
      // 采集配置名称
      {
        id: 'collector_config_name',
        label: this.$t('名称'),
        disabled: true,
      },
      // 存储名
      {
        id: 'table_id',
        label: this.$t('存储名'),
      },
      // 日志类型
      {
        id: 'collector_scenario_name',
        label: this.$t('日志类型'),
      },
      // 过期时间
      {
        id: 'retention',
        label: this.$t('过期时间'),
      },
      // 采集状态
      {
        id: 'es_host_state',
        label: this.$t('采集状态'),
      },
      // 更新人
      {
        id: 'updated_by',
        label: this.$t('更新人'),
      },
      // 更新时间
      {
        id: 'updated_at',
        label: this.$t('更新时间'),
      },
      // 操作
      {
        id: 'operation',
        label: this.$t('操作'),
        disabled: true,
      },
      // 存储集群
      {
        id: 'storage_cluster_name',
        label: this.$t('存储集群'),
      },
      // 数据类型
      {
        id: 'category_name',
        label: this.$t('数据类型'),
      },
    ];

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
      params: {
        keyword: '',
        collector_scenario_id: '',
        category_id: '',
      },
      isAllowedCreate: null,
      columnSetting: {
        fields: settingFields,
        selectedFields: settingFields.slice(1, 8),
      },
      // 是否支持一键检测
      enableCheckCollector: window.ENABLE_CHECK_COLLECTOR,
      // 一键检测弹窗配置
      reportDetailShow: false,
      // 一键检测采集项标识
      checkRecordId: '',
      emptyType: 'empty',
      filterSearchObj: {},
      isFilterSearch: false,
    };
  },
  computed: {
    ...mapGetters({
      spaceUid: 'spaceUid',
      bkBizId: 'bkBizId',
      authGlobalInfo: 'globals/authContainerInfo',
    }),
    ...mapGetters('globals', ['globalsData']),
    authorityMap() {
      return authorityMap;
    },
    scenarioFilters() {
      const { collector_scenario } = this.globalsData;
      const target = [];
      // eslint-disable-next-line camelcase
      collector_scenario && collector_scenario.forEach((data) => {
        if (data.is_active) {
          target.push({
            text: data.name,
            value: data.id,
          });
        }
      });
      return target;
    },
    categoryFilters() {
      const { category } = this.globalsData;
      const target = [];
      category && category.forEach((data) => {
        data.children.forEach((val) => {
          target.push({
            text: val.name,
            value: val.id,
          });
        });
      });
      return target;
    },
  },
  created() {
    !this.authGlobalInfo && this.checkCreateAuth();
  },
  mounted() {
    this.needGuide = !localStorage.getItem('needGuide');
    this.timerNum = 0;
    !this.authGlobalInfo && this.search();
  },
  destroyed() {
    this.timerNum = -1;
    this.stopStatusPolling();
  },
  methods: {
    handleSearchChange(val) {
      if (val === '' && !this.isTableLoading) {
        this.requestData();
      }
    },
    search() {
      this.pagination.current = 1;
      this.requestData();
    },
    checkcFields(field) {
      return this.columnSetting.selectedFields.some(item => item.id === field);
    },
    // 离开当前页路由操作
    leaveCurrentPage(row, operateType) {
      if (operateType === 'status' && (!this.loadingStatus || row.status === 'terminated')) return; // 已停用禁止操作
      if (operateType === 'status' && (!row.status || row.status === 'prepare')) {
        return this.operateHandler(row, 'edit');
      }
      // running、prepare 状态不能启用、停用
      if (operateType === 'start' || operateType === 'stop') {
        if (!this.loadingStatus || row.status === 'running' || row.status === 'prepare' || !this.collectProject) return;
        if (operateType === 'start') { // 启用
          this.toggleCollect(row);
        } else {
          // 如果是容器采集项则停用页显示状态页
          this.$router.push({
            name: 'collectStop',
            params: {
              collectorId: row.collector_config_id || '',
            },
            query: {
              spaceUid: this.$store.state.spaceUid,
            },
          });
        }
        return;
      }
      // running 状态不能删除
      if (operateType === 'delete') {
        if (!this.collectProject) return;
        if (!row.is_active && row.status !== 'running') {
          this.$bkInfo({
            type: 'warning',
            subTitle: this.$t('当前采集项名称为{n}，确认要删除？', { n: row.collector_config_name }),
            confirmFn: () => {
              this.requestDeleteCollect(row);
            },
          });
        }
        return;
      }

      let backRoute = undefined;
      const params = {};
      const query = {};
      const routeMap = {
        add: 'collectAdd',
        view: 'manage-collection',
        status: 'manage-collection',
        edit: 'collectEdit',
        field: 'collectField',
        search: 'retrieve',
        clean: 'clean-edit',
        storage: 'collectStorage',
        clone: 'collectAdd',
      };
      const targetRoute = routeMap[operateType];
      // 查看详情 - 如果处于未完成状态，应该跳转到编辑页面
      if (targetRoute === 'manage-collection') {
        if (!row.table_id) {
          return this.operateHandler(row, 'edit');
        }
      }
      if (['manage-collection', 'collectEdit', 'collectField', 'collectStorage'].includes(targetRoute)) {
        params.collectorId = row.collector_config_id;
      }
      if (operateType === 'status') {
        query.type = 'collectionStatus';
      }
      if (operateType === 'search') {
        if (!row.index_set_id && !row.bkdata_index_set_ids.length) return;
        params.indexId = row.index_set_id ? row.index_set_id : row.bkdata_index_set_ids[0];
      }
      if (operateType === 'clean') {
        params.collectorId = row.collector_config_id;
        if (row.itsm_ticket_status === 'applying') {
          return this.operateHandler(row, 'field');
        }
        backRoute = this.$route.name;
      }
      // 克隆操作需要ID进行数据回显
      if (operateType === 'clone') {
        params.collectorId = row.collector_config_id;
        query.collectorId = row.collector_config_id;
        query.type = 'clone';
      }
      this.$store.commit('collect/setCurCollect', row);
      this.$router.push({
        name: targetRoute,
        params,
        query: {
          ...query,
          spaceUid: this.$store.state.spaceUid,
          backRoute,
        },
      });
    },
    // 表头过滤
    handleFilterChange(data) {
      Object.keys(data).forEach((item) => {
        this.params[item] = data[item].join('');
      });
      Object.entries(data).forEach(([key, value]) => this.filterSearchObj[key] = value.length);
      this.isFilterSearch = Object.values(this.filterSearchObj).reduce((pre, cur) => ((pre += cur), pre), 0);
      this.search();
    },
    handleSettingChange({ fields }) {
      this.columnSetting.selectedFields = fields;
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
    scenarioFiltersMethod(value, row, column) {
      const property = column.property;
      return row[property] === value;
    },
    categoryFiltersMethod(value, row, column) {
      const property = column.property;
      return row[property] === value;
    },
    requestData() {
      this.isTableLoading = true;
      this.emptyType = (this.params.keyword || this.isFilterSearch) ? 'search-empty' : 'empty';
      this.$http.request('collect/getCollectList', {
        query: {
          bk_biz_id: this.bkBizId,
          keyword: this.params.keyword,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
          not_custom: 1,
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
        .catch(() => {
          this.emptyType = '500';
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    handleOperation(type) {
      if (type === 'clear-filter') {
        this.params.keyword = '';
        this.pagination.current = 1;
        clearTableFilter(this.$refs.collectTable);
        this.requestData();
        return;
      }

      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.pagination.current = 1;
        this.requestData();
        return;
      }
    },
    requestCollectList() {
      return new Promise((resolve, reject) => {
        this.$http.request('collect/getCollectList', {
          query: {
            ...this.params,
            bk_biz_id: this.bkBizId,
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
    // 启用
    toggleCollect(row) {
      const { isActive, status, statusName } = row;
      row.status = 'running';
      row.status_name = this.$t('部署中');
      this.$http.request('collect/startCollect', {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          row.is_active = !row.is_active;
          this.startStatusPolling();
        }
      })
        .catch(() => {
          row.is_active = isActive;
          row.status = status;
          row.status_name = statusName;
        });
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
    handleShowReport(row) {
      this.$http.request('collect/runCheck', {
        data: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.data?.check_record_id) {
          this.reportDetailShow = true;
          this.checkRecordId = res.data.check_record_id;
        }
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
    padding: 20px 24px;

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

      .filter-column {
        .cell {
          /* stylelint-disable-next-line declaration-no-important */
          display: flex !important;
        }
      }
    }

    .bk-table-body-wrapper {
      overflow: visible;
    }

    .operate-column .cell {
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

      .icon-circle {
        width: 5px;
        height: 5px;
        display: inline-block;
        border-radius: 50%;
        transform: translateY(-2px);

        &::before {
          content: '';
        }
      }

      &.status-running i {
        display: inline-block;
        animation: button-icon-loading 1s linear infinite;
      }

      &.status-success i {
        background: $iconSuccessColor;
      }

      &.status-failed i {
        background: $iconFailColor;
      }
    }

    .collect-table-operate {
      display: flex;
      align-items: center;

      .king-button {
        margin-right: 14px;

        &:last-child {
          margin-right: 0;
        }
      }
    }

    .bk-dropdown-list a.text-disabled:hover {
      color: #c4c6cc;
      cursor: not-allowed;
    }

    .collection-operation-list {
      max-height: 190px;
    }

    .collect-table-operate {
      display: flex;
    }

    .bk-dropdown-trigger {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }

  .bk-table-setting-popover-content-theme.tippy-tooltip {
    padding: 15px 0 0;

    .bk-table-setting-content .content-line-height {
      display: none;
    }
  }
</style>
