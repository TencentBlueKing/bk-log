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
    class="extract-auth-manage"
    v-bkloading="{ isLoading }"
    data-test-id="extractAuthManage_div_extractAuthManageBox">
    <div>
      <bk-button
        v-cursor="{ active: isAllowedManage === false }"
        :disabled="isAllowedManage === null || isLoading"
        :loading="isButtonLoading"
        class="king-button"
        theme="primary"
        style="margin: 20px 0;width: 120px;"
        data-test-id="extractAuthManageBox_button_addNewExtractAuthManage"
        @click="handleCreateStrategy">
        {{$t('新增')}}
      </bk-button>
    </div>
    <bk-table class="king-table" :data="strategyList" row-key="strategy_id">
      <bk-table-column :label="$t('名称')" min-width="100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{row.strategy_name}}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('授权目标')" min-width="100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{row.modules.map(item => item.bk_inst_name).join('; ')}}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('文件目录')" min-width="100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{row.visible_dir.join('; ')}}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('文件后缀')" min-width="100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{row.file_type.join('; ')}}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('执行人')" min-width="100">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{row.operator || '--'}}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('创建时间')" prop="created_at" min-width="100"></bk-table-column>
      <bk-table-column :label="$t('创建人')" prop="created_by" min-width="80"></bk-table-column>
      <bk-table-column :label="$t('操作')" min-width="80">
        <div slot-scope="{ row }" class="task-operation-container">
          <span class="task-operation" @click="handleEditStrategy(row)">{{$t('编辑')}}</span>
          <span class="task-operation" @click="handleDeleteStrategy(row)">{{$t('删除')}}</span>
        </div>
      </bk-table-column>
      <div slot="empty">
        <empty-status :empty-type="emptyType" @operation="handleOperation" />
      </div>
    </bk-table>

    <bk-sideslider
      transfer
      :is-show.sync="showManageDialog"
      :width="520"
      :quick-close="true"
      :before-close="handleCloseSideslider"
      :title="type === 'create' ? $t('新增') : $t('编辑')">
      <directory-manage
        v-bkloading="{ isLoading: isSliderLoading }"
        slot="content"
        :user-api="userApi"
        :allow-create="allowCreate"
        :strategy-data="strategyData"
        @confirm="confirmCreateOrEdit" />
    </bk-sideslider>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import DirectoryManage from './directory-manage';
import * as authorityMap from '../../../../common/authority-map';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'ManageExtract',
  components: {
    DirectoryManage,
    EmptyStatus,
  },
  data() {
    return {
      isLoading: true,
      strategyList: [],
      allowCreate: false,
      isAllowedManage: null, // 是否有管理权限
      isButtonLoading: false, // 没有权限时点击新增按钮请求权限链接
      users: [],
      showManageDialog: false,
      isSliderLoading: false,
      type: '', // 新增或编辑策略
      strategyData: {}, // 新增或编辑策略时传递的数据
      userApi: '',
      emptyType: 'empty',
    };
  },
  computed: {
    ...mapGetters(['spaceUid']),
  },
  created() {
    this.checkManageAuth();
  },
  methods: {
    async checkManageAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: [authorityMap.MANAGE_EXTRACT_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        });
        this.isAllowedManage = res.isAllowed;
        if (res.isAllowed) {
          this.initStrategyList();
          this.allowCreate = false;
          this.userApi = window.BK_LOGIN_URL;
        } else {
          this.isLoading = false;
        }
      } catch (err) {
        console.warn(err);
        this.isLoading = false;
        this.isAllowedManage = false;
      }
    },
    async initStrategyList() {
      try {
        this.isLoading = true;
        const res = await this.$http.request('extractManage/getStrategyList', {
          query: { bk_biz_id: this.$store.state.bkBizId },
        });
        this.strategyList = res.data;
      } catch (e) {
        console.warn(e);
        this.emptyType = '500';
      } finally {
        this.isLoading = false;
      }
    },
    async handleCreateStrategy() {
      if (!this.isAllowedManage) {
        try {
          this.isButtonLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: [authorityMap.MANAGE_EXTRACT_AUTH],
            resources: [{
              type: 'space',
              id: this.spaceUid,
            }],
          });
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.isButtonLoading = false;
        }
        return;
      }

      this.type = 'create';
      this.showManageDialog = true;
      this.strategyData = {
        strategy_name: '',
        user_list: [],
        visible_dir: [''],
        file_type: [''],
        operator: this.$store.state.userMeta.operator,
        select_type: 'topo',
        modules: [],
      };
    },
    handleEditStrategy(row) {
      this.type = 'edit';
      this.showManageDialog = true;
      this.strategyData = row;
    },
    handleDeleteStrategy(row) {
      this.$bkInfo({
        title: `${this.$t('确定要删除')}【${row.strategy_name}】？`,
        closeIcon: false,
        confirmFn: this.syncConfirmFn.bind(this, row.strategy_id),
      });
    },
    // 这里使用同步是为了点击确认后立即关闭info
    syncConfirmFn(id) {
      this.confirmDeleteStrategy(id);
    },
    async confirmDeleteStrategy(id) {
      try {
        this.isLoading = true;
        await this.$http.request('extractManage/deleteStrategy', {
          params: {
            strategy_id: id,
          },
        });
        this.messageSuccess(this.$t('删除成功'));
        await this.initStrategyList();
      } catch (e) {
        console.warn(e);
        this.isLoading = false;
      }
    },
    async confirmCreateOrEdit(strategyData) {
      if (strategyData === null) {
        this.showManageDialog = false;
        return;
      }

      this.isSliderLoading = true;
      const data = Object.assign(strategyData, {
        bk_biz_id: this.$store.state.bkBizId,
      });

      if (this.type === 'create') {
        try {
          await this.$http.request('extractManage/createStrategy', {
            data,
          });
          this.showManageDialog = false;
          this.messageSuccess(this.$t('创建成功'));
          await this.initStrategyList();
        } catch (e) {
          console.warn(e);
        } finally {
          this.isSliderLoading = false;
        }
      } else if (this.type === 'edit') {
        try {
          await this.$http.request('extractManage/updateStrategy', {
            params: {
              strategy_id: data.strategy_id,
            },
            data,
          });
          this.messageSuccess(this.$t('修改成功'));
          this.showManageDialog = false;
          await this.initStrategyList();
        } catch (e) {
          console.warn(e);
        } finally {
          this.isSliderLoading = false;
        }
      }
    },
    async handleCloseSideslider() {
      return await this.showDeleteAlert();
    },
    /**
     * @desc: 如果提交可用则点击遮罩时进行二次确认弹窗
     */
    showDeleteAlert() {
      return new Promise((reject) => {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('是否放弃本次操作？'),
          confirmFn: () => {
            reject(true);
          },
          close: () => {
            reject(false);
          },
        });
      });
    },
    handleOperation(type) {
      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.initStrategyList();
        return;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .extract-auth-manage {
    padding: 0 24px 20px;

    /*表格内容样式*/
    ::v-deep .king-table {
      .task-operation-container {
        display: flex;
        align-items: center;

        .task-operation {
          margin-right: 12px;
          color: #3a84ff;
          cursor: pointer;
        }
      }
    }
  }
</style>
