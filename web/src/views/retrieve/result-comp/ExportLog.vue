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
    <div
      :class="{ 'operation-icon': true, 'disabled-icon': !queueStatus }"
      @click="exportLog"
      data-test-id="fieldForm_div_exportData"
      v-bk-tooltips="queueStatus ? $t('btn.export') : undefined">
      <span class="icon log-icon icon-xiazai"></span>
    </div>

    <!-- 导出弹窗提示 -->
    <bk-dialog
      v-model="showAsyncExport"
      theme="primary"
      ext-cls="async-export-dialog"
      :mask-close="false"
      :show-footer="false">
      <div class="export-container" v-bkloading="{ isLoading: exportLoading }">
        <span class="bk-icon bk-dialog-warning icon-exclamation"></span>
        <div class="header">
          {{ totalCount > 2000000 ? $t('retrieve.dataMoreThanMillion') : $t('retrieve.dataMoreThan') }}
        </div>
        <div class="export-type immediate-export">
          <span class="bk-icon icon-info-circle"></span>
          <span class="export-text">{{ $t('retrieve.immediateExportDesc') }}</span>
          <bk-button theme="primary" @click="openDownloadUrl">{{ $t('retrieve.immediateExport') }}</bk-button>
        </div>
        <div class="export-type async-export">
          <span class="bk-icon icon-info-circle"></span>
          <span v-if="totalCount > 2000000" class="export-text">{{ $t('retrieve.asyncExportMoreDesc') }}</span>
          <span v-else class="export-text">{{ $t('retrieve.asyncExportDesc') }}</span>
          <bk-button @click="downloadAsync">{{ $t('retrieve.asyncExport') }}</bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    totalCount: {
      type: Number,
      default: 0,
    },
    queueStatus: {
      type: Boolean,
      default: true,
    },
    asyncExportUsable: {
      type: Boolean,
      default: true,
    },
    asyncExportUsableReason: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      showAsyncExport: false,
      exportLoading: false,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
  },
  methods: {
    exportLog() {
      if (!this.queueStatus) return;

      // 导出数据为空
      if (!this.totalCount) {
        const infoDialog = this.$bkInfo({
          type: 'error',
          title: this.$t('retrieve.exportFailed'),
          subTitle: this.$t('retrieve.dataNone'),
          showFooter: false,
        });
        setTimeout(() => infoDialog.close(), 3000);
      } else if (this.totalCount > 10000) {
        // 导出数量大于1w且小于100w 可直接下载1w 或 异步全量下载全部
        // 通过 field 判断是否支持异步下载
        if (this.asyncExportUsable) {
          this.showAsyncExport = true;
        } else {
          const h = this.$createElement;
          this.$bkInfo({
            type: 'warning',
            title: this.$t('retrieve.dataMoreThan'),
            subHeader: h('p', {
              style: {
                whiteSpace: 'normal',
                padding: '0 20px',
                wordBreak: 'break-all',
              },
            }, `${this.$t('retrieve.reasonFor')}${this.asyncExportUsableReason}${this.$t('retrieve.reasonDesc')}`),
            okText: this.$t('retrieve.immediateExport'),
            confirmFn: () => this.openDownloadUrl(),
          });
        }
      } else {
        this.openDownloadUrl();
      }
    },
    openDownloadUrl() {
      const params = Object.assign(this.retrieveParams, { begin: 0, bk_biz_id: this.bkBizId });
      const exportParams = encodeURIComponent(JSON.stringify({
        ...params,
        size: this.totalCount,
      }));
      // eslint-disable-next-line max-len
      const targetUrl = `${window.SITE_URL}api/v1/search/index_set/${this.$route.params.indexId}/export/?export_dict=${exportParams}`;
      window.open(targetUrl);
    },
    downloadAsync() {
      const params = Object.assign(this.retrieveParams, { begin: 0, bk_biz_id: this.bkBizId });
      const data = { ...params };
      data.size = this.totalCount;
      data.time_range = 'customized';

      this.exportLoading = true;
      this.$http.request('retrieve/exportAsync', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data,
      }).then((res) => {
        if (res.result) {
          this.$bkMessage({
            theme: 'success',
            message: res.data.prompt,
          });
        }
      })
        .finally(() => {
          this.showAsyncExport = false;
          this.exportLoading = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.operation-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  margin-left: 10px;
  cursor: pointer;
  border: 1px solid #c4c6cc;
  transition: boder-color .2s;
  border-radius: 2px;
  outline: none;
  &:hover {
    border-color: #979ba5;
    transition: boder-color .2s;
  }
  &:active {
    border-color: #3a84ff;
    transition: boder-color .2s;
  }
  .log-icon {
    width: 16px;
    font-size: 16px;
    color: #979ba5;
  }
}
.disabled-icon {
  background-color: #fff;
  border-color: #dcdee5;
  cursor: not-allowed;
  &:hover,
  .log-icon {
    border-color: #dcdee5;
    color: #c4c6cc;
  }
}

.async-export-dialog {
  .header {
    padding: 18px 0px 32px !important;
  }
  .export-container {
    text-align: center;
  }
  .bk-dialog-warning {
    display: block;
    margin: 0 auto;
    width: 58px;
    height: 58px;
    line-height: 58px;
    font-size: 30px;
    color: #fff;
    border-radius: 50%;
    background-color: #ffb848;
  }
  .header {
    padding: 18px 24px 32px;
    display: inline-block;
    width: 100%;
    font-size: 24px;
    color: #313238;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.5;
    margin: 0;
  }
  .export-type {
    margin-bottom: 24px;
    padding: 0 22px;
    display: flex;
    align-items: center;
    .export-text {
      margin-left: 8px;
      max-width: 184px;
      text-align: left;
      font-size: 14px;
      color: #313238;
      line-height: 18px;
    }
    .bk-button {
      margin-left: auto;
    }
  }
}
</style>
