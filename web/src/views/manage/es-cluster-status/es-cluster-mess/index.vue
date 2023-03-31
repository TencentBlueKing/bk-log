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
  <div class="es-access-container" data-test-id="esAccess_div_esAccessBox" ref="accessContainerRef">
    <div class="es-cluster-list-container" :style="`width: calc(100% - ${ introWidth }px);`">
      <div class="main-operator-container">
        <bk-button
          theme="primary"
          style="width: 120px;"
          :disabled="isAllowedCreate === null || tableLoading"
          v-cursor="{ active: isAllowedCreate === false }"
          data-test-id="esAccessBox_button_addNewEsAccess"
          @click="addDataSource">{{ $t('新建') }}
        </bk-button>
        <bk-input
          v-model="params.keyword"
          style="width: 360px;float: right;"
          right-icon="bk-icon icon-search"
          data-test-id="esAccessBox_input_search"
          :placeholder="$t('搜索ES源名称，地址，创建人')"
          :clearable="true"
          @change="handleSearch">
        </bk-input>
      </div>
      <bk-table
        v-bkloading="{ isLoading: tableLoading }"
        data-test-id="esAccessBox_table_esAccessTableBox"
        class="king-table"
        ref="clusterTable"
        :data="tableDataPaged"
        :pagination="pagination"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column
          label="ID"
          :render-header="$renderHeader"
          prop="cluster_config.cluster_id"
          min-width="60">
        </bk-table-column>
        <bk-table-column
          :label="$t('名称')"
          :render-header="$renderHeader"
          prop="cluster_config.cluster_name"
          min-width="170">
        </bk-table-column>
        <bk-table-column :label="$t('地址')" :render-header="$renderHeader" min-width="170">
          <template slot-scope="props">
            {{ props.row.cluster_config.domain_name || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('source_type')"
          :label="$t('来源')"
          :render-header="$renderHeader"
          prop="source_type"
          min-width="80"
          class-name="filter-column"
          column-key="source_type"
          :filters="sourceFilters"
          :filter-multiple="false"
          :filter-method="sourceFilterMethod">
          <template slot-scope="props">
            {{ props.row.source_name || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('port')"
          :label="$t('端口')"
          :render-header="$renderHeader"
          prop="cluster_config.port"
          min-width="80">
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('schema')"
          :label="$t('协议')"
          :render-header="$renderHeader"
          prop="cluster_config.schema"
          min-width="80">
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('cluster_config')"
          :label="$t('连接状态')"
          :render-header="$renderHeader"
          min-width="80"
          class-name="filter-column"
          prop="cluster_config.cluster_id"
          column-key="cluster_config.cluster_id"
          :filters="sourceStateFilters"
          :filter-method="sourceStateFilterMethod"
          :filter-multiple="false">
          <template slot-scope="{ row }">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="state-container" v-html="getStateText(row.cluster_config.cluster_id)"></div>
          <!--eslint-enable-->
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('enable_hot_warm')"
          :label="$t('冷热数据')"
          :render-header="$renderHeader"
          min-width="80">
          <template slot-scope="{ row }">
            {{ row.cluster_config.enable_hot_warm ? $t('开') : $t('关') }}
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('storage_total')"
          width="90"
          :render-header="$renderHeader"
          :label="$t('总量')">
          <template slot-scope="{ row }">
            <span>{{formatFileSize(row.storage_total)}}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('storage_usage')"
          width="110"
          :render-header="$renderHeader"
          :label="$t('空闲率')">
          <template slot-scope="{ row }">
            <div class="percent">
              <div class="percent-progress">
                <bk-progress :theme="'success'" :show-text="false" :percent="getPercent(row)"></bk-progress>
              </div>
              <span>{{`${100 - row.storage_usage}%`}}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('creator')"
          :label="$t('创建人')"
          :render-header="$renderHeader"
          prop="cluster_config.creator"
          min-width="80">
        </bk-table-column>
        <bk-table-column
          v-if="checkcFields('create_time')"
          :label="$t('创建时间')"
          :render-header="$renderHeader"
          class-name="filter-column"
          prop="cluster_config.create_time"
          min-width="170"
          sortable>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" :render-header="$renderHeader" width="180">
          <template slot-scope="props">
            <!-- 共享集群，平台默认时 无法新建索引集 -->
            <log-button
              theme="primary"
              text
              class="mr10"
              :tips-conf="props.row.is_platform ? $t('公共集群，禁止创建自定义索引集') : $t('平台默认的集群不允许编辑和删除，请联系管理员。')"
              :button-text="$t('建索引集')"
              :disabled="!props.row.is_editable || props.row.is_platform"
              @on-click="createIndexSet(props.row)">>
            </log-button>
            <log-button
              theme="primary"
              text
              class="mr10"
              v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_ES_SOURCE_AUTH]) }"
              :tips-conf="$t('平台默认的集群不允许编辑和删除，请联系管理员。')"
              :button-text="$t('编辑')"
              :disabled="!props.row.is_editable"
              @on-click="editDataSource(props.row)">
            </log-button>
            <log-button
              theme="primary"
              text
              class="mr10"
              v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_ES_SOURCE_AUTH]) }"
              :tips-conf="$t('平台默认的集群不允许编辑和删除，请联系管理员。')"
              :button-text="$t('删除')"
              :disabled="!props.row.is_editable"
              @on-click="deleteDataSource(props.row)">
            </log-button>
          </template>
        </bk-table-column>
        <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
          <bk-table-setting-content
            :fields="clusterSetting.fields"
            :selected="clusterSetting.selectedFields"
            :max="clusterSetting.max"
            @setting-change="handleSettingChange">
          </bk-table-setting-content>
        </bk-table-column>
        <div slot="empty">
          <empty-status :empty-type="emptyType" @operation="handleOperation" />
        </div>
      </bk-table>
    </div>

    <div
      :class="['intro-container',isDraging && 'draging-move']"
      :style="`width: ${ introWidth }px`">
      <div :class="`drag-item ${!introWidth && 'hidden-drag'}`" :style="`right: ${introWidth - 18}px`">
        <span
          class="bk-icon icon-more"
          @mousedown.left="dragBegin"></span>
      </div>
      <intro-panel
        :is-open-window="isOpenWindow"
        @handleActiveDetails="handleActiveDetails" />
    </div>

    <!-- 编辑或新建ES源 -->
    <es-slider
      v-if="isRenderSlider"
      :show-slider.sync="showSlider"
      :edit-cluster-id="editClusterId"
      @hidden="handleSliderHidden"
      @updated="handleUpdated" />

  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import EsSlider from './es-slider';
