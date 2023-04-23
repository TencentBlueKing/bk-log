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
    <bk-alert class="king-alert" type="info" closable>
      <div slot="title" class="slot-title-container">
        <i18n path="接入前请查看 {0} ，尤其是在日志量大的情况下请务必提前沟通。">
          <a class="link" @click="handleGotoLink('logCollection')"> {{ $t('接入指引') }}</a>
        </i18n>
      </div>
    </bk-alert>
    <bk-form
      :label-width="labelWidth"
      :model="formData"
      ref="validateForm"
      data-test-id="addNewCollectionItem_form_acquisitionConfig">
      <!-- 基础信息 -->
      <div data-test-id="acquisitionConfig_div_baseMessageBox">
        <div class="add-collection-title">{{ $t('基础信息') }}</div>
        <bk-form-item
          :label="$t('名称')"
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
          ext-cls="en-bk-form"
          :label="$t('英文名')"
          :required="true"
          :rules="rules.collector_config_name_en"
          :icon-offset="120"
          :property="'collector_config_name_en'">
          <div class="en-name-box">
            <div>
              <bk-input
                class="w520"
                v-model="formData.collector_config_name_en"
                show-word-limit
                maxlength="50"
                data-test-id="baseMessage_input_fillEnglishName"
                :disabled="isUpdate && !!formData.collector_config_name_en"
                :placeholder="$t('支持数字、字母、下划线，长短5～50字符')">
              </bk-input>
              <span v-if="!isTextValid" class="text-error">{{formData.collector_config_name_en}}</span>
            </div>
            <span v-bk-tooltips.top="$t('自动转换成正确的英文名格式')">
              <bk-button v-if="!isTextValid" text @click="handleEnConvert">{{$t('自动转换')}}</bk-button>
            </span>
          </div>
          <p class="en-name-tips" slot="tip">{{ $t('英文名用于索引和数据源') }}</p>
        </bk-form-item>
        <bk-form-item :label="$t('备注说明')">
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
      <div data-test-id="acquisitionConfig_div_sourceLogBox">
        <div class="add-collection-title original-title">
          <span>{{ $t('源日志信息') }}</span>
          <div class="flex-ac" v-show="!isPhysicsEnvironment">
            <span>{{$t('Yaml模式')}}</span>
            <div
              v-bk-tooltips.top="{ content: $t('请先选择集群'), delay: 500 }"
              :disabled="!!formData.bcs_cluster_id">
              <bk-switcher
                class="ml10"
                v-model="isYaml"
                theme="primary"
                :disabled="!formData.bcs_cluster_id"
                :pre-check="handelChangeYaml">
              </bk-switcher>
            </div>
          </div>
        </div>
        <!-- 环境选择 -->
        <bk-form-item :label="$t('环境选择')" required>
          <div class="environment-box">
            <div class="environment-container"
                 v-for="(fItem, fIndex) of environmentList"
                 :key="fIndex">
              <span class="environment-category">{{fItem.category}}</span>
              <div class="button-box">
                <div
                  v-for="(sItem, index) of fItem.btnList"
                  :key="index"
                  :class="{
                    'environment-button': true,
                    active: sItem.id === currentEnvironment,
                    disable: sItem.isDisable,
                  }"
                  @click="handleSelectEnvironment(sItem.id, sItem.isDisable)">
                  <img :src="sItem.img" />
                  <p>{{sItem.name}}</p>
                </div>
              </div>
            </div>
          </div>
        </bk-form-item>
        <!-- 数据分类 -->
        <bk-form-item
          required
          :label="$t('数据分类')"
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
                  :name="`${item.name}-${option.name}`">
                  {{ option.name }}
                </bk-option>
              </bk-option-group>
            </template>
          </bk-select>
        </bk-form-item>
        <!-- 物理环境 日志类型 -->
        <bk-form-item v-if="isPhysicsEnvironment" :label="$t('日志类型')" required>
          <div class="bk-button-group log-type">
            <bk-button
              v-for="(item, index) in getCollectorScenario"
              :data-test-id="`sourceLogBox_button_checkoutType${item.id}`"
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
        <!-- 容器环境 日志类型 -->
        <bk-form-item v-else :label="$t('日志类型')" required>
          <div class="bk-button-group log-type">
            <bk-button
              v-for="(item, index) in getCollectorScenario"
              :data-test-id="`sourceLogBox_buttom_checkoutType${item.id}`"
              :key="index"
              :class="{
                'is-selected': item.id === formData.collector_scenario_id,
              }"
              @click="chooseLogType(item)"
            >{{ item.name }}
            </bk-button>
          </div>
        </bk-form-item>
        <!-- 采集目标 -->
        <div v-if="isPhysicsEnvironment" class="form-div mt">
          <bk-form-item
            class="item-target"
            ref="formItemTarget"
            required
            :label="$t('采集目标')"
            :rules="rules.nodes"
            :property="'target_nodes'">
            <bk-button
              theme="default"
              icon="plus"
              style="font-size: 12px"
              data-test-id="sourceLogBox_button_addCollectionTarget"
              :title="$t('新增')"
              :class="colorRules ? 'rulesColor' : ''"
              :disabled="!formData.category_id"
              @click="showIpSelectorDialog = true">
              {{ $t('选择目标') }}
            </bk-button>
            <input type="text" :value="formData.target_nodes" style="display: none">
          </bk-form-item>
          <div class="count" v-if="formData.target_nodes.length">
            <span>{{ collectTargetTarget[formData.target_node_type + '1'] }}</span>
            <span class="font-blue">{{ formData.target_nodes.length }}</span>
            <span>{{ collectTargetTarget[formData.target_node_type + '2'] }}</span>
          </div>
          <!-- 目标选择器 -->
          <log-ip-selector
            mode="dialog"
            allow-host-list-miss-host-id
            :key="bkBizId"
            :height="670"
            :show-dialog.sync="showIpSelectorDialog"
            :value="selectorNodes"
            :show-view-diff="isUpdate"
            :original-value="ipSelectorOriginalValue"
            :panel-list="ipSelectorPanelList"
            @change="handleTargetChange"
          />
          <!-- <ip-selector-dialog
            :show-dialog.sync="showIpSelectorDialog"
            :target-object-type="formData.target_object_type"
            :target-node-type="formData.target_node_type"
            :target-nodes="formData.target_nodes"
            @target-change="targetChange">
          </ip-selector-dialog> -->
        </div>
        <!-- 物理环境 配置项 -->
        <config-log-set-item
          v-if="isPhysicsEnvironment"
          ref="formConfigRef"
          :is-clone-or-update="isCloneOrUpdate"
          :scenario-id="formData.collector_scenario_id"
          :current-environment="currentEnvironment"
          :config-data="formData"
          @configChange="(val) => handelFormChange(val, 'formConfig')">
        </config-log-set-item>

        <bk-form-item
          v-if="!isPhysicsEnvironment"
          class="cluster-select-box"
          required
          :label="$t('集群选择')"
          :rules="rules.bcs_cluster_id"
          :property="'bcs_cluster_id'">
          <div class="cluster-select">
            <bk-select
              v-model="formData.bcs_cluster_id"
              searchable
              :disabled="isUpdate || isRequestCluster"
              :clearable="false"
              @change="handelClusterChange">
              <bk-option
                v-for="(cluItem, cluIndex) of localClusterList"
                :key="cluIndex"
                :id="cluItem.id"
                :name="cluItem.name">
              </bk-option>
            </bk-select>
            <!-- <span class="tips">说明详情</span> -->
          </div>
        </bk-form-item>

        <yaml-editor
          v-if="isYaml && !isPhysicsEnvironment"
          v-model="formData.yaml_config"
          ref="yamlEditorRef"
          value-type="base64"
          :yaml-form-data.sync="yamlFormData"
          :cluster-id="formData.bcs_cluster_id"
        ></yaml-editor>

        <template v-else>
          <!-- 配置项  容器环境才显示配置项 -->
          <bk-form-item v-if="!isPhysicsEnvironment" :label="$t('配置项')" required>
            <div
              class="config-box"
              v-en-style="'width: 790px;'"
              v-for="(conItem, conIndex) of formData.configs"
              :key="conIndex">
              <div class="config-title">
                <span>{{getFromCharCode(conItem.noQuestParams.letterIndex)}}</span>
                <span
                  v-if="formData.configs.length > 1"
                  class="bk-icon icon-delete"
                  @click="handleDeleteConfig(conIndex, conItem.noQuestParams.letterIndex)"></span>
              </div>

              <div class="config-container">
                <div class="config-cluster-box">
                  <div class="config-cluster-title justify-bt">
                    <div>
                      <span class="title">{{$t('选择{n}范围', { n: isNode ? $t('节点') : $t('容器') })}}</span>
                      <span>
                        <span class="bk-icon icon-info-circle"></span>
                        <span>{{$t('所有选择范围可相互叠加并作用')}}</span>
                      </span>
                    </div>
                    <div
                      v-bk-tooltips.top="{ content: $t('请先选择集群'), delay: 500 }"
                      :class="['preview', !formData.bcs_cluster_id && 'disable']"
                      :disabled="!!formData.bcs_cluster_id"
                      @click="handelShowDialog(conIndex, 'view')">
                      <span class="bk-icon icon-eye"></span>
                      <span>{{$t('预览')}}</span>
                    </div>
                  </div>
                  <div
                    class="config-item hover-light"
                    v-if="isShowScopeItem(conIndex, 'namespace')">
                    <div class="config-item-title flex-ac">
                      <span>{{$t('按NameSpace选择')}}</span>
                      <span
                        class="bk-icon icon-delete"
                        @click="handleDeleteConfigParamsItem(conIndex, 'namespace')">
                      </span>
                    </div>
                    <div
                      v-bk-tooltips.top="{ content: $t('请先选择集群'), delay: 500 }"
                      :disabled="!!formData.bcs_cluster_id">
                      <bk-select
                        v-model="conItem.namespaces"
                        multiple
                        display-tag
                        searchable
                        :disabled="isNode || !formData.bcs_cluster_id || nameSpaceRequest"
                        @selected="(option) => handleNameSpaceSelect(option, conIndex)">
                        <bk-option
                          v-for="oItem in nameSpacesSelectList"
                          :key="oItem.id"
                          :name="oItem.name"
                          :id="oItem.id"
                        ></bk-option>
                      </bk-select>
                    </div>
                  </div>

                  <div class="config-item" v-if="isShowScopeItem(conIndex, 'label')">
                    <div class="config-item-title flex-ac">
                      <span>{{$t('按标签选择{n}', { n: isNode ? $t('节点') : $t('容器') })}}</span>
                      <span
                        class="bk-icon icon-delete"
                        @click="handleDeleteConfigParamsItem(conIndex, 'label')">
                      </span>
                    </div>
                    <div v-if="!conItem.noQuestParams.handleEditLabel" class="select-label flex-ac">
                      <div class="manually" @click="handleEnterLabel(conIndex, true)">
                        <span class="bk-icon icon-close-circle"></span>
                        <span>{{$t('手动输入标签')}}</span>
                      </div>
                      <div class="select" @click="handelShowDialog(conIndex, 'label')">
                        <span class="bk-icon icon-close-circle"></span>
                        <span>{{$t('选择已有标签')}}</span>
                      </div>
                    </div>
                    <match-label-item
                      v-else
                      only-show-select-edit
                      :match-item="conItem.noQuestParams.editLabelValue"
                      :submit-edit="(val) => handleSubmitExpressions(conIndex, val)"
                      @cancelEdit="handleEnterLabel(conIndex, false)" />
                    <div class="specify-domain">
                      <template v-for="labItem in conItem.labelSelector">
                        <match-label-item
                          show-edit
                          :key="labItem.id"
                          :active-label-edit-i-d.sync="activeLabelEditID"
                          :match-item="labItem"
                          :submit-edit="(val) => handleLabelEdit(conIndex, labItem.id, val)"
                          @deleteItem="deleteLabItem(conIndex, labItem.id)"
                        />
                      </template>
                    </div>
                  </div>

                  <div class="config-item hover-light" v-if="isShowScopeItem(conIndex, 'load')">
                    <div class="config-item-title flex-ac">
                      <span>{{$t('按工作负载选择')}}</span>
                      <span
                        class="bk-icon icon-delete"
                        @click="handleDeleteConfigParamsItem(conIndex, 'load')">
                      </span>
                    </div>
                    <container-target-item
                      :container.sync="conItem.container"
                      :bcs-cluster-id="formData.bcs_cluster_id"
                      :con-item="conItem"
                      :type-list="typeList" />
                  </div>

                  <div class="config-item hover-light" v-if="isShowScopeItem(conIndex, 'containerName')">
                    <div class="config-item-title flex-ac">
                      <span>{{$t('容器名')}}</span>
                      <span
                        class="bk-icon icon-delete"
                        @click="handleDeleteConfigParamsItem(conIndex, 'containerName')">
                      </span>
                    </div>
                    <bk-tag-input
                      v-model="conItem.containerNameList"
                      allow-create
                      free-paste
                      has-delete-icon
                      ext-cls="container-input"
                      @change="() => handleContainerNameChange(conIndex)"
                      @blur="(inputStr, list) => handleContainerNameBlur(inputStr, list, conIndex)">
                    </bk-tag-input>
                  </div>

                  <bk-dropdown-menu
                    v-if="isShowAddScopeButton(conIndex)"
                    style="margin-left: 12px;"
                    :disabled="!formData.bcs_cluster_id">
                    <div slot="dropdown-trigger">
                      <div
                        v-bk-tooltips.top="{ content: $t('请先选择集群'), delay: 500 }"
                        :disabled="!!formData.bcs_cluster_id">
                        <bk-button
                          theme="primary"
                          size="small"
                          outline
                          icon="plus"
                          :disabled="!formData.bcs_cluster_id">
                          {{$t('添加范围')}}
                        </bk-button>
                      </div>
                    </div>
                    <ul class="bk-dropdown-list" slot="dropdown-content">
                      <li
                        v-for="(isShowScope, scopeStr) in conItem.noQuestParams.scopeSelectShow"
                        v-show="isShowScopeButton(conIndex, scopeStr)"
                        :key="`${scopeStr}`"
                        @click="handleAddNewScope(conIndex, scopeStr)">
                        <a href="javascript:;">{{getScopeName(scopeStr)}}</a>
                      </li>
                    </ul>
                  </bk-dropdown-menu>
                </div>

                <div
                  class="hight-setting"
                  data-test-id="acquisitionConfig_div_contentFiltering">
                  <!-- 容器环境 配置项 -->
                  <config-log-set-item
                    show-type="vertical"
                    ref="containerConfigRef"
                    :is-clone-or-update="isCloneOrUpdate"
                    :scenario-id="formData.collector_scenario_id"
                    :current-environment="currentEnvironment"
                    :config-data="conItem"
                    :config-length="formData.configs.length"
                    @configChange="(val) => handelFormChange(val, 'containerConfig', conIndex)">
                  </config-log-set-item>
                </div>
              </div>
            </div>
          </bk-form-item>

          <div v-if="!isPhysicsEnvironment">
            <!-- <div v-show="isConfigConflict" class="conflict-container flex-ac">
              <span class="bk-icon icon-exclamation-circle"></span>
              <span class="conflict-message">
                <span>{{$t('冲突检查结果')}}</span> :
                <span>{{conflictMessage}}</span>
              </span>
              <span v-for="item in conflictList" :key="item" class="collection-item">配置{{index}}</span>
            </div> -->
            <div
              class="add-config-item"
              v-en-style="'margin-left: 140px; width: 790px;'"
              @click="handleAddNewContainerConfig">
              <div>
                <span class="bk-icon icon-plus"></span> {{$t('添加配置项')}}
              </div>
            </div>
            <bk-form-item :label="$t('附加日志标签')">
              <div class="add-log-label form-div"
                   v-for="(item, index) in formData.extra_labels"
                   :key="index">
                <bk-input
                  v-model.trim="item.key"
                  :class="{ 'extra-error': item.key === '' && isExtraError }"
                  @blur="isExtraError = false"></bk-input>
                <span>=</span>
                <bk-input
                  v-model.trim="item.value"
                  :class="{ 'extra-error': item.value === '' && isExtraError }"
                  @blur="isExtraError = false"></bk-input>
                <div class="ml9">
                  <i :class="['bk-icon icon-plus-circle-yuan icons']"
                     @click="handleAddExtraLabel"></i>
                  <i :class="['bk-icon icon-minus-circle-shape icons ml9',
                              { disable: formData.extra_labels.length === 1 }]"
                     @click="handleDeleteExtraLabel(index)"></i>
                </div>
              </div>
              <bk-checkbox class="mt8" v-model="formData.add_pod_label">
                {{$t('是否自动添加Pod中的labels')}}
              </bk-checkbox>
            </bk-form-item>
          </div>
        </template>
      </div>

      <!-- 上报链路配置 -->
      <template v-if="!isCloseDataLink">
        <div class="add-collection-title">{{ $t('链路配置') }}</div>
        <bk-form-item required property="data_link_id" :label="$t('上报链路')" :rules="rules.linkConfig">
          <bk-select
            data-test-id="acquisitionConfig_div_selectReportLink"
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
        :label-params="currentSelector"
        @configLabelChange="(val) => handelFormChange(val, 'dialogChange')" />

      <config-view-dialog
        :is-show-dialog.sync="isShowViewDialog"
        :is-node="isNode"
        :view-query-params="viewQueryParams" />

      <!-- <bk-dialog
        v-model="isShowSubmitErrorDialog"
        theme="primary"
        header-position="left"
        :mask-close="false">
        {{submitErrorMessage}}
      </bk-dialog> -->

      <div class="page-operate">
        <bk-button
          theme="primary"
          data-test-id="acquisitionConfig_div_nextPage"
          :title="$t('开始采集')"
          :loading="isHandle"
          :disabled="!collectProject"
          @click.stop.prevent="startCollect">
          {{ $t('下一步') }}
        </bk-button>
        <bk-button
          theme="default"
          data-test-id="acquisitionConfig_div_cancel"
          class="ml10"
          :title="$t('取消')"
          @click="cancel">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </bk-form>
  </div>
