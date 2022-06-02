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
            class="w520"
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
          <div class="config-enName-box">
            <bk-input
              class="w520"
              v-model="formData.collector_config_name_en"
              show-word-limit
              maxlength="50"
              data-test-id="baseMessage_input_fillEnglishName"
              :disabled="isUpdate && !!(formData.collector_config_name_en)"
              :placeholder="$t('dataSource.en_name_tips')"
              @change="clearError">
            </bk-input>
            <p v-show="!configNameEnIsNotRepeat" class="repeat-message">{{$t('dataSource.en_name_repeat')}}</p>
          </div>
          <p class="en-name-tips" slot="tip">{{ $t('dataSource.en_name_placeholder') }}</p>
        </bk-form-item>
        <bk-form-item :label="$t('configDetails.remarkExplain')">
          <bk-input
            class="w520"
            type="textarea"
            v-model="formData.description"
            data-test-id="baseMessage_input_fillDetails"
            maxlength="100">
          </bk-input>
        </bk-form-item>
      </div>

      <!-- 源日志信息 -->
      <div data-test-id="acquisitionConfigur_div_sourceLogBox">
        <div class="add-collection-title">{{ $t('dataSource.Source_log_information') }}</div>
        <!-- 环境选择 -->
        <bk-form-item :label="$t('环境选择')" required>
          <div class="environment-box">
            <div class="environment-container"
                 v-for="(fItem,fIndex) of environmentList"
                 :key="fIndex">
              <span class="environment-category">{{fItem.category}}</span>
              <div class="button-box">
                <div
                  v-for="(sItem,index) of fItem.btnList" :key="index"
                  :class="['environment-button', sItem === currentEnvironment && 'active']"
                  @click="handleSelectEnvironment(sItem)">
                  <span></span>
                  <p>{{sItem}}</p>
                </div>
              </div>
            </div>
          </div>
        </bk-form-item>
        <!-- 物理环境 日志类型 -->
        <bk-form-item v-if="isPhysicsEnvironment" :label="$t('configDetails.logType')" required>
          <div class="bk-button-group log-type">
            <bk-button
              v-for="(item, index) in getCollectorScenario"
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
        <!-- 采集目标 -->
        <div v-if="isPhysicsEnvironment" class="form-div mt">
          <bk-form-item
            class="item-target"
            ref="formItemTarget"
            required
            :label="$t('configDetails.target')"
            :rules="rules.nodes"
            :property="'target_nodes'">
            <bk-button
              theme="default"
              icon="plus"
              style="font-size: 12px"
              data-test-id="sourceLogBox_button_addCollectionTarget"
              :title="$t('configDetails.newly_increased')"
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
        <!-- 物理环境 配置 -->
        <config-log-set-item
          v-if="isPhysicsEnvironment"
          :scenario-id="formData.collector_scenario_id"
          :current-environment="currentEnvironment"
          :config-data="formData"
          @configChange="(val) => handelFormChange(val, 'formConfig')">
        </config-log-set-item>

        <bk-form-item
          v-if="!isPhysicsEnvironment"
          :label="$t('集群选择')"
          :rules="rules.cluster"
          class="cluster-select-box"
          required>
          <div class="cluster-select">
            <bk-select v-model="formData.bcs_cluster_id"></bk-select>
            <span class="tips">123</span>
          </div>
        </bk-form-item>

        <bk-form-item
          v-if="!isPhysicsEnvironment"
          :label="$t('Yaml模式')"
          class="mt8">
          <bk-switcher v-model="isYaml" theme="primary"></bk-switcher>
        </bk-form-item>

        <yaml-editor v-if="isYaml && !isPhysicsEnvironment"></yaml-editor>
        <template v-else>
          <!-- 容器环境 日志类型 -->
          <bk-form-item v-if="!isPhysicsEnvironment" :label="$t('configDetails.logType')" required>
            <div class="bk-button-group log-type">
              <bk-button
                v-for="(item, index) in getCollectorScenario"
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
          <!-- 配置项  容器环境才显示配置项 -->
          <bk-form-item v-if="!isPhysicsEnvironment" :label="$t('配置项')" required>
            <div class="config-box" v-for="(conItem, conIndex) of formData.container_config" :key="conIndex">
              <div class="config-title">
                <span>A</span>
                <span
                  v-if="formData.container_config.length > 1"
                  class="bk-icon icon-close3-shape"
                  @click="handleDeleteConfig(conIndex)"></span>
              </div>

              <div class="config-container">
                <div class="config-item container-select">
                  <span>{{$t('NameSpace选择')}}</span>
                  <bk-select :disabled="isNode"></bk-select>
                  <div class="mt8 justify-bt">
                    <bk-checkbox
                      v-model="conItem.isAllContainer"
                      :disabled="isNode"
                      @change="(state) => handelClickAllContainer(conIndex, state)">
                      {{$t('所有容器')}}
                    </bk-checkbox>
                    <div class="justify-bt container-btn-container">
                      <div
                        v-if="!isContainerHaveValue(conItem.container)"
                        :class="['container-btn', (isNode || conItem.isAllContainer) && 'disable']"
                        @click="handelShowDialog(conIndex, 'container',(isNode || conItem.isAllContainer))">
                        <span class="bk-icon icon-plus-circle-shape"></span>
                        <span>{{$t('指定容器')}}</span>
                      </div>
                      <div
                        v-if="!isSelectorHaveValue(conItem.label_selector)"
                        :class="['container-btn', conItem.isAllContainer && 'disable']"
                        @click="handelShowDialog(conIndex, 'label', conItem.isAllContainer)">
                        <span class="bk-icon icon-plus-circle-shape"></span>
                        <span>{{$t('指定标签')}}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="config-item" v-if="isContainerHaveValue(conItem.container)">
                  <span>{{$t('指定容器')}}</span>
                  <div class="specify">
                    <div class="edit" @click="handelShowDialog(conIndex, 'container')">
                      <span class="bk-icon icon-edit-line"></span>
                      <span>{{$t('编辑')}}</span>
                    </div>
                    <div class="specify-box">
                      <div
                        class="specify-container"
                        v-for="([speKey, speValue], speIndex) in Object.entries(conItem.container)"
                        :key="speIndex">
                        <span v-if="speValue">
                          <span>{{specifyName[speKey]}}</span> : <span>{{speValue}}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="config-item" v-if="isSelectorHaveValue(conItem.label_selector)">
                  <span>{{$t('指定标签')}}</span>
                  <div class="specify">
                    <div class="edit" @click="handelShowDialog(conIndex, 'label')">
                      <span class="bk-icon icon-edit-line"></span>
                      <span>{{$t('编辑')}}</span>
                    </div>
                    <template v-for="(labItem, labKey) in conItem.label_selector">
                      <div class="specify-box"
                           v-for="(matchItem, matchKey) of labItem"
                           :key="`${labKey}_${matchKey}`">
                        <div class="specify-container justify-bt">
                          <span>{{matchItem.key}}</span>
                          <div class="operator">{{matchItem.operator}}</div>
                        </div>
                        <div class="specify-container">
                          <span>{{matchItem.value}}</span>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>

                <div
                  class="hight-setting"
                  data-test-id="acquisitionConfigur_div_contentFiltering">
                  <!-- 容器环境 配置项 -->
                  <config-log-set-item
                    show-type="vertical"
                    :scenario-id="formData.collector_scenario_id"
                    :current-environment="currentEnvironment"
                    :config-data="conItem"
                    :config-length="formData.container_config.length"
                    @configChange="(val) => handelFormChange(val, 'containerConfig', conIndex)">
                  </config-log-set-item>
                </div>
              </div>
            </div>
          </bk-form-item>

          <div v-if="!isPhysicsEnvironment">
            <div class="conflict-container flex-ac">
              <span class="bk-icon icon-exclamation-circle"></span>
              <span class="conflict-message">
                <span>{{$t('冲突检查结果')}}</span> :
                <span>目标重复</span>
              </span>
              <span v-for="index in 4" :key="index" class="collection-item">采集配置{{index}}</span>
            </div>
            <bk-button
              theme="primary"
              size="small"
              outline
              icon="plus"
              class="add-config-item"
              @click="handleAddNewContainerConfig">
              {{$t('添加配置项')}}
            </bk-button>
            <bk-form-item :label="$t('附加日志标签')">
              <div class="add-log-label form-div" v-for="(item, index) in formData.extra_labels" :key="index">
                <bk-input v-model="item.key"></bk-input>
                <span>=</span>
                <bk-input v-model="item.value"></bk-input>
                <div class="ml9">
                  <i :class="['bk-icon icon-plus-circle-shape icons']"
                     @click="handleAddLabel"></i>
                  <i
                    :class="['bk-icon icon-minus-circle-shape icons ml9',
                             { disable: formData.extra_labels.length === 1 }]"
                    @click="handleDeleteLabel(index)"></i>
                </div>
              </div>
              <bk-checkbox v-model="formData.add_pod_label">
                {{$t('是否自动添加Pod中的labels')}}
              </bk-checkbox>
            </bk-form-item>
          </div>
        </template>
      </div>

      <!-- 上报链路配置 -->
      <template v-if="!isCloseDataLink">
        <div class="add-collection-title">{{ $t('上报链路配置') }}</div>
        <bk-form-item required property="data_link_id" :label="$t('上报链路')" :rules="rules.linkConfig">
          <bk-select
            data-test-id="acquisitionConfigur_div_selectReportLink"
            class="w520"
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

      <label-target-dialog
        :is-show-dialog.sync="isShowLabelTargetDialog"
        :label-selector="currentSelector"
        @configLabelChange="(val) => handelFormChange(val, 'dialogChange')">
      </label-target-dialog>

      <container-target-dialog
        :is-show-dialog.sync="isShowContainerTargetDialog"
        :container="currentContainer"
        @configContainerChange="(val) => handelFormChange(val, 'dialogChange')">
      </container-target-dialog>

      <div class="page-operate">
        <bk-button
          theme="primary"
          data-test-id="acquisitionConfigur_div_nextPage"
          :title="$t('retrieve.Start_collecting')"
          :loading="isHandle"
          :disabled="!collectProject"
          @click.stop.prevent="startCollect">
          {{ $t('retrieve.next') }}
        </bk-button>
        <bk-button
          theme="default"
          data-test-id="acquisitionConfigur_div_cancel"
          class="ml10"
          :title="$t('indexSetList.cancel')"
          @click="cancel">
          {{ $t('indexSetList.cancel') }}
        </bk-button>
      </div>
    </bk-form>
  </div>
