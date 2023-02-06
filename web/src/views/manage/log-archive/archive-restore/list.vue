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
  <section class="log-archive-restore" data-test-id="archive_section_restoreContainer">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        data-test-id="restoreContainer_button_addNewRestore"
        @click="handleCreate">
        {{ $t('logArchive.restore') }}
      </bk-button>
      <div class="restore-search fr">
        <bk-input
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          data-test-id="restoreContainer_input_searchRestoreItem"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="log-restore-table">
      <bk-table
        class="restore-table"
        data-test-id="restoreContainer_div_restoreTable"
        :data="dataList"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('索引集名称')" min-width="200">
          <template slot-scope="props">
            {{ props.row.index_set_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.archiveItem')">
          <template slot-scope="props">
            {{ props.row.instance_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.timeRange')" min-width="240">
          <template slot-scope="props">
            {{ `${props.row.start_time} - ${props.row.end_time}` }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('logArchive.occupySize')"
          class-name="filter-column">
          <template slot-scope="props">
            {{ getFileSize(props.row.total_store_size) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('过期时间')" min-width="120">
          <template slot-scope="props">
            {{ props.row.expired_time }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.restoreStatus')">
          <template slot-scope="props">
            <div class="restore-status">
              <span :class="`status-icon is-${props.row.status}`"></span>
              <span class="status-text">{{ props.row.status_name }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logArchive.isExpired')">
          <template slot-scope="props">
            {{ props.row.is_expired ? $t('common.yes') : $t('common.no') }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="180">
          <div class="restore-table-operate" slot-scope="props">
            <!-- 检索 -->
            <log-button
              theme="primary"
              text
              ext-cls="mr10 king-button"
              :button-text="$t('检索')"
              :disabled="props.row.is_expired"
              :cursor-active="!(props.row.permission && props.row.permission[authorityMap.SEARCH_LOG_AUTH])"
              @on-click="operateHandler(props.row, 'search')">
            </log-button>
            <!-- 编辑 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              :disabled="props.row.is_expired"
              v-cursor="{
                active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
              }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <!-- 删除 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              :disabled="props.row.is_expired"
              v-cursor="{
                active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
              }"
              @click.stop="operateHandler(props.row, 'delete')">
              {{ $t('btn.delete') }}
            </bk-button>
          </div>
        </bk-table-column>
      </bk-table>
    </section>
    <!-- 新增/编辑回溯 -->
    <RestoreSlider
      v-if="isRenderSlider"
      :show-slider.sync="showSlider"
      :edit-restore="editRestore"
      @updated="handleUpdated"
    />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import RestoreSlider from './restore-slider';
import { formatFileSize } from '@/common/util';
import * as authorityMap from '../../../../common/authority-map';

export default {
  name: 'ArchiveRestore',
  components: {
    RestoreSlider,
  },
  data() {
    return {
      isTableLoading: false,
      isRenderSlider: true,
      showSlider: false,
      editRestore: null,
      timer: null,
      timerNum: 0,
      keyword: '',
      dataList: [],
      restoreIds: [], // 异步获取状态参数
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      params: {
        keyword: '',
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    authorityMap() {
      return authorityMap;
    },
  },
  created() {
    this.search();
  },
  beforeDestroy() {
    this.timerNum = -1;
    this.stopStatusPolling();
  },
  methods: {
    search() {
      this.pagination.current = 1;
      this.stopStatusPolling();
      this.requestData();
    },
    handleFilterChange(data) {
      Object.keys(data).forEach((item) => {
        this.params[item] = data[item].join('');
      });
      this.pagination.current = 1;
      this.search();
    },
    handleCreate() {
      this.showSlider = true;
      this.editRestore = null;
    },
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.stopStatusPolling();
        this.requestData();
      }
    },
    /**
     * 分页限制
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handleLimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.current = 1;
        this.pagination.limit = page;
        this.stopStatusPolling();
        this.requestData();
      }
    },
    // 轮询
    startStatusPolling() {
      this.timerNum += 1;
      const timerNum = this.timerNum;
      this.stopStatusPolling();
      this.timer = setTimeout(() => {
        timerNum === this.timerNum && this.restoreIds && this.requestRestoreStatus(true);
      }, 10000);
    },
    stopStatusPolling() {
      clearTimeout(this.timer);
    },
    requestRestoreList() {
      return new Promise((resolve, reject) => {
        this.$http.request('archive/restoreList', {
          query: {
            ...this.params,
            bk_biz_id: this.bkBizId,
            page: this.pagination.current,
            pagesize: this.pagination.limit,
          },
        }).then((res) => {
          const { data } = res;
          this.restoreIds = [];
          this.pagination.count = data.total;
          this.restoreIds = [];
          data.list.forEach((row) => {
            row.status = '';
            row.status_name = '';
            this.restoreIds.push(row.restore_config_id);
          });
          this.dataList.splice(0, this.dataList.length, ...data.list);
          resolve(res);
        })
          .catch((err) => {
            reject(err);
          })
          .finally(() => {
            this.isTableLoading = false;
          });
      });
    },
    requestData() {
      this.isTableLoading = true;
      Promise.all([this.requestRestoreList()]).then(() => {
        if (this.restoreIds.length) {
          this.requestRestoreStatus();
        }
      })
        .catch(() => {})
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    requestRestoreStatus(isPrivate) {
      const timerNum = this.timerNum;
      this.$http.request('archive/getRestoreStatus', {
        data: {
          restore_config_ids: this.restoreIds,
        },
      }).then((res) => {
        if (timerNum === this.timerNum) {
          this.statusHandler(res.data || []);
          this.startStatusPolling();
        }
        if (!isPrivate) {
          this.loadingStatus = true;
        }
      })
        .catch(() => {
          if (isPrivate) {
            this.stopStatusPolling();
          }
        });
    },
    statusHandler(data) {
      data.forEach((item) => {
        this.dataList.forEach((row) => {
          if (row.restore_config_id === item.restore_config_id) {
            const completeCount = item.complete_doc_count;
            const totalCount = item.total_doc_count;

            if (completeCount >= totalCount) {
              row.status = 'finish';
              row.status_name = this.$t('完成');
            }
            if (completeCount === 0) {
              row.statusHandler = 'unStart';
              row.status_name = this.$t('logArchive.notStarted');
            }
            if (completeCount > 0 && completeCount < totalCount) {
              const precent = `${Math.round(completeCount / totalCount * 100)}%`;
              row.status = 'restoring';
              row.status_name = `${this.$t('logArchive.restoring')}(${precent})`;
            }
          }
        });
      });
    },
    handleUpdated() {
      this.showSlider = false;
      this.search();
    },
    operateHandler(row, operateType) {
      if (operateType === 'search') {
        if (!(row.permission?.[authorityMap.SEARCH_LOG_AUTH])) {
          return this.getOptionApplyData({
            action_ids: [authorityMap.SEARCH_LOG_AUTH],
            resources: [{
              type: 'indices',
              id: row.index_set_id,
            }],
          });
        }
      }

      if (operateType === 'edit' || operateType === 'delete') {
        if (!(row.permission?.[authorityMap.MANAGE_COLLECTION_AUTH])) {
          return this.getOptionApplyData({
            action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
            resources: [{
              type: 'collection',
              id: row.instance_id,
            }],
          });
        }
      }

      if (operateType === 'search') {
        this.$router.push({
          name: 'retrieve',
          params: {
            indexId: row.index_set_id,
          },
        });
        return;
      }

      if (operateType === 'edit') {
        this.editRestore = row;
        this.showSlider = true;
        return;
      }

      if (operateType === 'delete') {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('logArchive.Confirm_delete_restore'),
          confirmFn: () => {
            this.requestDelete(row);
          },
        });
      }
    },
    requestDelete(row) {
      this.$http.request('archive/deleteRestore', {
        params: {
          restore_config_id: row.restore_config_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.dataList.length <= 1
            ? (this.pagination.current > 1 ? this.pagination.current - 1 : 1)
            : this.pagination.current;
          this.messageSuccess(this.$t('删除成功'));
          if (page !== this.pagination.current) {
            this.handlePageChange(page);
          } else {
            this.requestData();
          }
        }
      })
        .catch(() => {});
    },
    getFileSize(size) {
      return formatFileSize(size);
    },
    async getOptionApplyData(paramData) {
      try {
        this.isTableLoading = true;
        const res = await this.$store.dispatch('getApplyData', paramData);
        this.$store.commit('updateAuthDialogData', res.data);
      } catch (err) {
        console.warn(err);
      } finally {
        this.isTableLoading = false;
      }
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .log-archive-restore {
    padding: 20px 24px;

    .top-operation {
      margin-bottom: 20px;

      @include clearfix;

      .bk-button {
        width: 120px;
      }
    }

    .restore-search {
      width: 320px;
    }

    .restore-table {
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

        &.is-finish {
          background: #6dd400;
        }

        &.is-unStart {
          background: #e02020;

        }

        &.is-restoring {
          background: #fe9c00;
        }
      }
    }
  }
</style>
