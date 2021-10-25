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
  <div class="biz-menu-select">
    <div class="menu-select">
      <span tabindex="{0}" class="menu-select-name" @mousedown="handleClickBizSelect">
        {{ bizName }}
        <i
          class="bk-select-angle bk-icon icon-angle-down select-icon"
          :style="{ transform: `rotate(${!showBizList ? '0deg' : '-180deg'})` }"
        />
      </span>
    </div>
    <div class="menu-select-list" :style="{ display: showBizList ? 'flex' : 'none' }">
      <bk-input
        ref="menuSearchInput"
        class="menu-select-search"
        right-icon="bk-icon icon-search"
        :placeholder="$t('搜索')"
        :clearable="false"
        :value="keyword"
        @clear="handleBizSearch"
        @change="handleBizSearch"
        @blur="() => (showBizList = false)">
      </bk-input>
      <ul class="biz-list">
        <template v-if="bizList.length">
          <li
            v-for="(item) in bizList"
            :key="item.id"
            :class="['list-item', { 'is-select': item.project_id === projectId }]"
            @mousedown="() => projectChange(item.project_id)">
            {{ item.project_name }}
          </li>
        </template>
        <li v-else class="list-empty">{{ $t('无匹配的数据') }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { menuArr } from './nav/complete-menu';

export default {
  data() {
    return {
      bizId: '',
      keyword: '',
      demoProjectUrl: '', // demo 业务链接
      showBizList: false,
      isSelectLoading: false,
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
      projectId: state => state.projectId,
      myProjectList: state => state.myProjectList,
    }),
    bizName() {
      return this.myProjectList.find(item => item.project_id === this.projectId)?.project_name;
    },
    // 业务列表
    bizList() {
      return this.myProjectList.filter(item => item.project_name.includes(this.keyword));
    },
  },
  created() {
    // this.requestMyProjectList();
  },
  methods: {
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
    projectChange(projectId) {
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
    async setRouter(projectId, bizId) {
      try {
        const res = await this.$store.dispatch('getMenuList', projectId);
        const menuList = this.replaceMenuId(res.data || []);
        menuList.forEach((child) => {
          child.id = this.routeMap[child.id] || child.id;
          const menu = menuArr.find(menuItem => menuItem.id === child.id);
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
        this.$store.commit('setPageLoading', true);
        const newQuery = {
          ...this.$route.query,
          projectId,
        };
        if (this.$route.query.bizId) {
          delete newQuery.projectId;
          newQuery.bizId = bizId;
        }
        this.$router.push({
          name: this.$route.name,
          params: {
            ...this.$route.params,
          },
          query: newQuery,
        });
        setTimeout(() => {
          this.$emit('auth', null); // 表示不显示无业务权限的页面
          this.$store.commit('setPageLoading', false);
          this.isFirstLoad = false;
        }, 0);
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
    handleClickBizSelect() {
      this.showBizList = !this.showBizList;
      setTimeout(() => {
        this.$refs.menuSearchInput.focus();
      }, 100);
    },
    handleBizSearch(v) {
      this.keyword = v;
    },
    handleBizChange() {},
  },
};
</script>

<style lang="scss">
  @import '../scss/mixins/flex.scss';
  @import '../scss/mixins/ellipsis.scss';

  .biz-menu-select {
    padding: 0 16px;
    .menu-select {
      flex: 1;
      display: flex;
      position: relative;
      height: 32px;
      border: 1px solid #2c354d;
      border-radius: 2px;
      background-color: rgba(255,255,255,.05);
      &-name {
        padding: 0 36px 0 10px;
        flex: 1;
        min-width: 227px;
        position: relative;
        color: #acb2c6;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 30px;
        // @include flex-align(center);
        .select-icon {
          position: absolute;
          top: 4px;
          right: 10px;
          font-size: 18px;
          transition: transform .3s cubic-bezier(.4,0,.2,1),-webkit-transform .3s cubic-bezier(.4,0,.2,1);
        }
      }
      &-list {
        display: flex;
        position: fixed;
        left: 16px;
        top: 102px;
        flex-direction: column;
        z-index: 99;
        background-color: #363f56;
        overflow: auto;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,.20);
        .biz-list {
          display: flex;
          flex-direction: column;
          max-height: 240px;
          overflow: auto;
          min-width: 270px;
          padding: 6px 0;
          .list-empty,
          %list-empty {
            height: 32px;
            flex: 0 0 32px;
            padding: 0 16px;
            color: #acb5c6;
            font-size: 12px;
            @include flex-center;
          }
          .list-item {
            justify-content: flex-start;
            @extend %list-empty;
            @include ellipsis;
            @include flex-align(left);
            &.is-select,
            &%is-select {
              color: #fff;
              background-color: #2c354d;
            }
            &:hover {
              cursor: pointer;
              @extend %is-select;
            }
          }
          &::-webkit-scrollbar {
            width: 4px;
            height: 4px;
          }
          &::-webkit-scrollbar-thumb {
            border-radius: 20px;
            background: #363f56;
            box-shadow: inset 0 0 6px rgba(204, 204, 204, .3);
          }
        }
      }
      &-search {
        margin: 0 5px;
        flex: 1;
        width: inherit;
        .bk-form-input {
          border: 0;
          border-bottom: 1px solid rgba(240,241,245,.16);
          border-radius: 0;
          background-color: #363f56;
          color: #acb5c6;
          &:focus {
            background-color: #363f56 !important;
            border-color: rgba(240,241,245,.16) !important;
          }
        }
      }
    }
    .menu-title {
      height: 32px;
      flex: 1;
      border-radius: 4px;
      width: 32px;
      min-width: 32px;
      max-width: 32px;
      background: #a09e21;
      color: #f4f7fa;
      font-weight: bold;

      @include flex-center;
    }
  }
</style>
