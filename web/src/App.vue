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
  <div id="app" v-bkloading="{ isLoading: pageLoading }">
    <head-nav
      v-show="!asIframe && !pageLoading"
      @reloadRouter="routerKey += 1"
      @welcome="welcomePageData = $event"
      @auth="authPageInfo = $event"
    ></head-nav>
    <div :class="['log-search-container', asIframe && 'as-iframe']" v-if="!pageLoading">
      <auth-page v-if="authPageInfo" :info="authPageInfo"></auth-page>
      <welcome-page v-else-if="welcomePageData" :data="welcomePageData"></welcome-page>
      <router-view v-else :key="routerKey"></router-view>
    </div>
    <auth-dialog></auth-dialog>
    <LoginModal v-if="loginData" :login-data="loginData" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import headNav from '@/components/nav/head-nav';
import LoginModal from '@/components/LoginModal';
import WelcomePage from '@/components/common/welcome-page';
import AuthPage from '@/components/common/auth-page';
import AuthDialog from '@/components/common/auth-dialog';
import jsCookie from 'js-cookie';

export default {
  name: 'app',
  components: {
    headNav,
    LoginModal,
    AuthPage,
    AuthDialog,
    WelcomePage,
  },
  data() {
    return {
      loginData: null,
      authPageInfo: null,
      welcomePageData: null,
      routerKey: 0,
    };
  },
  computed: {
    ...mapGetters({
      pageLoading: 'pageLoading',
      asIframe: 'asIframe',
    }),
  },
  created() {
    const platform = window.navigator.platform.toLowerCase();
    if (platform.indexOf('win') === 0) {
      document.body.style['font-family'] = 'Microsoft Yahei, pingFang-SC-Regular, Helvetica, Aria, sans-serif';
    } else {
      document.body.style['font-family'] = 'pingFang-SC-Regular, Microsoft Yahei, Helvetica, Aria, sans-serif';
    }
    this.$store.commit('updateRunVersion', window.runVersion || '');

    // 是否转换日期类型字段格式
    const isFormatDate = jsCookie.get('operation');
    if (isFormatDate === 'false') {
      this.$store.commit('updateIsFormatDate', false);
    }

    // 弹窗登录
    window.bus.$on('show-login-modal', (loginData) => {
      this.loginData = loginData;
    });
    window.bus.$on('close-login-modal', () => {
      this.loginData = null;
      setTimeout(() => {
        window.location.reload();
      }, 0);
    });
  },
  mounted() {
    this.$store.dispatch('getBkBizList');
  },
};
</script>

<style lang="scss">
  @import './scss/reset.scss';
  @import './scss/app.scss';
  @import './scss/animation.scss';
  @import './scss/mixins/clearfix.scss';

  #app {
    min-width: 1280px;
    height: 100%;
    min-height: 730px;
    background: #f4f7fa;
  }

  .button-text {
    color: #3a84ff;
    cursor: pointer;

    &:hover {
      color: #699df4;
    }

    &:active {
      color: #2761dd;
    }

    &.is-disabled {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }

  .text-overflow-hidden {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .button-text {
    color: #3a84ff;
    cursor: pointer;

    &:hover {
      color: #699df4;
    }

    &:active {
      color: #2761dd;
    }

    &.is-disabled {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }

  .log-search-container {
    position: relative;
    width: 100%;
    height: calc(100% - 50px);
    overflow-y: hidden;

    &.as-iframe {
      height: 100%;
    }
  }

  /*无权限时 v-cursor 样式*/
  .cursor-element {
    width: 12px;
    height: 16px;
    background: url('./images/cursor-lock.svg') no-repeat;
  }
  // 检索里一些公用的样式
  .tab-button {
    float: left;

    @include clearfix;

    .tab-button-item {
      // display: table-column;
      margin-left: -1px;
      padding: 0 15px;
      border: 1px solid #c4c6cc;
      border-left-color: transparent;
      font-size: 0;
      color: #63656e;
      cursor: pointer;

      &:first-child {
        margin-left: 0;
        border-left-color: #c4c6cc;
        border-radius: 2px 0 0 2px;
      }

      &:last-child {
        border-radius: 0 2px 2px 0;
      }

      &.active {
        border: 1px solid #3a84ff;
        color: #3a84ff;
        background: #e1ecff;
        z-index: 10;
      }
    }

    .tab-button-text {
      display: inline-block;
      width: 100%;
      line-height: 32px;
      font-size: 12px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
  }
  // hack 组件样式
  .bk-dialog.bk-info-box .bk-dialog-header-inner {
    white-space: normal !important;
  }

  .bk-date-picker-dropdown .bk-picker-confirm-time {
    color: #3a84ff;
  }

  .tippy-tooltip .tippy-content {
    word-break: break-all;
  }

  .bk-form-control.is-error .bk-form-input {
    border-color: #ff5656;
  }
  // 表格单元 v-bk-overflow-tips
  .bk-table .bk-table-body-wrapper .table-ceil-container {
    width: 100%;

    > span {
      display: block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  // hack vue-json-pretty
  .json-view-wrapper .vjs-value {
    word-break: break-all;
  }
  // hack be-select将下拉宽度全部交给slot以控制宽度和事件传播
  .custom-no-padding-option.bk-option > .bk-option-content {
    padding: 0;

    > .option-slot-container {
      padding: 9px 16px;
      min-height: 32px;
      line-height: 14px;

      &.no-authority {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #c4c6cc;
        cursor: not-allowed;

        .text {
          width: calc(100% - 56px);
        }

        .apply-text {
          flex-shrink: 0;
          display: none;
          color: #3a84ff;
          cursor: pointer;
        }

        &:hover .apply-text {
          display: flex;
        }
      }
    }
  }
</style>
