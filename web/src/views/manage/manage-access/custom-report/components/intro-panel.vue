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
    <div :class="`right-window ${isOpenWindow ? 'window-active' : ''}`">
      <div class="create-btn details" @click="handleActiveDetails(null)">
        <span class="bk-icon icon-text-file" :style="`color:${isOpenWindow ? '#3A84FF;' : ''}`"></span>
      </div>
      <div class="top-title">
        <p> {{$t('帮助文档')}}</p>
        <div class="create-btn close" @click="handleActiveDetails(false)">
          <span class="bk-icon icon-minus-line"></span>
        </div>
      </div>
      <div class="html-container">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div v-html="customTypeIntro"></div>
      </div>
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
    isOpenWindow: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
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
    handleActiveDetails(state) {
      this.$emit('handleActiveDetails', state ? state : !this.isOpenWindow);
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/flex';
  @import '@/scss/mixins/scroller';

  .intro-panel {
    width: 100%;
    height: 100%;
    position: relative;

    .right-window {
      width: 100%;
      height: 100%;
      background: #fff;
      border: 1px solid #dcdee5;
      position: absolute;
      z-index: 99;
      color: #63656e;
      padding: 16px 0 0 24px;

      .html-container {
        max-height: calc(100vh - 200px);
        overflow-y: auto;
        padding-right: 24px;
      }

      .top-title {
        height: 48px;
      }

      &.window-active {
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

      a {
        display: inline-block;
        margin: 10px 0;
        color: #3a84ff;
      }
    }

    .create-btn {
      width: 24px;
      height: 24px;
      position: absolute;
      z-index: 999;

      @include flex-center;

      &.details {
        top: 64px;
        right: 16px;
        position: fixed;
        transform: rotateZ(360deg) rotateX(180deg);

        @include flex-center;
      }

      &.close {
        top: 10px;
        right: 16px;
      }

      &:hover {
        cursor: pointer;
        background: #f0f1f5;
        color: #3a84ff;
        border-radius: 2px;
      }
    }
  }
</style>
