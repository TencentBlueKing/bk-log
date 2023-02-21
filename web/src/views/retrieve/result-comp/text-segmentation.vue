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
  <span class="log-content-wrapper">
    <text-highlight
      v-if="!isNeedSegment"
      style="word-break: break-all;"
      :queries="markList">
      {{formatterStr(content)}}
    </text-highlight>
    <span v-else class="segment-content">
      <template
        v-for="(item, index) in splitList">
        <!-- 换行 -->
        <br :key="index" v-if="item === '\n'">
        <!-- 分割符 -->
        <template v-else-if="segmentReg.test(item)">{{item}}</template>
        <!-- 高亮 -->
        <mark
          :key="index"
          v-else-if="checkMark(item)"
          @click="handleClick($event, item)">{{item}}</mark>
        <!-- 可操作分词 -->
        <span
          :key="index"
          v-else-if="index < (segmentLimitIndex)"
          class="valid-text"
          @click="handleClick($event, item)">{{item}}</span>
        <template v-else>{{item}}</template>
      </template>
    </span>

    <div v-show="false">
      <div ref="moreTools" class="event-icons">
        <span
          class="icon bk-icon icon-close-circle"
          v-bk-tooltips.top="{ content: `${$t('添加')} is ${$t('过滤项')}`, delay: 300 }"
          @click="handleMenuClick('is')">
        </span>
        <span
          class="icon bk-icon icon-minus-circle"
          v-bk-tooltips.top="{ content: `${$t('添加')} is not ${$t('过滤项')}`, delay: 300 }"
          @click="handleMenuClick('not')">
        </span>
        <span
          class="icon log-icon icon-copy"
          v-bk-tooltips.top="{ content: $t('复制'), delay: 300 }"
          @click="handleMenuClick('copy')">
        </span>
      </div>
    </div>
  </span>
</template>

<script>
import TextHighlight from 'vue-text-highlight';

export default {
  components: {
    TextHighlight,
  },
  props: {
    content: {
      type: [String, Number],
      required: true,
    },
    fieldType: {
      type: String,
      default: '',
    },
    menuClick: Function,
  },
  data() {
    return {
      curValue: '', // 当前选中分词
      segmentReg: /([,&*+:;?^=!$<>'"{}()|[\]/\\|\s\r\n\t]|[-])/,
      segmentLimitIndex: 0, // 分词超出最大数量边界下标
      limitCount: 256, // 支持分词最大数量
    };
  },
  computed: {
    isNeedSegment() {
      return ['text'].includes(this.fieldType);
    },
    splitList() {
      let value = this.content;
      // 高亮显示
      if (this.markList.length) {
        value = String(value).replace(/<mark>/g, '')
          .replace(/<\/mark>/g, '');
      }
      let arr = value.split(this.segmentReg);
      arr = arr.filter(val => val.length);
      this.getLimitValidIndex(arr);
      return arr;
    },
    markList() {
      let markVal = this.content.toString().match(/(<mark>).*?(<\/mark>)/g) || [];
      if (markVal.length) {
        markVal = markVal.map(item => item.replace(/<mark>/g, '')
          .replace(/<\/mark>/g, ''));
      }
      return markVal;
    },
  },
  beforeDestroy() {
    this.handleDestroy();
  },
  methods: {
    /**
     * @desc 获取限制最大分词数下标
     * @param { Array } list
     */
    getLimitValidIndex(list) {
      let segmentCount = 0;
      this.segmentLimitIndex = 0;
      for (let index = 0; index < list.length; index++) {
        this.segmentLimitIndex += 1;
        if (!this.segmentReg.test(list[index])) {
          segmentCount += 1;
        }
        if (segmentCount > this.limitCount) break;
      }
    },
    formatterStr(content) {
      // 匹配高亮标签
      let value = content;
      if (this.markList.length) {
        value = String(value).replace(/<mark>/g, '')
          .replace(/<\/mark>/g, '');
      }

      return value;
    },
    handleDestroy() {
      if (this.popoverInstance) {
        this.popoverInstance?.hide(0);
        this.popoverInstance?.destroy();
        this.popoverInstance = null;
        this.curValue = '';
      }
    },
    handleClick(e, value) {
      this.handleDestroy();

      this.curValue = value;
      this.popoverInstance = this.$bkPopover(e.target, {
        content: this.$refs.moreTools,
        trigger: 'click',
        placement: 'bottom',
        arrow: true,
        theme: 'light',
        interactive: true,
        extCls: 'event-tippy-content',
        onHidden: () => {
          this.popoverInstance && this.popoverInstance.destroy();
          this.popoverInstance = null;
        },
      });
      this.popoverInstance && this.popoverInstance.show(10);
    },
    checkMark(splitItem) {
      if (!this.markList.length) return false;
      // 以句号开头或句号结尾的分词符匹配成功也高亮展示
      return this.markList.some(item => item === splitItem
       || splitItem.startsWith(`.${item}`)
       || splitItem.endsWith(`${item}.`),
      );
    },
    handleMenuClick(event) {
      this.menuClick(event, this.curValue);
      this.handleDestroy();
    },
  },
};
</script>

<style lang="scss">
  .event-tippy-content {
    .event-icons {
      display: flex;
      align-items: center;
    }

    .tippy-tooltip {
      padding: 4px 0 2px 8px;
    }

    .icon {
      display: inline-block;
      margin-right: 10px;
      font-size: 14px;
      cursor: pointer;

      &:hover {
        color: #3a84ff;
      }
    }

    .bk-icon {
      transform: rotate(45deg);
    }

    .icon-minus-circle,
    .icon-chart {
      margin-right: 4px;
    }

    .icon-copy {
      margin-right: 3px;
      font-size: 24px;
    }
  }

  .log-content-wrapper {
    word-break: break-all;

    .segment-content {
      white-space: normal;
    }

    .menu-list {
      display: none;
      position: absolute;
    }

    .valid-text {
      cursor: pointer;

      &:hover {
        color: #3a84ff;
      }
    }
  }
</style>
