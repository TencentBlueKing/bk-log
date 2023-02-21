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
  <div :class="{ 'log-date-picker': true, 'is-custom-picker': isShowCustom }">
    <span class="bk-icon icon-clock custom-clock" v-if="isShowCustom"></span>
    <bk-date-picker
      :class="[
        'king-date-picker',
        isHome ? 'is-retrieve-home' : 'is-retrieve-detail',
        isShowCustom ? 'is-defalut-picker' : ''
      ]"
      type="datetimerange"
      format="yyyy-MM-dd HH:mm:ss"
      data-test-id="frontPageSearch_div_timeSelect"
      :placement="isHome ? 'bottom-start' : 'bottom-end'"
      :clearable="false"
      :editable="true"
      :open="isShowDatePicker"
      :shortcuts="shortcuts"
      :value="datePickerValue"
      @change="handleDateChange"
      @shortcut-change="handleShortcutChange"
      @open-change="handleOpenChange">
      <div
        v-if="!isHome && !customTime"
        slot="trigger"
        class="trigger"
        @click.stop="togglePicker">
        <span class="bk-icon icon-clock"></span>
        <span>{{ shortText || `${datePickerValue[0]} - ${datePickerValue[1]}` }}</span>
        <span class="bk-icon icon-angle-down" :class="isShowDatePicker && 'active'"></span>
      </div>
      <div v-else-if="shortText && !customTime" slot="trigger" @click.stop="togglePicker">
        <div :class="['bk-date-picker-editor', { 'is-focus': isShowDatePicker }]">
          {{ shortText }}
        </div>
        <div class="icon-wrapper">
          <span class="log-icon icon-date-picker"></span>
        </div>
      </div>
    </bk-date-picker>
    <span class="bk-icon icon-angle-down" :class="isShowDatePicker && 'active'" v-if="isShowCustom"></span>
  </div>
</template>

<script>
export default {
  props: {
    isHome: {
      type: Boolean,
      default: true,
    },
    timeRange: { // 显示自定义时间范围，customized 显示组件默认选择范围
      type: String,
      required: true,
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
      shortTextEnum: {
        customized: '',
        '5s': this.$t('近 5 秒'),
        '5m': this.$t('近 5 分钟'),
        '15m': this.$t('近 15 分钟'),
        '30m': this.$t('近 30 分钟'),
        '1h': this.$t('近 1 小时'),
        '4h': this.$t('近 4 小时'),
        '12h': this.$t('近 12 小时'),
        '1d': this.$t('近 1 天'),
        [this.$t('近 5 秒')]: '5s',
        [this.$t('近 5 分钟')]: '5m',
        [this.$t('近 15 分钟')]: '15m',
        [this.$t('近 30 分钟')]: '30m',
        [this.$t('近 1 小时')]: '1h',
        [this.$t('近 4 小时')]: '4h',
        [this.$t('近 12 小时')]: '12h',
        [this.$t('近 1 天')]: '1d',
      },
      shortcuts: [
        {
          text: this.$t('近 5 秒'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 5 * 1000);
            return [start, end];
          },
        }, {
          text: this.$t('近 5 分钟'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 5 * 60);
            return [start, end];
          },
        }, {
          text: this.$t('近 15 分钟'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 15 * 60);
            return [start, end];
          },
        }, {
          text: this.$t('近 30 分钟'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 30 * 60);
            return [start, end];
          },
        }, {
          text: this.$t('近 1 小时'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60);
            return [start, end];
          },
        }, {
          text: this.$t('近 4 小时'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 4);
            return [start, end];
          },
        }, {
          text: this.$t('近 12 小时'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 12);
            return [start, end];
          },
        }, {
          text: this.$t('近 1 天'),
          value() {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 1000 * 60 * 60 * 24);
            return [start, end];
          },
        }],
    };
  },
  computed: {
    shortText() {
      return this.shortTextEnum[this.timeRange];
    },
    customTime() { // 需要支持时间可编辑，当选择了具体时间时不展示slot内容
      return this.timeRange === 'customized';
    },
    isShowCustom() {
      return this.customTime && !this.isHome;
    },
  },
  mounted() {
    this.$store.commit('retrieve/updateCachePickerValue', [...this.datePickerValue]);
    this.$store.commit('retrieve/updateCacheTimeRange', this.timeRange);
    window.bus.$on('changeTimeByChart', this.handleChangeTimeByChart);
  },
  beforeDestroy() {
    window.bus.$off('changeTimeByChart', this.handleChangeTimeByChart);
  },
  methods: {
    togglePicker() {
      this.isShowDatePicker = !this.isShowDatePicker;
    },
    handleDateChange(date) {
      // if (type !== undefined) console.log('日期选择事件')
      // else console.log('快捷键事件')
      this.$store.commit('retrieve/updateCachePickerValue', date);
      this.$emit('update:datePickerValue', date);
    },
    handleShortcutChange(data) {
      if (data !== undefined) { // 快捷键事件
        const timeRange = this.shortTextEnum[data.text];
        this.$store.commit('retrieve/updateCacheTimeRange', timeRange);
        this.$emit('update:timeRange', timeRange);
        this.isShowDatePicker = false;
      } else { // 日期选择事件
        this.$store.commit('retrieve/updateCacheTimeRange', 'customized');
        this.$emit('update:timeRange', 'customized');
      }
    },
    handleOpenChange(state) {
      this.isShowDatePicker = state;
      // 因为事件可能会在日期数据变化前触发，所以需要等数据更新后再处理
      setTimeout(() => {
        if (state === true) {
          this.dateHistory = {
            timeRange: this.timeRange,
            time0: this.datePickerValue[0],
            time1: this.datePickerValue[1],
          };
        } else { // 关闭日期组件，检查值是否变化
          const { timeRange, time0, time1 } = this.dateHistory;
          if (this.timeRange !== 'customized') { // 快捷键模式
            if (timeRange !== this.timeRange) {
              this.$emit('datePickerChange');
            }
          } else { // 正常模式
            const [newTime0, newTime1] = this.datePickerValue;
            if (time0 !== newTime0 || time1 !== newTime1) {
              this.$emit('datePickerChange');
            }
          }
        }
      });
    },
    handleChangeTimeByChart(datePickerValue, timeRange) {
      this.$emit('update:datePickerValue', datePickerValue);
      this.$emit('update:timeRange', timeRange);
      window.bus.$emit('retrieveWhenChartChange');
    },
  },
};
</script>

