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
  <section class="log-view">
    <pre id="log-content">
      <div
      v-for="(item, index) in escapedReverseLogList"
      :key="item.replace(/\s/g, '') + index"
        class="line"
        v-show="checkLineShow(item, index, 'reverse')">
        <span class="line-num">{{ index - reverseLogList.length }}</span>
        <highlight-html
          v-if="showHighlight(item)"
          :item="item"
          :filter-key="filterKey"
          :ignore-case="ignoreCase"
        ></highlight-html>
        <span v-if="checkTextShow(item, index, 'reverse')" class="line-text">{{ item }}</span>
    </div>
    <div
      v-for="(item, index) in escapedLogList"
      :key="item.replace(/\s/g, '') + index"
      :class="['line', { 'log-init': index === 0, 'new-log-line': newIndex && index >= newIndex }]"
      v-show="checkLineShow(item, index, 'normal')">
      <span class="line-num">{{ index }}</span>
      <highlight-html
        v-if="showHighlight(item)"
        :item="item"
        :filter-key="filterKey" />
      <span class="line-text" v-show="checkTextShow(item, index, 'normal')">{{ item }}</span>
    </div>
  </pre>
  </section>
</template>

<script>
import HighlightHtml from './highlight-html';

export default {
  name: 'LogView',
  components: {
    HighlightHtml,
  },
  props: {
    reverseLogList: {
      type: Array,
      default() {
        return [];
      },
    },
    logList: {
      type: Array,
      default() {
        return [];
      },
    },
    filterKey: {
      type: String,
      default: '',
    },
    isRealTimeLog: {
      type: Boolean,
      default: false,
    },
    maxLength: {
      type: Number,
      default: 0,
    },
    shiftLength: {
      type: Number,
      default: 0,
    },
    interval: {
      type: Object,
      default: () => ({}),
    },
    filterType: {
      type: String,
      default: '',
    },
    ignoreCase: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      oldIndex: null,
      newIndex: null,
      intervalTime: null,
      resRangeIndexs: [],
      reverseResRangeIndexs: [],
    };
  },
  computed: {
    escapedLogList() {
      return this.logList.map(this.escapeString);
    },
    escapedReverseLogList() {
      return this.reverseLogList.map(this.escapeString);
    },
    isIncludeFilter() {
      return this.filterType === 'include';
    },
  },
  watch: {
    logList(val) {
      if (this.isRealTimeLog) {
        // 实时日志记录新增日志索引
        if (this.oldIndex) {
          this.newIndex = this.oldIndex;
          this.oldIndex = val.length;
        } else {
          this.oldIndex = val.length;
        }
        // 超过限制长度的处理
        if (val.length > this.maxLength) {
          this.oldIndex = this.oldIndex - this.shiftLength;
        }
      }
    },
    escapedReverseLogList() {
      if (this.filterKey.length) {
        this.setResRange();
      }
    },
    filterKey(val) {
      if (val.length) {
        this.setResRange();
      } else {
        this.reverseResRangeIndexs.splice(0, this.reverseResRangeIndexs.length);
        this.resRangeIndexs.splice(0, this.resRangeIndexs.length);
      }
    },
    interval: {
      deep: true,
      handler() {
        clearTimeout(this.intervalTime);
        this.intervalTime = setTimeout(() => {
          if (this.filterKey.length) {
            this.setResRange();
          }
        }, 500);
      },
    },
    ignoreCase() {
      this.setResRange();
    },
  },
  methods: {
    checkLineShow(item, index, field) {
      if (this.isIncludeFilter) {
        const list = field === 'reverse' ? this.reverseResRangeIndexs : this.resRangeIndexs;
        return this.handleMatch(item) || list.includes(index);
      }
      return this.filterKey.length ? !this.handleMatch(item) : true;
    },
    showHighlight(item) {
      return this.filterKey.length && this.handleMatch(item);
    },
    checkTextShow(item, index, field) {
      if (this.isIncludeFilter) {
        const list = field === 'reverse' ? this.reverseResRangeIndexs : this.resRangeIndexs;
        return !this.filterKey.length || (!this.showHighlight(item) && list.includes(index));
      }
      return item;
    },
    handleMatch(key) {
      let { filterKey } = this;
      const keyVal = this.ignoreCase ? key : key.toLowerCase();
      filterKey = this.ignoreCase ? filterKey : filterKey.toLowerCase();

      return keyVal.includes(filterKey);
    },
    escapeString(val) {
      if (typeof val !== 'string') return '';
      const map = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#x27;': '\'',
      };
      return val.replace(RegExp(`(${Object.keys(map).join('|')})`, 'g'), match => map[match]);
    },
    setResRange() {
      this.resRangeIndexs.splice(0, this.resRangeIndexs.length);
      this.reverseResRangeIndexs.splice(0, this.reverseResRangeIndexs.length);
      const reverListLen = this.escapedReverseLogList.length;
      const listLen = this.escapedLogList.length;
      let resExtra = 0;
      let reverseResExtra = 0;

      // 根据前后行数缓存索引
      this.escapedReverseLogList.forEach((item, index) => {
        if (this.handleMatch(item)) {
          const min = index - Number(this.interval.prev);
          const max = index + Number(this.interval.next);
          const minVal = min < 0 ? 0 : min;
          const maxVal = max >= reverListLen ? (reverListLen - 1) : max;

          if (max >= reverListLen) resExtra = Math.abs(max - index);

          for (let i = minVal; i <= maxVal; i++) {
            this.reverseResRangeIndexs.push(i);
          }
        }
      });

      // 根据前后行数缓存索引
      this.escapedLogList.forEach((item, index) => {
        if (this.handleMatch(item)) {
          const min = index - Number(this.interval.prev);
          const max = index + Number(this.interval.next);
          const minVal = min < 0 ? 0 : min;
          const maxVal = max >= listLen ? (listLen - 1) : max;

          if (min < 0) reverseResExtra = Math.abs(min);

          for (let i = minVal; i <= maxVal; i++) {
            this.resRangeIndexs.push(i);
          }
        }
      });

      if (resExtra) {
        for (let i = 0; i < resExtra; i++) {
          if (!this.resRangeIndexs.includes(i)) {
            this.resRangeIndexs.push(i);
          }
        }
      }

      if (reverseResExtra) {
        for (let i = 0; i < reverseResExtra; i++) {
          const index = this.escapedReverseLogList.length - i - 1;
          if (!this.reverseResRangeIndexs.includes(index)) {
            this.reverseResRangeIndexs.push(index);
          }
        }
      }
    },
  },
};
</script>

<style lang="scss">
  @import '../../scss/mixins/clearfix';

  .log-view {
    min-height: 100%;
    color: #979ba5;
    background: #222;

    #log-content {
      box-sizing: border-box;
      margin: 0;
      font-size: 0;

      .line {
        display: flex;
        flex-direction: row;
        margin: 0;
        padding: 0 15px 0 55px;
        min-height: 16px;
        font-size: 12px;

        &.log-init {
          background: #5f3a3a;
        }

        &.new-log-line {
          background: #5f3a3a;
        }

        &:hover {
          background-color: #383838;
        }
      }

      .line-num {
        display: inline-block;
        margin-left: -37px;
        padding-right: 12px;
        min-width: 32px;
        line-height: 24px;
        text-align: right;
        color: #5f697d;
        user-select: none;
      }

      .line-text {
        line-height: 24px;
        white-space: pre-wrap;
        word-wrap: break-word;
        word-break: break-all;
      }
    }
  }
</style>
