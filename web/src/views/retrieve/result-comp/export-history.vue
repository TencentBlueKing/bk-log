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
  <bk-dialog
    v-model="isShowDialog"
    theme="primary"
    width="1600"
    render-directive="if"
    :position="position"
    :show-footer="false"
    :mask-close="false"
    :draggable="false"
    :scrollable="true"
    @cancel="closeDialog">
    <div class="table-title">
      {{$t('exportHistory.downloadHistory')}}
    </div>
    <div class="search-history">
      <bk-button theme="primary" @click="handleSearchAll"> {{$t('exportHistory.btnTip')}}</bk-button>
    </div>
    <div class="table-container" v-bkloading="{ isLoading: tableLoading }">
      <bk-table
        class="export-table"
        :data="exportList"
        :pagination="pagination"
        :outer-border="false"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <!-- ID -->
        <bk-table-column
          label="ID"
          prop="id"
          width="80"></bk-table-column>
        <!-- index_set_id -->
        <template v-if="isShowSetLabel">
          <bk-table-column
            :label="$t('exportHistory.indexSetID')"
            width="100">
            <template slot-scope="{ row }">
              <span>
                {{row.log_index_set_id}}
              </span>
            </template>
          </bk-table-column>
        </template>
        <!-- 检测请求参数 -->
        <bk-table-column
          :label="$t('exportHistory.parameter')"
          width="180">
          <template slot-scope="{ row }">
            <bk-popover placement="top" theme="light">
              <div slot="content">
                <span
                  class="bk-icon icon-text-file"
                  :title="$t('复制')"
                  @click="handleCopyMsg(row.search_dict)"></span>
                <!-- eslint-disable-next-line vue/no-v-html -->
                <div v-html="getSearchDictHtml(row.search_dict)"></div>
              </div>
              <div class="parameter-search">
                <span>{{getSearchDictStr(row.search_dict)}}</span>
              </div>
            </bk-popover>
          </template>
        </bk-table-column>
        <!-- 下载类型 -->
        <bk-table-column
          :label="$t('exportHistory.downloadType')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <span>{{row.export_type === 'async' ? $t('exportHistory.async') : $t('exportHistory.sync')}}</span>
          </template>
        </bk-table-column>
        <!-- 导出状态 -->
        <bk-table-column
          :label="$t('exportHistory.exportState')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <bk-popover placement="top" theme="light">
              <div slot="content">
                <span>{{$t('exportHistory.completeTime')}}:{{getFormatDate(row.export_completed_at)}}</span>
                <span v-if="row.error_msg">，{{$t('exportHistory.abnormalReason')}}:{{row.error_msg}}</span>
              </div>
              <span style="cursor: pointer;">{{getStatusStr(row.export_status)}}</span>
            </bk-popover>
          </template>
        </bk-table-column>
        <!-- 文件名 -->
        <bk-table-column
          :label="$t('exportHistory.fileName')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <bk-popover v-if="row.export_pkg_name" placement="top" theme="light">
              <div slot="content">
                <span>{{row.export_pkg_name ? row.export_pkg_name : '--'}}</span>
              </div>
              <div class="file-name">
                <span>{{row.export_pkg_name ? row.export_pkg_name : '--'}}</span>
              </div>
            </bk-popover>
            <span v-else>{{row.export_pkg_name ? row.export_pkg_name : '--'}}</span>
          </template>
        </bk-table-column>
        <!-- 文件大小 -->
        <bk-table-column
          :label="$t('exportHistory.fileSize')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <span>{{row.export_pkg_size ? `${row.export_pkg_size}M` : '--'}}</span>
          </template>
        </bk-table-column>
        <!-- 操作者 -->
        <bk-table-column
          :label="$t('exportHistory.operator')"
          prop="export_created_by"
          align="center"
          header-align="center">
        </bk-table-column>
        <!-- 操作时间 -->
        <bk-table-column
          :label="$t('exportHistory.operatingTime')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <span>{{getFormatDate(row.export_created_at)}}</span>
          </template>
        </bk-table-column>
        <!-- 操作 -->
        <bk-table-column
          :label="$t('exportHistory.operate')"
          width="100"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <bk-button
              text
              style="margin-right: 10px;"
              v-if="isShowDownload(row)"
              @click="downloadExport(row)">
              {{$t('exportHistory.download')}}
            </bk-button>
            <bk-button
              text
              v-if="isShowRetry(row)"
              @click="retryExport(row)">
              {{$t('exportHistory.retry')}}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>

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
            {{ searchDict.size > 2000000 ? $t('retrieve.dataMoreThanMillion') : $t('retrieve.dataMoreThan') }}
          </div>
          <div class="export-type immediate-export">
            <span class="bk-icon icon-info-circle"></span>
            <span class="export-text">{{ $t('retrieve.immediateExportDesc') }}</span>
            <bk-button theme="primary" @click="openDownloadUrl()">{{ $t('retrieve.immediateExport') }}</bk-button>
          </div>
          <div class="export-type async-export">
            <span class="bk-icon icon-info-circle"></span>
            <span v-if="searchDict.size > 2000000" class="export-text">{{ $t('retrieve.asyncExportMoreDesc') }}</span>
            <span v-else class="export-text">{{ $t('retrieve.asyncExportDesc') }}</span>
            <bk-button @click="downloadAsync">{{ $t('retrieve.asyncExport') }}</bk-button>
          </div>
        </div>
      </bk-dialog>
    </div>
  </bk-dialog>
