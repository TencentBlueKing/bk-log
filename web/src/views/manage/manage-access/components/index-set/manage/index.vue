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
  <div class="access-manage-container" v-bkloading="{ isLoading: basicLoading }">
    <auth-container-page v-if="authPageInfo" :info="authPageInfo"></auth-container-page>
    <template v-if="!authPageInfo && !basicLoading && curIndexSet">
      <bk-tab :active.sync="activePanel" type="border-card">
        <bk-tab-panel
          v-for="panel in panels"
          v-bind="panel"
          :key="panel.name"></bk-tab-panel>
      </bk-tab>
      <keep-alive>
        <component
          class="tab-content"
          :index-set-data="curIndexSet"
          :index-set-id="curIndexSet.index_set_id"
          :is="dynamicComponent"
          @update-active-panel="activePanel = $event" />
      </keep-alive>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import AuthContainerPage from '@/components/common/auth-container-page';
import BasicInfo from './basic-info';
import FieldInfo from './field-info';
import UsageDetails from '@/views/manage/manage-access/components/usage-details';
import * as authorityMap from '../../../../../../common/authority-map';

export default {
  name: 'IndexSetManage',
  components: {
    AuthContainerPage,
    BasicInfo,
    FieldInfo,
    UsageDetails,
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      basicLoading: true,
      authPageInfo: null,
      activePanel: this.$route.query.type || 'basicInfo',
      panels: [
        { name: 'basicInfo', label: this.$t('配置信息') },
        { name: 'usageDetails', label: this.$t('使用详情') },
        { name: 'fieldInfo', label: this.$t('字段信息') },
      ],
    };
  },
  computed: {
    ...mapState('collect', ['curIndexSet', 'scenarioMap']),
    dynamicComponent() {
      const componentMaP = {
        basicInfo: 'BasicInfo',
        usageDetails: 'UsageDetails',
        fieldInfo: 'FieldInfo',
      };
      return componentMaP[this.activePanel] || 'BasicInfo';
    },
  },
  created() {
    this.initPage();
  },
  methods: {
    async initPage() {
      // 进入路由需要先判断权限
      const indexSetId = this.$route.params.indexSetId.toString();
      try {
        const paramData = {
          action_ids: [authorityMap.MANAGE_INDICES_AUTH],
          resources: [{
            type: 'indices',
            id: indexSetId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          // 显示无权限页面
        } else {
          // 正常显示页面
          await Promise.all([
            this.fetchIndexSetData(indexSetId),
            this.fetchScenarioMap(),
          ]);
        }
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    // 索引集详情
    async fetchIndexSetData(indexSetId) {
      if (!this.curIndexSet.index_set_id || this.curIndexSet.index_set_id.toString() !== indexSetId) {
        const { data: indexSetData } = await this.$http.request('indexSet/info', {
          params: {
            index_set_id: indexSetId,
          },
        });
        this.$store.commit('collect/updateCurIndexSet', indexSetData);
      }
    },
    // 数据源(场景)映射关系
    async fetchScenarioMap() {
      if (!this.scenarioMap) {
        const { data } = await this.$http.request('meta/scenario');
        const map = {};
        data.forEach((item) => {
          map[item.scenario_id] = item.scenario_name;
        });
        this.$store.commit('collect/updateScenarioMap', map);
      }
    },
  },
};
</script>
