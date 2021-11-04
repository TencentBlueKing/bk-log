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
  <div>
    <div class="result-table-container" data-test-id="retrieve_from_fieldForm">
      <!-- 表格内容 -->
      <!-- <bk-table v-if="!renderTable" class="king-table"></bk-table> -->
      <bk-table
        ref="resultTable"
        :class="['king-table', { 'is-wrap': isWrap }]"
        :data="tableList"
        :show-header="!showOriginal"
        :outer-border="!showOriginal"
        :empty-text="$t('retrieve.notData')"
        @row-click="tableRowClick"
        @row-mouse-enter="handleMouseEnter"
        @row-mouse-leave="handleMouseLeave"
        @header-dragend="handleHeaderDragend">
        <!-- 展开详情 -->
        <bk-table-column
          type="expand"
          width="30"
          align="center"
          v-if="showOriginal || visibleFields.length">
          <template slot-scope="{ $index }">
            <expand-view
              v-bind="$attrs"
              :data="originTableList[$index]"
              :total-fields="totalFields"
              :visible-fields="visibleFields"
              @menuClick="handleMenuClick">
            </expand-view>
          </template>
        </bk-table-column>
        <!-- 显示字段 -->
        <!-- 原始 -->
        <template v-if="showOriginal">
          <bk-table-column class-name="original-time" width="160">
            <template slot-scope="{ row }">
              <span class="time-field">{{ formatDate(Number(row[timeField]) || '') }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :class-name="`original-str${isWrap ? ' is-wrap' : ''}`">
            <!-- eslint-disable-next-line -->
            <template slot-scope="{ row, column, $index }">
              <div :class="['str-content', { 'is-limit': !cacheExpandStr.includes($index) }]">
                <span>{{ JSON.stringify(row) }}</span>
                <p
                  v-if="!cacheExpandStr.includes($index)"
                  class="show-whole-btn"
                  @click.stop="handleShowWhole($index)">
                  {{ $t('展开全部') }}
                </p>
              </div>
            </template>
          </bk-table-column>
        </template>
        <!-- 表格 -->
        <template v-else v-for="(field,index) in visibleFields">
          <bk-table-column
            align="left"
            :key="field.field_name"
            :min-width="field.minWidth"
            :render-header="renderHeaderAliasName"
            :index="index"
            :width="field.width">
            <template slot-scope="{ row }">
              <TableColumn
                :is-wrap="isWrap"
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

        <!-- 初次加载骨架屏loading -->
        <bk-table-column v-if="tableLoading" slot="empty">
          <retrieve-loader
            is-loading
            :is-original-field="showOriginal"
            :visible-fields="visibleFields">
          </retrieve-loader>
        </bk-table-column>

        <!-- 下拉刷新骨架屏loading -->
        <template slot="append" v-if="tableList.length && visibleFields.length && isPageOver">
          <retrieve-loader
            :is-original-field="showOriginal"
            :visible-fields="visibleFields">
          </retrieve-loader>
        </template>
      </bk-table>
      <!-- 表格底部内容 -->
      <p class="more-desc" v-if="tableList.length === limitCount">{{ $t('retrieve.showMore') }}
        <a href="javascript: void(0);" @click="scrollToTop">{{ $t('btn.backToTop') }}</a>
      </p>
      <!-- <div
        v-if="tableList.length && visibleFields.length && isPageOver"
        v-bkloading="{ isLoading: true }"
        style="height: 40px;">
      </div> -->
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
  </div>
</template>

<script>
import { mapState } from 'vuex';
import tableRowDeepViewMixin from '@/mixins/tableRowDeepViewMixin';
import RealTimeLog from '../../result-comp/RealTimeLog';
import ContextLog from '../../result-comp/ContextLog';
import TableColumn from '../../result-comp/TableColumn';
import ExpandView from './ExpandView.vue';
import { formatDate } from '@/common/util';
import RetrieveLoader from '@/skeleton/retrieve-loader';

export default {
  components: {
    TableColumn,
    RealTimeLog,
    ContextLog,
    ExpandView,
    RetrieveLoader,
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
    visibleFields: {
      type: Array,
      required: true,
    },
    totalFields: {
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
    tableList: {
      type: Array,
      required: true,
    },
    originTableList: {
      type: Array,
      required: true,
    },
    isPageOver: {
      type: Boolean,
      required: false,
    },
    showOriginal: {
      type: Boolean,
      default: false,
    },
    timeField: {
      type: String,
      default: '',
    },
    isWrap: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      formatDate,
      throttle: false, // 滚动节流 是否进入cd
      finishPolling: false,
      count: 0, // 数据总条数
      pageSize: 50, // 每页展示多少数据
      totalPage: 1,
      currentPage: 1, // 当前加载了多少页
      totalCount: 0,
      scrollHeight: 0,
      limitCount: 2000,
      fieldsSettingLoading: false,
      webConsoleLoading: false, // 点击 WebConsole 时表格 loading
      cacheOpenMoreList: [], // 暂存点击打开的项集合
      curHoverIndex: -1, // 当前鼠标hover行的索引
      showAllHandle: false, // hove操作区域显示全部icon
      overflowHandle: [], // 当操作按钮大于3个时 用于保存超出的icon key
      showScrollTop: false, // 显示滚动到顶部icon
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
      cacheExpandStr: [],
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      clearTableWidth: state => state.clearTableWidth,
    }),
    ...mapState('globals', ['fieldTypeMap']),
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
      return (showRealtimeLog
      || showContextLog
      || showWebConsole
      || showMonitorWeb) && this.tableList.length;
    },
  },
  watch: {
    retrieveParams: {
      deep: true,
      handler() {
        this.cacheExpandStr = [];
      },
    },
    '$route.params.indexId'() { // 切换索引集重置状态
      this.cacheExpandStr = [];
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
    // 滚动到顶部
    scrollToTop() {
      this.$easeScroll(0, 300, this.$parent.$parent.$parent.$refs.scrollContainer);
    },
    // 展开表格行JSON
    tableRowClick(row) {
      this.$refs.resultTable.toggleRowExpansion(row);
      this.curHoverIndex = -1;
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
      if (field) {
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
      }
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
    handleShowWhole(index) {
      this.cacheExpandStr.push(index);
    },
    handleMenuClick(option) {
      switch (option.operation) {
        case 'is':
        case 'is not':
          // eslint-disable-next-line no-case-declarations
          const { fieldName, operation, value } = option;
          this.$emit('addFilterCondition', fieldName, operation, value.toString());
          break;
        case 'copy':
          try {
            const input = document.createElement('input');
            input.setAttribute('value', option.value);
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            this.messageSuccess(this.$t('复制成功'));
          } catch (e) {
            console.warn(e);
          }
          break;
        case 'display':
          this.$emit('fieldsUpdated', option.displayFieldNames);
          break;
        default:
          break;
      }
    },
  },
};
</script>


<style lang="scss">
.tippy-tooltip.light-theme.bk-table-setting-popover-content-theme {
  padding: 0;
}
.result-table-container {
  position: relative;
  background: #fff;
  .king-table {
    margin-top: 16px;
    td {
      vertical-align: top;
    }
    .bk-table-body-wrapper {
      min-height: calc(100vh - 550px);
      .bk-table-empty-block {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: calc(100vh - 600px);;
      }
    }
    .cell {
      .operation-button:not(:last-child) {
        padding-right: 8px;
      }
    }
    td mark {
      background: #f3e186;
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
      padding: 12px 10px;
      align-items: flex-start;
      top: 0;
      overflow: hidden;
      justify-content: flex-end;
    }
    .fix-content {
      width: auto;
      background-color: #f0f1f5;
    }
    .time-field {
      font-weight: 700;
    }
    .original-str {
      .cell {
        padding: 12px 14px 0 14px;
      }
      .str-content {
        position: relative;
        line-height: 20px;
        &.is-limit {
          max-height: 96px;
        }
      }
      &.is-wrap {
        .cell {
          padding: 12px 14px;
        }
        .str-content {
          display: inline-block;
          overflow: hidden;
        }
      }
      .show-whole-btn {
        position: absolute;
        top: 80px;
        width: 100%;
        height: 24px;
        color: #3A84FF;
        font-size: 12px;
        background: #fff;
        cursor: pointer;
        transition: background-color .25s ease;
      }
    }
    .original-time {
      padding-top: 16px;
    }
    .hover-row {
      .show-whole-btn{
        background-color: #f0f1f5;
      }
    }
    td.bk-table-expanded-cell {
      padding: 0;
    }
    .bk-table-column-expand .bk-icon {
      top: 20px;
    }
    &.is-wrap .cell {
      display: inline-table;
    }
    .bk-table-empty-text {
      padding: 0;
      width: 100%;
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
// 日志全屏状态下的样式
.log-full-dialog {
  /deep/ .bk-dialog-content {
    margin-bottom: 0 !important;
  }
}
</style>
