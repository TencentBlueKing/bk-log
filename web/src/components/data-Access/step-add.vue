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
  <div class="add-collection-container">
    <bk-alert v-if="guideUrl" class="king-alert" type="info" closable>
      <div slot="title" class="slot-title-container">
        {{ $t('接入前请查看') }}
        <a class="link" target="_blank" :href="guideUrl"> {{ $t('接入指引') }}</a>
        {{ $t('，尤其是在日志量大的情况下请务必提前沟通。') }}
      </div>
    </bk-alert>
    <bk-form
      :label-width="115"
      :model="formData"
      ref="validateForm"
      data-test-id="addNewCollectionItem_form_acquisitionConfigur">
      <!-- 基础信息 -->
      <div data-test-id="acquisitionConfigur_div_baseMessageBox">
        <div class="add-collection-title">{{ $t('dataSource.basic_information') }}</div>
        <bk-form-item
          :label="$t('dataSource.source_name')"
          :required="true"
          :rules="rules.collector_config_name"
          :property="'collector_config_name'">
          <bk-input
            data-test-id="baseMessage_input_fillName"
            v-model="formData.collector_config_name"
            show-word-limit
            maxlength="50">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('dataSource.source_en_name')"
          :required="true"
          :rules="rules.collector_config_name_en"
          :property="'collector_config_name_en'">
          <bk-input
            v-model="formData.collector_config_name_en"
            show-word-limit
            maxlength="50"
            data-test-id="baseMessage_input_fillEnglishName"
            :disabled="isUpdate && !!(formData.collector_config_name_en)"
            :placeholder="$t('dataSource.en_name_tips')">
          </bk-input>
          <p class="en-name-tips" slot="tip">{{ $t('dataSource.en_name_placeholder') }}</p>
        </bk-form-item>
        <bk-form-item :label="$t('configDetails.remarkExplain')">
          <bk-input
            type="textarea"
            style="width: 320px;"
            v-model="formData.description"
            data-test-id="baseMessage_input_fillDetails"
            maxlength="100">
          </bk-input>
        </bk-form-item>
      </div>

      <!-- 源日志信息 -->
      <div data-test-id="acquisitionConfigur_div_sourceLogBox">
        <div class="add-collection-title">{{ $t('dataSource.Source_log_information') }}</div>
        <!-- 日志类型 -->
        <bk-form-item :label="$t('configDetails.logType')" required>
          <div class="bk-button-group log-type">
            <bk-button
              v-for="(item, index) in globalsData.collector_scenario"
              :data-test-id="`sourceLogBox_buttom_checkoutType${item.id}`"
              :key="index"
              :disabled="isUpdate"
              :class="{
                'disable': !item.is_active,
                'is-selected': item.id === formData.collector_scenario_id,
                'is-updated': isUpdate && item.id === formData.collector_scenario_id
              }"
              @click="chooseLogType(item)"
            >{{ item.name }}
            </bk-button>
          </div>
        </bk-form-item>
        <!-- 数据分类 -->
        <bk-form-item
          :label="$t('configDetails.dataClassify')"
          required
          :rules="rules.category_id"
          :property="'category_id'">
          <bk-select
            style="width: 320px;"
            v-model="formData.category_id"
            data-test-id="sourceLogBox_div_selectDataClassification"
            :disabled="isUpdate"
            @selected="chooseDataClass">
            <template v-for="(item, index) in globalsData.category">
              <bk-option-group :id="item.id" :name="item.name" :key="index">
                <bk-option
                  v-for="(option, key) in item.children"
                  :key="key"
                  :id="option.id"
                  :name="`${item.name}-${option.name}`"> {{ option.name }}
                </bk-option>
              </bk-option-group>
            </template>
          </bk-select>
        </bk-form-item>
        <!-- 日志种类 -->
        <bk-form-item
          v-if="formData.collector_scenario_id === 'wineventlog'"
          :label="$t('configDetails.logSpecies')"
          data-test-id="sourceLogBox_div_logSpecies"
          required>
          <bk-checkbox-group
            v-model="selectLogSpeciesList"
            @change="outherBlurRules">
            <div class="species-item">
              <bk-checkbox
                v-for=" (item, index) in logSpeciesList"
                :disabled="selectLogSpeciesList.length === 1 && selectLogSpeciesList[0] === item.id"
                :value="item.id"
                :key="index">
                {{item.name}}
              </bk-checkbox>
              <bk-tag-input
                v-model="outherSpeciesList"
                :class="outherRules ? 'tagRulesColor' : ''"
                @blur="outherBlurRules"
                @remove="outherBlurRules"
                :allow-auto-match="true"
                :has-delete-icon="true"
                :allow-create="true">
              </bk-tag-input>
            </div>
          </bk-checkbox-group>
        </bk-form-item>
        <!-- 采集目标 -->
        <div class="form-div mt">
          <bk-form-item
            :label="$t('configDetails.target')"
            class="item-target"
            required
            :rules="rules.nodes"
            :property="'target_nodes'"
            ref="formItemTarget">
            <bk-button
              theme="default"
              :title="$t('configDetails.newly_increased')"
              icon="plus"
              style="font-size: 12px"
              data-test-id="sourceLogBox_button_addCollectionTarget"
              :class="colorRules ? 'rulesColor' : ''"
              :disabled="!formData.category_id"
              @click="showIpSelectorDialog = true">
              {{ $t('retrieve.select_target') }}
            </bk-button>
            <input type="text" :value="formData.target_nodes" style="display: none">
          </bk-form-item>
          <div class="count" v-if="formData.target_nodes.length">
            <span>{{ collectTargetTarget[formData.target_node_type + '1'] }}</span>
            <span class="font-blue">{{ formData.target_nodes.length }}</span>
            <span>{{ collectTargetTarget[formData.target_node_type + '2'] }}</span>
          </div>
          <ip-selector-dialog
            :show-dialog.sync="showIpSelectorDialog"
            :target-object-type="formData.target_object_type"
            :target-node-type="formData.target_node_type"
            :target-nodes="formData.target_nodes"
            @target-change="targetChange">
          </ip-selector-dialog>
        </div>
        <div v-if="formData.collector_scenario_id !== 'wineventlog'">
          <!-- 日志路径 -->
          <div class="form-div mt" v-for="(log, index) in logPaths" :key="index">
            <bk-form-item
              :label="index === 0 ? $t('retrieve.logPath') : ''" required
              :rules="rules.paths"
              :property="'params.paths.' + index + '.value'">
              <bk-input
                v-model="log.value"
                data-test-id="sourceLogBox_input_addLogPath"
              ></bk-input>
            </bk-form-item>
            <div class="ml9">
              <i class="bk-icon icon-plus-circle icons"
                 @click="addLog"
                 data-test-id="sourceLogBox_i_newAddLogPath"
              ></i>
              <i
                :class="['bk-icon icon-minus-circle icons ml9', { disable: logPaths.length === 1 }] "
                data-test-id="sourceLogBox_i_deleteAddLogPath"
                @click="delLog(index)"></i>
            </div>
            <div class="tips" v-if="index === 0">
              {{ $t('retrieve.log_available') }}
              <span class="font-gray">{{ $t('retrieve.log_wildcard_character') }}</span>
            </div>
          </div>
          <!-- 日志字符集 -->
          <bk-form-item :label="$t('configDetails.logSet')" required>
            <bk-select
              data-test-id="sourceLogBox_div_changeLogCharacterTet"
              style="width: 320px;"
              searchable
              v-model="formData.data_encoding"
              :clearable="false">
              <bk-option
                v-for="(option, ind) in globalsData.data_encoding"
                :key="ind"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
        </div>
        <!-- 段日志正则调试 -->
        <div v-if="hasMultilineReg" class="multiline-log-container">
          <div class="row-container">
            <bk-form-item
              :label="$t('行首正则')"
              :rules="rules.notEmptyForm"
              required
              property="params.multiline_pattern">
              <bk-input
                data-test-id="sourceLogBox_input_beginningRegular"
                v-model.trim="formData.params.multiline_pattern"
              ></bk-input>
            </bk-form-item>
            <bk-button
              text size="small"
              class="king-button"
              data-test-id="sourceLogBox_button_debugging"
              @click="showRegDialog = true">
              {{ $t('调试') }}
            </bk-button>
          </div>
          <div class="row-container second">
            {{ $t('最多匹配') }}
            <bk-form-item :rules="rules.maxLine" property="params.multiline_max_lines">
              <bk-input
                v-model="formData.params.multiline_max_lines"
                type="number"
                :precision="0"
                data-test-id="sourceLogBox_input_mostMatches"
                :show-controls="false">
              </bk-input>
            </bk-form-item>
            {{ $t('行，最大耗时') }}
            <bk-form-item :rules="rules.maxTimeout" property="params.multiline_timeout">
              <bk-input
                v-model="formData.params.multiline_timeout"
                type="number"
                :precision="0"
                data-test-id="sourceLogBox_input_maximumTimeConsuming"
                :show-controls="false">
              </bk-input>
            </bk-form-item>
            {{ $t('秒') }}
          </div>
          <multiline-reg-dialog
            :old-pattern.sync="formData.params.multiline_pattern"
            :show-dialog.sync="showRegDialog">
          </multiline-reg-dialog>
        </div>
      </div>

      <!-- 日志内容过滤 -->
      <div class="add-collection-title">{{ $t('retrieve.Log_content_filtering') }}</div>
      <div class="hight-setting" data-test-id="acquisitionConfigur_div_contentFiltering">
        <div v-if="formData.collector_scenario_id !== 'wineventlog'">
          <div class="tips ml115">{{ $t('retrieve.suggest_clean') }}</div>
          <div class="form-div">
            <bk-form-item :label="$t('configDetails.filterContent')">
              <bk-select
                style="width: 129px; margin-right: 8px;"
                :clearable="false"
                v-model="formData.params.conditions.type"
                @change="chooseType">
                <bk-option id="match" :name="$t('retrieve.String_filtering')"></bk-option>
                <bk-option id="separator" :name="$t('retrieve.Separator_filtering')"></bk-option>
              </bk-select>
            </bk-form-item>
            <bk-input v-show="isString" v-model="formData.params.conditions.match_content"></bk-input>
            <bk-select
              style="width: 254px; margin-left: 8px; height: 32px"
              :clearable="false"
              v-if="isString" v-model="formData.params.conditions.match_type">
              <bk-option id="include" :name="$t('retrieve.Keep_string')"></bk-option>
              <bk-option id="exclude" :name="$t('retrieve.Keep_filtering')" disabled>
                <span v-bk-tooltips.right="$t('正在开发中')">{{ $t('retrieve.Keep_filtering') }}</span>
              </bk-option>
            </bk-select>
            <bk-select
              style="width: 320px; margin-right: 8px; height: 32px"
              v-if="!isString"
              v-model="formData.params.conditions.separator">
              <bk-option
                v-for="(option, index) in globalsData.data_delimiter"
                :key="index"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
          <div class="tips ml115" v-show="!isString">{{ $t('retrieve.Complex_filtering') }}</div>
          <div class="form-div" v-if="!isString">
            <div class="choose-table">
              <div class="choose-table-item choose-table-item-head">
                <div class="left">{{ $t('retrieve.How_columns') }}</div>
                <div class="main">{{ $t('retrieve.equal_to') }}</div>
                <div class="right">{{ $t('retrieve.To_add_delete') }}</div>
              </div>
              <div class="choose-table-item-body">
                <div class="choose-table-item" v-for="(item, index) in separatorFilters" :key="index">
                  <div class="left">
                    <bk-form-item
                      label="" :rules="rules.separator_filters" style="width: 100px;"
                      :property="'params.conditions.separator_filters.' + index + '.fieldindex'">
                      <bk-input style="width: 100px;" v-model="item.fieldindex"></bk-input>
                    </bk-form-item>
                  </div>
                  <div :class="['main', { line: separatorFilters.length > 1 }] ">
                    <bk-form-item
                      label="" :rules="rules.separator_filters"
                      :property="'params.conditions.separator_filters.' + index + '.word'">
                      <bk-input v-model="item.word"></bk-input>
                    </bk-form-item>
                  </div>
                  <div class="right">
                    <i class="bk-icon icon-plus-circle icons" @click="addItem"></i>
                    <i
                      :class="['bk-icon icon-minus-circle icons ml9', { disable: separatorFilters.length === 1 }] "
                      @click="delItem(index)">
                    </i>
                  </div>
                </div>
                <div class="choose-select" v-if="separatorFilters && separatorFilters.length > 1">
                  <bk-select class="select-div" v-model="type" @selected="changeType">
                    <bk-option id="and" :name="$t('configDetails.and')"></bk-option>
                    <bk-option id="or" :name="$t('configDetails.or')"></bk-option>
                  </bk-select>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <div class="tips ml115">{{ $t('retrieve.suggest_clean') }}</div>
          <div>
            <bk-form-item :label="$t('configDetails.filterContent')">
              <div class="form-div win-filter" v-for="(item, index) in eventSettingList" :key="index">
                <bk-select
                  class="select-div"
                  :clearable="false"
                  @selected="tagBlurRules(item,index)"
                  v-model="item.type">
                  <bk-option
                    v-for="option in selectEventList"
                    :key="option.id"
                    :id="option.id"
                    :disabled="option.isSelect"
                    :name="option.name">
                  </bk-option>
                </bk-select>
                <bk-tag-input
                  class="tag-input"
                  v-model="item.list"
                  :class="item.isCorrect ? '' : 'tagRulesColor'"
                  @blur="tagBlurRules(item,index)"
                  @remove="tagBlurRules(item,index)"
                  :allow-auto-match="true"
                  :has-delete-icon="true"
                  :allow-create="true">
                </bk-tag-input>
                <div class="ml9">
                  <i :class="
                       ['bk-icon icon-plus-circle icons',
                        { disable: eventSettingList.length === selectEventList.length }]"
                     @click="addWinEvent"
                  ></i>
                  <i
                    :class="['bk-icon icon-minus-circle icons ml9', { disable: eventSettingList.length === 1 }] "
                    @click="delWinEvent(index)"></i>
                </div>
              </div>
            </bk-form-item>
          </div>
        </div>
      </div>

      <!-- 上报链路配置 -->
      <template v-if="!isCloseDataLink">
        <div class="add-collection-title">{{ $t('上报链路配置') }}</div>
        <bk-form-item required property="data_link_id" :label="$t('上报链路')" :rules="rules.linkConfig">
          <bk-select
            data-test-id="acquisitionConfigur_div_selectReportLink"
            style="width: 320px;"
            v-model="formData.data_link_id"
            :clearable="false"
            :disabled="isUpdate">
            <bk-option
              v-for="item in linkConfigurationList"
              :key="item.data_link_id"
              :id="item.data_link_id"
              :name="item.link_group_name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </template>

      <bk-form-item>
        <bk-button
          theme="primary"
          data-test-id="acquisitionConfigur_div_nextPage"
          :title="$t('retrieve.Start_collecting')"
          @click.stop.prevent="startCollect"
          :loading="isHandle"
          :disabled="!collectProject">
          {{ $t('retrieve.next') }}
        </bk-button>
        <bk-button
          theme="default"
          data-test-id="acquisitionConfigur_div_cancel"
          :title="$t('indexSetList.cancel')"
          class="ml10"
          @click="cancel">
          {{ $t('indexSetList.cancel') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>
<script>
import MultilineRegDialog from './multiline-reg-dialog';
import ipSelectorDialog from './ip-selector-dialog';
import { mapGetters, mapState } from 'vuex';
import { projectManages } from '@/common/util';

export default {
  components: {
    MultilineRegDialog,
    ipSelectorDialog,
  },
  data() {
    return {
      guideUrl: window.COLLECTOR_GUIDE_URL,
      colorRules: false,
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      showRegDialog: false, // 显示段日志调试弹窗
      linkConfigurationList: [], // 链路配置列表
      formData: {
        collector_config_name: '', // 采集项名称
        collector_config_name_en: '', // 采集项英文名称
        category_id: '', // 数据分类
        collector_scenario_id: 'row',
        data_encoding: 'UTF-8', // 日志字符集
        data_link_id: '', // 链路配置
        description: '', // 备注
        target_object_type: 'HOST', // 目前固定为 HOST
        target_node_type: 'TOPO', // 动态 TOPO 静态 INSTANCE 服务模版 SERVICE_TEMPLATE 集群模板 SET_TEMPLATE
        target_nodes: [], // 采集目标
        params: {
          multiline_pattern: '', // 行首正则, char
          multiline_max_lines: '50', // 最多匹配行数, int
          multiline_timeout: '2', // 最大耗时, int
          paths: [ // 日志路径
            { value: '' },
          ],
          conditions: {
            type: 'match', // 过滤方式类型
            match_type: 'include', // 过滤方式 可选字段 include, exclude
            match_content: '',
            separator: '',
            separator_filters: [ // 分隔符过滤条件
              { fieldindex: '', word: '', op: '=', logic_op: 'and' },
            ],
          },
          winlog_name: [], // windows事件名称
          winlog_level: [], // windows事件等级
          winlog_event_id: [], // windows事件id
        },
      },
      rules: {
        notEmptyForm: [ // 不能为空的表单
          {
            required: true,
            trigger: 'blur',
          },
        ],
        maxLine: [ // 最多匹配行数
          {
            validator: (val) => {
              if (val > 1000) {
                this.formData.params.multiline_max_lines = '1000';
              } else if (val < 1) {
                this.formData.params.multiline_max_lines = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
        maxTimeout: [ // 最大耗时
          {
            validator: (val) => {
              if (val > 10) {
                this.formData.params.multiline_timeout = '10';
              } else if (val < 1) {
                this.formData.params.multiline_timeout = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
        collector_config_name: [ // 采集名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
        ],
        collector_config_name_en: [ // 采集英文名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
          {
            min: 5,
            trigger: 'blur',
          },
          {
            regex: /^[A-Za-z0-9_]+$/,
            trigger: 'blur',
          },
        ],
        category_id: [ // 数据分类
          {
            required: true,
            trigger: 'blur',
          },
        ],
        paths: [ // 日志路径
          {
            required: true,
            trigger: 'change',
          },
        ],
        separator_filters: [ // 分隔符过滤条件
          {
            required: true,
            trigger: 'blur',
          },
        ],
        // 上报链路配置
        linkConfig: [
          {
            required: true,
            trigger: 'blur',
          },
        ],
        nodes: [
          {
            validator: this.checkNodes,
            trigger: 'change',
          },
        ],
      },
      logUrl: [
        { value: '' },
      ],
      chooseList: [
        { fieldindex: '', word: '', op: '=', logic_op: 'and' },
      ],
      type: 'and',
      isUpdate: false,
      isHandle: false,
      globals: {},
      showIpSelectorDialog: false,
      collectTargetTarget: { // 已(动态)选择 静态主机 节点 服务模板 集群模板
        INSTANCE1: this.$t('configDetails.selected'),
        INSTANCE2: this.$t('configDetails.staticHosts'),
        TOPO1: this.$t('configDetails.Dynamic_selection'),
        TOPO2: this.$t('configDetails.Been'),
        SERVICE_TEMPLATE1: this.$t('configDetails.selected'),
        SERVICE_TEMPLATE2: this.$t('configDetails.serviceTemplates'),
        SET_TEMPLATE1: this.$t('configDetails.selected'),
        SET_TEMPLATE2: this.$t('configDetails.setTemplates'),
      },
      logSpeciesList: [{
        id: 'Application',
        name: this.$t('应用程序'),
      }, {
        id: 'Security',
        name: this.$t('安全'),
      }, {
        id: 'System',
        name: this.$t('win系统'),
      }, {
        id: 'Outher',
        name: this.$t('其他'),
      }],
      outherRules: false,
      selectLogSpeciesList: ['Application', 'Security', 'System', 'Outher'],
      outherSpeciesList: [],
      selectEventList: [
        {
          id: 'winlog_event_id',
          name: this.$t('事件ID'),
          isSelect: false,
        },
        {
          id: 'winlog_level',
          name: this.$t('级别'),
          isSelect: false,
        },
      ],
      eventSettingList: [
        { type: 'winlog_event_id', list: [], isCorrect: true },
      ],
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters('globals', ['globalsData']),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    // 分隔符字段过滤条件
    separatorFilters() {
      const { params } = this.formData;
      return params.conditions.separator_filters || [{
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      }];
    },
    // 日志路径
    logPaths() {
      const { params } = this.formData;
      return params.paths || [];
    },
    // 是否为字符串过滤
    isString() {
      return this.formData.params.conditions.type === 'match';
    },
    // 是否打开行首正则功能
    hasMultilineReg() {
      return this.formData.collector_scenario_id === 'section';
    },
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    isCloseDataLink() {
      // 没有可上报的链路时，编辑采集配置链路ID为0或null时，隐藏链路配置框，并且不做空值校验。
      return !this.linkConfigurationList.length || (this.isUpdate && !this.curCollect.data_link_id);
    },
  },
  created() {
    this.getLinkData();
    this.isUpdate = this.$route.name !== 'collectAdd';
    if (this.isUpdate) {
      this.formData = JSON.parse(JSON.stringify(this.curCollect));
      const { params } = this.formData;
      if (this.formData.target?.length) { // IP 选择器预览结果回填
        this.formData.target_nodes = this.formData.target;
      }
      if (!this.formData.collector_config_name_en) { // 兼容旧数据英文名为空
        this.formData.collector_config_name_en = this.formData.table_id || '';
      }
      if (this.formData.collector_scenario_id !== 'wineventlog') {
        if (params.paths.length > 0) {
          params.paths = typeof params.paths[0] === 'string' ? params.paths.map(item => ({ value: item })) : params.paths;
        } else { // 兼容原日志路径为空列表
          params.paths = [{ value: '' }];
        }
      } else {
        const outherList = params.winlog_name.filter(v => ['Application', 'Security', 'System'].indexOf(v) === -1);
        if (outherList.length > 0) {
          this.outherSpeciesList = outherList;
          this.selectLogSpeciesList = params.winlog_name;
          this.selectLogSpeciesList.push('Outher');
        } else {
          this.selectLogSpeciesList = params.winlog_name;
        }

        delete params.ignore_older;
        delete params.max_bytes;
        delete params.tail_files;

        const newEventSettingList = [];
        for (const [key, val] of Object.entries(params)) {
          if (key !== 'winlog_name' && val[0] !== '') {
            newEventSettingList.push({
              type: key,
              list: val,
              isCorrect: true,
            });
          }
        }
        if (newEventSettingList.length !== 0) {
          this.eventSettingList = newEventSettingList;
        }
        this.selectDisabledChange();
      }

      // 分隔符过滤条件 and/or 初始值
      if (this.curCollect.params.conditions.type === 'separator') {
        this.type = this.curCollect.params.conditions.separator_filters[0].logic_op;
      }
    }
  },
  mounted() {
  },
  methods: {
    async getLinkData() {
      try {
        this.tableLoading = true;
        const res = await this.$http.request('linkConfiguration/getLinkList', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        this.linkConfigurationList = res.data.filter(item => item.is_active);
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    // 开始采集
    startCollect() {
      if (this.eventSettingList.some(el => el.isCorrect === false) || this.outherRules) {
        return;
      }
      this.$refs.validateForm.validate().then(() => {
        const params = this.handleParams();
        if (this.isCloseDataLink) {
          delete params.data_link_id;
        }
        if (this.formData.collector_scenario_id === 'wineventlog') {
          // win_log
          const winParams = {};
          if (this.selectLogSpeciesList.includes('Outher')) {
            this.selectLogSpeciesList.splice(this.selectLogSpeciesList.indexOf('Outher'), 1);
          }
          winParams.winlog_name = this.selectLogSpeciesList.concat(this.outherSpeciesList);
          this.eventSettingList.forEach((el) => {
            winParams[el.type] = el.list;
          });
          params.params = winParams;
        }
        this.isHandle = true;
        this.setCollection(params);
      }, () => {});
    },
    // 新增/修改采集
    setCollection(params) {
      this.isHandle = true;
      const urlParams = {};
      let requestUrl;
      if (this.isUpdate) {
        urlParams.collector_config_id = Number(this.$route.params.collectorId);
        requestUrl = this.isItsm ? 'collect/onlyUpdateCollection' : 'collect/updateCollection';
      } else {
        requestUrl = this.isItsm ? 'collect/onlyCreateCollection' : 'collect/addCollection';
      }
      const updateData = { params: urlParams, data: params };
      this.$http.request(requestUrl, updateData).then((res) => {
        if (res.code === 0) {
          if (this.isUpdate && this.isItsm) {
            sessionStorage.setItem('collectionUpdateData', JSON.stringify(updateData));
          }
          if (this.formData.collector_scenario_id !== 'wineventlog') {
            params.params.paths = params.params.paths.map(item => ({ value: item }));
          }
          this.$store.commit(`collect/${this.isUpdate ? 'updateCurCollect' : 'setCurCollect'}`, Object.assign({}, this.formData, params, res.data));
          this.$emit('stepChange');
          this.setDetail(res.data.collector_config_id);
          this.isHandle = false;
        }
      })
        .finally(() => {
          this.isHandle = false;
        });
    },
    // 处理提交参数
    handleParams() {
      const formData = JSON.parse(JSON.stringify(this.formData));
      const {
        collector_config_name,
        collector_config_name_en,
        target_object_type,
        target_node_type,
        target_nodes,
        data_encoding,
        data_link_id,
        description,
        params,
      } = formData;
      if (this.formData.collector_scenario_id !== 'wineventlog') {
        if (!this.hasMultilineReg) { // 行首正则未开启
          delete params.multiline_pattern;
          delete params.multiline_max_lines;
          delete params.multiline_timeout;
        }
        const { match_type, match_content, separator, separator_filters, type } = params.conditions;
        params.conditions = type === 'match' ? { type, match_type, match_content } : {
          type,
          separator,
          separator_filters,
        };
        params.paths = params.paths.map(item => item.value);
      }
      if (this.isUpdate) { // 编辑
        return {
          collector_config_id: Number(this.$route.params.collectorId),
          collector_config_name,
          collector_config_name_en,
          target_node_type,
          target_object_type,
          target_nodes,
          data_encoding,
          data_link_id,
          description,
          params,
        };
      }  // 新增
      return Object.assign(formData, {
        data_link_id,
        bk_biz_id: this.bkBizId,
      });
    },
    // 选择日志类型
    chooseLogType(item) {
      if (item.is_active) {
        this.formData.collector_scenario_id = item.id;
      }
    },
    // 选择数据分类
    chooseDataClass() {
      // console.log(val)
      /**
                 * 以下为预留逻辑
                 */
      // 当父类为services时，仅能选取动态类型目标；其他父类型目标为静态类型时，切换为serveices时需要做清空判断操作
      // if (['services', 'module'].includes(val)) {
      //     if (this.formData.target_object_type === 'SERVICE') {
      //         this.formData.target_nodes = []
      //     }
      //     this.formData.target_object_type = 'SERVICE'
      // } else {
      //     this.formData.target_object_type = 'HOST'
      // }
    },
    // 切换选择过滤内容
    chooseType(value) {
      this.isString = value === 'match';
      const conditions = this.formData.params.conditions || {};
      if (!this.isString && conditions.separator_filters.length < 1) {
        Object.assign(conditions, {
          separator_filters: [ // 分隔符过滤条件
            { fieldindex: '', word: '', op: '=', logic_op: this.type },
          ],
        });
      }
    },
    // 修改分隔符过滤的并&或
    changeType(value) {
      this.type = value;
      this.formData.params.conditions.separator_filters.map((item) => {
        item.logic_op = value;
      });
    },
    addLog() {
      this.formData.params.paths.push({ value: '' });
    },
    delLog(index) {
      if (this.formData.params.paths.length > 1) {
        this.formData.params.paths.splice(this.formData.params.paths.findIndex((item, ind) => ind === index), 1);
      }
    },
    addWinEvent() {
      const e = this.eventSettingList.map(el => el.type);
      const s = this.selectEventList.map(el => el.id);
      if (e.length !== s.length) {
        const selectFilter = s.filter(v => e.indexOf(v) === -1);
        this.eventSettingList.push({ type: selectFilter[0], list: [], isCorrect: true });
        this.selectDisabledChange(true);
      }
    },
    delWinEvent(index) {
      if (this.eventSettingList.length > 1) {
        this.eventSettingList.splice(this.eventSettingList.findIndex((el, ind) => index === ind), 1);
        this.selectDisabledChange(false);
      }
    },
    selectDisabledChange(state = true) {
      if (this.eventSettingList.length === 1) {
        this.selectEventList.forEach(el => el.isSelect = false);
      }
      if (this.eventSettingList.length === this.selectEventList.length) {
        this.selectEventList.forEach(el => el.isSelect = true);
      }
      for (const eItem of this.eventSettingList) {
        for (const sItem of this.selectEventList) {
          if (eItem.type === sItem.id) {
            sItem.isSelect = state;
          }
        }
      }
    },
    outherBlurRules(input, tags) {
      this.outherRules = !tags.every(el => /^[a-zA-Z /]*$/.test(el));
      tags.length === 0 && (this.outherRules = false);
      const slist = this.selectLogSpeciesList;
      if (slist.length === 1 && slist[0] === 'Outher' && this.outherSpeciesList.length === 0) {
        this.outherRules = true;
      }
    },
    tagBlurRules(item, index) {
      switch (item.type) {
        case 'winlog_event_id':
          this.eventSettingList[index].isCorrect =  item.list.every(el => /^[\d -]+$/.test(el));
          break;
        case 'winlog_level':
          this.eventSettingList[index].isCorrect =  item.list.every(el => /^[A-Za-z]+$/.test(el));
          break;
      }
    },
    addItem() {
      this.formData.params.conditions.separator_filters.push({
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      });
    },
    delItem(index) {
      const { separator_filters } = this.formData.params.conditions;
      if (separator_filters.length > 1) {
        separator_filters.splice(separator_filters.findIndex((item, ind) => index === ind), 1);
      }
    },
    // 取消操作
    cancel() {
      this.$router.push({
        name: 'collection-item',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    // 采集目标选择内容变更
    targetChange(params) { // bk_biz_id, target_object_type, target_node_type, target_nodes
      // this.formData.target_object_type = params.target_object_type
      this.formData.target_node_type = params.target_node_type;
      this.formData.target_nodes = params.target_nodes;
      this.showIpSelectorDialog = false;
      // 触发 bk-form 的表单验证
      this.$refs.formItemTarget.validate('change');
    },
    checkNodes() {
      this.colorRules = !(this.formData.target_nodes && this.formData.target_nodes.length);
      return this.formData.target_nodes.length;
    },
    // 新增的时候更新详情
    setDetail(id) {
      this.$http.request('collect/details', {
        params: { collector_config_id: id },
      }).then((res) => {
        if (res.data) {
          this.$store.commit('collect/setCurCollect', res.data);
        }
      });
    },
  },
};
</script>
<style lang="scss">
  .add-collection-container {
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .king-alert {
      margin: 24px 0 -18px;

      .link {
        color: #3a84ff;
      }
    }

    .add-collection-title {
      width: 100%;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
      padding-top: 38px;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }

    .tips,
    .en-name-tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
    }

    .en-name-tips {
      margin-left: 0;
      margin-top: 8px;
      line-height: 12px;
    }

    .hight-setting {
      width: 100%;
      min-height: 60px;
      margin: 20px 0;

      .icons-downs {
        display: inline-block;
        width: 9px;
        height: 5px;
        background: url('../../images/icons/triangle.png');
        background-size: 100% 100%;
        margin-right: 6px;
        vertical-align: middle;
        margin-top: -3px;
      }

      .icon-left {
        transform: rotate(-90deg);
      }
    }

    .bk-label {
      color: #90929a;
    }

    .bk-form-control {
      width: 320px;
    }

    .multiline-log-container {
      margin: 20px 0;

      .row-container {
        display: flex;
        align-items: center;

        &.second {
          padding-left: 115px;
          margin-top: 10px;
          font-size: 12px;
          color: #63656e;

          .bk-form-item {
            margin: 0 !important;

            .bk-form-content {
              margin: 0 !important;

              .bk-form-control {
                width: 64px;
                margin: 0 6px;
              }
            }
          }
        }
      }
    }

    .form-div {
      display: flex;
      margin-bottom: 20px;

      .form-inline-div {
        .bk-form-content {
          display: flex;
        }
      }

      .prefix {
        font-size: 14px;
        line-height: 32px;
        color: #858790;
        margin-right: 8px;
      }

      .count {
        font-size: 12px;
        line-height: 32px;
        color: #7a7c85;
        margin-left: 8px;
      }

      .font-blue {
        color: #4e99ff;
        font-weight: bold;
      }

      .font-gray {
        color: #858790;
      }

      .icons {
        font-size: 21px;
        vertical-align: middle;
        cursor: pointer;
        color: #979ba5;
        line-height: 32px;
      }

      .disable {
        color: #dcdee5;
        cursor: not-allowed;
      }

      .item-target {
        &.is-error .bk-form-content {
          padding-right: 30px;
        }
      }
    }

    .win-filter{
      .select-div{
        width: 129px;
        margin-right: 8px;
      }
      .tag-input{
        width: 320px;
      }
    }

    .choose-table {
      background: #fff;
      width: 60%;
      height: 100%;
      border: 1px solid #dcdee5;
      margin-left: 115px;
      padding-bottom: 14px;

      .bk-form-content {
        margin-left: 0 !important;
      }

      label {
        width: 0 !important;
      }

      .choose-table-item {
        display: flex;
        height: 32px;
        line-height: 32px;
        padding: 0 20px;
        font-size: 13px;
        color: #858790;
        margin-top: 13px;
        position: relative;

        .left {
          width: 110px;
        }

        .main {
          flex: 1;
          padding-right: 130px;
          position: relative;

          .bk-form-control {
            width: 88%;
          }
        }

        .line {
          .bk-form-control {
            &::before {
              content: '';
              width: 25px;
              height: 1px;
              border-top: 1px dashed #c4c6cc;
              position: absolute;
              left: 100%;
              top: 16px;
            }
          }
        }

        .right {
          width: 60px;
        }
      }

      .choose-table-item-head {
        height: 42px;
        line-height: 42px;
        background: #fafbfd;
        border-bottom: 1px solid #dcdee5;
        margin-top: 0;
      }

      .choose-table-item-body {
        position: relative;
        height: 100%;

        .choose-select {
          height: 100%;
          position: absolute;
          top: 0;
          left: calc(88% - 120px);
          display: flex;
          align-items: center;

          .select-div {
            width: 80px;
          }

          &::before {
            content: '';
            width: 20px;
            height: 1px;
            border-top: 1px dashed #c4c6cc;
            position: absolute;
            right: 80px;
            top: 50%;
          }

          &::after {
            content: '';
            width: 1px;
            height: calc(100% - 32px);
            border-left: 1px dashed #c4c6cc;
            position: absolute;
            right: 100px;
            top: 17px;
          }
        }
      }
    }

    .log-type {
      height: 32px;
      border-radius: 2px;

      .bk-button {
        min-width: 106px;
        font-size: 12px;

        span {
          padding: 0 1px;
        }
      }

      .disable {
        color: #dcdee5;
        cursor: not-allowed;
        border-color: #dcdee5;
      }

      .is-updated {
        background: #fafbfd;
        border-color: #dcdee5;
        color: #63656e;
      }
    }

    .species-item{
      display: flex;
      flex-direction: column;
      position: relative;
      .bk-form-checkbox{
        height: 30px;
        line-height: 30px;
      }
      .bk-tag-selector{
        position: absolute;
        top: 89px;
        left: 65px;
        width: 320px;
      }
    }

    .ml {
      margin-left: -115px;
    }

    .mt {
      margin-top: 20px;
    }

    .ml9 {
      margin-left: 8px;
    }

    .ml10 {
      margin-left: 10px;
    }

    .ml115 {
      margin-left: 115px;
    }

    .is-selected {
      z-index: 2 !important;
    }

    .bk-form .bk-form-content .tooltips-icon {
      left: 330px;
    }

    .rulesColor {
      border-color: #ff5656 !important;
    }

    .tagRulesColor{
      .bk-tag-input{
        border-color: #ff5656 !important;
      }
    }
  }
</style>
