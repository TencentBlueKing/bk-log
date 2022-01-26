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
              <span>{{getStatusStr(row.export_status)}}</span>
            </bk-popover>
          </template>
        </bk-table-column>
        <!-- 文件名 -->
        <bk-table-column
          :label="$t('exportHistory.fileName')"
          align="center"
          header-align="center">
          <template slot-scope="{ row }">
            <span>
              {{row.export_pkg_name ? row.export_pkg_name : '--'}}
            </span>
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
    </div>
  </bk-dialog>
</template>

<script>
import { formatDate } from '@/common/util';


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
      isSearchAll: false,
      isShowSetLabel: false,
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      position: {
        top: 120,
      },
      exportStatusList: {
        download_log: this.$t('exportHistory.pulling'),
        export_package: this.$t('exportHistory.exportPackage'),
        export_upload: this.$t('exportHistory.exportUpload'),
        success: this.$t('exportHistory.success'),
        failed: this.$t('exportHistory.failed'),
        expired: this.$t('exportHistory.expired'),
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
        if (this.isSearchAll) {
          this.isShowSetLabel = true;
        }
      })
        .finally(() => {
          this.tableLoading = false;
        });
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
    closeDialog() {
      this.isSearchAll = false;
      this.exportList = [];
      this.$emit('handleCloseDialog');
    },
    downloadExport($row) {
      if ($row.download_url) {
        window.open($row.download_url);
        return;
      }
      this.$emit('historyDownload', $row.search_dict);
    },
    retryExport($row) {
      this.$emit('historyDownload', $row.search_dict);
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
</style>