<style lang="scss" scoped>
  .log-date-picker {
    display: flex;
    align-items: center;

    &.is-custom-picker {
      height: 52px;
      padding-left: 17px;
      border-left: 1px solid #f0f1f5;
    }

    .king-date-picker {
      &.is-retrieve-home {
        width: 320px;

        ::v-deep .bk-date-picker-editor {
          background: #fff;
          border-color: #fff;
          line-height: 30px;

          &.is-focus {
            border-color: #3a84ff;
          }
        }

        ::v-deep .icon-date-picker {
          position: absolute;
          left: 7px;
          top: 7px;
          font-size: 18px;
        }
      }

      &.is-retrieve-detail {
        width: auto;

        .trigger {
          display: flex;
          align-items: center;
          height: 52px;
          white-space: nowrap;
          line-height: 22px;
          cursor: pointer;

          .icon-clock {
            padding: 0 5px 0 17px;
            font-size: 14px;
            color: #63656e;
          }

          .icon-angle-down {
            margin: 0 10px;
            font-size: 22px;
            color: #63656e;
            transition: transform .3s;

            &.active {
              transform: rotate(-180deg);
              transition: transform .3s;
            }
          }

          &::before {
            content: '';
            width: 1px;
            height: 14px;
            background-color: #dcdee5;
            position: absolute;
            left: 0;
            top: 20px;
          }

          &:hover {
            color: #3a84ff;

            .icon-clock,
            .icon-angle-down {
              color: #3a84ff;
            }
          }
        }
      }

      &.is-defalut-picker {
        min-width: 268px;

        ::v-deep .bk-date-picker-editor {
          padding-left: 5px;
          padding-right: 0;
          border: none;
        }

        ::v-deep .icon-wrapper {
          display: none;
        }
      }
    }

    .custom-clock {
      font-size: 14px;
      color: #63656e;
    }

    .icon-angle-down {
      margin: 0 10px 0 0;
      font-size: 22px;
      color: #63656e;
      transition: transform .3s;

      &.active {
        transform: rotate(-180deg);
        transition: transform .3s;
      }
    }

    &.is-custom-picker:hover {
      .custom-clock,
      .icon-angle-down,
      ::v-deep .bk-date-picker-rel .bk-date-picker-editor {
        color: #3a84ff;
      }
    }
  }
</style>
