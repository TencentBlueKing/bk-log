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
  <div class="result-scroll-container" ref="scrollContainer" @scroll.passive="handleScroll">
    <!-- 检索结果 -->
    <div class="result-text">
      {{ $t('retrieve.result1') }}
      <span class="total-count">{{ totalCount }}</span>
      {{ $t('retrieve.result2') + tookTime + $t('retrieve.ms') }}
      <template v-if="showAddMonitor">
        <span>{{ $t('retrieve.result3') }}</span>
        <a href="javascript:void(0);" class="monitor-link" @click="jumpMonitor">
          {{ $t('retrieve.result4') }}
          <span class="log-icon icon-lianjie"></span>
        </a>
      </template>
    </div>
    <ResultEChart
      :retrieve-params="retrieveParams"
      @change-queue-res="changeQueueRes"
      @change-total-count="changeTotalCount" />
    <div class="result-table-container">
      <div class="cut-line"></div>
      <!-- 表格上的按钮 -->
      <div class="log-operation">
        <TimeFormatter></TimeFormatter>
        <div class="operation-icons">
          <!-- 字段设置 -->
          <bk-popover
            ref="fieldsSettingPopper"
            trigger="click"
            placement="bottom-end"
            theme="light bk-select-dropdown"
            animation="slide-toggle"
            :offset="0"
            :distance="15"
            :on-show="handleDropdownShow"
            :on-hide="handleDropdownHide">
            <slot name="trigger">
              <div class="operation-icon">
                <span class="icon log-icon icon-set-icon"></span>
              </div>
            </slot>
            <div slot="content" class="fields-setting-container">
              <FieldsSetting
                v-if="showFieldsSetting"
                :field-alias-map="fieldAliasMap"
                :retrieve-params="retrieveParams"
                @confirm="confirmModifyFields" @cancel="closeDropdown" />
            </div>
          </bk-popover>
          <!-- 导出 -->
          <div
            :class="{ 'operation-icon': true, 'disabled-icon': !queueStatus }"
            @click="exportLog"
            v-bk-tooltips="queueStatus ? $t('btn.export') : undefined">
            <span class="icon log-icon icon-xiazai"></span>
          </div>
        </div>
      </div>
      <!-- 表格内容 -->
      <bk-table v-if="!renderTable" class="king-table"></bk-table>
      <bk-table
        v-else
        v-bkloading="{ isLoading: tableLoading || webConsoleLoading, zIndex: 0, extCls: 'result-table-loading' }"
        ref="resultTable"
        class="king-table"
        :data="tableList"
        :empty-text="$t('retrieve.notData')"
        @row-click="tableRowClick"
        @row-mouse-enter="handleMouseEnter"
        @row-mouse-leave="handleMouseLeave"
        @header-dragend="handleHeaderDragend">
        <!-- 展开详情 -->
        <bk-table-column type="expand" width="30" align="center" v-if="visibleFields.length">
          <template slot-scope="{ $index }">
            <div class="json-view-wrapper">
              <VueJsonPretty :deep="5" :data="originTableList[$index]" />
            </div>
          </template>
        </bk-table-column>
        <!-- 显示字段 -->
        <template v-for="(field,index) in visibleFields">
          <bk-table-column
            align="left"
            :key="field.field_name"
            :min-width="field.minWidth"
            :render-header="renderHeaderAliasName"
            :index="index"
            :width="field.width">
            <template slot-scope="{ row }">
              <TableColumn
                :content="tableRowDeepView(row, field.field_name, field.field_type)"
                @iconClick="(type, content) => handleIconClick(type, content, field, row)"
              ></TableColumn>
            </template>
          </bk-table-column>
        </template>
        <!-- 实时日志 上下文 -->
        <bk-table-column
          v-if="showHandleOption"
          :label="$t('retrieve.operate')"
          :width="84"
          align="right"
          :resizable="false">
          <!-- eslint-disable-next-line -->
          <template slot-scope="{ row, column, $index }">
            <div
              :class="{ 'handle-content': true, 'fix-content': showAllHandle }"
              v-if="curHoverIndex === $index"
              @mouseenter="mouseenterHandle"
              @mouseleave="mouseleaveHandle">
              <span
                v-bk-tooltips="{ content: $t('retrieve.log'), delay: 500 }"
                class="handle-card"
                v-if="showRealtimeLog && !checkIsHide('showRealtimeLog')">
                <span
                  class="icon log-icon icon-handle icon-time"
                  @click.stop="openLogDialog(row, 'realTimeLog')">
                </span>
              </span>
              <span
                v-bk-tooltips="{ content: $t('retrieve.context'), delay: 500 }"
                class="handle-card"
                v-if="showContextLog && !checkIsHide('showContextLog')">
                <span
                  class="icon log-icon icon-handle icon-document"
                  @click.stop="openLogDialog(row, 'contextLog')">
                </span>
              </span>
              <span
                v-bk-tooltips="{ content: $t('retrieve.monitorAlarm'), delay: 500 }"
                class="handle-card"
                v-if="showMonitorWeb && !checkIsHide('showMonitorWeb')">
                <span class="icon icon-handle log-icon icon-inform" @click.stop="openMonitorWeb(row)"></span>
              </span>
              <span
                v-bk-tooltips="{ content: 'WebConsole', delay: 500 }"
                class="handle-card"
                v-if="showWebConsole && !checkIsHide('showWebConsole')">
                <span class="icon icon-handle log-icon icon-teminal" @click.stop="openWebConsole(row)"></span>
              </span>
              <span class="bk-icon icon-more handle-card icon-handle" v-if="showMoreHandle && !showAllHandle"></span>
            </div>
          </template>
        </bk-table-column>
      </bk-table>
      <!-- 表格底部内容 -->
      <template v-if="tableList.length && visibleFields.length">
        <p class="more-desc" v-if="!isPageOver && count === limitCount">{{ $t('retrieve.showMore') }}
          <a href="javascript: void(0);" @click="scrollToTop">{{ $t('btn.backToTop') }}</a>
        </p>
        <div
          v-if="isPageOver"
          v-bkloading="{ isLoading: true }"
          style="height: 40px;">
        </div>
      </template>
    </div>

    <!-- 滚动到顶部 -->
    <div class="fixed-scroll-top-btn" v-show="showScrollTop" @click="scrollToTop">
      <i class="bk-icon icon-angle-up"></i>
    </div>

    <!-- 实时滚动日志/上下文 -->
    <bk-dialog
      v-model="logDialog.visible"
      :ext-cls="logDialog.fullscreen ? 'log-dialog log-full-dialog' : 'log-dialog'"
      :title="logDialog.title"
      :header-position="logDialog.headerPosition"
      :width="logDialog.width"
      :fullscreen="logDialog.fullscreen"
      :draggable="false"
      :mask-close="false"
      :esc-close="false"
      :show-footer="false"
      @after-leave="hideDialog">
      <RealTimeLog
        v-if="logDialog.type === 'realTimeLog'"
        :log-params="logDialog.data"
        @toggleScreenFull="toggleScreenFull"
        @close-dialog="hideDialog" />
      <ContextLog
        v-if="logDialog.type === 'contextLog'"
        :retrieve-params="retrieveParams"
        :log-params="logDialog.data"
        @toggleScreenFull="toggleScreenFull"
        @close-dialog="hideDialog" />
    </bk-dialog>

    <bk-dialog
      v-model="showAsyncExport"
      theme="primary"
      ext-cls="async-export-dialog"
      :mask-close="false"
      :show-footer="false">
      <div class="export-container" v-bkloading="{ isLoading: exportLoading }">
        <span class="bk-icon bk-dialog-warning icon-exclamation"></span>
        <div class="header">
          {{ totalCount > 2000000 ? $t('retrieve.dataMoreThanMillion') : $t('retrieve.dataMoreThan') }}
        </div>
        <div class="export-type immediate-export">
          <span class="bk-icon icon-info-circle"></span>
          <span class="export-text">{{ $t('retrieve.immediateExportDesc') }}</span>
          <bk-button theme="primary" @click="openDownloadUrl">{{ $t('retrieve.immediateExport') }}</bk-button>
        </div>
        <div class="export-type async-export">
          <span class="bk-icon icon-info-circle"></span>
          <span v-if="totalCount > 2000000" class="export-text">{{ $t('retrieve.asyncExportMoreDesc') }}</span>
          <span v-else class="export-text">{{ $t('retrieve.asyncExportDesc') }}</span>
          <bk-button @click="downloadAsync">{{ $t('retrieve.asyncExport') }}</bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import tableRowDeepViewMixin from '@/mixins/tableRowDeepViewMixin';
