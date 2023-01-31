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
          :total-fields="totalFields"
          :finger-operate-data="fingerOperateData"
          :request-data="requestData"
          @handleFingerOperate="handleFingerOperate" />
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
          :width-list="smallLoaderWidthList" />
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
            ref="fingerTableRef"
            :cluster-switch="clusterSwitch"
            :request-data="requestData"
            :config-data="configData"
            :finger-list="fingerList"
            :is-page-over="isPageOver"
            :all-finger-list="allFingerList"
            :loader-width-list="smallLoaderWidthList"
            @paginationOptions="paginationOptions"
            @updateRequest="updateRequest"
            @handleScrollIsShow="handleScrollIsShow" />
        </div>
      </div>

      <bk-table
        v-else
        class="no-text-table"
        :data="[]">
        <div slot="empty">
          <div class="empty-text">
            <span class="bk-table-empty-icon bk-icon icon-empty"></span>
            <p v-if="!isHaveAnalyzed">
              {{$t('canNotFieldMessage1')}}
              <span class="empty-leave" @click="handleLeaveCurrent">{{$t('计算平台')}}</span>
              {{$t('canNotFieldMessage2')}}
            </p>
            <div v-else>
              <p>{{exhibitText}}</p>
              <span class="empty-leave" @click="handleLeaveCurrent">
                {{exhibitOperate}}
              </span>
            </div>
          </div>
        </div>
      </bk-table>

      <div class="fixed-scroll-top-btn" v-show="showScrollTop" @click="scrollToTop">
        <i class="bk-icon icon-angle-up"></i>
      </div>
    </div>
    <clustering-loader
      is-loading
      v-else
      :width-list="loadingWidthList.global" />
  </div>
</template>

