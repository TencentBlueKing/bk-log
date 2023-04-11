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
  <nav class="log-search-nav">
    <div class="nav-left fl">
      <div class="log-logo-container" @click.stop="jumpToHome">
        <img
          v-if="logoImgUrl"
          :src="logoImgUrl"
          alt="logo"
          class="logo-image">
        <span class="logo-text">{{ logoText }}</span>
      </div>
    </div>
    <div class="nav-center fl" data-test-id="topNav_div_topNavBox">
      <ul>
        <li
          v-for="menu in topMenu"
          :key="menu.id"
          :id="`${menu.id}MenuGuide`"
          :class="['menu-item', { 'active': activeTopMenu.id === menu.id }]"
          :data-test-id="`topNavBox_li_${menu.id}`"
          @click="routerHandler(menu)">
          <template>
            {{ menu.name }}
          </template>
        </li>
      </ul>
    </div>
    <div class="nav-right fr" v-show="usernameRequested">
      <!-- 语言 -->
      <bk-dropdown-menu
        align="center"
        trigger="click"
        @show="dropdownLanguageShow"
        @hide="dropdownLanguageHide">
        <div
          class="icon-language-container"
          :class="isShowLanguageDropdown && 'active'"
          slot="dropdown-trigger">
          <div class="icon-circle-container">
            <span class="icon log-icon icon-locale icon-language"></span>
          </div>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li v-for="item in languageList" :key="item.id">
            <a
              href="javascript:;"
              :class="{ 'active': language === item.id }"
              @click="changeLanguage(item.id)">
              {{ item.name }}
            </a>
          </li>
        </ul>
      </bk-dropdown-menu>
      <!-- 版本日志和文档中心 -->
      <bk-dropdown-menu
        align="center"
        trigger="click"
        @show="dropdownHelpShow"
        @hide="dropdownHelpHide"
        ref="dropdownHelp">
        <div
          class="icon-language-container"
          :class="isShowHelpDropdown && 'active'"
          slot="dropdown-trigger">
          <div class="icon-circle-container">
            <span class="icon log-icon icon-icon-help-document-fill" slot="dropdown-trigger"></span>
          </div>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li>
            <a
              href="javascript:;"
              @click.stop="dropdownHelpTriggerHandler('docCenter')">
              {{ $t('文档中心') }}
            </a>
            <a
              href="javascript:;"
              @click.stop="dropdownHelpTriggerHandler('logVersion')">
              {{ $t('版本日志') }}
            </a>
            <a
              href="javascript:;"
              @click.stop="dropdownHelpTriggerHandler('feedback')">
              {{ $t('问题反馈') }}
            </a>
          </li>
        </ul>
      </bk-dropdown-menu>
      <log-version :dialog-show.sync="showLogVersion" />
      <span class="username" v-if="username">{{ username }}</span>
    </div>
  </nav>
</template>

<script>
import { mapState } from 'vuex';
import jsCookie from 'js-cookie';
import LogVersion from './log-version';
import { menuArr } from './complete-menu';
import navMenuMixin from '@/mixins/nav-menu-mixin';