</template>

<script>
import { formatDate, copyMessage } from '@/common/util';


export default {
  props: {
    showHistoryExport: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      exportList: [],
      isShowDialog: false,
      tableLoading: false,
      isSearchAll: false, // 是否查看所有索引集下载历史
      isShowSetLabel: false, // 是否展示索引集ID
      exportLoading: false,
      showAsyncExport: false, // 是否展示同异步选择弹窗
      searchDict: { // 当前重试选择的请求参数
        size: 0,
      },
      exportStatusList: {
        download_log: this.$t('exportHistory.pulling'),
        export_package: this.$t('exportHistory.exportPackage'),
        export_upload: this.$t('exportHistory.exportUpload'),
        success: this.$t('exportHistory.success'),
        failed: this.$t('exportHistory.failed'),
        expired: this.$t('exportHistory.expired'),
      },
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      position: {
        top: 120,
      },
    };
  },
  computed: {
    bkBizId() {
      return this.$store.state.bkBizId;
    },
  },
  watch: {
    showHistoryExport(val) {
      this.isShowDialog = val;
      if (val) {
        this.getTableList();
      }
    },
  },
  methods: {
    getTableList() {
      const { limit, current } = this.pagination;
      this.tableLoading = true;
      this.$http.request('retrieve/getExportHistoryList', {
        params: {
          index_set_id: this.$route.params.indexId,
          bk_biz_id: this.bkBizId,
          page: current,
          pagesize: limit,
          show_all: this.isSearchAll,
        },
      }).then((res) => {
        if (res.result) {
          this.pagination.count = res.data.total;
          this.exportList = res.data.list;
        }
        // 查询所有索引集时才显示索引集IDLabel
        if (this.isSearchAll) {
          this.isShowSetLabel = true;
        }
      })
        .finally(() => {
          this.tableLoading = false;
        });
    },
    downloadExport($row) {
      // 异步导出使用downloadURL下载
      if ($row.download_url) {
        window.open($row.download_url);
        return;
      }
      this.openDownloadUrl($row.search_dict);
    },
    retryExport($row) {
      // 异常任务直接异步下载
      if ($row.export_status === 'failed') {
        this.downloadAsync($row.search_dict);
        return;
      };
      // 数据大于1万时显示确认异步弹窗
      if ($row.search_dict.size > 10000) {
        this.searchDict = $row.search_dict;
        this.showAsyncExport = true;
      } else {
        this.openDownloadUrl($row.search_dict);
      }
    },
    openDownloadUrl(params) {
      params = params ? params : this.searchDict;
      const exportParams = encodeURIComponent(JSON.stringify({ ...params }));
      // eslint-disable-next-line max-len
      const targetUrl = `${window.SITE_URL}api/v1/search/index_set/${this.$route.params.indexId}/export/?export_dict=${exportParams}`;
      window.open(targetUrl);
    },
    downloadAsync(dict) {
      dict = dict ? dict : this.searchDict;
      const data = { ...dict };

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
    handleSearchAll() {
      this.isSearchAll = true;
      this.getTableList();
    },
    getSearchDictStr(searchObj) {
      return JSON.stringify(searchObj);
    },
    getSearchDictHtml(searchObj) {
      const objStr = JSON.stringify(searchObj, null, 4);
      return objStr.replace(/\n/g, '<br>').replace(/\s/g, ' ');
    },
    isShowDownload(row) {
      return row.export_status === 'success';
    },
    isShowRetry(row) {
      return ['failed', 'expired', 'success'].includes(row.export_status);
    },
    getStatusStr(status) {
      return this.exportStatusList[status];
    },
    getFormatDate(time) {
      return formatDate(time);
    },
    handleCopyMsg(searchObj) {
      copyMessage(JSON.stringify(searchObj));
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getTableList();
    },
    handleLimitChange(size) {
      if (this.pagination.limit !== size) {
        this.pagination.current = 1;
        this.pagination.limit = size;
        this.getTableList();
      }
    },
    /**
     * @desc: 关闭table弹窗清空数据
     */
    closeDialog() {
      this.isSearchAll = false;
      this.isShowSetLabel = false;
      this.exportList = [];
      this.pagination = {
        current: 1,
        count: 0,
        limit: 10,
      };
      this.searchDict = {
        size: 0,
      };
      this.$emit('handleCloseDialog');
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/flex.scss';

.table-title {
  font-size: 16px;
  font-weight: 700;
}

.search-history {
  width: 100%;
  text-align: right;
  margin: 10px 0 20px 0;
}

.icon-text-file {
  position: absolute;
  right: 10px;
  font-size: 16px;
  cursor: pointer;
  transform: rotateZ(180deg);
}

.export-table {
  height: calc(100vh - 380px);
  overflow-y: auto;

  .bk-table-body-wrapper {
    min-height: calc(100vh - 520px);

    .bk-table-empty-block {
      min-height: calc(100vh - 440px);

      @include flex-center;
    }
  }
}

.parameter-search {
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  width: 140px;
}

.async-export-dialog {
  .header {
    /* stylelint-disable-next-line declaration-no-important */
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
