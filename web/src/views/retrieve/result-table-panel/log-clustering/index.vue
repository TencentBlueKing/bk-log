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
  <div>
    <div class="log-cluster-table-container" v-if="!globalLoading">
      <div
        class="cluster-nav"
        v-if="exhibitAll"
        data-test-id="cluster_div_fingerOperate">
        <div class="bk-button-group">
          <bk-button
            size="small"
            v-for="(item) of clusterNavList"
            :key="item.id"
            :class="active === item.id ? 'is-selected' : ''"
            @click="handleClickNav(item.id)">
            {{item.name}}
          </bk-button>
        </div>

        <finger-operate
          v-if="active === 'dataFingerprint'"
          :finger-operate-data="fingerOperateData"
          :request-data="requestData"
          @handleFingerOperate="handleFingerOperate"></finger-operate>
      </div>

      <bk-alert
        v-if="active === 'dataFingerprint' && signatureSwitch && !exhibitAll"
        :title="$t('clusterAlert')"
        closable
        type="info">
      </bk-alert>

      <div v-if="exhibitAll">
        <clustering-loader
          is-loading
          v-if="tableLoading"
          :width-list="smallLoaderWidthList">
        </clustering-loader>
        <div v-else>
          <ignore-table
            v-if="active === 'ignoreNumbers' || active === 'ignoreSymbol'"
            v-bind="$attrs"
            v-on="$listeners"
            :total-fields="totalFields"
            :origin-table-list="originTableList"
            :clustering-field="clusteringField"
            :active="active" />
          <data-fingerprint
            v-if="active === 'dataFingerprint'"
            v-bind="$attrs"
            v-on="$listeners"
            :cluster-switch="clusterSwitch"
            :request-data="requestData"
            :config-data="configData"
            :finger-list="fingerList"
            :loader-width-list="smallLoaderWidthList"
            :is-page-over="isPageOver"
            @paginationOptions="paginationOptions" />
        </div>
      </div>

      <bk-table
        v-else
        class="no-text-table"
        :data="[]">
        <div slot="empty">
          <div class="empty-text">
            <span class="bk-table-empty-icon bk-icon icon-empty"></span>
            <p>{{exhibitText}}</p>
            <span class="empty-leave" @click="handleLeaveCurrent">
              {{exhibitOperate}}
            </span>
          </div>
        </div>
      </bk-table>
    </div>
    <clustering-loader
      is-loading
      v-else
      :width-list="loadingWidthList.global">
    </clustering-loader>
  </div>
</template>

<script>
import DataFingerprint from './DataFingerprint';
import IgnoreTable from './IgnoreTable';
import ClusteringLoader from '@/skeleton/clustering-loader';
import fingerOperate from './components/fingerOperate';
import { mapGetters } from 'vuex';