import IntroPanel from './components/intro-panel.vue';
import dragMixin from '@/mixins/drag-mixin';
import { formatFileSize, clearTableFilter } from '../../../../common/util';
import * as authorityMap from '../../../../common/authority-map';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'EsClusterMess',
  components: {
    EsSlider,
    IntroPanel,
    EmptyStatus,
  },
  mixins: [dragMixin],
  data() {
    const settingFields = [
      // 数据ID
      {
        id: 'cluster_id',
        label: 'ID',
        disabled: true,
      },
      // 集群名称
      {
        id: 'collector_config_name',
        label: this.$t('名称'),
        disabled: true,
      },
      // 地址
      {
        id: 'domain_name',
        label: this.$t('地址'),
        disabled: true,
      },
      // 来源
      {
        id: 'source_type',
        label: this.$t('来源'),
      },
      // 端口
      {
        id: 'port',
        label: this.$t('端口'),
      },
      // 协议
      {
        id: 'schema',
        label: this.$t('协议'),
      },
      // 连接状态
      {
        id: 'cluster_config',
        label: this.$t('连接状态'),
      },
      // 冷热数据
      {
        id: 'enable_hot_warm',
        label: this.$t('冷热数据'),
      },
      // 总量
      {
        id: 'storage_total',
        label: this.$t('总量'),
      },
      // 空闲率
      {
        id: 'storage_usage',
        label: this.$t('空闲率'),
      },
      // 创建人
      {
        id: 'creator',
        label: this.$t('创建人'),
      },
      // 创建时间
      {
        id: 'create_time',
        label: this.$t('创建时间'),
      },
    ];
    return {
      tableLoading: true,
      tableDataOrigin: [], // 原始数据
      tableDataSearched: [], // 搜索过滤数据
      tableDataPaged: [], // 前端分页
      pagination: {
        count: 0,
        limit: 10,
        current: 1,
      },
      stateMap: {},
      params: {
        keyword: '',
      },
      isAllowedCreate: null, // 是否有权限新建
      isRenderSlider: true, // 渲染侧边栏组件，关闭侧滑时销毁组件，避免接口在 pending 时关闭侧滑后又马上打开
      showSlider: false, // 显示编辑或新建ES源侧边栏
      editClusterId: null, // 编辑ES源ID,
      isOpenWindow: false,
      sourceStateFilters: [{ text: this.$t('正常'), value: true }, { text: this.$t('失败'), value: false }],
      clusterSetting: {
        fields: settingFields,
        selectedFields: settingFields.slice(0, 10),
      },
      introWidth: 0,
      emptyType: 'empty',
      filterSearchObj: {},
      isFilterSearch: false,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      spaceUid: 'spaceUid',
      globalsData: 'globals/globalsData',
    }),
    authorityMap() {
      return authorityMap;
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
    this.checkCreateAuth();
    this.getTableData();
    this.formatFileSize = formatFileSize;
    this.$nextTick(() => {
      this.maxIntroWidth = this.$refs.accessContainerRef.clientWidth - 580;
    });
  },
  methods: {
    async checkCreateAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: [authorityMap.CREATE_ES_SOURCE_AUTH],
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
     * 获取存储集群列表
     */
    async getTableData() {
      try {
        this.tableLoading = true;// 表格数据
        const tableRes = await this.$http.request('/source/list', {
          query: {
            bk_biz_id: this.bkBizId,
          },
        });
        this.tableLoading = false;
        const list = tableRes.data;
        if (!list.length) return;
        // 生成并赋值ipv6精简模式
        list.forEach((item) => {
          item.shortIp = this.shortenIPv6Address(item.cluster_config.domain_name);
        });
        this.tableDataOrigin = list;
        this.tableDataSearched = list;
        this.pagination.count = list.length;
        this.computePageData();
        // 连接状态
        try {
          const stateRes = await this.$http.request('/source/connectionStatus', {
            query: {
              bk_biz_id: this.bkBizId,
            },
            data: {
              cluster_list: list.map(item => item.cluster_config.cluster_id),
            },
          });
          this.stateMap = stateRes.data;
        } catch (e) {
          console.warn(e);
          this.stateMap = {};
        }
      } catch (e) {
        console.warn(e);
        this.tableLoading = false;
        this.tableDataOrigin.splice(0);
        this.tableDataSearched.splice(0);
        this.pagination.count = 0;
      }
    },
    getStateText(id) {
      const info = this.stateMap[id]; // 兼容接口布尔值和对象
      const state = (typeof info === 'boolean') ? info : info?.status;
      if (state === true) {
        return `<span class="bk-badge bk-danger"></span> ${this.$t('正常')}`;
      } if (state === false) {
        return `<span class="bk-badge bk-warning"></span> ${this.$t('失败')}`;
      }
      return '--';
    },
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.computePageData();
      }
    },
    handleLimitChange(limit) {
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.computePageData();
    },
    // 搜索ES源名称，地址，创建人
    handleSearch() {
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(this.searchCallback, 300);
    },
    // 来源过滤
    sourceFilterMethod(value, row, column) {
      const property = column.property;
      this.handlePageChange(1);
      return row[property] === value;
    },
    searchCallback() {
      const keyword = this.params.keyword.trim();
      if (keyword) {
        this.tableDataSearched = this.tableDataOrigin.filter((item) => {
          if (item.cluster_config.cluster_name) {
            return (item.cluster_config.cluster_name
                      + item.cluster_config.creator
                      + item.cluster_config.domain_name // 原始ipv6或ipv4 shotIP为精简后的ipv6地址
                      + item.shortIp).includes(keyword);
          }
          return (item.source_name + item.updated_by).includes(keyword);
        });
      } else {
        this.tableDataSearched = this.tableDataOrigin;
      }
      this.emptyType = (this.params.keyword || this.isFilterSearch) ? 'search-empty' : 'empty';
      this.pagination.current = 1;
      this.pagination.count = this.tableDataSearched.length;
      this.computePageData();
    },
    // ipv6精简
    shortenIPv6Address(ipv6) {
      // 检查是否为IPv4地址，如果是，则返回空字符串 搜索时直接使用原始domain_name
      if (ipv6.includes('.')) return '';

      // 将IPv6地址按冒号分隔成数组
      const parts = ipv6.split(':');
      let zeroes = 0;
      let output = '';

      // 找到所有连续的0，并计算需要缩短的位数
      for (const partItem of parts) {
        if (partItem === '0000') {
          zeroes += 1;
        } else {
          if (zeroes > 0) {
            output += ':';
            zeroes = 0;
          }
          output += `${partItem}:`;
        }
      }

      // 如果末尾有连续的0，需要再加一个冒号
      if (zeroes > 0) output += ':';

      // 返回缩短后的IPv6地址
      return output.replace(/(^|:)0(:0)*(:|$)/, '::');
    },
    // 根据分页数据过滤表格
    computePageData() {
      const { current, limit } = this.pagination;
      const start = (current - 1) * limit;
      const end = this.pagination.current * this.pagination.limit;
      this.tableDataPaged = this.tableDataSearched.slice(start, end);
    },
    // 新建ES源
    async addDataSource() {
      if (this.isAllowedCreate) {
        this.showSlider = true;
        this.editClusterId = null;
      } else {
        try {
          this.tableLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: [authorityMap.CREATE_ES_SOURCE_AUTH],
            resources: [{
              type: 'space',
              id: this.spaceUid,
            }],
          });
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.tableLoading = false;
        }
      }
    },
    // 建索引集
    createIndexSet(row) {
      this.$router.push({
        name: 'es-index-set-create',
        query: {
          spaceUid: this.$store.state.spaceUid,
          cluster: row.cluster_config.cluster_id,
        },
      });
    },
    // 编辑ES源
    async editDataSource(item) {
      const id = item.cluster_config.cluster_id;
      if (!(item.permission?.[authorityMap.MANAGE_ES_SOURCE_AUTH])) {
        try {
          const paramData = {
            action_ids: [authorityMap.MANAGE_ES_SOURCE_AUTH],
            resources: [{
              type: 'es_source',
              id,
            }],
          };
          this.tableLoading = true;
          const res = await this.$store.dispatch('getApplyData', paramData);
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.tableLoading = false;
        }
        return;
      }

      this.showSlider = true;
      this.editClusterId = id;
    },
    // 删除ES源
    async deleteDataSource(row) {
      const id = row.cluster_config.cluster_id;
      if (!(row.permission?.[authorityMap.MANAGE_ES_SOURCE_AUTH])) {
        try {
          const paramData = {
            action_ids: [authorityMap.MANAGE_ES_SOURCE_AUTH],
            resources: [{
              type: 'es_source',
              id,
            }],
          };
          this.tableLoading = true;
          const res = await this.$store.dispatch('getApplyData', paramData);
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.tableLoading = false;
        }
        return;
      }

      this.$bkInfo({
        type: 'warning',
        subTitle: this.$t('当前集群为{n}，确认要删除？', { n: row.cluster_config.domain_name }),
        confirmFn: () => {
          this.handleDelete(row);
        },
      });
    },
    handleDelete(row) {
      this.$http.request('source/deleteEs', {
        params: {
          bk_biz_id: this.bkBizId,
          cluster_id: row.cluster_config.cluster_id,
        },
      }).then((res) => {
        if (res.result) {
          if (this.tableDataPaged.length <= 1) {
            this.pagination.current = this.pagination.current > 1 ? this.pagination.current - 1 : 1;
          }
          const deleteIndex = this.tableDataSearched.findIndex((item) => {
            return item.cluster_config.cluster_id === row.cluster_config.cluster_id;
          });
          this.tableDataSearched.splice(deleteIndex, 1);
          this.computePageData();
        }
      })
        .catch(() => {});
    },
    // 新建、编辑源更新
    handleUpdated() {
      this.showSlider = false;
      this.pagination.count = 1;
      this.getTableData();
    },
    handleSliderHidden() {
      this.isRenderSlider = false;
      this.$nextTick(() => {
        this.isRenderSlider = true;
      });
    },
    handleSettingChange({ fields }) {
      this.clusterSetting.selectedFields = fields;
    },
    handleActiveDetails(state) {
      this.isOpenWindow = state;
      this.introWidth = state ? 360 : 0;
    },
    // 状态过滤
    sourceStateFilterMethod(value, row) {
      const info = this.stateMap[row.cluster_config.cluster_id]; // 兼容接口布尔值和对象
      const state = (typeof info === 'boolean') ? info : info?.status;
      return state === value;
    },
    checkcFields(field) {
      return this.clusterSetting.selectedFields.some(item => item.id === field);
    },
    getPercent($row) {
      return (100 - $row.storage_usage) / 100;
    },
    handleFilterChange(data) {
      Object.entries(data).forEach(([key, value]) => this.filterSearchObj[key] = value.length);
      this.isFilterSearch = Object.values(this.filterSearchObj).reduce((pre, cur) => ((pre += cur), pre), 0);
      this.searchCallback();
    },
    handleOperation(type) {
      if (type === 'clear-filter') {
        this.params.keyword = '';
        clearTableFilter(this.$refs.clusterTable);
        this.getTableData();
        return;
      }

      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.getTableData();
        return;
      }
    },
  },
};
</script>

