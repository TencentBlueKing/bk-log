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
        <li v-for="menu in topMenu" :key="menu.id"
            :class="['menu-item', { 'active': activeTopMenu.id === menu.id }]"
            @click="routerHandler(menu)"
            :data-test-id="`topNavBox_li_${menu.id}`">
          <!-- <template v-if="menu.dropDown"> -->
          <template v-if="['dashboard', 'trace'].includes(menu.id)">
            <bk-dropdown-menu :ref="`menu${menu.router}`" align="center">
              <span slot="dropdown-trigger" style="font-size: 14px;">{{ menu.name }}</span>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-for="item in menu.children" :key="item.id" class="drop-menu-item">
                  <a href="javascript:;"
                     :class="{ 'active': item.id === dropDownActive.id }"
                     @click.stop="triggerHandler(item, menu)">{{ item.name }}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </template>
          <template v-else>
            {{ menu.name }}
          </template>
        </li>
      </ul>
    </div>
    <div class="nav-right fr" v-show="usernameRequested">
      <!-- 切换业务 -->
      <bk-select
        class="select-business fl" style="width: 260px;"
        ext-popover-cls="select-business-dropdown-content"
        :disabled="isDisableSelectBiz"
        :search-with-pinyin="true"
        :style="isDisableSelectBiz && { background: '#182132' }"
        :searchable="true"
        :clearable="false"
        show-select-all
        :value="projectId"
        @selected="projectChange">
        <bk-option
          v-for="item in myProjectList"
          class="custom-no-padding-option"
          :key="item.project_id"
          :id="item.project_id"
          :name="item.project_name">
          <div
            v-if="!(item.permission && item.permission.view_business)"
            class="option-slot-container no-authority"
            @click.stop>
            <span class="text">{{ item.project_name }}</span>
            <span class="apply-text" @click="applyProjectAccess(item)">{{ $t('申请权限') }}</span>
          </div>
          <div v-else v-bk-overflow-tips class="option-slot-container">
            <span>{{ item.project_name }}</span>
          </div>
        </bk-option>
        <div slot="extension" class="select-business-extension">
          <div
            class="extension-item"
            @click="applyBusinessAccess"
            v-bkloading="{ isLoading: isSelectLoading }">
            {{ $t('申请业务权限') }}
          </div>
          <div class="extension-item" @click="experienceDemo" v-if="demoProjectUrl">{{ $t('体验DEMO') }}</div>
        </div>
      </bk-select>
      <!-- 语言 -->
      <bk-dropdown-menu align="center" @show="dropdownLanguageShow" @hide="dropdownLanguageHide">
        <div class="icon-language-container" :class="isShowLanguageDropdown && 'active'" slot="dropdown-trigger">
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
      <bk-dropdown-menu align="center" @show="dropdownHelpShow" @hide="dropdownHelpHide" ref="dropdownHelp">
        <div class="icon-language-container" :class="isShowHelpDropdown && 'active'" slot="dropdown-trigger">
          <div class="icon-circle-container">
            <span class="icon log-icon icon-icon-help-document-fill" slot="dropdown-trigger"></span>
          </div>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li>
            <a href="javascript:;" @click.stop="dropdownHelpTriggerHandler('docCenter')">{{ $t('nav.docCenter') }}</a>
            <a href="javascript:;" @click.stop="dropdownHelpTriggerHandler('logVersion')">{{ $t('nav.versionLog') }}</a>
            <a href="javascript:;" @click.stop="dropdownHelpTriggerHandler('feedback')">{{ $t('问题反馈') }}</a>
          </li>
        </ul>
      </bk-dropdown-menu>
      <LogVersion :dialog-show.sync="showLogVersion" />
      <span class="username" v-if="username">{{ username }}</span>
    </div>
  </nav>
</template>

<script>
import { mapState } from 'vuex';
import jsCookie from 'js-cookie';
import LogVersion from './log-version';

