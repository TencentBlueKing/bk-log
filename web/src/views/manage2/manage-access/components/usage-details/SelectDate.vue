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

    /deep/ .bk-date-picker-editor {
      background: #fff;
      line-height: 30px;

      &.is-focus {
        border-color: #3a84ff;
      }
    }
  }
</style>
