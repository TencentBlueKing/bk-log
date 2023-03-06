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
  <!-- 自定义上报列表页面 -->
  <div class="custom-item-container" data-test-id="custom_div_customContainer">
    <section class="operation">
      <div class="top-operation">
        <bk-button
          class="fl"
          theme="primary"
          data-test-id="customContainer_button_addNewCustom"
          v-cursor="{ active: isAllowedCreate === false }"
          @click="operateHandler({}, 'add')"
          :disabled="!collectProject || isAllowedCreate === null || isRequest">
          {{ $t('新建自定义上报') }}
        </bk-button>
        <div class="collect-search fr">
          <bk-input
            clearable
            v-model="inputKeyWords"
            data-test-id="customContainer_input_searchTableItem"
            :placeholder="$t('搜索名称、存储索引名')"
            :right-icon="'bk-icon icon-search'"
            @enter="search"
            @change="handleSearchChange">
          </bk-input>
        </div>
      </div>

      <div class="table-operation" data-test-id="customContainer_table_container">
        <bk-table
          class="custom-table"
          v-bkloading="{ isLoading: isRequest }"
          :data="collectList"
          :pagination="pagination"
          :limit-list="pagination.limitList"
          @page-change="handlePageChange"
          @page-limit-change="handleLimitChange">
          <bk-table-column
            :label="$t('数据ID')"
            :render-header="$renderHeader"
            prop="collector_config_id"
            width="100">
            <template slot-scope="props">
              <span>
                {{ props.row.bk_data_id || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('名称')" :render-header="$renderHeader" prop="collector_config_name">
            <template slot-scope="props">
              <span class="collector-config-name" @click="operateHandler(props.row, 'view')">
                {{ props.row.collector_config_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('监控对象')" :render-header="$renderHeader" prop="category_name">
            <template slot-scope="props">
              <span>
                {{ props.row.category_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('数据类型')" :render-header="$renderHeader" prop="custom_name">
            <template slot-scope="props">
              <span>
                {{ props.row.custom_name || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('过期时间')" :render-header="$renderHeader" min-width="50">
            <template slot-scope="props">
              <span>
                {{ props.row.retention ? `${props.row.retention}${$t('天')}` : '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('创建记录')" :render-header="$renderHeader" prop="created_at">
            <template slot-scope="props">
              <span>
                {{ props.row.created_at || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('更新记录')"
            :render-header="$renderHeader"
            prop="updated_at"
            width="239">
            <template slot-scope="props">
              <span>
                {{ props.row.updated_at || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('操作')"
            :render-header="$renderHeader"
            class-name="operate-column"
            width="202">
            <div class="collect-table-operate" slot-scope="props">
              <bk-button
                class="king-button"
                theme="primary"
                text
                :disabled="!props.row.is_active || (!props.row.index_set_id && !props.row.bkdata_index_set_ids.length)"
                v-cursor="{ active: !(props.row.permission && props.row.permission[authorityMap.SEARCH_LOG_AUTH]) }"
                @click="operateHandler(props.row, 'search')">
                {{ $t('检索') }}</bk-button>
              <bk-button
                class="king-button"
                theme="primary"
                text
                v-cursor="{
                  active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                }"
                @click="operateHandler(props.row, 'edit')">
                {{ $t('编辑') }}</bk-button>
              <bk-button
                class="king-button"
                theme="primary"
                text
                :disabled="!props.row.table_id"
                v-cursor="{
                  active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                }"
                @click="operateHandler(props.row, 'clean')">
                {{ $t('前往清洗') }}</bk-button>
              <bk-dropdown-menu ref="dropdown" align="right">
                <i
                  class="bk-icon icon-more"
                  style="font-size: 14px; font-weight: bold; display: inline-block;"
                  slot="dropdown-trigger">
                </i>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <!-- 查看详情 -->
                  <li>
                    <a
                      href="javascript:;"
                      v-cursor="{
                        active: !(props.row.permission && props.row.permission[authorityMap.VIEW_COLLECTION_AUTH])
                      }"
                      @click="operateHandler(props.row, 'view')">
                      {{ $t('详情') }}
                    </a>
                  </li>
                  <li v-if="props.row.is_active">
                    <a
                      href="javascript:;"
                      class="text-disabled"
                      v-if="!collectProject">
                      {{$t('停用')}}
                    </a>
                    <a
                      href="javascript:;"
                      v-else
                      v-cursor="{
                        active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                      }"
                      @click.stop="operateHandler(props.row, 'stop')">
                      {{$t('停用')}}
                    </a>
                  </li>
                  <li v-else>
                    <a
                      href="javascript:;"
                      class="text-disabled"
                      v-if="!collectProject">
                      {{$t('启用')}}
                    </a>
                    <a
                      href="javascript:;"
                      v-else
                      v-cursor="{
                        active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                      }"
                      @click.stop="operateHandler(props.row, 'start')">
                      {{$t('启用')}}
                    </a>
                  </li>
                  <li>
                    <a
                      href="javascript:;"
                      class="text-disabled"
                      v-if="!collectProject">
                      {{$t('删除')}}
                    </a>
                    <a
                      href="javascript:;"
                      v-else
                      v-cursor="{
                        active: !(props.row.permission && props.row.permission[authorityMap.MANAGE_COLLECTION_AUTH])
                      }"
                      @click="deleteCollect(props.row)">
                      {{$t('删除')}}
                    </a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </div>
          </bk-table-column>
          <div slot="empty">
            <empty-status :empty-type="emptyType" @operation="handleOperation" />
          </div>
        </bk-table>
      </div>
    </section>
  </div>
</template>

<script>
import { projectManages } from '@/common/util';
import collectedItemsMixin from '@/mixins/collected-items-mixin';
import { mapGetters } from 'vuex';
import * as authorityMap from '../../../../common/authority-map';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'CustomReportList',
  components: {
    EmptyStatus,
  },
  mixins: [collectedItemsMixin],
  data() {
    return {
      inputKeyWords: '',
      collectList: [],
      isAllowedCreate: null,
      collectProject: projectManages(this.$store.state.topMenu, 'collection-item'), // 权限
      isRequest: false,
      params: {
        collector_config_id: '',
      },
      pagination: {
        current: 1,
        count: 100,
        limit: 10,
        limitList: [10, 20, 50, 100],
      },
      emptyType: 'empty',
    };
  },
  computed: {
    ...mapGetters({
      spaceUid: 'spaceUid',
      bkBizId: 'bkBizId',
      authGlobalInfo: 'globals/authContainerInfo',
    }),
    authorityMap() {
      return authorityMap;
    },
  },
  created() {
    !this.authGlobalInfo && this.checkCreateAuth();
  },
  mounted() {
    !this.authGlobalInfo && this.search();
  },
  methods: {
    search() {
      this.pagination.current = 1;
      this.requestData();
    },
    // 路由跳转
    leaveCurrentPage(row, operateType) {
      if (operateType === 'start' || operateType === 'stop') {
        if (!this.collectProject) return;
        if (operateType === 'stop') {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('确认停用当前采集项？'),
            confirmFn: () => {
              this.toggleCollect(row, operateType);
            },
          });
        } else {
          this.toggleCollect(row, operateType);
        }
        return;
      }

      let backRoute;
      const params = {};
      const query = {};
      const routeMap = {
        add: 'custom-report-create',
        edit: 'custom-report-edit',
        search: 'retrieve',
        clean: 'clean-edit',
        view: 'custom-report-detail',
      };

      if (operateType === 'search') {
        if (!row.index_set_id && !row.bkdata_index_set_ids.length) return;
        params.indexId = row.index_set_id ? row.index_set_id : row.bkdata_index_set_ids[0];
      }

      if (['clean', 'edit', 'view'].includes(operateType)) {
        params.collectorId = row.collector_config_id;
      }

      if (operateType === 'clean') {
        backRoute = this.$route.name;
      }

      const targetRoute = routeMap[operateType];
      // this.$store.commit('collect/setCurCollect', row);
      this.$router.push({
        name: targetRoute,
        params,
        query: {
          ...query,
          spaceUid: this.$store.state.spaceUid,
          backRoute,
        },
      });
    },
    // 启用 || 停用
    toggleCollect(row, type) {
      const { isActive } = row;
      this.$http.request(`collect/${type === 'start' ? 'startCollect' : 'stopCollect'}`, {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          row.is_active = !row.is_active;
          res.result && this.messageSuccess(this.$t('修改成功'));
          this.requestData();
        }
      })
        .catch(() => {
          row.is_active = isActive;
        });
    },
    // 删除
    deleteCollect(row) {
      this.$bkInfo({
        type: 'warning',
        subTitle: this.$t('当前上报名称为{n}，确认要删除？', { n: row.collector_config_name }),
        confirmFn: () => {
          this.requestDeleteCollect(row);
        },
      });
    },
    requestData() {
      this.isRequest = true;
      this.emptyType = this.inputKeyWords ? 'search-empty' : 'empty';
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
        .catch(() => {
          this.emptyType = '500';
        })
        .finally(() => {
          this.isRequest = false;
        });
    },
    handleSearchChange(val) {
      if (val === '' && !this.isRequest) {
        this.requestData();
      }
    },
    handleOperation(type) {
      if (type === 'clear-filter') {
        this.inputKeyWords = '';
        this.pagination.current = 1;
        this.requestData();
        return;
      }

      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.pagination.current = 1;
        this.requestData();
        return;
      }
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/conf';
  @import '@/scss/devops-common.scss';
  @import '@/scss/mixins/cursor.scss';

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
          background-color: #fafbfd;
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

      .collector-config-name {
        @include cursor;
      }
    }
  }
</style>
