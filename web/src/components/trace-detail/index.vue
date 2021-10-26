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
  <bk-sideslider
    transfer
    ext-cls="trace-detail-sideslider"
    :is-show.sync="isShowSlider"
    :quick-close="true"
    :width="sideWidth"
    @hidden="handleHidden">
    <div slot="header">
      <div class="trace-detail-header">
        <span>{{ $t('详情') }}</span>
        <i
          :class="`bk-icon icon-${isFullScreen ? 'un-full-screen' : 'full-screen'}`"
          @click="handleFullScreen">
        </i>
      </div>
    </div>
    <div slot="content" ref="traceDetailContainer">
      <div
        :class="['trace-detail-container', { 'is-full-screen': isFullScreen }]"
        v-bkloading="{ isLoading }">
        <iframe :src="src" class="trace-iframe" @load="handleIframeLoad"></iframe>
      </div>
    </div>
  </bk-sideslider>
</template>

<script>
export default {
  props: {
    isShow: {
      type: Boolean,
      default: false,
    },
    traceId: {
      type: String,
      default: '',
    },
    indexSetName: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isShowSlider: false,
      isLoading: false,
      isFullScreen: false,
      src: '',
    };
  },
  computed: {
    bkBizId() {
      return this.$store.state.bkBizId;
    },
    sideWidth() {
      const minWidth = 1000;
      const viewWidth = document.body.clientWidth;
      const width = (viewWidth / 2) < minWidth ? minWidth : (viewWidth / 2);
      return width;
    },
  },
  watch: {
    isShow(val) {
      this.isShowSlider = val;
      if (val) {
        this.isLoading = true;
        this.updateIframeSrc();
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
      } else {
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
      }
    },
  },
  methods: {
    // 初始化 iframe 页面
    updateIframeSrc() {
      let siteUrl = window.SITE_URL;
      if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
      if (!siteUrl.endsWith('/')) siteUrl += '/';
      const queryParams = JSON.stringify(['now-1h', 'now', this.indexSetName, { query: this.traceId }]);
      const prefixUrl = window.origin + siteUrl;
      this.src = `${prefixUrl}grafana/explore?orgName=${this.bkBizId}&left=${queryParams}`;
    },
    // iframe 页面加载完毕
    handleIframeLoad() {
      setTimeout(() => this.isLoading = false, 500);
    },
    // 设置全屏
    handleFullScreen() {
      if (!document.fullscreenElement) {
        this.$refs.traceDetailContainer.requestFullscreen();
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    },
    handleFullscreenChange() {
      if (document.fullscreenElement) {
        this.isFullScreen = true;
      } else {
        this.isFullScreen = false;
      }
    },
    handleHidden() {
      this.$emit('update:isShow', false);
    },
  },
};
</script>

<style lang="scss">
  .trace-detail-sideslider {
    .trace-detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-right: 20px;
      .bk-icon {
        cursor: pointer;
      }
    }
    .trace-detail-container {
      width: 100%;
      height: calc(100vh - 60px);
      &.is-full-screen {
        height: 100vh;
      }
      .trace-iframe {
        border: none;
        width: 100%;
        height: 100%;
      }
    }
  }
</style>

