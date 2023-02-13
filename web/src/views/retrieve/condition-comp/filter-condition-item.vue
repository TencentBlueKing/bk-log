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
  <div class="add-condition-filter-container">
    <bk-popover
      ref="conditionPopper"
      trigger="click"
      placement="bottom-start"
      theme="light"
      ext-cls="condition-filter-popper"
      :tippy-options="{ hideOnClick: false, boundary: 'window' }"
      :on-show="handlePopoverShow"
      :on-hide="handlePopoverHide">
      <span
        class="filter-text"
        v-if="isAdd"
        data-test-id="dataQuery_span_addConditions">
        {{ $t('添加条件') }}
      </span>
      <div class="condition-item-container" v-else>
        <div class="tag text-tag field-tag" v-bk-overflow-tips>
          <!-- <span class="bk-icon icon-close-circle-shape" @click="removeFilterCondition(coreData.field)"></span> -->
          {{ localData.field + (fieldAliasMap[localData.field] ? `(${fieldAliasMap[localData.field]})` : '')}}
        </div>
        <div class="tag symbol-tag">{{ localData.operator }}</div>
        <div class="tag text-tag" v-bk-overflow-tips>{{ formaterValue(localData.value) }}</div>
        <span class="bk-icon icon-close-line" @click.stop="removeFilterCondition(localData.field)"></span>
        <!-- <div class="tag symbol-tag" v-if="index !== filterCondition.length - 1">and</div> -->
      </div>
      <div class="add-condition-filter-popover" slot="content">
        <div class="filter-title">{{ $t('retrieve.addFilter') }}</div>
        <div class="add-filter-content">
          <div class="option-item">
            <label>{{ $t('indexSetList.field_name') }}</label>
            <bk-select
              :value="coreData.field"
              style="width: 240px;"
              data-test-id="addConditions_div_selectField"
              searchable
              :clearable="false"
              @change="handleFieldChange">
              <template v-for="option in filterFields">
                <bk-option :key="option.id" :id="option.id" :name="option.name"></bk-option>
              </template>
            </bk-select>
          </div>
          <div class="option-item" style="margin-right: 0">
            <label>{{ $t('indexSetList.operation') }}</label>
            <bk-select
              :value="coreData.operator"
              :clearable="false"
              @change="handleOperatorChange"
              data-test-id="addConditions_div_fieldFilter"
              style="width: 120px;">
              <template v-for="option in filterOperators">
                <bk-option
                  :key="option.operator"
                  :id="option.operator"
                  :name="option.label">
                </bk-option>
              </template>
            </bk-select>
          </div>
          <div class="option-item" v-if="!isShowValue">
            <label style="margin-left: 10px;">{{ $t('indexSetList.field_value') }}</label>
            <bk-tag-input
              v-model="coreData.value"
              style="width: 240px;"
              data-test-id="addConditions_input_valueFilter"
              allow-create
              allow-auto-match
              :paste-fn="pasteFn"
              :placeholder="filterPlaceholder"
              :list="valueList"
              :content-width="232"
              :max-data="getOperatorLength"
              @change="handleValueChange"
              @blur="handleValueBlur"
              trigger="focus">
            </bk-tag-input>
          </div>
        </div>
        <div class="filter-footer">
          <bk-button theme="primary" @click="handleConfirm">{{ $t('btn.confirm') }}</bk-button>
          <bk-button @click="handleCancel">{{ $t('btn.cancel') }}</bk-button>
        </div>
      </div>
    </bk-popover>
  </div>
</template>

