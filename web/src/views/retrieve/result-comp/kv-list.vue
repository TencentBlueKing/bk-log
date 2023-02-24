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
  <div class="kv-list-wrapper">
    <div class="kv-content">
      <div class="log-item" v-for="(field, index) in fieldKeyMap" :key="index">
        <div class="field-label">
          <span
            class="field-type-icon mr5"
            :class="getFieldIcon(field)"
            v-bk-tooltips="fieldTypePopover(field)"
          ></span>
          <span :title="field">{{ field }}</span>
        </div>
        <div class="handle-option-list">
          <span
            v-for="(option) in toolMenuList"
            :key="option.id"
            :class="`icon ${getHandleIcon(option, field)} ${checkDisable(option.id, field)}`"
            v-bk-tooltips="{ content: getIconPopover(option.id, field), delay: 300 }"
            @click.stop="handleMenuClick(option.id, field)">
          </span>
        </div>
        <div class="field-value">
          <text-segmentation
            :content="formatterStr(data, field)"
            :field-type="getFieldType(field)"
            :menu-click="(type, content) => handleMenuClick(type, content, field)"
          />
          <span
            v-if="getRelationMonitorField(field)"
            class="relation-monitor-btn"
            @click="handleViewMonitor(field)">
            <span>{{ getRelationMonitorField(field) }}</span>
            <i class="log-icon icon-jump"></i>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import TextSegmentation from './text-segmentation';
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';

