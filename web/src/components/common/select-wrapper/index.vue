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
  <bk-select
    v-model="value"
    :searchable="searchable"
    :multiple="multiSelect"
    :clearable="allowClear"
    :loading="isLoading"
    :disabled="disabled"
    :placeholder="calcPlaceHolder"
    :remote-method="remoteMethod"
    @selected="handleSelected"
    @toggle="handleToggle"
    @clear="handleClear"
    @change="handleChange">
    <div
      class="select-option-wrapper bk-scroll-ys"
      :style="calcStyle"
      v-scroll-bottom="{ callback: handleScrollCallback }">
      <template v-if="calcHasChild">
        <bk-option-group
          v-for="(group, index) in calcList"
          :name="group[groupKey] || group[displayKey] || group[settingKey]"
          :key="index">
          <bk-option
            v-for="(option, oIndex) in group.children"
            :key="oIndex"
            :id="option[settingKey]"
            :name="option[displayKey]"
            :disabled="!!option.disabled || !!group.isReadonly || !!group.disabled"
            @mouseenter.native="e => handleEnter(e, option)"
            @mouseleave.native="handleLeave">
          </bk-option>
        </bk-option-group>
      </template>
      <template v-else>
        <bk-option
          v-for="(option, index) in calcList"
          :key="index"
          :id="option[settingKey]"
          :name="option[displayKey]"
          :disabled="!!option.disabled"
          @mouseenter.native="e => handleEnter(e, option)"
          @mouseleave.native="handleLeave">
        </bk-option>
      </template>
    </div>
    <div slot="extension">
      <slot name="bottom-option"></slot>
    </div>
  </bk-select>
</template>

<script>
import scrollBottom from './scroll-bottom.js';
import tippy from 'tippy.js';

