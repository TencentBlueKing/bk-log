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
  <div
    :class="{ 'handle-content': true, 'fix-content': showAllHandle, 'origin-content': logType === 'origin' }"
    v-if="curHoverIndex === index"
    @mouseenter="mouseenterHandle"
    @mouseleave="mouseleaveHandle">
    <span class="handle-card" v-bk-tooltips="{ allowHtml: true, content: '#realTimeLog-html', delay: 500 }">
      <span
        :class="`icon log-icon icon-handle icon-time ${!isActiveLog && 'is-disable'}`"
        @click.stop="handleCheckClick('realTimeLog', isActiveLog)">
      </span>
    </span>
    <span class="handle-card" v-bk-tooltips="{ allowHtml: true, content: '#contextLog-html', delay: 500 }">
      <span
        :class="`icon log-icon icon-handle icon-document ${!isActiveLog && 'is-disable'}`"
        @click.stop="handleCheckClick('contextLog', isActiveLog)">
      </span>
    </span>
    <span class="handle-card" v-bk-tooltips="{ allowHtml: true, content: '#monitorWeb-html', delay: 500 }">
      <span
        :class="`icon icon-handle log-icon icon-inform ${!isActiveMonitorWeb && 'is-disable'}`"
        @click.stop="handleCheckClick('monitorWeb', isActiveMonitorWeb)"></span>
    </span>
    <span v-bk-tooltips="{ content: 'WebConsole', delay: 500 }"
          class="handle-card"
          v-if="isActiveWebConsole && showAllHandle">
      <span
        class="icon icon-handle log-icon icon-teminal"
        @click.stop="handleClick('webConsole')"></span>
    </span>
    <span class="bk-icon icon-more icon-handle" v-if="isActiveWebConsole && !showAllHandle"></span>
    <div id="realTimeLog-html">
      <span>
        <span v-if="!isActiveLog" class="bk-icon icon-exclamation-circle-shape"></span>
        <span>{{toolMessage.realTimeLog}}</span>
      </span>
    </div>
    <div id="contextLog-html">
      <span>
        <span v-if="!isActiveLog" class="bk-icon icon-exclamation-circle-shape"></span>
        <span>{{toolMessage.contextLog}}</span>
      </span>
    </div>
    <div id="monitorWeb-html">
      <span>
        <span v-if="!isActiveMonitorWeb" class="bk-icon icon-exclamation-circle-shape"></span>
        <span>{{toolMessage.monitorWeb}}</span>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    index: {
      type: Number,
      default: 0,
    },
    curHoverIndex: {
      type: Number,
      default: -1,
    },
    operatorConfig: {
      type: Object,
      required: true,
    },
    logType: {
      type: String,
      default: 'table',
    },
    handleClick: Function,
  },
  data() {
    return {
      showAllHandle: false, // hove操作区域显示全部icon
    };
  },
  computed: {
    isActiveLog() {
      return this.operatorConfig?.contextAndRealtime.is_active;
    },
    isActiveWebConsole() {
      return this.operatorConfig?.bcsWebConsole.is_active;
    },
    isActiveMonitorWeb() {
      return this.operatorConfig?.bkmonitor.is_active;
    },
    toolMessage() {
      return this.operatorConfig.toolMessage;
    },
  },
  methods: {
    mouseenterHandle() {
      this.showAllHandle = true;
    },
    mouseleaveHandle() {
      this.showAllHandle = false;
    },
    handleCheckClick(clickType, isActive = false) {
      if (!isActive) return;
      return this.handleClick(clickType);
    },
  },
};
</script>

<style lang="scss" scoped>
  .handle-content {
    display: flex;
    position: absolute;
    right: 0;
    width: 84px;
    padding: 14px 10px;
    align-items: flex-start;
    top: 0;
    overflow: hidden;
    justify-content: flex-end;
  }

  .fix-content {
    width: auto;
    background-color: #f5f7fa;
  }

  .icon-exclamation-circle-shape {
    color: #d7473f;
  }

  .icon-more {
    transform: translateY(2px) translateX(4px);
  }

  .is-disable {
    /* stylelint-disable-next-line declaration-no-important */
    color: #eceef2 !important;

    /* stylelint-disable-next-line declaration-no-important */
    cursor: no-drop !important;
  }
</style>