export default {
  components: {
    TextSegmentation,
  },
  mixins: [tableRowDeepViewMixin],
  props: {
    data: {
      type: Object,
      default: () => {},
    },
    fieldList: {
      type: Array,
      default: () => [],
    },
    visibleFields: {
      type: Array,
      required: true,
    },
    totalFields: {
      type: Array,
      required: true,
    },
    kvShowFieldsList: {
      type: Array,
      require: true,
    },
    apmRelation: {
      type: Object,
      default: () => {},
    },
    sortList: {
      type: Array,
      require: true,
    },
    retrieveParams: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      toolMenuList: [
        { id: 'is', icon: 'bk-icon icon-enlarge-line search' },
        { id: 'not', icon: 'bk-icon icon-narrow-line search' },
        { id: 'display', icon: 'bk-icon icon-arrows-up-circle' },
        // { id: 'chart', icon: 'log-icon icon-chart' },
        { id: 'copy', icon: 'log-icon icon-copy' },
      ],
      toolMenuTips: {
        is: this.$t('添加 {n} 过滤项', { n: 'is' }),
        not: this.$t('添加 {n} 过滤项', { n: 'is not' }),
        hiddenField: this.$t('隐藏字段'),
        displayField: this.$t('显示字段'),
        copy: this.$t('复制'),
        text_is: this.$t('文本类型不支持 {n} 操作', { n: 'is' }),
        text_not: this.$t('文本类型不支持 {n} 操作', { n: 'is not' }),
      },
    };
  },
  computed: {
    ...mapState('globals', ['fieldTypeMap']),
    bkBizId() {
      return this.$store.state.bkBizId;
    },
    fieldKeyMap() {
      return this.totalFields.filter(item => this.kvShowFieldsList.includes(item.field_name)).map(el => el.field_name);
    },
    hiddenFields() {
      return this.fieldList.filter(item => !this.visibleFields.some(visibleItem => item === visibleItem));
    },
    filedSettingConfigID() { // 当前索引集的显示字段ID
      return this.$store.state.retrieve.filedSettingConfigID;
    },
  },
  methods: {
    formatterStr(row, field) {
      return this.tableRowDeepView(row, field, this.getFieldType(field));
    },
    getHandleIcon(option, field) {
      if (option.id !== 'display') return option.icon;

      const isDisplay = this.visibleFields.some(item => item.field_name === field);
      return `${option.icon} ${isDisplay ? 'is-hidden' : ''}`;
    },
    getFieldType(field) {
      const target = this.fieldList.find(item => item.field_name === field);
      return target ? target.field_type : '';
    },
    getFieldIcon(field) {
      const fieldType = this.getFieldType(field);
      return this.fieldTypeMap[fieldType] ? this.fieldTypeMap[fieldType].icon : 'log-icon icon-unkown';
    },
    fieldTypePopover(field) {
      const target = this.fieldList.find(item => item.field_name === field);
      const fieldType = target ? target.field_type : '';

      return {
        content: this.fieldTypeMap[fieldType] && this.fieldTypeMap[fieldType].name,
        disabled: !this.fieldTypeMap[fieldType],
      };
    },
    checkDisable(id, field) {
      const type = this.getFieldType(field);
      const isExist = this.filterIsExist(id, field);
      return (['is', 'not'].includes(id) && type === 'text') || type === '__virtual__' || isExist  ? 'is-disabled' : '';
    },
    getIconPopover(id, field) {
      const type = this.getFieldType(field);
      if (type === 'text' && ['is', 'not'].includes(id)) return this.toolMenuTips[`text_${id}`];
      if (type === '__virtual__' && ['is', 'not'].includes(id)) return this.$t('该字段为平台补充 不可检索');
      if (this.filterIsExist(id, field)) return this.$t('已添加过滤条件');
      if (id !== 'display') return this.toolMenuTips[id];

      const isDisplay = this.visibleFields.some(item => item.field_name === field);
      return this.toolMenuTips[isDisplay ? 'hiddenField' : 'displayField'];
    },
    handleMenuClick(operator, item, field) {
      let params = {};
      const curValue = this.tableRowDeepView(this.data, item, this.getFieldType(item), false);
      if (!field) {  // disable时操作禁用
        const disableStr = this.checkDisable(operator, item);
        if (disableStr === 'is-disabled') return;
      }
      if (['is', 'not'].includes(operator)) {
        if (!field && !this.getFieldType(item)) return;

        if (this.getFieldType(item) === 'text') return;

        if (!field && curValue === undefined) return;

        params = {
          fieldName: field ? field : item,
          operation: operator === 'is' ? 'is' : 'is not',
          value: field ? item : curValue,
        };
      }

      if (operator === 'copy') {
        if (!field && curValue === undefined) return;
        params.operation = 'copy';
        params.value = field ? item : curValue;
      }

      if (operator === 'display') {
        const displayFieldNames = this.visibleFields.map(field => field.field_name);
        const isDisplay = displayFieldNames.includes(item);
        if (isDisplay) {
          displayFieldNames.splice(displayFieldNames.indexOf(item), 1);
        } else {
          displayFieldNames.push(item);
        }
        params.operation = 'display';
        params.displayFieldNames = displayFieldNames;
        if (!displayFieldNames.length) return; // 可以设置为全部隐藏，但是不请求接口
      }

      if (Object.keys(params).length) this.$emit('menuClick', params);
    },
    /**
     * @desc 关联跳转
     * @param { string } field
     */
    handleViewMonitor(field) {
      let path = '';
      switch (field) {
        // trace检索
        case 'trace_id':
        case 'traceID':
          if (this.apmRelation.is_active) {
            const { app_name: appName, bk_biz_id: bkBizId } = this.apmRelation.extra;
            path = `/?bizId=${bkBizId}#/trace/home?app_name=${appName}&search_type=accurate&trace_id=${this.data[field]}`;
          } else {
            this.$bkMessage({
              theme: 'warning',
              message: this.$t('未找到相关的应用，请确认是否有Trace数据的接入。'),
            });
          }
          break;
        // 主机监控
        case 'serverIp':
        case 'ip':
          path = `/?bizId=${this.bkBizId}#/performance/detail/${this.data[field]}-0`;
          break;
        // 容器
        case 'container_id':
        case '__ext.container_id':
          path = `/?bizId=${this.bkBizId}#/k8s`;
          break;
        default:
          break;
      }

      if (path) {
        const url = `${window.MONITOR_URL}${path}`;
        window.open(url, '_blank');
      }
    },
    /**
     * @desc 判断是否有关联监控跳转
     * @param { string } field
     */
    getRelationMonitorField(field) {
      const key = field.toLowerCase();
      switch (key) {
        // trace检索
        case 'trace_id':
        case 'traceid':
          return this.$t('trace检索');
        // 主机监控
        case 'serverip':
        case 'ip':
          return this.$t('主机');
        // 容器
        case 'container_id':
        case '__ext.container_id':
          return this.$t('容器');
        default:
          return;
      }
    },
    filterIsExist(id, field) {
      if (this.retrieveParams?.addition.length) {
        if (id === 'not') id = 'is not';
        const curValue = this.tableRowDeepView(this.data, field, this.getFieldType(field), false);
        return this.retrieveParams.addition.some((addition) => {
          return addition.field === field
        && addition.operator === id
        && addition.value.toString() === curValue.toString();
        });
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .kv-list-wrapper {
    .log-item {
      display: flex;
      align-items: baseline;

      .field-label {
        width: 160px;
        min-width: 160px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        ::v-deep .icon-ext {
          width: 13px;
          display: inline-block;
          font-size: 12px;
          transform: translateX(-1px) scale(.8);
        }
      }

      .field-value {
        word-break: break-all;
      }

      .handle-option-list {
        flex-shrink: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0 20px;

        .icon {
          margin-right: 6px;
          font-size: 14px;
          cursor: pointer;

          &:hover {
            color: #3a84ff;
          }
        }

        .search {
          font-size: 16px;
        }

        .icon-arrows-up-circle {
          transform: rotate(45deg);
        }

        .icon-arrows-up-circle {
          margin-right: 2px;
          font-size: 12px;

          &.is-hidden {
            transform: rotate(225deg);
          }
        }

        .icon-chart {
          margin: 0 0 0 6px;
        }

        .icon-copy {
          transform: rotate(0);
          font-size: 24px;
          cursor: pointer;
        }

        .icon-close-circle,
        .icon-minus-circle,
        .icon-arrows-up-circle,
        .icon-copy {
          &.is-disabled {
            color: #dcdee5;
            cursor: not-allowed;
          }
        }
      }
    }

    .relation-monitor-btn {
      margin-left: 12px;
      color: #3a84ff;
      cursor: pointer;
    }
  }
</style>
