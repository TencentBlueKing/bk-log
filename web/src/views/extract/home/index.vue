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
  <div
    class="main-container"
    data-test-id="logExtraction_div_fromBox"
    v-bkloading="{ isLoading }">
    <div class="option-container">
      <bk-button
        theme="primary"
        style="width: 120px;"
        data-test-id="fromBox_button_addNewExtraction"
        @click="handleCreateTask">{{ $t('新建') }}</bk-button>
      <bk-input
        v-model="searchKeyword"
        class="king-input-search"
        data-test-id="fromBox_input_searchExtraction"
        :placeholder="$t('搜索文件名、创建人，按 enter 键搜索')"
        :clearable="true"
        :left-icon="'bk-icon icon-search'"
        @clear="handleSearch"
        @left-icon-click="handleSearch"
        @enter="handleSearch"
        @change="handleSearchChange">
      </bk-input>
    </div>
    <bk-table
      class="king-table"
      :data="taskList"
      :pagination="pagination"
      data-test-id="fromBox_table_tableBox"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column :label="$t('下载目标')" min-width="140">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{ ipList(row.ip_list) }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('文件')" min-width="240">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{ row.file_path.join('; ') }}</span>
        </div>
      </bk-table-column>
      <bk-table-column
        :label="$t('创建时间')"
        prop="created_at"
        min-width="120">
      </bk-table-column>
      <bk-table-column :label="$t('备注')" min-width="120">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{ row.remark || '--' }}</span>
        </div>
      </bk-table-column>
      <bk-table-column
        :label="$t('创建人')"
        prop="created_by"
        min-width="100">
      </bk-table-column>
      <bk-table-column :label="$t('任务状态')" min-width="100">
        <div
          slot-scope="{ row }"
          :class="{
            'task-status-warning': true,
            'task-status-success': row.download_status === 'downloadable' || row.download_status === 'redownloadable',
            'task-status-error': row.download_status === 'expired' || row.download_status === 'failed'
          }">
          <span class="bk-icon icon-refresh" v-if="!notLoadingStatus.includes(row.download_status)"></span>
          <span>{{ row.download_status_display }}</span>
          <span
            class="log-icon icon-info-fill"
            v-if="row.download_status === 'failed'"
            v-bk-tooltips="row.task_process_info"></span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" min-width="100">
        <div slot-scope="{ row }" class="task-operation-container">
          <span class="task-operation" @click="viewDetail(row)">{{ $t('详情') }}</span>
          <span
            class="task-operation"
            v-if="row.preview_ip && row.preview_ip.indexOf(':') !== -1"
            @click="cloneTask(row)">
            {{ $t('克隆') }}
          </span>
          <span
            class="task-operation"
            v-if="row.download_status === 'downloadable'"
            @click="downloadFile(row)">
            {{ $t('下载') }}
          </span>
          <span
            class="task-operation"
            v-if="row.download_status === 'redownloadable'"
            @click="reDownloadFile(row)">
            {{ $t('重新下载') }}
          </span>
        </div>
      </bk-table-column>
      <div slot="empty">
        <empty-status :empty-type="emptyType" @operation="handleOperation" />
      </div>
    </bk-table>
    <!-- 表格侧边栏 -->
    <bk-sideslider :is-show.sync="sideSlider.isShow" :quick-close="true" :title="$t('详情')" :width="660" transfer>
      <div slot="content" class="task-detail-content" v-bkloading="{ isLoading: sideSlider.isLoading }">
        <list-box icon="log-icon icon-info-fill" :title="sideSlider.data.task_process_info" :mark="true" />
        <task-status-detail :status-data="sideSlider.data.task_step_status" />
        <download-url :task-id="sideSlider.data.task_id" />
        <list-box icon="bk-icon icon-sitemap" :title="$t('文件路径')" :list="sideSlider.data.preview_directory" />
        <list-box icon="bk-icon icon-data" :title="$t('下载目标')" :list="sideSlider.data.ip_list" />
        <list-box icon="bk-icon icon-file" :title="$t('文件列表')" :list="sideSlider.data.file_path" />
        <list-box icon="bk-icon icon-clock" :title="$t('过期时间')" :list="sideSlider.data.expiration_date" />
        <text-filter-detail v-if="sideSlider.data.filter_type" :data="sideSlider.data" />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import ListBox from './list-box';
