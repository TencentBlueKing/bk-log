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
    class="extract-link-list-container"
    v-bkloading="{ isLoading }"
    data-test-id="extractLinkList_div_extractLinkListBox">
    <div>
      <bk-button
        v-cursor="{ active: isAllowedManage === false }"
        :disabled="isAllowedManage === null || isLoading"
        :loading="isButtonLoading"
        class="king-button"
        theme="primary"
        style="margin: 20px 0;width: 120px;"
        data-test-id="extractLinkListBox_button_addNewLinkList"
        @click="handleCreate">
        {{ $t('新增') }}
      </bk-button>
    </div>
    <bk-table
      class="king-table"
      :data="extractLinkList"
      row-key="strategy_id"
      data-test-id="extractLinkListBox_table_LinkListTableBox">
      <bk-table-column :label="$t('链路名称')">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{ row.name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('链路类型')" prop="created_at">
        <div slot-scope="{ row }">
          <template>{{linkNameMap[row.link_type]}}</template>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" width="200">
        <div slot-scope="{ row }" class="task-operation-container">
          <span class="task-operation" @click="handleEditStrategy(row)">{{ $t('编辑') }}</span>
          <span class="task-operation" @click="handleDeleteStrategy(row)">{{ $t('删除') }}</span>
        </div>
      </bk-table-column>
      <div slot="empty">
        <empty-status :empty-type="emptyType" @operation="handleOperation" />
      </div>
    </bk-table>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import * as authorityMap from '../../../../common/authority-map';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'ExtractLinkList',
  components: {
    EmptyStatus,
  },
  data() {
    return {
      isLoading: true,
      extractLinkList: [],
      isAllowedManage: null, // 是否有管理权限
      isButtonLoading: false, // 没有权限时点击新增按钮请求权限链接
      linkNameMap: {
        common: this.$t('内网链路'),
        qcloud_cos: this.$t('腾讯云链路'),
        bk_repo: this.$t('bk_repo链路'),
      },
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
          this.initList();
        } else {
          this.isLoading = false;
        }
      } catch (err) {
        console.warn(err);
        this.isLoading = false;
        this.isAllowedManage = false;
      }
    },
    // 初始化提取链路列表
    async initList() {
      try {
        const res = await this.$http.request('extractManage/getLogExtractLinks');
        this.extractLinkList = res.data;
      } catch (e) {
        console.warn(e);
        this.emptyType = '500';
      } finally {
        this.isLoading = false;
      }
    },
    // 新增提取链路
    async handleCreate() {
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
      } else {
        this.$router.push({
          name: 'extract-link-create',
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      }
    },
    // 编辑提取链路
    handleEditStrategy(row) {
      this.$router.push({
        name: 'extract-link-edit',
        params: {
          linkId: row.link_id,
        },
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    // 删除提取链路
    handleDeleteStrategy(row) {
      this.$bkInfo({
        title: `${this.$t('确定要删除')}【${row.name}】？`,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            this.isLoading = true;
            await this.$http.request('extractManage/deleteLogExtractLink', {
              params: {
                link_id: row.link_id,
              },
            });
            this.messageSuccess(this.$t('删除成功'));
            await this.initList();
          } catch (e) {
            console.warn(e);
            this.isLoading = false;
          }
        },
      });
    },
    handleOperation(type) {
      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.search();
        return;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .extract-link-list-container {
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
