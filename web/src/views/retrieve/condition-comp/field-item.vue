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
  <li class="filed-item">
    <div class="filed-title" :class="{ 'expanded': isExpand }" @click="handleClickItem(fieldItem)">
      <!-- 三角符号 -->
      <span class="bk-icon" :class="{ 'icon-right-shape': showFieldsChart }"></span>
      <!-- 字段类型对应的图标 -->
      <span
        class="field-type-icon"
        :class="getFieldIcon(fieldItem.field_type) || 'log-icon icon-unkown'"
        v-bk-tooltips="{
          content: fieldTypeMap[fieldItem.field_type] && fieldTypeMap[fieldItem.field_type].name,
          disabled: !fieldTypeMap[fieldItem.field_type]
        }"
      ></span>
      <!-- 字段名 -->
      <span class="overflow-tips field-name" v-bk-overflow-tips>
        {{ showFieldAlias ? fieldAliasMap[fieldItem.field_name] : fieldItem.field_name }}
      </span>
      <!-- 聚合字段数量 -->
      <span class="field-count" v-if="isShowFieldsCount">{{ gatherFieldsCount }}</span>
      <!-- 设置字段显示或隐藏 -->
      <div
        class="operation-text"
        @click.stop="handleShowOrHiddenItem">
        {{ type === 'visible' ? $t('隐藏') : $t('显示') }}
      </div>
    </div>
    <!-- 显示聚合字段图表信息 -->
    <agg-chart
      v-if="showFieldsChart"
      v-show="isExpand"
      :retrieve-params="retrieveParams"
      :parent-expand="isExpand"
      :statistical-field-data="statisticalFieldData"
      :field-name="fieldItem.field_name"
      :field-type="fieldItem.field_type" />
  </li>
</template>

<script>
import { mapState } from 'vuex';
import AggChart from './agg-chart';

export default {
  components: {
    AggChart,
  },
  props: {
    type: {
      type: String,
      default: 'visible',
      validator: v => ['visible', 'hidden'].includes(v),
    },
    fieldItem: {
      type: Object,
      default() {
        return {};
      },
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
    statisticalFieldData: {
      type: Object,
      default() {
        return {};
      },
    },
    retrieveParams: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isExpand: false,
    };
  },
  computed: {
    ...mapState('globals', ['fieldTypeMap']),
    gatherFieldsCount() { // 聚合字段有多少个
      return Object.keys(this.statisticalFieldData).length;
    },
    // 显示融合字段统计比例图表
    showFieldsChart() {
      return Object.keys(this.statisticalFieldData).length && this.fieldItem.field_type !== 'text';
    },
    isShowFieldsCount() {
      return !['object', 'nested', 'text'].includes(this.fieldItem.field_type);
    },
  },
  methods: {
    getFieldIcon(fieldType) {
      return this.fieldTypeMap[fieldType] ? this.fieldTypeMap[fieldType].icon : 'log-icon icon-unkown';
    },
    // 点击字段行，展开显示聚合信息
    handleClickItem() {
      if (this.showFieldsChart) {
        this.isExpand = !this.isExpand;
      }
    },
    // 显示或隐藏字段
    handleShowOrHiddenItem() {
      this.$emit('toggleItem', this.type, this.fieldItem);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '@/scss/mixins/overflow-tips.scss';

  .filed-item {
    margin-bottom: 6px;

    .filed-title {
      position: relative;
      display: flex;
      align-items: center;
      height: 26px;
      padding-right: 50px;
      border-radius: 2px;
      cursor: pointer;

      .bk-icon {
        width: 12px;
        font-size: 12px;
        margin: 0 5px;
        transition: transform .3s;
      }

      .field-type-icon {
        width: 12px;
        margin: 0 5px 0 0;
        font-size: 12px;
        color: #979ba5;
      }

      .icon-ext {
        width: 18px;
        transform: scale(.8)
      }

      .field-count {
        min-width: 22px;
        line-height: 16px;
        text-align: center;
        padding: 0 4px;
        margin-left: 4px;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        background-color: #fafbfd;
      }

      .operation-text {
        position: absolute;
        right: 0;
        display: none;
        width: 40px;
        color: #3a84ff;
        text-align: center;

        &:active {
          color: #2761dd;
        }

        &:hover {
          color: #699df4;
        }
      }

      &:hover {
        background-color: #f4f5f8;

        .operation-text {
          display: block;
        }
      }

      &.expanded {
        background-color: #f0f1f5;

        .icon-right-shape {
          transform: rotate(90deg);
          transition: transform .3s;
        }
      }
    }
  }
</style>
