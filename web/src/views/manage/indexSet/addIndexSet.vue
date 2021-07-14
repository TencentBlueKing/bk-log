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
  <section v-bkloading="{ isLoading: isSectionLoading }">
    <auth-page v-if="authPageInfo" :info="authPageInfo"></auth-page>
    <bk-form v-else :model="formData" ref="validateForm">
      <bk-form-item
        :label="$t('indexSetList.Index_set_name')"
        required
        :rules="rules.index_set_name"
        :property="'index_set_name'"
        style="width: 30%;">
        <bk-input v-model="formData.index_set_name" :placeholder="$t('form.pleaseEnter')"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t('configDetails.dataClassify')"
        required
        :rules="rules.category_id"
        :property="'category_id'"
        style="width: 30%;">
        <bk-select v-model="formData.category_id">
          <template v-for="(item, index) in globalsData.category">
            <bk-option-group :id="item.id" :name="item.name" :key="index">
              <bk-option
                v-for="(option, key) in item.children"
                :key="key"
                :id="option.id"
                :name="`${item.name}-${option.name}`"> {{option.name}}
              </bk-option>
            </bk-option-group>
          </template>
        </bk-select>
      </bk-form-item>
      <!-- 是否为 trace 日志 -->
      <div class="bk-form-item is-required" style="width: 60%;" v-if="isShowTrace">
        <label class="bk-label" style="width: 150px;">
          <span class="bk-label-text" style="border-bottom: 1px dashed #d8d8d8;cursor: pointer;"
                v-bk-tooltips="traceTipConfig">{{$t('indexSetList.isTraceLog')}}</span>
        </label>
        <div id="trace-tip" style="padding: 0 10px;">
          <h4>{{$t('indexSetList.traceLogTips')}}</h4>
          <bk-table style="margin: -10px 0 10px;" :data="traceTipList">
            <bk-table-column :label="$t('indexSetList.field_name')" prop="field"></bk-table-column>
            <bk-table-column :label="$t('indexSetList.field_type')" prop="type"></bk-table-column>
            <bk-table-column :label="$t('indexSetList.description')" prop="description"></bk-table-column>
          </bk-table>
        </div>
        <div class="bk-form-content" style="margin-left: 150px;">
          <div class="bk-form-control">
            <bk-radio-group v-model="isTraceLog">
              <bk-radio :value="1" style="margin-right: 16px;">{{$t('common.yes')}}</bk-radio>
              <bk-radio :value="0">{{$t('common.no')}}</bk-radio>
            </bk-radio-group>
          </div>
        </div>
      </div>
      <bk-form-item :label="$t('indexSetList.dataOrigin')" required style="width: 60%;">
        <select-source v-bkloading="{ isLoading: isDataSourceLoading }"
                       :is-loading="isDataSourceLoading" :is-edit="isEdit"
                       :index-set-id="indexSetId"
                       :scenario-id.sync="formData.scenario_id"
                       :source-id.sync="formData.storage_cluster_id"
                       :source-name="sourceName"
                       :indexes.sync="formData.indexes"
                       :time-index.sync="timeIndexs"
                       @loading="isDataSourceLoading = $event"
        ></select-source>
      </bk-form-item>
      <bk-form-item v-if="accessUserManage"
                    :label="$t('indexSetList.jurisdiction')"
                    required :rules="rules.view_roles" :property="'view_roles'" style="width: 30%;">
        <bk-select
          v-model="formData.view_roles"
          searchable
          multiple
          :placeholder="$t('btn.select')"
          show-select-all>
          <bk-option v-for="(role, index) in roleList"
                     :key="index"
                     :id="role.group_id"
                     :name="role.group_name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item>
        <bk-button
          :theme="'primary'"
          type="button"
          :loading="submitStatus"
          :title="$t('btn.submit')"
          @click.stop.prevent="submitHandle"
          class="mr10" :disabled="!collectProject">{{ $t('btn.submit') }}</bk-button>
        <bk-button
          :theme="'default'"
          type="button"
          :title="$t('btn.cancel')"
          @click="returnIndexList"
          class="mr10">
          {{ $t('btn.cancel') }}
        </bk-button>
        <label v-show="isIndexes" class="tips-txt">{{$t('indexSetList.indexesTips')}}</label>
      </bk-form-item>
    </bk-form>
  </section>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import selectSource from './selectSource';
import AuthPage from '@/components/common/auth-page';
import { projectManage } from '@/common/util';

