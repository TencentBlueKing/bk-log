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
  <div class="filter-condition-container">
    <template v-for="(item, index) in filterCondition">
      <div :key="item.field + 1" class="tag text-tag field-tag" v-bk-overflow-tips>
        <span class="bk-icon icon-close-circle-shape" @click="removeFilterCondition(item.field)"></span>
        {{ item.field + (fieldAliasMap[item.field] ? `(${fieldAliasMap[item.field]})` : '')}}
      </div>
      <div :key="item.field + 2" class="tag symbol-tag">{{ item.operator }}</div>
      <div :key="item.field + 3" class="tag text-tag" v-bk-overflow-tips>{{ item.value }}</div>
      <div :key="item.field + 4" class="tag symbol-tag" v-if="index !== filterCondition.length - 1">and</div>
    </template>
    <!-- 添加 -->
    <div class="tag add-tag" @click="showDialog = true">
      <span class="bk-icon icon-plus-line"></span>
      <span class="add-text" v-if="!filterCondition.length">{{ $t('添加条件') }}</span>
    </div>

    <bk-dialog
      v-model="showDialog"
      header-position="left"
      :title="$t('retrieve.addFilter')"
      :ok-text="$t('btn.add')"
      :width="680"
      :mask-close="false"
      :esc-close="false"
      :draggable="false"
      :auto-close="false"
      @confirm="handleConfirm"
      @cancel="resetData">
      <div class="add-filter-dialog">
        <bk-select
          :value="coreData.field"
          style="width: 240px;"
          searchable
          :clearable="false"
          @change="handleFieldChange">
          <template v-for="option in filterFields">
            <bk-option :key="option.id" :id="option.id" :name="option.name"></bk-option>
          </template>
        </bk-select>
        <bk-select
          :value="coreData.operator"
          style="width: 120px;margin: 0 10px;"
          :clearable="false"
          @change="handleOperatorChange">
          <template v-for="option in filterOperators">
            <bk-option :key="option.operator" :id="option.operator" :name="option.label"></bk-option>
          </template>
        </bk-select>
        <bk-tag-input
          v-model="coreData.value"
          style="width: 240px;"
          allow-create
          allow-auto-match
          :paste-fn="pasteFn"
          :placeholder="filterPlaceholder"
          :list="valueList"
          trigger="focus">
        </bk-tag-input>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
export default {
  props: {
    filterCondition: { // 过滤条件查询参数
      type: Array,
      required: true,
    },
    fieldAliasMap: {
      type: Object,
      default() {
        return {};
      },
    },
    statisticalFieldsData: { // 过滤条件字段可选值关系表
      type: Object,
      required: true,
    },
    totalFields: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      coreData: {
        field: '',
        operator: '',
        value: [], // String or Array
      },

      filterOperators: [], // 过滤条件操作符
      valueList: [], // 字段可选值列表
      filterPlaceholder: '',

      showDialog: false,
    };
  },
  computed: {
    filterFields() { // 剔除掉检索查询参数里面已有的过滤条件
      const result = [];
      this.totalFields.forEach((item) => {
        const fieldName = item.field_name;
        if (item.field_type !== 'text' && !this.filterCondition.some(filterItem => filterItem.field === fieldName)) {
          const alias = this.fieldAliasMap[fieldName];
          if (alias && alias !== fieldName) {
            result.push({
              id: fieldName,
              name: `${fieldName}(${alias})`,
            });
          } else {
            result.push({
              id: fieldName,
              name: fieldName,
            });
          }
        }
      });
      return result;
    },
  },
  watch: {
    // 每次检索时请求更新
    statisticalFieldsData() {
      this.resetData();
    },
    filterFields(val) {
      this.handleFieldChange(val[0]?.id);
    },
  },
  created() {
    // 请求过滤条件符号
    this.$http.request('retrieve/getOperators').then((res) => {
      this.filterOperators = res.data;
      this.handleOperatorChange(res.data?.[0].operator || 'is');
    })
      .catch(e => console.warn(e));
  },
  methods: {
    // 字段改变
    handleFieldChange(field) {
      this.coreData.value = [];
      this.valueList = [];
      this.coreData.field = field || '';
      if (field && this.statisticalFieldsData[field]) {
        const fieldValues = Object.keys(this.statisticalFieldsData[field]);
        if (fieldValues?.length) {
          this.valueList = fieldValues.map(item => ({ id: item, name: item }));
        }
      }
    },
    // 条件符号改变
    handleOperatorChange(operator) {
      this.coreData.operator = operator;
      for (const item of this.filterOperators) {
        if (item.operator === operator) {
          this.filterPlaceholder = item.placeholder || this.$t('form.pleaseEnter');
          break;
        }
      }
    },
    // 粘贴过滤条件
    pasteFn(pasteValue) {
      if (!this.coreData.value.includes(pasteValue)) {
        this.coreData.value.push(pasteValue);
      }
    },
    handleConfirm() {
      // 延时220ms执行，因为tag-input组件值失焦后200ms才改变
      setTimeout(() => {
        if (this.coreData.field && this.coreData.operator && this.coreData.value.length) {
          this.showDialog = false;
          this.$emit('addFilterCondition', this.coreData.field, this.coreData.operator, this.coreData.value.join(','));
          this.resetData();
        } else {
          this.messageError(this.$t('请输入完整的过滤条件'));
        }
      }, 220);
    },
    resetData() {
      this.handleFieldChange(this.filterFields[0]?.id);
    },
    removeFilterCondition(field) {
      this.$emit('removeFilterCondition', field);
    },
  },
};
</script>

<style lang="scss" scoped>
  .filter-condition-container {
    display: flex;
    flex-flow: wrap;

    .tag {
      padding: 0 10px;
      margin-right: 2px;
      margin-bottom: 2px;
      background: #eceef5;
      border-radius: 2px;
      font-size: 12px;
      color: #63656e;
      line-height: 32px;
      white-space: nowrap;

      &.text-tag {
        max-width: 108px;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      &.symbol-tag {
        color: #ff9c01;
      }

      &.field-tag {
        position: relative;

        .icon-close-circle-shape {
          display: none;
          position: absolute;
          right: 0;
          top: 0;
          cursor: pointer;
          font-size: 16px;
        }

        &:hover {
          .icon-close-circle-shape {
            display: block;

            &:hover {
              color: #ea3636;
            }
          }
        }
      }

      &.add-tag {
        padding: 0 7px;
        cursor: pointer;

        .icon-plus-line {
          font-size: 14px;
        }

        .add-text {
          margin-right: 3px;
        }

        &:hover {
          color: #3a84ff;
        }
      }
    }
  }

  .add-filter-dialog {
    display: flex;
    align-items: center;
    margin-bottom: 14px;
  }
</style>
