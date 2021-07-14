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
  <div class="es-access-container">
    <div class="main-operator-container">
      <bk-button
        theme="primary"
        style="width: 120px;"
        :disabled="isAllowedCreate === null || tableLoading"
        v-cursor="{ active: isAllowedCreate === false }"
        @click="addDataSource">{{ $t('新建') }}
      </bk-button>
      <bk-input
        v-model="keyword"
        style="width: 360px;"
        right-icon="bk-icon icon-search"
        :placeholder="$t('搜索ES源名称，地址，创建人')"
        :clearable="true"
        @change="handleSearch">
      </bk-input>
    </div>
    <bk-table
      v-bkloading="{ isLoading: tableLoading }"
      class="king-table"
      :data="tableDataPaged"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange">
      <bk-table-column label="ID" align="center" prop="cluster_config.cluster_id" width="60"></bk-table-column>
      <bk-table-column :label="$t('名称')" prop="cluster_config.cluster_name" min-width="170"></bk-table-column>
      <bk-table-column :label="$t('地址')" min-width="170">
        <template slot-scope="props">
          {{ props.row.cluster_config.domain_name || '--' }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('端口')" prop="cluster_config.port" min-width="80"></bk-table-column>
      <bk-table-column :label="$t('协议')" prop="cluster_config.schema" min-width="80"></bk-table-column>
      <bk-table-column :label="$t('连接状态')" min-width="80">
        <template slot-scope="{ row }">
          <!-- eslint-disable vue/no-v-html -->
          <div class="state-container" v-html="getStateText(row.cluster_config.cluster_id)"></div>
          <!--eslint-enable-->
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('创建人')" prop="cluster_config.creator" min-width="80"></bk-table-column>
      <bk-table-column :label="$t('创建时间')" prop="cluster_config.create_time" min-width="170"></bk-table-column>
      <bk-table-column :label="$t('冷热数据')" min-width="80">
        <template slot-scope="{ row }">
          {{ row.cluster_config.enable_hot_warm ? $t('开') : $t('关') }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" min-width="160">
        <template slot-scope="props">
          <bk-button
            theme="primary"
            text
            :disabled="!props.row.is_editable"
            @click="createIndexSet">
            {{ $t('建索引集') }}
          </bk-button>
          <bk-button
            theme="primary"
            text
            :disabled="!props.row.is_editable"
            v-cursor="{
              active: props.row.is_editable &&
                !(props.row.permission &&
                  props.row.permission.manage_es_source)
            }"
            @click="editDataSource(props.row)">{{ $t('编辑') }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- 编辑或新建ES源 -->
    <es-access-slider
      v-if="isRenderSlider"
      :show-slider.sync="showSlider"
      :edit-cluster-id="editClusterId"
      @hidden="handleSliderHidden"
      @updated="handleUpdated"
    ></es-access-slider>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import esAccessSlider from './esAccessSlider';

export default {
  name: 'access-es',
  components: {
    esAccessSlider,
  },
  data() {
    return {
      keyword: '',
      tableLoading: true,
      tableDataOrigin: [], // 原始数据
      tableDataSearched: [], // 搜索过滤数据
      tableDataPaged: [], // 前端分页
      pagination: {
        count: 0,
        limit: 10,
        current: 1,
      },
      stateMap: {},

      isAllowedCreate: null, // 是否有权限新建
      isRenderSlider: true, // 渲染侧边栏组件，关闭侧滑时销毁组件，避免接口在 pending 时关闭侧滑后又马上打开
      showSlider: false, // 显示编辑或新建ES源侧边栏
      editClusterId: null, // 编辑ES源ID
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
  },
  created() {
    this.checkCreateAuth();
    this.getTableData();
  },
  methods: {
    async checkCreateAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: ['create_es_source'],
          resources: [{
            type: 'biz',
            id: this.bkBizId,
          }],
        });
        this.isAllowedCreate = res.isAllowed;
      } catch (err) {
        console.warn(err);
        this.isAllowedCreate = false;
      }
    },
    /**
             * 获取存储集群列表
             */
    async getTableData() {
      try {
        this.tableLoading = true;
        // 表格数据
        const tableRes = await this.$http.request('/source/list', {
          query: {
            bk_biz_id: this.bkBizId,
          },
        });
        this.tableLoading = false;
        const list = tableRes.data;
        if (!list.length) {
          return;
        }
        this.tableDataOrigin = list;
        this.tableDataSearched = list;
        this.pagination.count = list.length;
        this.computePageData();
        // 连接状态
        try {
          const stateRes = await this.$http.request('/source/connectionStatus', {
            query: {
              bk_biz_id: this.bkBizId,
            },
            data: {
              cluster_list: list.map(item => item.cluster_config.cluster_id),
            },
          });
          this.stateMap = stateRes.data;
        } catch (e) {
          console.warn(e);
          this.stateMap = {};
        }
      } catch (e) {
        console.warn(e);
        this.tableLoading = false;
        this.tableDataOrigin.splice(0);
        this.tableDataSearched.splice(0);
        this.pagination.count = 0;
      }
    },
    getStateText(id) {
      const state = this.stateMap[id]?.status;
      if (state === true) {
        return `<span class="bk-badge bk-danger"></span> ${this.$t('正常')}`;
      } if (state === false) {
        return `<span class="bk-badge bk-warning"></span> ${this.$t('失败')}`;
      }
      return '<span class="bk-icon icon-refresh" style="display: inline-block; animation: button-icon-loading 1s linear infinite;"></i>';
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.computePageData();
    },
    handleLimitChange(limit) {
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.computePageData();
    },
    // 搜索ES源名称，地址，创建人
    handleSearch() {
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(this.searchCallback, 300);
    },
    searchCallback() {
      if (this.keyword) {
        this.tableDataSearched = this.tableDataOrigin.filter((item) => {
          if (item.cluster_config.cluster_name) {
            return (item.cluster_config.cluster_name
            + item.cluster_config.creator
            + item.cluster_config.es_host).includes(this.keyword);
          }
          return (item.source_name + item.updated_by).includes(this.keyword);
        });
      } else {
        this.tableDataSearched = this.tableDataOrigin;
      }
      this.pagination.current = 1;
      this.pagination.count = this.tableDataSearched.length;
      this.computePageData();
    },
    // 根据分页数据过滤表格
    computePageData() {
      const { current, limit } = this.pagination;
      const start = (current - 1) * limit;
      const end = this.pagination.current * this.pagination.limit;
      this.tableDataPaged = this.tableDataSearched.slice(start, end);
    },
    // 新建ES源
    async addDataSource() {
      if (this.isAllowedCreate) {
        this.showSlider = true;
        this.editClusterId = null;
      } else {
        try {
          this.tableLoading = true;
          const res = await this.$store.dispatch('getApplyData', {
            action_ids: ['create_es_source'],
            resources: [{
              type: 'biz',
              id: this.bkBizId,
            }],
          });
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.tableLoading = false;
        }
      }
    },
    // 建索引集
    createIndexSet() {
      this.$router.push({
        name: 'addIndexSet',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    // 编辑ES源
    async editDataSource(item) {
      const id = item.cluster_config.cluster_id;
      // eslint-disable-next-line camelcase
      if (!(item.permission?.manage_es_source)) {
        try {
          const paramData = {
            action_ids: ['manage_es_source'],
            resources: [{
              type: 'es_source',
              id,
            }],
          };
          this.tableLoading = true;
          const res = await this.$store.dispatch('getApplyData', paramData);
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.tableLoading = false;
        }
        return;
      }

      this.showSlider = true;
      this.editClusterId = id;
    },
    // 新建、编辑源更新
    handleUpdated() {
      this.showSlider = false;
      this.pagination.count = 1;
      this.getTableData();
    },
    handleSliderHidden() {
      this.isRenderSlider = false;
      this.$nextTick(() => {
        this.isRenderSlider = true;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .es-access-container {
    padding: 20px 60px;

    .main-operator-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .king-table {
      /deep/ .state-container {
        display: flex;
        align-items: center;

        .bk-badge {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-right: 4px;
        }

        .bk-danger {
          background-color: #2dcb56;
        }

        .bk-warning {
          background-color: #ea3636;
        }
      }

      /deep/ .cell {
        padding: 4px 15px;
      }
    }
  }
</style>
