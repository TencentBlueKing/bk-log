<template>
  <div class="extract-link-list-container" v-bkloading="{ isLoading }">
    <div>
      <bk-button
        v-cursor="{ active: isAllowedManage === false }"
        :disabled="isAllowedManage === null || isLoading"
        :loading="isButtonLoading"
        class="king-button"
        theme="primary"
        style="margin: 20px 0;width: 120px;"
        @click="handleCreate">
        {{ $t('新增') }}
      </bk-button>
    </div>
    <bk-table class="king-table" :data="extractLinkList" row-key="strategy_id">
      <bk-table-column :label="$t('链路名称')">
        <div class="table-ceil-container" slot-scope="{ row }">
          <span v-bk-overflow-tips>{{ row.name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('链路类型')" prop="created_at">
        <div slot-scope="{ row }">
          <template v-if="row.link_type === 'common'">{{ $t('内网链路') }}</template>
          <template v-else-if="row.link_type === 'qcloud_cos'">{{ $t('腾讯云链路') }}</template>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" width="200">
        <div slot-scope="{ row }" class="task-operation-container">
          <span class="task-operation" @click="handleEditStrategy(row)">{{ $t('编辑') }}</span>
          <span class="task-operation" @click="handleDeleteStrategy(row)">{{ $t('删除') }}</span>
        </div>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
export default {
  name: 'extract-link-list',
  data() {
    return {
      isLoading: true,
      extractLinkList: [],
      isAllowedManage: null, // 是否有管理权限
      isButtonLoading: false, // 没有权限时点击新增按钮请求权限链接
    };
  },
  created() {
    this.checkManageAuth();
  },
  methods: {
    async checkManageAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: ['manage_extract_config'],
          resources: [{
            type: 'biz',
            id: this.$store.state.bkBizId,
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
            action_ids: ['manage_extract_config'],
            resources: [{
              type: 'biz',
              id: this.$store.state.bkBizId,
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
            projectId: window.localStorage.getItem('project_id'),
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
          projectId: window.localStorage.getItem('project_id'),
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
  },
};
</script>

<style lang="scss" scoped>
  .extract-link-list-container {
    padding: 0 60px 20px;

    /*表格内容样式*/
    /deep/ .king-table {
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
