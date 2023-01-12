/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import { mapState } from 'vuex';
import { formatDate, random, copyMessage } from '@/common/util';
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';
import EventPopover from '@/views/retrieve/result-comp/event-popover.vue';
import RegisterColumn from '@/views/retrieve/result-comp/register-column.vue';
import TextHighlight from 'vue-text-highlight';
import OperatorTools from '@/views/retrieve/result-table-panel/original-log/operator-tools';
import RetrieveLoader from '@/skeleton/retrieve-loader';
import TableColumn from '@/views/retrieve/result-comp/table-column';
import ExpandView from '@/views/retrieve/result-table-panel/original-log/expand-view.vue';
import EmptyView from '@/views/retrieve/result-table-panel/original-log/empty-view';

export default {
  components: {
    EventPopover,
    TextHighlight,
    OperatorTools,
    RetrieveLoader,
    TableColumn,
    ExpandView,
    RegisterColumn,
    EmptyView,
  },
  mixins: [tableRowDeepViewMixin],
  props: {
    tableList: {
      type: Array,
      required: true,
    },
    originTableList: {
      type: Array,
      required: true,
    },
    totalFields: {
      type: Array,
      required: true,
    },
    visibleFields: {
      type: Array,
      required: true,
    },
    showFieldAlias: {
      type: Boolean,
      default: false,
    },
    fieldAliasMap: {
      type: Object,
      default: () => { },
    },
    isWrap: {
      type: Boolean,
      default: false,
    },
    retrieveParams: {
      type: Object,
      required: true,
    },
    tableLoading: {
      type: Boolean,
      required: true,
    },
    isPageOver: {
      type: Boolean,
      required: false,
    },
    timeField: {
      type: String,
      default: '',
    },
    operatorConfig: {
      type: Object,
      required: true,
    },
    handleClickTools: Function,
  },
  data() {
    return {
      formatDate,
      curHoverIndex: -1, // 当前鼠标hover行的索引
      cacheExpandStr: [], // 记录展开收起的行
      cacheOverFlowCol: [], // 记录超出四行高度的列
      tableRandomKey: '',
    };
  },
  computed: {
    ...mapState('globals', ['fieldTypeMap']),
    showHandleOption() {
      if (this.visibleFields.length !== 0) {
        const columnObj = JSON.parse(localStorage.getItem('table_column_width_obj'));
        const { params: { indexId }, query: { bizId } } = this.$route;
        let widthObj = {};

        for (const bizKey in columnObj) {
          if (bizKey === bizId) {
            for (const fieldKey in columnObj[bizId].fields) {
              fieldKey === indexId && (widthObj = columnObj[bizId].fields[indexId]);
            }
          }
        }

        this.visibleFields.forEach((el, index) => {
          el.width = widthObj[index] === undefined ? 'default' : widthObj[index];
        });
      }
      return this.tableList.length;
    },
  },
  watch: {
    retrieveParams: {
      deep: true,
      handler() {
        this.cacheExpandStr = [];
        this.cacheOverFlowCol = [];
      },
    },
    '$route.params.indexId'() { // 切换索引集重置状态
      this.cacheExpandStr = [];
      this.cacheOverFlowCol = [];
    },
    visibleFields: {
      deep: true,
      handler() {
        this.tableRandomKey = random(6);
      },
    },
  },
  methods: {
    handleShowWhole(index) {
      this.cacheExpandStr.push(index);
    },
    handleHideWhole(index) {
      this.cacheExpandStr = this.cacheExpandStr.map(item => item !== index);
    },
    handleOverColumn(fieldName) {
      if (!this.cacheOverFlowCol.includes(fieldName)) this.cacheOverFlowCol.push(fieldName);
    },
    getMarkList(content) {
      // 匹配高亮标签
      let markList = [];

      const markVal = content.match(/(<mark>).*?(<\/mark>)/g) || [];
      if (markVal.length) {
        markList = markVal.map(item => item.replace(/<mark>/g, '')
          .replace(/<\/mark>/g, ''));
      }

      return markList;
    },
    formatterStr(content) {
      // 匹配高亮标签
      let value = content;

      const markVal = content.match(/(<mark>).*?(<\/mark>)/g) || [];
      if (markVal.length) {
        value = String(value).replace(/<mark>/g, '')
          .replace(/<\/mark>/g, '');
      }

      return value;
    },
    // 展开表格行JSON
    tableRowClick(row, option, column) {
      if (column.className && column.className.includes('original-str')) return;
      const ele = this.$refs.resultTable;
      ele.toggleRowExpansion(row);
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
    // eslint-disable-next-line no-unused-vars
    renderHeaderAliasName(h, { column, $index }) {
      const field = this.visibleFields[$index - 1];
      if (field) {
        const fieldName = this.showFieldAlias ? this.fieldAliasMap[field.field_name] : field.field_name;
        const fieldType = field.field_type;
        const fieldIcon = this.getFieldIcon(field.field_type);
        const content = this.fieldTypeMap[fieldType] ? this.fieldTypeMap[fieldType].name : undefined;

        return h('div', {
          class: 'render-header',
        }, [
          h('span', {
            class: `field-type-icon ${fieldIcon}`,
            style: {
              marginRight: '4px',
            },
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
        copyMessage(value);
      } else if (['is', 'is not'].includes(type)) {
        this.$emit('addFilterCondition', field.field_name, type, value === '--' ? '' : value.toString());
      }
    },
    getFieldIcon(fieldType) {
      return this.fieldTypeMap[fieldType] ? this.fieldTypeMap[fieldType].icon : 'log-icon icon-unkown';
    },
    handleMenuClick(option) {
      switch (option.operation) {
        case 'is':
        case 'is not':
          // eslint-disable-next-line no-case-declarations
          const { fieldName, operation, value } = option;
          this.$emit('addFilterCondition', fieldName, operation, value === '--' ? '' : value.toString());
          break;
        case 'copy':
          copyMessage(option.value);
          break;
        case 'display':
          this.$emit('fieldsUpdated', option.displayFieldNames, undefined, false);
          break;
        default:
          break;
      }
    },
  },
};