import DownloadUrl from './download-url';
import TaskStatusDetail from './task-status-detail';
import TextFilterDetail from './text-filter-detail';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'ExtractHome',
  components: {
    ListBox,
    DownloadUrl,
    TaskStatusDetail,
    TextFilterDetail,
    EmptyStatus,
  },
  data() {
    return {
      searchKeyword: '',
      isLoading: false,
      // 列表数据
      taskList: [],
      pagination: {
        count: 0,
        current: 1,
        limit: 10,
      },
      // 轮询时间(s)
      timeout: 10,
      timeoutID: null,
      // 侧边栏
      sideSlider: {
        isLoading: false,
        isShow: false,
        data: {},
      },
      // 不需要转圈的状态
      notLoadingStatus: ['downloadable', 'redownloadable', 'expired', 'failed'],
      // 不需要轮询的状态
      doneStatus: ['redownloadable', 'expired', 'failed'],
      emptyType: 'empty',
    };
  },
  computed: {
    pollingList() {
      // 需要轮询状态的下载项
      return this.taskList.filter(item => !this.doneStatus.includes(item.download_status));
    },
  },
  created() {
    this.initTaskList();
  },
  mounted() {
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
  },
  beforeDestroy() {
    clearTimeout(this.timeoutID);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },
  methods: {
    async initTaskList() {
      try {
        clearTimeout(this.timeoutID);
        this.isLoading = true;
        this.emptyType = this.searchKeyword ? 'search-empty' : 'empty';
        const payload = {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
            page: this.pagination.current,
            pagesize: this.pagination.limit,
          },
        };
        if (this.searchKeyword) {
          payload.query.keyword = this.searchKeyword;
        }
        const res = await this.$http.request('extract/getTaskList', payload);
        this.pagination.count = res.data.total;
        this.taskList = res.data.list;
        this.timeout = res.data.timeout || 10;
        this.pollingTaskStatus();
      } catch (e) {
        console.warn(e);
        this.emptyType = '500';
      } finally {
        this.isLoading = false;
      }
    },
    pollingTaskStatus() {
      this.timeoutID = setTimeout(async () => {
        if (!this.pollingList.length) {
          return;
        }
        try {
          const res = await this.$http.request('extract/pollingTaskStatus', {
            query: {
              task_list: this.pollingList.map(item => item.task_id).join(','),
            },
          });

          res.data.forEach((newItem) => {
            const taskItem = this.taskList.find(item => item.task_id === newItem.task_id);
            if (taskItem) {
              taskItem.task_process_info = newItem.task_process_info;
              taskItem.download_status = newItem.download_status;
              taskItem.download_status_display = newItem.download_status_display;
            }
          });
        } catch (err) {
          console.warn(err);
        }
        this.pollingTaskStatus();
      }, this.timeout * 1000);
    },
    handleVisibilityChange() {
      if (document.hidden) {
        clearTimeout(this.timeoutID);
      } else {
        this.initTaskList();
      }
    },
    handleSearch() {
      this.pagination.current = 1;
      this.initTaskList();
    },
    async viewDetail(row) {
      try {
        this.sideSlider.isShow = true;
        this.sideSlider.isLoading = true;
        this.sideSlider.data = {};
        const res = await this.$http.request('extract/getTaskDetail', {
          params: {
            id: row.task_id,
          },
        });
        this.sideSlider.data = res.data;
      } catch (err) {
        console.warn(err);
      } finally {
        this.sideSlider.isLoading = false;
      }
    },
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.initTaskList();
      }
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.pagination.current = 1;
      this.initTaskList();
    },
    handleCreateTask() {
      this.$router.push({
        name: 'extract-create',
      });
    },
    // 克隆
    cloneTask(row) {
      sessionStorage.setItem('cloneData', JSON.stringify(row));
      this.$router.push({
        name: 'extract-clone',
      });
    },
    // 下载文件
    downloadFile({ task_id }) {
      let urlPrefix = window.AJAX_URL_PREFIX;
      if (!urlPrefix.endsWith('/')) urlPrefix += '/';
      const { bkBizId } = this.$store.state;
      // eslint-disable-next-line camelcase
      const downloadUrl = `${urlPrefix}log_extract/tasks/download/?task_id=${task_id}&bk_biz_id=${bkBizId}`;
      window.open(downloadUrl);
    },
    // 重新下载
    async reDownloadFile({ task_id }) {
      try {
        this.isLoading = true;
        await this.$http.request('extract/reDownloadFile', {
          data: {
            task_id,
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        await this.initTaskList();
      } catch (e) {
        console.warn(e);
        this.isLoading = false;
      }
    },
    ipList(ipList) {
      if (ipList[0].ip === undefined) {
        return ipList.join('; ');
      }
      return ipList.map(item => `${item.bk_cloud_id}:${item.ip}`).join('; ');
    },
    handleSearchChange(val) {
      if (val === '' && !this.isLoading) {
        this.initTaskList();
      }
    },
    handleOperation(type) {
      if (type === 'clear-filter') {
        this.searchKeyword = '';
        this.pagination.current = 1;
        this.initTaskList();
        return;
      }

      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.pagination.current = 1;
        this.initTaskList();
        return;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .main-container {
    /*新增任务样式*/
    .option-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 0;

      .king-input-search {
        width: 486px;

        ::v-deep .icon-search {
          &:hover {
            color: #3b84ff;
            cursor: pointer;
          }
        }
      }
    }

    /*表格内容样式*/
    ::v-deep .king-table {
      background-color: #fff;

      /*分页下拉*/
      .bk-select-name {
        /* stylelint-disable-next-line declaration-no-important */
        width: 76px !important;
      }

      .task-operation-container {
        display: flex;
        align-items: center;

        .task-operation {
          margin-right: 12px;
          color: #3a84ff;
          cursor: pointer;
        }
      }

      .task-status-warning {
        display: flex;
        align-items: center;
        color: #ff9c01;

        .icon-info-fill {
          margin-left: 2px;
          cursor: pointer;
        }

        .icon-refresh {
          margin-right: 2px;
          animation: refresh-rotate 1s linear infinite;

          @keyframes refresh-rotate {
            0% {transform: rotate(0deg);}

            100% {transform: rotate(360deg);}
          }
        }
      }

      .task-status-success {
        color: #2dcb56;
      }

      .task-status-error {
        color: #ea3636;
      }
    }
  }

  /*侧边栏插槽*/
  .task-detail-content {
    height: calc(100vh - 60px);
    padding-bottom: 20px;
    overflow: auto;

    ::v-deep .list-box-container {
      padding: 14px 20px 10px;
      font-size: 15px;
      line-height: 40px;
      color: #63656e;

      .list-title {
        display: flex;
        align-items: center;

        .bk-icon {
          margin-right: 6px;
          font-size: 14px;
        }

        .text {
          color: #313238;
          margin: 0;
          font-size: 16px;
          font-weight: 500;
          line-height: 20px;
          padding: 10px 0;
          word-break: break-all;
        }

        &.mark {
          .log-icon {
            margin-right: 4px;
            font-size: 16px;
            color: #ea3636;
          }

          .text {
            color: #ea3636;
          }
        }
      }

      .list-box {
        border-top: 1px solid #dcdee5;

        .list-item {
          padding: 10px 0;
          line-height: 20px;
          border-bottom: 1px solid #dcdee5;
          word-break: break-all;

          &:hover {
            background-color: #f0f1f5;
          }
        }
      }
    }
  }
</style>
