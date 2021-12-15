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
  <div class="intro-panel">
    <div
      :class="`right-button ${isOpenWindow ? 'button-active' : ''}`"
      @click="isOpenWindow = !isOpenWindow">
      <i :class="`bk-icon icon-angle-double-${isOpenWindow ? 'right' : 'left'}`"></i>
    </div>
    <div :class="`right-window ${isOpenWindow ? 'window-active' : ''}`">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-html="customTypeIntro"></div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isOpenWindow: false, // 是否展开使用列表
    };
  },
  computed: {
    ...mapGetters({
      globalsData: 'globals/globalsData',
    }),
    dataTypeList() {
      const { databus_custom: databusCustom } = this.globalsData;
      return databusCustom || [];
    },
    customTypeIntro() {
      const curType = this.dataTypeList.find(type => type.id === this.data.custom_type);
      return curType ? this.replaceVaribles(curType.introduction) : '';
    },
  },
  methods: {
    replaceVaribles(intro) {
      let str = intro;
      const varibleList = intro.match(/\{\{([^)]*)\}\}/g);
      varibleList && varibleList.forEach((item) => {
        const val = item.match(/\{\{([^)]*)\}\}/)[1];
        str = this.data[val] ? str.replace(item, this.data[val]) : str;
      });

      return str;
    },
  },
};
</script>

<style lang="scss">
@import "../../../../../scss/mixins/flex";
@import '../../../../../scss/mixins/scroller';

.intro-panel {
  .right-button{
    width: 24px;
    height: 96px;
    border-radius: 8px 0 0 8px;
    border: 1px solid #dcdee5;
    border-right: none;
    background-color: #fafbfd;
    cursor: pointer;
    position: fixed;
    right: 0;
    top: calc(50vh - 48px);
    transition:right .5s;
    &.button-active{
      right: 400px;
    }
    @include flex-center;
  }
  .right-window{
    width: 400px;
    height: 100vh;
    background: #fff;
    border: 1px solid #dcdee5;
    position: fixed;
    right: -400px;
    top: 102px;
    z-index: 99;
    color: #63656e;
    transition:right .5s;
    padding: 16px 24px 0;
    &.window-active{
      right: 0;
    }
    h1 {
      font-size: 12px;
      font-weight: 700;
      margin: 26px 0 10px;
      &:first-child {
        margin-top: 0;
      }
    }
    ul {
      margin-left: 10px;
      li {
        margin-top: 8px;
        list-style: inside;
        font-size: 12px;
      }
    }
    p {
      font-size: 12px;
    }
    pre {
      margin: 0;
      margin-top: 6px;
      padding: 10px 14px;
      background: #f4f4f7;
      overflow-x: auto;
      @include scroller;
    }
  }
}
</style>
