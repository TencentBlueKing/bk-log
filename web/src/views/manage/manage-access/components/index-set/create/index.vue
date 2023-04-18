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
    class="create-index-container"
    v-bkloading="{ isLoading: basicLoading }"
    data-test-id="logIndexSetBox_div_newlogIndexSetBox">
    <auth-container-page v-if="authPageInfo" :info="authPageInfo"></auth-container-page>
    <template v-else>
      <article class="article">
        <h3 class="title">{{ $t('基础信息') }}</h3>
        <bk-form
          class="king-form"
          ref="formRef"
          :label-width="160"
          :model="formData"
          :rules="formRules">
          <bk-form-item
            :label="$t('索引集名称')"
            required
            property="index_set_name">
            <bk-input
              v-model="formData.index_set_name"
              data-test-id="newlogIndexSetBox_input_indexSetName">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t('数据分类')"
            required
            property="category_id">
            <bk-select
              v-model="formData.category_id"
              :clearable="false"
              data-test-id="newlogIndexSetBox_select_dataClassification">
              <template v-for="item in globalsData.category">
                <bk-option-group
                  :id="item.id"
                  :name="item.name"
                  :key="item.id">
                  <bk-option
                    v-for="option in item.children"
                    :key="option.id" :id="option.id"
                    :name="`${item.name}-${option.name}`">
                    {{ option.name }}
                  </bk-option>
                </bk-option-group>
              </template>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('集群')"
            v-if="scenarioId !== 'bkdata'"
            required
            property="storage_cluster_id">
            <bk-select
              data-test-id="newlogIndexSetBox_select_selectCluster"
              v-model="formData.storage_cluster_id"
              v-bk-tooltips.top="{
                content: $t('不能跨集群添加多个索引，切换集群请先清空索引'),
                delay: 300,
                disabled: !formData.indexes.length }"
              :clearable="false"
              :disabled="!!formData.indexes.length"
              searchable>
              <bk-option
                v-for="option in clusterList"
                v-show="option.storage_cluster_id"
                class="custom-no-padding-option"
                :key="option.storage_cluster_id"
                :id="option.storage_cluster_id"
                :name="option.storage_cluster_name">
                <div
                  v-if="!(option.permission && option.permission[authorityMap.MANAGE_ES_SOURCE_AUTH])"
                  class="option-slot-container no-authority"
                  @click.stop>
                  <span class="text">{{ option.storage_cluster_name }}</span>
                  <span class="apply-text" @click="applyClusterAccess(option)">{{ $t('申请权限') }}</span>
                </div>
                <div v-else class="option-slot-container">
                  {{ option.storage_cluster_name }}
                </div>
              </bk-option>
            </bk-select>
          </bk-form-item>
        </bk-form>
      </article>
      <article class="article">
        <h3 class="title">{{ subTitle }}</h3>
        <div class="collection-form" v-if="isShowTrace">
          <div class="collection-label">{{ $t('索引') }}</div>
          <div class="selected-collection trace">
            <trace-select :value.sync="formData.indexes" @update:value="handleTraceSelected" />
            <bk-table
              class="king-table"
              max-height="379"
              :data="traceMatches"
              v-if="traceMatches.length">
              <bk-table-column :label="$t('序号')" prop="f">
                <div slot-scope="{ $index }">
                  {{ $index + 1 }}
                </div>
              </bk-table-column>
              <bk-table-column :label="$t('字段名')" prop="field_name"></bk-table-column>
              <bk-table-column :label="$t('字段类型')" prop="field_type"></bk-table-column>
              <bk-table-column :label="$t('别名')" prop="ch_name"></bk-table-column>
              <bk-table-column :label="$t('数据类型')" prop="data_type"></bk-table-column>
              <bk-table-column :label="$t('匹配结果')">
                <div
                  slot-scope="{ row }"
                  :class="row.field_type === 'MUST' && row.match_result === 'FIELD_MISS' && 'error-text'">
                  {{ row.match_result_display }}
                </div>
              </bk-table-column>
            </bk-table>
          </div>
        </div>
        <div class="collection-form" v-else>
          <div class="collection-label">{{ $t('已选索引') }}</div>
          <div class="selected-collection">
            <template v-for="(item, index) in formData.indexes">
              <bk-tag
                closable
                :key="item.result_table_id"
                @close="removeCollection(index)">
                <span
                  style="max-width: 360px;"
                  class="overflow-tips"
                  v-bk-overflow-tips
                >
                  {{ item.result_table_id }}
                </span>
              </bk-tag>
            </template>
            <bk-button
              class="king-button"
              icon="plus"
              @click="openDialog"
              data-test-id="newlogIndexSetBox_button_addNewIndex"
            >{{ $t('新增索引') }}</bk-button>
          </div>
        </div>
      </article>
      <bk-button
        theme="primary"
        style="width: 86px;"
        :loading="submitLoading"
        data-test-id="newlogIndexSetBox_button_submit"
        @click="submitForm">
        {{ $t('提交') }}
      </bk-button>
      <component
        ref="selectCollectionRef"
        :is="scenarioId === 'es' ? 'SelectEs' : 'SelectCollection'"
        :parent-data="formData"
        :time-index.sync="timeIndex"
        v-if="!isShowTrace"
        @selected="addCollection" />
    </template>
  </div>