export default {
  name: 'header-nav',
  components: {
    LogVersion,
  },
  props: {},
  data() {
    return {
      isSelectLoading: false,
      isFirstLoad: true,
      isOpenVersion: window.runVersion.indexOf('open') !== -1,
      demoProjectUrl: '', // demo 业务链接
      logoText: window.TITLE_MENU || '',
      logoImgUrl: window.MENU_LOGO_URL || '',
      username: '',
      usernameRequested: false,
      isShowLanguageDropdown: false,
      isShowHelpDropdown: false,
      showLogVersion: false,
      language: 'zh-cn',
      languageList: [{ id: 'zh-cn', name: '中文' }, { id: 'en', name: 'English' }],
      menuArr: [
        {
          name: this.$t('nav.retrieve'),
          id: 'retrieve',
          level: 1,
        },
        {
          name: this.$t('nav.dashboard'),
          id: 'dashboard',
          level: 1,
          dropDown: true,
          children: [{
            id: 'create_dashboard',
            name: this.$t('新建仪表盘'),
            level: 2,
            isDashboard: true,
            project_manage: true,
          }, {
            id: 'create_folder',
            name: this.$t('新建目录'),
            level: 2,
            isDashboard: true,
            project_manage: true,
          }, {
            id: 'import_dashboard',
            name: this.$t('导入仪表盘'),
            level: 2,
            isDashboard: true,
            project_manage: true,
          }],
        },
        {
          name: this.$t('nav.extract'),
          id: 'extract',
          level: 1,
        },
        {
          name: this.$t('trace.trace'),
          id: 'trace',
          level: 1,
          dropDown: true,
          children: [
            {
              id: 'trace_list',
              name: this.$t('trace.traceList'),
              level: 2,
              project_manage: true,
            },
            {
              id: 'trace_detail',
              name: this.$t('trace.traceDetail'),
              level: 2,
              project_manage: true,
            },
          ],
        },
        {
          name: this.$t('nav.monitors'),
          id: 'monitor',
          level: 1,
          children: [
            {
              name: this.$t('nav.alarmStrategy'),
              id: 'alarmStrategy',
              level: 2,
              children: [
                {
                  name: this.$t('nav.addstrategy'),
                  id: 'addstrategy',
                  level: 3,
                },
                {
                  name: this.$t('nav.editstrategy'),
                  id: 'editstrategy',
                  level: 3,
                },
              ],
            },
          ],
        },
        {
          name: this.$t('nav.manage'),
          id: 'manage',
          level: 1,
          dropDown: true,
          children: [
            {
              name: this.$t('nav.dataSource'),
              id: 'manage',
              level: 2,
              children: [
                {
                  name: this.$t('nav.collectAccess'),
                  id: 'collectAccess',
                  level: 3,
                  children: [
                    {
                      name: this.$t('nav.New_acquisition'),
                      id: 'collectAdd',
                      level: 4,
                    },
                    {
                      name: this.$t('nav.Edit_collection'),
                      id: 'collectEdit',
                      level: 4,
                    },
                    {
                      name: this.$t('nav.Enable_collections'),
                      id: 'collectStart',
                      level: 4,
                    },
                    {
                      name: this.$t('nav.Disable_collection'),
                      id: 'collectStop',
                      level: 4,
                    },
                    {
                      name: this.$t('nav.Field_extraction'),
                      id: 'collectField',
                      level: 4,
                    },
                    {
                      name: this.$t('nav.Configuration_details'),
                      id: 'allocation',
                      level: 4,
                      children: [
                        {
                          name: this.$t('nav.Data_sampling'),
                          id: 'jsonFormat',
                          level: 5,
                        },
                      ],
                    },
                  ],
                },
                {
                  name: this.$t('nav.esAccess'),
                  id: 'esAccess',
                  level: 3,
                },
              ],
            },
            {
              name: this.$t('nav.indexSet'),
              id: 'indexSet',
              level: 2,
              children: [
                {
                  name: this.$t('nav.addIndexSet'),
                  id: 'addIndexSet',
                  level: 3,
                },
                {
                  name: this.$t('nav.editIndexSet'),
                  id: 'editIndexSet',
                  level: 3,
                },
              ],
            },
            {
              name: this.$t('链路配置'),
              id: 'linkConfiguration',
              level: 2,
            },
            {
              name: this.$t('nav.permissionGroup'),
              id: 'permissionGroup',
              level: 2,
            },
            {
              name: this.$t('nav.v3Migrate'),
              id: 'migrate',
              level: 2,
            },
            {
              name: this.$t('nav.extractManage'),
              id: 'manageExtract',
              level: 2,
            },
          ],
        },
      ],
      routeMap: { // 后端返回的导航id映射
        search: 'retrieve',
        // monitor: 'monitor',
        // manage: 'manage',
        manage_access: 'manage',
        manage_index_set: 'indexSet',
        manage_data_link: 'linkConfiguration',
        manage_user_group: 'permissionGroup',
        manage_migrate: 'migrate',
        manage_extract: 'manageExtract',
      },
    };
  },
  computed: {
    ...mapState({
      topMenu: state => state.topMenu,
      menuList: state => state.menuList,
      currentMenu: state => state.currentMenu,
      activeTopMenu: state => state.activeTopMenu,
      projectId: state => state.projectId,
      bkBizId: state => state.bkBizId,
      myProjectList: state => state.myProjectList,
      errorPage: state => state.errorPage,
      asIframe: state => state.asIframe,
      iframeQuery: state => state.iframeQuery,
    }),
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
  created() {
    this.language = jsCookie.get('blueking_language') || 'zh-cn';
    this.$store.commit('updateMenuList', this.menuArr);
    this.getUserInfo();
    setTimeout(() => this.requestMyProjectList());
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
    async requestMyProjectList() {
      try {
        const res = await this.$http.request('project/getMyProjectList');
        // 根据权限排序
        const s1 = [];
        const s2 = [];
        const queryObj = JSON.parse(JSON.stringify(this.$route.query));

        if (queryObj.from) {
          this.$store.commit('updateAsIframe', queryObj.from);
          this.$store.commit('updateIframeQuery', queryObj);
        }

        for (const item of res.data) {
          // eslint-disable-next-line camelcase
          if (item.permission?.view_business) {
            s1.push(item);
          } else {
            s2.push(item);
          }
        }
        const projectList = s1.concat(s2);

        projectList.forEach((item) => {
          item.bk_biz_id = `${item.bk_biz_id}`;
          item.project_id = `${item.project_id}`;
        });
        const { bizId, projectId } = queryObj;
        const demoId = String(window.DEMO_BIZ_ID);
        const demoProject = projectList.find(item => item.bk_biz_id === demoId);
        this.demoProjectUrl = demoProject ? this.getDemoProjectUrl(demoProject.project_id) : '';
        const isOnlyDemo = demoProject && projectList.length === 1;
        if (!projectList.length || isOnlyDemo) { // 没有一个业务或只有一个demo业务显示欢迎页面
          const args = {
            newBusiness: { url: window.BIZ_ACCESS_URL },
            getAccess: {},
          };
          if (isOnlyDemo) {
            this.$store.commit('updateMyProjectList', projectList);
            if (bizId === demoProject.bk_biz_id || projectId === demoProject.project_id) {
              // 查询参数指定查看 demo 业务
              return this.projectChange(demoProject.project_id);
            }
            args.demoBusiness = {
              url: this.demoProjectUrl,
            };
          }
          if (projectId || bizId) { // 查询参数带非 demo 业务 id，获取业务名和权限链接
            const query = bizId ? { bk_biz_id: bizId } : { project_id: projectId };
            const [betaRes, authRes] = await Promise.all([
              this.$http.request('/meta/getMaintainerApi', { query }),
              this.$store.dispatch('getApplyData', {
                action_ids: ['view_business'],
                resources: [], // todo 需要将 url query 改成 bizId
              }),
            ]);
            args.getAccess.businessName = betaRes.data.bk_biz_name;
            args.getAccess.url = authRes.data.apply_url;
          } else {
            const authRes = await this.$store.dispatch('getApplyData', {
              action_ids: ['view_business'],
              resources: [],
            });
            args.getAccess.url = authRes.data.apply_url;
          }
          this.$store.commit('setPageLoading', false);
          this.projectChange();
          this.$emit('welcome', args);
        } else { // 正常业务
          this.$store.commit('updateMyProjectList', projectList);
          // 首先从查询参数找，然后从storage里面找，还找不到就返回第一个不是demo的业务
          const firstRealProjectId = projectList.find(item => item.bk_biz_id !== demoId).project_id;
          if (projectId || bizId) {
            const matchProject = projectList.find(item => item.project_id === projectId || item.bk_biz_id === bizId);
            this.projectChange(matchProject ? matchProject.project_id : firstRealProjectId);
          } else {
            const storageProjectId = window.localStorage.getItem('project_id');
            const hasProject = storageProjectId
              ? projectList.some(item => item.project_id === storageProjectId) : false;
            this.projectChange(hasProject ? storageProjectId : firstRealProjectId);
          }
        }
      } catch (e) {
        console.warn(e);
        this.$store.commit('setPageLoading', false);
      }
    },
    getDemoProjectUrl(id) {
      let siteUrl = window.SITE_URL;
      if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
      if (!siteUrl.endsWith('/')) siteUrl += '/';
      return `${window.location.origin + siteUrl}#/retrieve?projectId=${id}`;
    },
    experienceDemo() {
      window.open(this.demoProjectUrl);
    },
    async applyBusinessAccess() {
      try {
        this.isSelectLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['view_business'],
          resources: [],
        });
        window.open(res.data.apply_url);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isSelectLoading = false;
      }
    },
    jumpToHome() {
      this.$router.push({
        name: 'retrieve',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
      setTimeout(() => {
        this.$emit('reloadRouter');
      });
    },
    replaceMenuId(list) {
      list.forEach((item) => {
        if (item.id === 'search') {
          item.id = 'retrieve';
        }
        item.id = item.id.replaceAll('_', '-');
        if (item.children) {
          this.replaceMenuId(item.children);
        }
      });
      return list;
    },
    routerHandler(menu) {
      if (menu.id === this.activeTopMenu.id) {
        if (menu.id === 'retrieve') {
          this.$router.push({
            name: menu.id,
            query: {
              projectId: window.localStorage.getItem('project_id'),
            },
          });
          this.$emit('reloadRouter');
          return;
        } if (menu.id === 'extract') {
          if (this.$route.query.create) {
            this.$router.push({
              name: 'extract',
              query: {
                projectId: window.localStorage.getItem('project_id'),
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
                projectId: window.localStorage.getItem('project_id'),
              },
            });
          } else {
            this.$emit('reloadRouter');
          }
          return;
        } if (menu.id === 'dashboard') {
          if (this.$route.query.manageAction) {
            const newQuery = { ...this.$route.query };
            delete newQuery.manageAction;
            this.$router.push({
              name: 'dashboard',
              query: newQuery,
            });
          }
          this.$emit('reloadRouter');
          return;
        } if (menu.id === 'manage') {
          if (this.$route.name !== 'collection-item') {
            this.$router.push({
              name: 'manage',
              query: {
                projectId: window.localStorage.getItem('project_id'),
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
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      } else {
        this.$router.push({
          name: menu.id,
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      }
    },
    // 业务列表点击申请业务权限
    async applyProjectAccess(item) {
      this.$el.click(); // 手动关闭下拉
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['view_business'],
          resources: [{
            type: 'biz',
            id: item.bk_biz_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$bkLoading.hide();
      }
    },
    // 选择的业务是否有权限
    checkProjectAuth(project) {
      // eslint-disable-next-line camelcase
      if (project?.permission?.view_business) {
        return true;
      }
      this.$store.commit('updateProject', project.project_id);
      this.$store.dispatch('getApplyData', {
        action_ids: ['view_business'],
        resources: [{
          type: 'biz',
          id: project.bk_biz_id,
        }],
      }).then((res) => {
        this.$emit('auth', res.data);
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.$store.commit('setPageLoading', false);
        });
    },
    /**
             * 更新当前项目
             * @param  {String} projectId - 当前项目id
             */
    projectChange(projectId = '') {
      this.$store.commit('updateProject', projectId);
      if (projectId) {
        const project = this.myProjectList.find(item => item.project_id === projectId);
        if (!this.checkProjectAuth(project)) {
          return;
        }
      }
      window.localStorage.setItem('project_id', projectId);
      let bizId = '';
      for (const item of this.myProjectList) {
        if (item.project_id === projectId) {
          bizId = item.bk_biz_id;
          window.localStorage.setItem('bk_biz_id', bizId);
          break;
        }
      }
      projectId && this.setRouter(projectId, bizId); // 项目id不为空时，获取菜单
    },
    async setRouter(projectId, bizId) {
      try {
        const res = await this.$store.dispatch('getMenuList', projectId);
        const menuList = this.replaceMenuId(res.data || []);
        menuList.forEach((child) => {
          child.id = this.routeMap[child.id] || child.id;
          const menu = this.menuArr.find(menuItem => menuItem.id === child.id);
          if (menu) {
            this.deepUpdateMenu(menu, child);
          }
        });
        this.$store.commit('updateTopMenu', menuList);
        this.$store.commit('updateMenuProject', res.data || []);

        const manageGroupNavList = menuList.find(item => item.id === 'manage')?.children || [];
        const manageNavList = [];
        manageGroupNavList.forEach((group) => {
          manageNavList.push(...group.children);
        });
        const logCollectionNav = manageNavList.find(nav => nav.id === 'log-collection');
        if (logCollectionNav) {
          // 增加日志采集导航子菜单
          logCollectionNav.children = [{
            id: 'collection-item',
            name: this.$t('采集项'),
            project_manage: logCollectionNav.project_manage,
          }, {
            id: 'log-index-set',
            name: this.$t('索引集'),
            project_manage: logCollectionNav.project_manage,
          }];
        }
        this.$watch('$route.name', () => {
          const matchedList = this.$route.matched;
          const activeTopMenu = menuList.find((item) => {
            return matchedList.some(record => record.name === item.id);
          }) || {};
          this.$store.commit('updateActiveTopMenu', activeTopMenu);
          const activeManageNav = manageNavList.find((item) => {
            return matchedList.some(record => record.name === item.id);
          }) || {};
          this.$store.commit('updateActiveManageNav', activeManageNav);
          const activeManageSubNav = activeManageNav?.children?.find((item) => {
            return matchedList.some(record => record.name === item.id);
          }) || {};
          this.$store.commit('updateActiveManageSubNav', activeManageSubNav);
        }, {
          immediate: true,
        });

        return menuList;
      } catch (e) {
        console.warn(e);
      } finally {
        if (this.$route.name !== 'retrieve') {
          const RoutingHop = this.$route.name === 'notIndex'
            ? 'retrieve' : this.isFirstLoad
              ? this.$route.name ? this.$route.name : 'retrieve' : 'retrieve';
          const newQuery = {
            ...this.$route.query,
            projectId,
          };
          if (this.$route.query.bizId) {
            delete newQuery.projectId;
            newQuery.bizId = bizId;
          }
          this.$router.push({
            name: RoutingHop,
            params: {
              ...this.$route.params,
            },
            query: newQuery,
          });
        }
        setTimeout(() => {
          this.$emit('auth', null); // 表示不显示无业务权限的页面
          this.$store.commit('setPageLoading', false);
          this.isFirstLoad = false;
        }, 0);
      }
    },
    deepUpdateMenu(oldMenu, resMenu) { // resMenu结果返回的menu子级
      resMenu.name = oldMenu.name;
      resMenu.dropDown = oldMenu.dropDown;
      resMenu.dropDown = oldMenu.dropDown;
      resMenu.level = oldMenu.level;
      resMenu.isDashboard = oldMenu.isDashboard;
      if (resMenu.children) {
        if (oldMenu.children) {
          resMenu.children.forEach((item) => {
            item.id = this.routeMap[item.id] || item.id;
            if (resMenu.id === 'dashboard') {
              item.id = item.id.replaceAll('-', '_');
            }
            const menu = oldMenu.children.find(menuItem => menuItem.id === item.id);
            if (menu) {
              this.deepUpdateMenu(menu, item);
            }
          });
        }
      } else {
        if (oldMenu.children) {
          resMenu.children = oldMenu.children;
        }
      }
    },
    changeLanguage(value) {
      const domainList = location.hostname.split('.');

      // 本项目开发环境因为需要配置了 host 域名比联调环境多 1 级
      if (NODE_ENV === 'development') {
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
    triggerHandler(item, menu) {
      if (item.isDashboard) {
        this.$router.push({
          name: 'dashboard',
          query: {
            projectId: window.localStorage.getItem('project_id'),
            manageAction: item.id,
          },
        });
      } else if (this.$route.name !== item.id) {
        this.$router.push({
          name: item.id,
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      }
      this.$refs[`menu${menu.router}`][0].hide();
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
        window.open(window.BK_DOC_URL);
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
      }

      .bk-dropdown-content {
        line-height: normal;
        z-index: 2105;
        min-width: 112px;
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
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 4px;
        cursor: pointer;

        .icon-circle-container {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          border-radius: 16px;
          transition: all .2s;

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
