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
  <section class="step-field-container" data-test-id="addNewCollectionItem_section_fieldExtractionBox">
    <auth-container-page v-if="isCleanField && authPageInfo" :info="authPageInfo"></auth-container-page>
    <div class="step-field" v-bkloading="{ isLoading: basicLoading }" v-else>
      <bk-alert v-if="!isCleanField && !isTempField && !isSetEdit" class="king-alert" type="info">
        <div slot="title" class="slot-title-container">{{$t('通过字段清洗，可以格式化日志内容方便检索、告警和分析。')}}</div>
      </bk-alert>
      <bk-alert v-if="isSetEdit" class="king-alert" type="info">
        <div slot="title" class="slot-title-container">{{$t('将过滤后的日志采集上来后，日志检索模块可进行日志内容格式化，方便检索和分析。')}}</div>
      </bk-alert>
      <div class="collector-select" v-show="isCleanField && !isSetEdit">
        <label>{{ $t('采集项') }}</label>
        <bk-select
          style="width: 520px;"
          :clearable="false"
          searchable
          :disabled="isEditCleanItem"
          v-model="cleanCollector"
          @change="handleCollectorChange">
          <bk-option
            v-for="option in cleanCollectorList"
            :key="option.collector_config_id"
            :id="option.collector_config_id"
            :name="option.collector_config_name">
            <div
              v-if="!(option.permission && option.permission[authorityMap.MANAGE_COLLECTION_AUTH])"
              class="option-slot-container no-authority"
              @click.stop>
              <span class="text">
                <span>{{ option.collector_config_name }}</span>
                <span style="color: #979ba5;">（{{ `#${option.collector_config_id}` }}）</span>
              </span>
              <span class="apply-text" @click="applyProjectAccess(option)">{{ $t('申请权限') }}</span>
            </div>
            <div v-else v-bk-overflow-tips class="option-slot-container">
              <span>{{ option.collector_config_name }}</span>
              <span style="color: #979ba5;">（{{ `#${option.collector_config_id}` }}）</span>
            </div>
          </bk-option>
        </bk-select>
      </div>
      <div class="step-field-title">
        <div>{{$t('原始日志')}}</div>
        <div class="text-nav" v-if="!isTempField">
          <span
            @click="refreshClick"
            data-test-id="fieldExtractionBox_span_originalLogRefresh"
          >{{$t('刷新')}}</span>
          <span
            @click="chickFile"
            data-test-id="fieldExtractionBox_span_viewReportingLog"
          >{{$t('查看上报日志')}}</span>
        </div>
      </div>
      <template>
        <div class="log-style">
          <bk-input
            placeholder=" "
            data-test-id="fieldExtractionBox_input_originalLog"
            :type="'textarea'"
            :rows="3"
            :input-style="{
              'background-color': '#313238',
              height: '82px',
              'line-height': '24px',
              color: '#C4C6CC',
              borderRadius: '2px'
            }"
            v-model.trim="logOriginal">
          </bk-input>
        </div>
        <bk-sideslider
          class="locker-style"
          transfer
          :is-show.sync="defaultSettings.isShow"
          :quick-close="true"
          :modal="false"
          :width="596">
          <div slot="header">
            {{$t('上报日志详情')}}
            <span @click="copyText(JSON.stringify(jsonText))">{{$t('复制')}}</span>
          </div>
          <div class="p20 json-text-style" slot="content">
            <VueJsonPretty :deep="5" :data="jsonText" />
          </div>
        </bk-sideslider>
      </template>

      <section class="field-method">
        <div :class="{ 'field-method-head': true, 'field-template-head': isTempField }">
          <h4 class="field-method-title fl field-text">{{ $t('字段清洗') }}</h4>
          <bk-tab
            v-if="!isTempField"
            :active.sync="activePanel"
            type="unborder-card"
            ext-cls="field-method-tab">
            <bk-tab-panel
              v-for="(panel, index) in panels"
              v-bind="panel"
              :key="index">
            </bk-tab-panel>
          </bk-tab>
        </div>

        <!-- 基础清洗 -->
        <div v-show="activePanel === 'base'">
          <!-- 模式选择 -->
          <div class="field-step field-method-step" style="margin-top: 20px;">
            <div class="step-head">
              <div>
                <span class="step-text">{{ $t('模式选择') }}</span>
                <span
                  v-if="!isTempField"
                  data-test-id="fieldExtractionBox_span_applyTemp"
                  :class="{
                    'template-text': true,
                    'template-disabled': (isCleanField && !cleanCollector) || isSetDisabled
                  }"
                  @click="openTemplateDialog(false)">
                  <span class="log-icon icon-daoru"></span>
                  {{ $t('应用模版') }}
                </span>
              </div>
              <p class="documentation button-text" v-if="docUrl" @click="handleGotoLink('logExtract')">
                <span>{{$t('说明文档')}}</span> <span class="log-icon icon-jump"></span>
              </p>
            </div>

            <!-- 选择字段过滤方法 -->
            <div class="field-button-group">
              <div class="bk-button-group">
                <bk-button
                  v-for="option in globalsData.etl_config"
                  :key="option.id"
                  :disabled="(isCleanField && !cleanCollector) || isSetDisabled"
                  @click="params.etl_config = option.id"
                  :class="params.etl_config === option.id ? 'is-selected' : ''"
                  :data-test-id="`fieldExtractionBox_button_filterMethod${option.id}`">
                  {{ option.name }}
                </bk-button>
              </div>

              <template v-if="params.etl_config === 'bk_log_regexp'">
                <span
                  v-bk-tooltips="{ allowHtml: true, placement: 'right', content: '#reg-tip' }"
                  style="margin-left: 10px;color: #979ba5; cursor: pointer;"
                  class="log-icon icon-info-fill fl"></span>
                <div id="reg-tip">
                  <p>{{$t('正则表达式(golang语法)需要匹配日志全文，如以下DEMO将从日志内容提取请求时间与内容')}}</p>
                  <p>{{$t(' - 日志内容：[2006-01-02 15:04:05] content')}}</p>
                  <p>{{$t(' - 表达式：')}}\[(?P&lt;request_time>[^]]+)\] (?P&lt;content>.+)</p>
                </div>
              </template>
            </div>

            <!-- 分隔符选择 -->
            <bk-select
              style="width: 320px; margin-top: 20px;"
              v-if="params.etl_config === 'bk_log_delimiter'"
              data-test-id="fieldExtractionBox_div_selectSeparator"
              :disabled="isExtracting"
              :clearable="false"
              v-model="params.etl_params.separator">
              <bk-option
                v-for="option in globalsData.data_delimiter"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>

            <!-- 正则表达式输入框 -->
            <div class="field-method-regex" v-if="params.etl_config === 'bk_log_regexp'">
              <div class="textarea-wrapper">
                <pre class="mimic-textarea">
                {{ params.etl_params.separator_regexp }}
              </pre>
                <bk-input
                  class="regex-textarea"
                  data-test-id="fieldExtractionBox_input_regular"
                  :placeholder="defaultRegex"
                  :type="'textarea'"
                  v-model="params.etl_params.separator_regexp">
                </bk-input>
              </div>
              <p class="format-error" v-if="!isJsonOrOperator && !formatResult">{{ $t('格式解析失败，可以尝试其他提取方法') }}</p>
            </div>
          </div>

          <!-- 调试设置字段 -->
          <div class="field-step field-method-step" data-test-id="fieldExtraction_div_debugSetField">
            <div class="step-head">
              <span class="step-text">{{ $t('调试设置字段') }}</span>
              <div class="">
                <bk-button
                  class="fl debug-btn"
                  theme="primary"
                  :disabled="!logOriginal || isExtracting || !showDebugBtn || isSetDisabled"
                  @click="debugHandler"
                  data-test-id="fieldExtractionBox_button_debugging">
                  {{ $t('调试') }}
                </bk-button>
                <p class="format-error ml10 fl" v-if="isJsonOrOperator && !formatResult">
                  {{ $t('格式解析失败，可以尝试其他提取方法') }}
                </p>
              </div>
            </div>

            <!-- 调试字段表格 -->
            <template>
              <div class="field-method-result">
                <field-table
                  ref="fieldTable"
                  :key="renderKey"
                  :is-extracting="isExtracting"
                  :is-temp-field="isTempField"
                  :is-edit-json="isUnmodifiable"
                  :is-set-disabled="isSetDisabled"
                  :extract-method="formData.etl_config"
                  :deleted-visible="deletedVisible"
                  :fields="formData.fields"
                  :retain-original-value="formData.etl_params.retain_original_text"
                  @deleteVisible="visibleHandle"
                  @handleKeepLog="handleKeepLog"
                  @standard="dialogVisible = true"
                  @reset="getDetail">
                </field-table>
              </div>
            </template>
          </div>

          <!-- 调试设置字段 -->
          <div v-if="isClearTemplate" class="field-step field-method-step">
            <div class="step-head">
              <span class="step-text">{{ $t('可见范围') }}</span>
            </div>

            <template>
              <div class="field-method-result visible-select">
                <bk-radio-group v-model="formData.visible_type">
                  <bk-radio
                    class="scope-radio"
                    v-for="item of visibleScopeSelectList"
                    :key="item.id"
                    :value="item.id">
                    {{item.name}}
                  </bk-radio>
                </bk-radio-group>
                <bk-select
                  v-model="visibleBkBiz"
                  v-show="scopeValueType"
                  searchable
                  multiple
                  display-tag>
                  <bk-option
                    v-for="item in mySpaceList"
                    :key="item.space_uid"
                    :id="item.bk_biz_id"
                    :name="item.space_full_code_name">
                    <div class="space-code-option">
                      <span class="code-name" :title="item.space_full_code_name">{{item.space_full_code_name}}</span>
                      <div class="list-item-right">
                        <span :class="['list-item-tag', 'light-theme', item.space_type_id || 'other-type']">
                          {{item.space_type_name}}
                        </span>
                        <span :class="`${visibleBkBiz.includes(item.bk_biz_id) && 'bk-icon icon-check-1'}`"></span>
                      </div>
                    </div>
                  </bk-option>
                </bk-select>
              </div>
            </template>
          </div>
        </div>

        <!-- 高级清洗 -->
        <div v-show="activePanel === 'advance'">
          <div class="advance-clean-step-container">
            <div class="step-item">
              <div class="image-content">
                <img src="../../images/clean-image1.png" alt="">
              </div>
              <div class="step-description">
                <span class="step-num">1</span>
                <span class="description-text">{{ $t('高级清洗只能应用于日志平台采集的日志，会在链路上分发给计算平台进行更复杂的数据处理。') }}</span>
              </div>
            </div>
            <span class="bk-icon icon-angle-double-right-line"></span>
            <div class="step-item">
              <div class="image-content">
                <img src="../../images/clean-image2.png" alt="">
              </div>
              <div class="step-description">
                <span class="step-num">2</span>
                <span class="description-text">
                  <i18n path="选择了高级字段提取能力后，会跳转到计算平台进行更多的字段处理，计算平台提供13种清洗算法。具体的使用方法可查看{0}">
                    <a class="link" @click="handleGotoLink('bkBase')">
                      {{ $t('计算平台文档') }}
                      <span class="log-icon icon-lianjie"></span>
                    </a>
                  </i18n>
                </span>
                <p class="remark">{{ $t('注： 同一个日志可以进行多次清洗。') }}</p>
              </div>
            </div>
            <span class="bk-icon icon-angle-double-right-line"></span>
            <div class="step-item">
              <div class="image-content">
                <img src="../../images/clean-image3.png" alt="">
              </div>
              <div class="step-description">
                <span class="step-num">3</span>
                <span class="description-text">{{ $t('清洗完并且存储到ES后，日志平台会识别到对应的索引创建日志平台的索引集，后续可以直接在检索和监控中使用。') }}</span>
                <p class="remark">{{ $t('注：如果清洗后存储成其他类型，将无法关联上。') }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="form-button">
        <!-- 上一步 -->
        <bk-button
          v-if="!isCleanField && !isTempField && !isSetEdit"
          theme="default"
          data-test-id="fieldExtractionBox_button_previousPage"
          :title="$t('上一步')"
          class="mr10"
          :disabled="isLoading"
          @click="prevHandler">
          {{$t('上一步')}}
        </bk-button>
        <!-- 前往高级清洗 -->
        <log-button
          v-if="activePanel === 'advance'"
          theme="primary"
          data-test-id="fieldExtractionBox_button_goToAdvancedCleaning"
          :tips-conf="advanceDisableTips"
          :button-text="$t('前往高级清洗')"
          :disabled="advanceDisable"
          @on-click="advanceHandler">
        </log-button>
        <!-- 下一步/完成 -->
        <bk-button
          v-if="activePanel === 'base' && !isTempField"
          theme="primary"
          data-test-id="fieldExtractionBox_button_nextPage"
          @click.stop.prevent="finish(true)"
          :loading="isLoading"
          :disabled="!collectProject || !showDebugBtn || !hasFields || isSetDisabled">
          {{isSetEdit ? $t('保存') : $t('下一步')}}
        </bk-button>
        <!-- 跳过 -->
        <bk-button
          v-if="!isTempField && !isSetEdit"
          theme="default"
          :title="$t('取消')"
          class="ml10"
          data-test-id="fieldExtractionBox_button_Pass"
          @click="handleSkip"
          :disabled="isLoading">
          {{$t('跳过')}}
        </bk-button>
        <!-- 保存模板 -->
        <bk-button
          v-if="activePanel === 'base'"
          theme="default"
          class="ml10"
          data-test-id="fieldExtractionBox_button_saveTemplate"
          :disabled="!hasFields || isSetDisabled"
          @click="openTemplateDialog(true)">
          {{$t('保存模板')}}
        </bk-button>
        <!-- 日志清洗 保存模板 取消 -->
        <bk-button
          v-if="isCleanField || isTempField"
          theme="default"
          class="ml10"
          data-test-id="fieldExtractionBox_button_cancelSaveTemplate"
          @click="handleCancel(false)">
          {{isSetEdit ? $t('重置') : $t('取消')}}
        </bk-button>
        <!-- 检索字段提取设置 重置 -->
        <bk-button
          v-if="isSetEdit"
          theme="default"
          class="ml10"
          data-test-id="fieldExtractionBox_button_cancelSaveTemplate"
          :disabled="!collectProject || !showDebugBtn || !hasFields || isSetDisabled"
          @click="setDetail(setId)">
          {{$t('重置')}}
        </bk-button>
      </div>

      <bk-dialog
        v-model="dialogVisible"
        width="1012"
        :header-position="'left'"
        :mask-close="false"
        :draggable="false"
        :show-footer="false"
        :title="$t('查看内置字段')">
        <div class="standard-field-table">
          <field-table
            v-if="dialogVisible"
            :table-type="'preview'"
            :extract-method="formData.etl_config"
            :fields="copyBuiltField"
            :json-text="copysText">
          </field-table>
        </div>
      </bk-dialog>

      <!-- 选择模版 -->
      <bk-dialog
        v-model="templateDialogVisible"
        width="480"
        :header-position="'left'"
        :mask-close="false"
        :draggable="false"
        :title="isSaveTempDialog ? $t('保存模板') : $t('选择模版')"
        :confirm-fn="handleTemplConfirm">
        <div class="template-content">
          <div v-if="isSaveTempDialog">
            <label style="color: #63656e;">模板名称</label>
            <bk-input v-model="saveTempName" style="margin-top: 8px"></bk-input>
          </div>
          <bk-select v-else v-model="selectTemplate" data-test-id="fieldExtractionBox_select_selectTemplate">
            <bk-option
              v-for="option in templateList"
              :key="option.clean_template_id"
              :id="option.clean_template_id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </div>
      </bk-dialog>
    </div>
  </section>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import fieldTable from './field-table';
import AuthContainerPage from '@/components/common/auth-container-page';
import { projectManages } from '@/common/util';
import * as authorityMap from '../../common/authority-map';

export default {
  components: {
    fieldTable,
    AuthContainerPage,
  },
  props: {
    operateType: String,
    curStep: {
      type: Number,
      default: 1,
    },
    collectorId: String,
    isCleanField: Boolean,
    isTempField: Boolean,
    isSetEdit: Boolean,
    setId: Number,
    setDisabled: Boolean,
  },
  data() {
    return {
      // isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      refresh: false,
      // eslint-disable-next-line no-useless-escape
      defaultRegex: '(?P<request_ip>[\d\.]+)[^[]+\[(?P<request_time>[^]]+)\]',
      isLoading: false,
      basicLoading: false,
      isUnmodifiable: false,
      fieldType: '',
      deletedVisible: true,
      copysText: {},
      jsonText: {},
      defaultSettings: {
        isShow: false,
      },
      logOriginal: '',
      params: { // 此处为可以变动的数据，如果调试成功，则将此条件保存至formData，保存时还需要对比此处与formData是否有差异
        etl_config: 'bk_log_text',
        etl_params: {
          separator_regexp: '',
          separator: '',
        },
      },
      formData: { // 最后一次正确的结果，保存以此数据为准
        table_id: '',
        etl_config: 'bk_log_text',
        etl_params: {
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
        },
        fields: [],
        visible_type: 'current_biz', // 可见范围单选项
        visible_bk_biz: [], // 多个业务
      },
      copyBuiltField: [],
      formatResult: true, // 验证结果是否通过
      rules: {
        table_id: [{
          required: true,
          trigger: 'blur',
        }, {
          max: 50,
          trigger: 'blur',
        }, {
          min: 5,
          trigger: 'blur',
        }, {
          regex: /^[A-Za-z0-9_]+$/,
          trigger: 'blur',
        }],
      },
      isExtracting: false,
      dialogVisible: false,
      rowTemplate: {
        alias_name: '',
        description: '',
        field_type: '',
        is_analyzed: false,
        is_built_in: false,
        is_delete: false,
        is_dimension: false,
        is_time: false,
        value: '',
        option: {
          time_format: '',
          time_zone: '',
        },
      },
      activePanel: 'base',
      panels: [
        { name: 'base', label: this.$t('基础') },
        { name: 'advance', label: this.$t('高级') },
      ],
      selectTemplate: '', // 应用模板
      saveTempName: '',
      templateList: [], // 模板列表
      templateDialogVisible: false,
      isSaveTempDialog: false,
      cleanCollector: '', // 日志清洗选择的采集项
      cleanCollectorList: [],
      renderKey: 0, // key-changing
      authPageInfo: null,
      docCenterUrl: window.BK_DOC_DATA_URL,
      visibleScopeSelectList: [ // 可见范围单选列表
        { id: 'current_biz', name: this.$t('当前空间可见') },
        { id: 'multi_biz', name: this.$t('多空间选择') },
        { id: 'all_biz', name: this.$t('全平台') },
      ],
      visibleBkBiz: [], // 多业务选择id列表
      cacheVisibleList: [], // 缓存多业务选择下拉框
      visibleIsToggle: false,
      docUrl: window.BK_ETL_DOC_URL,
    };
  },
  computed: {
    ...mapState({
      mySpaceList: state => state.mySpaceList,
    }),
    ...mapGetters({
      bkBizId: 'bkBizId',
      spaceUid: 'spaceUid',
      curCollect: 'collect/curCollect',
      globalsData: 'globals/globalsData',
    }),
    authorityMap() {
      return authorityMap;
    },
    isJsonOrOperator() {
      return this.params.etl_config === 'bk_log_json' || this.params.etl_config === 'bk_log_delimiter';
    },
    hasFormat() { // 最后一次正确的fileds结果
      return this.formData.fields.length;
    },
    showDebugBtn() {
      const methods = this.params.etl_config;
      if (!methods || methods === 'bk_log_text') return false;
      if (methods === 'bk_log_delimiter') {
        return this.params.etl_params.separator;
      }
      if (methods === 'bk_log_regexp') {
        return this.params.etl_params.separator_regexp !== '';
      }
      return true;
    },
    hasFields() {
      return this.formData.fields.length;
    },
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    isEditTemp() {
      return this.$route.name === 'clean-template-edit';
    },
    isEditCleanItem() {
      return this.$route.name === 'clean-edit' || this.isSetEdit;
    },
    advanceDisable() {
      return window.FEATURE_TOGGLE.scenario_bkdata !== 'on'
              || this.curCollect.bkdata_data_id === null
              || (this.isCleanField && !this.cleanCollector);
    },
    advanceDisableTips() {
      if (window.FEATURE_TOGGLE.scenario_bkdata !== 'on') {
        return '';
      }
      if (this.curCollect.bkdata_data_id === null) {
        return '';
      }
      return '';
    },
    unAuthBkdata() {
      return window.FEATURE_TOGGLE.scenario_bkdata !== 'on';
    },
    isSetDisabled() {
      return this.isSetEdit && this.setDisabled;
    },
    // 可见范围单选判断，禁用下拉框
    scopeValueType() {
      return this.formData.visible_type === 'multi_biz';
    },
    // 入口是否是清洗模板
    isClearTemplate() {
      return ['clean-template-create', 'clean-template-edit'].includes(this.$route.name);
    },
  },
  watch: {
    'formData.fields'() {
      this.renderKey = this.renderKey + 1;
    },
    'params.etl_config'() {
      this.formatResult = true;
    },
    // 切换可见范围时 恢复缓存或清空业务选择
    'formData.visible_type': {
      handler(val) {
        this.visibleBkBiz = val !== 'multi_biz' ? [] : JSON.parse(JSON.stringify(this.cacheVisibleList));
      },
    },
  },
  created() {
    if (this.unAuthBkdata) { // 未授权计算平台则禁用高级清洗
      this.panels[1].disabled = true;
      this.panels[1].renderLabel = (h) => {
        return h('div', {
          class: 'render-header',
        }, [
          h('span', {
            directives: [
              {
                name: 'bk-tooltips',
                value: this.$t('未部署基础计算平台，无法进行高级清洗'),
              },
            ],
          }, this.$t('高级')),
        ]);
      };
    }
  },
  async mounted() {
    // 清洗列表进入
    if (this.isCleanField) {
      this.initCleanItem();
      return;
    }

    // 清洗模板进入
    if (this.isTempField) {
      this.initCleanTemp();
      return;
    }

    // 检索字段提取进入
    if (this.isSetEdit) {
      if (this.setId) { // 可设置字段提取
        this.setDetail(this.setId);
      } else {
        setTimeout(() => {
          this.basicLoading = false;
        }, 10);
      }
      return;
    }

    // 采集项编辑进入
    await this.getDetail();
    const isClone = this.$route.query?.type === 'clone';
    const collectorID = isClone
      ? (this.$route.query?.collectorId || this.curCollect.collector_config_id)
      : this.curCollect.collector_config_id;
    this.getCleanStash(collectorID);
    this.getDataLog('init');
  },
  methods: {
    // 初始化清洗项
    initCleanItem() {
      this.basicLoading = true;
      const query = {
        bk_biz_id: this.bkBizId,
        have_data_id: 1,
      };
      if (!this.isEditCleanItem) {
        query.bkdata = true;
      }
      // 获取采集项列表
      this.$http.request('collect/getAllCollectors', { query }).then((res) => {
        const data = res.data;
        if (data.length) {
          this.cleanCollectorList = data;
          if (this.isEditCleanItem) {
            if (this.isSetEdit) {
              this.cleanCollector = this.setId;
            } else {
              this.cleanCollector = this.$route.params.collectorId;
            }
          } else this.basicLoading = false;
        } else this.basicLoading = false;
      })
        .catch(() => {
          this.basicLoading = false;
        });
    },
    // 初始化清洗模板详情
    initCleanTemp() {
      if (this.isEditTemp) { // 克隆与编辑获取模板详情
        const { templateId } = this.$route.params;
        this.basicLoading = true;
        this.$http.request('clean/templateDetail', {
          params: {
            clean_template_id: templateId,
          },
          query: {
            bk_biz_id: this.bkBizId,
          },
        }).then((res) => {
          if (res.data) {
            this.setTempDetail(res.data);
          }
        })
          .finally(() => {
            this.basicLoading = false;
          });
      } else {
        setTimeout(() => {
          this.basicLoading = false;
        }, 100);
      }
    },
    // 设置模板已有fields
    setTempDetail(data) {
      const {
        name,
        clean_type,
        etl_params,
        etl_fields,
        visible_type,
        visible_bk_biz_id: visibleBkBizList,
      } = data;
      this.saveTempName = name;
      /* eslint-disable */
      this.params.etl_config = clean_type
      Object.assign(this.params.etl_params, {
        separator_regexp: etl_params.separator_regexp || '',
        separator: etl_params.separator || ''
      })
      this.visibleBkBiz = visibleBkBizList;
      this.cacheVisibleList = visibleBkBizList;
      this.fieldType = clean_type
      /* eslint-enable */
      Object.assign(this.formData, {
        etl_config: this.fieldType,
        etl_params: Object.assign({
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
        }, etl_params ? JSON.parse(JSON.stringify(etl_params)) : {}), // eslint-disable-line
        fields: etl_fields,
        visible_type,
      });
    },
    // 高级清洗配置
    setAdvanceCleanTab(isAdvance) {
      if (isAdvance) {
        this.activePanel = 'advance';
        this.panels[0].disabled = true;
        this.panels[0].renderLabel = (h) => {
          return h('div', {
            class: 'render-header',
          }, [
            h('span', {
              directives: [
                {
                  name: 'bk-tooltips',
                  value: this.$t('当前采集项已配置基础清洗，无需重复配置'),
                },
              ],
            }, this.$t('基础')),
          ]);
        };
      } else {
        if (this.unAuthBkdata) return;
        this.activePanel = 'base';
        this.panels = [
          { name: 'base', label: this.$t('基础') },
          { name: 'advance', label: this.$t('高级') },
        ];
      }
    },
    debugHandler() {
      this.formData.fields.splice(0, this.formData.fields.length);
      this.requestEtlPreview();
    },
    // 字段提取
    fieldCollection(isCollect = false) {
      const {
        etl_config,
        fields,
        etl_params,
        visible_type,
      } = this.formData;
      this.isLoading = true;
      this.basicLoading = true;
      let data = {
        clean_type: etl_config,
        etl_params: {
          retain_original_text: etl_params.retain_original_text,
          separator_regexp: etl_params.separator_regexp,
          separator: etl_params.separator,
        },
        etl_fields: fields,
        visible_type,
      };
      /* eslint-disable */
      if (etl_config !== 'bk_log_text') {
        const etlParams = {
          retain_original_text: etl_params.retain_original_text
        }
        if (etl_config === 'bk_log_delimiter') {
          etlParams.separator = etl_params.separator
        }
        if (etl_config === 'bk_log_regexp') {
          etlParams.separator_regexp = etl_params.separator_regexp
        }
        data.etl_params = etlParams
        data.etl_fields = this.$refs.fieldTable.getData()
      }

      let requestUrl;
      const urlParams = {};
      if (this.isSetEdit) { // 检索设置 直接入库
        const { 
          table_id, storage_cluster_id, retention, storage_replies, allocation_min_days, view_roles 
        } = this.curCollect;
        urlParams.collector_config_id = this.curCollect.collector_config_id;
        data = {
          table_id,
          storage_cluster_id,
          retention,
          storage_replies,
          allocation_min_days,
          view_roles,
          etl_config,
          fields: data.etl_fields,
          etl_params,
        }
        requestUrl = 'collect/fieldCollection'
      } else if (isCollect) { // 缓存采集项清洗配置
        urlParams.collector_config_id = this.curCollect.collector_config_id;
        data.bk_biz_id = this.bkBizId;
        delete data.visible_type;
        requestUrl = 'clean/updateCleanStash';
      } else { // 新建/编辑清洗模板
        data.name = this.saveTempName
        data.bk_biz_id = this.bkBizId
        // 可见范围非多业务选择时删除visible_bk_biz_id
        data.visible_bk_biz_id = this.visibleBkBiz;
        data.visible_type !== 'multi_biz' && (delete data.visible_bk_biz_id);
        if (this.isEditTemp) urlParams.clean_template_id = this.$route.params.templateId
        requestUrl = this.isEditTemp ? 'clean/updateTemplate' : 'clean/createTemplate';
      }
      const updateData = { params: urlParams, data };

      this.$http.request(requestUrl, updateData).then((res) => {
        if (res.code === 0) {
          if (this.isSetEdit) {
            this.messageSuccess(this.$t('保存成功'));
            this.$emit('updateLogFields');
          } else if (isCollect) {
            const step = this.isCleanField ? 2 : null
            this.$emit('stepChange', step);
          } else {
            this.messageSuccess(this.$t('保存成功'));
            // 清洗模板编辑则返回模板列表
            if(this.isTempField) {
              this.$emit('change-submit', true)
              this.handleCancel(false)
            }
          }
        }
      })
        .finally(() => {
          this.isLoading = false;
          this.basicLoading = false;
        });
    },
    // 检查提取方法或条件是否已变更
    checkEtlConfChnage(isCollect = false) {
      // 非bk_log_text类型需要有正确的结果
      if (this.formData.etl_config && this.formData.etl_config !== 'bk_log_text' && !this.hasFormat) return;
      let isConfigChange = false; // 提取方法或条件是否已变更
      const etlConfigParam = this.params.etl_config;
      if (etlConfigParam !== 'bk_log_text') {
        const etlConfigForm = this.formData.etl_config;
        if (etlConfigParam !== etlConfigForm) {
          isConfigChange = true;
        } else {
          const etlParams = this.params.etl_params;
          const etlParamsForm = this.formData.etl_params;
          if (etlConfigParam === 'bk_log_regexp') {
            isConfigChange = etlParams.separator_regexp !== etlParamsForm.separator_regexp;
          }
          if (etlConfigParam === 'bk_log_delimiter') {
            isConfigChange = etlParams.separator !== etlParamsForm.separator;
          }
        }
      }
      if (isConfigChange) {
        const h = this.$createElement;
        this.$bkInfo({
          type: 'warning',
          title: this.$t('是否按原配置提交?'),
          subHeader: h('p', {
            style: {
              whiteSpace: 'normal',
            },
          }, this.$t('字段提取方法或条件已发生变更，需【调试&设置】按钮点击操作成功才会生效')),
          confirmFn: () => {
            isCollect ? this.fieldCollection(true) : this.handleSaveTemp();
          },
        });
        return;
      }
      isCollect ? this.fieldCollection(true) : this.handleSaveTemp();
    },
    // 完成按钮
    finish(isCollect = false) {
      if (!this.params.etl_config) {
        this.$bkMessage({
          theme: 'error',
          message: this.$t('请选择字段提取方法'),
        });
      }
      // 清洗模板选择多业务时不能为空
      if (this.formData.visible_type === 'multi_biz' && !this.visibleBkBiz.length && this.isClearTemplate) {
        this.messageError(this.$t('可见类型为业务属性时，业务标签不能为空'));
        return
      }
      // const promises = [this.checkStore()];
      const promises = [];
      if (this.formData.etl_config !== 'bk_log_text') {
        promises.splice(1, 0, ...this.checkFieldsTable());
      }
      Promise.all(promises).then(() => {
        this.checkEtlConfChnage(isCollect);
      }, (validator) => {
        console.warn('保存失败', validator);
      });
    },
    // 字段表格校验
    checkFieldsTable() {
      return this.formData.etl_config !== 'bk_log_text' ? this.$refs.fieldTable.validateFieldTable() : [];
    },
    // 跳过
    handleSkip() {
      this.$emit('stepChange', this.curStep + 1);
    },
    handleCancel(isCollect = false) {
      if (isCollect) return;
      if(this.isSetEdit){
        this.$emit('reset-page')
        return
      }
      const { query: { backRoute } } = this.$route;
      let routeName;
      if (!this.isSetEdit && !!backRoute) {
        routeName = backRoute
      } else {
        routeName = this.isCleanField ? 'log-clean-list' : 'log-clean-templates';
      }
      this.$router.push({
        name: routeName,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    prevHandler() {
      this.$emit('stepChange', 1);
    },
    // 即将前往高级清洗
    advanceHandler() {
      const h = this.$createElement;
      // const h = this.$createElement;
      this.$bkInfo({
        type: 'warning',
        title: this.$t('跳转到计算平台'),
        subHeader: h('p', {
          style: {
            whiteSpace: 'normal',
            padding: '0 28px',
            color: '#63656e',
          },
        }, this.$t('高级清洗需要跳转到计算平台并终止当前流程，请确认是否继续跳转')),
        // okText: this.$t('直接下载'),
        confirmFn: () => {
          const id = this.curCollect.bkdata_data_id;
          const jumpUrl = `${window.BKDATA_URL}/#/data-access/data-detail/${id}/3`;
          window.open(jumpUrl, '_blank');
          this.$emit('change-submit', true);
          // 前往高级清洗刷新页
          this.$emit('changeClean');
        },
      });
    },
    // 获取详情
    getDetail() {
      // const tsStorageId = this.formData.storage_cluster_id;
      const {
        table_id,
        storage_cluster_id,
        table_id_prefix,
        etl_config,
        etl_params,
        fields,
      } = this.curCollect;
      const option = { time_zone: '', time_format: '' };
      const copyFields = fields ? JSON.parse(JSON.stringify(fields)) : [];
      copyFields.forEach((row) => {
        row.value = '';
        if (row.is_delete) {
          const copyRow = Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), JSON.parse(JSON.stringify(row)));
          Object.assign(row, copyRow);
        }
        if (row.option) {
          row.option = Object.assign({}, option, row.option || {});
        } else {
          row.option = Object.assign({}, option);
        }
      });
      /* eslint-disable */
      this.params.etl_config = etl_config
      Object.assign(this.params.etl_params, {
        separator_regexp: etl_params?.separator_regexp || '',
        separator: etl_params?.separator || ''
      })
      this.isUnmodifiable = !!(table_id || storage_cluster_id)
      this.fieldType = etl_config || 'bk_log_text'
      /* eslint-enable */
      Object.assign(this.formData, {
        table_id,
        // storage_cluster_id,
        table_id_prefix,
        etl_config: this.fieldType,
        etl_params: Object.assign({
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
        }, etl_params ? JSON.parse(JSON.stringify(etl_params)) : {}), // eslint-disable-line
        fields: copyFields.filter(item => !item.is_built_in),
      });
      if (!this.copyBuiltField.length) {
        this.copyBuiltField = copyFields.filter(item => item.is_built_in);
      }
      if (this.curCollect.etl_config && this.curCollect.etl_config !== 'bk_log_text') {
        this.formatResult = true;
      }
    },
    chickFile() {
      this.defaultSettings.isShow = true;
    },
    //  原始日志刷新
    refreshClick() {
      if (this.refresh) {
        this.getDataLog('init');
      }
    },
    copyText(data) {
      const createInput = document.createElement('input');
      createInput.value = data;
      document.body.appendChild(createInput);
      createInput.select(); // 选择对象
      document.execCommand('Copy'); // 执行浏览器复制命令
      createInput.style.display = 'none';
      const h = this.$createElement;
      this.$bkMessage({
        message: h('p', {
          style: {
            textAlign: 'center',
          },
        }, this.$t('复制成功')),
        offsetY: 80,
      });
    },
    requestEtlPreview(type) {
      const { etl_config, etl_params } = this.params;
      /* eslint-disable */
      if (!this.logOriginal || !etl_config || etl_config === 'bk_log_text') return
      if (etl_config === 'bk_log_regexp' && !etl_params.separator_regexp) return
      if (etl_config === 'bk_log_delimiter' && !etl_params.separator) return
      const newFields = this.$refs.fieldTable ? this.$refs.fieldTable.getData() : [] // 不能取原fileds，因字段修改后的信息保留在table组件里
      this.isExtracting = type === 'init' ? !type : true
      const etlParams = {}
      if (etl_config === 'bk_log_delimiter') {
        etlParams.separator = etl_params.separator
      }
      if (etl_config === 'bk_log_regexp') {
        etlParams.separator_regexp = etl_params.separator_regexp
      }

      let requestUrl;
      const urlParams = {};
      const data = {
        etl_config,
        etl_params: etlParams,
        data: this.logOriginal,
      };

      if (this.isTempField) {
        requestUrl = 'clean/getEtlPreview';
      } else {
        urlParams.collector_config_id = this.curCollect.collector_config_id,
        requestUrl = 'collect/getEtlPreview';
      }
      const updateData = { params: urlParams, data }
      this.$http.request(requestUrl, updateData).then((res) => {
        // 以下为整个页面关键逻辑
        /**
         * 只有点击调试按钮，并且成功了，才会改变原有的fields列表，否则只是结果失败，不做任何操作
         */
        // value 用于展示右边的预览值 - 编辑进入时需要触发预览
        if (res.data && res.data.fields) {
          const dataFields = res.data.fields;
          dataFields.forEach((item) => {
            item.verdict = this.judgeNumber(item);
          });
          const fields = this.formData.fields;

          /* eslint-disable */
          if (!type) { // 只有点击了调试按钮，才能修改fields列表  // 原始日志更新值改边预览值
            if (!this.formData.etl_config || this.formData.etl_config !== etl_config || !newFields.length) { // 如果没有提取方式 || 提取方式发生变化 || 不存在任何字段
              const list = dataFields.reduce((arr, item) => {
                const field = Object.assign({}, JSON.parse(JSON.stringify(this.rowTemplate)), item)
                arr.push(field)
                return arr
              }, [])
              this.formData.fields.splice(0, fields.length, ...list)
              } else { // 否则 - 将对table已修改值-> newFields进行操作
                if (etl_config === 'bk_log_json' || etl_config === 'bk_log_regexp') {
                  const list = dataFields.reduce((arr, item) => {
                    const child = newFields.find(field => {
                      // return  !field.is_built_in && (field.field_name === item.field_name || field.alias_name === item.field_name)
                      return !field.is_built_in && field.field_name === item.field_name
                    })
                    item = child ? Object.assign({}, child, item) : Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item)
                    arr.push(item)
                    return arr
                  }, [])
                  if (etl_config === 'bk_log_json') { // json方式下已删除操作的需要拿出来合并到新的field列表里
                    const deletedFileds = newFields.reduce((arr, field) => {
                      if (field.is_delete && !dataFields.find(item => item.field_name === field.field_name)) {
                        arr.push(field)
                      }
                      return arr
                    }, [])
                    list.splice(list.length, 0, ...deletedFileds)
                  }
                  this.formData.fields.splice(0, fields.length, ...list)
                }

                if (etl_config === 'bk_log_delimiter') { // 分隔符逻辑较特殊，需要单独拎出来
                  let index
                  newFields.forEach((item, idx) => { // 找到最后一个field_name不为空的下标
                    if (item.field_name && !item.is_delete) {
                      index = idx + 1
                    }
                  })
                  const list = []
                  const deletedFileds = newFields.filter(item => item.is_delete)
                  list.splice(list.length, 0, ...deletedFileds) // 将已删除的字段存进数组
                  if (index) {
                    newFields.forEach((item, idx) => { // 找到最后一个field_name不为空的下标
                      const child = dataFields.find(data => data.field_index === item.field_index)
                      item.value = child ? child.value : '' // 修改value值(预览值)
                      if (index > idx && !item.is_delete) { // 将未删除的存进数组
                        list.push(item)
                      }
                    })
                    dataFields.forEach(item => { // 新增的字段需要存进数组
                      const child = list.find(field => field.field_index === item.field_index)
                      if (!child) {
                        list.push(Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item))
                      }
                    })
                  } else {
                    dataFields.reduce((arr, item) => {
                      const field = Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item)
                      arr.push(field)
                      return arr
                    }, list)
                  }
                  list.sort((a, b) => a.field_index - b.field_index) // 按 field_index 大小进行排序

                  this.formData.fields.splice(0, fields.length, ...list)
                }
              }
              this.formatResult = true // 此时才能将结果设置为成功
              this.savaFormData()

          } else { // 仅做预览赋值操作，不改变结果
            newFields.forEach(field => {
              const child = dataFields.find(item => {
                if (etl_config === 'bk_log_json') {
                  return field.field_name === item.field_name
                  // return  field.field_name === item.field_name || field.alias_name === item.field_name // 同上
                } else {
                  return etl_config === 'bk_log_delimiter' ? (field.field_index === item.field_index) : field.field_name === item.field_name
                }
              })
              if (!field.is_built_in) {
                field.value = child ? child.value : ''
              }
            })
            this.formData.fields.splice(0, fields.length, ...newFields)
          }
          /* eslint-enable */
        } else {
          this.formatResult = false;
        }
      })
        .catch(() => {
          if (!type) { // 原始日志内容修改不引发结果变更
            this.formatResult = false;
          }
        })
        .finally(() => {
          this.isExtracting = false;
        });
    },
    savaFormData() {
      this.formData.etl_config = this.params.etl_config;
      Object.assign(this.formData.etl_params, this.params.etl_params);
    },
    //  获取采样状态
    getDataLog(isInit) {
      this.refresh = false;
      this.basicLoading = true;
      this.$http.request('source/dataList', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
      }).then((res) => {
        if (res.data && res.data.length) {
          this.copysText = Object.assign(res.data[0].etl, res.data[0].etl.items[0]) || {};
          const data = res.data[0];
          this.jsonText = data.origin || {};
          this.logOriginal = data.etl.data || '';
          if (this.logOriginal) {
            this.requestEtlPreview(isInit);
          }
          this.copyBuiltField.forEach((item) => {
            const fieldName = item.field_name;
            if (fieldName) {
              // eslint-disable-next-line no-prototype-builtins
              if (item.hasOwnProperty('value')) {
                item.value = this.copysText[fieldName];
              } else {
                this.$set(item, 'value', this.copysText[fieldName]);
              }
            }
          });
        }
      })
        .catch(() => {
        })
        .finally(() => {
          this.basicLoading = false;
          this.refresh = true;
        });
    },
    visibleHandle(val) {
      this.deletedVisible = val;
    },
    handleKeepLog(value) {
      this.formData.etl_params.retain_original_text = value;
    },
    judgeNumber(val) {
      const { value } = val;
      if (value === 0) return false;

      return (value && value !== ' ') ? isNaN(value) : true;
    },
    // 模板弹窗确认
    handleTemplConfirm() {
      if (this.isSaveTempDialog) {
        if (this.saveTempName.trim() === '') {
          this.$bkMessage({
            theme: 'error',
            message: this.$t('请输入模板名称'),
          });
          return;
        }
        this.templateDialogVisible = false;
        this.fieldCollection(false);
      } else {
        if (!this.selectTemplate) {
          this.$bkMessage({
            theme: 'error',
            message: this.$t('请选择清洗模板'),
          });
          return;
        }

        // 应用模板设置
        const curTemp = this.templateList.find(temp => temp.clean_template_id === this.selectTemplate);
        this.formData.fields.splice(0, this.formData.fields.length);
        this.setTempDetail(curTemp);
        this.templateDialogVisible = false;
      }
    },
    // 打开保存/选择模板弹窗
    openTemplateDialog(isSave = false) {
      if (isSave) { // 保存模板前往检验
        this.finish(false);
        return;
      }

      // 新增清洗未选择采集项
      if ((this.isCleanField && !this.cleanCollector) || this.isSetDisabled) return;

      // 选择应用模板
      this.isSaveTempDialog = isSave;
      this.templateDialogVisible = true;
      this.$http.request('clean/cleanTemplate', {
        query: {
          bk_biz_id: this.bkBizId,
        },
      }).then((res) => {
        if (res.data) {
          this.templateList = res.data;
        }
      });
    },
    // 保存模板
    handleSaveTemp() {
      this.isSaveTempDialog = true;
      this.templateDialogVisible = true;
    },
    // 获取采集项清洗基础配置缓存 用于存储入库提交
    getCleanStash(id) {
      this.$http.request('clean/getCleanStash', {
        params: {
          collector_config_id: id,
        },
      }).then((res) => {
        if (res.data) {
          const { clean_type, etl_params, etl_fields } = res.data;
          this.formData.fields.splice(0, this.formData.fields.length);
          /* eslint-disable */
          this.params.etl_config = clean_type
          Object.assign(this.params.etl_params, {
            separator_regexp: etl_params.separator_regexp || '',
            separator: etl_params.separator || ''
          })
          this.fieldType = clean_type
          /* eslint-enable */
          Object.assign(this.formData, {
            etl_config: this.fieldType,
            etl_params: Object.assign({
              retain_original_text: true,
              separator_regexp: '',
              separator: '',
            }, etl_params ? JSON.parse(JSON.stringify(etl_params)) : {}), // eslint-disable-line
            fields: etl_fields,
          });
        }
      })
        .finally(() => {
          this.basicLoading = false;
        });
    },
    // 新建、编辑采集项时获取更新详情
    async setDetail(id) {
      if (!id) return;
      this.$http.request('collect/details', {
        params: { collector_config_id: id },
      }).then(async (res) => {
        if (res.data) {
          this.$store.commit('collect/setCurCollect', res.data);
          await this.getDetail();
          await this.getCleanStash(id);
          this.getDataLog('init');
        }
      })
        .finally(() => {
          // this.basicLoading = false;
        });
    },
    // 新增、编辑清洗选择采集项
    async handleCollectorChange(id) {
      this.basicLoading = true;
      // 先校验有无采集项管理权限
      const paramData = {
        action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
        resources: [{
          type: 'collection',
          id,
        }],
      };
      const res = await this.$store.dispatch('checkAndGetData', paramData);
      if (res.isAllowed === false) {
        this.authPageInfo = res.data;
        this.basicLoading = false;
        return;
      }
      const curCollect = this.cleanCollectorList.find((item) => {
        return item.collector_config_id.toString() === id.toString();
      });
      if (curCollect.create_clean_able || this.isEditCleanItem) {
        this.setAdvanceCleanTab(false);
        // 获取采集项详情
        await this.setDetail(id);
      } else { // 新增清洗且当前采集项已有基础清洗 则默认只能新增高级清洗
        this.$store.commit('collect/setCurCollect', curCollect);
        this.setAdvanceCleanTab(true);
        this.basicLoading = false;
      }
    },
    // 采集项列表点击申请采集项目管理权限
    async applyProjectAccess(item) {
      this.$el.click(); // 手动关闭下拉
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: item.collector_config_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$bkLoading.hide();
      }
    },
    handleOpenDocument() {
      window.open(this.docUrl, '_blank');
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/space-tag-option';

  .step-field-container {
    min-width: 950px;
    max-height: 100%;
    padding: 0 30px 42px;
    overflow: auto;
  }

  .step-field {
    .king-alert {
      margin: 30px auto -28px;
    }

    .collector-select {
      display: flex;
      align-items: center;
      margin: 50px 0 -26px;

      label {
        margin-right: 16px;
        font-size: 12px;
        color: #63656e;
      }
    }

    .step-field-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
      padding-top: 50px;
      padding-bottom: 10px;
    }

    .text-nav {
      display: inline-block;
      font-size: 12px;
      color: #3a84ff;
      font-weight: normal;

      span {
        margin-left: 10px;
        cursor: pointer;
      }
    }

    .bk-switcher-small {
      width: 36px;
      height: 20px;

      &::after {
        width: 16px;
        height: 16px;
      }

      &.is-checked:after {
        margin-left: -18px;
      }
    }

    .tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
    }

    .tips_storage {
      width: 540px;
      background-color: rgb(239, 248, 255);
      border: 1px solid deepskyblue;
      font-size: 12px;
      padding: 10px;
      margin-top: 15px;

      div {
        line-height: 24px;
        color: #63656e;
      }
    }

    .form-div {
      display: flex;
      margin: 20px 0;

      .form-inline-div {
        white-space: nowrap;

        .bk-form-content {
          display: flex;
          flex-wrap: nowrap;
        }
      }

      .prefix {
        font-size: 14px;
        line-height: 32px;
        color: #858790;
        margin-right: 8px;
        min-width: 80px;
        text-align: right;
      }
    }

    .field-method {
      position: relative;
      margin: 30px 0 0 0;

      .preview-panel-left {
        width: 621px;
      }

      .loading-block {
        position: absolute;
        top: calc(100% + 20px);
        left: 0;
        width: 100%;
        height: 40px;
      }
    }

    .field-method-head {
      margin: 0 0 10px 0;
      top: -34px;

      @include clearfix;

      .field-method-link {
        margin-left: 16px;
      }

      .toggle-icon {
        margin-right: 4px;
        color: #3a84ff;
        cursor: pointer;
      }

      .table-setting {
        line-height: 18px;
        display: flex;
        align-items: center;
      }

      .disabled-setting {
        .bk-label,
        .toggle-icon,
        .visible-deleted-text,
        .field-method-link {
          color: #c4c6cc;
        }

        .toggle-icon,
        .field-method-link {
          cursor: not-allowed;
        }
      }
    }

    .field-template-head {
      padding-bottom: 20px;
      border-bottom: 1px solid #dcdee5;
    }

    .field-method-title {
      margin: 0;
      line-height: 20px;
      font-size: 14px;
      font-weight: normal;
      color: #7a7c85;
    }

    .field-text {
      position: relative;
      top: 10px;
      margin-right: 22px;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
    }

    .bk-tab-label-wrapper .bk-tab-label-item .bk-tab-label {
      font-size: 12px;
    }

    .field-method-tab.bk-tab-unborder-card {
      .bk-tab-label-list .bk-tab-label-item {
        min-width: 80px;
      }

      .bk-tab-section {
        display: none;
      }
    }

    .field-step {
      position: relative;
      margin-bottom: 12px;
      padding-bottom: 24px;
      padding-left: 20px;

      &::before {
        content: '';
        position: absolute;
        top: 4px;
        left: 0;
        width: 8px;
        height: 8px;
        border: 2px solid #d8d8d8;
        border-radius: 50%;
      }

      &::after {
        content: '';
        position: absolute;
        top: 18px;
        left: 6px;
        width: 1px;
        height: 100%;
        background: #d8d8d8;
      }

      &:last-child::before {
        top: 8px;
      }

      &:last-child::after {
        top: 22px;
        height: calc(100% - 30px);
      }

      .step-text {
        color: #63656e;
        font-size: 14px;
      }

      .template-text {
        margin-left: 10px;
        font-size: 12px;
        color: #3a84ff;
        cursor: pointer;
      }

      .template-disabled {
        color: #c4c6cc;
        cursor: not-allowed;
      }

      .field-button-group {
        display: flex;
        align-items: center;
        margin: 20px 0 0;
      }
    }

    .step-head {
      width: 242px;
      display: flex;
      align-items: center;

      .documentation {
        color: #3a84ff;
        font-size: 12px;
        transform: translateX(45px) translateY(2px);
        cursor: pointer;
      }
    }

    .field-method-link {
      font-size: 12px;
      color: #3a84ff;
      cursor: pointer;
    }

    .field-method-result {
      margin-top: 8px;
    }

    .visible-select {
      width: 560px;

      .scope-radio {
        margin: 0 26px 14px 0;
      }

      .visible-scope-box {
        min-height: 30px;
        display: flex;
        position: relative;

        .please-select {
          color: #c3cdd7;
          margin-left: 10px;
        }

        .icon-angle-down {
          position: absolute;
          font-size: 20px;
          top: 4px;
          right: 0;
          transform: rotateZ(0deg);
          transition: all .3s;
        }

        .icon-rotate {
          transform: rotateZ(180deg);
        }
      }
    }

    .field-method-cause {
      margin-bottom: 20px;

      @include clearfix;
    }

    .debug-btn {
      margin-left: 12px;
      background: #fff;
      color: #3a84ff;

      &:hover {
        color: #fff;
      }
    }

    .field-method-regex {
      margin-top: 20px;

      .regex-btn {
        position: absolute;
        top: 0;
        right: 0;
      }
    }

    .textarea-wrapper {
      width: 100%;
      position: relative;
    }

    .mimic-textarea {
      margin: 0;
      padding: 6px 10px;
      width: 100%;
      line-height: 1.5;
      min-height: 72px;
      font-size: 12px;
      color: transparent;
      outline: none;
      white-space: pre-wrap;
    }

    .regex-textarea {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;

      .bk-textarea-wrapper {
        height: 100%;
      }

      textarea {
        height: 100%;
        overflow: hidden;
      }
    }

    .hot-data-form-item {
      .bk-form-content {
        display: flex;
        align-items: center;

        .disable-tips {
          margin-left: 10px;
          font-size: 12px;
          color: #63656e;

          a {
            color: #3a84ff;
          }
        }
      }
    }

    .form-item-flex {
      display: flex;

      .bk-label {
        line-height: 20px;
        width: auto;
        padding: 0;
        font-size: 12px;
        color: #63656e;

        &.has-desc > span {
          margin-right: 20px;
          border-bottom: 1px dashed #d8d8d8;
          cursor: pointer;
        }
      }

      .bk-form-content {
        flex: 1;
        margin: 0 0 0 10px;
        font-size: 0;
      }
    }

    .visible-deleted-text {
      font-size: 12px;
      color: #63656e;
    }

    .format-error {
      position: absolute;
      left: 280px;
      margin-top: 8px;
      font-size: 12px;
      color: #ea3636;
    }

    .log-style {
      height: 82px;

      .bk-form-textarea:focus {
        /* stylelint-disable-next-line declaration-no-important */
        background-color: #313238 !important;
        border-radius: 2px;
      }

      .bk-textarea-wrapper {
        border: none;
      }
    }

    .advance-clean-step-container {
      display: flex;
      margin-top: 40px;

      .image-content {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
      }

      .icon-angle-double-right-line {
        margin: 110px 30px 0;
        color: rgba(105, 157, 244, .9);
        opacity: .9;
      }

      .step-num {
        margin-right: 8px;
        font-size: 24px;
        font-family: Impact, Impact-Regular;
        color: #a3c5fd;
        line-height: 29px;
      }

      .step-description {
        margin-top: 26px;
        width: 320px;
        line-height: 20px;
        color: #63656e;
        font-size: 14px;
      }

      .remark {
        margin-top: 20px;
        color: #979ba5;
        font-size: 12px;
      }

      .link {
        color: #3a84ff;
        cursor: pointer;

        span {
          margin-left: 4px;
        }
      }
    }

    .form-button {
      margin-top: 28px;
    }
  }

  .standard-field-table {
    width: 965px;
    padding-bottom: 14px;
    max-height: 464px;
    overflow-x: hidden;
    overflow-y: auto;

    .preview-panel-left {
      width: 615px;
    }

    .preview-panel-right {
      width: 350px;
    }
  }

  .json-text-style {
    background-color: #313238;
    color: #c4c6cc;
  }

  .option-slot-container {
    padding: 8px 0;
    min-height: 32px;
    line-height: 14px;

    &.no-authority {
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #c4c6cc;
      cursor: not-allowed;

      .text {
        width: calc(100% - 56px);
      }

      .apply-text {
        flex-shrink: 0;
        display: none;
        color: #3a84ff;
        cursor: pointer;
      }

      &:hover .apply-text {
        display: flex;
      }
    }
  }
</style>
