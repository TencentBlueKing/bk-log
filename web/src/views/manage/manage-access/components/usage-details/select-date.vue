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
  <bk-date-picker
    class="king-date-picker"
    type="datetimerange"
    format="yyyy-MM-dd HH:mm:ss"
    placement="bottom-end"
    :clearable="false"
    :editable="true"
    :disabled="disabled"
    :open="isShowDatePicker"
    :value="datePickerValue"
    @change="handleDateChange"
    @open-change="handleOpenChange">
  </bk-date-picker>
</template>

<script>
export default {
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    datePickerValue: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isShowDatePicker: false,
      dateHistory: {}, // 日期组件历史值，每次开启记录，关闭比较，变化就搜索
    };
  },
  methods: {
    togglePicker() {
      this.isShowDatePicker = !this.isShowDatePicker;
    },
    handleDateChange(date) {
      // if (type !== undefined) console.log('日期选择事件')
      // else console.log('快捷键事件')
      this.$emit('update:datePickerValue', date);
    },
    handleOpenChange(state) {
      this.isShowDatePicker = state;
      // 因为事件可能会在日期数据变化前触发，所以需要等数据更新后再处理
      setTimeout(() => {
        if (state === true) {
          this.dateHistory = {
            time0: this.datePickerValue[0],
            time1: this.datePickerValue[1],
          };
        } else { // 关闭日期组件，检查值是否变化
          const { time0, time1 } = this.dateHistory;
          const [newTime0, newTime1] = this.datePickerValue;
          if (time0 !== newTime0 || time1 !== newTime1) {
            this.$emit('datePickerChange');
          }
        }
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .king-date-picker {
    width: 320px;
    font-weight: normal;

    :deep(.bk-date-picker-editor) {
      background: #fff;
      line-height: 30px;

      &.is-focus {
        border-color: #3a84ff;
      }
    }
  }
</style>