export default {
  name: 'BkdataSelector',
  directives: {
    scrollBottom,
  },
  components: {},
  props: {
    placeholder: {
      type: String,
      default: '',
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    hasCreateItem: {
      type: Boolean,
      default: false,
    },
    hasChildren: {
      type: [Boolean, String],
      default: false,
    },
    list: {
      type: Array,
      required: true,
    },
    selected: {
      type: [String, Number],
      required: true,
    },
    displayKey: {
      type: String,
      default: 'name',
    },
    groupKey: {
      type: String,
      default: 'name',
    },
    disabled: {
      type: [String, Boolean, Number],
      default: false,
    },
    multiSelect: {
      type: Boolean,
      default: false,
    },
    searchable: {
      type: Boolean,
      default: false,
    },
    searchKey: {
      type: String,
      default: null,
    },
    allowClear: {
      type: Boolean,
      default: false,
    },
    settingKey: {
      type: String,
      default: 'id',
    },
    optionTip: {
      type: Boolean,
      default: false,
    },
    toolTipTpl: {
      type: [String, Function],
      default: '',
    },
    customStyle: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      value: '',
      scrollHeight: 216,
      searchVal: '',
      currentPage: 1,
      pageSize: 100,
      currentPageUpdating: false,
      listSlideName: 'toggle-slide',
      timerId: 0,
      bkPopoverInstance: null,
      bkPopoverTimerId: 0,
      popoverWidth: '100%',
      popInstances: [],
    };
  },
  computed: {
    calcStyle() {
      return Object.assign({}, { 'max-height': `${this.scrollHeight}px`, width: this.popoverWidth }, this.customStyle);
    },
    calcHasChild() {
      return this.hasChildren === 'auto' ? this.list.some(item => item.children && Array.isArray(item.children)) : this.hasChildren;
    },
    calcPlaceHolder() {
      return this.placeholder || this.$t('btn.select');
    },
    isToolTipEnabled() {
      return this.optionTip;
    },
    calcSearchKey() {
      return this.searchable && (this.searchKey || this.displayKey);
    },
    searchedList() {
      if (!this.calcHasChild) {
        return this.orderListBySelectedValue().filter(item => this.stringToRegExp(this.searchVal, 'i').test(item[this.calcSearchKey]));
      }
      const cloneList = JSON.parse(JSON.stringify(this.orderListBySelectedValue()));
      return cloneList.map(item => Object.assign(item, {
        children: (item.children || []).filter(child => this.stringToRegExp(this.searchVal, 'ig').test(child[this.calcSearchKey])),
      })).filter(node => this.stringToRegExp(this.searchVal, 'i').test(node[this.groupKey || this.calcSearchKey]) || node.children.length);
    },
    calcList() {
      if (!this.calcHasChild) {
        return this.searchedList.slice(0, this.currentPage * this.pageSize);
      }
      if (this.searchedList.length) {
        const cloneList = JSON.parse(JSON.stringify(this.searchedList));
        const nodeSign = { groupIndex: 0, nodeIndex: 0, counted: 0 };
        const lastIndex = this.currentPage * this.pageSize;
        cloneList.some((item, index) => {
          nodeSign.groupIndex = index;
          const childeLen = Array.isArray(item.children) ? item.children.length : 0;
          if (nodeSign.counted + childeLen >= lastIndex) {
            nodeSign.nodeIndex = lastIndex - nodeSign.counted;
            return true;
          }
          nodeSign.counted += childeLen;
          return false;
        });

        const target = cloneList.slice(0, nodeSign.groupIndex + 1);
        if (nodeSign.nodeIndex) {
          target[nodeSign.groupIndex].children = target[nodeSign.groupIndex].children.slice(0, nodeSign.nodeIndex);
        }
        return target;
      }
      return this.searchedList;
    },
  },
  watch: {
    selected: {
      immediate: true,
      handler(val) {
        val !== this.value && this.$set(this, 'value', val);
      },
    },
    list() {
      this.currentPage = 1;
    },
    value(val, oldValue) {
      val !== oldValue && this.$emit('update:selected', val);
    },
  },
  mounted() {
    // this.createPopInsrance()
  },
  methods: {
    /** 重新排序列表，提升已选择的条目位置 */
    orderListBySelectedValue() {
      if (this.selected !== null && this.selected !== undefined && this.selected !== '') {
        /** 有字目录时，做排序，保证已选择模块在第一页显示 */
        if (this.calcHasChild) {
          return this.list.map((item) => {
            const orderItems = this.orderList(item.children);
            return Object.assign(item, {
              order: orderItems.isReOrdered ? 1 : 0,
              children: orderItems.newList,
            });
          }).sort((a, b) => b.order - a.order);
        }
        return this.orderList(this.list).newList;
      }
      return this.list;
    },

    /** 根据已选择的Value重新排序，保证已选择的条目在第一页就有，要不回填时显示会有问题 */
    orderList(list) {
      /** 筛选出已选择条目，包含只有一层，有Children，多选 */
      const compList = list.filter((item) => {
        const itemValue = typeof item === 'string' ? item : item[this.settingKey];
        if (Array.isArray(this.selected)) {
          return this.selected.includes(itemValue);
        }
        return itemValue === this.selected;
      });

      const hasSelectedItem = compList.length > 0;

      /** 筛选剩余条目 */
      const otherList = list.filter((other) => {
        const isString = typeof other === 'string';
        return !compList.some((item) => {
          const itemValue = isString ? item : item[this.settingKey];
          const otherValue = isString ? other : other[this.settingKey];
          return itemValue === otherValue;
        });
      });

      return {
        isReOrdered: hasSelectedItem,
        newList: compList.concat(otherList),
      };
    },
    stringToRegExp(pattern, flags) {
      // eslint-disable-next-line no-useless-escape
      return new RegExp(pattern.replace(/[\[\]\\{}()+*?.$^|]/g, match => `\\${match}`), flags);
    },
    handleEnter(e, option) {
      if (this.isToolTipEnabled) {
        this.bkPopoverTimerId && clearTimeout(this.bkPopoverTimerId);
        this.bkPopoverTimerId = setTimeout(() => {
          const popInstance = tippy(e.target, {
            content: this.getCalcTip(option),
            trigger: 'manual',
            theme: 'light',
            arrow: true,
            placement: 'left',
            popperOptions: {
              onCreate(data) {
                return updateTipPosition(data);
              },
              onUpdate(data) {
                return updateTipPosition(data);
              },
            },
          });
          this.fireInstance();
          popInstance && popInstance.show();
          this.popInstances.push(popInstance);
        }, 300);
      }

      function updateTipPosition(data) {
        const oldTransform = data.styles.transform;
        if (!/translateX\(100%\)/g.test(oldTransform)) {
          data.styles.transform += ' translateX(calc(100% + 20px))';
        }

        const instanceOldTransform = data.instance.popper.style.transform;
        if (!/translateX\(100%\)/g.test(instanceOldTransform)) {
          data.instance.popper.style.transform += ' translateX(calc(100% + 20px))';
        }
        return data;
      }
    },
    handleLeave() {
      if (this.isToolTipEnabled) {
        this.fireInstance();
      }
    },
    fireInstance() {
      while (this.popInstances.length) {
        const instance = this.popInstances[0];
        instance && instance.destroy();
        this.popInstances.shift();
      }
    },
    getCalcTip(option) {
      return (typeof this.toolTipTpl === 'function' && this.toolTipTpl(option)) || this.toolTipTpl || this.getDefaultTpl(option);
    },
    getDefaultTpl(option) {
      return `${this.displayKey}:${option[this.displayKey]}`;
    },
    handleScrollCallback() {
      const pageCount = this.getTotalCount();
      if (pageCount > this.currentPage && !this.currentPageUpdating) {
        this.currentPageUpdating = true;
        this.currentPage = this.currentPage + 1;
        this.$nextTick(() => {
          setTimeout(() => {
            this.currentPageUpdating = false;
          }, 300);
        });
      }
    },
    getTotalCount() {
      if (!this.hasChildren) {
        return Math.ceil(this.searchedList.length / this.pageSize);
      }
      const total = this.searchedList.reduce((pre, node) => {
        const childLen = Array.isArray(node.children) ? node.children.length : 0;
        pre += childLen + 1;
        return pre;
      }, 0);
      return Math.ceil(total / this.pageSize);
    },
    remoteMethod(val) {
      this.timerId && clearTimeout(this.timerId);
      this.timerId = setTimeout(() => {
        this.searchVal = val;
        this.currentPage = 1;
      }, 300);
    },
    handleSelected(value, option) {
      this.value = value;

      this.$nextTick(() => {
        let selectedItem = null;
        if (this.calcHasChild) {
          this.calcList.some(item => item.children.some((child) => {
            if (child[this.settingKey] === value) {
              selectedItem = child;
              return true;
            }
            return false;
          }));
        } else {
          selectedItem = this.calcList.find(item => item[this.settingKey] === value);
        }
        this.bkPopoverTimerId && clearTimeout(this.bkPopoverTimerId);
        this.fireInstance();
        this.$emit('item-selected', value, selectedItem, option);
      });
    },
    handleToggle(isOpen) {
      this.$emit('visible-toggle', isOpen);
    },
    handleClear(oldValue) {
      this.$emit('clear', oldValue);
      this.value = '';
    },
    handleChange(newValue, oldValue) {
      this.$emit('change', newValue, oldValue);
    },
  },
  // beforeDestory() {
  //     this.bkPopoverInstance && this.bkPopoverInstance.destroy(true)
  // }
};
</script>

<style lang="scss" scoped>
  .bkdata-select-popcontainer {
    position: absolute;
    min-width: 50px;
    min-height: 30px;
  }

  .select-option-wrapper {
    width: 100%;
    height: 100%;
  }

  .bk-select {
    width: 100%;
  }
</style>
