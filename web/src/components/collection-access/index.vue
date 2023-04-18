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
  <section :class="['access-wrapper',itsmTicketIsApplying && 'iframe-container']"
           v-bkloading="{ isLoading: basicLoading }">
    <auth-container-page v-if="authPageInfo" :info="authPageInfo"></auth-container-page>
    <div class="access-container" v-else-if="!basicLoading && !isCleaning">
      <section class="access-step-wrapper" v-en-style="'width: 258px'">
        <div class="fixed-steps" :style="{ height: (stepList.length * 76) + 'px' }">
          <bk-steps
            v-if="stepList.length"
            theme="primary"
            direction="vertical"
            :cur-step.sync="showSteps"
            :steps="stepList">
          </bk-steps>
          <div class="step-arrow" :style="{ top: (curStep * 76 - 38) + 'px' }"></div>
        </div>
      </section>
      <section v-bkloading="{ isLoading: containerLoading, zIndex: 10 }"
               class="access-step-container" v-if="operateType">
        <template v-if="isItsmAndNotStartOrStop">
          <step-add
            v-if="curStep === 1"
            :container-loading.sync="containerLoading"
            :operate-type="operateType"
            :is-physics.sync="isPhysics"
            :is-update.sync="isUpdate"
            @stepChange="(num) => stepChange(num, 'add')" />
          <step-issued
            v-if="curStep === 2"
            :operate-type="operateType"
            :is-switch="isSwitch"
            @stepChange="stepChange" />
          <step-field
            v-if="curStep === 3"
            :cur-step="curStep"
            :operate-type="operateType"
            @changeIndexSetId="updateIndexSetId"
            @stepChange="stepChange"
            @changeClean="isCleaning = true" />
          <step-storage
            v-if="curStep === 4"
            :cur-step="curStep"
            :operate-type="operateType"
            @changeIndexSetId="updateIndexSetId"
            @stepChange="stepChange"
            @setAssessmentItem="setAssessmentItem"
            @change-submit="changeSubmit" />
          <step-result
            v-if="isFinish"
            :operate-type="operateType"
            :is-switch="isSwitch"
            :index-set-id="indexSetId"
            :apply-data="applyData"
            @stepChange="stepChange" />
        </template>
        <template v-else>
          <step-add
            v-if="curStep === 1 && !isSwitch"
            :operate-type="operateType"
            :container-loading.sync="containerLoading"
            :is-physics.sync="isPhysics"
            :is-update.sync="isUpdate"
            @stepChange="(num) => stepChange(num, 'add')" />
          <step-issued
            v-if="(curStep === 2 && !isSwitch) || (curStep === 1 && isSwitch)"
            :operate-type="operateType"
            :is-switch="isSwitch"
            @stepChange="stepChange" />
          <step-field
            v-if="curStep === 3"
            :cur-step="curStep"
            :operate-type="operateType"
            @changeIndexSetId="updateIndexSetId"
            @stepChange="stepChange"
            @changeClean="isCleaning = true" />
          <step-storage
            v-if="curStep === 4"
            :cur-step="curStep"
            :operate-type="operateType"
            @changeIndexSetId="updateIndexSetId"
            @stepChange="stepChange"
            @setAssessmentItem="setAssessmentItem"
            @change-submit="changeSubmit" />
          <step-result
            v-if="isFinish"
            :operate-type="operateType"
            :is-switch="isSwitch"
            :index-set-id="indexSetId"
            :apply-data="applyData"
            @stepChange="stepChange" />
        </template>
      </section>
    </div>
    <advance-clean-land v-else-if="!basicLoading && isCleaning" back-router="collection-item" />
  </section>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import { stepsConf, finishRefer } from './step';
import AuthContainerPage from '@/components/common/auth-container-page';
import stepAdd from './step-add';
import stepIssued from './step-issued';
import stepField from './step-field';
import stepStorage from './step-storage.vue';
import stepResult from './step-result';
import advanceCleanLand from '@/components/collection-access/advance-clean-land';
import * as authorityMap from '../../common/authority-map';