</template>

<script>
import SelectCollection from './select-collection';
import TraceSelect from './trace-select';
import SelectEs from './select-es';
import AuthContainerPage from '@/components/common/auth-container-page';
import { projectManages } from '@/common/util';
import { mapGetters, mapState } from 'vuex';
import * as authorityMap from '../../../../../../common/authority-map';

export default {
  name: 'IndexSetCreate',
  components: {
    SelectCollection,
    TraceSelect,
    SelectEs,
    AuthContainerPage,
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      isEdit: false, // 编辑索引集 or 新建索引集
      basicLoading: true,
      submitLoading: false,
      authPageInfo: null,
      isSubmit: false,
      clusterList: [], // 集群列表
      isShowTrace: this.$route.name.includes('track'), // 全链路追踪
      traceMatches: [], // trace index 匹配字段结果
      timeIndex: null,
      formData: {
        scenario_id: scenarioId, // 采集接入
        index_set_name: '', // 索引集名称
        category_id: '', // 数据分类
        storage_cluster_id: '', // 集群
        indexes: [], // 采集项
      },
      formRules: {
        index_set_name: [{
          required: true,
          trigger: 'blur',
        }],
        category_id: [{
          required: true,
          trigger: 'blur',
        }],
        storage_cluster_id: [{
          required: true,
          trigger: 'blur',
        }],
      },
    };
  },
  computed: {
    ...mapState(['spaceUid', 'bkBizId', 'showRouterLeaveTip']),
    ...mapState('collect', ['curIndexSet']),
    ...mapGetters('globals', ['globalsData']),
    authorityMap() {
      return authorityMap;
    },
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    subTitle() {
      const textMap = {
        log: this.$t('采集项'),
        es: this.$t('索引'),
        bkdata: this.$t('数据源'),
      };
      return textMap[this.scenarioId];
    },
  },
  created() {
    this.checkAuth();
    this.fetchPageData();
    this.getIndexStorage();
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit && !this.showRouterLeaveTip) {
      this.$bkInfo({
        title: this.$t('是否放弃本次操作？'),
        confirmFn: () => {
          next();
        },
      });
      return;
    }
    next();
  },
  methods: {
    // 检查权限、确认基本信息
    async checkAuth() {
      try {
        const isEdit = this.$route.name.endsWith('edit');
        this.isEdit = isEdit;
        const paramData = isEdit ? {
          action_ids: [authorityMap.MANAGE_INDICES_AUTH],
          resources: [{
            type: 'indices',
            id: this.$route.params.indexSetId,
          }],
        } : {
          action_ids: [authorityMap.CREATE_INDICES_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
        }
        if (isEdit) {
          await this.fetchIndexSetData();
          const data = this.curIndexSet;
          Object.assign(this.formData, {
            index_set_name: data.index_set_name,
            category_id: data.category_id,
            storage_cluster_id: data.storage_cluster_id,
            indexes: data.indexes,
          });
          this.timeIndex = {
            time_field: data.time_field,
            time_field_type: data.time_field_type,
            time_field_unit: data.time_field_unit,
          };
          if (this.isShowTrace) {
            await this.handleTraceSelected(this.formData.indexes);
          }
        }
        this.basicLoading = false;
      } catch (err) {
        console.warn(err);
        this.$nextTick(this.returnIndexList);
      }
    },
    // 索引集详情
    async fetchIndexSetData() {
      const indexSetId = this.$route.params.indexSetId.toString();
      if (!this.curIndexSet.index_set_id || this.curIndexSet.index_set_id.toString() !== indexSetId) {
        const { data: indexSetData } = await this.$http.request('indexSet/info', {
          params: {
            index_set_id: indexSetId,
          },
        });
        this.$store.commit('collect/updateCurIndexSet', indexSetData);
      }
    },
    // 初始化集群列表
    async fetchPageData() {
      try {
        if (this.scenarioId !== 'es') return;
        const clusterRes = await this.$http.request('/source/logList', {
          query: {
            bk_biz_id: this.bkBizId,
            scenario_id: 'es',
          },
        });
        // 有权限的优先展示
        const s1 = [];
        const s2 = [];
        for (const item of clusterRes.data) {
          if (item.permission?.[authorityMap.MANAGE_ES_SOURCE_AUTH]) {
            s1.push(item);
          } else {
            s2.push(item);
          }
        }
        this.clusterList = s1.concat(s2).filter(item => !item.is_platform);
        if (this.$route.query.cluster) {
          const clusterId = this.$route.query.cluster;
          if (this.clusterList.some(item => item.storage_cluster_id === Number(clusterId))) {
            this.formData.storage_cluster_id = Number(clusterId);
          }
        }
      } catch (e) {
        console.warn(e);
      }
    },
    async getIndexStorage() { // 索引集列表的集群
      try {
        if (this.scenarioId !== 'log') return;
        const queryData = { bk_biz_id: this.bkBizId };
        const res = await  this.$http.request('collect/getStorage', {
          query: queryData,
        });
        if (res.data) {
        // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            if (item.permission?.manage_es_source) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          this.clusterList = s1.concat(s2);
        }
      } catch (e) {
        console.warn(e);
      }
    },
    // 申请集群权限
    async applyClusterAccess(option) {
      try {
        this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.MANAGE_ES_SOURCE_AUTH],
          resources: [{
            type: 'es_source',
            id: option.storage_cluster_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    // 增加采集项
    openDialog() {
      if (this.scenarioId === 'es' && !this.formData.storage_cluster_id) {
        return this.messageError(this.$t('请选择集群'));
      }
      this.$refs.selectCollectionRef.openDialog();
    },
    addCollection(item) {
      if (this.scenarioId === 'log') this.formData.storage_cluster_id = item.storage_cluster_id;
      this.formData.indexes.push(item);
    },
    // 删除采集项
    removeCollection(index) {
      this.formData.indexes.splice(index, 1);
      if (!this.formData.indexes.length) {
        this.timeIndex = null;
      }
    },
    // 数据平台trace选择索引后校验
    async handleTraceSelected(val) {
      try {
        this.basicLoading = true;
        const res = await this.$http.request('/resultTables/traceMatchList', {
          data: {
            indices: val.map(item => item.result_table_id),
            scenario_id: 'bkdata',
          },
        });
        this.traceMatches = res.data;
      } catch (e) {
        console.warn(e);
        this.traceMatches.splice(0);
      } finally {
        this.basicLoading = false;
      }
    },
    // 新建索引集提交
    async submitForm() {
      try {
        await this.$refs.formRef.validate();
        const hasMatch = this.traceMatches.some((item) => {
          return item.field_type === 'MUST' && item.match_result === 'FIELD_MISS';
        });
        if (!this.formData.indexes.length) {
          return this.messageError(this.$t('请选择索引'));
        } if (this.isShowTrace && hasMatch) {
          return this.messageError(this.$t('MUST类型的字段缺失'));
        }
        this.submitLoading = true;
        const requestBody = Object.assign({
          view_roles: [], // 兼容后端历史遗留代码
          space_uid: this.spaceUid,
        }, this.formData);
        if (this.isShowTrace) {
          requestBody.is_trace_log = true;
        }
        if (this.scenarioId === 'es') {
          Object.assign(requestBody, this.timeIndex);
        } else {
          delete requestBody.storage_cluster_id;
        }
        const res = this.isEdit ? await this.$http.request('/indexSet/update', {
          params: {
            index_set_id: this.$route.params.indexSetId,
          },
          data: requestBody,
        }) : await this.$http.request('/indexSet/create', { data: requestBody });
        this.isSubmit = true;
        this.handleCreatSuccess(res.data);
      } catch (e) {
        console.warn(e);
      } finally {
        this.submitLoading = false;
      }
    },
    handleCreatSuccess({ bkdata_auth_url: authUrl, index_set_id: id }) {
      if (authUrl) {
        let redirectUrl = ''; // 数据平台授权地址
        if (process.env.NODE_ENV === 'development') {
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
          name: `${this.scenarioId}-index-set-list`,
        });
        let siteUrl = window.SITE_URL;
        if (siteUrl.startsWith('http')) {
          if (!siteUrl.endsWith('/')) siteUrl += '/';
          indexSetPath = siteUrl + href;
        } else {
          if (!siteUrl.startsWith('/')) siteUrl = `/${siteUrl}`;
          if (!siteUrl.endsWith('/')) siteUrl += '/';
          indexSetPath = window.origin + siteUrl + href;
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
      } else {
        this.messageSuccess(this.isEdit ? this.$t('设置成功') : this.$t('创建成功'));
        this.returnIndexList();
      }
    },
    returnIndexList() {
      this.$router.push({
        name: this.$route.name.replace(/create|edit/, 'list'),
        query: { ...this.$route.query },
      });
    },
  },
};
</script>

<style scoped lang="scss">
@import '@/scss/mixins/overflow-tips.scss';

.create-index-container {
  padding: 20px 24px;

  .article {
    padding: 22px 24px;
    margin-bottom: 20px;
    border: 1px solid #dcdee5;
    border-radius: 3px;
    background-color: #fff;

    .title {
      margin: 0 0 10px;
      font-size: 14px;
      font-weight: bold;
      color: #63656e;
      line-height: 20px;
    }

    .king-form {
      width: 680px;

      :deep(.bk-form-item) {
        padding: 10px 0;
        margin: 0;
      }
    }

    .collection-form {
      display: flex;
      font-size: 14px;
      color: #63656e;

      .collection-label {
        position: relative;
        width: 160px;
        padding: 10px 24px 10px 0;
        line-height: 32px;
        text-align: right;

        &:after {
          content: '*';
          color: #ea3636;
          font-size: 12px;
          display: inline-block;
          position: absolute;
          top: 12px;
          right: 16px;
        }
      }

      .selected-collection {
        display: flex;
        flex-flow: wrap;
        padding: 10px 0 0;

        :deep(.bk-tag) {
          display: inline-flex;
          align-items: center;
          height: 32px;
          line-height: 32px;
          background-color: #f0f1f5;
          padding: 0 4px 0 10px;
          margin: 0 10px 10px 0;

          .bk-tag-close {
            font-size: 18px;
          }
        }

        .king-button {
          margin-bottom: 10px;
        }
      }

      .selected-collection.trace {
        flex-flow: column;
        padding: 10px 0;

        .king-table {
          width: 1000px;
          margin-top: 10px;

          .error-text {
            color: #ea3636;
          }
        }
      }
    }
  }
}
</style>
