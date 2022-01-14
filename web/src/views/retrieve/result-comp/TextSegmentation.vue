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
    <span
      v-if="!isNeedSegment"
      class="valid-text"
      @click="handleClick($event, content)">{{ formatterStr(content) }}</span>
    <template v-else class="segment-content">
      <span
        v-for="(item, index) in splitList"
        :key="index">
        <!-- 分割符 -->
        <span v-if="segmentReg.test(item)">{{item}}</span>
        <!-- 高亮 -->
        <mark
          v-else-if="markList.length && markList.includes(item)"
          @click="handleClick($event, item)">{{item}}</mark>
        <!-- 可操作分词 -->
        <span v-else class="valid-text" @click="handleClick($event, item)">{{item}}</span>
      </span>
    </template>

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
export default {
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
      markList: [], // 高亮
      segmentReg: /([,&*+:;?^=!$<>'"{}()|[\]/\\|\s\r\n\t]|[-])/,
    };
  },
  computed: {
    isNeedSegment() {
      return ['text'].includes(this.fieldType);
    },
    splitList() {
      let value = this.content;
      // 高亮显示
      const markVal = this.content.toString().match(/(?<=<mark>).*?(?=<\/mark>)/g) || [];
      this.markList = markVal;
      if (markVal.length) {
        value = String(value).replace(/<mark>/g, '')
          .replace(/<\/mark>/g, '');
      }
      const arr = value.split(this.segmentReg);

      return arr;
    },
  },
  beforeDestroy() {
    this.handleDestroy();
  },
  methods: {
    formatterStr(content) {
      // 匹配高亮标签
      let value = content;
      const markVal = content.toString().match(/(?<=<mark>).*?(?=<\/mark>)/g) || [];
      if (markVal) {
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
      color: #3A84FF;
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
    // word-break: keep-all;
    &:hover {
      color: #3a84ff;
    }
  }
}
</style>