export default {
  components: {
    DataFingerprint,
    IgnoreTable,
    ClusteringLoader,
    fingerOperate,
  },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    configData: {
      type: Object,
      require: true,
    },
    cleanConfig: {
      type: Object,
      require: true,
    },
    totalFields: {
      type: Array,
      require: true,
    },
    originTableList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      active: 'ignoreNumbers',
      clusterSwitch: false, // 日志聚类开关
      signatureSwitch: false, // 数据指纹开关
      configID: -1, // 采集项ID
      exhibitAll: false, // 是否显示nav
      alreadyClickNav: [], // 已加载过的nav
      globalLoading: false, // 日志聚类大loading
      tableLoading: false, // 详情loading
      isShowCustomize: true, // 是否显示自定义
      clusterNavList: [{
        id: 'ignoreNumbers',
        name: this.$t('忽略数字'),
      }, {
        id: 'ignoreSymbol',
        name: this.$t('忽略符号'),
      }, {
        id: 'dataFingerprint',
        name: this.$t('数据指纹'),
      }],
      fingerOperateData: {
        partterSize: 0, // slider当前值
        sliderMaxVal: 0, // partter最大值
        comparedList: [], // 同比List
        partterList: [], // partter敏感度List
        isNear24: false, // 近24h
        isShowCustomize: true, // 是否显示自定义
        signatureSwitch: false, // 数据指纹开关
      },
      requestData: { // 数据请求
        pattern_level: '',
        year_on_year_hour: 0,
        show_new_pattern: false,
        size: 10000,
      },
      fingerList: [], // 数据指纹List
      isPageOver: false,
      fingerListPage: 1,
      fingerListPageSize: 50,
      allFingerList: [], // 所有数据指纹List
      loadingWidthList: { // loading表头宽度列表
        global: [''],
        ignore: [60, 90, 90, ''],
        notCompared: [150, 90, 90, ''],
        compared: [150, 90, 90, 100, 100, ''],
      },
    };
  },
  computed: {
    ...mapGetters({
      globalsData: 'globals/globalsData',
    }),
    smallLoaderWidthList() {
      if (this.active !== 'dataFingerprint') {
        return this.loadingWidthList.ignore;
      }
      return this.requestData.year_on_year_hour > 0
        ? this.loadingWidthList.compared
        : this.loadingWidthList.notCompared;
    },
    exhibitText() {
      return this.clusterSwitch ? (this.configID ? this.$t('goCleanMessage') : this.$t('noConfigIDMessage')) : this.$t('goSettingMessage');
    },
    exhibitOperate() {
      return this.clusterSwitch ? (this.configID ? this.$t('跳转到日志清洗') : '') : this.$t('去设置');
    },
    clusteringField() {
      return this.configData?.extra?.clustering_field || '';
    },
  },
  watch: {
    configData: {
      deep: true,
      immediate: true,
      handler(val) {
        this.clusterSwitch = val.is_active;
        this.fingerOperateData.signatureSwitch = val.extra.signature_switch;
        this.configID = this.cleanConfig.extra?.collector_config_id;
      },
    },
    originTableList: {
      handler(newList) {
        if (newList.length > 0) {
          if (this.active === 'dataFingerprint' && this.configData.extra.signature_switch) {
            this.alreadyClickNav.push('dataFingerprint');
            this.requestData.pattern_level === '' && this.initTable();
            this.requestFinger();
          }
        }
      },
    },
    totalFields: {
      deep: true,
      immediate: true,
      handler(newList) {
        if (newList.length > 0) {
          if (!this.configData.is_active) {
            this.exhibitAll = false;
            return;
          }
          this.requestData.pattern_level === '' && this.initTable();
          this.exhibitAll = newList.some(el => el.field_type === 'text');
        }
      },
    },
    '$route.params.indexId'() {
      this.alreadyClickNav = [];
      this.globalLoading = true;
      setTimeout(() => {
        this.globalLoading = false;
      }, 750);
    },
    requestData: {
      deep: true,
      handler() {
        this.requestFinger();
      },
    },
  },
  methods: {
    handleClickNav(id) {
      this.active = id;
      const isClick = this.alreadyClickNav.some(el => el === id);
      if (!isClick) {
        this.alreadyClickNav.push(id);
        if (this.alreadyClickNav.includes('dataFingerprint') && this.configData.extra.signature_switch) {
          this.requestFinger();
        }
      }
    },
    // 初始化数据指纹配置
    initTable() {
      const {
        log_clustering_level_year_on_year: yearOnYearList,
        log_clustering_level: clusterLevel,
      } = this.globalsData;
      let patternLevel;
      if (clusterLevel && clusterLevel.length > 0) {
        if (clusterLevel.length % 2 === 1) {
          patternLevel = (clusterLevel.length + 1) / 2;
        } else {
          patternLevel = clusterLevel.length  / 2;
        }
      }
      Object.assign(this.fingerOperateData, {
        partterSize: patternLevel - 1,
        sliderMaxVal: clusterLevel.length - 1,
        partterList: clusterLevel,
        comparedList: yearOnYearList,
      });
      Object.assign(this.requestData, {
        pattern_level: clusterLevel[patternLevel - 1],
      });
    },
    // 数据指纹操作
    handleFingerOperate(operateType, val) {
      if (operateType === 'compared') {
        this.requestData.year_on_year_hour = val;
      }
      if (operateType === 'partterSize') {
        this.requestData.pattern_level = val;
      }
      if (operateType === 'isShowNear') {
        this.requestData.show_new_pattern = val;
      }
      if (operateType === 'enterCustomize') {
        this.handleEnterCompared(val);
      }
      if (operateType === 'customize') {
        this.fingerOperateData.isShowCustomize = val;
      }
    },
    // 跳转
    handleLeaveCurrent() {
      if (!this.clusterSwitch) {
        this.$emit('showSettingLog');
        return;
      }
      if (this.configID && this.configID > 0) {
        this.$router.push({
          name: 'clean-edit',
          params: { collectorId: this.configID },
          query: { projectId: window.localStorage.getItem('project_id') },
        });
      }
    },
    // 同比自定义输入
    handleEnterCompared(val) {
      const matchVal = val.match(/^(\d+)h$/);
      if (!matchVal) {
        this.$bkMessage({
          theme: 'warning',
          message: this.$t('请按照提示输入'),
        });
        return;
      }
      this.fingerOperateData.isShowCustomize = true;
      const isRepeat =  this.fingerOperateData.comparedList.some(el => el.id === Number(matchVal[1]));
      if (isRepeat) {
        this.requestData.year_on_year_hour = Number(matchVal[1]);
        return;
      }
      this.fingerOperateData.comparedList.push({
        id: Number(matchVal[1]),
        name: `${matchVal[1]}小时前`,
      });
      this.requestData.year_on_year_hour = Number(matchVal[1]);
    },
    // 请求数据指纹
    requestFinger() {
      this.tableLoading = true;
      this.$http.request('/logClustering/clusterSearch', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data: {
          ...this.retrieveParams,
          ...this.requestData,
        },
      })
        .then((res) => {
          this.fingerListPage = 1;
          this.allFingerList = res.data;
          this.fingerList = res.data.slice(0, this.fingerListPageSize);
        })
        .finally(() => {
          this.tableLoading = false;
        });
    },

    paginationOptions() {
      if (this.isPageOver || this.fingerList.length >= this.allFingerList.length) {
        return;
      }
      this.isPageOver = true;
      this.fingerListPage += 1;
      setTimeout(() => {
        const { fingerListPageSize: size, fingerListPage: page } = this;
        this.fingerList = this.fingerList.concat(this.allFingerList.slice((page - 1) * size, size * page));
        this.isPageOver = false;
      }, 1500);
    },
  },
};
</script>

<style lang="scss">
@import "@/scss/mixins/flex.scss";

.log-cluster-table-container {
  .cluster-nav {
    min-width: 760px;
    margin-bottom: 12px;
    color: #63656e;
    @include flex-justify(space-between);
  }
  .bk-alert {
    margin-bottom: 16px;
  }
}
.no-text-table {
  .bk-table-empty-block {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 480px);
  }
  .empty-text {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    .bk-icon {
      font-size: 65px;
    }
    .empty-leave {
      color: #3a84ff;
      margin-top: 8px;
      cursor: pointer;
    }
  }
}
</style>
