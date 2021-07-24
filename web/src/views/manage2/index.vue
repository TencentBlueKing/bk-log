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
  <div class="manage-container">
    <bk-navigation
      class="hack-king-navigation"
      navigation-type="left-right"
      head-height="0"
      header-title=""
      hover-width="200"
      default-open
      :theme-color="navThemeColor"
      @toggle="handleToggle">
      <template slot="menu">
        <bk-navigation-menu :item-default-bg-color="navThemeColor" :default-active="activeManageNav.id">
          <template v-for="groupItem in manageNavList">
            <bk-navigation-menu-group
              :key="groupItem.id"
              :group-name="isExpand ? groupItem.name : groupItem.keyword">
              <template v-for="navItem in groupItem.children">
                <bk-navigation-menu-item
                  :key="navItem.id"
                  :id="navItem.id"
                  :icon="getMenuIcon(navItem)"
                  @click="handleClickNavItem(navItem.id)">
                  {{ isExpand ? navItem.name : '' }}
                </bk-navigation-menu-item>
              </template>
            </bk-navigation-menu-group>
          </template>
        </bk-navigation-menu>
      </template>
      <div class="navigation-content">
        <sub-nav></sub-nav>
        <router-view class="manage-content" :key="routerKey"></router-view>
      </div>
    </bk-navigation>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import SubNav from '@/components/nav/manage-nav';

export default {
  name: 'manage-index',
  components: {
    SubNav,
  },
  data() {
    return {
      navThemeColor: '#2c354d',
      routerKey: 0,
      isExpand: true,
    };
  },
  computed: {
    ...mapState(['topMenu', 'activeManageNav']),
    ...mapState('globals', ['globalsData']),
    manageNavList() {
      return this.topMenu.find(item => item.id === 'manage')?.children || [];
    },
  },
  created() {
    this.getGlobalsData();
  },
  methods: {
    getMenuIcon(item) {
      if (item.icon) {
        return `log-icon icon-${item.icon}`;
      }

      return 'bk-icon icon-home-shape';
    },
    handleClickNavItem(id) {
      if (this.activeManageNav.id !== id) {
        this.$router.push({
          name: id,
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      } else {
        this.routerKey += 1;
      }
    },
    // 获取全局数据
    getGlobalsData() {
      if (Object.keys(this.globalsData).length) {
        return;
      }
      this.$http.request('collect/globals').then((res) => {
        this.$store.commit('globals/setGlobalsData', res.data);
      })
        .catch((e) => {
          console.warn(e);
        });
    },
    handleToggle(data) {
      this.isExpand = data;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/scroller.scss';

  .manage-container {
    height: 100%;

    .navigation-content {
      min-width: 1280px;
      height: 100%;
      background-color: #fafbfd;

      .manage-content {
        height: calc(100% - 52px);

        @include scroller($backgroundColor: #C4C6CC, $width: 8px);
      }
    }

    /deep/ .bk-table {
      background: #fff;

      .cell {
        display: block;
      }

      .bk-table-pagination-wrapper {
        background: #fafbfd;
      }
    }
  }
</style>
