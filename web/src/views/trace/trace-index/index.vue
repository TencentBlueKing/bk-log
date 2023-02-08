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
  <div id="trace" v-bkloading="{ isLoading: false }">
    <top-nav :menu="menu"></top-nav>
    <div class="trace-container">
      <div class="search">
        <div class="search-item">
          <div class="search-trace">
            <div class="text-item">{{$t('indexSetList.index_set')}}</div>
            <bk-select
              class="search-area fl"
              style="width: 300px"
              :searchable="true"
              :clearable="false"
              v-model="indexId"
              @selected="changeIndexSet">
              <bk-option
                v-for="item in indexSetList"
                class="custom-no-padding-option"
                :key="item.index_set_id"
                :id="item.index_set_id"
                :name="item.computedName">
                <div
                  v-if="!(item.permission && item.permission[authorityMap.SEARCH_LOG_AUTH])"
                  class="option-slot-container no-authority"
                  @click.stop>
                  <span class="text">{{item.computedName}}</span>
                  <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
                </div>
                <div v-else class="option-slot-container">
                  {{item.computedName}}
                </div>
              </bk-option>
            </bk-select>
          </div>
          <div class="search-trace">
            <div class="text-item">{{$t('trace.time_quantum')}}</div>
            <bk-date-picker
              class="search-area fl"
              style="width: 300px"
              :clearable="false"
              :editable="true"
              :open="openDatePanel"
              :shortcuts="shortcuts"
              :type="'datetimerange'"
              :value="initDateTimeRange"
              format="yyyy-MM-dd HH:mm:ss"
              @change="dateChange"
              @open-change="openChange">
              <div v-if="showShortText" slot="trigger" @click.stop="openChange(!openDatePanel)">
                <div :class="['bk-date-picker-editor short-text', { 'is-focus': openDatePanel }]">
                  {{showShortText}}
                </div>
                <div class="icon-wrapper">
                  <span
                    class="log-icon icon-date-picker"
                    style="font-size: 18px;position: absolute;left: 7px;top: 7px;color: #979ba5;">
                  </span>
                </div>
              </div>
            </bk-date-picker>
          </div>
          <div class="search-trace" v-for="(val, ind) in traceData.additions" :key="ind">
            <div class="text-item">{{val.fields_alias}}</div>
            <bk-select
              v-if="val.show_type === 'select'"
              class="search-area fl"
              :searchable="true"
              :clearable="true"
              show-select-all
              v-model="searchData[val.field_name]">
              <bk-option
                v-for="option in docCountList[val.field_name]"
                :key="option"
                :id="option"
                :name="option">
              </bk-option>
            </bk-select>
            <bk-input
              v-else
              :type="val.show_type" style="width: 170px; margin-top: 8px;"
              :placeholder="$t('form.pleaseEnter')"
              v-model="searchData[val.field_name]"
              @enter="searchHandle">
            </bk-input>
            <div
              class="more-text"
              @click="moreTime = !moreTime"
              v-if="ind === traceData.additions.length - 1">
              {{$t('dataManage.more')}}
              <i class="bk-icon icon-down-shape" v-if="!moreTime"></i>
              <i class="bk-icon icon-up-shape" v-else></i>
            </div>
          </div>
        </div>
        <div class="search-time" :style="moreTime ? '' : 'display: none'">
          <!-- eslint-disable -->
          <div
            class="duration"
            v-for="(val,key) in traceData.advance_additions"
            :key="key"
            v-if="val.field_name === 'duration'">
            <!--eslint-enable-->
            <div>{{val.fields_alias}}（ms）</div>
            <div>
              <bk-input
                type="number"
                style="width: 100px; margin: 10px 0 0 0;"
                :placeholder="$t('form.pleaseEnter')"
                v-model="searchData.duration_gte"
                @enter="searchHandle"></bk-input>
              <div style="line-height: 30px;padding-top: 10px">{{$t('trace.to')}}</div>
              <bk-input
                type="number"
                style="width: 100px; margin: 10px 0 0 0;"
                :placeholder="$t('form.pleaseEnter')"
                v-model="searchData.duration_lte"
                @enter="searchHandle"></bk-input>
            </div>
          </div>
          <!-- eslint-disable -->
          <div
            class="code"
            v-for="(val,key) in traceData.advance_additions"
            :key="key"
            v-if="val.field_name !== 'duration'">
            <!--eslint-enable-->
            <div style="margin-bottom: 10px;">{{val.fields_alias}}</div>
            <bk-select
              v-if="val.show_type === 'select'"
              class="search-area fl"
              :searchable="true"
              :clearable="true"
              show-select-all
              v-model="searchData[val.field_name]">
              <bk-option
                v-for="(option, index) in docCountList[val.field_name]"
                :key="index"
                :id="option"
                :name="option">
              </bk-option>
            </bk-select>
            <bk-input
              v-else
              :type="val.show_type" style="width: 170px; margin-top: 8px;"
              :placeholder="$t('form.pleaseEnter')"
              v-model="searchData[val.field_name]"
              @enter="searchHandle">
            </bk-input>
          </div>
        </div>
        <div class="search-keyword">
          <div>{{$t('alarmStrategy.additions')}}</div>
          <div style="font-size: 0;">
            <input
              type="text"
              class="bk-form-input" style="width: calc(100% - 90px);"
              placeholder="Traceid / Spanid / Tag / Log"
              v-model="params.keyword"
              @keyup.enter="searchHandle">
            <bk-button
              class="search-detail-button"
              theme="primary"
              :disabled="searchDisabled || !!authPageInfo"
              v-cursor="{ active: isSearchAllowed === false }"
              @click="searchHandle">
              {{$t('btn.search')}}
            </bk-button>
          </div>
        </div>
      </div>
      <div style="border-bottom: 1px solid #dcdee5;">
        <auth-container-page
          style="margin-top: 50px"
          v-if="authPageInfo"
          :info="authPageInfo">
        </auth-container-page>
        <template v-else>
          <div
            class="chart-view"
            v-if="traceData.charts.length"
            v-bkloading="{ isLoading: isChartLoading, zIndex: 1 }">
            <div class="chart-click">
              <span
                v-for="(val, key) in traceData.charts" :key="key"
                :class="fieldName === val.field_name && 'click-color'"
                @click="handleCheckChartType(val)"
              >{{val.tips}}</span>
            </div>
            <chartView
              :chart-data="chartData"
              :field-name="fieldName"
              :char-dot-data="charDotData"
              :initial-call="initialCall"
              :initial-call-show="initialCallShow"
              :chart-cut="chartCut === 'line' ? 'line' : 'consuming'"
              @toggle-call-show="handleToggleCallShow"></chartView>
          </div>
          <div class="table-search" v-bkloading="{ isLoading: isTableLoading, zIndex: 1 }">
            <div class="log-switch">
              <time-formatter></time-formatter>
            </div>
            <bk-table
              style="margin-top: 15px;"
              v-if="loaded"
              ref="logDetailTable"
              :empty-text="$t('retrieve.notData')"
              :data="logTableList"
              :size="size"
              @cell-click="handleCellClick">
              <template v-if="logTableList.length">
                <!-- 展开详情 -->
                <bk-table-column type="expand" width="30" align="center">
                  <template slot-scope="item">
                    <div class="json-view-wrapper">
                      <VueJsonPretty :deep="5" :data="logAllJsonList[item.$index]" />
                    </div>
                  </template>
                </bk-table-column>
                <!-- 显示字段 -->
                <template v-for="(field, index) in visibleFieldsInfo">
                  <bk-table-column
                    v-if="field.field_name === 'tag.error'" :key="field.field_name"
                    :label="field.field_alias || field.field_name">
                    <div slot-scope="{ row }">
                      <table-status :is-error="Boolean(row.tag.error)"></table-status>
                    </div>
                  </bk-table-column>
                  <bk-table-column
                    :key="index"
                    :label="field.field_alias ? field.field_alias : field.field_name"
                    :min-width="field.minWidth" v-else-if="field.field_name === 'traceID'">
                    <template slot-scope="item">
                      <div class="td-log-container">
                        <span v-if="tableRowDeepView(item.row, field.field_name)">
                          <span style="color: #3a84ff;cursor: pointer;">{{item.row.traceID}}</span>
                        </span>
                      </div>
                    </template>
                  </bk-table-column>
                  <bk-table-column
                    :key="index"
                    :label="field.field_alias ? field.field_alias : field.field_name"
                    :min-width="field.minWidth" v-else>
                    <template slot-scope="{ row }">
                      <div class="td-log-container">
                        <span class="field-container add-to">
                          {{tableRowDeepView(row, field.field_name, field.field_type)}}
                        </span>
                      </div>
                    </template>
                  </bk-table-column>
                </template>
              </template>
            </bk-table>
          </div>
        </template>
      </div>
    </div>
    <div class="fixed-scroll-top-btn" v-show="isShowScrollTop" @click="scrollToTop">
      <i class="bk-icon icon-angle-up"></i>
    </div>
    <trace-detail
      :is-show.sync="showTraceDetail"
      :trace-id="traceId"
      :index-set-name="indexSetName" />
  </div>
