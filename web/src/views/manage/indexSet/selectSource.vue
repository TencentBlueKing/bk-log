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
  <div class="source-box">
    <bk-radio-group v-model="selectScenarioId">
      <bk-radio v-for="(item, index) in scenarioList" :key="index" :value="item.scenario_id"
                :disabled="isEdit || isDisabled.biz || isDisabled.source">{{ item.scenario_name }}
      </bk-radio>
    </bk-radio-group>
    <template v-if="selectScenarioId">
      <div>
        <bk-select
          v-if="selectScenarioId === 'es'"
          style="width: 350px; margin-top: 10px"
          v-model="selectSourceId"
          searchable
          :disabled="isDisabled.source"
          @selected="selectedSource">
          <bk-option
            v-for="(item, index) in sortedSourceList"
            v-show="item.storage_cluster_id"
            class="custom-no-padding-option"
            :key="index"
            :id="item.storage_cluster_id"
            :name="item.storage_cluster_name">
            <div v-if="!(item.permission && item.permission.manage_es_source)"
                 class="option-slot-container no-authority" @click.stop>
              <span class="text">{{item.storage_cluster_name}}</span>
              <span class="apply-text" @click="applyESAccess(item)">{{$t('申请权限')}}</span>
            </div>
            <div v-else class="option-slot-container">
              {{item.storage_cluster_name}}
            </div>
          </bk-option>
        </bk-select>
      </div>
      <div class="mt20">
        <bk-button
          :theme="'default'"
          type="button"
          :title="$t('indexSetList.addindex')"
          @click="handleClick">
          {{ $t('indexSetList.addindex') }}
        </bk-button>
      </div>
      <bk-table
        class="mt20"
        :empty-text="$t('indexSetList.empty')"
        :data="tableConfig[selectScenarioId].data"
        :size="tableConfig[selectScenarioId].size"
        v-bkloading="{ isLoading: reloadTable }">
        <bk-table-column :label="$t('indexSetList.index')" prop="result_table_id"></bk-table-column>
        <bk-table-column
          :label="$t('indexSetList.bk_biz_name')"
          prop="bk_biz_name"
          v-if="selectScenarioId === 'bkdata'">
          <template slot-scope="props">
            {{ props.row.bk_biz_name || filterBizName(props.row.bk_biz_id) }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('indexSetList.bk_biz_name')"
          prop="bk_biz_name"
          v-else-if="selectScenarioId === 'log'">
          <template slot-scope="props">
            {{ props.row.bk_biz_name || filterBizName(props.row.bk_biz_id) }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('indexSetList.cluster_name')" v-else-if="selectScenarioId === 'es'">
          <template slot-scope="props">
            {{ selectedSourceName || props.row.result_table_id }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('indexSetList.jurisdictions')">
          <template slot-scope="props">
            {{ props.row.apply_status_name || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('indexSetList.operation')" width="150">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="remove(props.row)">{{ $t('btn.delete') }}</bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </template>
    <bk-dialog
      v-model="showAddIndex"
      :title="$t('indexSetList.addindex')"
      :header-position="'left'"
      :width="680"
      :mask-close="false"
      :show-footer="false"
      @after-leave="resetIndexParams">
      <bk-form
        :model="indexParams" :label-width="100" ref="validateForm"
        style="min-height: 424px;"
        v-bkloading="{ isLoading: isFormLoading }">
        <template v-if="selectScenarioId === 'bkdata'">
          <bk-form-item
            :label="$t('indexSetList.bk_biz_name')"
            required
            :rules="rules.bk_biz_id"
            :property="'bk_biz_id'"
            style="width: 80%;">
            <selectWrapper
              :selected.sync="indexParams.bk_biz_id"
              :searchable="true"
              :list="bkBizList"
              :display-key="'bk_biz_name'"
              :search-key="'bk_biz_name'"
              :setting-key="'bk_biz_id'"
              :disabled="true">
            </selectWrapper>
          </bk-form-item>
          <bk-form-item
            :label="$t('indexSetList.index')"
            required
            :rules="rules.result_table_id"
            :property="'result_table_id'"
            style="width: 80%;">
            <bk-select
              :clearable="false"
              v-model="indexParams.result_table_id"
              @change="getIndexInfo"
              searchable>
              <bk-option
                v-for="(indexObj, index) in indexList[selectScenarioId]"
                :disabled="selectedIndexId.indexOf(indexObj.result_table_id) > -1"
                :key="index"
                :id="indexObj.result_table_id"
                :name="indexObj.result_table_id">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item label="">
            <div class="border-class">
              <div class="index-info">
                <bk-table
                  style="position: absolute;top: -1px;"
                  :outer-border="false"
                  :empty-text="$t('btn.vacancy')"
                  v-bkloading="{ isLoading: reloadListTable }"
                  :data="indexFields"
                  size="small"
                  width="100%">
                  <bk-table-column
                    :label="$t('indexSetList.field_name')"
                    prop="field_name"
                    min-width="240">
                  </bk-table-column>
                  <bk-table-column
                    :label="$t('indexSetList.field_type')"
                    prop="field_type"
                    min-width="180">
                  </bk-table-column>
                </bk-table>
              </div>
            </div>
          </bk-form-item>
        </template>
        <template v-else-if="selectScenarioId === 'es'">
          <bk-form-item
            required
            property="result_table_id"
            class="add-index-input-container"
            :class="indexErrorText && 'is-error'"
            :label="$t('indexSetList.index')"
            :rules="rules.result_table_id">
            <bk-input
              v-model="indexParams.result_table_id"
              placeholder="log_search_*'"
              @focus="initRtId"
              @enter="getSourceIndexList">
            </bk-input>
            <bk-button
              class="king-button"
              :loading="isIndexSearchLoading"
              :disabled="isIndexSearchLoading"
              @click="getSourceIndexList">{{$t('btn.search')}}
            </bk-button>
            <div class="error-tips-container" v-if="indexErrorText">
              <span class="log-icon icon-info-fill" v-bk-tooltips="{ width: 440, content: indexErrorText }"></span>
            </div>
            <div class="input-tips">{{ $t('indexSetList.tips') }}</div>
          </bk-form-item>
          <bk-form-item label="">
            <div class="border-class">
              <div class="index-info">
                <div class="result-tips" v-if="showTableIndex">
                  <i class="bk-icon icon-check-circle-shape"></i>
                  {{$t('indexSetList.successfullyMatch') +
                    ' ' +
                    indexList[selectScenarioId].length +
                    ' ' +
                    $t('migrate.items')}}
                </div>
                <bk-table
                  style="position: absolute;top: -1px;"
                  :outer-border="false"
                  v-bkloading="{ isLoading: reloadListTable }"
                  :empty-text="$t('btn.vacancy')"
                  :data="showIndexList"
                  size="small"
                  :pagination="pagination"
                  :show-limit="false"
                  @page-change="handlePageChange"
                  width="100%">
                  <bk-table-column :label="$t('indexSetList.index')">
                    <template slot-scope="props">
                      <b>{{indexParams.result_table_id.replace(/\*$/, '')}}</b>
                      {{props.row.result_table_id.replace(indexParams.result_table_id.replace(/\*$/, ''), '')}}
                    </template>
                  </bk-table-column>
                </bk-table>
              </div>
            </div>
          </bk-form-item>
          <bk-form-item
            :label="$t('indexSetList.time')"
            required
            :rules="rules.time_field"
            :property="'time_field'"
            style="width: 525px;">
            <bk-select
              v-model="indexParams.time_field"
              searchable>
              <!-- eslint-disable -->
              <bk-option
                v-if="item.field_type === 'date' || item.field_type === 'long'"
                v-for="(item, index) in indexFields"
                :key="index"
                :id="item.field_name"
                :name="item.field_name">
                <!--eslint-enable-->
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('indexSetList.unit')"
            required
            :rules="rules.time_format"
            :property="'time_format'"
            style="width: 525px;"
            v-if="longData">
            <bk-select
              v-model="timeIndex.time_format"
              searchable>
              <bk-option
                v-for="(item, index) in timeFields"
                :key="index"
                :id="item.field_id"
                :name="item.field_name">
              </bk-option>
            </bk-select>
          </bk-form-item>
        </template>
        <template v-else-if="selectScenarioId === 'log'">
          <bk-form-item
            :label="$t('indexSetList.bk_biz_name')"
            required
            :rules="rules.bk_biz_id"
            :property="'bk_biz_id'"
            style="width: 80%;">
            <selectWrapper
              :selected.sync="indexParams.bk_biz_id"
              :searchable="true"
              :list="bkBizList"
              :display-key="'bk_biz_name'"
              :search-key="'bk_biz_name'"
              :setting-key="'bk_biz_id'"
              :disabled="true">
            </selectWrapper>
          </bk-form-item>
          <bk-form-item
            :label="$t('indexSetList.index')"
            required
            :rules="rules.display_name"
            :property="'result_table_id'"
            style="width: 80%;">
            <bk-select
              :clearable="false"
              v-model="indexParams.result_table_id"
              @change="getIndexInfo"
              searchable>
              <bk-option
                v-for="(item, index) in sortedLogIndexList"
                class="custom-no-padding-option"
                :disabled="selectedIndexId.indexOf(item.result_table_id) > -1"
                :key="index"
                :id="item.result_table_id"
                :name="item.result_table_name_alias">
                <div
                  v-if="!(item.permission && item.permission.manage_collection)"
                  class="option-slot-container no-authority" @click.stop>
                  <span class="text">{{item.result_table_name_alias}}</span>
                  <span class="apply-text" @click="applyCollectorAccess(item)">{{$t('申请权限')}}</span>
                </div>
                <div v-else class="option-slot-container">
                  {{item.result_table_name_alias}}
                </div>
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item label="">
            <div class="border-class">
              <div class="index-info">
                <bk-table
                  style="position: absolute;top: -1px;"
                  :outer-border="false"
                  v-bkloading="{ isLoading: reloadListTable }"
                  :empty-text="$t('btn.vacancy')"
                  :data="indexFields"
                  size="small"
                  width="100%">
                  <bk-table-column
                    :label="$t('indexSetList.field_name')"
                    prop="field_name"
                    min-width="240">
                  </bk-table-column>
                  <bk-table-column
                    :label="$t('indexSetList.field_type')"
                    prop="field_type"
                    min-width="180">
                  </bk-table-column>
                </bk-table>
              </div>
            </div>
          </bk-form-item>
        </template>
        <div class="bk-form-footer" v-show="!isFormLoading">
          <bk-button
            theme="primary"
            :disabled="!validateStatus"
            :loading="submitStatus"
            @click.stop.prevent="addIndexHandler"
            class="mr10">
            {{$t('indexSetList.affirm')}}
          </bk-button>
          <bk-button theme="default" @click="cancelHandler">{{$t('indexSetList.cancel')}}</bk-button>
        </div>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import selectWrapper from '@/components/common/selectWrapper';

export default {
  name: 'selectSource',
  components: {
    selectWrapper,
  },
  props: {
    scenarioId: [String, Number],
    sourceId: [String, Number],
    sourceName: {
      type: String,
      default: '',
    },
    timeIndex: {
      type: Object,
      default: () => ({
        time_format: '',
        time_field_type: '',
        time_field: '',
      }),
    },
    isEdit: {
      type: Boolean,
      default: false,
    },
    isLoading: {
      type: Boolean,
      default: true,
    },
    indexes: {
      type: Array,
      default: () => [],
    },
    indexSetId: [String, Number],
  },
  data() {
    return {
      isFormLoading: false, // 新增索引弹窗表单loading
      timeDate: '',
      nextDataTime: {},
      reloadListTable: false,
      selectScenarioId: this.scenarioId,
      selectSourceId: this.sourceId,
      selectIndexs: this.indexes,
      selectedSourceName: this.sourceName,
      tableConfig: {
        es: {
          data: {},
        },
      },
      defaultConfig: {
        data: [],
        size: 'small',
      },
      reloadTable: false,
      indexList: {},
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      timeFields: [
        { field_name: '秒（second）', field_id: 'second' },
        { field_name: '毫秒（millisecond）', field_id: 'millisecond' },
        { field_name: '微秒（microsecond）', field_id: 'microsecond' },
      ],
      selectedIndexId: [],
      scenarioList: [],
      showAddIndex: false,
      showAddOutIndex: false,
      indexParams: {
        bk_biz_id: '',
        result_table_id: '',
        time_field: '',
        time_format: '',
      },
      isDisabled: {
        biz: false,
        source: false,
      },
      bizList: [],
      indexFields: [],
      sourceList: [],
      rules: {
        bk_biz_id: [
          {
            required: true,
            trigger: 'change',
          },
        ],
        result_table_id: [
          {
            required: true,
            trigger: 'change',
          },
        ],
        time_field: [
          {
            required: true,
            trigger: 'change',
          },
          {
            validator: this.checkName,
            message: '时间字段需要保持一致',
            trigger: 'change',
          },
        ],
        time_format: [
          {
            required: true,
            trigger: 'change',
          },
        ],
      },
      validateStatus: false,
      submitStatus: false,
      indexErrorText: '',
      isIndexSearchLoading: false,
    };
  },
  computed: {
    ...mapState({
      currentProject: state => state.projectId,
      bkBizId: state => state.bkBizId,
      bkBizList: state => state.bkBizList,
    }),
    // es列表条数显示
    showTableIndex() {
      const show = this.indexList[this.selectScenarioId] ? this.indexList[this.selectScenarioId].length > 0 : false;
      return show;
    },
    showIndexList() {
      this.pagination.count = this.indexList[this.selectScenarioId] ? this.indexList[this.selectScenarioId].length : '';
      const start = (this.pagination.current - 1) * this.pagination.limit;
      const end = Math.min(this.indexList[this.selectScenarioId] ? this.indexList[this.selectScenarioId].length : '', this.pagination.current * this.pagination.limit);
      const pageFilter = this.indexList[this.selectScenarioId] ? this.indexList[this.selectScenarioId].slice(start, end) : '';
      this.reloadListTable = false;
      return pageFilter;
    },
    longData() {
      let longData;
      this.indexFields.forEach((item) => {
        if (item.field_name === this.indexParams.time_field) {
          this.timeIndex.time_field_type = item.field_type;
          this.timeIndex.time_field = item.field_name;
          longData = item.field_type === 'long';
        }
      });
      return longData;
    },
    // 根据权限排序后的列表
    sortedSourceList() {
      const s1 = [];
      const s2 = [];
      for (const item of this.sourceList) {
        // eslint-disable-next-line camelcase
        if (item.permission?.manage_es_source) {
          s1.push(item);
        } else {
          s2.push(item);
        }
      }
      return s1.concat(s2);
    },
    sortedLogIndexList() {
      const s1 = [];
      const s2 = [];
      for (const item of (this.indexList.log || [])) {
        // eslint-disable-next-line camelcase
        if (item.permission?.manage_collection) {
          s1.push(item);
        } else {
          s2.push(item);
        }
      }
      return s1.concat(s2);
    },
  },
  watch: {
    isLoading(val) {
      val === false && this.initConfig();
    },
    // scenarioId (val) {
    //     this.selectScenarioId !== val && this.selectScenarioId = val
    // },
    selectScenarioId(val) {
      this.bizList = this.bkBizList;
      this.indexParams.bk_biz_id = this.bkBizId;
      if (val === 'es') {
        this.sourceList.length === 0 && this.getSourceList();
      }
      this.scenarioId !== val && this.$emit('update:scenarioId', val);
    },
    showTableIndex(val) {
      if (val) {
        this.indexParams.time_field = this.timeIndex.time_field;
        this.indexParams.time_format = this.timeIndex.time_format === 'second' ? '秒（second）' : this.timeIndex.time_format === 'millisecond' ? '毫秒（millisecond）' : '微秒（microsecond）';
      }
    },
    selectSourceId(val) {
      this.sourceId !== val && this.$emit('update:sourceId', val);
    },
    'indexParams.time_field'(val) {
      val && this.checkValidateStatus();
    },
    'timeIndex.time_format'(val) {
      val && this.checkValidateStatus();
    },
    sourceName(val) {
      this.selectedSourceName = val;
    },
    indexes(val) {
      if (val.length === 0) {
        this.timeDate = '';
        this.timeIndex.time_format = '';
        this.timeIndex.time_field_type = '';
      } else {
        this.timeDate = val[0].time_field;
      }
    },
  },
  created() {
    this.getScenario();
  },
  methods: {
    /**
             * 编辑索引集时，初始化数据配置
             * @return {[type]} [description]
             */
    initConfig() {
      this.selectScenarioId = this.scenarioId;
      this.selectSourceId = this.sourceId;
      this.selectIndexs = this.indexes;
      this.selectedSourceName = this.sourceName;
      this.tableConfig !== {} && (this.tableConfig[this.selectScenarioId].data = this.indexes);
      if (this.isEdit) {
        this.indexes.forEach((item) => {
          this.selectedIndexId.push(item.result_table_id);
        });
        this.changeStatus();
      } else {
        // 默认选择第一个接入场景
        !this.selectScenarioId
         && this.scenarioList.length > 0
          && (this.selectScenarioId = this.scenarioList[0].scenario_id);
      }
    },
    /**
             * 如果result_table_id为空，在光标后自动追加*
             * @return {[type]} [description]
             */
    initRtId(value, event) {
      if (!this.indexParams.result_table_id) {
        this.indexParams.result_table_id = '*';
        setTimeout(() => {
          event.target.setSelectionRange(0, 0);
        }, 50);
      }
    },
    /**
             * 获取接入场景
             */
    getScenario() {
      this.$http.request('/meta/scenario', {}).then((res) => {
        this.scenarioList = res.data;
        // 初始化各个接入场景索引表格配置
        this.scenarioList.forEach((item) => {
          this.tableConfig[item.scenario_id] = JSON.parse(JSON.stringify(this.defaultConfig));
          // this.indexList[item.scenario_id] = []
          this.$set(this.indexList, item.scenario_id, []);
        });
        this.selectScenarioId !== '' && (this.tableConfig[this.selectScenarioId].data = this.indexes);
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    /**
             * 获取外部数据源
             * @return {[type]} [description]
             */
    getSourceList() {
      let url = '/source/list';
      if (this.selectScenarioId === 'es') {
        url = '/source/logList';
      }
      this.$http.request(url, {
        query: {
          bk_biz_id: this.bkBizId,
          scenario_id: this.selectScenarioId,
        },
      }).then((res) => {
        this.sourceList = res.data;
        this.changeStatus();
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    /**
             * 监听es接入场景下result_table_id变更，获取匹配索引列表
             * @return {[type]} [description]
             */
    getSourceIndexList() {
      this.indexList[this.selectScenarioId] = [];
      this.indexFields = [];
      this.checkValidateStatus();

      const val = this.indexParams.result_table_id;
      if (val && val !== '*') {
        this.indexErrorText = '';
        this.getIndexList();
        this.getIndexInfo();
      }
    },
    /**
             * 获取索引列表
             */
    async getIndexList() {
      try {
        const res = await this.$http.request('/resultTables/list', {
          query: {
            scenario_id: this.selectScenarioId,
            bk_biz_id: this.indexParams.bk_biz_id,
            storage_cluster_id: this.selectSourceId,
            result_table_id: this.indexParams.result_table_id,
          },
        });
        this.indexList[this.selectScenarioId] = res.data;
        if (res.data.length === 0) {
          this.$bkMessage({
            theme: 'warning',
            message: '当前业务下没有索引',
            delay: 1500,
          });
        }
      } catch (e) {
        console.warn(e);
        this.indexErrorText += e.message;
      }
    },
    // 采集接入新增索引选择采集项-申请权限
    async applyCollectorAccess(option) {
      try {
        this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
        this.isFormLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['manage_collection'],
          resources: [{
            type: 'collection',
            id: option.collector_config_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.isFormLoading = false;
      }
    },
    // 第三方ES选择数据源-申请权限
    async applyESAccess(option) {
      try {
        this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
        this.$emit('loading', true);
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['manage_es_source'],
          resources: [{
            type: 'es_source',
            id: option.storage_cluster_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$emit('loading', false);
      }
    },
    /**
             * 获取索引详情
             */
    async getIndexInfo() {
      if (!this.indexParams.result_table_id) return;
      try {
        this.checkValidateStatus();
        this.reloadListTable = true;
        this.isIndexSearchLoading = true;
        const res = await this.$http.request('/resultTables/info', {
          params: {
            result_table_id: this.indexParams.result_table_id,
          },
          query: {
            scenario_id: this.selectScenarioId,
            bk_biz_id: this.indexParams.bk_biz_id,
            storage_cluster_id: this.selectSourceId,
          },
        });
        this.indexFields = res.data && res.data.fields;
        if (this.indexFields.length) {
          this.indexParams.time_field = this.timeDate;
        }
      } catch (e) {
        console.warn(e);
        this.indexErrorText += e.message;
      } finally {
        this.reloadListTable = false;
        this.isIndexSearchLoading = false;
      }
    },
    /**
             * 分页变换
             * @param  {Number} page 当前页码
             * @return {[type]}      [description]
             */
    handlePageChange(page) {
      this.pagination.current = page;
    },
    /**
             * 获取业务列表
             * @return {[type]} [description]
             */
    getBizList() {
      this.$http.request('/biz/list', {}).then((res) => {
        this.bizList = res.data;
        this.indexParams.bk_biz_id = this.bkBizId;
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    /**
             * 删除索引
             * @param  {Object} set 索引对象
             */
    remove(row) {
      const index = this.tableConfig[this.selectScenarioId].data.indexOf(row);
      if (index !== -1) {
        this.tableConfig[this.selectScenarioId].data.splice(index, 1);
        this.selectedIndexId.splice(this.selectedIndexId.indexOf(row.result_table_id), 1);
        this.changeStatus();
      }
    },
    handleClick() {
      if (this.selectScenarioId === 'bkdata' || this.selectScenarioId === 'log') {
        this.indexParams.bk_biz_id = this.bkBizId;
        this.getIndexList();
        this.showAddIndex = true;
      } else if (this.selectScenarioId === 'es') {
        if (this.selectSourceId) {
          this.showAddIndex = true;
        } else {
          const h = this.$createElement;
          this.$bkMessage({
            message: h('p', {
              style: {
                textAlign: 'center',
              },
            }, this.$t('indexSetList.Please_select')),
            offsetY: 80,
          });
        }
      }
    },
    selectedSource(value, option) {
      this.selectedSourceName = option.name;
    },
    addIndexHandler() {
      this.$refs.validateForm.validate().then(() => {
        this.submitStatus = true;
        this.$emit('update:timeIndex', this.timeIndex);
        // eslint-disable-next-line camelcase
        const append_basic = {
          index: this.indexParams.result_table_id,
        };
        if (this.selectScenarioId === 'es') {
          append_basic.time_field = this.timeIndex.time_field;
          append_basic.time_field_type = this.timeIndex.time_field_type;
        }
        const basicIndices = this.tableConfig[this.selectScenarioId].data.map(item => item.result_table_id);
        const data = {
          scenario_id: this.selectScenarioId,
          storage_cluster_id: this.selectSourceId,
          basic_indices: basicIndices,
          append_index: append_basic,
        };
        if (!data.basic_indices.length) {
          delete data.basic_indices;
        } else if (this.selectScenarioId === 'es') {
          data.basic_indices = basicIndices.map(index => ({
            index,
            time_field: this.timeIndex.time_field,
            time_field_type: this.timeIndex.time_field_type,
          }));
        } else {
          data.basic_indices = basicIndices.map(index => ({ index }));
        }
        if (this.selectScenarioId !== 'es') {
          delete data.storage_cluster_id;
        }
        this.$http.request('/resultTables/adapt', {
          data,
        }).then(() => {
          if (this.selectScenarioId === 'bkdata' || this.selectScenarioId === 'log' || this.selectScenarioId === 'es') {
            this.tableConfig[this.selectScenarioId].data.unshift(JSON.parse(JSON.stringify(this.indexParams)));
            if (this.selectScenarioId === 'es') {
              this.nextDataTime = this.tableConfig[this.selectScenarioId].data[0];
            }
            this.selectedIndexId.push(this.indexParams.result_table_id);
            this.timeDate = JSON.parse(JSON.stringify(this.indexParams.time_field));
            this.resetIndexParams();
            this.changeStatus();
          }
          this.showAddIndex = false;
        })
          .catch((err) => {
            console.warn(err);
            this.validateStatus = false;
          })
          .finally(() => {
            this.submitStatus = false;
          });
      }, () => {});
      return false;
    },
    cancelHandler() {
      this.showAddIndex = false;
      this.resetIndexParams();
    },
    filterBizName(bizId) {
      const matchBiz = bizId ? this.bkBizList.find(biz => String(biz.bk_biz_id) === String(bizId)) : [];
      // eslint-disable-next-line camelcase
      return matchBiz?.bk_biz_name || '--';
    },
    /**
             * 变更数据源选择状态
             * @return {[type]} [description]
             */
    changeStatus() {
      if (this.selectScenarioId === 'bkdata' || this.selectScenarioId === 'log') {
        this.isDisabled.biz = this.tableConfig[this.selectScenarioId].data.length > 0;
      } else if (this.selectScenarioId === 'es') {
        this.isDisabled.source = this.sourceList.length > 0 && this.tableConfig[this.selectScenarioId].data.length > 0;
        this.selectSourceId = (this.tableConfig[this.selectScenarioId].data.length > 0 && this.selectSourceId) || '';
      }
      this.$emit('update:indexes', this.tableConfig[this.selectScenarioId].data);
    },
    /**
             * 检测验证状态
             * @return {[type]} [description]
             */
    checkValidateStatus() {
      if (this.selectScenarioId === 'bkdata' || this.selectScenarioId === 'log') {
        this.validateStatus = this.indexParams.bk_biz_id && this.indexParams.result_table_id;
      } else if (this.selectScenarioId === 'es') {
        this.validateStatus = this.selectSourceId && this.indexParams.result_table_id && this.indexParams.result_table_id !== '*' && this.indexParams.time_field;
        if (this.longData) {
          this.validateStatus = this.validateStatus && this.timeIndex.time_format;
        }
      }
    },
    /**
             * 重置新增索引参数值
             * @return {[type]} [description]
             */
    resetIndexParams() {
      this.indexFields = [];
      this.indexParams.result_table_id = '';
      this.indexParams.fields = '';
      if (this.selectScenarioId === 'es') {
        this.indexList[this.selectScenarioId] = [];
        this.indexParams.bk_biz_id = '';
        this.indexParams.time_field = '';
      }
    },
    checkName(val) {
      // eslint-disable-next-line camelcase
      let time_field;
      if (!this.timeDate) return true;
      if (val === this.timeDate) {
        // eslint-disable-next-line camelcase
        time_field = true;
      } else {
        // eslint-disable-next-line camelcase
        time_field = false;
      }
      // eslint-disable-next-line camelcase
      return time_field;
    },
  },
};
</script>

<style lang="scss" scoped>
  .source-box {
    padding: 20px;
    min-height: 180px;
    border: 1px solid #dcdee5;

    .bk-form-radio {
      margin-right: 10px;
    }
  }

  /deep/ .bk-page-count-right {
    display: none;
  }

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

  /deep/ .bk-form-item.is-error .bk-select {
    border-color: #ff5656;
    color: #ff5656;
  }

  .border-class {
    border: 1px solid #ccc;
    height: 263px;
    overflow: hidden;
    width: 80%
  }

  .index-info {
    width: 100%;
    height: 265px;
    overflow-y: auto;
    position: relative;
  }

  /*滚动条样式*/
  .index-info::-webkit-scrollbar {
    width: 4px;
  }

  .index-info::-webkit-scrollbar-thumb {
    border-radius: 10px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, .2);
    background: rgba(0, 0, 0, .2);
  }

  .index-info::-webkit-scrollbar-track {
    box-shadow: inset 0 0 5px rgba(0, 0, 0, .2);
    border-radius: 0;
    background: rgba(0, 0, 0, .1);
  }

  .add-index-input-container {
    position: relative;
    width: 435px;

    .king-button {
      position: absolute;
      top: 0;
      right: -90px;
    }

    .error-tips-container {
      position: absolute;
      top: 0;
      right: -122px;
    }

    .log-icon {
      font-size: 18px;
      cursor: pointer;
      color: #ea3636;
    }

    .input-tips {
      color: #aaa;
    }
  }

  .bk-form-footer {
    margin: 20px -22px -11px;
    padding: 15px 20px 0;
    text-align: right;
    border-top: 1px solid #ccc;
  }

  .result-tips {
    font-size: 12px;
    color: #2dcb56;
    padding-left: 12px;
  }
</style>
