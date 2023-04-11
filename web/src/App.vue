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
  <div id="app" v-bkloading="{ isLoading: pageLoading }" :class="{ 'clear-min-height': $route.name === 'retrieve' }">
    <head-nav
      v-show="!isAsIframe && !pageLoading"
      @reloadRouter="routerKey += 1"
      @welcome="welcomePageData = $event" />
    <div :class="['log-search-container', isAsIframe && 'as-iframe']">
      <welcome-page v-if="welcomePageData" :data="welcomePageData" />
      <!-- 导航改版 -->
      <bk-navigation
        v-else-if="menuList && menuList.length"
        class="bk-log-navigation"
        navigation-type="left-right"
        head-height="0"
        header-title=""
        default-open
        :theme-color="navThemeColor"
        @toggle="handleToggle">
        <template slot="menu">
          <div class="biz-menu">
            <biz-menu-select :is-expand="isExpand" />
          </div>
          <bk-navigation-menu
            :item-default-bg-color="navThemeColor"
            :default-active="activeManageNav.id">
            <template v-for="groupItem in menuList">
              <bk-navigation-menu-group
                v-if="groupItem.children.length"
                :key="groupItem.id"
                :group-name="isExpand ? groupItem.name : groupItem.keyword">
                <template v-for="navItem in groupItem.children">
                  <a class="nav-item" :key="navItem.id" :href="getRouteHref(navItem.id)">
                    <bk-navigation-menu-item
                      :data-test-id="`navBox_nav_${navItem.id}`"
                      :id="navItem.id"
                      :icon="getMenuIcon(navItem)"
                      @click="handleClickNavItem(navItem.id)">
                      <span>{{ isExpand ? navItem.name : '' }}</span>
                      <span v-if="navItem.id === 'custom-report'" class="beta-class">BETA</span>
                    </bk-navigation-menu-item>
                  </a>
                </template>
              </bk-navigation-menu-group>
            </template>
          </bk-navigation-menu>
        </template>
        <div class="navigation-content" v-if="!pageLoading">
          <auth-container-page v-if="authPageInfo" :info="authPageInfo"></auth-container-page>
          <router-view v-else class="manage-content" :key="routerKey"></router-view>
        </div>
      </bk-navigation>
      <!-- 无侧边栏页面 -->
      <router-view v-else-if="!pageLoading && !menuList" class="manage-content" :key="routerKey"></router-view>
      <novice-guide
        v-if="displayRetrieve"
        :data="guideStep"
        guide-page="default" />
    </div>
    <auth-dialog />
    <bk-paas-login ref="login" />
    <!-- <login-modal v-if="loginData" :login-data="loginData" /> -->
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import headNav from '@/components/nav/head-nav';
// import LoginModal from '@/components/login-modal';
import WelcomePage from '@/components/common/welcome-page';
import AuthContainerPage from '@/components/common/auth-container-page';
import AuthDialog from '@/components/common/auth-dialog';
import BizMenuSelect from '@/components/biz-menu';
import NoviceGuide from '@/components/novice-guide';
import jsCookie from 'js-cookie';
import BkPaasLogin from '@blueking/paas-login';