</template>

<script>
import topNav from '@/components/nav/top-nav';
import AuthContainerPage from '@/components/common/auth-container-page';
import TableStatus from '@/components/common/table-status';
import { mapState, mapGetters } from 'vuex';
import chartView from './chart-view.vue';
import TimeFormatter from '@/components/common/time-formatter';
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';
import TraceDetail from '@/components/trace-detail';
import * as authorityMap from '../../../common/authority-map';

export default {
  name: 'TraceIndex',
  components: {
    topNav,
    AuthContainerPage,
    TableStatus,
    chartView,
    TimeFormatter,
    TraceDetail,
  },
  mixins: [tableRowDeepViewMixin],
  data() {
    return {
      authPageInfo: null,
      traceData: {
        additions: [],
        advance_additions: [],
        charts: [],
      },
      chartData: {},
      fieldName: '',
      charDotData: {},
      timeZone: '',
      basicLoading: false,
      isChartLoading: false,
      isTableLoading: true,
      docCountList: {},
      searchData: {},
      messagetop: {
        content: this.$t('trace.Method_calc'),
        showOnInit: false,
        placements: ['top'],
      },
      logAllJsonList: [],
      initialCall: false,
      initialCallShow: false,
      Scatter: false,
      tableRowsWidth: {},
      moreTime: false,
      size: 'small',
      startTime: '',
      menu: { name: this.$t('调用链'), id: 'trace', level: 1 },
      indexSetList: [],
      indexId: '',
      openDatePanel: false,
      initDateTimeRange: [],
      showShortText: this.$t('retrieve.period_15Min'),
      searchDisabled: false,
      chartCut: 'line',
      shortcuts: [
        {
          text: this.$t('retrieve.period_5S'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 5 * 1000);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_5S');
          },
        },
        {
          text: this.$t('retrieve.period_5Min'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 5 * 60);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_5Min');
          },
        },
        {
          text: this.$t('retrieve.period_15Min'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 15 * 60);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_15Min');
          },
        },
        {
          text: this.$t('retrieve.period_30Min'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 30 * 60);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_30Min');
          },
        },
        {
          text: this.$t('retrieve.period_1H'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_1H');
          },
        },
        {
          text: this.$t('retrieve.period_4H'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 4);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_4H');
          },
        },
        {
          text: this.$t('retrieve.period_12H'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 12);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_12H');
          },
        },
        {
          text: this.$t('retrieve.period_1D'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 24);
            return [start, end];
          },
          onClick: () => {
            this.showShortText = this.$t('retrieve.period_1D');
          },
        },
      ],
      loaded: true,
      logTableList: [],
      settingSort: [],
      // 表格所有字段
      totalFields: [],
      // 显示的字段的名字
      visibleFieldsName: [],
      // 显示字段的信息
      visibleFieldsInfo: [],
      // 设置排序权重
      sortFields: [],
      logAllTableList: {},
      isShowScrollTop: false,
      totalCount: 0, // 后端搜索结果总条数
      throttle: false, // 滚动节流 是否进入cd
      isPageOver: false, // 前端分页加载是否结束
      dataListPaged: [], // 将列表数据按 pageSize 分页
      count: 0, // 数据总条数
      pageSize: 30, // 每页展示多少数据
      totalPage: 1,
      currentPage: 0, // 当前加载了多少页
      params: {
        start_time: '',
        end_time: '',
        time_range: '15m',
        keyword: '*',
        addition: [],
        begin: 0,
        size: 20,
      },
      isSearchAllowed: null,
      showTraceDetail: false,
      traceId: '',
      indexSetName: '',
    };
  },
  computed: {
    ...mapState({
      spaceUid: state => state.spaceUid,
      bkBizId: state => state.bkBizId,
      indexIdCache: state => state.traceIndexId,
    }),
    ...mapGetters({
      authGlobalInfo: 'globals/authContainerInfo',
    }),
    authorityMap() {
      return authorityMap;
    },
  },
  watch: {
    indexId(val) {
      const option = this.indexSetList.find(item => item.index_set_id === val);
      // eslint-disable-next-line camelcase
      this.isSearchAllowed = Boolean(option?.permission?.[authorityMap.SEARCH_LOG_AUTH]);
      this.searchData = {};
      this.totalFields = [];
      this.initDateTime();
      this.searchHandle();
      this.$store.commit('updateTraceIndexId', this.indexId);
    },
    '$route.query.spaceUid'() {
      this.initDateTime();
      this.$nextTick(() => this.getIndexSet());
    },
    showShortText(val) {
      if (!val && val !== 0) {
        this.params.time_range = 'customized';
      } else {
        const timerInfo = {};
        timerInfo[this.$t('retrieve.period_5S')] = '5s';
        timerInfo[this.$t('retrieve.period_5Min')] = '5m';
        timerInfo[this.$t('retrieve.period_15Min')] = '15m';
        timerInfo[this.$t('retrieve.period_30Min')] = '30m';
        timerInfo[this.$t('retrieve.period_1H')] = '1h';
        timerInfo[this.$t('retrieve.period_4H')] = '4h';
        timerInfo[this.$t('retrieve.period_12H')] = '12h';
        timerInfo[this.$t('retrieve.period_1D')] = '1d';
        this.params.time_range = timerInfo[val];
      }
    },
  },
  created() {
    !this.authGlobalInfo && this.getIndexSet();
  },
  mounted() {
    this.registerScrollEvent();
    this.timeZone = new Date().toString()
      .substr(24, 32)
      .substr(0, 9);
  },
  methods: {
    changeIndexSet(newValue) {
      // 切换索引集
      this.indexId = newValue;
      this.$router.push({
        params: {
          indexId: this.indexId,
        },
        query: {
          bizId: this.bkBizId,
        },
      });
    },
    // 申请索引集的搜索权限
    async applySearchAccess(item) {
      this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.SEARCH_LOG_AUTH],
          resources: [{
            type: 'indices',
            id: item.index_set_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    initDateTime() {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 1000 * 15 * 60);
      this.initDateTimeRange = [this.switchTimeFormat(start), this.switchTimeFormat(end)];
      this.params.start_time = this.initDateTimeRange[0];
      this.params.end_time = this.initDateTimeRange[1];
      this.params.time_range = '15m';
    },
    switchTimeFormat(time) {
      const dateTime = new Date(time);
      const year = dateTime.getFullYear();
      const month = dateTime.getMonth() + 1;
      const date = dateTime.getDate();
      const hour = dateTime.getHours();
      const minute = dateTime.getMinutes();
      const second = dateTime.getSeconds();
      // eslint-disable-next-line max-len
      return `${year}-${this.addZero(month)}-${this.addZero(date)} ${this.addZero(hour)}:${this.addZero(minute)}:${this.addZero(second)}`;
    },
    addZero(v) {
      return v < 10 ? `0${v}` : v;
    },
    dateChange(data, type) {
      this.initDateTimeRange = data;
      if (type === 'date' || type === 'time' || type === 'datetimerange' || type) {
        this.showShortText = '';
      }
    },
    handleCellClick(row, column) {
      if (column.label === 'traceID') {
        // const routeData = this.$router.resolve({
        //   path: `/trace?indexId=${this.indexId}&traceId=${row.traceID}&startTime=${row.startTime}`,
        //   query: {
        //     spaceUid: this.spaceUid,
        //   },
        // });
        // window.open(routeData.href, '_blank');
        const option = this.indexSetList.find(item => item.index_set_id === this.indexId);
        this.showTraceDetail = true;
        this.traceId = row.traceID;
        this.indexSetName = option.index_set_name;
      } else {
        this.$refs.logDetailTable.toggleRowExpansion(row);
      }
    },
    openChange(data) {
      this.openDatePanel = data;
    },
    scrollToTop() {
      this.$easeScroll(0, 300, this.searchContentEl);
    },
    async getFieldsInfo() {
      const res = await this.$http.request('trace/getLogTableHead', {
        params: { index_set_id: this.indexId },
        mock: false,
        manualSchema: true,
      });
      const { fields: totalFields, display_fields: displayFields, sort_list: sortFields, trace: traceData } = res.data;
      totalFields.forEach((field) => {
        field.minWidth = 0; // field.minWidth = field.field_type === 'date' ? 200 : 300
      });
      const visibleFieldsName = this.filterVisibleName(displayFields, totalFields);
      const visibleFieldsInfo = this.filterVisibleInfo(visibleFieldsName, totalFields);
      return { totalFields, sortFields, visibleFieldsName, visibleFieldsInfo, traceData };
    },
    filterVisibleName(displayFields, totalFields) {
      // 后台给的 display_fields 可能有无效字段 所以进行过滤，获得排序后的字段名字数组
      return displayFields.filter((name) => {
        for (let i = 0; i < totalFields.length; i++) {
          if (totalFields[i].field_name === name) {
            return true;
          }
        }
        return false;
      });
    },
    filterVisibleInfo(visibleName, totalField) {
      // 获取排序后的字段对象数组
      return visibleName.map((name) => {
        for (let i = 0; i < totalField.length; i++) {
          if (totalField[i].field_name === name) {
            return totalField[i];
          }
        }
      });
    },
    async getIndexSet() {
      this.authPageInfo = null;
      this.basicLoading = true;
      try {
        const res = await this.$http.request('trace/getIndexSet', {
          query: { bk_biz_id: this.bkBizId },
          mock: false,
          manualSchema: true,
        });
        if (res.data.length) {
          res.data.forEach((item) => {
            item.computedName = `${item.index_set_name}(${item.indices.map(item => item.result_table_id).join(';')})`;
          });
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            // eslint-disable-next-line camelcase
            if (item.permission?.[authorityMap.SEARCH_LOG_AUTH]) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          this.indexSetList = s1.concat(s2);
          // 如果都没有权限直接显示页面无权限
          // eslint-disable-next-line camelcase
          if (!this.indexSetList[0]?.permission?.[authorityMap.SEARCH_LOG_AUTH]) {
            this.$store.dispatch('getApplyData', {
              action_ids: [authorityMap.SEARCH_LOG_AUTH],
              resources: [{
                type: 'indices',
                id: this.indexSetList[0].index_set_id,
              }],
            }).then((res) => {
              this.authPageInfo = res.data;
            })
              .catch((err) => {
                console.warn(err);
              })
              .finally(() => {
                this.basicLoading = false;
              });
            return;
          }

          // 切换路由
          const cacheValid = this.indexSetList.some(item => item.index_set_id === this.indexIdCache);
          this.changeIndexSet(cacheValid ? this.indexIdCache : this.indexSetList[0].index_set_id);
        } else {
          this.$router.push({
            name: 'notTraceIndex',
          });
        }
      } catch (e) {
        this.$router.push({
          name: 'notTraceIndex',
        });
      }
    },
    async searchHandle() {
      const paramData = {
        action_ids: [authorityMap.SEARCH_LOG_AUTH],
        resources: [{
          type: 'indices',
          id: this.indexId,
        }],
      };
      if (this.isSearchAllowed === null) {
        try {
          this.basicLoading = true;
          this.isTableLoading = true;
          const res = await this.$store.dispatch('checkAndGetData', paramData);
          if (res.isAllowed === false) {
            this.isSearchAllowed = false;
            this.$store.commit('updateAuthDialogData', res.data);
            return;
          }
        } catch (err) {
          console.warn(err);
          return;
        } finally {
          this.basicLoading = false;
          this.isTableLoading = false;
        }
      } else if (this.isSearchAllowed === false) { // 已知当前选择索引无权限
        try {
          this.basicLoading = true;
          this.isTableLoading = true;
          const res = await this.$store.dispatch('getApplyData', paramData);
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.basicLoading = false;
          this.isTableLoading = false;
        }
        return;
      }
      this.searchDisabled = true;
      this.isTableLoading = true;
      this.params.start_time = this.initDateTimeRange[0];
      this.params.end_time = this.initDateTimeRange[1];
      try {
        if (!this.totalFields.length) {
          this.basicLoading = true;
          this.isTableLoading = true;
          const {
            totalFields,
            sortFields,
            visibleFieldsName,
            visibleFieldsInfo,
            traceData,
          } = await this.getFieldsInfo();
          this.totalFields = totalFields;
          this.sortFields = sortFields;
          this.visibleFieldsName = visibleFieldsName;
          this.visibleFieldsInfo = visibleFieldsInfo;
          this.traceData = traceData;
          // eslint-disable-next-line camelcase
          this.fieldName = this.fieldName ? this.fieldName : (traceData.charts[0]?.field_name || '');
          this.getDocCountList();
          this.basicLoading = false;
          // await this.requestDateHistogram(false)
        }
        this.params.addition = [];
        const searchData = JSON.parse(JSON.stringify(this.searchData));
        for (const val in searchData) {
          const additionData = { method: val === 'duration_lte' ? 'lte' : val === 'duration_gte' ? 'gte' : 'is' };
          if (this.searchData[val]) {
            additionData.key = (val === 'duration_lte' || val === 'duration_gte') ? 'duration' : val;
            additionData.value = this.searchData[val];
            this.params.addition.push(additionData);
          }
        }
        delete this.params.fields;
        const promisList = [this.requestTableList()];
        if (this.initialCallShow) {
          promisList.push(this.requestDateHistogram(true));
        }
        await Promise.all(promisList);
      } catch (e) {
        console.warn(e);
      } finally {
        this.searchDisabled = false;
        this.basicLoading = false;
        this.isTableLoading = false;
      }
    },
    async requestTableList() {
      this.totalCount = 0;
      this.took = 0;
      this.logAllJsonList = [];
      this.logTableList = [];
      this.dataListShadow = [];
      this.dataListPaged = [];
      this.isPageOver = true;

      this.scrollToTop();
      try {
        this.isTableLoading = true;
        this.params.size = 20;
        const res = await this.$http.request('trace/requestTableList', {
          params: { index_set_id: this.indexId },
          data: this.params,
          mock: false,
          manualSchema: true,
        });
        this.tableRowsWidth = {};
        const fieldsObj = res.data.fields || {};
        for (const key in fieldsObj) {
          if (key) {
            this.tableRowsWidth[key] = fieldsObj[key].max_length || 0;
          }
        }
        this.totalCount = res.data.total > 20 ? 20 : res.data.total;
        this.logAllTableList = res.data.list;
        if (res.data.list.length) {
          this.initPageConf(res.data.list);
          this.loadPage();
        }
        this.logAllJsonList.splice(0, this.logAllJsonList.length, ...res.data.origin_log_list);
        this.calcTableRowWith();
      } catch (e) {
        throw e;
      } finally {
        this.isTableLoading = false;
      }
    },
    initPageConf(list) {
      this.currentPage = 0;
      this.isPageOver = false;

      this.count = list.length;
      this.pageSize = 30;
      this.totalPage = Math.ceil(this.count / this.pageSize) || 1;

      this.dataListShadow = list;
      this.dataListPaged = [];
      for (let i = 0; i < this.count; i += this.pageSize) {
        this.dataListPaged.push(this.dataListShadow.slice(i, i + this.pageSize));
      }
    },
    registerScrollEvent() {
      this.searchContentEl = document.querySelector('.trace-container');
      this.searchContentEl.addEventListener('scroll', this.handleScroll, { passive: true });
    },
    handleScroll() {
      if (this.throttle) {
        return;
      }

      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;

        const el = this.searchContentEl;
        this.isShowScrollTop = el.scrollTop > 550;

        if (this.isPageOver) {
          return;
        }
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 60) {
          this.loadPage(el.scrollTop);
        }
      }, 200);
    },
    loadPage(top) {
      this.currentPage += 1;
      this.isPageOver = this.currentPage === this.totalPage;
      this.logTableList.splice(this.logTableList.length, 0, ...this.dataListPaged[this.currentPage - 1]);
      top && this.$nextTick(() => {
        this.searchContentEl.scrollTop = top;
      });
    },
    calcTableRowWith() {
      const rowObj = {};
      const rowWidth = [];
      this.visibleFieldsInfo.forEach((item) => {
        const key = item.field_name;
        rowObj[key] = this.tableRowsWidth[key];
        rowWidth.push(this.tableRowsWidth[key]);
      });
      const rowNum = rowWidth.length;
      const allWidth = rowWidth.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
      const WIDTH = 1000; // 固定最小宽度
      if (Math.ceil(allWidth * 6.5) <= WIDTH - rowNum * 20) {
        this.visibleFieldsInfo.forEach((row) => {
          const key = row.field_name;
          rowObj[key] = rowObj[key] < 5 ? 5 : rowObj[key];
          rowObj[key] = rowObj[key] > 30 ? rowObj[key] / 1.5 : rowObj[key];
          row.minWidth = rowObj[key] / allWidth * (WIDTH - rowNum * 20);
        });
      } else {
        const half = Math.ceil(rowNum / 2);
        const proportion = [];
        for (const key in rowObj) {
          const width = rowObj[key] * 6.5;
          if (width >= Math.floor(half / rowNum * WIDTH)) {
            proportion.push(half);
          } else if (width <= Math.floor(1 / rowNum * WIDTH)) {
            proportion.push(1);
          } else {
            proportion.push(Math.floor(width * rowNum / WIDTH));
          }
        }
        const proportionNum = proportion.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
        this.visibleFieldsInfo.forEach((row, index) => {
          row.minWidth = WIDTH * (proportion[index] / proportionNum);
        });
      }
    },
    async getDocCountList() {
      const data = [];
      this.traceData.additions.forEach((item) => {
        if (item.show_type === 'select') {
          data.push(item.field_name);
        }
      });
      await this.$http.request('trace/getDocCountList', {
        params: { index_set_id: this.indexId },
        data: {
          fields: data,
        },
        mock: false,
        manualSchema: true,
      }).then((res) => {
        if (res.result) {
          this.docCountList = res.data.aggs_items;
        }
      });
    },
    async requestDateHistogram(val) {
      this.params.size = 9999;
      const url = val ? 'trace/requestDateHistogram' : 'trace/requestDateScatter';
      if (val) {
        const item = this.traceData.charts.find(item => item.field_name === this.fieldName);
        if (!item) {
          return;
        }
        if (item.chart_alias === 'line') {
          this.params.fields = [{ term_filed: item.field_name }];
        } else if (item.chart_alias === 'consuming') {
          this.params.fields = [{
            term_filed: item.field_name,
            metric_type: 'avg',
            metric_field: 'duration',
          }];
        }
      }
      try {
        this.initialCall = false;
        this.isChartLoading = true;
        const res = await this.$http.request(url, {
          params: {
            index_set_id: this.indexId,
          },
          data: this.params,
        });
        if (res.result) {
          if (val) {
            this.chartData = res.data.aggs;
          }
          this.$forceUpdate();
        }
      } catch (e) {
        this.chartData = {};
        throw e;
      } finally {
        this.initialCall = true;
        setTimeout(() => {
          this.isChartLoading = false;
        }, 100);
      }
    },
    async handleCheckChartType(val) {
      if (!this.initialCallShow) this.initialCallShow = true;

      const { chart_alias: chartCut, field_name: fieldName } = val;
      if (!this.chartData[fieldName]) {
        try {
          this.isChartLoading = true;
          if (!this.initialCallShow) this.initialCall = false;
          if (chartCut === 'line') {
            this.params.fields = [{ term_filed: fieldName }];
          } else if (chartCut === 'consuming') {
            this.params.fields = [{
              term_filed: fieldName,
              metric_type: 'avg',
              metric_field: 'duration',
            }];
          }
          const res = await this.$http.request('trace/requestDateHistogram', {
            params: {
              index_set_id: this.indexId,
            },
            data: this.params,
          });
          if (res.result) {
            this.chartData[fieldName] = res.data.aggs[fieldName];
            this.chartCut = chartCut;
            this.fieldName = fieldName;
          }
        } catch (e) {
          console.warn(e);
        } finally {
          this.initialCall = true;
          setTimeout(() => {
            this.isChartLoading = false;
          }, 100);
        }
      } else {
        this.chartCut = chartCut;
        this.fieldName = fieldName;
      }
    },
    handleToggleCallShow() {
      this.initialCallShow = !this.initialCallShow;
      if (this.initialCallShow && !this.chartData[this.fieldName]) {
        this.requestDateHistogram(true);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';
  @import '../../../scss/mixins/clearfix.scss';
  @import '../../../scss/devops-common.scss';

  #trace {
    height: 100%;
    overflow-y: auto;

    @include scroller(#ccc, 4px);

    .chart-view {
      position: relative;
      background: #fff;
      padding: 20px 60px;

      .chart-click {
        z-index: 10;
        position: absolute;
        top: 30px;
        font-size: 14px;

        span {
          display: inline-block;
          margin-left: 20px;
          cursor: pointer;
          padding: 5px;
        }

        .click-color {
          color: rgb(85, 150, 255);
          border-bottom: 2px solid rgb(85, 150, 255);
        }
      }
    }

    .search-item {
      display: flex;
      flex-wrap: wrap;
      background: #f4f7fa;
      padding: 0 60px;
      color: #63656e;
      font-size: 14px;

      .text-item {
        margin-bottom: 8px;
        line-height: 20px;
      }

      .search-trace {
        margin-right: 10px;
        padding-top: 20px;
      }
    }

    .search-area {
      width: 170px;
      background: #fff;
    }

    .more-text {
      display: inline-block;
      cursor: pointer;
      transition: height .2s;
      padding-left: 20px;
      line-height: 30px;
    }

    .search-time {
      padding: 20px 60px 0 60px;
      display: flex;
      color: #63656e;
      font-size: 14px;

      .duration {
        div {
          display: flex;
          margin-right: 10px;
        }
      }

      .code {
        margin-right: 10px;
      }
    }

    .search-keyword {
      padding: 20px 60px 0 60px;
      color: #63656e;
      font-size: 14px;

      div {
        margin-bottom: 10px;
        margin-right: 10px;
      }
    }

    .top-middle:hover {
      color: #3a84ff;
    }

    .search {
      padding: 10px 0;
      border-bottom: 1px solid rgb(220, 222, 229);
    }

    .table-search {
      padding: 20px 60px 24px;
      background-color: #fff;
    }

    .icon-sec {
      font-size: 12px;
      color: rgb(45, 203, 86);
      margin-right: 3px;
    }

    .icon-fai {
      font-size: 12px;
      color: rgb(234, 54, 54);
      margin-right: 3px;
    }

    .search-detail-button {
      width: 80px;
      margin-left: 10px;

      div {
        /* stylelint-disable-next-line declaration-no-important */
        margin: 0 !important;
      }
    }

    .trace-container {
      height: calc(100% - 60px);
      overflow-x: hidden;
      overflow-y: auto;

      @include scroller(#ccc, 4px);
    }

    .log-switch {
      line-height: 14px;
    }

    .fixed-scroll-top-btn {
      position: fixed;
      bottom: 24px;
      right: 14px;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 36px;
      height: 36px;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .2);
      border: 1px solid #dde4eb;
      border-radius: 4px;
      color: #63656e;
      background: #f0f1f5;
      cursor: pointer;
      z-index: 50;
      transition: all .2s;

      &:hover {
        color: #fff;
        background: #979ba5;
        transition: all .2s;
      }

      .bk-icon {
        font-size: 20px;
        font-weight: bold;
      }
    }
  }
</style>