</template>

<script>
// import MultilineRegDialog from './multiline-reg-dialog';
import ipSelectorDialog from './ip-selector-dialog';
import configLogSetItem from './components/config-log-set-item';
import labelTargetDialog from './components/label-target-dialog';
import containerTargetDialog from './components/container-target-dialog';
import yamlEditor from './components/yaml-editor';
import { mapGetters, mapState } from 'vuex';
import { projectManages } from '@/common/util';
import { deepClone } from '../monitor-echarts/utils';

export default {
  components: {
    ipSelectorDialog,
    labelTargetDialog,
    configLogSetItem,
    containerTargetDialog,
    yamlEditor,
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
        environment: 'container_log_config', // 容器环境
        bcs_cluster_id: '', // 集群ID
        add_pod_label: false, // 是否自动添加Pod中的labels
        extra_labels: [ // 附加日志标签
          {
            key: '',
            value: '',
          },
        ],
        yaml: '这是一个yaml', // yaml
        container_config: [ // 配置项列表
          {
            isAllContainer: false,
            namespaces: [],
            container: {
              workload_type: '',
              workload_name: '',
              container_name: '',
            }, // 容器
            label_selector: { // 指定标签或表达式
              match_labels: [],
              match_expressions: [],
            },
            data_encoding: 'UTF-8',
            params: {
              paths: [{ value: '' }], // 日志路径
              conditions: {
                type: 'match', // 过滤方式类型
                match_type: 'include',  // 过滤方式 可选字段 include, exclude
                match_content: '',
                separator: '',
                separator_filters: [ // 分隔符过滤条件
                  { fieldindex: '', word: '', op: '=', logic_op: 'and' },
                ],
              },
              multiline_pattern: '', // 行首正则, char
              multiline_max_lines: '50', // 最多匹配行数, int
              multiline_timeout: '2', // 最大耗时, int
            },
          },
        ],
      },
      rules: {
        category_id: [ // 数据分类
          {
            required: true,
            trigger: 'blur',
          },
        ],
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
          {
            // 检查英文名是否可用
            validator: this.checkEnName,
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
        cluster: [ // 集群
          {
            required: true,
            trigger: 'blur',
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
      configBaseObj: {}, // 新增配置项的基础对象
      configNameEnIsNotRepeat: true, // 英文名没有重复
      currentEnvironment: '', // 当前选择的环境
      isYaml: false, // 是否是yaml模式
      environmentList: [
        { category: this.$t('物理环境'), btnList: ['Linux', 'Window'] },
        { category: this.$t('容器环境'), btnList: [this.$t('标准输出'), 'container', 'node'] },
      ],
      specifyName: { // 指定容器中文名
        workload_type: this.$t('应用类型'),
        workload_name: this.$t('应用名称'),
        container_name: this.$t('容器名称'),
      },
      allContainer: { // 所有容器时指定容器默认传空
        workload_type: '',
        workload_name: '',
        container_name: '',
      },
      allLabelSelector: { // 所有容器时指定标签和表达式默认传空
        match_labels: [],
        match_expressions: [],
      },
      isShowLabelTargetDialog: false, // 是否展示指定标签dialog
      isShowContainerTargetDialog: false, // 是否展示指定容器dialog
      formTime: null, // form更改防抖timer
      currentSelector: {}, // 当前操作的配置项指定标签值
      currentContainer: {}, // 当前操作的配置项指定容器值
      currentSetIndex: 0, // 档期那操作的配置项的下标
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
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    isCloseDataLink() {
      // 没有可上报的链路时，编辑采集配置链路ID为0或null时，隐藏链路配置框，并且不做空值校验。
      return !this.linkConfigurationList.length || (this.isUpdate && !this.curCollect.data_link_id);
    },
    // 是否是物理环境
    isPhysicsEnvironment() {
      return ['Linux', 'Window'].includes(this.currentEnvironment);
    },
    // 是否是Node环境
    isNode() {
      if (this.currentEnvironment === 'node') {
        this.formData.container_config.forEach((item) => {
          item.isAllContainer = false; // node环境时 所有容器，指定容器禁用
          item.container = this.allContainer;
        });
      }
      return this.currentEnvironment === 'node';
    },
    // 获取日志类型列表
    getCollectorScenario() {
      try {
        if (this.currentEnvironment === 'Window') return this.globalsData.collector_scenario;
        const cloneList = JSON.parse(JSON.stringify(this.globalsData.collector_scenario));
        const winIndex = cloneList.findIndex(item => item.id === 'wineventlog');
        cloneList.splice(winIndex, 1);
        return cloneList;
      } catch (error) {
        return [];
      }
    },
  },
  watch: {
    currentEnvironment: {
      handler(nval, oval) {
        const collectorList = this.globalsData.collector_scenario;
        if (oval === 'Window' && this.formData.collector_scenario_id === 'wineventlog') {
          this.formData.collector_scenario_id = collectorList[0].id;
        }
      },
    },
  },
  created() {
    this.getLinkData();
    this.isUpdate = this.$route.name !== 'collectAdd';
    const isClone = this.$route.query?.type === 'clone';
    this.configBaseObj = deepClone(this.formData.container_config[0]); // 添加配置项基础对象赋值
    // 克隆与编辑均进行数据回填
    if (this.isUpdate || isClone) {
      // this.formData = JSON.parse(JSON.stringify(this.curCollect));
      Object.assign(this.formData, this.curCollect);
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
      // 克隆采集项的时候 清空以下回显或者重新赋值 保留其余初始数据
      if (isClone) {
        this.formData.collector_config_name = `${this.formData.collector_config_name}_clone`;
        this.formData.description = this.formData.description ? `${this.formData.description}_clone` : '';
        this.formData.collector_config_name_en = '';
        this.formData.target_nodes = [];
      } else {
        // 克隆时不缓存初始数据
        // 编辑采集项时缓存初始数据 用于对比提交时是否发生变化 未修改则不重新提交 update 接口
        this.localParams = this.handleParams();
      }
    }
  },
  mounted() {},
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
      // if (this.eventSettingList.some(el => el.isCorrect === false) || this.outherRules) {
      //   return;
      // }
      const params = this.handleParams();
      if (JSON.stringify(this.localParams) === JSON.stringify(params)) {
        // 未修改表单 直接跳转下一步
        this.$emit('stepChange');
        this.isHandle = false;
        return;
      }
      this.$refs.validateForm.validate().then(() => {
        if (this.isCloseDataLink) {
          delete params.data_link_id;
        }
        if (this.formData.collector_scenario_id === 'wineventlog') {
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
        requestUrl = 'collect/updateCollection';
      } else {
        requestUrl = 'collect/addCollection';
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
        // if (!this.hasMultilineReg) { // 行首正则未开启
        //   delete params.multiline_pattern;
        //   delete params.multiline_max_lines;
        //   delete params.multiline_timeout;
        // }
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
    async checkEnName(val) {
      if (this.isUpdate) return true;
      const result = await this.getEnNameIsRepeat(val);
      return result;
    },
    // 检测英文名是否可用
    async getEnNameIsRepeat(val) {
      try {
        const res =  await this.$http.request('collect/getPreCheck', {
          params: { collector_config_name_en: val, bk_biz_id: this.$store.state.bkBizId },
        });
        if (res.data) {
          this.configNameEnIsNotRepeat = res.data.allowed;
          return res.data.allowed;
        }
      } catch (error) {
        this.configNameEnIsNotRepeat = true;
        return false;
      }
    },
    clearError() {
      if (!this.configNameEnIsNotRepeat) {
        this.configNameEnIsNotRepeat = true;
      }
    },
    /**
     * @desc: 环境选择
     * @param name 环境名称
     */
    handleSelectEnvironment(name) {
      this.currentEnvironment = name;
    },
    handleAddLabel() {
      this.formData.extra_labels.push({ key: '', value: '' });
    },
    handleDeleteLabel(index) {
      this.formData.extra_labels.length > 1 && (this.formData.extra_labels.splice(index, 1));
    },
    /**
     * @desc: 用户操作合并form数据
     * @param { Object } val 操作后返回值对象
     * @param { String } operator 配置项还是form本身
     * @param { Number } index 配置项下标
     */
    handelFormChange(val, operator, index) {
      const setIndex = index ? index : this.currentSetIndex;
      const setTime = operator === 'dialogChange' ? 10 : 500;
      clearTimeout(this.formTime);
      this.formTime = setTimeout(() => {
        switch (operator) {
          case 'formConfig':
            Object.assign(this.formData, val);
            break;
          case 'dialogChange':
          case 'containerConfig':
            Object.assign(this.formData.container_config[setIndex], val);
            break;
        }
      }, setTime);
    },
    /**
     * @desc: 配置项点击所有容器
     * @param { Number } index 下标
     * @param { Boolean } state 状态
     */
    handelClickAllContainer(index, state) {
      this.currentSetIndex = index;
      if (state) {
        // 点击所有容器配置项的指定标签和容器都填为空
        this.formData.container_config[index].container = this.allContainer;
        this.formData.container_config[index].label_selector = this.allLabelSelector;
      }
    },
    /**
     * @desc: 指定操作弹窗
     * @param { Number } index 下标
     * @param { String } type 标签或容器
     * @param { Boolean } disable 是否禁用
     */
    handelShowDialog(index, type, disable) {
      if (disable) return;
      this.currentSetIndex = index;
      type === 'label' ?  this.isShowLabelTargetDialog = true : this.isShowContainerTargetDialog = true;
      this.currentSelector = this.formData.container_config[index].label_selector;
      this.currentContainer = this.formData.container_config[index].container;
    },
    handleAddNewContainerConfig() {
      this.formData.container_config.push(deepClone(this.configBaseObj));
    },
    handleDeleteConfig(index) {
      this.formData.container_config.splice(index, 1);
    },
    isSelectorHaveValue(labelSelector) {
      return Object.values(labelSelector).some(item => item.length);
    },
    isContainerHaveValue(container) {
      return Object.values(container).some(item => item);
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/flex.scss';

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

    .log-paths {
      .bk-form-control {
        width: 460px;
      }
    }
  }

  .bk-label {
    color: #90929a;
  }

  .bk-form-control {
    width: 320px;
  }

  .w520 {
    &.bk-form-control {
      width: 520px;
    }

    &.bk-select {
      width: 520px;
    }
  }

  .multiline-log-container {
    margin-top: 20px;

    .row-container {
      display: flex;
      align-items: center;

      &.second {
        // padding-left: 115px;
        margin-top: 10px;
        font-size: 12px;
        color: #63656e;

        .bk-form-item {
          /* stylelint-disable-next-line declaration-no-important */
          margin: 0 !important;

          .bk-form-content {
            /* stylelint-disable-next-line declaration-no-important */
            margin: 0 !important;

            .bk-form-control {
              width: 64px;
              margin: 0 6px;
            }
          }
        }
      }

      .king-button {
        margin-bottom: 4px;
      }

      &.pl115 {
        padding-left: 115px;
      }
    }
  }

  .form-div {
    display: flex;

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

  .win-filter {
    margin-top: 8px;

    .select-div {
      width: 129px;
      margin-right: 8px;
    }

    .tag-input {
      width: 320px;
    }
  }

  .choose-table {
    background: #fff;
    width: 100%;
    height: 100%;
    max-width: 1170px;
    border: 1px solid #dcdee5;
    padding-bottom: 14px;

    .bk-form-content {
      /* stylelint-disable-next-line declaration-no-important */
      margin-left: 0 !important;
    }

    label {
      /* stylelint-disable-next-line declaration-no-important */
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

  .species-item {
    display: flex;
    flex-direction: column;
    position: relative;

    .bk-form-checkbox {
      height: 30px;
      line-height: 30px;
    }

    .bk-tag-selector {
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

  .mt8 {
    margin-top: 8px;
  }

  .is-selected {
    /* stylelint-disable-next-line declaration-no-important */
    z-index: 2 !important;
  }

  .bk-form .bk-form-content .tooltips-icon {
    left: 330px;
  }

  .rulesColor {
    /* stylelint-disable-next-line declaration-no-important */
    border-color: #ff5656 !important;
  }

  .tagRulesColor {
    .bk-tag-input {
      /* stylelint-disable-next-line declaration-no-important */
      border-color: #ff5656 !important;
    }
  }

  .config-enName-box {
    display: flex;

    .repeat-message {
      font-size: 14px;
      margin-left: 6px;
      color: #ff5656;
    }
  }

  .win-content {
    padding-bottom: 20px;
    position: relative;
    left: 115px;

    > span {
      color: #90929a;
      font-size: 14px;
      position: absolute;
      left: -80px;
      top: 6px;
    }

    .filter-select {
      margin-top: 11px;
    }

    .bk-select {
      width: 184px;
      margin: 0 8px 12px 0;
      height: 32px;
    }
  }

  .environment-box {
    display: flex;
    align-items: center;
    margin-bottom: 30px;

    .environment-container {
      height: 68px;
      margin-right: 8px;

      .environment-category {
        display: inline-block;
        font-weight: lighter;
        margin-bottom: 2px;
        color: #63656e;
      }

      .button-box {
        display: flex;

        .environment-button {
          width: 120px;
          height: 40px;
          margin-right: 16px;
          color: #313238;
          border: 1px solid #dcdee5;
          border-radius: 2px;
          display: flex;
          align-items: center;
          cursor: pointer;
          user-select: none;

          &.active {
            background: #e1ecff;
            border: 1px solid #3a84ff;
          }
        }
      }

      &:not(:first-child) {
        margin-left: 24px;
        position: relative;

        &::before {
          content: ' ';
          width: 1px;
          height: 32px;
          background-color: #dcdee5;
          position: absolute;
          left: -24px;
          top: 36px;
        }
      }
    }
  }

  .cluster-select-box {
    margin-top: 20px;

    .bk-select {
      width: 382px;
    }

    .tips {
      font-size: 12px;
      color: #979ba5;
    }
  }

  .config-box {
    width: 730px;
    background: #fff;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    font-size: 14px;
    margin-bottom: 20px;

    .config-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 31px;
      background: #f0f1f5;
      border-radius: 1px 1px 0 0;
      padding: 0 16px;

      .icon-close3-shape {
        color: #ea3636;
        cursor: pointer;
      }
    }

    .config-container {
      padding: 16px 24px;
      color: #63656e;

      .config-item {
        margin-bottom: 16px;

        > span {
          margin-bottom: 4px;
        }
      }

      .container-select {
        width: 300px;
      }

      .container-btn-container {
        align-items: center;
        position: relative;

        .container-btn {
          color: #3a84ff;
          cursor: pointer;

          &.disable {
            color: #c4c6cc;
            cursor: not-allowed;
          }

          &:not(:last-child) {
            margin-right: 24px;
            position: relative;

            &::after {
              content: ' ';
              width: 1px;
              height: 16px;
              background-color: #dcdee5;
              position: absolute;
              left: 87px;
              top: 8px;
            }
          }
        }
      }

      .filter-content {
        color: #979ba5;
        margin-top: 24px;

        > span {
          color: #63656e;
          margin-bottom: 0;
        };
      }

      .filter-select {
        margin-top: 11px;

        .bk-select {
          width: 184px;
          height: 32px
        }
      }

      .specify {
        min-width: 573px;
        position: relative;

        .edit {
          position: absolute;
          right: 0;
          top: -30px;
          color: #3a84ff;
          cursor: pointer;
        }

        .specify-box {
          display: flex;
          flex-flow: wrap;
          padding: 8px 16px;
          margin-bottom: 8px;
          background: #f5f7fa;
          border-radius: 2px;

          .specify-container {
            width: 50%;

            .operator {
              padding: 0 6px;
              height: 24px;
              line-height: 24px;
              text-align: center;
              color: #ff9c01;
              background: #fff;
              border-radius: 2px;
            }

            :last-child {
              margin-left: 12px;
            }
          }
        }
      }

      .bk-label {
        color: #63656e;
      }
    }
  }

  .conflict-container {
    width: 730px;
    height: 32px;
    margin: 12px 0 0 115px;
    font-size: 12px;
    background: #fff4e2;
    border: 1px solid #ffdfac;
    border-radius: 2px;
    padding: 0 11px;

    .icon-exclamation-circle {
      color: #ff9c01;
      font-size: 16px;
    }

    .conflict-message {
      margin: 0 16px 0 9px;
      color: #63656e;
    }

    .collection-item {
      margin-left: 24px;
      color: #3a84ff;
    }
  }

  .add-config-item {
    margin: 14px 0 14px 115px;
  }

  .add-log-label {
    display: flex;

    &:not(:first-child) {
      margin-top: 20px;
    }

    span {
      color: #ff9c01;
      margin: 0 7px;
    }

    .bk-form-control {
      width: 240px;
    }
  }

  .page-operate {
    margin-top: 36px;
  }

  .justify-bt {
    align-items: center;

    @include flex-justify(space-between);
  }

  .flex-ac {
    @include flex-align();
  }
}
</style>
