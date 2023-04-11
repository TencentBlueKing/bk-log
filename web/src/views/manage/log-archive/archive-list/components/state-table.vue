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
  <section
    class="archive-state-list"
    ref="scrollContainer"
    @scroll.passive="handleScroll">
    <section>
      <bk-table
        class="state-table"
        :data="dataList"
        v-bkloading="{ isLoading: isTableLoading }"
        :outer-border="false">
        <bk-table-column :label="$t('索引名')" min-width="300">
          <template slot-scope="props">
            {{ props.row.index_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('数据起止时间')" min-width="200">
          <template slot-scope="props">
            {{ `${props.row.start_time} - ${props.row.end_time}` }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('剩余')">
          <template slot-scope="props">
            {{ props.row.expired_time }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('大小')">
          <template slot-scope="props">
            {{ getFileSize(props.row.store_size) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('归档状态')">
          <template slot-scope="props">
            <div class="restore-status">
              <span :class="`status-icon is-${props.row.state}`"></span>
              <span class="status-text">{{ stateMap[props.row.state] }}</span>
            </div>
          </template>
        </bk-table-column>
        <!-- 添加操作列后可去掉此列宽度 -->
        <bk-table-column :label="$t('是否已回溯')" width="200">
          <template slot-scope="props">
            {{ props.row.is_stored ? $t('是') : $t('否') }}
          </template>
        </bk-table-column>
        <!-- <bk-table-column :label="$t('操作')" width="130">
          <div class="state-table-operate" slot-scope="props">
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'restore')">
              {{ $t('重试') }}
            </bk-button>
          </div>
        </bk-table-column> -->
      </bk-table>
      <template v-if="dataList.length">
        <div
          v-show="!isPageOver"
          v-bkloading="{ isLoading: true }"
          style="height: 40px;">
        </div>
      </template>
    </section>
  </section>
</template>

<script>
import { formatFileSize } from '@/common/util';

export default {
  name: 'ArchiveState',
  props: {
    archiveConfigId: {
      type: Number,
      default: '',
    },
  },
  data() {
    return {
      isTableLoading: false,
      throttle: false, // 滚动节流
      isPageOver: false,
      dataList: [],
      stateMap: {
        SUCCESS: this.$t('成功'),
        FAIL: this.$t('失败'),
        PARTIAL: this.$t('失败'),
        IN_PROGRESS: this.$t('回溯中'),
      },
      curPage: 0,
      pageSize: 20,
    };
  },
  created() {
    this.init();
  },
  methods: {
    handleScroll() {
      if (this.throttle || this.isPageOver) {
        return;
      }
      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;
        const el = this.$refs.scrollContainer;
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 60) {
          this.loadMore(el.scrollTop);
        }
      }, 200);
    },
    loadMore() {
      this.curPage = this.curPage + 1;
      this.requestData();
    },
    init() {
      this.isTableLoading = true;
      Promise.all([this.requestData()])
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    requestData() {
      return new Promise(() => {
        this.$http.request('archive/archiveConfig', {
          query: {
            page: this.curPage,
            pagesize: this.pageSize,
          },
          params: {
            archive_config_id: this.archiveConfigId,
          },
        }).then((res) => {
          const { data } = res;
          this.isPageOver = data.indices.length < this.pageSize;
          if (data.indices.length) {
            const list = [];
            data.indices.forEach((item) => {
              list.push({
                ...item,
              });
            });
            this.dataList.splice(this.dataList.length, 0, ...list);
          }
        })
          .finally(() => {
            this.isTableLoading = false;
          });
      });
    },
    operateHandler() {},
    getFileSize(size) {
      return formatFileSize(size);
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .archive-state-list {
    max-height: 500px;
    overflow: auto;

    .state-table {
      th.is-first,
      td.is-first {
        padding-left: 80px;
      }

      .filter-column {
        .cell {
          display: flex;
        }
      }

      .restore-status {
        display: flex;
        align-items: center;
      }

      .status-icon {
        display: inline-block;
        margin-right: 6px;
        width: 4px;
        height: 4px;
        border-radius: 50%;

        &.is-SUCCESS {
          background: #6dd400;
        }

        &.is-FAIL,
        &.is-PARTIAL {
          background: #e02020;

        }

        &.is-IN_PROGRESS {
          background: #fe9c00;
        }
      }
    }
  }
</style>
