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
            :class="getFieldIcon(field) || 'log-icon icon-unkown'"
            v-bk-tooltips="fieldTypePopover(field)"
          ></span>
          <span :title="field">{{ field }}</span>
        </div>
        <div class="handle-option-list">
          <span
            v-for="(option) in toolMenuList"
            :key="option.id"
            :class="`icon ${getHandleIcon(option, field)} ${checkDisable(option.id, field)}`"
            @click.stop="handleMenuClick(option.id, field)">
          </span>
        </div>
        <div class="field-value">
          <text-segmentation
            :content="formatterStr(data, field)"
            :field-type="getFieldType(field)"
            :menu-click="(type, content) => handleMenuClick(type, content, field)">
          </text-segmentation>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import TextSegmentation from './TextSegmentation';
import tableRowDeepViewMixin from '@/mixins/tableRowDeepViewMixin';

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
  },
  data() {
    return {
      toolMenuList: [
        { id: 'is', icon: 'bk-icon icon-close-circle' },
        { id: 'not', icon: 'bk-icon icon-minus-circle' },
        { id: 'display', icon: 'bk-icon icon-arrows-up-circle' },
        // { id: 'chart', icon: 'log-icon icon-chart' },
        { id: 'copy', icon: 'log-icon icon-copy' },
      ],
    };
  },
  computed: {
    ...mapState('globals', ['fieldTypeMap']),
    fieldKeyMap() {
      return this.totalFields.map(item => item.field_name);
    },
    hiddenFields() {
      return this.fieldList.filter(item => !this.visibleFields.some(visibleItem => item === visibleItem));
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
      const iconMap = {
        number: 'log-icon icon-number',
        keyword: 'log-icon log-icon icon-string',
        text: 'log-icon icon-text',
        date: 'bk-icon icon-clock',
      };
      const fieldType = this.getFieldType(field);
      if (fieldType === 'long' || fieldType === 'integer') {
        return iconMap.number;
      }
      return iconMap[fieldType];
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
      return ['is', 'not'].includes(id) && type === 'text' ? 'is-disabled' : '';
    },
    handleMenuClick(operator, item, field) {
      let params = {};
      const curValue = this.tableRowDeepView(this.data, item, this.getFieldType(item), false);

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
      }

      if (Object.keys(params).length) this.$emit('menuClick', params);
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
          color: #3A84FF;
        }
      }
      .bk-icon {
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
      .icon-minus-circle {
        &.is-disabled {
          color: #dcdee5;
          cursor: not-allowed;
        }
      }
    }
  }
}
</style>
