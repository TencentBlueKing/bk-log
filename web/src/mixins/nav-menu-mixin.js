/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import { mapState } from 'vuex';
import { menuArr } from '../components/nav/complete-menu';

export default {
  data() {
    return {
      routeMap: { // 后端返回的导航id映射
        search: 'retrieve',
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
      activeTopMenu: state => state.activeTopMenu,
      projectId: state => state.projectId,
      bkBizId: state => state.bkBizId,
      myProjectList: state => state.myProjectList,
    }),
  },
  watch: {
    '$route.query'(val) {
      const queryObj = JSON.parse(JSON.stringify(val));
      if (queryObj.from) {
        this.$store.commit('updateAsIframe', queryObj.from);
        this.$store.commit('updateIframeQuery', queryObj);
      }
    },
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
              return this.checkProjectChange(demoProject.project_id);
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
          this.checkProjectChange();
          this.$emit('welcome', args);
        } else { // 正常业务
          this.$store.commit('updateMyProjectList', projectList);
          // 首先从查询参数找，然后从storage里面找，还找不到就返回第一个不是demo的业务
          const firstRealProjectId = projectList.find(item => item.bk_biz_id !== demoId).project_id;
          if (projectId || bizId) {
            const matchProject = projectList.find(item => item.project_id === projectId || item.bk_biz_id === bizId);
            this.checkProjectChange(matchProject ? matchProject.project_id : firstRealProjectId);
          } else {
            const storageProjectId = window.localStorage.getItem('project_id');
            const hasProject = storageProjectId
              ? projectList.some(item => item.project_id === storageProjectId) : false;
            this.checkProjectChange(hasProject ? storageProjectId : firstRealProjectId);
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
    checkProjectChange(projectId = '') {
      if (!this.isFirstLoad && this.$route.meta.needBack) {
        this.$store.commit('updateRouterLeaveTip', true);

        this.$bkInfo({
          title: this.$t('pageLeaveTips'),
          confirmFn: () => {
            this.projectChange(projectId);
          },
          cancelFn: () => {
            this.$store.commit('updateRouterLeaveTip', false);
          },
        });
        return;
      }
      this.projectChange(projectId);
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
    // 选择的业务是否有权限
    checkProjectAuth(project) {
      // eslint-disable-next-line camelcase
      if (project && project.permission && project.permission.view_business) {
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

          const topMenuList =  activeTopMenu.children?.length ? activeTopMenu.children : [];
          const topMenuChildren = topMenuList.reduce((pre, cur) => {
            if (cur.children?.length) {
              pre.push(...cur.children);
            }
            return pre;
          }, []);
          const activeManageNav = topMenuChildren.find((item) => {
            return matchedList.some(record => record.name === item.id);
          }) || {};
          this.$store.commit('updateActiveManageNav', activeManageNav);

          const activeManageSubNav = activeManageNav.children
            ? activeManageNav.children.find((item) => {
              return matchedList.some(record => record.name === item.id);
            }) : {};
          this.$store.commit('updateActiveManageSubNav', activeManageSubNav);
        }, {
          immediate: true,
        });

        return menuList;
      } catch (e) {
        console.warn(e);
      } finally {
        if (this.$route.name !== 'retrieve' && !this.isFirstLoad) {
          // 所有页面的子路由在切换业务的时候都统一返回到父级页面
          const { name, meta, params, query } = this.$route;
          const RoutingHop = meta.needBack && !this.isFirstLoad ? meta.backName : name ? name : 'retrieve';
          const newQuery = {
            ...query,
            projectId,
          };
          if (query.bizId) {
            delete newQuery.projectId;
            newQuery.bizId = bizId;
          }
          if (params.indexId) delete params.indexId;
          this.$store.commit('setPageLoading', true);
          this.$router.push({
            name: RoutingHop,
            params: {
              ...params,
            },
            query: newQuery,
          });
        }
        setTimeout(() => {
          this.$emit('auth', null); // 表示不显示无业务权限的页面
          this.$store.commit('setPageLoading', false);
          this.isFirstLoad = false;
          this.$store.commit('updateRouterLeaveTip', false);
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
            // if (resMenu.id === 'dashboard') {
            //   item.id = item.id.replaceAll('-', '_');
            // }
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
  },
};