export default {
  name: 'App',
  components: {
    headNav,
    // LoginModal,
    AuthContainerPage,
    AuthDialog,
    WelcomePage,
    BizMenuSelect,
    NoviceGuide,
    BkPaasLogin,
  },
  data() {
    return {
      loginData: null,
      welcomePageData: null,
      routerKey: 0,
      navThemeColor: '#2c354d',
      isExpand: true,
      curGuideStep: 0,
      isAsIframe: false,
      rightClickRouteName: '', // 当前右键选中的路由
      visible: false, // 是否展示右键菜单
      top: 0, // 右键菜单定位top
      left: 0, // 右键菜单定位left
    };
  },
  computed: {
    ...mapState([
      'topMenu',
      'activeTopMenu',
      'activeManageNav',
      'userGuideData',
    ]),
    ...mapGetters({
      pageLoading: 'pageLoading',
      asIframe: 'asIframe',
      authPageInfo: 'globals/authContainerInfo',
    }),
    navActive() {
      return '';
    },
    menuList() {
      const list = this.topMenu.find(item => item.id === this.activeTopMenu.id)?.children;
      return list;
    },
    displayRetrieve() {
      return this.$store.state.retrieve.displayRetrieve;
    },
    guideStep() {
      return this.userGuideData?.default || {};
    },
  },
  watch: {
    asIframe: {
      immediate: true,
      handler(val) {
        this.isAsIframe = val;
      },
    },
  },
  created() {
    const platform = window.navigator.platform.toLowerCase();
    if (platform.indexOf('win') === 0) {
      document.body.style['font-family'] = 'Microsoft Yahei, pingFang-SC-Regular, Helvetica, Aria, sans-serif';
    } else {
      document.body.style['font-family'] = 'pingFang-SC-Regular, Microsoft Yahei, Helvetica, Aria, sans-serif';
    }
    this.$store.commit('updateRunVersion', window.RUN_VER || '');

    // 是否转换日期类型字段格式
    const isFormatDate = jsCookie.get('operation');
    if (isFormatDate === 'false') {
      this.$store.commit('updateIsFormatDate', false);
    }
    const isEnLanguage = (jsCookie.get('blueking_language') || 'zh-cn') === 'en';
    this.$store.commit('updateIsEnLanguage', isEnLanguage);

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

    this.getUserGuide();
  },
  mounted() {
    window.LoginModal = this.$refs.login;
  },
  methods: {
    getMenuIcon(item) {
      if (item.icon) {
        return `bk-icon log-icon icon-${item.icon}`;
      }

      return 'bk-icon icon-home-shape';
    },
    handleClickNavItem(id) {
      this.$router.push({
        name: id,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
      if (id === 'default-dashboard') {
        this.routerKey = this.routerKey + 1;
      }
    },
    handleToggle(val) {
      this.isExpand = val;
    },
    getUserGuide() {
      this.$http.request('meta/getUserGuide').then((res) => {
        this.$store.commit('setUserGuideData', res.data);
      })
        .catch((e) => {
          console.warn(e);
        });
    },
    getRouteHref(pageName) {
      const newUrl = this.$router.resolve({
        name: pageName,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
      return newUrl.href;
    },
  },
};
</script>

<style lang="scss">
  @import './scss/reset.scss';
  @import './scss/app.scss';
  @import './scss/animation.scss';
  @import './scss/mixins/clearfix.scss';
  @import './scss/mixins/scroller.scss';

  #app {
    min-width: 1280px;
    height: 100%;
    min-height: 730px;
    background: #f4f7fa;
  }

  .clear-min-height {
    /* stylelint-disable-next-line declaration-no-important */
    min-height: 0 !important;
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
    /* stylelint-disable-next-line declaration-no-important */
    white-space: normal !important;
  }

  .bk-date-picker-dropdown .bk-picker-confirm-time {
    color: #3a84ff;
  }

  .tippy-tooltip .tippy-content {
    padding: 0;
    word-break: break-all;
  }

  .bk-form-control.is-error .bk-form-input {
    border-color: #ff5656;
  }
  // 导航
  .bk-log-navigation.bk-navigation,
  .hack-king-navigation.bk-navigation {
    /* stylelint-disable-next-line declaration-no-important */
    width: 100% !important;

    /* stylelint-disable-next-line declaration-no-important */
    height: 100% !important;

    .container-header {
      /* stylelint-disable-next-line declaration-no-important */
      display: none !important;
    }

    .bk-navigation-wrapper {
      height: 100%;

      .navigation-container {
        /* stylelint-disable-next-line declaration-no-important */
        max-width: calc(100% - 60px) !important;
        z-index: 100;

        .container-content {
          /* stylelint-disable-next-line declaration-no-important */
          height: 100% !important;

          /* stylelint-disable-next-line declaration-no-important */
          max-height: 100% !important;
          padding: 0;

          .navigation-content {
            height: 100%;
          }
        }
      }

      .bk-navigation-menu-group {
        .group-name-wrap .group-name {
          margin-right: 0;
        }
      }

      .navigation-menu-item-icon.bk-icon {
        min-width: 28px;
      }

      .nav-item {
        width: 100%;
        display: inline-block;
      }
    }

    .nav-slider-list {
      /* stylelint-disable-next-line declaration-no-important */
      height: calc(100% - 56px) !important;
    }

  }

  .biz-menu {
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,.10);
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
  // 采集项管理、索引集管理通用样式
  .access-manage-container {
    padding: 28px 24px;

    .bk-tab-section {
      display: none;
    }

    .go-search {
      // position: fixed;
      position: absolute;
      right: 0;
      font-size: 12px;
      z-index: 999;

      .icon-info {
        color: #979ba5;
        font-size: 14px;
      }

      .search-button {
        display: inline-block;
        color: #3a84ff;
        cursor: pointer;
      }

      .search-text {
        height: 32px;
        line-height: 32px;
        background: #fff;
        box-shadow: 0 2px 4px 0 #1919290d;
        border-radius: 2px;
        padding: 0 9px;
      }
    }

    .tab-content {
      height: calc(100% - 50px);
      overflow: auto;
      padding: 20px;
      background-color: #fff;
      box-shadow: 0 2px 4px 0 #1919290d;
      border-top: none;

      @include scroller($backgroundColor: #C4C6CC, $width: 4px);

      .main-title {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
        line-height: 20px;
        padding: 0 0 8px 0;
        border-bottom: 1px solid #dcdee5;
        margin-bottom: 20px;
      }

      .refresh-button {
        display: flex;
        align-items: center;
        font-size: 12px;
        font-weight: normal;
        color: #3a84ff;
        margin-left: 8px;
        cursor: pointer;

        &:hover {
          color: #699df4;
        }

        .bk-icon {
          font-size: 13px;
          margin-right: 4px;
        }
      }

      .charts-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;

        .chart-container {
          position: relative;
          width: calc((100% - 16px) / 2);
          padding: 0 16px;
          border: 1px solid #f0f1f5;
          border-radius: 3px;
          box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .05);

          .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 50px;

            .title {
              font-size: 12px;
              font-weight: bold;
              color: #63656e;
              line-height: 16px;
            }

            .date-picker {
              display: flex;
              align-items: center;
            }
          }

          .chart-canvas-container {
            position: relative;
            height: 230px;

            &.big-chart {
              height: 280px;
            }
          }

          .king-exception {
            position: absolute;
            top: 80px;
            left: 0;
          }
        }
      }
    }
  }

  .title-overflow {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .beta-class {
    color: #ffa228;
    margin-left: 2px;
    padding-top: 3px;
  }

  .bk-dialog-type-header .header {
    white-space: normal;
    text-overflow: inherit;
    overflow: hidden;
  }
</style>
