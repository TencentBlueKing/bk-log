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
  <div class="trace-detail-container">
    <div class="top-title-container">
      <h2 class="top-title">{{$route.query.traceId}}</h2>
    </div>
    <div class="main-container">
      <div :class="['chart-container', isCollapseChart && 'collapsed']" v-if="tableList.length">
        <transition name="zoom">
          <ChartTree
            ref="connectionChart"
            :tree="originTableList[0]"
            :config="chartTreeConfig"
            v-show="!isCollapseChart"
            @showSpanId="viewSpanDetail" />
        </transition>
        <div class="chart-side-bar">
          <div class="chart-name">{{$t('调用关系图')}}</div>
          <div class="icon-container collapse-icon" @click="isCollapseChart = !isCollapseChart">
            <span class="bk-icon icon-angle-up"></span>
          </div>
          <div class="icon-container shot-icon">
            <span class="log-icon icon-camera-fill" v-if="!isCollapseChart" @click="chartShot"></span>
          </div>
        </div>
      </div>
      <div class="button-container">
        <div class="button-left-container">
          <!-- 查看日志 -->
          <bk-button @click="isShowLog = true" :disabled="isLoading">{{$t('设置显示字段')}}</bk-button>
          <time-formatter style="margin-left: 16px;"></time-formatter>
          <div style="margin-left: 16px">
            <bk-switcher v-model="asyncSwitch" theme="primary"></bk-switcher>
            <span class="asyncSwitch">{{$t('仅显示同步请求')}}</span>
          </div>
        </div>
        <div
          :class="['fields-config', isLoading && 'disabled']"
          ref="fieldsConfigRef"
          v-bk-tooltips="fieldsConfigTooltip">
          <span class="log-icon icon-set-icon"></span>
        </div>
        <div id="fields-config-tippy">
          <!-- 字段显示设置 -->
          <h3 class="config-title">{{$t('设置显示字段')}}</h3>
          <ul class="config-list">
            <li v-for="field in fieldsConfigList" :key="field.field_name">
              <bk-checkbox :disabled="field.is_editable === false" v-model="field.is_display">
                {{field.field_alias || field.field_name}}
              </bk-checkbox>
            </li>
          </ul>
          <div class="config-buttons">
            <!-- 确定、取消按钮 -->
            <bk-button
              class="king-button"
              theme="primary"
              @click="confirmConfig">
              {{$t('确定')}}
            </bk-button>
            <bk-button class="king-button" @click="cancelConfig">{{$t('取消')}}</bk-button>
          </div>
        </div>
      </div>
      <div :class="['table-container', tableList.length === 0 && 'empty-data']" v-bkloading="{ isLoading }">
        <bk-table ref="table" :border="true" :row-style="computeRowStyle" :data="tableList">
          <!-- 表格字段数据 -->
          <template v-for="(field, index) in visibleFieldsList">
            <!-- 第一个字段、嵌套树结构展示 -->
            <bk-table-column
              v-if="index === 0"
              :key="field.field_name"
              :label="field.field_alias || field.field_name"
              min-width="240">
              <div
                slot-scope="{ row }" :class="['table-nesting-container', row.hasChildren && 'has-children']"
                :style="{ 'padding-left': row.tableLevel * 12 + 'px' }"
                @click="expandRow(row)">
                <div :class="['icon-container', row.showChildren && 'expanded']">
                  <span v-if="row.hasChildren" class="bk-icon icon-right-shape"></span>
                </div>
                <span
                  v-if="field.field_name === 'spanID'"
                  class="table-view-span-detail"
                  @click.stop="viewSpanDetail(row)">
                  {{row.spanID}}
                </span>
                <table-status
                  v-else-if="field.field_name === 'tags.error'"
                  :is-error="Boolean(row.tags.error)">
                </table-status>
                <span v-else>{{tableRowDeepView(row, field.field_name, field.field_type)}}</span>
              </div>
            </bk-table-column>

            <template v-else>
              <!-- spanID -->
              <bk-table-column
                v-if="field.field_name === 'spanID'"
                :key="field.field_name"
                :label="field.field_alias || field.field_name">
                <div class="table-ceil-container" slot-scope="{ row }">
                  <span
                    class="table-view-span-detail"
                    v-bk-overflow-tips
                    @click="viewSpanDetail(row)">
                    {{row.spanID}}
                  </span>
                </div>
              </bk-table-column>

              <!-- 成功/失败状态 -->
              <bk-table-column
                v-else-if="field.field_name === 'tags.error'"
                :key="field.field_name"
                :label="field.field_alias || field.field_name">
                <div slot-scope="{ row }">
                  <table-status :is-error="Boolean(row.tags.error)"></table-status>
                </div>
              </bk-table-column>

              <bk-table-column v-else :key="field.field_name" :label="field.field_alias || field.field_name">
                <div class="table-ceil-container" slot-scope="{ row }">
                  <span v-bk-overflow-tips>{{tableRowDeepView(row, field.field_name, field.field_type)}}</span>
                </div>
              </bk-table-column>
            </template>
          </template>

          <!-- 时序图 -->
          <bk-table-column :render-header="renderTimeRange" min-width="628">
            <div class="table-chart-bar-container" slot-scope="{ row }">
              <div class="table-chart-bar" :style="computeTimeBarStyle(row)">
                <div class="table-chart-text">{{row.to - row.from + 'ms'}}</div>
              </div>
            </div>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
    <bk-sideslider
      :title="$t('日志')"
      :width="1096"
      :is-show.sync="isShowLog"
      :quick-close="true">
      <view-log
        slot="content"
        :is-show-log="isShowLog"
        :log-list="logList"
        :log-fields="logFields">
      </view-log>
    </bk-sideslider>
    <bk-sideslider
      transfer
      ext-cls="span-detail-slider"
      :title="spanID"
      :width="640"
      :is-show.sync="isShowSpan"
      :quick-close="true">
      <div slot="content" class="span-detail-slot">
        <VueJsonPretty v-if="spanDetail" :data="spanDetail" />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import ViewLog from './view-log';
