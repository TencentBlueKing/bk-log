<template>
  <div class="access-manage-container" v-bkloading="{ isLoading: basicLoading }">
    <auth-page v-if="authPageInfo" :info="authPageInfo"></auth-page>
    <template v-if="!authPageInfo && !basicLoading && curIndexSet">
      <bk-tab :active.sync="activePanel" type="border-card">
        <bk-tab-panel v-for="panel in panels" v-bind="panel" :key="panel.name"></bk-tab-panel>
      </bk-tab>
      <keep-alive>
        <component
          class="tab-content"
          :index-set-data="curIndexSet"
          :index-set-id="curIndexSet.index_set_id"
          :is="dynamicComponent"
          @update-active-panel="activePanel = $event"></component>
      </keep-alive>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import AuthPage from '@/components/common/auth-page';
import BasicInfo from './BasicInfo';
import FieldInfo from './FieldInfo';
import UsageDetails from '@/views/manage2/manage-access/components/usage-details';

export default {
  name: 'IndexSetManage',
  components: {
    AuthPage,
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
        { name: 'basicInfo', label: this.$t('基本信息') },
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
          action_ids: ['manage_indices'],
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