<style lang="scss">
  .es-access-container {
    transition: padding .5s;
    position: relative;
    display: flex;
    justify-content: space-between;

    .main-operator-container {
      margin-bottom: 20px;
    }

    .king-table {
      .state-container {
        display: flex;
        align-items: center;

        .bk-badge {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          margin-right: 4px;
        }

        .bk-danger {
          background-color: #2dcb56;
        }

        .bk-warning {
          background-color: #ea3636;
        }
      }

      :deep(.cell) {
        padding: 4px 15px;
      }

      .filter-column {
        .cell {
          display: flex;
        }
      }
    }

    .es-cluster-list-container {
      padding: 20px 24px;
    }

    .intro-container {
      position: relative;
      top: 2px;
      width: 400px;
      height: calc(100vh - 104px);
      overflow: hidden;
      border-left: 1px solid transparent;

      &.draging-move {
        border-left-color: #3a84ff;
      }
    }

    .drag-item {
      width: 20px;
      height: 40px;
      display: inline-block;
      color: #c4c6cc;
      position: absolute;
      z-index: 99;
      right: 304px;
      top: 48%;
      user-select: none;
      cursor: col-resize;

      &.hidden-drag {
        display: none;
      }

      .icon-more::after {
        content: '\e189';
        position: absolute;
        left: 0;
        top: 12px;
      }
    }

    .percent {
      display: flex;
      align-items: center;

      .percent-progress {
        width: 40px;
        margin-right: 4px;
      }
    }
  }

  .bk-table-setting-popover-content-theme.tippy-tooltip {
    padding: 15px 0 0;

    .bk-table-setting-content .content-line-height {
      display: none;
    }
  }
</style>
