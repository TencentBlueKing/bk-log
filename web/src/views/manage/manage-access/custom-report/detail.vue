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
  <div
    v-bkloading="{ isLoading: basicLoading }"
    ref="detailRef"
    :style="`padding-right: ${introWidth + 20}px;`"
    class="custom-report-detail-container access-manage-container">
    <auth-container-page v-if="authPageInfo" :info="authPageInfo"></auth-container-page>
    <template v-if="!authPageInfo && !basicLoading && reportDetail">
      <basic-tab :active.sync="activePanel" type="border-card">
        <bk-tab-panel v-for="panel in panels" v-bind="panel" :key="panel.name"></bk-tab-panel>
        <div class="go-search" slot="setting">
          <div class="search-text">
            <span class="bk-icon icon-info"></span>
            <i18n path="数据采集好了，去 {0}">
              <span class="search-button" @click="handleGoSearch">{{$t('查看数据')}}</span>
            </i18n>
          </div>
        </div>
      </basic-tab>
      <keep-alive>
        <component
          class="tab-content"
          :collector-data="reportDetail"
          :index-set-id="reportDetail.index_set_id || ''"
          :is="dynamicComponent"
          @update-active-panel="activePanel = $event"></component>
      </keep-alive>
    </template>

    <div
      :class="['intro-container',isDraging && 'draging-move']"
      :style="`width: ${ introWidth }px`">
      <div :class="`drag-item ${!introWidth && 'hidden-drag'}`" :style="`right: ${introWidth - 18}px`">
        <span
          class="bk-icon icon-more"
          @mousedown.left="dragBegin"></span>
      </div>
      <intro-panel
        :data="reportDetail"
        :is-open-window="isOpenWindow"
        @handleActiveDetails="handleActiveDetails" />
    </div>
  </div>
</template>

<script>
import AuthContainerPage from '@/components/common/auth-container-page';
import BasicInfo from '../log-collection/collection-item/manage-collection/basic-info';
import DataStorage from '../log-collection/collection-item/manage-collection/data-storage';
import DataStatus from '../log-collection/collection-item/manage-collection/data-status';
import UsageDetails from '@/views/manage/manage-access/components/usage-details';
import dragMixin from '@/mixins/drag-mixin';
import IntroPanel from './components/intro-panel';
import BasicTab from '@/components/basic-tab';
import * as authorityMap from '../../../../common/authority-map';

export default {
  name: 'CollectionItem',
  components: {
    AuthContainerPage,
    BasicInfo,
    DataStorage,
    DataStatus,
    UsageDetails,
    IntroPanel,
    BasicTab,
  },
  mixins: [dragMixin],
  data() {
    return {
      basicLoading: true,
      authPageInfo: null,
      reportDetail: {},
      activePanel: this.$route.query.type || 'basicInfo',
      isOpenWindow: true,
      panels: [
        { name: 'basicInfo', label: this.$t('配置信息') },
        { name: 'dataStorage', label: this.$t('数据存储') },
        { name: 'dataStatus', label: this.$t('数据状态') },
        { name: 'usageDetails', label: this.$t('使用详情') },
      ],
    };
  },
  computed: {
    dynamicComponent() {
      const componentMaP = {
        basicInfo: 'BasicInfo',
        dataStorage: 'DataStorage',
        dataStatus: 'DataStatus',
        usageDetails: 'UsageDetails',
      };
      return componentMaP[this.activePanel] || 'BasicInfo';
    },
  },
  created() {
    this.initPage();
  },
  mounted() {
    this.$nextTick(() => {
      this.maxIntroWidth = this.$refs.detailRef.clientWidth - 380;
    });
  },
  methods: {
    async initPage() {
      // 进入路由需要先判断权限
      try {
        const paramData = {
          action_ids: [authorityMap.VIEW_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: this.$route.params.collectorId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          // 显示无权限页面
        } else {
          // 正常显示页面
          const { data: reportDetail } = await this.$http.request('collect/details', {
            params: {
              collector_config_id: this.$route.params.collectorId,
            },
          });
          this.reportDetail = reportDetail;
          this.$store.commit('collect/setCurCollect', reportDetail);
        }
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    handleActiveDetails(state) {
      this.isOpenWindow = state;
      this.introWidth = state ? 360 : 0;
    },
    handleGoSearch() {
      const params = {
        indexId: this.reportDetail.index_set_id
          ? this.reportDetail.index_set_id
          : this.reportDetail.bkdata_index_set_ids[0],
      };
      this.$router.push({
        name: 'retrieve',
        params,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
  },
};
</script>

<style lang="scss">
  .intro-container {
    position: fixed;
    top: 99px;
    right: 0;
    z-index: 999;
    height: calc(100vh - 99px);
    overflow: hidden;
    border-left: 1px solid transparent;

    .drag-item {
      width: 20px;
      height: 40px;
      display: inline-block;
      color: #c4c6cc;
      position: absolute;
      z-index: 100;
      right: 304px;
      top: 48%;
      user-select: none;
      cursor: col-resize;

      &.hidden-drag {
        display: none;
      }

      .icon-more::after {
        content: '\e189';
        position: absolute;
        left: 0;
        top: 12px;
      }
    }

    &.draging-move {
      border-left-color: #3a84ff;
    }
  }
</style>