<script>
export default {
  props: {
    isAdd: {
      type: Boolean,
      default: true,
    },
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
    filterAllOperators: {
      type: Object,
      required: true,
    },
    totalFields: {
      type: Array,
      required: true,
    },
    editData: {
      type: Object,
      default: () => ({}),
    },
    editIndex: {
      type: Number,
      default: -1,
    },
  },
  data() {
    return {
      coreData: {
        field: '',
        operator: '',
        value: [], // String or Array
      },
      localData: {
        field: '',
        operator: '',
        value: [], // String or Array
      },
      mappingKay: {
        '=': 'is',
        '!=': 'is not',
      },
      valueList: [{ id: '', name: `-${this.$t('空')}-` }], // 字段可选值列表
      filterPlaceholder: '',
      isHaveCompared: false, // 是否有大小对比的值
      showFilterPopover: false,
      isShowValue: false,
    };
  },
  computed: {
    filterFields() { // 剔除掉检索查询参数里面已有的过滤条件
      const result = [];
      this.totalFields.forEach((item) => {
        if (!this.operatorsKeyList.includes(item.field_type)) return;
        const fieldName = item.field_name;
        // if (item.field_type !== 'text' && !this.filterCondition.some(filterItem => filterItem.field === fieldName)) {
        // if (item.field_type !== 'text') { // 允许重复选择相同字段筛选条件
        //     const alias = this.fieldAliasMap[fieldName]
        //     if (alias && alias !== fieldName) {
        //         result.push({
        //             id: fieldName,
        //             name: `${fieldName}(${alias})`
        //         })
        //     } else {
        //         result.push({
        //             id: fieldName,
        //             name: fieldName
        //         })
        //     }
        // }
        const alias = this.fieldAliasMap[fieldName];
        if (alias && alias !== fieldName) {
          result.push({
            id: fieldName,
            name: `${fieldName}(${alias})`,
            operatorKey: item.field_type,
          });
        } else {
          result.push({
            id: fieldName,
            name: fieldName,
            operatorKey: item.field_type,
          });
        }
      });
      return result;
    },
    filterOperators() { // 过滤条件操作符
      const fieldsItem = this.filterFields.find(item => item.id === this.coreData.field);
      return this.filterAllOperators[fieldsItem?.operatorKey]?.map(item => ({
        ...item,
        operator: this.mappingKay[item.operator] ?? item.operator,
      })) || [];
    },
    getOperatorLength() { // 是否是对比的操作 如果是 则值限制只能输入1个
      return this.isHaveCompared ? 1 : -1;
    },
    operatorsKeyList() {  // 请求后的操作键名 用于过滤可选的字段
      return Object.keys(this.filterAllOperators);
    },
  },
  watch: {
    // 每次检索时请求更新
    statisticalFieldsData() {
      if (this.isAdd) {
        this.resetData();
      }
    },
  },
  created() {
    this.setDefaultEditValue();
  },
  mounted() {
    document.getElementById('app').addEventListener('click', this.closePopoverIfOpened);
  },
  beforeDestroy() {
    document.getElementById('app').removeEventListener('click', this.closePopoverIfOpened);
  },
  methods: {
    handlePopoverShow() {
      const operatorsFirstItem = Object.values(this.filterAllOperators)[0]?.[0];
      this.handleOperatorChange(operatorsFirstItem?.operator || 'is');
      this.setDefaultEditValue();
      this.showFilterPopover = true;
    },
    handlePopoverHide() {
      this.showFilterPopover = false;
    },
    formaterValue(value) {
      if (value.length === 1 && value[0] === '') {
        return `-${this.$t('空')}-`;
      }

      return value.join(',');
    },
    setDefaultEditValue() {
      if (this.isAdd) return;

      const params = {
        ...this.editData,
        value: this.editData.value.toString().split(','),
      };
      this.handleFieldChange(params.field);
      this.localData = params;
      this.$nextTick(() => {
        Object.assign(this.coreData, params, {});
      });
    },
    closePopoverIfOpened() {
      if (this.showFilterPopover) {
        this.$nextTick(() => {
          this.$refs.conditionPopper.instance.hide();
        });
      }
    },
    // 字段改变
    handleFieldChange(field) {
      const fieldItem = this.filterFields.find(item => item.id === field);
      const isNotShowNull = !['text', 'keyword'].includes(fieldItem?.operatorKey);
      this.coreData.value = [];
      this.valueList = isNotShowNull ? [] : [{ id: '', name: `-${this.$t('空')}-` }];
      this.coreData.field = field || '';
      this.handleOperatorChange(this.filterOperators[0]?.operator || 'is');
      if (field && this.statisticalFieldsData[field]) {
        const fieldValues = Object.keys(this.statisticalFieldsData[field]);
        if (fieldValues?.length) {
          this.valueList = fieldValues.map((item) => {
            const markList = item.toString().match(/(<mark>).*?(<\/mark>)/g) || [];
            if (markList.length) {
              item = markList.map(item => item.replace(/<mark>/g, '')
                .replace(/<\/mark>/g, '')).join(',');
            }
            return {
              id: item,
              name: item,
            };
          });
          if (!isNotShowNull) this.valueList.unshift({ id: '', name: `-${this.$t('空')}-` });
        }
      }
    },
    // 条件符号改变
    handleOperatorChange(operator) {
      this.coreData.operator = this.mappingKay[operator] ?? operator;
      if (['exists', 'does not exists'].includes(operator)) {
        this.coreData.value = [];
        this.valueList = [{ id: '', name: `-${this.$t('空')}-` }];
      }
      this.isShowValue = ['exists', 'does not exists'].includes(operator);
      this.isHaveCompared = ['<', '<=', '>', '>='].includes(operator);
      if (this.isHaveCompared) this.coreData.value = [this.coreData.value[0] || ''];
      for (const item of this.filterOperators) {
        if (item.operator === operator) {
          this.filterPlaceholder = item.placeholder || this.$t('form.pleaseEnter');
          break;
        }
      }
    },
    // 值改变
    handleValueChange(val) {
      if (!val.length) return;
      const newVal = val[val.length - 1];
      if (newVal === '') { // 选择了-空-过滤值
        this.coreData.value = [''];
      } else if (val.length && this.coreData.value.includes('')) { // 选择了有效值但已有选项中含有空值
        this.coreData.value = this.coreData.value.filter(item => item);
      }
    },
    // 当有对比的操作时 值改变
    handleValueBlur(val) {
      if (val === '' || !this.isHaveCompared) return;
      this.coreData.value = [val];
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
        if (this.coreData.field
                        && ((this.coreData.operator && this.coreData.value.length)
                            || (['exists', 'does not exists'].includes(this.coreData.operator)))) {
          this.closePopoverIfOpened();
          this.$emit(
            'addFilterCondition',
            this.coreData.field,
            this.coreData.operator,
            this.coreData.value.join(','),
            this.editIndex,
          );
          this.resetData();
          this.$nextTick(() => {
            this.setDefaultEditValue();
          });
        } else {
          this.messageError(this.$t('请输入完整的过滤条件'));
        }
      }, 220);
    },
    handleCancel() {
      this.closePopoverIfOpened();
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

<style lang="scss">
  .add-condition-filter-container {
    .condition-item-container {
      position: relative;
      display: flex;
      flex-flow: wrap;
      align-items: center;
      border-radius: 2px;
      margin-right: 8px;
      margin-bottom: 2px;
      padding: 0 22px 0 4px;
      background: #eceef5;
      cursor: pointer;
    }

    .filter-text {
      margin-left: 24px;
      color: #3a84ff;
      cursor: pointer;
    }

    .tag {
      padding: 0 4px;
      margin-bottom: 2px;
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

    .icon-close-line {
      position: absolute;
      right: 2px;
      top: 10px;
      display: none;
      margin: 0 6px;
      font-size: 12px;
      font-weight: 700;
      color: #979ba5;
      cursor: pointer;
    }

    .condition-item-container:hover {
      .icon-close-line {
        display: inline-block;
      }
    }
  }

  .add-condition-filter-popover {
    .filter-title {
      padding: 24px 24px 22px;
      color: #313238;
      font-size: 16px;
    }

    .add-filter-content {
      display: flex;
      align-items: center;
      margin-bottom: 24px;
      padding: 0 24px;

      label {
        display: inline-block;
        margin-bottom: 4px;
        color: #2d3542;
        font-size: 12px;
      }
    }

    .option-item:nth-child(2) {
      margin: 0 10px;
    }

    .filter-footer {
      padding: 8px 24px 10px 0;
      text-align: right;
      border-top: 1px solid #dcdee5;
      background-color: #fafbfd;

      .bk-primary {
        margin-right: 6px;
      }
    }

    .bk-tag-selector {
      .bk-tag-input {
        margin-left: 10px;
      }
    }
  }
</style>
