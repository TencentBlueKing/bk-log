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
  <section class="migrate-container">
    <h3>{{$t('migrate.description1')}}</h3>
    <h3>{{$t('migrate.description2')}}</h3>
    <h3>{{$t('migrate.description3')}}</h3>
    <h3 style="padding-left: 7px;">{{$t('migrate.description4')}}</h3>
    <h3 style="padding-left: 7px;">{{$t('migrate.description5')}}</h3>
    <h3>{{$t('migrate.description6')}}</h3>

    <bk-table
      :data="list"
      class="king-table"
      @select="handleSelect"
      @select-all="handleSelect"
      v-bkloading="{ isLoading: isShowingTableLoading }">
      <!-- checkbox -->
      <bk-table-column type="selection" width="60" align="center" :selectable="validateSelectable"></bk-table-column>

      <!-- ID -->
      <bk-table-column label="ID" width="90" prop="bkdata_data_id"></bk-table-column>

      <!-- 采集项名称 -->
      <bk-table-column :label="$t('migrate.collectionItemName')" prop="data_alias"></bk-table-column>

      <!-- 数据分类 -->
      <bk-table-column :label="$t('migrate.dataClassification')">
        <template slot-scope="props">
          <bk-select
            :disabled="props.row.task_step !== 'READY'"
            :clearable="false"
            v-if="globalsData.category"
            v-model="props.row.category_id"
            @selected="changeDataType(props.row, $event)">
            <template v-for="(item, index) in globalsData.category">
              <bk-option-group :id="item.id" :name="item.name" :key="index">
                <bk-option
                  v-for="(option, optionIndex) in item.children"
                  :key="optionIndex"
                  :id="option.id"
                  :name="`${item.name}-${option.name}`"> {{option.name}}
                </bk-option>
              </bk-option-group>
            </template>
          </bk-select>
        </template>
      </bk-table-column>

      <!-- 采集路径 -->
      <bk-table-column :label="$t('migrate.collectionPath')">
        <template slot-scope="props">
          <div style="padding: 4px 0;">
            <p v-for="(item, index) in props.row.path_list" :key="index">{{item}}</p>
          </div>
        </template>
      </bk-table-column>

      <!-- 开始时间 -->
      <bk-table-column :label="$t('migrate.startTime')" prop="start_time">
        <template slot-scope="props">
          <div>{{props.row.start_time || '—'}}</div>
        </template>
      </bk-table-column>

      <!-- 迁移步骤 -->
      <bk-table-column :label="$t('migrate.migrationSteps')">
        <template slot-scope="props">
          <!-- 数据待确认 -->
          <div v-if="props.row.task_step === 'CONFIRM_DATA'" class="migrate-step confirm-data">
            <span class="text" @click="showConfirmDataDialog(props.row)">{{props.row.task_step_display}}</span>
            <span class="bk-icon icon-exclamation-circle"></span>
          </div>
          <!-- 完成 -->
          <div v-else-if="props.row.task_step === 'FINISHED'" class="migrate-step finished-data">
            <span class="text">{{props.row.task_step_display}}</span>
            <span class="bk-icon icon-chain" @click="goToSearch(props.row)"></span>
          </div>
          <div v-else class="migrate-step other-data">
            <span class="text">{{props.row.task_step_display}}</span>
            <span v-if="props.row.task_status === 'FAILED'" class="bk-icon icon-exclamation-circle"></span>
          </div>
        </template>
      </bk-table-column>

      <!-- 操作 -->
      <bk-table-column :label="$t('migrate.operation')">
        <template slot-scope="props">
          <div class="option-container">
            <span @click="viewDetail(props.row)">{{$t('migrate.detail')}}</span>
            <span
              v-if="props.row.task_status === 'FAILED'"
              @click="retryMigrate(props.row)">
              {{$t('migrate.retry')}}
            </span>
          </div>
        </template>
      </bk-table-column>
    </bk-table>

    <div class="action-container">
      <bk-button
        theme="primary"
        class="king-button"
        :disabled="!selectedItems.length || isShowingTableLoading"
        @click="confirmMigrate">
        {{$t('migrate.bulkMigrate')}}
      </bk-button>
      <bk-checkbox v-model="isMigrateDirectly">{{$t('migrate.migrateOption')}}</bk-checkbox>
    </div>

    <bk-dialog
      v-model="isShowingConfirmDataDialog"
      theme="primary"
      width="800"
      :ok-text="$t('migrate.confirmSwitch')"
      :close-icon="false"
      :confirm-fn="confirmData">
      <div>
        <bk-table
          v-bkloading="{ isLoading: isShowingConfirmTableLoading }"
          :border="true"
          :data="dataToConfirm"
          @select="handleSelect"
          @select-all="handleSelect">
          <!-- 日期 -->
          <bk-table-column :label="$t('migrate.date')" prop="date" width="108"></bk-table-column>

          <!-- 原采集存储索引 -->
          <bk-table-column :label="$t('migrate.originalIndex')" prop="start_time">
            <template slot-scope="props">
              <div v-if="props.row.old_index">{{computeIndexText(props.row.old_index)}}</div>
            </template>
          </bk-table-column>

          <!-- 新采集存储索引 -->
          <bk-table-column :label="$t('migrate.newIndex')" prop="start_time">
            <template slot-scope="props">
              <div v-if="props.row.new_index">
                <span @click="checkedIndexInfo = props.row" style="cursor: pointer;">
                  <bk-radio
                    :checked="checkedIndexInfo && props.row.new_index.index_id === checkedIndexInfo.new_index.index_id">
                  </bk-radio>
                  <span
                    v-bk-tooltips="$t('migrate.switchTips')"
                    style="outline: none">
                    {{computeIndexText(props.row.new_index)}}
                  </span>
                </span>
              </div>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </bk-dialog>

    <bk-sideslider
      :is-show.sync="isShowingDetailSidebar"
      :quick-close="true"
      :title="$t('migrate.taskLog')"
      :width="580">
      <div
        slot="content"
        class="detail-text"
        v-bkloading="{ isLoading: isShowingDetailLoading }">
        <pre>{{detailText}}</pre>
      </div>
    </bk-sideslider>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data() {
    return {
      timer: null,
      // 定时更新的字段
      updateFields: [
        'collector_config_id',
        'start_time',
        'task_status',
        'task_step',
        'task_step_display',
      ],
      list: [],
      isShowingTableLoading: true,
      selectedItems: [],
      isMigrateDirectly: false,
      isShowingDetailLoading: true,
      detailText: '',
      isShowingDetailSidebar: false,
      // 数据待确认
      isShowingConfirmDataDialog: false,
      isShowingConfirmTableLoading: true,
      itemToConfirm: null,
      dataToConfirm: [],
      checkedIndexInfo: null,
    };
  },
  computed: {
    ...mapGetters('globals', ['globalsData']),
  },
  created() {
    this.initData();
  },
  beforeDestroy() {
    clearInterval(this.timer);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },
  methods: {
    // 初始化
    async initData() {
      this.isShowingTableLoading = true;
      this.selectedItems = [];

      this.isMigrateDirectly = false;
      this.list = await this.getList();
      this.isShowingTableLoading = false;

      this.setTimer();
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
    },
    async getList() {
      try {
        const res = await this.$http.request('migrate/getUpgradeList', {
          query: {
            bk_biz_id: localStorage.getItem('bk_biz_id'),
          },
        });
        return res.data;
      } catch (e) {
        console.warn(e);
        return [];
      }
    },
    setTimer() {
      this.timer = setInterval(async () => {
        const list = await this.getList();
        this.list.forEach((item) => {
          for (let i = 0; i < list.length; i++) {
            const newItem = list[i];
            if (item.bkdata_data_id === newItem.bkdata_data_id) {
              this.updateFields.forEach((key) => {
                item[key] = newItem[key];
              });
              break;
            }
          }
        });
      }, 10000);
    },
    handleVisibilityChange() {
      if (document.hidden) {
        clearInterval(this.timer);
      } else {
        this.setTimer();
      }
    },
    // 左侧 checkbox 只有在 task_step === READY 才能被勾选
    validateSelectable(row) {
      return row.task_step === 'READY';
    },
    // 勾选 checkbox
    handleSelect(selection) {
      this.selectedItems = selection;
    },
    // 改变数据分类 只有在 task_step === READY 才能改变
    changeDataType(item, type) {
      item.category_id = type;
    },

    // 数据待确认
    async showConfirmDataDialog(item) {
      this.isShowingConfirmDataDialog = true;
      this.isShowingConfirmTableLoading = true;
      this.itemToConfirm = item;
      this.dataToConfirm = [];
      this.checkedIndexInfo = null;

      try {
        const res = await this.$http.request('migrate/getIndexInfo', {
          params: {
            bkdata_data_id: item.bkdata_data_id,
          },
        });
        this.dataToConfirm = res.data;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isShowingConfirmTableLoading = false;
      }
    },
    computeIndexText(indexInfo) {
      const { index_id: id, count } = indexInfo;
      return `${id}（${count}${this.$t('migrate.items')}）`;
    },
    async confirmData() {
      if (!this.checkedIndexInfo) {
        this.messageWarn(this.$t('migrate.pleaseCheckNewIndex'));
        return;
      }
      this.isShowingConfirmDataDialog = false;
      this.isShowingTableLoading = true;

      try {
        const res = await this.$http.request('migrate/setIndexInfo', {
          params: {
            bkdata_data_id: this.itemToConfirm.bkdata_data_id,
          },
          data: {
            bkdata_data_id: this.checkedIndexInfo.new_index.index_id,
            index_date: this.checkedIndexInfo.date,
          },
        });
        if (res.result === true) {
          this.initData();
        }
      } catch (e) {
        console.warn(e);
        this.isShowingTableLoading = false;
      }
    },

    // 完成 前往检索
    goToSearch(item) {
      this.$router.push({
        name: 'allocation',
        params: {
          collectorId: item.collector_config_id,
        },
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    // 查看详情
    async viewDetail(item) {
      this.isShowingDetailSidebar = true;
      this.isShowingDetailLoading = true;
      this.detailText = '';

      try {
        const res = await this.$http.request('migrate/getTaskLog', {
          params: {
            bkdata_data_id: item.bkdata_data_id,
          },
        });
        this.detailText = res.data.task_log ? res.data.task_log : this.$t('migrate.noLog');
      } catch (e) {
        console.warn(e);
      } finally {
        this.isShowingDetailLoading = false;
      }
    },
    // 任务失败 重试迁移
    async retryMigrate(item) {
      this.isShowingTableLoading = true;

      try {
        const params = [{ bkdata_data_id: item.bkdata_data_id }];
        await this.$http.request('migrate/startTask', { data: params });
        this.initData();
      } catch (e) {
        console.warn(e);
      } finally {
        this.initData();
      }
    },
    // 批量迁移
    async confirmMigrate() {
      this.isShowingTableLoading = true;

      try {
        const params = this.selectedItems.map(item => ({
          bkdata_data_id: item.bkdata_data_id,
          category_id: item.category_id,
          skip_data_migrate: this.isMigrateDirectly,
        }));
        await this.$http.request('migrate/startTask', { data: params });
      } catch (e) {
        console.warn(e);
      } finally {
        this.initData();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .migrate-container {
    color: #313238;
    padding: 20px 60px;
    font-size: 14px;

    h3 {
      margin: 0 0 6px;
      font-size: 14px;
      font-weight: normal;
    }

    .king-table {
      margin: 32px 0;

      .migrate-step {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .bk-icon {
          margin-right: 16px;
          font-weight: bold;
        }

        &.confirm-data {
          .text {
            color: #3a84ff;
            cursor: pointer;
          }

          .bk-icon {
            color: #ff9c01;
          }
        }

        &.finished-data {
          .bk-icon {
            color: #2dcb56;
            cursor: pointer;
          }
        }

        &.other-data {
          .bk-icon {
            color: #ea3636;
          }
        }
      }

      .option-container span {
        color: #3a84ff;
        cursor: pointer;
        margin-right: 8px;
      }
    }

    .action-container {
      .king-button {
        margin-right: 16px;
      }
    }

    .detail-text {
      font-size: 12px;
      min-height: calc(100vh - 76px);
      padding: 6px 20px 0;
      overflow: auto;

      pre {
        white-space: pre-wrap;
      }
    }
  }
</style>