<script>
import DataFingerprint from './data-fingerprint';
import IgnoreTable from './ignore-table';
import ClusteringLoader from '@/skeleton/clustering-loader';
import fingerOperate from './components/finger-operate';
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
    indexSetItem: {
      type: Object,
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
      isClickFingerNav: false, // 是否点击过数据指纹nav
      globalLoading: false, // 日志聚类大loading
      tableLoading: false, // 详情loading
      isShowCustomize: true, // 是否显示自定义
      indexId: -1,
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
        patternSize: 0, // slider当前值
        sliderMaxVal: 0, // pattern最大值
        comparedList: [], // 同比List
        patternList: [], // pattern敏感度List
        isShowCustomize: true, // 是否显示自定义
        signatureSwitch: false, // 数据指纹开关
        groupList: [], // 缓存分组列表
        alarmObj: {}, // 是否需要告警对象
      },
      requestData: { // 数据请求
        pattern_level: '',
        year_on_year_hour: 0,
        show_new_pattern: false,
        group_by: [],
        size: 10000,
      },
      isPageOver: false,
      fingerPage: 1,
      fingerPageSize: 50,
      loadingWidthList: { // loading表头宽度列表
        global: [''],
        ignore: [60, 90, 90, ''],
        notCompared: [150, 90, 90, ''],
        compared: [150, 90, 90, 100, 100, ''],
      },
      fingerList: [],
      allFingerList: [], // 所有数据指纹List
      showScrollTop: false, // 是否展示返回顶部icon
      throttle: false, // 请求防抖
      isHaveText: false, // 是否含有text字段
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
      return this.configID ? this.$t('goCleanMessage') : this.$t('noConfigIDMessage');
    },
    exhibitOperate() {
      return this.configID ? this.$t('跳转到日志清洗') : '';
    },
    clusteringField() {
      // 如果有聚类字段则使用设置的
      if (this.configData?.extra?.clustering_field) return this.configData.extra.clustering_field;
      // 如果有log字段则使用log类型字段
      const logFieldItem = this.totalFields.find(item => item.field_name === 'log');
      if (logFieldItem) return logFieldItem.field_name;
      // 如果没有设置聚类字段和log字段则使用text列表里的第一项值
      const textTypeFieldList = this.totalFields.filter(item => item.is_analyzed) || [];
      if (textTypeFieldList.length) return textTypeFieldList[0].field_name;
      return  '';
    },
    bkBizId() {
      return this.$store.state.bkBizId;
    },
    isHaveAnalyzed() {
      return this.totalFields.some(item => item.is_analyzed);
    },
  },
  watch: {
    configData: {
      deep: true,
      immediate: true,
      handler(val) {
        this.globalLoading = true;
        // 日志聚类开关赋值
        this.clusterSwitch = val.is_active;
        // 数据指纹开关赋值
        this.fingerOperateData.signatureSwitch = val.extra.signature_switch;
        this.configID = this.cleanConfig.extra?.collector_config_id;
        this.isClickFingerNav = false;
        // 当前nav为数据指纹且数据指纹开启点击指纹nav则不再重复请求
        if (this.active === 'dataFingerprint' && val.extra.signature_switch) {
          this.isClickFingerNav = true;
        } else {
          this.fingerList = [];
          this.allFingerList = [];
        }
        // 判断是否可以字段提取的全局loading
        setTimeout(() => {
          this.globalLoading = false;
        }, 700);
      },
    },
    totalFields: {
      deep: true,
      immediate: true,
      handler(newList) {
        if (newList.length) {
          /**
           *  无字段提取或者聚类开关没开时直接不显示聚类nav和table
           *  来源如果是数据平台并且日志聚类大开关有打开则进入text判断
           *  有text则提示去开启日志聚类 无则显示跳转计算平台
           */
          // 初始化分组下拉列表
          this.filterGroupList();
          this.initTable();
          // 判断是否有text字段 无则提示当前不支持采集项清洗
          this.exhibitAll = newList.some(el => el.field_type === 'text');
        }
      },
    },
    originTableList: {
      deep: true,
      handler(newList) {
        if (newList.length) {
          // 过滤条件变化及当前活跃为数据指纹并且数据指纹打开时才发送请求
          if (this.indexId === this.$route.params.indexId
          && this.fingerOperateData.signatureSwitch) {
            this.requestFinger();
          } else {
            this.indexId = this.$route.params.indexId;
          }
        }
      },
    },
    requestData: {
      deep: true,
      handler() {
        if (this.fingerOperateData.signatureSwitch) {
          this.requestFinger();
        }
      },
    },
  },
  methods: {
    handleClickNav(id) {
      this.active = id;
      if (!this.isClickFingerNav) {
        if (this.configData.extra.signature_switch
         && id === 'dataFingerprint') {
          this.isClickFingerNav = true;
          this.requestFinger();
        }
      }
    },
    initTable() {
      const {
        log_clustering_level_year_on_year: yearOnYearList,
        log_clustering_level: clusterLevel,
      } = this.globalsData;
      let patternLevel;
      if (clusterLevel && clusterLevel.length > 0) {
        // 判断奇偶数来取pattern中间值
        if (clusterLevel.length % 2 === 1) {
          patternLevel = (clusterLevel.length + 1) / 2;
        } else {
          patternLevel = clusterLevel.length  / 2;
        }
      }
      Object.assign(this.fingerOperateData, {
        patternSize: patternLevel - 1,
        sliderMaxVal: clusterLevel.length - 1,
        patternList: clusterLevel,
        comparedList: yearOnYearList,
      });
      Object.assign(this.requestData, {
        pattern_level: clusterLevel[patternLevel - 1],
      });
      this.$nextTick(() => {
        this.scrollEl = document.querySelector('.result-scroll-container');
      });
    },
    /**
     * @desc: 数据指纹操作
     * @param { String } operateType 操作类型
     * @param { Any } val 具体值
     */
    handleFingerOperate(operateType, val) {
      switch (operateType) {
        case 'compared': // 同比操作
          this.requestData.year_on_year_hour = val;
          break;
        case 'patternSize': // patter大小
          this.requestData.pattern_level = val;
          break;
        case 'isShowNear': // 是否展示近24小时
          this.requestData.show_new_pattern = val;
          break;
        case 'enterCustomize': // 自定义同比时常
          this.handleEnterCompared(val);
          break;
        case 'customize': // 是否展示自定义
          this.fingerOperateData.isShowCustomize = val;
          break;
        case 'group': // 分组操作
          this.requestData.group_by = val;
          break;
        case 'getNewStrategy': // 获取新类告警状态
          this.fingerOperateData.alarmObj = val;
          break;
        case 'editAlarm': { // 更新新类告警请求
          const { alarmObj: { strategy_id: strategyID } } = this.fingerOperateData;
          if (strategyID) {
            this.$refs.fingerTableRef.policyEditing(strategyID);
          }
        }
          break;
      }
    },
    handleLeaveCurrent() {
      // 不显示字段提取时跳转计算平台
      if (this.indexSetItem.scenario_id !== 'log' && !this.isHaveText) {
        const jumpUrl = `${window.BKDATA_URL}`;
        window.open(jumpUrl, '_blank');
        return;
      }
      // 无清洗 去清洗
      if (this.configID && this.configID > 0) {
        this.$router.push({
          name: 'clean-edit',
          params: { collectorId: this.configID },
          query: {
            spaceUid: this.$store.state.spaceUid,
            backRoute: this.$route.name,
          },
        });
      }
    },
    /**
     * @desc: 同比自定义输入
     * @param { String } val
     */
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
      const isRepeat = this.fingerOperateData.comparedList.some(el => el.id === Number(matchVal[1]));
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
    /**
     * @desc: 数据指纹请求
     */
    requestFinger() {
      if (this.throttle) return;

      this.throttle = true;
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
        .then(async (res) => {
          this.fingerPage = 1;
          this.fingerList = [];
          this.allFingerList = res.data;
          const sliceFingerList = res.data.slice(0, this.fingerPageSize);
          const labelsList = await this.getFingerLabelsList(sliceFingerList);
          this.fingerList.push(...labelsList);
          this.showScrollTop = false;
        })
        .finally(() => {
          this.tableLoading = false;
        });

      setTimeout(() => {
        this.throttle = false;
      }, 500);
    },
    /**
     * @desc: 数据指纹分页操作
     */
    async paginationOptions() {
      if (this.isPageOver || this.fingerList.length >= this.allFingerList.length) {
        return;
      }
      this.isPageOver = true;
      this.fingerPage += 1;
      const { fingerPage: page, fingerPageSize: pageSize } = this;
      const sliceFingerList = this.allFingerList.slice(pageSize * (page - 1), pageSize * page);
      const labelsList = await this.getFingerLabelsList(sliceFingerList);
      setTimeout(() => {
        this.fingerList.push(...labelsList);
        this.isPageOver = false;
      }, 300);
    },
    /**
     * @desc: 获取标签列表
     * @param { Array } fingerList
     * @returns { Array } 请求成功时添加labels后的数组
     */
    async getFingerLabelsList(fingerList = []) {
      const setList = new Set();
      fingerList.forEach((el) => {
        if (el.monitor?.strategy_id) {
          setList.add(el.monitor.strategy_id);
        }
      });
      // 获取过滤后的策略ID
      const strategyIDs = [...setList];
      // 有策略ID时请求标签接口 无策略ID时则直接返回
      if (strategyIDs.length) {
        try {
          const res = await this.$http.request('/logClustering/getFingerLabels', {
            params: {
              index_set_id: this.$route.params.indexId,
            },
            data: {
              strategy_ids: strategyIDs,
              bk_biz_id: this.bkBizId,
            },
          });
          // 生成标签对象 key为策略ID 值为标签数组
          const strategyObj = res.data.reduce((pre, cur) => {
            pre[cur.strategy_id] = cur.labels;
            return pre;
          }, {});
          // 数据指纹列表添加labels属性
          const labelsList = fingerList.map((el) => {
            el.labels = strategyObj[el.monitor.strategy_id];
            return el;
          });
          return labelsList;
        } catch (error) {
          return fingerList;
        }
      } else {
        return fingerList;
      }
    },
    /**
     * @desc: 初始化分组select数组
     */
    filterGroupList() {
      const filterList = this.totalFields
        .filter(el => el.es_doc_values && !/^__dist/.test(el.field_name)) // 过滤__dist字段
        .map((item) => {
          const { field_name: id, field_alias: alias } = item;
          return { id, name: alias ? `${id}(${alias})` : id };
        });
      this.fingerOperateData.groupList = filterList;
      this.requestData.group_by = [];
    },
    scrollToTop() {
      this.$easeScroll(0, 300, this.scrollEl);
    },
    handleScrollIsShow() {
      this.showScrollTop = this.scrollEl.scrollTop > 550;
    },
    updateRequest() {
      this.requestFinger();
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/flex.scss';

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

.fixed-scroll-top-btn {
  position: fixed;
  bottom: 24px;
  right: 14px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .2);
  border: 1px solid #dde4eb;
  border-radius: 4px;
  color: #63656e;
  background: #f0f1f5;
  cursor: pointer;
  z-index: 2100;
  transition: all .2s;

  &:hover {
    color: #fff;
    background: #979ba5;
    transition: all .2s;
  }

  .bk-icon {
    font-size: 20px;
    font-weight: bold;
  }
}
</style>