export default {
  name: 'AccessSteps',
  components: {
    AuthContainerPage,
    stepAdd,
    stepIssued,
    stepField,
    stepStorage,
    stepResult,
    advanceCleanLand,
  },
  data() {
    return {
      authPageInfo: null,
      basicLoading: true,
      isCleaning: false,
      isSubmit: false,
      isUpdate: false, // 判断第一步是否是处于编辑状态
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      operateType: '',
      curStep: 1, // 组件步骤
      showSteps: 1, // 判断容器日志所用的展示步骤
      isPhysics: true, // 采集配置是否是物理环境
      indexSetId: '',
      stepList: [],
      globals: {},
      itsmTicketIsApplying: false,
      applyData: {},
      containerLoading: false, // 容器日志提交loading
    };
  },
  computed: {
    ...mapState({
      showRouterLeaveTip: state => state.showRouterLeaveTip,
    }),
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters(['bkBizId']),
    ...mapGetters(['spaceUid']),
    isCommon() {
      return ['add', 'edit'].some(item => item === this.operateType);
    },
    isCommonFinish() { // 存储操作完成的情况 table_id
      return ['add', 'edit'].some(item => this.operateType.search(item) !== -1);
    },
    isSwitch() {
      return ['start', 'stop'].some(item => item === this.operateType);
    },
    isItsmAndNotStartOrStop() {
      return this.isItsm && this.operateType !== 'start' && this.operateType !== 'stop';
    },
    isFinish() {
      if (this.isItsmAndNotStartOrStop) {
        return this.curStep === 5;
      }
      return finishRefer[this.operateType] === this.curStep;
    },
  },
  watch: {
    curStep() {
      this.setSteps();
    },
  },
  created() {
    this.initPage();
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit && !this.isSwitch && !this.showRouterLeaveTip) {
      this.$bkInfo({
        title: this.$t('是否放弃本次操作？'),
        confirmFn: () => {
          next();
        },
      });
      return;
    }
    next();
  },
  methods: {
    // 先校验页面权限再初始化
    async initPage() {
      try {
        const paramData = this.$route.name === 'collectAdd' ? {
          action_ids: [authorityMap.CREATE_COLLECTION_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        } : {
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: this.$route.params.collectorId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          this.basicLoading = false;
          return;
        }
      } catch (err) {
        console.warn(err);
        this.basicLoading = false;
        return;
      }

      const routeType = this.$route.name.toLowerCase().replace('collect', '');
      const { query: { type }, name: routeName } = this.$route;
      this.isUpdate = routeName !== 'collectAdd'; // 判断是否是更新
      if ((routeType !== 'add' && !this.$route.params.notAdd) || type === 'clone') { // 克隆时 请求初始数据
        try {
          const detailRes = await this.getDetail();
          this.operateType = routeType === 'edit' && detailRes.table_id ? 'editFinish' : routeType; // 若存在table_id则只有三步
        } catch (e) {
          console.warn(e);
          this.operateType = routeType;
        }
        try {
          const statusRes = await this.$http.request('collect/getCollectStatus', {
            query: {
              collector_id_list: this.$route.params.collectorId,
            },
          });
          if (statusRes.data[0].status === 'PREPARE') {
            // 准备中编辑时跳到第一步，所以不用修改步骤
          } else if (this.isItsm) {
            if (['edit', 'editFinish'].includes(this.operateType)) { // 未完成编辑
              this.curStep = this.applyData.itsm_ticket_status === 'applying' ? 5 : 1;
            } else if (this.operateType === 'field') {
              this.curStep = this.applyData.itsm_ticket_status === 'applying' ? 5 : 3;
            } else if (this.operateType === 'storage') {
              this.curStep = this.applyData.itsm_ticket_status === 'applying' ? 5 : 4;
            }
            // 审批通过后编辑直接进入第三步字段提取，否则进入第二步容量评估
          } else if (this.operateType === 'field') {
            this.curStep = 3;
          } else if (this.operateType === 'storage') {
            this.curStep = 4;
          }
          // 容器环境  非启用停用 非克隆状态则展示容器日志步骤
          if (!this.isPhysics && !this.isSwitch && type !== 'clone') {
            this.operateType = 'container';
          }
        } catch (e) {
          console.warn(e);
        }
      } else {
        this.operateType = routeType;
      }
      this.setSteps();
      this.basicLoading = false;
    },
    setSteps() {
      // 判断当前是否是物理环境 用于切换setp的数组
      if (this.isPhysics || this.isSwitch) {
        this.showSteps = this.curStep;
      } else {
        // 容器环境 非启用 停用情况 当前页若是采集配置则跳过采集下发直接进入字段提取步骤展示
        this.showSteps = this.curStep === 1  ?  1 : this.curStep - 1;
      }
      // 新增  并且为容器环境则步骤变为容器步骤 步骤为第一步时不判断
      if (this.operateType === 'add' && !this.isPhysics && this.curStep !== 1) {
        this.operateType = 'container';
      }
      const stepList = stepsConf[this.operateType];

      this.stepList = JSON.parse(JSON.stringify(stepList));

      this.stepList.forEach((step, index) => {
        if (index < this.showSteps - 1) {
          // step.icon = 'check-1'; // 组件bug。已完成的步骤无法为空icon。或者其它样式。需优化
        } else {
          step.icon = index + 1;
        }
      });
    },
    stepChange(num, type = null) {
      if (type === 'add' && !this.isPhysics && !num) {
        this.curStep = this.curStep + 2;
        return;
      }
      this.curStep = num || this.curStep + 1;
    },
    updateIndexSetId(indexId) {
      this.indexSetId = indexId;
    },

    // 获取详情
    getDetail() {
      return new Promise((resolve, reject) => {
        this.$http.request('collect/details', {
          // mock: true,
          // manualSchema: true,
          params: {
            collector_config_id: this.$route.params.collectorId,
          },
        }).then(async (res) => {
          if (res.data) {
            const collect = res.data;
            this.isPhysics = collect.environment !== 'container';
            if (collect.collector_scenario_id !== 'wineventlog' && this.isPhysics) {
              collect.params.paths = collect.params.paths.map(item => ({ value: item }));
            }
            // 如果当前页面采集流程未完成 则展示流程服务页面
            const applyDataItem = {
              iframe_ticket_url: collect.ticket_url,
              itsm_ticket_status: collect.itsm_ticket_status,
            };
            this.applyData = collect.itsm_ticket_status === 'applying' ? applyDataItem : {};
            this.itsmTicketIsApplying = false;
            this.$store.commit('collect/setCurCollect', collect);
            resolve(res.data);
          }
        })
          .catch((err) => {
            reject(err);
          });
      });
    },
    // 获取状态
    getCollectStatus(idStr) {
      return this.$http.request('collect/getCollectStatus', {
        query: {
          collector_id_list: idStr,
        },
      });
    },
    changeSubmit(isSubmit) {
      this.isSubmit = isSubmit;
    },
    setAssessmentItem(item) {
      this.applyData = item;
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';

  .access-wrapper {
    padding: 20px 24px;
  }

  .iframe-container {
    padding: 0;
  }

  .access-container {
    position: relative;
    display: flex;
    width: 100%;
    height: 100%;
    border: 1px solid $borderWeightColor;
    overflow: hidden;
  }

  .access-step-wrapper {
    padding-left: 30px;
    width: 200px;
    border-right: 1px solid $borderWeightColor;
    background: $bgHoverColor;

    .fixed-steps {
      position: relative;
      max-height: 100%;
      margin-top: 40px;

      .bk-steps {
        :last-child {
          &::after {
            display: none;
          }
        }
      }

      .bk-step {
        color: #7a7c85;
        height: 70px;
        display: flex;
        white-space: normal;

        &::after {
          width: 1px;
          left: 14px;
          background: none;
          border-left: 1px dashed #e5e6ec;
        }

        .bk-step-number {
          display: inline-block;
          width: 28px;
          height: 28px;
          line-height: 28px;
          font-size: 12px;
          color: #858790;
          text-align: center;
          border-radius: 50%;
          border: 1px solid #c4c6cc;
          margin-right: 10px;
          box-shadow: 0px 2px 4px 0px rgba(0, 130, 255, .15);
        }

        .bk-step-content {
          width: 78%;
          overflow: hidden;
          display: inline-block;
          hyphens: auto;
        }

        .bk-step-title {
          display: inline;
          color: #6e7079;
        }

        .bk-step-indicator {
          width: 28px;
          height: 28px;
          line-height: 26px;
        }
      }

      .current {
        .bk-step-number {
          color: #fff;
          background: #3a84ff;
          border: 1px solid #3a84ff;
          box-shadow: 0px 2px 4px 0px rgba(0, 130, 255, .15);
        }

        .bk-step-title {
          color: #448fff;
        }
      }

      .done {
        .bk-step-icon {
          color: #fff;
          border: 1px solid #dcdee5;
        }

        .bk-step-number {
          color: #fafbfd;
          box-shadow: 0px 2px 4px 0px rgba(0, 130, 255, .15);
          position: relative;
          background: #fafbfd;

          &::before {
            content: '';
            width: 16px;
            height: 16px;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            transform: translate(-50%, -50%);
            transform: translate(-50%, -50%);
            background-color: #fafbfd;
            border-radius: 50%;
            background-image: url('../../images/icons/finish.svg');
            background-size: 100% 100%;
          }
        }

        // .bk-step-indicator {
        //   background-color: #dcdee5;
        // }

        .bk-step-title {
          color: #63656e;
        }
      }
    }

    .step-arrow {
      position: absolute;
      width: 10px;
      height: 10px;
      border-top: 1px solid $borderWeightColor;
      border-right: 1px solid $borderWeightColor;
      border-left: 1px solid transparent;
      border-left: 1px solid transparent;
      right: 1px;
      background: #fff;
      transform-origin: 62% 0;
      transform: rotate(-135deg);
    }
  }

  .access-step-container {
    flex: 1;
    width: calc(100% - 200px);
    background: #fff;
  }
</style>
