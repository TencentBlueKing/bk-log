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
    <div class="result-table-container" data-test-id="retrieve_from_fieldForm">
      <keep-alive>
        <component
          :is="`${showOriginal ? 'OriginalList' : 'TableList'}`"
          v-bind="$attrs"
          v-on="$listeners"
          :table-list="tableList"
          :retrieve-params="retrieveParams"
          :handle-click-tools="handleClickTools"
        ></component>
      </keep-alive>

      <!-- 表格底部内容 -->
      <p class="more-desc" v-if="tableList.length === limitCount">{{ $t('仅展示检索结果的前2000条，如果要查看更多请优化查询条件') }}
        <a href="javascript: void(0);" @click="scrollToTop">{{ $t('返回顶部') }}</a>
      </p>
    </div>

    <!-- 实时滚动日志/上下文弹窗 -->
    <bk-dialog
      v-model="logDialog.visible"
      :ext-cls="logDialog.fullscreen ? 'log-dialog log-full-dialog' : 'log-dialog'"
      :title="logDialog.title"
      :header-position="logDialog.headerPosition"
      :width="logDialog.width"
      :fullscreen="logDialog.fullscreen"
      :draggable="false"
      :mask-close="false"
      :esc-close="false"
      :show-footer="false"
      @after-leave="hideDialog">
      <real-time-log
        v-if="logDialog.type === 'realTimeLog'"
        :log-params="logDialog.data"
        @toggleScreenFull="toggleScreenFull"
        @close-dialog="hideDialog" />
      <context-log
        v-if="logDialog.type === 'contextLog'"
        :retrieve-params="retrieveParams"
        :log-params="logDialog.data"
        @toggleScreenFull="toggleScreenFull"
        @close-dialog="hideDialog" />
    </bk-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import RealTimeLog from '../../result-comp/real-time-log';
import ContextLog from '../../result-comp/context-log';
import OriginalList from './original-list';
import TableList from './table-list';

export default {
  components: {
    RealTimeLog,
    ContextLog,
    OriginalList,
    TableList,
  },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    tableList: {
      type: Array,
      required: true,
    },
    showOriginal: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      limitCount: 2000,
      webConsoleLoading: false,
      logDialog: {
        title: '',
        type: '',
        width: '100%',
        visible: false,
        headerPosition: 'left',
        fullscreen: true,
        data: {},
      },
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      clearTableWidth: state => state.clearTableWidth,
    }),
    ...mapState('globals', ['fieldTypeMap']),
  },
  watch: {
    clearTableWidth() {
      const columnObj = JSON.parse(localStorage.getItem('table_column_width_obj'));
      const { params: { indexId }, query: { bizId } } = this.$route;
      if (columnObj === null || JSON.stringify(columnObj) === '{}') {
        return;
      }
      const isHaveBizId = Object.keys(columnObj).some(el => el === bizId);

      if (!isHaveBizId || columnObj[bizId].fields[indexId] === undefined) {
        return;
      }

      for (const bizKey in columnObj) {
        if (bizKey === bizId) {
          for (const fieldKey in columnObj[bizKey].fields) {
            if (fieldKey === indexId) {
              delete columnObj[bizId].fields[indexId];
              columnObj[bizId].indexsetIds.splice(columnObj[bizId].indexsetIds.indexOf(indexId, 1));
              columnObj[bizId].indexsetIds.length === 0 && delete columnObj[bizId];
            }
          }
        }
      }

      localStorage.setItem('table_column_width_obj', JSON.stringify(columnObj));
    },
  },
  methods: {
    // 滚动到顶部
    scrollToTop() {
      this.$easeScroll(0, 300, this.$parent.$parent.$parent.$refs.scrollContainer);
    },
    // 打开实时日志或上下文弹窗
    openLogDialog(row, type) {
      this.logDialog.data = row;
      this.logDialog.type = type;
      this.logDialog.title = type === 'realTimeLog' ? this.$t('实时滚动日志') : this.$t('上下文');
      this.logDialog.visible = true;
      this.logDialog.fullscreen = true;
    },
    openWebConsole(row) {
      const { cluster, container_id } = row;
      this.webConsoleLoading = true;
      this.$http.request('retrieve/getWebConsoleUrl', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        query: {
          cluster_id: encodeURIComponent(cluster),
          container_id,
        },
      }).then((res) => {
        window.open(res.data);
      })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.webConsoleLoading = false;
        });
    },
    openMonitorWeb(row) {
      const ip = row.serverIp || row.ip;
      const cloudId = row.cloudId?.toString() || row.cloudid?.toString();
      const id = cloudId ? `-${cloudId}` : '';
      const host = /\//.test(window.MONITOR_URL) ? window.MONITOR_URL : `${window.MONITOR_URL}/`;
      const url = `${host}?bizId=${this.bkBizId}#/performance/detail/${ip}${id}`;

      window.open(url);
    },
    handleClickTools(event, row, config) {
      if (['realTimeLog', 'contextLog'].includes(event)) {
        const contextFields = config.contextAndRealtime.extra?.context_fields;
        const dialogNewParams = {};
        // 传参配置指定字段
        if (Array.isArray(contextFields) && contextFields.length) {
          contextFields.push(config.timeField);
          for (const [key, val] of Object.entries(row)) {
            if (contextFields.includes(key)) dialogNewParams[key] = val;
          }
        } else {
          Object.assign(dialogNewParams, row);
        }
        this.openLogDialog(dialogNewParams, event);
      } else if (event === 'monitorWeb') this.openMonitorWeb(row);
      else if (event === 'webConsole') this.openWebConsole(row);
    },
    // 关闭实时日志或上下文弹窗后的回调
    hideDialog() {
      this.logDialog.type = '';
      this.logDialog.title = '';
      this.logDialog.visible = false;
    },
    // 实时日志或上下文弹窗开启或关闭全屏
    toggleScreenFull(isScreenFull) {
      this.logDialog.width = isScreenFull ? '100%' : 1078;
      this.logDialog.fullscreen = isScreenFull;
    },
  },
};
</script>


