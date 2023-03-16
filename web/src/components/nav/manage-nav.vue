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
  <div class="sub-nav-container">
    <div
      class="back-container"
      v-if="$route.meta.needBack"
      @click="handleBack">
      <span class="bk-icon icon-arrows-left"></span>
    </div>
    <div class="main-title">{{ $route.meta.needBack ? getTitleName() : activeManageNav.name }}</div>
    <div v-if="isShowDetailName" class="collect-link">{{ getBaseName() }}</div>
    <ul
      class="sub-nav-list"
      v-if="activeManageNav.children && !$route.meta.needBack"
      data-test-id="logCollection_ul_logCollectionNavBox">
      <template v-for="navItem in activeManageNav.children">
        <li
          :class="{ 'sub-nav-item': true, 'active': navItem.id === activeManageSubNav.id }"
          :key="navItem.id" @click="handleClickSubNav(navItem.id)"
          :data-test-id="`logCollectionNavBox_li_${navItem.id}`">
          {{ navItem.name }}
        </li>
      </template>
    </ul>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  props: {
    name: {
      type: String,
      default: '',
    },
    subNavList: {
      type: Array,
      default: null,
    },
  },
  data() {
    return {
      baseRouteNameList: [ // 展示详情名称的路由列表
        'log-index-set-manage',
        'manage-collection',
        'bkdata-index-set-manage',
        'custom-report-detail',
        'es-index-set-manage',
        'bkdata-track-manage',
      ],
    };
  },
  computed: {
    ...mapState(['activeManageNav', 'activeManageSubNav']),
    isShowDetailName() { // 是否需要展示详情名称
      return this.baseRouteNameList.includes(this.$route.name);
    },
  },
  methods: {
    handleClickSubNav(id) {
      if (this.activeManageSubNav.id !== id) {
        this.$router.push({
          name: id,
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      }
    },
    handleBack() {
      if (this.$route.meta.backName) {
        const { query: { backRoute } } = this.$route;
        this.$router.push({
          name: !!backRoute ? backRoute : this.$route.meta.backName,
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      }
    },
    // 根据路由名获取菜单名称
    getTitleName() {
      const collectionName = this.$store.state.collect.curCollect?.collector_config_name;
      const map = {
        collectAdd: this.$t('新建采集项'),
        collectEdit: collectionName,
        collectField: collectionName,
        collectStorage: collectionName,
        collectStart: collectionName,
        collectStop: collectionName,
        'manage-collection': this.$t('采集详情'),
        'log-index-set-create': this.$t('新建索引集'),
        'log-index-set-edit': this.$t('编辑索引集'),
        'log-index-set-manage': this.$t('采集详情'),
        'bkdata-index-set-create': this.$t('新建索引集'),
        'bkdata-index-set-edit': this.$t('编辑索引集'),
        'bkdata-index-set-manage': this.$t('采集详情'),
        'es-index-set-create': this.$t('新建索引集'),
        'es-index-set-edit': this.$t('编辑索引集'),
        'es-index-set-manage': this.$t('采集详情'),
        'bkdata-track-create': this.$t('新建索引集'),
        'bkdata-track-edit': this.$t('编辑索引集'),
        'bkdata-track-manage': this.$t('采集详情'),
        'extract-link-create': this.$t('新建提取链路'),
        'extract-link-edit': this.$t('编辑提取链路'),
        'clean-create': this.$t('新增清洗'),
        'clean-edit': this.$t('编辑清洗'),
        'clean-template-create': this.$t('新建清洗模板'),
        'clean-template-edit': this.$t('编辑清洗模板'),
        'extract-create': this.$t('新建日志提取任务'),
        'extract-clone': this.$t('克隆日志提取任务'),
        'custom-report-create': this.$t('新建自定义上报'),
        'custom-report-edit': this.$t('编辑自定义上报'),
        'custom-report-detail': this.$t('采集详情'),
      };
      return map[this.$route.name];
    },
    getBaseName() {
      const collectionName = this.$store.state.collect.curCollect?.collector_config_name;
      const map = {
        'manage-collection': collectionName,
        'log-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'bkdata-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'bkdata-track-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'es-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'custom-report-detail': collectionName,
      };
      return `${this.$t('采集')}: ${map[this.$route.name] ?? ''}`;
    },
  },
};
</script>

<style lang="scss" scoped>
  .sub-nav-container {
    display: flex;
    align-items: center;
    width: 100%;
    height: 48px;
    padding: 0 20px;
    line-height: 24px;
    background-color: #fff;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .10);
    position: fixed;
    top: 51px;
    z-index: 9;

    .main-title {
      font-size: 16px;
      color: #313238;
    }

    .back-container {
      .icon-arrows-left {
        font-size: 30px;
        color: #3a84ff;
        cursor: pointer;

        &:hover {
          color: #699df4;
        }
      }
    }

    .sub-nav-list {
      display: flex;
      font-size: 14px;
      color: #63656e;
      margin-left: 35px;

      .sub-nav-item {
        height: 52px;
        line-height: 52px;
        padding: 0 10px;
        margin: 0 25px;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: color, border-color .3s;

        &:hover,
        &.active {
          color: #3a84ff;
          border-bottom: 3px solid #3a84ff;
          transition: color, border-color .3s;
        }
      }
    }

    .collect-link {
      margin-left: 12px;
      font-size: 12px;
      border-radius: 2px;
      padding: 0 4px;
      color: #63656e;
      background: #f0f1f5;
    }
  }
</style>