</template>

<script>
import ContainerSvg from '@/images/container-icons/Container.svg';
import LinuxSvg from '@/images/container-icons/Linux.svg';
import NodeSvg from '@/images/container-icons/Node.svg';
import StdoutSvg from '@/images/container-icons/Stdout.svg';
import WindowsSvg from '@/images/container-icons/Windows.svg';
import LogIpSelector, { toTransformNode, toSelectorNode } from '@/components/log-ip-selector/log-ip-selector';
// import ipSelectorDialog from './ip-selector-dialog';
import configLogSetItem from './components/step-add/config-log-set-item';
import labelTargetDialog from './components/step-add/label-target-dialog';
import containerTargetItem from './components/step-add/container-target-item';
import yamlEditor from './components/step-add/yaml-editor';
import matchLabelItem from './components/step-add/match-label-item';
import configViewDialog from './components/step-add/config-view-dialog';
import { mapGetters } from 'vuex';
import { projectManages, random } from '@/common/util';
import { deepClone } from '../monitor-echarts/utils';

export default {
  components: {
    LogIpSelector,
    // ipSelectorDialog,
    labelTargetDialog,
    configLogSetItem,
    containerTargetItem,
    yamlEditor,
    matchLabelItem,
    configViewDialog,
  },
  props: {
    isUpdate: {
      type: Boolean,
      require: true,
    },
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
            type: '', // 过滤方式类型 match separator
            match_type: 'include', // 过滤方式 可选字段 include, exclude
            match_content: '',
            separator: '|',
            separator_filters: [ // 分隔符过滤条件
              { fieldindex: '', word: '', op: '=', logic_op: 'and' },
            ],
          },
          winlog_name: [], // windows事件名称
          winlog_level: [], // windows事件等级
          winlog_event_id: [], // windows事件id
        },
        environment: 'linux', // 容器环境
        bcs_cluster_id: '', // 集群ID
        add_pod_label: false, // 是否自动添加Pod中的labels
        extra_labels: [ // 附加日志标签
          {
            key: '',
            value: '',
          },
        ],
        yaml_config: '', // yaml base64
        yaml_config_enabled: false, // 是否以yaml模式结尾
        configs: [ // 配置项列表
          {
            namespaces: [],
            noQuestParams: {
              letterIndex: 0,
              handleEditLabel: false,
              editLabelValue: {
                key: '',
                operator: '',
                value: '',
              },
              scopeSelectShow: {
                namespace: false,
                label: true,
                load: true,
                containerName: true,
              },
              namespaceStr: '',
            },
            container: {
              workload_type: '',
              workload_name: '',
              container_name: '',
            }, // 容器
            containerNameList: [], // 容器名列表
            labelSelector: [], // 展示用的标签或表达式数组
            label_selector: { // 指定标签或表达式
              match_labels: [],
              match_expressions: [],
            },
            data_encoding: 'UTF-8',
            params: {
              paths: [{ value: '' }], // 日志路径
              conditions: {
                type: '', // 过滤方式类型 match separator
                match_type: 'include',  // 过滤方式 可选字段 include, exclude
                match_content: '',
                separator: '|',
                separator_filters: [ // 分隔符过滤条件
                  { fieldindex: '', word: '', op: '=', logic_op: 'and' },
                ],
              },
              multiline_pattern: '', // 行首正则, char
              multiline_max_lines: '50', // 最多匹配行数, int
              multiline_timeout: '2', // 最大耗时, int
              winlog_name: [], // windows事件名称
              winlog_level: [], // windows事件等级
              winlog_event_id: [], // windows事件id
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
        collector_config_name: [ // 采集名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            message: this.$t('不能多于50个字符'),
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
            message: this.$t('不能多于50个字符'),
            trigger: 'blur',
          },
          {
            min: 5,
            message: this.$t('不能少于5个字符'),
            trigger: 'blur',
          },
          {
            validator: this.checkEnNameValidator,
            message: this.$t('只支持输入字母，数字，下划线'),
            trigger: 'blur',
          },
          {
            // 检查英文名是否可用
            validator: this.checkEnNameRepeat,
            message: this.$t('该英文名已重复'),
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
        bcs_cluster_id: [ // 集群
          {
            required: true,
            trigger: 'blur',
          },
        ],
      },
      isTextValid: true,
      isHandle: false,
      isClone: false,
      globals: {},
      localParams: {}, // 缓存的初始数据 用于对比编辑时表单是否有属性更改
      showIpSelectorDialog: false,
      collectTargetTarget: { // 已(动态)选择 静态主机 节点 服务模板 集群模板
        INSTANCE1: this.$t('已选择'),
        INSTANCE2: this.$t('个静态主机'),
        TOPO1: this.$t('已动态选择'),
        TOPO2: this.$t('个节点'),
        SERVICE_TEMPLATE1: this.$t('已选择'),
        SERVICE_TEMPLATE2: this.$t('个服务模板'),
        SET_TEMPLATE1: this.$t('已选择'),
        SET_TEMPLATE2: this.$t('个集群模板'),
      },
      configBaseObj: {}, // 新增配置项的基础对象
      isYaml: false, // 是否是yaml模式
      yamlFormData: {}, // yaml请求成功时的表格数据
      currentEnvironment: 'linux', // 当前选中的环境
      environmentList: [
        {
          category: this.$t('物理环境'),
          btnList: [
            { id: 'linux', img: LinuxSvg, name: 'Linux', isDisable: false },
            { id: 'windows', img: WindowsSvg, name: 'Windows', isDisable: false },
          ],
        },
        {
          category: this.$t('容器环境'),
          btnList: [
            { id: 'container_log_config', img: ContainerSvg, name: 'Container', isDisable: false },
            { id: 'node_log_config', img: NodeSvg, name: 'Node', isDisable: false },
            { id: 'std_log_config', img: StdoutSvg, name: this.$t('标准输出'), isDisable: false },
          ],
        },
      ],
      typeList: [],
      scopeNameList: {
        namespace: this.$t('按命名空间选择'),
        label: this.$t('按标签选择{n}', { n: this.isNode ? this.$t('节点') : this.$t('容器') }),
        load: this.$t('按工作负载选择'),
        containerName: this.$t('直接指定容器名'),
      },
      baseLabelSelector: { // 指定标签或表达式
        match_labels: [],
        match_expressions: [],
      },
      viewQueryParams: {}, // 预览弹窗传参
      isRequestCluster: false, // 集群列表是否正在请求
      // isConfigConflict: false, // 配置项是否有冲突
      conflictList: [], // 冲突列表
      conflictMessage: '', // 冲突信息
      clusterList: [], // 集群列表
      nameSpacesSelectList: [], // namespace 列表
      allContainer: { // 所有容器时指定容器默认传空
        workload_type: '',
        workload_name: '',
        container_name: '',
      },
      activeLabelEditID: '',
      publicLetterIndex: 0, // 公共的字母下标
      isShowLabelTargetDialog: false, // 是否展示指定标签dialog
      isShowViewDialog: false, // 是否展预览dialog
      formTime: null, // form更改防抖timer
      currentSelector: {}, // 当前操作的配置项指定标签值
      currentSetIndex: 0, // 当前操作的配置项的下标
      isExtraError: false, // 附加标签是否有出错
      nameSpaceRequest: false, // 是否正在请求namespace接口
      uiconfigToYamlData: {}, // 切换成yaml时当前保存的ui配置
      // ip选择器面板
      ipSelectorPanelList: [
        'staticTopo',
        'dynamicTopo',
        'serviceTemplate',
        'setTemplate',
        'manualInput',
      ],
      // 编辑态ip选择器初始值
      ipSelectorOriginalValue: null,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters('globals', ['globalsData']),
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    isCloseDataLink() {
      // 没有可上报的链路时，编辑采集配置链路ID为0或null时，隐藏链路配置框，并且不做空值校验。
      return !this.linkConfigurationList.length || (this.isUpdate && !this.curCollect.data_link_id);
    },
    // 是否打开行首正则功能
    hasMultilineReg() {
      return this.formData.collector_scenario_id === 'section';
    },
    // 是否是wineventlog日志
    isWinEventLog() {
      return this.formData.collector_scenario_id === 'wineventlog';
    },
    // 是否是物理环境
    isPhysicsEnvironment() {
      const isPhysics = ['linux', 'windows'].includes(this.currentEnvironment);
      this.$emit('update:isPhysics', isPhysics);
      return isPhysics;
    },
    // 是否是Node环境
    isNode() {
      if (this.currentEnvironment === 'node_log_config') {
        this.formData.configs.forEach((item) => {
          item.container = this.allContainer;
          item.namespaces = [];
        });
      };
      return this.currentEnvironment === 'node_log_config';
    },
    // 获取日志类型列表
    getCollectorScenario() {
      try {
        const activeScenario = this.globalsData.collector_scenario.filter(item => item.is_active);
        if (this.currentEnvironment === 'windows') return activeScenario;
        const winIndex = activeScenario.findIndex(item => item.id === 'wineventlog');
        activeScenario.splice(winIndex, 1);
        return activeScenario;
      } catch (error) {
        return [];
      }
    },
    // 是否是编辑或者克隆
    isCloneOrUpdate() {
      return this.isUpdate || this.isClone;
    },
    localClusterList() {
      return this.clusterList.filter(val => (this.isNode ? !val.is_shared : true));
    },
    // ip选择器选中节点
    selectorNodes() {
      return this.getSelectorNodes();
    },
    updateCollectorConfigID() { // 若是新增容器日志 返回上一步 则使用curCollect缓存的collector_config_id更新;
      const { collectorId } = this.$route.params;
      return !!collectorId ? Number(collectorId) : Number(this.curCollect.collector_config_id);
    },
    labelWidth() {
      return this.$store.state.isEnLanguage ? 140 : 115;
    },
  },
  watch: {
    currentEnvironment(nVal, oVal) {
      if (oVal === 'windows' && this.isWinEventLog) {
        this.formData.collector_scenario_id = this.globalsData.collector_scenario[0].id;
      }
      if (['std_log_config', 'container_log_config', 'node_log_config'].includes(nVal)) {
        this.formData.environment = 'container';
        !this.clusterList.length && this.getBcsClusterList();
        !this.typeList.length && this.getWorkLoadTypeList();
        if (nVal === 'node_log_config' && this.getIsSharedCluster()) { // 选中node环境时 如果存在已选的共享集群 则清空
          this.formData.bcs_cluster_id = '';
        }
        return;
      };
      this.formData.environment = nVal;
    },
    'formData.bcs_cluster_id'(nVal, oVal) {
      this.getNameSpaceList(nVal, oVal === '');
    },
    'formData.extra_labels.length'() {
      this.isExtraError = false;
    },
    yamlFormData: {
      deep: true,
      handler(val) {
        if (val && val.configs.length) {
          this.currentEnvironment = val.configs[0].collector_type;
        }
      },
    },
  },
  created() {
    this.isClone = this.$route.query?.type === 'clone';
    this.$store.commit('updateRouterLeaveTip', false);
    this.configBaseObj = deepClone(this.formData.configs[0]); // 生成配置项的基础对象
    this.getLinkData();
    // 克隆与编辑均进行数据回填
    if (this.isUpdate || this.isClone) {
      const cloneCollect = JSON.parse(JSON.stringify(this.curCollect));
      if (cloneCollect.environment === 'container') { // 容器环境
        this.getWorkLoadTypeList();
        this.isYaml = cloneCollect.yaml_config_enabled;
        // yaml模式可能会有多种容器环境 选择第一项配置里的环境作为展示
        this.currentEnvironment = cloneCollect.configs[0].collector_type;
        this.publicLetterIndex = cloneCollect.configs.length - 1;
        const initFormData = this.initContainerFormData(cloneCollect);
        Object.assign(this.formData, initFormData);
        // 若是容器环境 克隆时 初始化物理环境的值
        this.formData.params = this.configBaseObj.params;
        this.formData.data_encoding = 'UTF-8';
      } else { // 物理环境
        this.currentEnvironment = cloneCollect.environment;
        Object.assign(this.formData, cloneCollect);
        if (this.formData.target_nodes?.length) { // IP 选择器预览结果回填
          this.ipSelectorOriginalValue = this.getSelectorNodes();
        }
        if (!this.formData.collector_config_name_en) { // 兼容旧数据英文名为空
          this.formData.collector_config_name_en = this.formData.table_id || '';
        }
      }
      // 克隆采集项的时候 清空以下回显或者重新赋值 保留其余初始数据
      if (this.isClone) {
        this.formData.collector_config_name = `${this.formData.collector_config_name}_clone`;
        this.formData.collector_config_name_en = '';
        this.formData.target_nodes = [];
      } else {
        // 编辑且非克隆则禁用另一边的环境按钮
        this.initBtnListDisable();
        this.$nextTick(() => {
        // 克隆时不缓存初始数据
        // 编辑采集项时缓存初始数据 用于对比提交时是否发生变化 未修改则不重新提交 update 接口
          this.localParams = this.handleParams();
        });
      }
    }
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
        if (this.linkConfigurationList.length && !this.isCloneOrUpdate) {
          this.formData.data_link_id = this.linkConfigurationList[0].data_link_id;
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    /**
     * @desc: 初始化编辑的form表单值
     * @param { Object } formData 基础表单
     * @param { Boolean } isYamlData 是否是yaml解析出的表单数据
     * @returns { Object } 返回初始化后的Form表单
     */
    initContainerFormData(formData, isYamlData = false) {
      const curFormData = deepClone(formData);
      if (!curFormData.extra_labels.length) {
        curFormData.extra_labels = [{
          key: '',
          value: '',
        }];
      }
      const filterConfigs = curFormData.configs.map((item, index) => {
        const {
          workload_name,
          workload_type,
          container_name,
          match_expressions: matchExpressions,
          match_labels: matchLabels,
          data_encoding,
          params,
          namespaces: itemNamespace,
          container: yamlContainer,
          label_selector: yamlSelector,
          collector_type,
        } = item;
        const namespaces = item.any_namespace ? ['*'] : itemNamespace;
        const container =  {
          workload_type,
          workload_name,
          container_name,
        };
        // eslint-disable-next-line camelcase
        let labelSelector = [
          ...matchLabels.map(item => ({ ...item, id: random(10), type: 'match_labels' })),
          ...matchExpressions.map(item => ({ ...item, id: random(10), type: 'match_expressions' })),
        ];
        let containerNameList = this.getContainerNameList(container_name);
        if (isYamlData) {
          Object.assign(container, yamlContainer);
          labelSelector = Object.entries(yamlSelector).reduce((pre, [labelKey, labelVal]) => {
            pre.push(...labelVal.map(item => ({ ...item, id: random(10), type: labelKey })));
            return pre;
          }, []);
          containerNameList = this.getContainerNameList(yamlContainer.container_name);
          params.paths = params.paths.length ? item.paths.map(item => ({ value: item })) : [{ value: '' }];
        } else {
          if (!params.conditions?.separator_filters) {
            params.conditions.separator_filters = [{ fieldindex: '', word: '', op: '=', logic_op: 'and' }];
          }
        };
        const scopeNameSpaceShow = Boolean(namespaces.length);
        const scopeLabelShow = Boolean(labelSelector.length);
        const scopeContainerNameShow = Boolean(containerNameList.length);
        const scopeLoadNameShow = Boolean(container.workload_type) || Boolean(container.workload_name);
        return {
          namespaces,
          noQuestParams: {
            letterIndex: index, // 配置项字母下标
            handleEditLabel: false,
            editLabelValue: {
              key: '',
              operator: '',
              value: '',
            },
            scopeSelectShow: {
              namespace: !scopeNameSpaceShow,
              label: !scopeLabelShow,
              load: !scopeLoadNameShow,
              containerName: !scopeContainerNameShow,
            },
            namespaceStr: '',
          },
          data_encoding,
          container,
          labelSelector,
          containerNameList,
          params,
          collector_type,
        };
      });
      curFormData.configs = filterConfigs;
      return curFormData;
    },
    getContainerNameList(containerName = '') {
      const splitList = containerName.split(',');
      if (splitList.length === 1 && splitList[0] === '') return [];
      return splitList;
    },
    // 开始采集
    async startCollect() {
      const isCanSubmit = await this.submitDataValidate();
      if (!isCanSubmit) return;
      const params = this.handleParams();
      if (this.objCompare(this.localParams, params)) {
        // 未修改表单 直接跳转下一步
        this.$emit('stepChange');
        this.isHandle = false;
        return;
      }
      this.$refs.validateForm.validate().then(() => {
        this.isCloseDataLink && delete params.data_link_id;
        this.isPhysicsEnvironment ? this.setCollection(params) : this.setContainerCollection(params);
      }, () => {});
    },
    /**
     * @desc: 提交表格时验证是否通过
     * @return { Boolean } 是否可以提交
     */
    async submitDataValidate() {
      try { // 基础信息表格验证
        await this.$refs.validateForm.validate();
      } catch (error) {}
      // win日志类型验证
      if (this.$refs.formConfigRef?.winCannotPass && this.isWinEventLog) return false;
      // 物理环境验证
      if (this.isPhysicsEnvironment) {
        let formValidate = true;
        try {
          await this.$refs.formConfigRef.$refs.validateForm.validate();
        } catch (error) {
          formValidate = false;
        }
        return formValidate;
      }
      // 容器环境并且打开yaml模式时进行yaml语法检测
      if (this.isYaml && !this.isPhysicsEnvironment) {
        if (!this.$refs.yamlEditorRef.getSubmitState || this.formData.yaml_config === '') {
          let message = this.$refs.yamlEditorRef.isHaveCannotSubmitWaring
            ? this.$t('yaml缺少必要的字段')
            : this.$t('yaml语法出错');
          this.formData.yaml_config === '' && (message = this.$t('yaml不能为空'));
          this.$bkMessage({ theme: 'error', message });
          return false;
        }
        return true;
      }
      // 容器环境时 进行配置项检查
      if (!this.isPhysicsEnvironment) {
        let containerConfigValidate = true;
        const configList = this.$refs.containerConfigRef;
        // 标准输出环境下配置项里过滤内容是否有分隔符过滤 有则进行配置项form校验
        const isCheckConfigItem = !(this.currentEnvironment === 'std_log_config' && this.formData.collector_scenario_id === 'row');
        // 检查配置项中是否有分隔符过滤
        const isHaveSeparator = configList.some(item => item.subFormData.params.conditions.type === 'separator');
        // 当容器环境不为标准输出且不为行日志文件时进行配置项form校验
        if (isCheckConfigItem || isHaveSeparator) {
          // 检查是否含有字段提取
          const matchIndexList = configList.reduce((pre, cur, index) => {
            cur.subFormData.params.conditions.type === 'match' && pre.push(index);
            return pre;
          }, []);
          // 获取应该检查的配置项的数量
          const checkLength = !isCheckConfigItem && matchIndexList.length
            ? (configList.length - matchIndexList.length)
            : configList.length;
          let validateLength = 0;
          for (const key in configList) {
            const index = Number(key);
            // 如果有字符串过滤且非标准输出非行日志的情况下则不进行验证直接跳过
            if (!isCheckConfigItem && matchIndexList.includes(index)) continue;
            try {
              // 这里如果表单没有校验的dom元素会一直是pending状态 没有返回值
              await configList[index].$refs.validateForm.validate();
              validateLength += 1;
            } catch (error) {
              continue;
            }
          }
          validateLength !== checkLength && (containerConfigValidate = false);
        }
        // 附加日志标签是否只单独填写了一边
        this.isExtraError = this.formData.extra_labels.some((item) => {
          const extraFillLength = Object.values(item).reduce((pre, cur) => {
            cur === '' && (pre += 1);
            return pre;
          }, 0);
          return extraFillLength === 1;
        });
        if (!containerConfigValidate || this.isExtraError) return false;
        if (this.getIsSharedCluster() && this.formData.configs.some(conf => !conf.namespaces.length)) {
          // 容器环境下选择了共享集群 但NameSpace为空
          this.$bkMessage({ theme: 'error', message: this.$t('配置项命名空间不能为空') });
          return false;
        }
      }
      return true;
    },
    // 新增/修改采集
    setCollection(params) {
      this.isHandle = true;
      const urlParams = {};
      let requestUrl;
      if (this.isUpdate) {
        urlParams.collector_config_id = this.updateCollectorConfigID;
        requestUrl = 'collect/updateCollection';
      } else {
        requestUrl = 'collect/addCollection';
      }
      const updateData = { params: urlParams, data: params };
      this.$http.request(requestUrl, updateData).then((res) => {
        if (res.code === 0) {
          this.$store.commit(`collect/${this.isUpdate ? 'updateCurCollect' : 'setCurCollect'}`, Object.assign({}, this.formData, params, res.data));
          this.$emit('stepChange');
          this.$emit('update:is-update', true); // 新建成功,更新是否是编辑状态
          this.setDetail(res.data.collector_config_id);
        }
      })
        .finally(() => {
          this.isHandle = false;
        });
    },
    // 容器日志新增/修改采集
    setContainerCollection(params) {
      this.isHandle = true;
      this.$emit('update:container-loading', true);
      const urlParams = {};
      let requestUrl;
      if (this.isUpdate) {
        urlParams.collector_config_id = this.updateCollectorConfigID;
        requestUrl = 'container/update';
      } else {
        requestUrl = 'container/create';
      }
      const data = Object.assign(params, this.isYaml ? this.yamlFormData : {}, { yaml_config_enabled: this.isYaml });
      const updateData = { params: urlParams, data };
      this.$http.request(requestUrl, updateData).then((res) => {
        if (res.code === 0) {
          this.$store.commit(`collect/${this.isUpdate ? 'updateCurCollect' : 'setCurCollect'}`,
            Object.assign({}, this.formData, params, res.data));
          this.$emit('update:is-update', true); // 新建成功,更新是否是编辑状态
          this.$emit('stepChange');
          this.setDetail(res.data.collector_config_id);
        }
      })
        .catch((error) => {
          console.warn(error);
          // this.isShowSubmitErrorDialog = true;
          // this.submitErrorMessage = error.message;
        })
        .finally(() => {
          this.isHandle = false;
          this.$emit('update:containerLoading', false);
        });
    },
    // 处理提交参数
    handleParams() {
      const formData = deepClone(this.formData);
      const {
        collector_config_name,
        collector_config_name_en,
        category_id,
        collector_scenario_id,
        description,
        target_object_type,
        target_node_type,
        target_nodes,
        data_encoding,
        data_link_id,
        params,
        environment,
        bcs_cluster_id,
        add_pod_label,
        extra_labels,
        configs,
        yaml_config,
      } = formData;
      const containerFromData = {}; // 容器环境From数据
      const physicsFromData = {}; // 物理环境From数据
      const publicFromData = {  // 通用From数据
        collector_config_name,
        collector_config_name_en,
        collector_scenario_id,
        description,
        environment,
        data_link_id,
        category_id,
      };
      // 容器环境
      if (!this.isPhysicsEnvironment) {
        Object.assign(containerFromData, publicFromData, {
          bcs_cluster_id,
          add_pod_label,
          extra_labels,
          configs,
          yaml_config,
          yaml_config_enabled: this.isYaml,
        });
        containerFromData.configs.forEach((item, index) => {
          JSON.stringify(item.namespaces) === '["*"]' && (item.namespaces = []);
          const { namespace, label, load, containerName } = this.getScopeSelectShow(index);
          item.collector_type = this.currentEnvironment;
          if (namespace || this.isNode) item.namespaces = [];
          if (load || this.isNode) {
            item.container.workload_type = '';
            item.container.workload_name = '';
          }
          if (containerName || this.isNode) item.container.container_name = '';

          item.label_selector = label ? this.baseLabelSelector : this.getLabelSelectorQueryParams(item.labelSelector);
          item.container.container_name = item.containerNameList.join(',');

          delete item.noQuestParams;
          delete item.labelSelector;
          delete item.containerNameList;
          // 若为标准输出 则直接清空日志路径
          if (item.collector_type === 'std_log_config') item.params.paths = [];
          item.params = this.filterParams(item.params, item.collector_type);
        });
        containerFromData.extra_labels = extra_labels.filter(item => !(item.key === '' && item.value === ''));
        return Object.assign(containerFromData, { // 容器环境更新
          bk_biz_id: this.bkBizId,
        });
      }
      const physicsParams = this.filterParams(params);
      // 物理环境
      Object.assign(physicsFromData, publicFromData, {
        target_node_type,
        target_object_type,
        target_nodes,
        data_encoding,
        params: physicsParams,
      });
      if (this.isUpdate) { // 物理环境编辑
        physicsFromData.collector_config_id = this.updateCollectorConfigID;
        delete physicsFromData.category_id;
        delete physicsFromData.collector_scenario_id;
        return Object.assign(physicsFromData, {
          bk_biz_id: this.bkBizId,
        });
      } // 物理环境新增
      return Object.assign(physicsFromData, {
        bk_biz_id: this.bkBizId,
      });
    },
    /**
     * @desc: 对表单的params传参参数进行处理
     * @param { Object } passParams
     * @param { String } collectorType 配置项中的容器类型
     */
    filterParams(passParams) {
      let params = deepClone(passParams);
      if (!this.isWinEventLog) {
        if (!this.hasMultilineReg) { // 行首正则未开启
          delete params.multiline_pattern;
          delete params.multiline_max_lines;
          delete params.multiline_timeout;
        }
        const { match_type, match_content, separator, separator_filters, type } = params.conditions;
        let finallyType = !type ? 'match' : type ; // 如果是分隔符过滤，都没有填写或只填写一半的值，若过滤数组为空变成match不传过滤内容
        const separatorEffectiveArr = separator_filters.filter(item => item.fieldindex && item.word);
        !separatorEffectiveArr.length && (finallyType = 'match');
        params.conditions = finallyType === 'match'
          ? {
            type: finallyType,
            match_type,
            match_content,
          }
          : {
            type: finallyType,
            separator,
            separator_filters: separatorEffectiveArr,
          };
        if (!separatorEffectiveArr.length && type === 'separator') {  // 当前是分隔符过滤但内容都没有填写则传默认的字符串类型
          Object.assign(params.conditions, {
            type: 'match',
            match_type: 'include',
            match_content: '',
          });
        }
        params.paths = params.paths.map(item => (typeof item === 'object' ? item.value : item));
      } else {
        params = this.$refs.formConfigRef.getWinParamsData;
      }
      return params;
    },
    // 选择日志类型
    chooseLogType(item) {
      if (item.is_active) this.formData.collector_scenario_id = item.id;
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
          spaceUid: this.$store.state.spaceUid,
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
    // 采集目标选择内容变更
    handleTargetChange(value) {
      const {
        host_list: hostList,
        node_list: nodeList,
        service_template_list: serviceTemplateList,
        set_template_list: setTemplateList,
      } = value;
      let type = '';
      let nodes = [];
      if (nodeList?.length) {
        type = 'TOPO';
        nodes = nodeList;
      }
      if (hostList?.length) {
        type = 'INSTANCE';
        nodes = hostList;
      }
      if (serviceTemplateList?.length) {
        type = 'SERVICE_TEMPLATE';
        nodes = serviceTemplateList;
      }
      if (setTemplateList?.length) {
        type = 'SET_TEMPLATE';
        nodes = setTemplateList;
      }
      if (!type) return;

      this.formData.target_node_type = type;
      this.formData.target_nodes = toTransformNode(nodes, type);
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
    async checkEnNameRepeat(val) {
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
        if (res.data) return res.data.allowed;
      } catch (error) {
        return false;
      }
    },
    /**
     * @desc: 环境选择
     * @param { String } name 环境名称
     * @param { Boolean } isDisable 是否禁用
     */
    handleSelectEnvironment(name, isDisable) {
      if (this.isUpdate && isDisable) return;
      this.currentEnvironment = name;
    },
    handleAddExtraLabel() {
      this.formData.extra_labels.push({ key: '', value: '' });
    },
    handleDeleteExtraLabel(index) {
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
            Object.assign(this.formData.configs[setIndex], val);
            break;
        }
      }, setTime);
    },
    /**
     * @desc: 配置项点击所有容器
     * @param { Number } index 下标
     * @param { Boolean } state 状态
     */
    getWorkLoadTypeList() {
      this.$http.request('container/getWorkLoadType').then((res) => {
        if (res.code === 0) this.typeList = res.data.map(item => ({ id: item, name: item }));
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    /**
     * @desc: 指定操作弹窗
     * @param { Number } index 下标
     * @param { String } dialogType 标签或预览
     */
    handelShowDialog(index, dialogType = 'label') {
      if (!this.formData.bcs_cluster_id) return;
      this.currentSetIndex = index;
      const type = this.isNode ? 'node' : 'pod';
      const config = this.formData.configs[index];
      if (dialogType === 'label') {
        this.currentSelector = {
          bk_biz_id: this.bkBizId,
          bcs_cluster_id: this.formData.bcs_cluster_id,
          type,
          namespaceStr: config.noQuestParams.namespaceStr,
          labelSelector: config.labelSelector,
        };
      } else if (dialogType === 'view') {
        const namespaces = (config.namespaces.length === 1 && config.namespaces[0] === '*') ? [] : config.namespaces;
        this.viewQueryParams = {
          bk_biz_id: this.bkBizId,
          bcs_cluster_id: this.formData.bcs_cluster_id,
          type,
          namespaces,
          label_selector: this.getLabelSelectorQueryParams(config.labelSelector, true),
          container: config.container,
        };
      }
      dialogType === 'label' ?  this.isShowLabelTargetDialog = true : this.isShowViewDialog = true;
    },
    handleAddNewContainerConfig() { // 添加配置项
      const newContainerConfig = deepClone(this.configBaseObj);
      this.publicLetterIndex += 1;
      newContainerConfig.noQuestParams.letterIndex = this.publicLetterIndex;
      this.formData.configs.push(newContainerConfig);
    },
    handleDeleteConfig(index, letterIndex) { // 删除配置项
      this.$bkInfo({
        subTitle: this.$t('确定要删除配置项{n}？', { n: this.getFromCharCode(letterIndex) }),
        type: 'warning',
        confirmFn: () => {
          this.formData.configs.splice(index, 1);
        },
      });
    },
    handleNameSpaceSelect(option, index) {
      const config = this.formData.configs[index];
      if (option[option.length - 1] === '*') { // 如果最后一步选择所有，则清空数组填所有
        const nameSpacesLength = config.namespaces.length;
        config.namespaces.splice(0, nameSpacesLength, '*');
        config.noQuestParams.namespaceStr = this.getNameSpaceStr(config.namespaces);
        return;
      }
      if (option.length > 1 && option.includes('*')) { // 如果选中其他的值 包含所有则去掉所有选项
        const allIndex = option.findIndex(item => item === '*');
        config.namespaces.splice(allIndex, 1);
      }
      config.noQuestParams.namespaceStr = this.getNameSpaceStr(config.namespaces);
    },
    // 当前所选集群是否共享集群
    getIsSharedCluster() {
      return this.clusterList?.find(cluster => cluster.id === this.formData.bcs_cluster_id)?.is_shared ?? false;
    },
    getNameSpaceList(clusterID, isFirstUpdateSelect = false) {
      if (!clusterID || (this.isPhysicsEnvironment && this.isUpdate)) return;
      const query = { bcs_cluster_id: clusterID, bk_biz_id: this.bkBizId };
      this.nameSpaceRequest = true;
      this.$http.request('container/getNameSpace', { query }).then((res) => {
        // 判断是否是第一次切换集群 如果是 则进行详情页namespace数据回显
        if (isFirstUpdateSelect) {
          const namespaceList = [];
          this.formData.configs.forEach((configItem) => {
            namespaceList.push(...configItem.namespaces);
          });
          const resIDList = res.data.map(item => item.id);
          const setList = new Set([...namespaceList, ...resIDList]);
          setList.delete('*');
          const allList = [...setList].map(item => ({ id: item, name: item }));
          this.nameSpacesSelectList = [...allList];
          if (!this.getIsSharedCluster()) {
            this.nameSpacesSelectList.unshift({ name: this.$t('所有'), id: '*' });
          }
          return;
        }
        this.nameSpacesSelectList = [...res.data];
        if (!this.getIsSharedCluster()) {
          this.nameSpacesSelectList.unshift({ name: this.$t('所有'), id: '*' });
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.nameSpaceRequest = false;
        });
    },
    /**
     * @desc: 获取bcs集群列表
     */
    getBcsClusterList() {
      if (this.isRequestCluster) return;
      this.isRequestCluster = true;
      const query = { bk_biz_id: this.bkBizId };
      this.$http.request('container/getBcsList', { query }).then((res) => {
        if (res.code === 0) {
          this.clusterList = res.data;
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isRequestCluster = false;
        });
    },
    /**
     * @desc: 切换ui模式或yaml模式
     * @param { Boolean } val
     */
    handelChangeYaml(val) {
      return new Promise((resolve, reject) => {
        if (val) {
          const { add_pod_label, extra_labels, configs } = this.handleParams();
          const data = { add_pod_label, extra_labels, configs };
          // 传入处理后的参数 请求ui配置转yaml的数据
          this.$http.request('container/containerConfigsToYaml', { data }).then((res) => {
            this.formData.yaml_config = res.data;
            // 保存进入yaml模式之前的ui配置参数
            Object.assign(this.uiconfigToYamlData, {
              add_pod_label: this.formData.add_pod_label,
              extra_labels: this.formData.extra_labels,
              configs: this.formData.configs,
            });
            resolve(true);
          })
            .catch((err) => {
              console.warn(err);
              reject(false);
            });
        } else {
          try {
            // 若有报错 则回填进入yaml模式之前的ui配置参数
            if (!this.$refs.yamlEditorRef.getSubmitState) {
              Object.assign(this.formData, this.uiconfigToYamlData);
            } else {
            // 无报错 回填yamlData的参数
              const assignData = this.initContainerFormData(this.yamlFormData, true);
              Object.assign(this.formData, assignData);
            }
            resolve(true);
          } catch (error) {
            resolve(false);
          }
        }
      });
    },
    /**
     * @desc: 编进进入时判断当前环境 禁用另一边环境选择
     */
    initBtnListDisable() {
      const operateIndex = ['linux', 'windows'].includes(this.currentEnvironment) ? 1 : 0;
      this.environmentList[operateIndex].btnList.forEach(item => item.isDisable = true);
    },
    getFromCharCode(index) {
      return String.fromCharCode(index + 65);
    },
    handelClusterChange() { // 切换集群清空 namespaces
      this.formData.configs = this.formData.configs.map((conf) => {
        return {
          ...conf,
          namespaces: [],
        };
      });
    },
    checkEnNameValidator(val) {
      this.isTextValid = new RegExp(/^[A-Za-z0-9_]+$/).test(val);
      return this.isTextValid;
    },
    objCompare(objectA = {}, objectB = {}) {
      return JSON.stringify(objectA) === JSON.stringify(objectB);
    },
    handleEnConvert() {
      const str = this.formData.collector_config_name_en;
      const convertStr = str.split('').reduce((pre, cur) => {
        if (cur === '-') cur = '_'; // 中划线转化成下划线
        if (!/\w/.test(cur)) cur = ''; // 不符合的值去掉
        return pre += cur;
      }, '');
      this.formData.collector_config_name_en = convertStr;
      this.$refs.validateForm.validate().then(() => {
        this.isTextValid = true;
      })
        .catch(() => {
          if (convertStr.length < 5) this.isTextValid = true;
        });
    },
    getSelectorNodes() {
      const { target_node_type: type, target_nodes: nodes } = this.formData;
      const targetList = toSelectorNode(nodes, type);
      return {
        host_list: type === 'INSTANCE' ? targetList : [],
        node_list: type === 'TOPO' ? targetList : [],
        service_template_list: type === 'SERVICE_TEMPLATE' ? targetList : [],
        set_template_list: type === 'SET_TEMPLATE' ? targetList : [],
      };
    },
    deleteLabItem(conIndex, matchID) {
      const labelSelector = this.formData.configs[conIndex].labelSelector;
      const labelIndex = labelSelector.findIndex(item => item.id === matchID);
      labelSelector.splice(labelIndex, 1);
    },
    handleLabelEdit(conIndex, matchID, newValue) {
      const labelSelector = this.formData.configs[conIndex].labelSelector;

      const isRepeat = labelSelector.some((item) => {
        return newValue.key === item.key
        && newValue.value === item.value
        && newValue.operator === item.operator;
      });

      const type = newValue.operator === '=' ? 'match_labels' : 'match_expressions';

      return new Promise((resolve) => {
        if (!isRepeat) {
          const labelIndex = labelSelector.findIndex(item => item.id === matchID);
          const newMatchObject = { ...labelSelector[labelIndex], ...newValue, type };
          labelSelector.splice(labelIndex, 1, newMatchObject);
        }
        resolve(true);
      });
    },
    // 手动添加表达式
    handleSubmitExpressions(conIndex, val) {
      const configs = this.formData.configs[conIndex];
      const isRepeat = configs.labelSelector.some((item) => {
        return val.key === item.key
        && val.value === item.value
        && val.operator === item.operator;
      });
      return new Promise((resolve) => {
        if (!isRepeat) {
          configs.labelSelector.unshift({
            ...val,
            id: random(10),
            type: 'match_expressions',
          });
        }
        configs.noQuestParams.handleEditLabel = false;
        resolve(true);
      });
    },
    handleEnterLabel(conIndex, isShow = true) {
      this.formData.configs[conIndex].noQuestParams.handleEditLabel = isShow;
    },
    getScopeName(conItem) {
      return this.scopeNameList[conItem];
    },
    // 是否显示对应模块的列表的按钮
    isShowScopeButton(conIndex, scope) {
      // 当前环境为node时， 除了label列表全部不显示
      if (this.isNode && scope !== 'label') return false;
      return this.getScopeSelectShow(conIndex)[scope];
    },
    // 点击添加范围的列表 显示对应模块
    handleAddNewScope(conIndex, scope) {
      this.getScopeSelectShow(conIndex)[scope] = false;
    },
    // 是否展示添加范围的按钮
    isShowAddScopeButton(conIndex) {
      const scopeSelectShow = this.getScopeSelectShow(conIndex);
      // 当前为node环境时 只判断label模块是否展示
      if (this.isNode) return scopeSelectShow.label;
      return Object.values(this.getScopeSelectShow(conIndex)).some(Boolean);
    },
    // 是否展示对应操作范围模块
    isShowScopeItem(conIndex, scope) {
      if (this.isNode) { // 当前环境为node时 若是标签模块则判断是否展示 其余均不显示
        if (scope === 'label') return !this.getScopeSelectShow(conIndex).label;
        if (scope !== 'label') return false;
      }
      return !this.getScopeSelectShow(conIndex)[scope];
    },
    // 点击删除icon 隐藏对应范围模块 初始化对应的值
    handleDeleteConfigParamsItem(conIndex, scope) {
      const config = this.formData.configs[conIndex];
      switch (scope) {
        case 'namespace':
          config.namespaces = [];
          break;
        case 'load':
          config.container.workload_type = '';
          config.container.workload_name = '';
          break;
        case 'label':
          config.labelSelector = [];
          break;
        case 'containerName':
          config.containerNameList = [];
          config.container.container_name = '';
          break;
        default:
          break;
      }
      this.getScopeSelectShow(conIndex)[scope] = true;
    },
    handleContainerNameBlur(input, list, conIndex) {
      if (!input) return;
      const config = this.formData.configs[conIndex];
      config.containerNameList = !list.length ? [input] : [...new Set([...config.containerNameList, input])];
      config.container.container_name = config.containerNameList.join(',');
    },
    handleContainerNameChange(conIndex) {
      const config = this.formData.configs[conIndex];
      config.container.container_name = config.containerNameList.join(',');
    },
    // 获取config里添加范围的列表
    getScopeSelectShow(conIndex) {
      return this.formData.configs[conIndex].noQuestParams.scopeSelectShow;
    },
    getNameSpaceStr(namespaces) {
      return (namespaces.length === 1 && namespaces[0] === '*') ? '' : namespaces.join(',');
    },
    /**
     * @desc: 展示用的标签格式转化成存储或传参的标签格式
     * @param {Object} labelSelector 主页展示用的label_selector
     * @param {Boolean} isViewType 是否是预览传参 in notin 操作符需要加括号
     * @returns {Object} 返回传参用的label_selector
     */
    getLabelSelectorQueryParams(labelSelector, isViewType = false) {
      return labelSelector.reduce((pre, cur) => {
        const value = (isViewType && ['NotIn', 'In'].includes(cur.operator)) ? `(${cur.value})` : cur.value;
        pre[cur.type].push({
          key: cur.key,
          operator: cur.operator,
          value,
        });
        return pre;
      }, {
        match_labels: [],
        match_expressions: [],
      });
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

  .en-bk-form {
    width: 710px;

    .en-name-box {
      align-items: center;

      @include flex-justify(space-between);
    }

    .text-error {
      display: inline-block;
      position: absolute;
      top: 6px;
      left: 12px;
      font-size: 12px;
      color: transparent;
      pointer-events: none;

      /* stylelint-disable-next-line declaration-no-important */
      text-decoration: red wavy underline !important;
    }
  }

  .bk-form-content {
    line-height: 20px;
  }

  .king-alert {
    margin: 24px 0 -18px;

    .link {
      color: #3a84ff;
      cursor: pointer;
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

  .original-title {
    @include flex-justify(start);

    > div {
      font-weight: 500;
      margin-left: 40px;
    }
  }

  .tips,
  .en-name-tips {
    padding: 4px 0;
    font-size: 12px;
    color: #aeb0b7;
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

  .w520 {
    &.bk-form-control {
      width: 520px;
    }

    &.bk-select {
      width: 520px;
    }
  }

  .multiline-log-container {
    margin-top: 4px;

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
      color: #c4c6cb;
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
    margin-bottom: -30px;

    .bk-form-checkbox {
      height: 30px;
      width: 320px;
      display: flex;
      align-items: center;
    }

    .bk-tag-selector {
      width: 320px;
      transform: translate3d(66px, -30px, 0);
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


  .win-content {
    padding-bottom: 20px;
    position: relative;
    left: 115px;
    width: 76%;

    > span {
      color: #90929a;
      font-size: 14px;
      position: absolute;
      left: -80px;
      top: 6px;
    }

    &.en-span span {
      left: -112px;
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

  .icon-close-circle {
    display: inline-block;
    font-size: 14px;
    transform: rotateZ(45deg);
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
        font-weight: 400;
        font-size: 14px;
        margin: 6px 0;
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

          img {
            padding: 0 8px 0 4px;
          }

          &.disable {
            background: #fafbfd;
            cursor: no-drop;
          }

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

      .icon-delete {
        font-size: 16px;
        color: #ea3636;
        cursor: pointer;
      }
    }

    .config-container {
      padding: 16px 24px;
      color: #63656e;
      background: #fafbfd;

      .config-cluster-box {
        padding: 8px 12px 16px;
        background: #fff;
        border: 1px solid #eaebf0;
        border-radius: 2px;
        font-size: 12px;

        .config-cluster-title {
          padding: 8px 12px;

          .title {
            font-weight: 700;
            margin-right: 14px;
          }

          .bk-icon {
            font-size: 14px;
          }

          .disable {
            /* stylelint-disable-next-line declaration-no-important */
            color: #63656e !important;

            /* stylelint-disable-next-line declaration-no-important */
            cursor: no-drop !important;
          }

          .preview {
            color: #3a84ff;
            cursor: pointer;
          }
        }
      }

      .config-item-title {
        padding-bottom: 8px;

        :last-child {
          margin-left: 8px;
          cursor: pointer;
        }

        .icon-delete {
          font-size: 14px;
          color: #ea3636;
          cursor: pointer;
          display: none;
        }
      }

      .config-item {
        padding: 8px 12px;
        margin-bottom: 12px;
        border-radius: 2px;
        font-size: 12px;

        .select-label {
          margin-top: 4px;
          color: #3a84ff;

          .manually {
            margin-right: 15px;
            cursor: pointer;
          }

          .select {
            margin-left: 15px;
            position: relative;
            cursor: pointer;

            &::before {
              content: ' ';
              position: absolute;
              left: -14px;
              top: 4px;
              display: inline-block;
              width: 1px;
              height: 14px;
              background: #eaebf0;
            }
          }
        }

        &.hover-light:hover {
          background: #f5f7fa;
        }

        &:hover .icon-delete {
          display: inline-block;
        }
      }

      .container-input {
        .input {
          max-width: none;
        }
      }

      .container-btn-container {
        align-items: center;
        position: relative;

        .span-box {
          margin-right: 24px;

          &:not(:first-child) {
            margin-right: 0;
            position: relative;

            &::before {
              content: ' ';
              width: 1px;
              height: 16px;
              background-color: #dcdee5;
              position: absolute;
              left: -11px;
              top: 3px;
            }
          }
        }

        .container-btn {
          color: #3a84ff;
          cursor: pointer;

          &.disable {
            color: #c4c6cc;
            cursor: not-allowed;
          }

          &.cluster-not-select {
            cursor: not-allowed;
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

      .specify-domain {
        margin-top: 8px;
        max-height: 210px;
        overflow-y: auto;

        > div {
          padding: 4px 0;
        }
      }

      .bk-select {
        background: #fff;
      }

      .bk-label {
        color: #63656e;
      }
    }
  }

  .conflict-container {
    width: 730px;
    height: 32px;
    margin: 12px 0 14px 115px;
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
    width: 730px;
    height: 42px;
    font-size: 12px;
    margin: 0 0 14px 115px;
    justify-content: center;
    background: #fafbfd;
    border: 1px dashed #dcdee5;
    cursor: pointer;

    @include flex-align();

    > div {
      color: #63656e;

      @include flex-center;
    }

    .icon-plus {
      color: #989ca7;
      font-size: 22px;
    }
  }

  .extra-error {
    .bk-form-input {
      border-color: #ff5656;
    }
  }

  .add-log-label {
    display: flex;
    align-items: center;

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