import { setFieldsWidth } from '@/common/util';
import TimeFormatter from '@/components/common/time-formatter';
import RealTimeLog from './RealTimeLog';
import ContextLog from './ContextLog';
import ResultEChart from './ResultEChart';
import FieldsSetting from './FieldsSetting';
import TableColumn from './TableColumn';
import { mapState } from 'vuex';

export default {
  components: {
    TimeFormatter,
    RealTimeLog,
    ContextLog,
    ResultEChart,
    FieldsSetting,
    TableColumn,
  },
  mixins: [tableRowDeepViewMixin],
  props: {
    renderTable: {
      type: Boolean,
      required: true,
    },
    tableLoading: {
      type: Boolean,
      required: true,
    },
    retrieveParams: {
      type: Object,
      required: true,
    },
    tookTime: {
      type: Number,
      required: true,
    },
    indexSetList: {
      type: Array,
      required: true,
    },
    tableData: {
      type: Object,
      required: true,
    },
    visibleFields: {
      type: Array,
      required: true,
    },
    fieldAliasMap: {
      type: Object,
      default() {
        return {};
      },
    },
    showFieldAlias: {
      type: Boolean,
      default: false,
    },
    showRealtimeLog: {
      type: Boolean,
      required: true,
    },
    showContextLog: {
      type: Boolean,
      required: true,
    },
    showWebConsole: {
      type: Boolean,
      required: true,
    },
    bkMonitorUrl: {
      type: String,
      required: true,
    },
    asyncExportUsable: {
      type: Boolean,
      default: true,
    },
    asyncExportUsableReason: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      originTableList: [],
      tableList: [],
      throttle: false, // 滚动节流 是否进入cd
      isPageOver: false, // 前端分页加载是否结束
      finishPolling: false,
      // isTableRequestLoading: false,
      // dataListPaged: [], // 将列表数据按 pageSize 分页
      count: 0, // 数据总条数
      pageSize: 50, // 每页展示多少数据
      totalPage: 1,
      currentPage: 1, // 当前加载了多少页
      totalCount: 0,
      scrollHeight: 0,
      limitCount: 2000,
      queueStatus: false,
      showFieldsSetting: false, // 字段设置
      fieldsSettingLoading: false,
      webConsoleLoading: false, // 点击 WebConsole 时表格 loading
      cacheOpenMoreList: [], // 暂存点击打开的项集合
      curHoverIndex: -1, // 当前鼠标hover行的索引
      showAllHandle: false, // hove操作区域显示全部icon
      overflowHandle: [], // 当操作按钮大于3个时 用于保存超出的icon key
      showScrollTop: false, // 显示滚动到顶部icon
      showAsyncExport: false, // 异步下载弹窗
      exportLoading: false,
      isInit: false,
      logDialog: {
        title: '',
        type: '',
        width: '100%',
        visible: false,
        headerPosition: 'left',
        fullscreen: true,
        data: {},
      },
      fieldTypeMap: {
        any: {
          name: this.$t('不限'),
        },
        number: {
          name: this.$t('数字'),
        },
        integer: {
          name: this.$t('数字'),
        },
        double: {
          name: this.$t('数字'),
        },
        long: {
          name: this.$t('文本'),
        },
        keyword: {
          name: this.$t('字符串'),
        },
        text: {
          name: this.$t('文本'),
        },
        date: {
          name: this.$t('时间'),
        },
        boolean: {
          name: '',
          icon: '',
        },
      },
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      clearTableWidth: state => state.clearTableWidth,
    }),
    showAddMonitor() {
      return Boolean(window.MONITOR_URL && this.$store.state.topMenu.some(item => item.id === 'monitor'));
    },
    showMonitorWeb() {
      return this.bkMonitorUrl !== '';
    },
    showMoreHandle() {
      const handleOptions = ['showRealtimeLog', 'showContextLog', 'showWebConsole', 'showMonitorWeb'];
      const isShowOptions = handleOptions.filter(item => this[item]);
      const isShowMore = isShowOptions.length > 3;

      if (isShowMore) {
        this.overflowHandle.push(...isShowOptions.slice(2));
      }

      return isShowMore;
    },
    showHandleOption() {
      const { showRealtimeLog, showContextLog, showWebConsole, showMonitorWeb, visibleFields } = this;
      if (visibleFields.length !== 0) {
        const columnObj = JSON.parse(localStorage.getItem('table_column_width_obj'));
        const { params: { indexId }, query: { bizId } } = this.$route;
        let widthObj = {};

        for (const bizKey in columnObj) {
          if (bizKey === bizId) {
            for (const fieldKey in columnObj[bizId].fields) {
              fieldKey === indexId && (widthObj =  columnObj[bizId].fields[indexId]);
            }
          }
        }

        visibleFields.forEach((el, index) => {
          el.width = widthObj[index] === undefined ? 'default' : widthObj[index];
        });
      }
      return (showRealtimeLog || showContextLog || showWebConsole || showMonitorWeb) && visibleFields.length;
    },
  },
  watch: {
    tableData(data) {
      this.finishPolling = data && data.finishPolling;
      if (data?.list?.length) {
        if (this.isInit) {
          // 根据接口 data.fields ==> item.max_length 设置各个字段的宽度比例
          setFieldsWidth(this.visibleFields, data.fields, 500);
          this.isInit = true;
        }
        this.count += data.list.length;
        this.tableList.push(...data.list);
        this.originTableList.push(...data.origin_log_list);
        this.$nextTick(() => {
          this.$refs.scrollContainer.scrollTop = this.newScrollHeight;
        });
        this.isPageOver = false;
      }
    },
    clearTableWidth() {
      const columnObj = JSON.parse(localStorage.getItem('table_column_width_obj'));
      const { params: { indexId }, query: { bizId } } = this.$route;
      if (columnObj === null || JSON.stringify(columnObj) === '{}') {
        return;
      }
      const isHaveBizId = Object.keys(columnObj).some(el => el === bizId);

      if (!isHaveBizId || columnObj[bizId].fields[indexId] === undefined) {
        return;
      }

      for (const bizKey in columnObj) {
        if (bizKey === bizId) {
          for (const fieldKey in columnObj[bizKey].fields) {
            if (fieldKey === indexId) {
              delete columnObj[bizId].fields[indexId];
              columnObj[bizId].indexsetIds.splice(columnObj[bizId].indexsetIds.indexOf(indexId, 1));
              columnObj[bizId].indexsetIds.length === 0 && delete columnObj[bizId];
            }
          }
        }
      }

      localStorage.setItem('table_column_width_obj', JSON.stringify(columnObj));
    },
  },
  methods: {
    // 跳转到监控
    jumpMonitor() {
      const indexSetId = this.$route.params.indexId;
      const params = {
        bizId: this.$store.state.bkBizId,
        indexSetId,
        scenarioId: '',
        indexStatement: this.retrieveParams.keyword, // 查询语句
        dimension: [], // 监控维度
        condition: [], // 监控条件
      };
      const indexSet = this.indexSetList.find(item => item.index_set_id === indexSetId);
      if (indexSet) {
        params.scenarioId = indexSet.category_id;
      }
      this.retrieveParams.addition.forEach((item) => {
        params.condition.push({
          condition: 'and',
          key: item.field,
          method: item.operator === 'eq' ? 'is' : item.operator,
          value: item.value,
        });
      });
      const urlArr = [];
      for (const key in params) {
        if (key === 'dimension' || key === 'condition') {
          urlArr.push(`${key}=${encodeURI(JSON.stringify(params[key]))}`);
        } else {
          urlArr.push(`${key}=${params[key]}`);
        }
      }
      window.open(`${window.MONITOR_URL}/?${urlArr.join('&')}#/strategy-config/add`, '_blank');
    },
    reset() {
      this.newScrollHeight = 0;
      this.$nextTick(() => {
        this.$refs.scrollContainer.scrollTop = this.newScrollHeight;
      });
      this.count = 0;
      this.currentPage = 1;
      this.originTableList = [];
      this.tableList = [];
      this.isInit = false;
      this.finishPolling = false;
    },
    // 滚动到顶部
    scrollToTop() {
      this.$easeScroll(0, 300, this.$refs.scrollContainer);
    },
    handleScroll() {
      if (this.throttle || this.isPageOver) {
        return;
      }
      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;
        const el = this.$refs.scrollContainer;
        this.showScrollTop = el.scrollTop > 550;
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 100) {
          if (this.count === this.limitCount || this.finishPolling) return;

          this.isPageOver = true;
          this.currentPage += 1;
          this.newScrollHeight = el.scrollTop;
          this.$emit('request-table-data');
        }
      }, 200);
    },

    // 字段设置
    handleDropdownShow() {
      this.showFieldsSetting = true;
    },
    handleDropdownHide() {
      this.showFieldsSetting = false;
    },
    confirmModifyFields(displayFieldNames, showFieldAlias) {
      this.$emit('fieldsUpdated', displayFieldNames, showFieldAlias);
      this.closeDropdown();
    },
    closeDropdown() {
      this.showFieldsSetting = false;
      this.$refs.fieldsSettingPopper.instance.hide();
    },
    changeTotalCount(count) {
      this.totalCount = count;
    },
    changeQueueRes(status) {
      this.queueStatus = status;
    },
    // 导出日志
    exportLog() {
      if (!this.queueStatus) return;

      // 导出数据为空
      if (!this.totalCount) {
        const infoDialog = this.$bkInfo({
          type: 'error',
          title: this.$t('retrieve.exportFailed'),
          subTitle: this.$t('retrieve.dataNone'),
          showFooter: false,
        });
        setTimeout(() => infoDialog.close(), 3000);
      } else if (this.totalCount > 10000) {
        // 导出数量大于1w且小于100w 可直接下载1w 或 异步全量下载全部
        // 通过 field 判断是否支持异步下载
        if (this.asyncExportUsable) {
          this.showAsyncExport = true;
        } else {
          const h = this.$createElement;
          this.$bkInfo({
            type: 'warning',
            title: this.$t('retrieve.dataMoreThan'),
            subHeader: h('p', {
              style: {
                whiteSpace: 'normal',
                padding: '0 60px',
              },
            }, `${this.$t('retrieve.reasonFor')}${this.asyncExportUsableReason}${this.$t('retrieve.reasonDesc')}`),
            okText: this.$t('retrieve.immediateExport'),
            confirmFn: () => this.openDownloadUrl(),
          });
        }
      } else {
        this.openDownloadUrl();
      }
    },
    openDownloadUrl() {
      const exportParams = encodeURIComponent(JSON.stringify({
        ...this.retrieveParams,
        size: this.totalCount,
      }));
      // eslint-disable-next-line max-len
      const targetUrl = `${window.SITE_URL}api/v1/search/index_set/${this.$route.params.indexId}/export/?export_dict=${exportParams}`;
      window.open(targetUrl);
    },
    downloadAsync() {
      const data = { ...this.retrieveParams };
      data.size = this.totalCount;
      data.time_range = 'customized';

      this.exportLoading = true;
      this.$http.request('retrieve/exportAsync', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data,
      }).then((res) => {
        if (res.result) {
          this.$bkMessage({
            theme: 'success',
            message: res.data.prompt,
          });
        }
      })
        .finally(() => {
          this.showAsyncExport = false;
          this.exportLoading = false;
        });
    },

    // 展开表格行JSON
    tableRowClick(row) {
      this.$refs.resultTable.toggleRowExpansion(row);
    },
    handleMouseEnter(index) {
      this.curHoverIndex = index;
    },
    handleMouseLeave() {
      this.curHoverIndex = -1;
    },
    handleHeaderDragend(newWidth, oldWidth, { index }) {
      const { params: { indexId }, query: { bizId } } = this.$route;
      if (index === undefined || bizId === undefined || indexId === undefined) {
        return;
      }
      const widthObj = {};
      widthObj[index] = newWidth;
      index === this.visibleFields.length - 1 && (widthObj[index] = 'default');

      let columnObj = JSON.parse(localStorage.getItem('table_column_width_obj'));
      if (columnObj === null) {
        columnObj = {};
        columnObj[bizId] = this.initSubsetObj(bizId, indexId);
      }
      const isIncludebizId = Object.keys(columnObj).some(el => el === bizId);
      isIncludebizId === false && (columnObj[bizId] = this.initSubsetObj(bizId, indexId));

      for (const key in columnObj) {
        if (key === bizId) {
          if (columnObj[bizId].fields[indexId] === undefined) {
            columnObj[bizId].fields[indexId] = {};
            columnObj[bizId].indexsetIds.push(indexId);
          }
          columnObj[bizId].fields[indexId] = Object.assign(columnObj[bizId].fields[indexId], widthObj);
        }
      }

      localStorage.setItem('table_column_width_obj', JSON.stringify(columnObj));
    },
    initSubsetObj(bizId, indexId) {
      const subsetObj = {};
      subsetObj.bizId = bizId;
      subsetObj.indexsetIds = [indexId];
      subsetObj.fields = {};
      subsetObj.fields[indexId] = {};
      return subsetObj;
    },
    mouseenterHandle() {
      this.showAllHandle = true;
    },
    mouseleaveHandle() {
      this.showAllHandle = false;
    },
    getFieldIcon(fieldType) {
      const iconMap = {
        number: 'log-icon icon-number',
        keyword: 'log-icon log-icon icon-string',
        text: 'log-icon icon-text',
        date: 'bk-icon icon-clock',
      };
      if (fieldType === 'long' || fieldType === 'integer') {
        return iconMap.number;
      }
      return iconMap[fieldType];
    },
    // eslint-disable-next-line no-unused-vars
    renderHeaderAliasName(h, { column, $index }) {
      const field = this.visibleFields[$index - 1];
      const fieldName = this.showFieldAlias ? this.fieldAliasMap[field.field_name] : field.field_name;
      const fieldType = field.field_type;
      const fieldIcon = this.getFieldIcon(field.field_type) || 'log-icon icon-unkown';
      const content = this.fieldTypeMap[fieldType] ? this.fieldTypeMap[fieldType].name : undefined;

      return h('div', {
        class: 'render-header',
      }, [
        h('span', {
          class: `field-type-icon ${fieldIcon}`,
          directives: [
            {
              name: 'bk-tooltips',
              value: content,
            },
          ],
        }),
        h('span', fieldName),
      ]);
    },
    handleIconClick(type, content, field, row) {
      let value = field.field_type === 'date' ? row[field.field_name] : content;
      value = String(value).replace(/<mark>/g, '')
        .replace(/<\/mark>/g, '');
      if (type === 'search') { // 将表格单元添加到过滤条件
        this.$emit('addFilterCondition', field.field_name, 'eq', value);
      } else if (type === 'copy') { // 复制单元格内容
        try {
          const input = document.createElement('input');
          input.setAttribute('value', value);
          document.body.appendChild(input);
          input.select();
          document.execCommand('copy');
          document.body.removeChild(input);
          this.messageSuccess(this.$t('复制成功'));
        } catch (e) {
          console.warn(e);
        }
      }
    },
    // 打开实时日志或上下文弹窗
    openLogDialog(row, type) {
      this.logDialog.data = row;
      this.logDialog.type = type;
      this.logDialog.title = type === 'realTimeLog' ? this.$t('retrieve.realTimeScrollingLog') : this.$t('retrieve.context');
      this.logDialog.visible = true;
      this.logDialog.fullscreen = true;
    },
    openWebConsole(row) {
      const { cluster, container_id } = row;
      this.webConsoleLoading = true;
      this.$http.request('retrieve/getWebConsoleUrl', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        query: {
          cluster_id: encodeURIComponent(cluster),
          container_id,
        },
      }).then((res) => {
        window.open(res.data);
      })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.webConsoleLoading = false;
        });
    },
    openMonitorWeb(row) {
      const ip = row.serverIp || row.ip;
      const cloudId = row.cloudId?.toString() || row.cloudid?.toString();
      const id = cloudId ? `-${cloudId}` : '';
      const host = /\//.test(this.bkMonitorUrl) ? this.bkMonitorUrl : `${this.bkMonitorUrl}/`;
      const url = `${host}?bizId=${this.bkBizId}#/performance/detail/${ip}${id}`;

      window.open(url);
    },
    openMoreHandle(row, column, index) {
      this.cacheOpenMoreList.push(index);
    },
    // 关闭实时日志或上下文弹窗后的回调
    hideDialog() {
      this.logDialog.type = '';
      this.logDialog.title = '';
      this.logDialog.visible = false;
    },
    // 实时日志或上下文弹窗开启或关闭全屏
    toggleScreenFull(isScreenFull) {
      this.logDialog.width = isScreenFull ? '100%' : 1078;
      this.logDialog.fullscreen = isScreenFull;
    },
    // 区分当前是否超过第3个的icon
    checkIsHide(key) {
      // 当前未hover操作区域 当前超出3个操作icon 超出第3个icon
      return !this.showAllHandle && this.showMoreHandle && this.overflowHandle.includes(key);
    },
  },
};
</script>

