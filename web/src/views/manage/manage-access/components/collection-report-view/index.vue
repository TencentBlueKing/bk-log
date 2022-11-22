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
    <div slot="content">123</div>
  </bk-sideslider>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isShow: false,
    };
  },
  watch: {
    value(val) {
      if (val) {
        this.isShow = true;
        this.handleCollectorCheck();
      } else {
        this.isShow = false;
      }
    },
  },
  methods: {
    async handleCollectorCheck() {
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
    }
  }
}
</style>
