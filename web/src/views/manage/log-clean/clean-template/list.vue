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
  <section class="clean-template-container" data-test-id="cleanTemplate_section_cleanTemplateBox">
    <section class="top-operation">
      <bk-button
        class="fl"
        theme="primary"
        data-test-id="cleanTemplateBox_button_addNewCleanTemplate"
        @click="handleCreate">
        {{ $t('新建') }}
      </bk-button>
      <div class="clean-search fr">
        <bk-input
          :clearable="true"
          data-test-id="cleanTemplateBox_input_cleanTemplateSearch"
          :right-icon="'bk-icon icon-search'"
          v-model="params.keyword"
          @enter="search">
        </bk-input>
      </div>
    </section>
    <section class="clean-template-list">
      <bk-table
        class="clean-table"
        :data="templateList"
        :size="size"
        data-test-id="cleanTemplateBox_table_cleanTemplateTable"
        v-bkloading="{ isLoading: isTableLoading }"
        :pagination="pagination"
        :limit-list="pagination.limitList"
        @filter-change="handleFilterChange"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange">
        <bk-table-column :label="$t('模板名称')">
          <template slot-scope="props">
            {{ props.row.name }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('格式化方法')"
          prop="clean_type"
          class-name="filter-column"
          column-key="clean_type"
          :filters="formatFilters"
          :filter-multiple="false">
          <template slot-scope="props">
            {{ getFormatName(props.row) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="200">
          <div class="collect-table-operate" slot-scope="props">
            <!-- 编辑 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'edit')">
              {{ $t('编辑') }}
            </bk-button>
            <!-- 删除 -->
            <bk-button
              theme="primary"
              text
              class="mr10 king-button"
              @click.stop="operateHandler(props.row, 'delete')">
              {{ $t('删除') }}
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
  name: 'CleanTemplate',
  data() {
    return {
      isTableLoading: true,
      size: 'small',
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      templateList: [],
      params: {
        keyword: '',
        clean_type: '',
      },
    };
  },
  computed: {
    ...mapGetters({
      spaceUid: 'spaceUid',
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
      // target.push({ text: '原始数据', value: 'bk_log_text' });
      return target;
    },
  },
  created() {
    this.search();
  },
  methods: {
    search() {
      this.pagination.current = 1;
      this.requestData();
    },
    handleCreate() {
      this.$router.push({
        name: 'clean-template-create',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    handleFilterChange(data) {
      Object.keys(data).forEach((item) => {
        this.params[item] = data[item].join('');
      });
      this.search();
    },
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
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
        this.requestData();
      }
    },
    requestData() {
      this.isTableLoading = true;
      this.$http.request('clean/cleanTemplate', {
        query: {
          ...this.params,
          bk_biz_id: this.bkBizId,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
        },
      }).then((res) => {
        const { data } = res;
        this.pagination.count = data.total;
        this.templateList = data.list;
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isTableLoading = false;
        });
    },
    operateHandler(row, operateType) {
      if (operateType === 'edit') {
        this.$router.push({
          name: 'clean-template-edit',
          params: {
            templateId: row.clean_template_id,
          },
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
        return;
      }
      if (operateType === 'delete') {
        this.$bkInfo({
          type: 'warning',
          subTitle: this.$t('当前模板名称为{n}，确认要删除？', { n: row.name }),
          confirmFn: () => {
            this.requestDeleteTemp(row);
          },
        });
        return;
      }
    },
    requestDeleteTemp(row) {
      this.$http.request('clean/deleteTemplate', {
        params: {
          clean_template_id: row.clean_template_id,
        },
        data: {
          bk_biz_id: this.bkBizId,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.templateList.length <= 1
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
    getFormatName(row) {
      const cleantype = row.clean_type;
      const matchItem = this.globalsData.etl_config.find((conf) => {
        return conf.id === cleantype;
      });
      return matchItem ? matchItem.name : '';
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';

  .clean-template-container {
    padding: 20px 24px;

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
