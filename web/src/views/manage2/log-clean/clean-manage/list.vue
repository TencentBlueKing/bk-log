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
  <section class="log-clean-container">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        :disabled="isAllowedManage === null"
        @click="handleCreate">
        {{ $t('新增') }}
      </bk-button>
      <div class="clean-search fr">
        <bk-input
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="log-clean-list">
      <bk-table
        class="clean-table"
        :data="cleanList"
        :size="size"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('migrate.collectionItemName')">
          <template slot-scope="props">
            {{ props.row.collector_config_name }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('logClean.storageIndex')">
          <template slot-scope="props">
            {{ props.row.result_table_id }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('logClean.etlConfig')"
          prop="clean_type"
          class-name="filter-column"
          column-key="clean_type"
          :filters="formatFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ getFormatName(props.row) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_by')">
          <template slot-scope="props">
            {{ props.row.updated_by }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.updated_at')">
          <template slot-scope="props">
            {{ props.row.updated_at }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('dataSource.operation')" width="200">
          <div class="collect-table-operate" slot-scope="props">
            <!-- 高级清洗授权 -->
            <bk-button
              v-if="props.row.bkdata_auth_url"
              theme="primary"
              text
              class="mr10 king-button"
              @click="handleAuth(props.row)">
              {{ $t('授权') }}
            </bk-button>
            <!-- 检索 -->
            <bk-button
              v-else
              theme="primary"
              text
              class="mr10 king-button"
              :disabled="!props.row.is_active || (!props.row.index_set_id && !props.row.bkdata_index_set_ids.length)"
              v-cursor="{ active: !(props.row.permission && props.row.permission.search_log) }"
              @click="operateHandler">
              {{ $t('nav.retrieve') }}
            </bk-button>
            <!-- 编辑 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <!-- 删除 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
              @click.stop="operateHandler(props.row, 'delete')">
              {{ $t('btn.delete') }}
            </bk-button>
          </div>
        </bk-table-column>
      </bk-table>
    </section>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'clean-list',
  data() {
    return {
      isTableLoading: true,
      size: 'small',
      isAllowedManage: null, // 是否有管理权限
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      cleanList: [
        {
          collector_config_id: 1,
          collector_config_name: 'test',
          index_set_id: 2,
          bkdata_auth_url: '1',
          bk_data_id: 10,
          etl_config: 'bk_log_json',
          result_table_id: 'test',
          permission: {
            search_log: true,
            view_collection: true,
            manage_collection: true,
          },
          updated_by: 'test',
          updated_at: '2021-07-24 17:42:32+0800',
        },
      ],
      params: {
        keyword: '',
        clean_type: '',
      },
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
      globalsData: 'globals/globalsData',
    }),
    formatFilters() {
      const { etl_config } = this.globalsData;
      const target = [];
      // eslint-disable-next-line camelcase
      etl_config && etl_config.forEach((data) => {
        target.push({
          text: data.name,
          value: data.id,
        });
      });
      target.push(
        { text: this.$t('logClean.rawData'), value: 'bk_log_text' },
        { text: this.$t('logClean.advancedClean'), value: 'bkdata_clean' },
      );
      return target;
    },
  },
  created() {
    this.checkManageAuth();
  },
  methods: {
    async checkManageAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          // TODO
          action_ids: ['manage_clean_config'],
          resources: [{
            type: 'biz',
            id: this.bkBizId,
          }],
        });
        this.isAllowedManage = res.isAllowed;
        if (res.isAllowed) {
          this.search();
        } else {
          this.isLoading = false;
        }
      } catch (err) {
        console.warn(err);
        this.isLoading = false;
        this.isAllowedManage = false;
      }
    },
    search() {
      this.handlePageChange(1);
    },
    handleFilterChange(data) {
      console.log(data);
      Object.keys(data).forEach((item) => {
        this.params[item] = data[item].join('');
      });
      console.log(this.params, 1);
      this.search();
    },
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      this.pagination.current = page;
      this.requestData();
    },
    /**
     * 分页限制
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handleLimitChange(page) {
      if (this.pagination.limit !== page) {
        this.pagination.limit = page;
        this.requestData();
      }
    },
    requestData() {
      this.$http.request('clean/cleanList', {
        query: {
          ...this.params,
          bk_biz_id: this.bkBizId,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
        },
      }).then((res) => {
        const { data } = res;
        this.pagination.count = data.total;
        this.cleanList = data.list;
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    handleCreate() {
      this.$router.push({
        name: 'clean-create',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    operateHandler(row, operateType) {
      if (operateType === 'edit') {
        this.$router.push({
          name: 'clean-edit',
          params: {
            collectorId: row.collector_config_id,
          },
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
        return;
      }
      // if (operateType === 'delete') {
      //   this.$bkInfo({
      //     type: 'warning',
      //     title: this.$t('logClean.Confirm_delete'),
      //     confirmFn: () => {
      //       this.requestDeleteClenItem(row);
      //     },
      //   });
      //   return;
      // }
    },
    getFormatName(row) {
      const cleantype = row.etl_config;
      const matchItem = this.globalsData.etl_config && this.globalsData.etl_config.find((conf) => {
        return conf.id === cleantype;
      });
      return matchItem ? matchItem.name : '';
    },
    // 计算平台授权跳转
    handleAuth({ bkdata_auth_url: authUrl, index_set_id: id }) {
      let redirectUrl = ''; // 数据平台授权地址
      if (NODE_ENV === 'development') {
        redirectUrl = `${authUrl}&redirect_url=${window.origin}/static/auth.html`;
      } else {
        let siteUrl = window.SITE_URL;
        if (siteUrl.startsWith('http')) {
          if (!siteUrl.endsWith('/')) siteUrl += '/';
          redirectUrl = `${authUrl}&redirect_url=${siteUrl}bkdata_auth/`;
        } else {
          if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
          if (!siteUrl.endsWith('/')) siteUrl += '/';
          redirectUrl = `${authUrl}&redirect_url=${window.origin}${siteUrl}bkdata_auth/`;
        }
      }
      // auth.html 返回索引集管理的路径
      let indexSetPath = '';
      const { href } = this.$router.resolve({
        name: 'log-clean-list',
      });
      let siteUrl = window.SITE_URL;
      if (siteUrl.startsWith('http')) {
        if (!siteUrl.endsWith('/')) siteUrl += '/';
        indexSetPath = siteUrl + href;
      } else {
        if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
        if (!siteUrl.endsWith('/')) siteUrl += '/';
        redirectUrl = window.origin + siteUrl + href;
      }
      // auth.html 需要使用的数据
      const urlComponent = `?indexSetId=${id}&ajaxUrl=${window.AJAX_URL_PREFIX}&redirectUrl=${indexSetPath}`;
      redirectUrl += encodeURIComponent(urlComponent);
      if (self !== top) { // 当前页面是 iframe
        window.open(redirectUrl);
        this.returnIndexList();
      } else {
        window.location.assign(redirectUrl);
      }
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .log-clean-container {
    padding: 20px 60px;
    .top-operation {
      margin-bottom: 20px;
      @include clearfix;
      .bk-button {
        width: 120px;
      }
    }
    .clean-search {
      width: 360px;
    }
    .clean-table {
      overflow: visible;
      .text-disabled {
        color: #c4c6cc;
      }
      .text-active {
        color: #3a84ff;
        cursor: pointer;
      }
      .filter-column {
        .cell {
          display: flex;
        }
      }
    }
  }
</style>
