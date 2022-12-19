<template>
  <!-- 一键检测弹窗 -->
  <bk-sideslider
    transfer
    :width="800"
    :quick-close="true"
    :ext-cls="'collection-report-detail'"
    :is-show.sync="isShow"
    @animation-end="closeReportSlider"
  >
    <div slot="header">{{ $t('一键检测') }}</div>
    <div slot="content">
      <div class="check-info">{{ checkInfo }}</div>
    </div>
  </bk-sideslider>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    // 检测任务id
    checkRecordId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isShow: false,
      checkInfo: '',
    };
  },
  watch: {
    value(val) {
      if (val) {
        this.isShow = true;
        this.handleCollectorCheck();
      } else {
        this.isShow = false;
        this.checkInfo = '';
      }
    },
  },
  methods: {
    /** 获取检测信息 */
    async handleCollectorCheck() {
      const res = await this.$http.request('collect/getCheckInfos', {
        data: {
          check_record_id: this.checkRecordId,
        },
      });
      if (res.data) {
        this.checkInfo = res.data.infos || '';

        if (!res.data.finished && this.isShow) { // 未完成检测 且 弹窗未关闭则继续请求
          setTimeout(() => {
            this.handleCollectorCheck();
          }, 1000);
        }
      }
    },
    closeReportSlider() {
      this.$emit('closeReport');
    },
  },
};
</script>

<style lang="scss">
.collection-report-detail {
  .detail-content {
    min-height: calc(100vh - 60px);
    white-space: pre-wrap;
  }

  .bk-sideslider-wrapper {
    padding-bottom: 0;

    .bk-sideslider-content {
      height: 100%;
      background-color: #313238;
      color: #c4c6cc;

      .check-info {
        padding: 20px;
        white-space: pre-wrap;
      }
    }
  }
}
</style>