export default {
  name: 'addIndexSet',
  components: {
    selectSource,
    AuthPage,
  },
  data() {
    return {
      isSectionLoading: true,
      authPageInfo: null,
      timeIndexs: {
        time_format: '',
        time_field_type: '',
      },
      isShowTrace: window.FEATURE_TOGGLE.trace === 'on',
      isTraceLog: 0,
      traceTipConfig: {
        allowHtml: true,
        width: 440,
        trigger: 'click',
        theme: 'light',
        content: '#trace-tip',
      },
      timeFields: [
        { field_name: '秒（second）', field_id: 'second' },
        { field_name: '毫秒（millisecond）', field_id: 'millisecond' },
        { field_name: '微秒（microsecond）', field_id: 'microsecond' },
      ],
      traceTipList: [
        { field: 'traceID', type: 'keyword', description: 'traceID (必要)' },
        { field: 'spanID', type: 'keyword', description: 'spanID (必要)' },
        { field: 'parentSpanID', type: 'keyword', description: 'parentSpanID (必要)' },
        { field: 'operationName', type: 'keyword', description: '操作名, 一个具有可读性的字符串，代表这个span所做的工作（例如：RPC方法名，函数名，或者一个大型计算中的某个阶段或子任务） (必要)' },
        { field: 'startTime', type: 'long', description: '毫秒时间戳 (必要)' },
        { field: 'duration', type: 'long', description: '\tspan执行耗时 毫秒 (必要)' },
        { field: 'tags', type: 'object', description: '一组键值对构成的Span标签集合 (可选)' },
        // TODO: 看未来ES存储情况
        // {
        //   field: 'logs',
        //   type: 'object',
        //   description: 'span的日志集合。每次log操作包含一个键值对，以及一个时间戳。 键值对中，键必须为string，值可以是任意类型(可选)',
        // },
        { field: 'relationship', type: 'integer', description: '关联关系 1-ChildOf、2-FollowsFrom (可选)' },
      ],
      globals: {},
      editIndex: false,
      indexSetId: this.$route.params.id,
      sourceName: '',
      formData: {
        index_set_name: '',
        storage_cluster_id: '',
        view_roles: [],
        project_id: '',
        scenario_id: '',
        indexes: [],
        category_id: '',
      },
      time_fields: [],
      time_fields_type: [],
      rules: {
        index_set_name: [{ required: true, trigger: 'blur' }],
        source_id: [{ required: true, trigger: 'change' }],
        time_field: [{ required: true, trigger: 'change' }],
        time_format: [{ required: true, trigger: 'change' }],
        time_field_type: [{ required: true, trigger: 'change' }],
        category_id: [{ required: true, trigger: 'blur' }],
        view_roles: [{ validator: val => val.length >= 1, trigger: 'change' }],
      },
      isDataSourceLoading: false,
      roleList: [],
      submitStatus: false,
    };
  },
  computed: {
    ...mapState({
      currentProject: state => state.projectId,
      bkBizId: state => state.bkBizId,
      menuProject: state => state.menuProject,
    }),
    ...mapGetters('globals', ['globalsData']),
    ...mapGetters(['accessUserManage']),
    isEdit() {
      return this.$route.name === 'editIndexSet';
    },
    collectProject() {
      return projectManage(this.menuProject, 'manage', 'indexSet');
    },
  },
  created() {
    this.initPage();
  },
  methods: {
    // 先校验页面权限再初始化
    async initPage() {
      try {
        const paramData = this.isEdit ? {
          action_ids: ['manage_indices'],
          resources: [{
            type: 'indices',
            id: this.$route.params.id,
          }],
        } : {
          action_ids: ['create_indices'],
          resources: [{
            type: 'biz',
            id: this.bkBizId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          return;
        }
      } catch (err) {
        console.warn(err);
        this.$nextTick(() => {
          this.$router.push({
            name: 'indexSet',
            query: {
              projectId: window.localStorage.getItem('project_id'),
            },
          });
        });
        return;
      } finally {
        this.isSectionLoading = false;
      }

      this.getRoleList();
      if (this.$route.name === 'editIndexSet') {
        this.isDataSourceLoading = true;
        this.editIndex = true;
        this.getIndexSetInfo();
      }
    },
    // 获取索引集详情
    getIndexSetInfo() {
      this.$http.request('/indexSet/info', {
        params: {
          index_set_id: this.$route.params.id,
        },
      }).then((res) => {
        if (res.data) {
          const { data } = res;
          this.formData.index_set_name = data.index_set_name || '';
          this.formData.storage_cluster_id = data.storage_cluster_id;
          this.formData.view_roles = data.view_roles;
          this.formData.scenario_id = data.scenario_id;
          this.formData.indexes = data.indexes;
          this.timeIndexs.time_field_type = data.time_field_type;
          this.timeIndexs.time_format = data.time_field_unit;
          this.timeIndexs.time_field = data.time_field;
          this.sourceName = data.source_name;
          this.formData.category_id = data.category_id;
          if (this.isShowTrace) {
            this.isTraceLog = data.is_trace_log ? 1 : 0;
          }
        }
        this.getIndexInfo();
        this.isDataSourceLoading = false;
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    async getIndexInfo() {
      try {
        const res = await this.$http.request('/resultTables/info', {
          params: {
            result_table_id: this.formData.indexes[0].result_table_id,
          },
          query: {
            scenario_id: this.formData.scenario_id,
            bk_biz_id: this.formData.indexes[0].bk_biz_id,
            storage_cluster_id: this.formData.storage_cluster_id,
          },
        });
        this.indexFields = res.data && res.data.date_candidate;
        if (this.indexFields.length) {
          this.time_fields = this.indexFields;
          // eslint-disable-next-line camelcase
          const time_fields_type = [...this.time_fields];
          const arr = [];
          time_fields_type.forEach((item) => {
            if (arr.indexOf(item.field_type) === -1) {
              arr.push(item.field_type);
            }
          });
          this.time_fields_type = arr;
        }
      } catch (e) {
        console.warn(e);
        this.indexErrorText += e.message;
      }
    },
    // 获取查看权限用户组列表
    getRoleList() {
      this.roleList = [];
    },
    // 提交索引集
    submitHandle() {
      this.formData.project_id = this.currentProject;
      const data = JSON.parse(JSON.stringify(this.formData));
      data.bk_biz_id = this.bkBizId;
      if (this.isShowTrace) {
        data.is_trace_log = this.isTraceLog;
      }
      if (data.indexes.length === 0) {
        this.isIndexes = true;
        return;
      }
      if (data.scenario_id === 'es') {
        data.time_field = data.indexes[0].time_field;
        data.time_field_type = this.timeIndexs.time_field_type;
        data.time_field_unit = this.timeIndexs.time_format === '毫秒（millisecond）' ? 'millisecond' : data.indexes[0].time_format === '秒（second）' ? 'second' : 'microsecond';
      }
      this.$refs.validateForm.validate().then(() => {
        this.submitStatus = true;
        let url = '';
        const payload = { data };
        if (data.scenario_id === 'bkdata' || data.scenario_id === 'log') {
          delete data.storage_cluster_id;
        }
        if (this.$route.name === 'editIndexSet') { // 更新索引集
          url = '/indexSet/update';
          payload.params = {
            index_set_id: this.$route.params.id,
          };
        } else if (this.$route.name === 'addIndexSet') { // 创建索引集
          url = '/indexSet/create';
        } else {
          console.warn('未知路由');
          return;
        }
        this.$http.request(url, payload).then((res) => {
          this.handleCreatSuccess(res.data);
        })
          .catch((err) => {
            console.warn(err);
          })
          .finally(() => {
            this.submitStatus = false;
          });
      }, () => {});
    },
    handleCreatSuccess({ bkdata_auth_url: authUrl, index_set_id: id }) {
      if (authUrl) {
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
        const indexSetPath = location.href.match(/http.*\/indexSet/)[0];
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
        if (this.$route.name === 'editIndexSet') { // 更新索引集
          this.messageSuccess(this.$t('common.configSuccessfully'));
        } else {
          this.messageSuccess(this.$t('common.createdSuccessfully'));
        }
        this.returnIndexList();
      }
    },
    returnIndexList() {
      this.$router.push({
        name: 'indexSet',
        query: { ...this.$route.query },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/clearfix';
  @import '../../../scss/conf';

  section {
    padding: 20px 60px;

    /deep/ .bk-form .bk-label {
      text-align: left;
    }

    /deep/ .bk-form-item.is-required .bk-label:after {
      content: '';
    }

    /deep/ .bk-form-item.is-required .bk-label:before {
      content: '*';
      color: #ff5656;
      position: relative;
      margin: 2px 2px 0 2px;
      display: inline-block;
      vertical-align: middle;
      font-size: 16px;
      font-weight: bold;
    }

    /deep/ .bk-form-item .bk-select {
      background: #fff;
    }

    /deep/ .bk-form-item.is-error .bk-select {
      border-color: #ff5656;
      color: #ff5656;
    }

    .bk-form-input {
      width: 220px;
    }
  }
</style>
