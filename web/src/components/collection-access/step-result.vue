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
  <div class="step-result-wrapper" v-if="isNotApplyPage">
    <div class="step-result-container" data-test-id="finish_div_finishBox">
      <i class="bk-icon icon-check-circle"></i>
      <h3 class="title">{{ finishText }}</h3>
      <!-- <p v-if="host.count"> -->
      <!-- <p class="info">
        {{ '共' }}<span class="host-number text-primary">{{ host.count || 0 }}</span>{{ '台主机' }}
        <template>{{ '，成功' }}
          <span class="host-number text-success">{{ host.success || 0 }}</span>{{ '台主机' }}
        </template>
        <template>{{ '，失败' }}
          <span class="host-number text-failed">{{ host.failed || 0 }}</span>{{ '台主机' }}
        </template>
      </p> -->
      <div class="result-button-group">
        <bk-button
          @click="routeChange('complete')"
          data-test-id="finishBox_button_backToList"
        >{{ $t('返回列表') }}</bk-button>
        <bk-button
          theme="primary" @click="routeChange('search')"
          data-test-id="finishBox_button_goToSearch"
        >{{ $t('探索') }}</bk-button>
      </div>
    </div>
  </div>
  <div
    v-else
    class="approval-detail-container">
    <bk-exception v-if="applyData" type="building">
      <div class="approval-text">
        <span>{{ $t('容量评估进行中') }}</span>
        <a :href="applyData.iframe_ticket_url"
           class="button-text"
           target="_blank"
           data-test-id="capacityContaineBox_a_viewApprovalDetails">
          {{ $t('点击查看审批详情') }}
          <span class="log-icon icon-lianjie"></span>
        </a>
      </div>
    </bk-exception>
  </div>
</template>

<script>
export default {
  name: 'StepResult',
  props: {
    operateType: String,
    isSwitch: Boolean,
    indexSetId: {
      type: [String, Number],
      default: '',
    },
    type: {
      type: String,
      default: 'create',
    },
    host: {
      type: Object,
      default() {
        return {};
      },
    },
    applyData: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      finish: {
        add: this.$t('采集项创建完成'),
        edit: this.$t('采集项修改完成'),
        editFinish: this.$t('采集项修改完成'),
        field: this.$t('采集项修改完成'),
        start: this.$t('采集项启用完成'),
        stop: this.$t('采集项停用完成'),
        storage: this.$t('采集项修改完成'),
        container: this.$t('采集项修改完成'),
      },
    };
  },
  computed: {
    // title () {
    //     const titleText = {
    //         add: '采集配置创建完成',
    //         edit: '采集配置修改完成',
    //         start: '启用采集配置任务完成',
    //         stop: '停用采集配置任务完成'
    //     }
    //     return titleText[this.operateType]
    // }
    finishText() {
      return this.finish[this.operateType];
    },
    isNotApplyPage() {
      return this.applyData.itsm_ticket_status !== 'applying';
    },
  },
  methods: {
    routeChange(type) {
      let routeName = 'collection-item';
      if (type === 'search' || type === 'clear') {
        routeName = 'retrieve';
      }
      this.$router.replace({
        name: routeName,
        params: {
          indexId: type === 'search' && this.indexSetId ? this.indexSetId : '',
        },
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/conf';

  .step-result-wrapper {
    position: relative;
    padding-top: 105px;

    .step-result-container {
      width: 500px;
      margin: 0 auto;
      text-align: center;

      .icon-check-circle {
        font-size: 56px;
        color: $successColor;
      }

      .title {
        margin: 21px 0 0 0;
        padding: 0;
        font-size: 16px;
        color: #000;
      }

      .info {
        margin-top: 10px;
        font-size: 12px;
        color: #6e7079;
      }

      .host-number {
        margin: 0 3px;
      }

      .text-primary {
        color: $primaryColor;
      }

      .text-success {
        color: $successColor;
      }

      .text-failed {
        color: $failColor;
      }
    }

    .result-button-group {
      margin-top: 36px;
      font-size: 0;

      .bk-button + .bk-button {
        margin-left: 10px;
      }
    }
  }

  .approval-detail-container {
    height: 100%;
    padding-top: 100px;
    font-size: 14px;

    .approval-text {
      display: flex;
      flex-flow: column;
      font-size: 16px;

      .button-text {
        margin-top: 16px;
      }
    }
  }
</style>