<style lang="scss" scoped>
  .result-scroll-container {
    margin-top: 48px;
    height: calc(100% - 48px);
    overflow: auto;
  }

  .result-text {
    font-size: 12px;
    color: #63656e;
    padding: 10px 20px;

    .monitor-link {
      color: #3a84ff;
    }

    .total-count {
      color: #f00;
    }
  }

  .result-table-container {
    position: relative;
    margin: 0 20px 16px;
    padding: 20px 24px;
    background: #fff;
    // border-radius: 2px;
    // box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
    .cut-line {
      position: absolute;
      top: 0;
      left: 24px;
      right: 24px;
      height: 1px;
      border-top: 1px solid#f0f1f5;;
    }

    .log-operation {
      position: relative;
      display: flex;
      justify-content: space-between;
      line-height: 30px;

      .operation-icons {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 74px;

        .operation-icon {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          cursor: pointer;
          border: 1px solid #c4c6cc;
          transition: boder-color .2s;
          border-radius: 2px;
          outline: none;

          &:hover {
            border-color: #979ba5;
            transition: boder-color .2s;
          }

          &:active {
            border-color: #3a84ff;
            transition: boder-color .2s;
          }

          .log-icon {
            width: 16px;
            font-size: 16px;
            color: #979ba5;
          }
        }
        .disabled-icon {
          background-color: #fff;
          border-color: #dcdee5;
          cursor: not-allowed;
          &:hover,
          .log-icon {
            border-color: #dcdee5;
            color: #c4c6cc;
          }
        }
      }
    }

    .king-table {
      margin-top: 16px;

      /deep/ .bk-table-body-wrapper {
        min-height: calc(100vh - 508px);

        .bk-table-empty-block {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 556px);;
        }
      }

      /deep/ .cell {
        display: inline-table;

        .operation-button:not(:last-child) {
          padding-right: 8px;
        }
      }

      /deep/ td mark {
        background: #f3e186;
      }

      .json-view-wrapper {
        padding: 10px 0;

        /deep/ .vjs-tree {
          font-size: 12px !important;

          .vjs-value__string {
            white-space: pre-wrap;
            tab-size: 3;
          }
        }
      }

      /deep/ .result-table-loading {
        width: calc(100% - 2px);
        height: calc(100% - 2px);
      }

      .handle-card {
        display: inline-block;
        margin-left: 10px;
        width: 14px;
        height: 14px;

        &:first-child {
          margin-left: 0;
        }
      }

      .icon-handle {
        font-size: 14px;
        color: #979ba5;
        cursor: pointer;

        &:hover {
          color: #3a84ff;
        }
      }

      .handle-content {
        display: flex;
        position: absolute;
        right: 0;
        width: 84px;
        height: 100%;
        padding: 0 10px;
        align-items: center;
        top: 0;
        overflow: hidden;
        justify-content: flex-end;
      }

      .fix-content {
        width: auto;
        background-color: #f0f1f5;
      }
    }

    /deep/ .render-header {
      .field-type-icon {
        width: 12px;
        margin: 0 4px 0 0;
        font-size: 12px;
        color: #979ba5;
      }
    }
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
    z-index: 2100;
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
  // 日志全屏状态下的样式
  .log-full-dialog {
    /deep/ .bk-dialog-content {
      margin-bottom: 0 !important;
    }
  }
  // 设置列表字段
  .fields-setting-container {
    width: 725px;
    height: 482px;
    border: 1px solid #dcdee5;
    box-sizing: border-box;
    color: #63656e;
    font-size: 14px;
  }

  .async-export-dialog {
    .header {
      padding: 18px 0px 32px !important;
    }

    .export-container {
      text-align: center;
    }

    .bk-dialog-warning {
      display: block;
      margin: 0 auto;
      width: 58px;
      height: 58px;
      line-height: 58px;
      font-size: 30px;
      color: #fff;
      border-radius: 50%;
      background-color: #ffb848;
    }

    .header {
      padding: 18px 24px 32px;
      display: inline-block;
      width: 100%;
      font-size: 24px;
      color: #313238;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      line-height: 1.5;
      margin: 0;
    }

    .export-type {
      margin-bottom: 24px;
      padding: 0 22px;
      display: flex;
      align-items: center;

      .export-text {
        margin-left: 8px;
        max-width: 184px;
        text-align: left;
        font-size: 14px;
        color: #313238;
        line-height: 18px;
      }

      .bk-button {
        margin-left: auto;
      }
    }
  }
</style>
