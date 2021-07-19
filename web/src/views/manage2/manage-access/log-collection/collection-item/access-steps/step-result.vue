<template>
  <div class="step-result-wrapper">
    <div class="step-result-container">
      <i class="bk-icon icon-check-circle"></i>
      <h3 class="title">{{ finishText }}</h3>
      <!-- <p v-if="host.count"> -->
      <!-- <p class="info">
                {{ '共' }}<span class="host-number text-primary">{{ host.count || 0 }}</span>{{ '台主机' }}
                <template>{{ '，成功' }}
                  <span class="host-number text-success">{{ host.success || 0 }}</span>{{ '台主机' }}</template>
                <template>{{ '，失败' }}
                  <span class="host-number text-failed">{{ host.failed || 0 }}</span>{{ '台主机' }}</template>
            </p> -->
      <div class="result-button-group">
        <bk-button @click="routeChange('complete')">{{ $t('dataManage.Return_list') }}</bk-button>
        <bk-button theme="primary" @click="routeChange('search')">{{ $t('dataManage.To_retrieve') }}</bk-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'step-result',
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
  },
  data() {
    return {
      finish: {
        add: this.$t('dataManage.add'),
        edit: this.$t('dataManage.edit'),
        editFinish: this.$t('dataManage.editFinish'),
        field: this.$t('dataManage.field'),
        start: this.$t('dataManage.start'),
        stop: this.$t('dataManage.stop'),
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
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
  },
};
</script>

<style lang="scss">
  @import '../../../../../../scss/conf';

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
</style>
