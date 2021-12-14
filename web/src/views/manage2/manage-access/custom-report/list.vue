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
  <div class="custom-item-container">
    <section class="operation">
      <div class="top-operation">
        <bk-button
          class="fl"
          theme="primary"
          @click="operateHandler({}, 'add')"
          :disabled="isRequest">
          {{ $t('customReport.reportCreate') }}
        </bk-button>
        <div class="collect-search fr">
          <bk-input
            clearable
            v-model="inputKeyWords"
            :placeholder="$t('')"
            :right-icon="'bk-icon icon-search'"
            @enter="inputEnter">
          </bk-input>
        </div>
      </div>
      <div class="table-operation">
        <bk-table
          class="custom-table"
          v-bkloading="{ isLoading: isRequest }"
          :data="collectList"
          :pagination="pagination"
          @page-change="handlePageChange">
          <bk-table-column :label="$t('customReport.dataID')" prop="collector_config_id">
            <template slot-scope="props">
              <span>
                {{ props.row.collector_config_id || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.name')" prop="collector_config_name">
            <template slot-scope="props">
              <span>
                {{ props.row.collector_config_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.monitoring')" prop="category_name">
            <template slot-scope="props">
              <span>
                {{ props.row.category_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.typeOfData')" prop="custom_name">
            <template slot-scope="props">
              <span>
                {{ props.row.custom_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.createRecord')" prop="created_at">
            <template slot-scope="props">
              <span>
                {{ props.row.created_at || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.updateRecord')" prop="updated_at" width="239">
            <template slot-scope="props">
              <span>
                {{ props.row.updated_at || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('customReport.operation')" width="202" class-name="operate-column">
            <div class="collect-table-operate" slot-scope="props">
              <bk-button
                class="king-button"
                theme="primary"
                text
                @click="operateHandler({}, 'search')">
                {{ $t('nav.retrieve') }}</bk-button>
              <bk-button
                class="king-button"
                theme="primary"
                text
                @click="operateHandler({}, 'edit')">
                {{ $t('编辑') }}</bk-button>
              <bk-button
                class="king-button"
                theme="primary"
                text
                @click="operateHandler({}, 'clean')">
                {{ $t('logClean.goToClean') }}</bk-button>
              <bk-dropdown-menu ref="dropdown" align="right">
                <i
                  class="bk-icon icon-more"
                  style="margin-left: 5px; font-size: 14px; font-weight: bold;"
                  slot="dropdown-trigger">
                </i>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <!-- 查看详情 -->
                  <li>
                    <a
                      href="javascript:;"
                      @click="operateHandler(props.row, 'view')">
                      {{ $t('详情') }}
                    </a>
                  </li>
                  <li v-if="props.row.is_active">
                    <a
                      href="javascript:;"
                      class="text-disabled"
                      v-if="!props.row.status ||
                        props.row.status === 'running' ||
                        props.row.status === 'prepare' ||
                        !collectProject">
                      {{$t('btn.block')}}
                    </a>
                    <a
                      href="javascript:;"
                      v-else
                      v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                      @click.stop="operateHandler(props.row, 'stop')">
                      {{$t('btn.block')}}
                    </a>
                  </li>
                  <li v-else>
                    <a
                      href="javascript:;"
                      class="text-disabled"
                      v-if="!props.row.status ||
                        props.row.status === 'running' ||
                        props.row.status === 'prepare' ||
                        !collectProject">
                      {{$t('btn.start')}}
                    </a>
                    <a
                      href="javascript:;"
                      v-else
                      v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
                      @click.stop="operateHandler(props.row, 'start')">
                      {{$t('btn.start')}}
                    </a>
                  </li>
                  <li>
                    <a
                      href="javascript:;"
                      @click="operateHandler(props.row, 'view')">
                      {{$t('btn.delete')}}
                    </a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </div>
          </bk-table-column>
        </bk-table>
      </div>
    </section>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
  name: 'custom-report-list',
  data() {
    return {
      inputKeyWords: '',
      collectList: [],
      isRequest: false,
      pagination: {
        current: 1,
        count: 100,
        limit: 10,
      },
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
    }),
  },
  mounted() {
    this.requestData();
  },
  methods: {
    requestData() {
      this.isRequest = true;
      this.$http.request('collect/getCollectList', {
        query: {
          bk_biz_id: this.bkBizId,
          keyword: this.inputKeyWords,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
          collector_scenario_id: 'custom',
        },
      }).then((res) => {
        const { data } = res;
        if (data && data.list) {
          this.collectList.splice(0, this.collectList.length, ...data.list);
          this.pagination.count = data.total;
        }
      })
        .finally(() => {
          this.isRequest = false;
        });
    },
    inputEnter() {},
    operateHandler(row, operateType) {
      const params = {};
      const query = {};
      const routeMap = {
        add: 'custom-report-create',
      };

      const targetRoute = routeMap[operateType];
      this.$router.push({
        name: targetRoute,
        params,
        query: {
          ...query,
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    handlePageChange(page) {
      this.pagination.current = page;
    },
    remove() {
    },
    reset() {
    },
  },
};
</script>

<style lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/conf";
@import "../../../../scss/devops-common.scss";

.custom-item-container {
  padding: 20px 24px;
  .top-operation {
    margin-bottom: 20px;
    @include clearfix;
    .bk-button {
      width: 150px;
    }
    .collect-search {
      width: 360px;
    }
  }
  .table-operation {
    .custom-table {
      overflow: visible;
      .bk-table-pagination-wrapper {
        background-color: #FAFBFD;
      }
      .operate-column .cell {
        overflow: visible;
      }
      .bk-table-body-wrapper {
        overflow: visible;
      }
      .collect-table-operate {
        display: flex;
        align-items: center;
        .king-button {
          margin-right: 14px;
          &:last-child {
            margin-right: 0;
          }
        }
      }
      .bk-dropdown-list a.text-disabled:hover {
        color: #c4c6cc;
        cursor: not-allowed;
      }
    }
  }
}
</style>
