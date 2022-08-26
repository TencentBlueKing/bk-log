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
  <div class="dashboard-container" v-bkloading="{ isLoading }">
    <auth-container-page v-if="authPageInfo" :info="authPageInfo" />
    <iframe v-if="src" :src="src" ref="iframeRef" class="dashboard-iframe" @load="handleIframeLoad"></iframe>
  </div>
</template>

<script>
import AuthContainerPage from '@/components/common/auth-container-page';
import * as authorityMap from '../../common/authority-map';

export default {
  name: 'Dashboard',
  components: {
    AuthContainerPage,
  },
  data() {
    return {
      isLoading: true,
      authPageInfo: null, // 无查看权限显示无权限页面
      hasManageAuth: false,
      src: '',
    };
  },
  computed: {
    spaceUid() {
      return this.$store.state.spaceUid;
    },
    bkBizId() {
      return this.$store.state.bkBizId;
    },
  },
  watch: {
    '$route.query.spaceUid': {
      handler(val) {
        val && this.bkBizId && this.handleBizChange();
      },
      immediate: true,
    },
    '$route.query.bizId': {
      handler(val) {
        val && this.handleBizChange();
      },
      immediate: true,
    },
    '$route.query.manageAction'(manageAction) { // 在仪表盘页面点击导航管理
      this.handleClickManage(manageAction);
    },
    '$route.name'(manageAction) {
      this.handleClickManage(manageAction);
    },
  },
  mounted() {
    window.addEventListener('message', this.messageListener);
  },
  beforeDestroy() {
    window.removeEventListener('message', this.messageListener);
  },
  methods: {
    messageListener(e) {
      const pathname = e?.data?.pathname;
      if (pathname) {
        const matches = pathname.match(/\/d\/([^/]+)\//);
        const isInDashboard = !!matches && matches.length > 0;
        const dashboardId = isInDashboard ? matches[1] : '';
        let dashboardData = {};
        const existData = localStorage.getItem('___grafana_dashboard_data___');
        if (existData) {
          dashboardData = JSON.parse(existData);
        }
        dashboardData[this.bkBizId] = dashboardId;
        localStorage.setItem('___grafana_dashboard_data___', JSON.stringify(dashboardData));
      }
    },
    async handleBizChange() {
      this.isLoading = true;
      this.authPageInfo = null;
      this.hasManageAuth = false;
      this.src = '';
      const hasViewAuth = await this.checkViewAuth();
      if (hasViewAuth) {
        this.updateIframeSrc();
      }
    },
    // 检查是否有查看权限
    async checkViewAuth() {
      try {
        const res = await this.$store.dispatch('checkAndGetData', {
          action_ids: [authorityMap.VIEW_DASHBOARD_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        });
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          this.isLoading = false;
          return false;
        }
        return true;
      } catch (e) {
        console.warn(e);
        this.isLoading = false;
        return false;
      }
    },
    // 初始化 iframe 页面
    updateIframeSrc() {
      let siteUrl = window.SITE_URL;
      if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
      if (!siteUrl.endsWith('/')) siteUrl += '/';
      const prefixUrl = window.origin + siteUrl;
      // ?develop=2 开放导航栏
      let dashboardId = '';
      const dashboardData = localStorage.getItem('___grafana_dashboard_data___');
      if (dashboardData && (dashboardId = JSON.parse(dashboardData)[this.bkBizId])) {
        this.src = `${prefixUrl}grafana/d/${dashboardId}/?orgName=${this.bkBizId}`;
      } else {
        this.src = `${prefixUrl}grafana/?orgName=${this.bkBizId}`;
      }
      // + (NODE_ENV === 'development' ? '?develop=2' : '')
    },
    // iframe 页面加载完毕
    async handleIframeLoad() {
      const { manageAction } = this.$route.query;
      if (manageAction) { // 页面加载完成之后检查是不是需要管理仪表盘
        await this.handleClickManage(manageAction);
      }
      this.isLoading = false;
    },
    // 在仪表盘页面点击导航管理
    async handleClickManage(manageAction) {
      if (this.authPageInfo || !manageAction) { // 没查看权限直返
        return;
      }

      if (this.hasManageAuth) {
        this.handleRouteManage(manageAction);
      } else {
        const hasManageAuth = await this.checkManageAuth();
        if (hasManageAuth) {
          this.hasManageAuth = true;
          this.handleRouteManage(manageAction);
        }
      }
    },
    // 有管理权限，通知 iframe 进入相关管理界面
    handleRouteManage(manageAction) {
      const idMap = {
        // create_dashboard: 'create',
        // create_folder: 'folder',
        // import_dashboard: 'import',
        'create-dashboard': 'create',
        'create-folder': 'folder',
        'import-dashboard': 'import',
      };
      if (idMap[manageAction]) {
        this.$refs.iframeRef.contentWindow.postMessage(idMap[manageAction], '*');
      } else {
        this.$refs.iframeRef.contentWindow.postMessage('home', '*');
      }
    },
    // 检查是否有管理权限
    async checkManageAuth() {
      try {
        const res = await this.$store.dispatch('checkAndGetData', {
          action_ids: [authorityMap.MANAGE_DASHBOARD_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        });
        if (res.isAllowed === false) {
          this.$store.commit('updateAuthDialogData', res.data);
          this.isLoading = false;
          return false;
        }
        return true;
      } catch (e) {
        console.warn(e);
        this.isLoading = false;
        return false;
      }
    },
  },
};
</script>

<style scoped lang="scss">
  .dashboard-container {
    height: 100%;

    .dashboard-iframe {
      border: none;
      width: 100%;
      height: 100%;
    }
  }
</style>
