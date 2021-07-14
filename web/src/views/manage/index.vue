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
  <section class="manage-wrapper">
    <top-nav :title="title" :menu="menu"></top-nav>
    <router-view class="manage-container" :key="$route.fullPath"></router-view>
  </section>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import topNav from '@/components/nav/top-nav';
export default {
  name: 'manage-index',
  components: {
    topNav,
  },
  data() {
    return {
      title: '',
      menu: null,
    };
  },
  computed: {
    ...mapState({
      menuList: state => state.menuList,
      currentMenu: state => state.currentMenu,
    }),
    ...mapGetters('globals', ['globalsData']),
  },
  watch: {
    '$route.name'(newVal) {
      this.getMenu(this.menuList, newVal);
    },
  },
  created() {
    this.getGlobalsData();
    this.getMenu(this.menuList, this.$route.name);
  },
  methods: {
    getMenu(menuList, route, parent) {
      menuList.forEach((item) => {
        if (item.id === route) {
          if (parent) {
            const menu = JSON.parse(JSON.stringify(parent === true ? item : parent));
            if (menu.id === 'indexSet') {
              delete menu.children;
            }
            this.menu = menu;
            if (parent.id === 'manage') {
              this.title = item.level === 4 ? item.name : item.level === 5 ? item.name : '';
            } else if (parent.id === 'indexSet') {
              this.title = item.level === 3 ? item.name : '';
            } else {
              this.title = '';
            }
            // 如需要，可以将title存入store，方便做同路由返回操作。
          }
        } else if (item.id !== route && item.children) {
          this.getMenu(item.children, route, item.dropDown ? item.dropDown : (parent === true ? item : parent));
        }
      });
    },
    // 获取全局数据
    getGlobalsData() {
      return new Promise((resolve, reject) => {
        this.$http.request('collect/globals', { query: {} }).then((res) => {
          if (res.data) {
            const globalsData = res.data || {};
            this.$store.commit('globals/setGlobalsData', globalsData);
            resolve(res.data);
          }
        })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
};
</script>

<style lang="scss">
  @import '../../scss/mixins/scroller.scss';

  .manage-wrapper {
    min-width: 1280px;
    height: 100%;
  }

  .manage-container {
    height: calc(100% - 60px);
    overflow-x: hidden;
    overflow-y: auto;

    @include scroller($backgroundColor: #c4c6cc, $width: 8px);

    .bk-table {
      background: #fff;

      .bk-table-pagination-wrapper {
        background: #fafbfd;
      }
    }
  }

  .bk-table .cell {
    display: block;
  }
</style>