<style lang="scss">
  .tippy-tooltip.light-theme.bk-table-setting-popover-content-theme {
    padding: 0;
  }

  .result-table-container {
    position: relative;
    background: #fff;

    .king-table {
      margin-top: 12px;

      td {
        vertical-align: top;
      }

      .bk-table-body-wrapper {
        min-height: calc(100vh - 550px);

        .bk-table-empty-block {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 600px);
        }
      }

      .cell {
        .operation-button:not(:last-child) {
          padding-right: 8px;
        }
      }

      td mark {
        background: #f3e186;
        color: #575961;
      }

      :deep(.result-table-loading) {
        width: calc(100% - 2px);
        height: calc(100% - 2px);
      }

      .handle-card {
        display: inline-block;
        margin-left: 10px;
        width: 14px;
        height: 14px;

        &:first-child {
          margin-left: 0;
        }
      }

      .icon-handle {
        font-size: 14px;
        color: #979ba5;
        cursor: pointer;

        &:hover {
          color: #3a84ff;
        }
      }

      .time-field {
        font-weight: 700;
      }

      .original-str,
      .visiable-field {
        .cell {
          padding: 12px 14px 0 14px;
        }

        .str-content {
          position: relative;
          line-height: 20px;

          &.is-limit {
            max-height: 96px;
          }
        }

        &.is-wrap {
          .cell {
            padding: 12px 14px 8px;
          }

          .str-content {
            display: inline-block;
            overflow: hidden;
          }
        }

        .show-whole-btn {
          position: absolute;
          top: 80px;
          width: 100%;
          height: 24px;
          color: #3a84ff;
          font-size: 12px;
          background: #fff;
          cursor: pointer;
          transition: background-color .25s ease;
        }

        .hide-whole-btn {
          line-height: 14px;
          margin-top: -2px;
          color: #3a84ff;
          cursor: pointer;
        }
      }

      .original-time {
        padding-top: 16px;

        .cell {
          padding-left: 2px;
        }
      }

      .hover-row {
        .show-whole-btn {
          background-color: #f5f7fa;
        }
      }

      .original-str {
        .hide-whole-btn {
          margin-top: 4px;
        }
      }

      td.bk-table-expanded-cell {
        padding: 0;
      }

      .bk-table-column-expand .bk-icon {
        top: 17px;
      }

      &.is-wrap .cell {
        display: inline-table;
      }

      .bk-table-empty-text {
        padding: 0;
        width: 100%;
      }

      .visiable-field {
        .str-content {
          &.is-limit {
            max-height: 72px;
          }
        }

        &.is-wrap .cell {
          padding: 12px 15px 8px;
        }

        .show-whole-btn {
          top: 56px;
        }
      }

      .row-hover {
        background: #fff;
      }

      th .cell {
        /* stylelint-disable-next-line declaration-no-important */
        padding: 0 15px !important;
      }

      &.original-table .bk-table-column-expand .bk-icon {
        top: 20px;
      }
    }

    :deep(.render-header) {
      .field-type-icon {
        width: 12px;
        margin: 0 4px 0 0;
        font-size: 12px;
        color: #979ba5;
      }
    }
  }
  // 日志全屏状态下的样式
  .log-full-dialog {
    :deep(.bk-dialog-content) {
      /* stylelint-disable-next-line declaration-no-important */
      margin-bottom: 0 !important;
    }
  }

  .more-desc {
    font-size: 12px;
    text-align: center;
    color: #979ba5;

    a {
      color: #3a84ff;
    }
  }
</style>