import TableStatus from '@/components/common/table-status';
import TimeFormatter from '@/components/common/time-formatter';
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';
import { convertDomToPng } from '@/common/util';
import ChartTree from './chart-tree';

export default {
  components: {
    ViewLog,
    TableStatus,
    TimeFormatter,
    ChartTree,
  },
  mixins: [tableRowDeepViewMixin],
  data() {
    return {
      asyncSwitch: false,
      isLoading: true,
      isCollapseChart: false,
      // 字段列表
      totalFieldsList: [],
      visibleFieldsList: [],
      // 字段显示设置时 clone totalFieldsList
      fieldsConfigList: [],
      // 字段显示设置tips配置
      isTooltipLoading: false,
      fieldsConfigTooltip: {
        allowHtml: true,
        width: 468,
        trigger: 'click',
        theme: 'light',
        extCls: 'fields-config-tooltip',
        content: '#fields-config-tippy',
        onShow: this.handleShowConfigTooltip,
      },
      // 树状图的配置字段
      chartTreeConfig: {
        display_field: 'operationName',
        error_field: 'tag.error',
        span_width: 120,
      },
      // 未经处理的表格数据
      originTableList: [],
      // 处理后的表格数据
      tableList: [],
      // 时序图相关的计算变量 绝对开始时间和相对范围
      tableMinFrom: 0,
      tableMaxRange: 0,
      // 默认展开的层级
      tableRowDefaultLevel: 3,

      // 查看日志
      isShowLog: false,
      logList: [],
      logFields: [],
      // 查看 span 详情
      isShowSpan: false,
      spanID: '',
      spanDetail: '',
    };
  },
  watch: {
    asyncSwitch() {
      const list = JSON.parse(JSON.stringify(this.originTableList));
      this.formatTableList(list, null, null);
    },
  },
  created() {
    this.initData();
  },
  methods: {
    async initData() {
      try {
        const { indexId, traceId, startTime } = this.$route.query;

        const [fieldRes, logRes, dataRes] = await Promise.all([
          this.$http.request('traceDetail/getTableField', {
            params: { index_set_id: indexId },
            query: { scope: 'trace_detail' },
          }),
          this.$http.request('traceDetail/getTableField', {
            params: { index_set_id: indexId },
            query: { scope: 'trace_detail_log' },
          }),
          this.$http.request('traceDetail/getTableData', {
            params: { index_set_id: indexId },
            query: { scope: 'trace_detail_log' },
            data: { startTime, traceID: traceId },
          }),
        ]);

        const { fields: totalFields, display_fields: displayFields, trace } = fieldRes.data;
        const { fields: logTotalFields, display_fields: logDisplayFields } = logRes.data;
        const { tree, list: logList } = dataRes.data;

        // eslint-disable-next-line camelcase
        trace?.chart_tree && (this.chartTreeConfig = trace.chart_tree);

        // 处理表头数据
        this.totalFieldsList = totalFields;
        this.visibleFieldsList = this.formatFieldsList(totalFields, displayFields);

        // 处理表格数据
        const resList = Object.keys(tree).length ? [tree] : []; // 如果 tree 是个空对象说明为空数据
        this.originTableList = JSON.parse(JSON.stringify(resList));
        this.formatTableList(resList, null, null);

        // 查看日志
        this.logList = logList;
        const logFields = [];
        logDisplayFields.forEach((fieldName) => {
          for (let i = 0; i < logTotalFields.length; i++) {
            const fieldInfo = logTotalFields[i];
            if (fieldInfo.field_name === fieldName) {
              logFields.push(fieldInfo);
              break;
            }
          }
        });
        this.logFields = logFields;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    /**
     * 处理表头字段数据 根据 display_fields 的顺序返回可见的字段
     * @param {Array} totalFields
     * @param {Array} displayFields
     * @return {Array}
     */
    formatFieldsList(totalFields, displayFields) {
      const fieldsList = [];

      displayFields.forEach((fieldName) => {
        for (let i = 0; i < totalFields.length; i++) {
          const fieldInfo = totalFields[i];
          if (fieldInfo.field_name === fieldName) {
            fieldsList.push(fieldInfo);
          }
        }
      });
      return fieldsList;
    },
    /**
     * 遍历递归处理表格数据
     * @param {Array} list
     * @param {Number} max 最大时间戳
     * @param {Number} min 最小时间戳
     * @return {Object}
     */
    formatTableList(list, max, min) {
      // 首轮循环
      let { length } = list;
      if (!length) {
        return { list: [], max: 0, min: 0 };
      }
      if (max === null) {
        max = list[0].to;
        min = list[0].from;
      }

      // 将树结构变成一个一维数组，通过给成员赋予变量实现样式交互上的树结构
      for (let i = 0; i < length; i++) {
        const item = list[i];

        min = item.from < min ? item.from : min;
        max = item.to > max ? item.to : max;

        // tableLevel 该成员在树结构中的层级
        item.tableLevel = item.tableParent ? item.tableParent.tableLevel + 1 : 0;

        // showItem 是否显示该成员
        item.showItem = item.tableLevel < this.tableRowDefaultLevel;

        if (item.children && item.children.length) {
          // hasChildren 该成员是否有子节点
          item.hasChildren = true;

          // showChildren 是否显示该成员的子节点
          item.showChildren = item.tableLevel < this.tableRowDefaultLevel - 1;

          // tableParent 子节点引用父节点
          const itemChildren = [];
          item.children.forEach((itemChild) => {
            if (this.asyncSwitch) {
              if (itemChild?.relationship && (itemChild.relationship !== 2)) {
                itemChild.tableParent = item;
                itemChildren.push(itemChild);
              }
            } else {
              itemChild.tableParent = item;
              itemChildren.push(itemChild);
            }
          });
          list.splice(i + 1, 0, ...itemChildren);
          length += itemChildren.length;
        }
      }
      this.tableList = list;
      this.tableMinFrom = min;
      this.tableMaxRange = max - min;
    },
    // 展开或收起行
    expandRow(item) {
      if (!item.hasChildren) {
        return;
      }

      const bool = !item.showChildren;
      item.showChildren = bool;
      item.children.forEach((itemChild) => {
        itemChild.showItem = bool;
        this.expandRowChild(itemChild, bool);
      });
    },
    // 爷爷关闭爸爸时，儿子也关闭，但是保留爸爸的 showChildren 以便下次开启时保留状态
    expandRowChild(item, bool) {
      if (item.hasChildren) {
        if (bool === true) {
          item.children.forEach((itemChild) => {
            itemChild.showItem = item.showChildren;
            this.expandRowChild(itemChild, item.showChildren);
          });
        } else if (bool === false) {
          item.children.forEach((itemChild) => {
            itemChild.showItem = false;
            this.expandRowChild(itemChild, false);
          });
        }
      }
    },
    // 根据 showItem 控制行样式
    computeRowStyle({ row }) {
      if (row.showItem === false) {
        return {
          display: 'none',
        };
      }
    },
    // 计算时序图宽度、边距样式
    computeTimeBarStyle(item) {
      const maxRange = this.tableMaxRange;
      const { from: fromTime, to } = item;
      const range = to - fromTime;

      return {
        width: `calc(100% * ${range / maxRange})`,
        'margin-left': `calc(100% * ${(fromTime - this.tableMinFrom) / maxRange})`,
      };
    },
    // 时序图表头样式
    renderTimeRange(h) {
      const maxRange = this.tableMaxRange;

      return h('div', {
        class: 'table-chart-header',
      }, [
        h('span', '0ms'),
        h(
          'span',
          { style: { position: 'absolute', left: '33.33%' } },
          `${Math.floor(maxRange / 3)}ms`,
        ),
        h(
          'span',
          { style: { position: 'absolute', left: '66.66%' } },
          `${Math.floor(maxRange / 3 * 2)}ms`,
        ),
        h('span', `${maxRange}ms`),
      ]);
    },
    // 显示字段设置
    handleShowConfigTooltip() {
      if (this.isLoading) {
        return false;
      }
      this.fieldsConfigList = JSON.parse(JSON.stringify(this.totalFieldsList));
    },
    // 确定设置显示字段
    confirmConfig() {
      const newFieldsList = this.fieldsConfigList.map((fieldInfo) => {
        if (fieldInfo.is_display) {
          return fieldInfo.field_name;
        }
        return false;
      }).filter(Boolean);
      this.postNewFieldsList(newFieldsList);
      this.$refs.fieldsConfigRef._tippy.hide();
    },
    // 设置新的显示字段
    async postNewFieldsList(newFieldsList) {
      try {
        this.isLoading = true;

        await this.$http.request('/traceDetail/postTableField', {
          params: { index_set_id: this.$route.query.indexId },
          query: { scope: 'trace_detail' },
          data: { display_fields: newFieldsList, sort_list: [] },
        });

        // 查询新的显示字段
        const res = await this.$http.request('traceDetail/getTableField', {
          params: { index_set_id: this.$route.query.indexId },
          query: { scope: 'trace_detail' },
        });
        const { fields: totalFields, display_fields: displayFields } = res.data;
        this.totalFieldsList = totalFields;
        this.visibleFieldsList = this.formatFieldsList(totalFields, displayFields);
        this.fieldsConfigList = [];
        this.messageSuccess(this.$t('设置成功'));
      } catch (e) {
        console.warn(e);
        this.$refs.fieldsConfigRef._tippy.show();
      } finally {
        this.isLoading = false;
      }
    },
    // 取消设置显示字段
    cancelConfig() {
      this.$refs.fieldsConfigRef._tippy.hide();
    },
    // 查看 span 详情
    viewSpanDetail({ spanID }) {
      this.isShowSpan = true;
      this.spanID = spanID;
      this.spanDetail = this.findSpanDetail(spanID, this.originTableList);
    },
    findSpanDetail(spanID, list) {
      for (let i = 0; i < list.length; i++) {
        const item = list[i];
        if (item.spanID === spanID) {
          const result = JSON.parse(JSON.stringify(item));
          result.children && delete result.children;
          return result;
        } if (item.children && item.children.length) {
          const deepResult = this.findSpanDetail(spanID, item.children);
          if (deepResult) {
            return deepResult;
          }
        }
      }

      return '';
    },

    // 截图图表
    chartShot() {
      convertDomToPng(this.$refs.connectionChart.$el, this.$route.query.traceId);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .trace-detail-container {
    height: 100%;
    color: #313238;
    font-size: 14px;

    .top-title-container {
      height: 61px;
      padding: 20px 0;
      margin: 0 60px;
      border-bottom: 1px solid #dde4eb;

      .top-title {
        margin: 0;
        padding-left: 10px;
        border-left: 2px solid #a3c5fd;
        line-height: 20px;
        font-size: 14px;
        font-weight: normal;
      }
    }

    .main-container {
      height: calc(100% - 61px);
      padding-bottom: 20px;
      overflow: auto;

      @include scroller($backgroundColor: #c4c6cc, $width: 4px);

      > div {
        width: calc(100% - 120px);
        margin-left: 60px;
      }

      .chart-container {
        position: relative;
        height: 460px;
        margin-top: 20px;
        background: #fff;
        overflow: hidden;
        border: 1px solid #dfe6ec;
        transition: height .3s;

        .chart-side-bar {
          position: absolute;
          top: 14px;
          left: 20px;
          display: flex;
          align-items: center;
          line-height: 20px;

          .icon-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 16px;
            height: 14px;
            margin-left: 10px;

            &.collapse-icon {
              background: #979ba5;
              border-radius: 2px;
              cursor: pointer;
              transition: background .2s;

              .bk-icon {
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                transition: transform .2s;
              }

              &:hover {
                background: #3a84ff;
                transition: background .2s;
              }
            }

            &.shot-icon {
              color: #979ba5;
              font-size: 20px;
              cursor: pointer;
              transition: color .2s;

              &:hover {
                color: #3a84ff;
                transition: color .2s;
              }
            }
          }
        }

        &.collapsed {
          height: 48px;
          transition: height .3s;

          .chart-side-bar .collapse-icon .bk-icon {
            transform: rotate(180deg);
            transition: transform .2s;
          }
        }
      }

      .button-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 32px;
        margin: 20px 0 20px 60px;

        .button-left-container {
          display: flex;
          align-items: center;
        }

        .fields-config {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          background: #fff;
          border: 1px solid #c4c6cc;
          border-radius: 2px;
          cursor: pointer;
          outline: none;

          .bk-icon {
            font-size: 12px;
          }

          &:hover {
            border-color: #979ba5;
            transition: border-color .2s;
          }

          &:active {
            border-color: #3a84ff;
            transition: border-color .2s;
          }

          &.disabled {
            color: #c4c6cc;
            border-color: #dcdee5;
            cursor: not-allowed;
          }
        }
      }

      .table-container {
        &.empty-data {
          height: 320px;
        }

        .table-chart-bar-container {
          display: flex;
          align-items: center;
          width: 100%;
          height: 40px;

          .table-chart-bar {
            position: relative;
            height: 10px;
            border-radius: 5px;
            background: #a3c5fd;
            overflow: visible;

            .table-chart-text {
              position: absolute;
              top: -13px;
              left: 0;
              width: 64px;
              line-height: 16px;
              color: #979ba5;
            }
          }
        }
      }
    }

    .asyncSwitch {
      display: inline-block;
      line-height: 30px;
      color: #63656e;
      margin-left: 5px;
    }
  }

  .span-detail-slider {
    .span-detail-slot {
      background: #313238;
      height: 100%;
      min-height: calc(100vh - 60px);
      color: #c4c6cc;
    }
  }
</style>

<style lang="scss">
  .fields-config-tooltip > .tippy-tooltip {
    padding: 0;
    border: 1px solid #dcdee5;

    #fields-config-tippy {
      .config-title {
        padding: 0 24px;
        margin-bottom: 14px;
        color: #313238;
        font-size: 24px;
        font-weight: normal;
      }

      .config-list {
        padding: 0 24px;
        width: 468px;
        display: flex;
        align-items: center;
        flex-flow: wrap;

        li {
          display: flex;
          align-items: center;
          width: 140px;
          height: 32px;
        }
      }

      .config-buttons {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 50px;
        margin-top: 16px;
        background: #fafbfd;
        border-top: 1px solid #dcdee5;

        .king-button {
          margin-right: 10px;
        }
      }

      .bk-form-checkbox .bk-checkbox-text {
        width: calc(100% - 22px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  .trace-detail-container {
    .bk-table-header-label {
      width: 100%;
    }

    .table-chart-header {
      position: relative;
      display: flex;
      justify-content: space-between;
      font-weight: normal;
    }

    .table-nesting-container {
      display: flex;
      align-items: center;
      height: 40px;

      &.has-children {
        cursor: pointer;

        &:hover {
          color: #3a84ff;

          .bk-icon {
            color: #3a84ff;
            transition: color .2s;
          }
        }
      }

      .icon-container {
        width: 12px;
        height: 12px;
        margin-right: 3px;
        transition: all .2s;

        &.expanded {
          transform: rotate(90deg);
          transition: all .2s;
        }

        .bk-icon {
          font-size: 12px;
          color: #c4c6cc;
          transition: color .2s;
        }
      }
    }

    .table-view-span-detail {
      color: #3a84ff;
      cursor: pointer;
    }
  }
</style>
