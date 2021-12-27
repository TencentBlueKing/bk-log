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
    :clearable="false"
    :shortcuts="shortcuts"
    use-shortcut-text
    shortcut-close
    :value="timeValue"
    :open="showDatePicker"
    @change="handleDateChange"
    @shortcut-change="handleShortcutChange"
    @open-change="handleOpenChange">
    <div v-if="timeRange !== 'custom'" slot="trigger" class="king-date-trigger" @click.stop="togglePicker">
      <div class="bk-date-picker-editor" :class="{ 'is-focus': showDatePicker }">
        {{ shortTextEnum[timeRange] }}
      </div>
      <div class="icon-wrapper">
        <span class="log-icon icon-date-picker"></span>
      </div>
    </div>
  </bk-date-picker>
</template>

<script>
export default {
  props: {
    timeRange: {
      type: String,
      required: true,
    },
    timeValue: {
      type: Array,
      required: true,
    },
  },
  data() {
    const oneDay = 1000 * 60 * 60 * 24;
    const oneWeek = oneDay * 7;
    const oneMonth = oneDay * 30;
    return {
      showDatePicker: false,
      shortcuts: [{
        text: this.$t('近一天'),
        value() {
          const end = new Date();
          const start = new Date();
          start.setTime(start.getTime() - oneDay);
          return [start, end];
        },
      }, {
        text: this.$t('近一周'),
        value() {
          const end = new Date();
          const start = new Date();
          start.setTime(start.getTime() - oneWeek);
          return [start, end];
        },
      }, {
        text: this.$t('近一月'),
        value() {
          const end = new Date();
          const start = new Date();
          start.setTime(start.getTime() - oneMonth);
          return [start, end];
        },
      }, {
        text: this.$t('所有'),
        value() {
          const end = new Date();
          const start = new Date('2000-01-01');
          return [start, end];
        },
      }],
      shortTextEnum: {
        [this.$t('近一天')]: '1d',
        [this.$t('近一周')]: '1w',
        [this.$t('近一月')]: '1m',
        [this.$t('所有')]: 'all',
        '1d': this.$t('近一天'),
        '1w': this.$t('近一周'),
        '1m': this.$t('近一月'),
        all: this.$t('所有'),
      },
    };
  },
  methods: {
    togglePicker() {
      this.showDatePicker = !this.showDatePicker;
    },
    handleOpenChange(state) {
      this.showDatePicker = state;
    },
    handleDateChange(date) {
      // if (type !== undefined) console.log('日期选择事件')
      // else console.log('快捷键事件')
      this.$emit('update:timeValue', date);
    },
    handleShortcutChange(data) {
      if (data !== undefined) { // 快捷键事件
        this.$emit('update:timeRange', this.shortTextEnum[data.text]);
      } else { // 日期选择事件
        this.$emit('update:timeRange', 'custom');
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .king-date-picker {
    width: 300px;
    margin-right: 20px;
    background-color: #fff;

    .king-date-trigger {
      .icon-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;

        .icon-date-picker {
          font-size: 18px;
        }
      }

      .bk-date-picker-editor {
        transition: border-color .3s;

        &.is-focus {
          border-color: #3a84ff;
          transition: border-color .3s;
        }
      }
    }
  }
</style>