export default {
  name: 'HeaderNav',
  components: {
    LogVersion,
  },
  mixins: [navMenuMixin],
  props: {},
  data() {
    return {
      isFirstLoad: true,
      isOpenVersion: window.RUN_VER.indexOf('open') !== -1,
      logoText: window.TITLE_MENU || '',
      username: '',
      usernameRequested: false,
      isShowLanguageDropdown: false,
      isShowHelpDropdown: false,
      showLogVersion: false,
      language: 'zh-cn',
      languageList: [{ id: 'zh-cn', name: '中文' }, { id: 'en', name: 'English' }],
    };
  },
  computed: {
    ...mapState({
      currentMenu: state => state.currentMenu,
      errorPage: state => state.errorPage,
      asIframe: state => state.asIframe,
      iframeQuery: state => state.iframeQuery,
    }),
    logoImgUrl() {
      return process.env.NODE_ENV === 'development' ? '' : (window.MENU_LOGO_URL || '');
    },
    dropDownActive() {
      let current;
      if (this.currentMenu.dropDown && this.currentMenu.children) {
        const routeName = this.$route.name;
        current = this.activeTopMenu(this.currentMenu.children, routeName);
      }
      return current || {};
    },
    isDisableSelectBiz() {
      return Boolean(this.$route.name === 'trace' && this.$route.query.traceId);
    },
  },
  async created() {
    this.language = jsCookie.get('blueking_language') || 'zh-cn';
    this.$store.commit('updateMenuList', menuArr);
    await this.getUserInfo();
    setTimeout(() => this.requestMySpaceList(), 100);
  },
  methods: {
    async getUserInfo() {
      try {
        const res = await this.$http.request('userInfo/getUsername');
        this.username = res.data.username;
        this.$store.commit('updateUserMeta', res.data);
        if (window.__aegisInstance) {
          window.__aegisInstance.setConfig({
            uin: res.data.username,
          });
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.usernameRequested = true;
      }
    },
    jumpToHome() {
      this.$router.push({
        name: 'retrieve',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
      setTimeout(() => {
        this.$emit('reloadRouter');
      });
    },
    routerHandler(menu) {
      if (menu.id === this.activeTopMenu.id) {
        if (menu.id === 'retrieve') {
          this.$router.push({
            name: menu.id,
            query: {
              spaceUid: this.$store.state.spaceUid,
            },
          });
          this.$emit('reloadRouter');
          return;
        } if (menu.id === 'extract') {
          if (this.$route.query.create) {
            this.$router.push({
              name: 'extract',
              query: {
                spaceUid: this.$store.state.spaceUid,
              },
            });
          } else {
            this.$emit('reloadRouter');
          }
          return;
        } if (menu.id === 'trace') {
          if (this.$route.name === 'trace-detail') {
            this.$router.push({
              name: 'trace-list',
              query: {
                spaceUid: this.$store.state.spaceUid,
              },
            });
          } else {
            this.$emit('reloadRouter');
          }
          return;
        } if (menu.id === 'dashboard') {
          // if (this.$route.query.manageAction) {
          //   const newQuery = { ...this.$route.query };
          //   delete newQuery.manageAction;
          //   this.$router.push({
          //     name: 'dashboard',
          //     query: newQuery,
          //   });
          // }
          // this.$emit('reloadRouter');
          // return;
          this.$router.push({
            name: menu.id,
            query: {
              spaceUid: this.$store.state.spaceUid,
            },
          });
          this.$emit('reloadRouter');
          return;
        } if (menu.id === 'manage') {
          if (this.$route.name !== 'collection-item') {
            this.$router.push({
              name: 'manage',
              query: {
                spaceUid: this.$store.state.spaceUid,
              },
            });
          } else {
            this.$emit('reloadRouter');
          }
          return;
        }
        this.$emit('reloadRouter');
        return;
      }
      if (menu.id === 'monitor') {
        window.open(`${window.MONITOR_URL}/?bizId=${this.bkBizId}#/strategy-config`, '_blank');
      } else if (menu.id === 'trace') {
        this.$router.push({
          name: 'trace-list',
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      } else {
        this.$router.push({
          name: menu.id,
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      }
    },
    changeLanguage(value) {
      const domainList = location.hostname.split('.');

      // 本项目开发环境因为需要配置了 host 域名比联调环境多 1 级
      if (process.env.NODE_ENV === 'development') {
        domainList.splice(0, 1);
      }

      // handle duplicate cookie names
      for (let i = 0; i < domainList.length - 1; i++) {
        jsCookie.remove('blueking_language', {
          domain: domainList.slice(i).join('.'),
        });
      }

      jsCookie.set('blueking_language', value, {
        expires: 30,
        // 和平台保持一致，cookie 种在上级域名
        domain: domainList.length > 2 ? domainList.slice(1).join('.') : domainList.join('.'),
      });

      window.location.reload();
    },
    dropdownLanguageShow() {
      this.isShowLanguageDropdown = true;
    },
    dropdownLanguageHide() {
      this.isShowLanguageDropdown = false;
    },
    dropdownHelpShow() {
      this.isShowHelpDropdown = true;
    },
    dropdownHelpHide() {
      this.isShowHelpDropdown = false;
    },
    dropdownHelpTriggerHandler(type) {
      this.$refs.dropdownHelp.hide();
      if (type === 'logVersion') {
        this.showLogVersion = true;
      } else if (type === 'docCenter') {
        // window.open(window.BK_DOC_URL);
        this.handleGotoLink('docCenter');
      } else if (type === 'feedback') {
        window.open(window.BK_FAQ_URL);
      }
    },
  },
};
</script>

<style lang="scss">
  @import '../../scss/mixins/clearfix';
  @import '../../scss/conf';
  @import '../../scss/mixins/flex';

  .log-search-nav {
    height: 50px;
    color: #fff;
    background: #000;

    @include clearfix;

    .nav-left {
      display: flex;
      align-items: center;
      width: 278px;
      height: 100%;
      padding-left: 23px;
      font-size: 18px;

      .log-logo-container {
        display: flex;
        align-items: center;
        height: 100%;
        color: #96a2b9;
        cursor: pointer;

        .logo-text {
          font-size: 18px;
        }

        .logo-image {
          margin-right: 10px;
        }

        .logo-image {
          margin-right: 10px;
        }
      }
    }

    .nav-center {
      font-size: 14px;

      ul {
        @include clearfix;
      }

      .menu-item {
        position: relative;
        float: left;
        padding: 0 20px;
        height: 50px;
        line-height: 50px;
        cursor: pointer;
        color: #979ba5;
        transition: color .3s linear;

        &.active {
          color: #fff;
          background: #0c1423;
          transition: all .3s linear;
        }

        &:hover {
          color: #fff;
          transition: color .3s linear;
        }

        &.guide-highlight {
          background: #000;
        }
      }

      .bk-dropdown-content {
        line-height: normal;
        z-index: 2105;
        min-width: 112px;

        /* stylelint-disable-next-line declaration-no-important */
        text-align: center !important;
      }

      .drop-menu-item > .active {
        color: #3a84ff;
      }
    }

    .nav-right {
      display: flex;
      align-items: center;
      height: 100%;
      color: #979ba5;

      @include clearfix;

      .select-business {
        margin-right: 22px;
        border-color: #445060;
        color: #979ba5;
      }

      .icon-language-container {
        height: 50px;
        margin: 4px;
        cursor: pointer;

        @include flex-center;

        .icon-circle-container {
          width: 32px;
          height: 32px;
          border-radius: 16px;
          transition: all .2s;

          @include flex-center;

          .log-icon {
            font-size: 16px;
            transition: all .2s;
          }
        }

        &:hover,
        &.active {
          .icon-circle-container {
            background: #252f43;
            transition: all .2s;

            .log-icon {
              color: #3a84ff;
              transition: all .2s;
            }
          }
        }
      }

      .icon-icon-help-document-fill {
        font-size: 16px;
        cursor: pointer;
      }

      .username {
        margin: 0 28px 0 12px;
        font-size: 14px;
        line-height: 20px;
      }

      .bk-dropdown-list .active {
        color: #3c96ff;
      }
    }
  }

  .select-business-dropdown-content {
    /* stylelint-disable-next-line declaration-no-important */
    border: none !important;

    .bk-select-search-wrapper {
      border: 1px solid #dcdee5;
      border-bottom: none;
      border-top-left-radius: 2px;
      border-top-right-radius: 2px;
    }

    .bk-options-wrapper {
      border-left: 1px solid #dcdee5;
      border-right: 1px solid #dcdee5;
    }

    .bk-select-extension {
      padding: 0;
      border: none;

      &:hover {
        background: #fafbfd;
      }

      .select-business-extension {
        display: flex;
        cursor: pointer;

        .extension-item {
          width: 50%;
          text-align: center;
          flex-grow: 1;
          border: 1px solid #dcdee5;

          &:nth-child(2) {
            margin-left: -1px;
            border-left-color: #dcdee5;
          }

          &:first-child {
            border-bottom-left-radius: 2px;
          }

          &:last-child {
            border-bottom-right-radius: 2px;
          }

          &:hover {
            color: #3a84ff;
            background: #f0f5ff;
            border-color: #3a84ff;
            z-index: 1;
          }
        }
      }
    }
  }
</style>
