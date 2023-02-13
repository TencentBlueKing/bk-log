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
  <div class="retrieve-container" v-bkloading="{ isLoading: false }">
    <!-- 检索页首页 -->
    <div v-if="hasAuth && isRetrieveHome" class="retrieve-home-container">
      <div class="retrieve-home" data-test-id="retrieve_div_frontPageSearchBox">
        <div class="retrieve-home-title">{{ $t('检索') }}</div>
        <div class="retrieve-home-condition">
          <!-- 选择索引集 -->
          <select-indexSet
            class="king-select-index-set"
            :index-id="indexId"
            :index-set-list="indexSetList"
            :basic-loading.sync="basicLoading"
            @selected="handleSelectIndex"
            @updateIndexSetList="updateIndexSetList" />
          <!-- 选择日期 -->
          <select-date
            :time-range.sync="retrieveParams.time_range"
            :date-picker-value="datePickerValue"
            @update:datePickerValue="handleDateChange"
            @datePickerChange="retrieveWhenDateChange" />
        </div>
        <!-- 首页搜索框 -->
        <retrieve-input
          v-model="retrieveParams.keyword"
          :show-history.sync="showHistory"
          :history-list="historyList"
          :is-search-allowed="isSearchAllowed"
          @focus="showHistory = true"
          @retrieve="retrieveLog" />
      </div>
      <!-- eslint-disable vue/no-v-html -->
      <div v-if="footerHtml" v-html="footerHtml"></div>
      <!--eslint-enable-->
    </div>
    <!-- 检索页详情页 -->
    <div v-if="!isRetrieveHome" class="retrieve-detail-container">
      <result-header
        ref="resultHeader"
        :is-as-iframe="isAsIframe"
        :show-retrieve-condition="showRetrieveCondition"
        :show-expand-init-tips="showExpandInitTips"
        :retrieve-params="retrieveParams"
        :time-range.sync="retrieveParams.time_range"
        :date-picker-value="datePickerValue"
        :index-set-item="indexSetItem"
        :is-show-collect="isShowCollect"
        @shouldRetrieve="retrieveLog"
        @initTipsHidden="handleInitTipsHidden"
        @open="openRetrieveCondition"
        @update:datePickerValue="handleDateChange"
        @datePickerChange="retrieveWhenDateChange"
        @settingMenuClick="handleSettingMenuClick"
        @closeRetrieveCondition="closeRetrieveCondition"
        @updateCollectCondition="updateCollectCondition" />
      <div class="page-loading-wrap" v-if="basicLoading || tableLoading">
        <div class="page-loading-bar"></div>
      </div>
      <div class="result-content">
        <!-- 收藏列表 -->
        <collect-index
          :width.sync="collectWidth"
          :is-show.sync="isShowCollect"
          :favorite-loading="favoriteLoading"
          :favorite-list="favoriteList"
          :style="{ width: collectWidth + 'px' }"
          :favorite-request-i-d="favoriteRequestID"
          :active-favorite="activeFavorite"
          :active-favorite-i-d="activeFavoriteID"
          :visible-fields="visibleFields"
          @handleClick="handleClickFavoriteItem"
          @isRefreshFavorite="updateActiveFavoriteData"
          @favoriteDialogSubmit="handleSubmitFavorite"
          @requestFavoriteList="getFavoriteList" />
        <!-- 检索详情页左侧 -->
        <div v-show="showRetrieveCondition" class="retrieve-condition" :style="{ width: leftPanelWidth + 'px' }">
          <!-- 监控显示的 tab 切换 -->
          <!-- <div v-if="isAsIframe" class="bk-button-group">
          <bk-button @click="handleCheckMonitor">{{ $t('指标检索') }}</bk-button>
          <bk-button class="is-selected">{{ $t('日志检索') }}</bk-button>
          <bk-button @click="handleCheckEvent">{{ $t('事件检索') }}</bk-button>
        </div> -->

          <!-- <div class="biz-menu-box" id="bizSelectorGuide" v-if="!isAsIframe">
          <biz-menu-select theme="light"></biz-menu-select>
        </div> -->

          <div class="king-tab" :class="isAsIframe && 'as-iframe'">
            <div class="tab-header">
              <span class="tab-title">
                {{ isFavoriteNewSearch ? $t('新检索') : getFavoriteName }}
                <span
                  v-show="!isFavoriteNewSearch"
                  class="bk-icon icon-edit-line"
                  @click="handleEditFavorite">
                </span>
              </span>
              <div class="tab-operation">
                <bk-popover
                  v-show="isShowUiType"
                  ref="formTipsRef"
                  :tippy-options="{
                    placement: 'top',
                    theme: 'light',
                    trigger: 'mouseenter',
                  }"
                  :disabled="isCanUseUiType || !isSqlSearchType">
                  <div
                    class="search-type"
                    @click="handleClickSearchType">
                    <span class="bk-icon icon-sort"></span>
                    <span>{{isSqlSearchType ? $t('表单') : 'Source'}}</span>
                  </div>
                  <div slot="content">
                    <span
                      style="color: #d7473f; display: inline-block; transform: translateY(-2px);"
                      class="bk-icon icon-exclamation-circle-shape">
                    </span>
                    <span>{{$t('表单Tips')}}</span>
                  </div>
                </bk-popover>
              </div>
            </div>
            <div class="tab-content" :style="`height:calc(100% - ${isAsIframe ? 60 : 108}px);`">
              <div class="tab-content-item" data-test-id="retrieve_div_dataQueryBox">
                <!-- 选择索引集 -->
                <div class="tab-item-title">{{ $t('索引集') }}</div>
                <select-indexSet
                  :index-id="indexId"
                  :index-set-list="indexSetList"
                  :basic-loading.sync="basicLoading"
                  @selected="handleSelectIndex"
                  @updateIndexSetList="updateIndexSetList" />
                <template v-if="isSqlSearchType">
                  <!-- 查询语句 -->
                  <query-statement
                    v-model="retrieveParams.keyword"
                    :history-records="statementSearchrecords"
                    @updateSearchParam="updateSearchParam"
                    @retrieve="retrieveLog" />
                  <retrieve-detail-input
                    v-model="retrieveParams.keyword"
                    :is-auto-query="isAutoQuery"
                    :retrieved-keyword="retrievedKeyword"
                    :dropdown-data="retrieveDropdownData"
                    :is-show-ui-type="isShowUiType"
                    @inputBlur="handleBlurSearchInput"
                    @retrieve="retrieveLog" />
                </template>
                <template v-else>
                  <ui-query
                    :is-favorite-search="isFavoriteSearch"
                    :keyword="retrieveParams.keyword"
                    :active-favorite="activeFavorite"
                    :is-clear-condition="isClearCondition"
                    @updateKeyWords="updateKeyWords" />
                </template>
                <!-- 添加过滤条件 -->
                <div class="tab-item-title flex-item-title">
                  <span>{{ $t('过滤条件') }}</span>
                  <div class="filter-item">
                    <span
                      @click="openIpQuick"
                      data-test-id="dataQuery_span_addIP"
                    >{{ $t('添加IP') }}</span>
                    <filter-condition-item
                      :filter-condition="retrieveParams.addition"
                      :total-fields="totalFields"
                      :field-alias-map="fieldAliasMap"
                      :filter-all-operators="filterAllOperators"
                      :statistical-fields-data="statisticalFieldsData"
                      @addFilterCondition="addFilterCondition"
                      @removeFilterCondition="removeFilterCondition" />
                  </div>
                </div>
                <div class="add-filter-condition-container">
                  <ip-quick
                    :target-node="retrieveParams.host_scopes.target_nodes"
                    :target-node-type="retrieveParams.host_scopes.target_node_type"
                    @openIpQuick="openIpQuick"
                    @confirm="handleSaveIpQuick" />
                  <div class="cut-line" v-if="showFilterCutline"></div>
                  <template v-for="(item, index) in retrieveParams.addition">
                    <filter-condition-item
                      :key="item.field + index + item.value"
                      :edit-index="index"
                      :is-add="false"
                      :edit-data="item"
                      :filter-all-operators="filterAllOperators"
                      :filter-condition="retrieveParams.addition"
                      :total-fields="totalFields"
                      :field-alias-map="fieldAliasMap"
                      :statistical-fields-data="statisticalFieldsData"
                      @addFilterCondition="addFilterCondition"
                      @removeFilterCondition="() => removeFilterCondition(index)" />
                  </template>
                </div>
                <!-- 查询收藏清空按钮 -->
                <div class="retrieve-button-group">
                  <div v-if="tableLoading" class="loading-box">
                    <div class="loading" v-bkloading="{ isLoading: true, theme: 'primary', mode: 'spin' }"></div>
                  </div>
                  <bk-button
                    v-else
                    v-bk-tooltips="{ content: getSearchType.changeBtnTips }"
                    class="query-btn"
                    :icon="getSearchType.icon"
                    @click="handleChangeSearchType">
                  </bk-button>
                  <bk-button
                    v-cursor="{ active: isSearchAllowed === false }"
                    theme="primary"
                    data-test-id="dataQuery_button_filterSearch"
                    :class="{ 'query-search': true,'loading': tableLoading }"
                    @click="retrieveLog">
                    <!-- {{ $t('查询') }} -->
                    {{ getSearchType.text }}
                  </bk-button>
                  <div class="favorite-btn-container">
                    <bk-button
                      v-show="isFavoriteNewSearch"
                      ext-cls="favorite-btn"
                      data-test-id="dataQuery_button_collection"
                      @click="handleClickFavorite">
                      <span class="favorite-btn-text">
                        <span class="icon bk-icon icon-star"></span>
                        <span>{{ $t('收藏') }}</span>
                      </span>
                    </bk-button>
                    <span
                      v-show="!isFavoriteNewSearch && isFavoriteUpdate"
                      class="catching-ball">
                    </span>
                    <bk-button
                      v-show="!isFavoriteNewSearch"
                      ext-cls="favorite-btn"
                      :disabled="!isFavoriteUpdate || favoriteUpdateLoading"
                      @click="handleUpdateFavorite">
                      <span v-bk-tooltips="{ content: $t('保存Tips'), disabled: !isFavoriteUpdate }">
                        <span class="favorite-btn-text">
                          <span :class="[
                            'icon',
                            !isFavoriteUpdate
                              ? 'log-icon icon-star-shape'
                              : 'bk-icon icon-save',
                          ]">
                          </span>
                          <span>{{ !isFavoriteUpdate ? $t('已收藏') : $t('保存') }}</span>
                        </span>
                      </span>
                    </bk-button>
                  </div>
                  <span v-bk-tooltips="{ content: $t('清空'), delay: 200 }">
                    <div class="clear-params-btn" @click="clearCondition">
                      <bk-button data-test-id="dataQuery_button_phrasesClear"></bk-button>
                      <span class="log-icon icon-brush"></span>
                    </div>
                  </span>
                </div>
              </div>
              <div class="tab-content-item" data-test-id="retrieve_div_fieldFilterBox">
                <!-- 字段过滤 -->
                <div class="tab-item-title field-filter-title" style="color: #313238;">{{ $t('字段过滤') }}</div>
                <field-filter
                  :retrieve-params="retrieveParams"
                  :total-fields="totalFields"
                  :visible-fields="visibleFields"
                  :sort-list="sortList"
                  :field-alias-map="fieldAliasMap"
                  :show-field-alias="showFieldAlias"
                  :statistical-fields-data="statisticalFieldsData"
                  :parent-loading="tableLoading"
                  @fieldsUpdated="handleFieldsUpdated" />
              </div>
            </div>
          </div>
        </div>
        <!-- 检索详情页右侧检索结果 -->
        <div class="retrieve-result" :style="{ width: 'calc(100% - ' + sumLeftWidth + 'px)' }">
          <!-- 无权限页面 -->
          <auth-container-page v-if="showAuthInfo" :info="showAuthInfo" />
          <template v-else>
            <!-- 初始化加载时显示这个空的盒子 避免先显示内容 再显示无权限页面 -->
            <div v-if="!hasAuth && !showAuthInfo && !isNoIndexSet" style="height: 100%;background: #f4f7fa;"></div>
            <!-- 无索引集 申请索引集页面 -->
            <no-index-set v-if="isNoIndexSet" />
            <!-- 详情右侧 -->
            <result-main
              ref="resultMainRef"
              v-else
              :sort-list="sortList"
              :table-loading="tableLoading"
              :retrieve-params="retrieveParams"
              :took-time="tookTime"
              :index-set-list="indexSetList"
              :table-data="tableData"
              :visible-fields="visibleFields"
              :total-fields="totalFields"
              :field-alias-map="fieldAliasMap"
              :show-field-alias="showFieldAlias"
              :bk-monitor-url="bkmonitorUrl"
              :async-export-usable="asyncExportUsable"
              :async-export-usable-reason="asyncExportUsableReason"
              :statistical-fields-data="statisticalFieldsData"
              :time-field="timeField"
              :config-data="clusteringData"
              :apm-relation="apmRelationData"
              :clean-config="cleanConfig"
              :picker-time-range="pickerTimeRange"
              :date-picker-value="datePickerValue"
              :index-set-item="indexSetItem"
              :operator-config="operatorConfig"
              :retrieve-search-number="retrieveSearchNumber"
              :retrieve-config-id="retrieveConfigId"
              @request-table-data="requestTableData"
              @fieldsUpdated="handleFieldsUpdated"
              @shouldRetrieve="retrieveLog"
              @addFilterCondition="addFilterCondition"
              @showSettingLog="handleSettingMenuClick('clustering')" />
          </template>
        </div>
      </div>
      <!-- 可拖拽页面布局宽度 -->
      <div
        v-show="showRetrieveCondition"
        :class="['drag-bar', isChangingWidth && 'dragging']"
        :style="{ left: sumLeftWidth - 1 + 'px' }">
        <img
          src="../../images/icons/drag-icon.svg"
          alt=""
          draggable="false"
          class="drag-icon"
          @mousedown.left="dragBegin">
      </div>
    </div>

    <!-- 目标选择器 -->
    <ip-selector-dialog
      :show-dialog.sync="showIpSelectorDialog"
      :show-dynamic-group="true"
      :target-nodes="retrieveParams.host_scopes.target_nodes"
      :target-node-type="retrieveParams.host_scopes.target_node_type"
      @target-change="handleSaveIpQuick" />

    <setting-modal
      :index-set-item="indexSetItem"
      :is-show-dialog="isShowSettingModal"
      :select-choice="clickSettingChoice"
      :total-fields="totalFields"
      :clean-config="cleanConfig"
      :config-data="clusteringData"
      :statistical-fields-data="statisticalFieldsData"
      @closeSetting="isShowSettingModal = false;"
      @updateLogFields="requestFields" />

    <add-collect-dialog
      v-model="isShowAddNewCollectDialog"
      :favorite-list="favoriteList"
      :add-favorite-data="addFavoriteData"
      :favorite-i-d="activeFavoriteID"
      :replace-data="replaceFavoriteData"
      :visible-fields="visibleFields"
      :is-click-favorite-edit="true"
      @submit="handleSubmitFavorite" />
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import SelectIndexSet from './condition-comp/select-indexSet';
import SelectDate from './condition-comp/select-date';
import RetrieveInput from './condition-comp/retrieve-input';
import RetrieveDetailInput from './condition-comp/retrieve-detail-input';
import QueryStatement from './condition-comp/query-statement';
import FilterConditionItem from './condition-comp/filter-condition-item';
import IpQuick from './condition-comp/ip-quick';
import IpSelectorDialog from '@/components/collection-access/ip-selector-dialog';
import FieldFilter from './condition-comp/field-filter';
import ResultHeader from './result-comp/result-header';
import NoIndexSet from './result-comp/no-index-set';
import ResultMain from './result-comp/result-main';
import AuthContainerPage from '@/components/common/auth-container-page';
import SettingModal from './setting-modal/index.vue';
import CollectIndex from './collect/collect-index';
import AddCollectDialog from './collect/add-collect-dialog';
import UiQuery from './condition-comp/ui-query';
import { formatDate, readBlobRespToJson, parseBigNumberList, random } from '@/common/util';
import { handleTransformToTimestamp } from '../../components/time-range/utils';
import indexSetSearchMixin from '@/mixins/indexSet-search-mixin';
import axios from 'axios';
import * as authorityMap from '../../common/authority-map';

export default {
  name: 'Retrieve',
  components: {
    SelectIndexSet,
    SelectDate,
    RetrieveInput,
    RetrieveDetailInput,
    QueryStatement,
    FilterConditionItem,
    IpQuick,
    IpSelectorDialog,
    FieldFilter,
    ResultHeader,
    ResultMain,
    NoIndexSet,
    SettingModal,
    AuthContainerPage,
    CollectIndex,
    AddCollectDialog,
    UiQuery,
    UiQuery,
  },
  mixins: [indexSetSearchMixin],
  data() {
    const currentTime = Date.now();
    const startTime = formatDate(currentTime - 15 * 60 * 1000);
    const endTime = formatDate(currentTime);
    return {
      hasAuth: false,
      isSearchAllowed: null, // true 有权限，false 无权限，null 未知权限
      renderTable: true, // 显示字段更新后手动触发重新渲染表格
      basicLoading: false, // view loading
      tableLoading: false, // 表格 loading
      requesting: false,
      // isRetrieveHome: !this.$route.params.indexId?.toString() && !this.$route.params.from, // 检索首页
      isRetrieveHome: false,
      isNoIndexSet: false,
      showRetrieveCondition: true, // 详情页显示检索左侧条件
      showExpandInitTips: false, // 展开初始tips
      hasExpandInitTipsShown: false,
      activeTab: 'search', // 检索左侧条件 tab - 数据查询：search；收藏记录：record。
      footerHtml: '', // 页脚内容
      isChangingWidth: false, // 拖拽
      leftPanelWidth: 450, // 左栏默认宽度
      leftPanelMinWidth: 350, // 左栏最小宽度
      leftPanelMaxWidth: 750, // 左栏最大宽度
      indexId: '', // 当前选择的索引ID
      indexSetItem: {}, // 当前索引集元素
      indexSetList: [], // 索引集列表,
      datePickerValue: ['now-15m', 'now'], // 日期选择器
      retrievedKeyword: '*', // 记录上一次检索的关键字，避免输入框失焦时重复检索
      retrieveParams: { // 检索参数
        bk_biz_id: this.$store.state.bkBizId,
        keyword: '*', // 搜索关键字
        // 自定义时间范围，10m 表示最近 10 分钟，10h 表示最近 10 小时，10d 表示最近 10 天
        // 当 time_range === 'customized' 时，检索时间范围为 start_time ~ end_time
        time_range: 'customized',
        start_time: startTime, // 时间范围，格式 YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
        end_time: endTime, // 时间范围
        // ip 快选，modules 和 ips 只能修改其一，另一个传默认值
        host_scopes: {
          // 拓扑选择模块列表，单个模块格式 {bk_inst_id: 2000003580, bk_obj_id: 'module'}
          modules: [],
          // 手动输入 ip，多个 ip 用英文 , 分隔
          ips: '',
          // 目标节点
          target_nodes: [],
          // 目标节点类型
          target_node_type: '',
        },
        // 过滤条件，可添加多个，每个过滤条件格式 {field: 'time', operator: 'is', value: 'xxx'}
        // field 为过滤的字段
        // operator 从接口获取，默认为 'is'
        // value 为过滤字段对应的值，如果为多个用英文 , 分隔
        addition: [],
        // begin 和 size 类似分页，两者相加不能超过 10000
        begin: 0,
        size: 500,
        // 聚合周期
        interval: 'auto',
      },
      showHistory: false, // 历史记录
      historyList: [],
      isFavoriteSearch: false, // 是否是收藏检索
      isAfterRequestFavoriteList: false, // 是否在检索后更新收藏列表
      statisticalFieldsData: {}, // 字段可选值统计
      retrieveDropdownData: {}, // 检索下拉字段可选值统计
      statementSearchrecords: [], // 查询语句历史记录
      // ipTopoSwitch: true, // IP快选功能相关
      totalFields: [], // 表格字段
      visibleFields: [], // 显示的排序后的字段
      sortList: [], // 排序字段
      notTextTypeFields: [], // 字段类型不为 text 的字段
      fieldAliasMap: {},
      showFieldAlias: localStorage.getItem('showFieldAlias') === 'true',
      tookTime: 0, // 耗时
      totalCount: 0, // 结果条数
      tableData: {}, // 表格结果
      bkmonitorUrl: false, // 监控主机详情地址
      asyncExportUsable: true, // 是否支持异步导出
      asyncExportUsableReason: '', // 无法异步导出原因
      isInitPage: true,
      isAutoQuery: localStorage.getItem('closeAutoQuery') !== 'true',
      isHideAutoQueryTips: localStorage.getItem('hideAutoQueryTips') === 'true',
      isPollingStart: false,
      startTimeStamp: 0,
      endTimeStamp: 0,
      logList: [], // 当前搜索结果的日志
      isNextTime: false,
      timer: null,
      isShowSettingModal: false,
      clickSettingChoice: '',
      timeField: '',
      isThollteField: false,
      globalsData: {},
      random,
      cleanConfig: {},
      clusteringData: { // 日志聚类参数
        name: '',
        is_active: true,
        extra: {
          collector_config_id: null,
          signature_switch: false,
          clustering_field: '',
        },
      },
      apmRelationData: {},
      showIpSelectorDialog: false,
      isAsIframe: false,
      localIframeQuery: {},
      isFirstLoad: true,
      pickerTimeRange: ['now-15m', 'now'],
      operatorConfig: {}, // 当前table操作的值
      authPageInfo: null,
      isShowAddNewCollectDialog: false, // 是否展示新增收藏弹窗
      collectWidth: localStorage.getItem('isAutoShowCollect') === 'true' ? 240 : 0, // 收藏默认栏宽度
      isShowCollect: localStorage.getItem('isAutoShowCollect') === 'true',
      isSqlSearchType: true, // 是否是sql模式
      activeFavorite: {}, // 当前点击的收藏参数
      activeFavoriteID: -1, // 当前点击就的收藏ID
      favoriteUpdateLoading: false,
      favoriteList: [],
      favoriteLoading: false,
      isClearCondition: false, // 是否清空检索条件
      favSearchList: [], // 收藏的表单模式列表
      inputSearchList: [], // 鼠标失焦后的表单模式列表
      filterAllOperators: {},
      addFavoriteData: {}, // 新增收藏所需的参数
      favoriteRequestID: 0, // 参数改变更新收藏
      replaceFavoriteData: {}, // 收藏判断不同后的替换参数
      searchMap: { // 检索按钮
        search: { // 查询
          icon: 'bk-icon log-icon icon-bofang',
          text: this.$t('查询'),
          changeBtnTips: this.$t('切换自动查询'),
        },
        searchIng: { // 查询中
          icon: 'loading',
          text: `${this.$t('查询中')}...`,
        },
        autoSearch: { // 自动查询
          icon: 'bk-icon log-icon icon-zanting',
          text: this.$t('自动查询'),
          changeBtnTips: this.$t('切换手动查询'),
        },
      },
      retrieveSearchNumber: 0, // 切换采集项或初始进入页面时 检索次数初始化为0 检索一次次数+1;
      retrieveConfigId: null, // 当前索引集关联的采集项ID
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      spaceUid: state => state.spaceUid,
      currentMenu: state => state.currentMenu,
      storedIndexID: state => state.indexId, // 路由切换时缓存当前选择的索引
    }),
    ...mapGetters(['asIframe', 'iframeQuery']),
    ...mapGetters({
      authMainPageInfo: 'globals/authContainerInfo',
    }),
    // 是否显示IP快选功能模块
    // showIpQuick() {
    //   return this.ipTopoSwitch;
    // },
    showFilterCutline() {
      const { host_scopes: hostScopes, addition } = this.retrieveParams;
      // return (host_scopes.modules.length || host_scopes.ips.length) && addition.length;
      return (hostScopes?.modules?.length
      || hostScopes?.ips?.length
      // eslint-disable-next-line camelcase
      || hostScopes?.target_nodes?.length)
      && addition?.length;
    },
    showSearchPage() {
      return this.hasAuth || this.isNoIndexSet;
    },
    showAuthInfo() { // 无业务权限则展示store里的 然后判断是否有索引集权限
      return this.authMainPageInfo || this.authPageInfo;
    },
    sumLeftWidth() { // 收藏和检索左边的页面的合计宽度
      return this.collectWidth + this.leftPanelWidth;
    },
    getSearchType() { // 获取搜索按钮状态
      if (this.tableLoading) return this.searchMap.searchIng;
      return this.searchMap[this.isAutoQuery ? 'autoSearch' : 'search'];
    },
    isCanUseUiType() { // 判断当前的检索语句生成的键名和操作符是否相同 不相等的话不能切换表单模式
      return this.inputSearchList.some(v => this.favSearchList.includes(v));
    },
    isShowUiType() { // 判断当前点击的收藏是否展示表单字段
      // eslint-disable-next-line camelcase
      return Boolean(this.activeFavorite?.params?.search_fields?.length);
    },
    isFavoriteNewSearch() { // 是否是新检索
      return this.activeFavoriteID === -1;
    },
    getFavoriteName() { // 获取当前点击的收藏名
      return this.activeFavorite?.name || '--';
    },
    isFavoriteUpdate() { // 判断当前收藏是否有参数更新
      const { params: retrieveParams } = this.getRetrieveFavoriteData();
      const { params } = this.activeFavorite;
      const favoriteParams = {
        host_scopes: params?.host_scopes,
        addition: params?.addition,
        keyword: params?.keyword,
      };
      return JSON.stringify(retrieveParams) !== JSON.stringify(favoriteParams);
    },
  },
  provide() {
    return {
      addFilterCondition: this.addFilterCondition,
    };
  },
  watch: {
    indexId(val) { // 切换索引集和初始化索引 id 时改变
      const option = this.indexSetList.find(item => item.index_set_id === val);
      this.indexSetItem = option ? option : { index_set_name: '', indexName: '', scenario_name: '', scenario_id: '' };
      // eslint-disable-next-line camelcase
      this.isSearchAllowed = !!option?.permission?.[authorityMap.SEARCH_LOG_AUTH];
      this.retrieveConfigId = option?.collector_config_id;
      if (this.isSearchAllowed) {
        this.authPageInfo = null;
        this.hasAuth = true;
      }
      this.isSqlSearchType = true;
      this.resetRetrieveCondition();
      this.$store.commit('updateIndexId', val);
      this.retrieveSearchNumber = 0; // 切换索引集 检索次数设置为0;
      val && this.requestSearchHistory(val);
    },
    spaceUid: {
      async handler() {
        this.indexId = '';
        this.indexSetList.splice(0);
        this.totalFields.splice(0);
        this.activeFavorite = {};
        this.activeFavoriteID = -1;
        this.retrieveParams.bk_biz_id = this.bkBizId;
        this.isSqlSearchType = true;
        this.fetchPageData();
        this.retrieveSearchNumber = 0; // 切换业务 检索次数设置为0;
      },
      immediate: true,
    },
    isSearchAllowed(val) {
      if (val && this.isRetrieveHome) {
        // 请求历史记录
        this.$http.request('retrieve/getHistoryList', {
          params: {
            index_set_id: this.indexId,
          },
        }).then((res) => {
          this.historyList = res.data;
        })
          .catch((e) => {
            console.warn(e);
          });
      }
    },
    showSearchPage(val) {
      if (val) this.$store.commit('retrieve/updateDisplayRetrieve', true);
    },
    asIframe: {
      immediate: true,
      handler(val) {
        this.isAsIframe = val;
      },
    },
    iframeQuery: {
      deep: true,
      handler(val) {
        this.localIframeQuery = val;
      },
    },
  },
  created() {
    this.$http.request('meta/footer').then((res) => {
      this.footerHtml = res.data;
    })
      .catch((err) => {
        console.warn(err);
      });
    this.getGlobalsData();
  },
  mounted() {
    if (!this.isHideAutoQueryTips) {
      this.checkAutoQueryTips();
    }
    window.bus.$on('retrieveWhenChartChange', this.retrieveWhenChartChange);
  },
  beforeDestroy() {
    window.bus.$off('retrieveWhenChartChange', this.retrieveWhenChartChange);
    clearTimeout(this.timer);
    this.timer = null;
  },
  methods: {
    checkAutoQueryTips() {
      if (this.$refs.queryTipPopover) {
        this.$refs.queryTipPopover.instance.show();
        return;
      }
      setTimeout(() => {
        this.checkAutoQueryTips();
      }, 100);
    },
    toggleCog() {
      if (!this.isHideAutoQueryTips) {
        localStorage.setItem('hideAutoQueryTips', true);
        this.isHideAutoQueryTips = true;
      }
    },
    toggleNotice() {
      localStorage.setItem('hideAutoQueryTips', true);
      this.isHideAutoQueryTips = true;
      this.$refs.queryTipPopover.instance.hide();
    },
    // 切换到监控指标检索
    handleCheckMonitor() {
      window.parent.postMessage('datarieval-click', '*');
    },
    // 切换到监控事件检索
    handleCheckEvent() {
      window.parent.postMessage('event-click', '*');
    },
    async fetchPageData() {
      // 有spaceUid且有业务权限时 才去请求索引集列表
      if (!this.authMainPageInfo && this.spaceUid) {
        // 收藏侧边栏打开且 则先获取到收藏列表再获取索引集列表
        this.isShowCollect && await this.getFavoriteList();
        this.requestOperateList();
        this.requestIndexSetList();
      } else {
        this.isFirstLoad = false;
      }
    },
    updateIndexSetList() {
      this.$http.request('retrieve/getIndexSetList', {
        query: {
          space_uid: this.spaceUid,
        },
      }).then((res) => {
        if (res.data.length) { // 有索引集
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            // eslint-disable-next-line camelcase
            if (item.permission?.[authorityMap.SEARCH_LOG_AUTH]) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          const indexSetList = s1.concat(s2);

          // 索引集数据加工
          indexSetList.forEach((item) => {
            item.index_set_id = `${item.index_set_id}`;
            item.indexName = item.index_set_name;
            item.lightenName = ` (${item.indices.map(item => item.result_table_id).join(';')})`;
          });
          this.indexSetList = indexSetList;
        }
      });
    },
    // 初始化索引集
    requestIndexSetList() {
      const spaceUid = (this.$route.query.spaceUid && this.isFirstLoad)
        ? this.$route.query.spaceUid : this.spaceUid;
      this.basicLoading = true;
      this.$http.request('retrieve/getIndexSetList', {
        query: {
          space_uid: spaceUid,
        },
      }).then((res) => {
        if (res.data.length) { // 有索引集
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            // eslint-disable-next-line camelcase
            if (item.permission?.[authorityMap.SEARCH_LOG_AUTH]) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          const indexSetList = s1.concat(s2);

          // 索引集数据加工
          indexSetList.forEach((item) => {
            item.index_set_id = `${item.index_set_id}`;
            item.indexName = item.index_set_name;
            item.lightenName = ` (${item.indices.map(item => item.result_table_id).join(';')})`;
          });
          this.indexSetList = indexSetList;

          const indexId = this.$route.params.indexId?.toString();
          const routeIndexSet = indexSetList.find(item => item.index_set_id === indexId);
          const isRouteIndex = !!routeIndexSet && !routeIndexSet?.permission?.[authorityMap.SEARCH_LOG_AUTH];

          // 如果都没有权限或者路由带过来的索引集无权限则显示索引集无权限
          // eslint-disable-next-line camelcase
          if (!indexSetList[0]?.permission?.[authorityMap.SEARCH_LOG_AUTH] || isRouteIndex) {
            const authIndexID = indexId || indexSetList[0].index_set_id;
            this.$store.dispatch('getApplyData', {
              action_ids: [authorityMap.SEARCH_LOG_AUTH],
              resources: [{
                type: 'indices',
                id: authIndexID,
              }],
            }).then((res) => {
              this.authPageInfo = res.data;
              this.$router.push({
                name: 'retrieve',
                params: {
                  indexId: null,
                },
                query: {
                  spaceUid: this.$store.state.spaceUid,
                  bizId: this.$store.state.bkBizId,
                },
              });
            })
              .catch((err) => {
                console.warn(err);
              })
              .finally(() => {
                this.basicLoading = false;
              });
            return;
          }
          this.hasAuth = true;


          if (indexId) { // 1、初始进入页面带ID；2、检索ID时切换业务；
            const indexItem = indexSetList.find(item => item.index_set_id === indexId);
            this.indexId = indexItem ? indexItem.index_set_id : indexSetList[0].index_set_id;
            this.retrieveLog();
          } else if (!this.isRetrieveHome) { // 无索引集时也在详情页，切换业务新的业务有索引集
            this.indexId = indexSetList[0].index_set_id;
            this.retrieveLog();
          } else { // 直接进入首页或通过导航进入检索页
            this.indexId = indexSetList.some(item => item.index_set_id === this.storedIndexID)
              ? this.storedIndexID
              : indexSetList[0].index_set_id;
            if (this.isAsIframe) { // 监控 iframe
              if (this.localIframeQuery.indexId) {
                if (this.indexSetList.some(item => item.index_set_id === this.localIframeQuery.indexId)) {
                  this.indexId = this.localIframeQuery.indexId;
                }
              }
              this.retrieveLog();
            } else {
              const queryObj = {
                spaceUid: this.$store.state.spaceUid,
                bizId: this.$store.state.bkBizId,
              };
              if (this.$route.query.from) {
                queryObj.from = this.$route.query.from;
              }
              this.$router.push({
                name: 'retrieve',
                params: {
                  indexId: null,
                },
                query: queryObj,
              });
            }
          }
          this.isNoIndexSet = false;
        } else { // 无索引集
          this.isRetrieveHome = false;
          this.isNoIndexSet = true;
          const queryObj = {
            spaceUid: this.$store.state.spaceUid,
            bizId: this.$store.state.bkBizId,
          };
          if (this.$route.query.from) {
            queryObj.from = this.$route.query.from;
          }
          this.$router.push({
            name: 'retrieve',
            params: {
              indexId: null,
            },
            query: queryObj,
          });
          this.indexId = '';
          this.indexSetList.splice(0);
        }
      })
        .catch((e) => {
          console.warn(e);
          this.isNoIndexSet = false;
          this.indexId = '';
          this.indexSetList.splice(0);
        })
        .finally(() => {
          this.basicLoading = false;
          this.isFirstLoad = false;
        });
    },
    // 获取检索历史
    requestSearchHistory(indexId) {
      this.$http.request('retrieve/getSearchHistory', {
        params: {
          index_set_id: indexId,
        },
      }).then((res) => {
        this.statementSearchrecords = res.data;
      });
    },
    requestOperateList() {
      this.$http.request('retrieve/getOperators').then((res) => {
        this.filterAllOperators = res.data;
      });
    },
    // 切换索引
    handleSelectIndex(val) {
      this.indexId = val;
      this.activeFavoriteID = -1;
      this.activeFavorite = {};
      if (!this.isRetrieveHome) {
        this.retrieveLog();
      }
    },
    // 切换索引时重置检索数据
    resetRetrieveCondition() {
      // 重置搜索条件，起始位置、日期相关字段不变
      // Object.assign(this.retrieveParams, {
      //     keyword: '*',
      //     host_scopes: {
      //         modules: [],
      //         ips: ''
      //     },
      //     addition: []
      // })
      // 过滤相关
      this.statisticalFieldsData = {};
      this.retrieveDropdownData = {};
      this.logList = [];
      // 字段相关
      this.totalFields.splice(0);
    },
    // 检索参数：日期改变
    handleDateChange(val) {
      this.datePickerValue = val;
      this.pickerTimeRange = val.every(item => item.includes('now')) ? val : [];
      this.formatTimeRange();
    },
    /**
     * @desc 时间选择组件返回时间戳格式转换
     */
    formatTimeRange() {
      const tempList = handleTransformToTimestamp(this.datePickerValue);
      Object.assign(this.retrieveParams, {
        start_time: formatDate(tempList[0] * 1000),
        end_time: formatDate(tempList[1] * 1000),
      });
    },
    updateSearchParam(addition, host) {
      this.retrieveParams.addition = addition;
      this.retrieveParams.host_scopes = host;
    },
    // 日期选择器选择时间完毕，检索
    retrieveWhenDateChange() {
      this.shouldUpdateFields = true;
      this.retrieveLog();
    },
    handleSettingMenuClick(val) {
      this.clickSettingChoice = val;
      this.isShowSettingModal = true;
    },
    // 添加过滤条件
    addFilterCondition(field, operator, value, index) {
      const isExist = this.retrieveParams.addition.some((addition) => {
        return addition.field === field
        && addition.operator === operator
        && addition.value.toString() === value.toString();
      });
      // 已存在相同条件
      if (isExist) return;

      const startIndex = index > -1 ? index : this.retrieveParams.addition.length;
      const deleteCount = index > -1 ? 1 : 0;
      this.retrieveParams.addition.splice(startIndex, deleteCount, { field, operator, value });
      if (this.isAutoQuery) {
        this.retrieveLog();
      }
    },
    removeFilterCondition(index) {
      this.retrieveParams.addition.splice(index, 1);
      this.retrieveLog();
    },
    // 打开 ip 选择弹窗
    openIpQuick() {
      // this.$refs.ipQuick.openDialog();
      this.showIpSelectorDialog = true;
    },
    // IP 选择
    handleSaveIpQuick(data) {
      // this.retrieveParams.host_scopes = data;
      const { target_node_type: targetNodeType, target_nodes: targetNodes } = data;
      this.retrieveParams.host_scopes.target_node_type = targetNodes.length ? targetNodeType : '';
      this.retrieveParams.host_scopes.target_nodes = targetNodes.map((node) => {
        const targets = ['TOPO', 'SERVICE_TEMPLATE', 'SET_TEMPLATE'].includes(targetNodeType)
          ? {
            node_path: node.node_path,
            bk_inst_name: node.bk_inst_name,
            bk_inst_id: node.bk_inst_id,
            bk_obj_id: node.bk_obj_id,
          }
          : targetNodeType === 'DYNAMIC_GROUP' ? { id: node.id, name: node.name, bk_obj_id: node.bk_obj_id }
            : { ip: node.ip, bk_cloud_id: node.bk_cloud_id, bk_supplier_id: node.bk_supplier_id };
        return targets;
      });
      this.showIpSelectorDialog = false;
      if (this.isAutoQuery) {
        this.retrieveLog();
      }
    },
    // 清空条件
    clearCondition() {
      Object.assign(this.retrieveParams, {
        keyword: '',
        host_scopes: {
          modules: [],
          ips: '',
          target_nodes: [],
          target_node_type: '',
        },
        addition: [],
      });
      this.isClearCondition = !this.isClearCondition;
      this.retrieveLog();
    },
    // 搜索记录
    retrieveFavorite({ index_set_id: indexSetID, params }) {
      if (this.indexSetList.find(item => item.index_set_id === String(indexSetID))) {
        this.isFavoriteSearch = true;
        this.indexId = String(indexSetID);
        const { search_fields, ...reset } = params;
        this.retrieveLog(reset);
      } else {
        this.messageError(this.$t('没有找到该记录下相关索引集'));
      }
    },
    /**
     * @desc: 检索日志
     * @param {Any} historyParams 历史数据
     * @param {Boolean} isMemoryFields 检索时是否需要记住当前展示的字段
     * @param {Boolean} isRequestChartsAndHistory 检索时是否请求历史记录和图表
     */
    async retrieveLog(historyParams, isMemoryFields = false, isRequestChartsAndHistory = true) {
      if (!this.indexId) return;
      const memoryFields = this.visibleFields.map(item => item.field_name);
      await this.$nextTick();
      this.basicLoading = true;
      this.showHistory = false;
      this.activeTab = 'search';
      this.$refs.resultHeader && this.$refs.resultHeader.pauseRefresh();

      // 是否有检索的权限
      const paramData = {
        action_ids: [authorityMap.SEARCH_LOG_AUTH],
        resources: [{
          type: 'indices',
          id: this.indexId,
        }],
      };
      if (this.isSearchAllowed === null) { // 直接从 url 进入页面 checkAllowed && getApplyData
        try {
          this.resultLoading = true;
          const res = await this.$store.dispatch('checkAndGetData', paramData);
          if (res.isAllowed === false) {
            this.isSearchAllowed = false;
            this.$store.commit('updateAuthDialogData', res.data);
            return;
          }
        } catch (err) {
          console.warn(err);
          return;
        } finally {
          this.resultLoading = false;
        }
      } else if (this.isSearchAllowed === false) { // 已知当前选择索引无权限
        try {
          this.basicLoading = true;
          const res = await this.$store.dispatch('getApplyData', paramData);
          this.$store.commit('updateAuthDialogData', res.data);
        } catch (err) {
          console.warn(err);
        } finally {
          this.basicLoading = false;
        }
        return;
      }

      // 设置检索参数，历史记录或收藏的参数
      if (historyParams) {
        Object.assign(this.retrieveParams, historyParams);
        // 禁用 IP 快选时过滤历史记录或收藏中相关字段
        // if (!this.showIpQuick) {
        //   this.retrieveParams.host_scopes.ips = '';
        // }
      }
      // 通过 url 查询参数设置检索参数
      let queryParams = {};
      let queryParamsStr = {};
      const urlRetrieveParams = this.$route.query.retrieveParams;
      if (urlRetrieveParams) {
        try {
          queryParams = JSON.parse(decodeURIComponent(urlRetrieveParams));
          queryParamsStr = JSON.parse(decodeURIComponent(urlRetrieveParams));
          if (queryParams.start_time && queryParams.end_time) {
            this.datePickerValue = [queryParams.start_time, queryParams.end_time];
          }
        } catch (e) {
          console.warn('url 查询参数解析失败', e);
        }
      } else { // 兼容之前的语法
        const shouldCoverParamFields = [
          'keyword',
          'host_scopes',
          'addition',
          'start_time',
          'end_time',
          'time_range',
          'pickerTimeRange',
        ];
        for (const field of shouldCoverParamFields) {
          if (this.isInitPage) {
            const param = this.$route.query[field]; // 指定查询参数
            if (param) {
              if (field === 'pickerTimeRange') {
                queryParams.pickerTimeRange = decodeURIComponent(param).split(',');
                queryParamsStr.pickerTimeRange = param;
              } else {
                queryParams[field] = ['keyword', 'start_time', 'end_time', 'time_range'].includes(field)
                  ? decodeURIComponent(param)
                  : decodeURIComponent(param) ? JSON.parse(decodeURIComponent(param)) : param;
                queryParamsStr[field] = param;
              }
            }
            if (queryParams.start_time && queryParams.end_time) {
              this.datePickerValue = [queryParams.start_time, queryParams.end_time];
            }
          } else {
            switch (field) {
              case 'keyword':
              case 'start_time':
              case 'end_time':
              case 'time_range':
                if (this.retrieveParams[field] !== '') {
                  queryParamsStr[field] = encodeURIComponent(this.retrieveParams[field]);
                }
                break;
              case 'addition':
                if (this.retrieveParams[field].length) {
                  queryParamsStr[field] = (JSON.stringify(this.retrieveParams[field]));
                }
                break;
              case 'host_scopes':
                if (this.retrieveParams[field].ips !== ''
                || this.retrieveParams[field].modules.length
                || this.retrieveParams[field].target_nodes.length) {
                  queryParamsStr[field] = (JSON.stringify(this.retrieveParams[field]));
                }
                break;
              case 'pickerTimeRange':
                if (this[field].length) {
                  queryParamsStr[field] = encodeURIComponent(this[field]);
                }
              default:
                break;
            }
          }
        }
      }
      // 进入检索详情页
      this.isRetrieveHome = false;
      const queryObj = {
        spaceUid: this.$store.state.spaceUid,
        bizId: this.$store.state.bkBizId,
        ...queryParamsStr,
      };
      if (this.$route.query.from) {
        queryObj.from = this.$route.query.from;
      }
      this.$router.push({
        name: 'retrieve',
        params: {
          indexId: this.indexId,
        },
        query: queryObj,
      });
      // 接口请求
      try {
        this.tableLoading = true;
        this.resetResult();
        if (!this.totalFields.length || this.shouldUpdateFields) {
          window.bus.$emit('openChartLoading');
          await this.requestFields();
          this.shouldUpdateFields = false;
        }

        if (this.isInitPage) {
          Object.assign(this.retrieveParams, queryParams); // 回填查询参数中的检索条件
          if (queryParams.pickerTimeRange?.length) {
            this.pickerTimeRange = queryParams.pickerTimeRange;
            this.datePickerValue = queryParams.pickerTimeRange;
            this.formatTimeRange();
          }
          this.isInitPage = false;
        }

        this.retrieveParams.keyword = this.retrieveParams.keyword.trim();
        if (isRequestChartsAndHistory) { // 是否请求图表和历史记录
          this.requestChart();
          this.requestSearchHistory(this.indexId);
        }

        await this.handleResetTimer();
        await this.requestTable();
        if (this.isAfterRequestFavoriteList) await this.getFavoriteList();

        // 已检索 判断当前检索是否是初始化的收藏检索 添检索次数
        const beAddedNumber = (!this.retrieveSearchNumber && this.isFavoriteSearch) ? 2 : 1;
        this.retrieveSearchNumber += beAddedNumber;
      } catch (e) {
        console.warn(e);
        if (!e.message.includes('request canceled')) { // 接口出错、非重复请求被取消
          this.tableLoading = false;
        }
      } finally {
        // 如果是收藏检索并且开启检索显示, 合并当前字段和收藏字段 更新显示字段
        // eslint-disable-next-line camelcase
        if (this.isFavoriteSearch && this.activeFavorite?.is_enable_display_fields) {
          const { display_fields: favoriteDisplayFields } = this.activeFavorite;
          const displayFields = [...new Set([...memoryFields, ...favoriteDisplayFields])];
          this.handleFieldsUpdated(displayFields, undefined, false);
        };
        // 检索完后 回显当前展示的字段
        if (isMemoryFields && memoryFields.length) this.handleFieldsUpdated(memoryFields, undefined, false);
        if (this.isFavoriteSearch) {
          setTimeout(() => {
            this.initSearchList();
          }, 500);
          this.isSqlSearchType = !this.isShowUiType; // 判断是否有表单模式的数组值 如果有 则切换为表单模式
        }
        // 搜索完毕后，如果开启了自动刷新，会在 timeout 后自动刷新
        this.$refs.resultHeader && this.$refs.resultHeader.setRefreshTime();
        this.isFavoriteSearch = false;
        this.isAfterRequestFavoriteList = false;
        this.favoriteUpdateLoading = false;
        this.basicLoading = false;
      }
    },
    // 请求字段
    async requestFields() {
      if (this.isThollteField) return;
      this.isThollteField = true;
      try {
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: { index_set_id: this.indexId },
          query: {
            start_time: this.retrieveParams.start_time,
            end_time: this.retrieveParams.end_time,
            is_realtime: 'True',
          },
        });
        const notTextTypeFields = [];
        const { data } = res;
        const {
          fields,
          config,
          display_fields: displayFields,
          time_field: timeField,
          sort_list: sortList,
          config_id,
        } = data;
        const localConfig = {};
        config.forEach((item) => {
          localConfig[item.name] = { ...item };
        });
        const {
          bkmonitor,
          ip_topo_switch: ipTopoSwitch,
          context_and_realtime: contextAndRealtime,
          bcs_web_console: bcsWebConsole,
          async_export: asyncExport,
          clean_config: cleanConfig,
          clustering_config: clusteringConfig,
          apm_relation: apmRelation,
        } = localConfig;

        this.operatorConfig = { // 操作按钮配置信息
          bkmonitor,
          bcsWebConsole,
          contextAndRealtime,
          timeField,
        };
        // 初始化操作按钮消息
        this.operatorConfig.toolMessage = this.initToolTipsMessage(this.operatorConfig);
        this.cleanConfig = cleanConfig;
        this.clusteringData = clusteringConfig;
        this.apmRelationData = apmRelation;

        fields.forEach((item) => {
          item.minWidth = 0;
          item.filterExpand = false; // 字段过滤展开
          item.filterVisible = true; // 字段过滤搜索字段名是否显示
          if (item.field_type !== 'text') {
            notTextTypeFields.push(item.field_name);
          }
        });
        this.notTextTypeFields = notTextTypeFields;
        this.ipTopoSwitch = ipTopoSwitch.is_active;
        this.bkmonitorUrl = bkmonitor.is_active;
        this.asyncExportUsable = asyncExport.is_active;
        this.asyncExportUsableReason = !asyncExport.is_active ? asyncExport.extra.usable_reason : '';
        this.timeField = timeField;
        this.totalFields = fields;
        // 后台给的 display_fields 可能有无效字段 所以进行过滤，获得排序后的字段
        this.visibleFields = displayFields.map((displayName) => {
          for (const field of fields) {
            if (field.field_name === displayName) {
              return field;
            }
          }
        }).filter(Boolean);
        this.sortList = sortList;

        const fieldAliasMap = {};
        fields.forEach((item) => {
          fieldAliasMap[item.field_name] = item.field_alias || item.field_name;
        });
        this.fieldAliasMap = fieldAliasMap;
        this.isThollteField = false;
        this.$store.commit('retrieve/updateFiledSettingConfigID', config_id); // 当前配置ID
      } catch (e) {
        this.ipTopoSwitch = true;
        this.bkmonitorUrl = false;
        this.asyncExportUsable = true;
        this.asyncExportUsableReason = '';
        this.timeField = '';
        this.totalFields.splice(0);
        this.visibleFields.splice(0);
        this.isThollteField = false;
        throw e;
      }
    },
    /**
     * @desc: 字段设置更新了
     * @param {Array} displayFieldNames 展示字段
     * @param {Boolean} showFieldAlias 是否别名
     * @param {Boolean} isRequestFields 是否请求字段
     */
    async handleFieldsUpdated(displayFieldNames, showFieldAlias, isRequestFields = true) {
      this.$store.commit('updateClearTableWidth', 1);
      this.visibleFields = displayFieldNames.map((displayName) => {
        for (const field of this.totalFields) {
          if (field.field_name === displayName) {
            return field;
          }
        }
      });
      if (showFieldAlias !== undefined) {
        this.showFieldAlias = showFieldAlias;
        window.localStorage.setItem('showFieldAlias', showFieldAlias);
      }
      this.renderTable = false;
      await this.$nextTick();
      isRequestFields && this.requestFields();
      this.renderTable = true;
    },
    requestTableData() {
      if (this.timer || this.requesting) return;

      this.requestTable();
    },
    // 表格
    async requestTable() {
      // 轮循结束
      if (this.finishPolling || this.requesting) return;

      this.requesting = true;

      if (!this.isPollingStart) {
        const { startTimeStamp, endTimeStamp } = this.getRealTimeRange();
        this.startTimeStamp = startTimeStamp;
        this.endTimeStamp = endTimeStamp;
        // 请求间隔时间
        this.requestInterval = this.isPollingStart ? this.requestInterval
          : this.handleRequestSplit(startTimeStamp, endTimeStamp);
        // 获取坐标分片间隔
        this.handleIntervalSplit(startTimeStamp, endTimeStamp);

        this.pollingEndTime = endTimeStamp;
        this.pollingStartTime = this.pollingEndTime - this.requestInterval;
        if (this.pollingStartTime < startTimeStamp || this.requestInterval === 0) {
          this.pollingStartTime = startTimeStamp;
        }
        this.isPollingStart = true;
      } else if (this.isNextTime) {
        this.pollingEndTime = this.pollingStartTime;
        this.pollingStartTime = this.pollingStartTime - this.requestInterval;

        if (this.pollingStartTime < this.startTimeStamp) {
          this.pollingStartTime = this.startTimeStamp;
        }
      }

      const { currentPage, pageSize } = this.$refs.resultMainRef;
      const begin = currentPage === 1 ? 0 : (currentPage - 1) * pageSize;

      try {
        const baseUrl = process.env.NODE_ENV === 'development' ? 'api/v1' : window.AJAX_URL_PREFIX;
        const res = await axios({
          method: 'post',
          url: `/search/index_set/${this.indexId}/search/`,
          withCredentials: true,
          baseURL: baseUrl,
          responseType: 'blob',
          data: {
            ...this.retrieveParams,
            time_range: 'customized',
            begin,
            size: pageSize,
            interval: this.interval,
            // 每次轮循的起始时间
            start_time: formatDate(this.pollingStartTime),
            end_time: formatDate(this.pollingEndTime),
          },
        }).then((res) => {
          return readBlobRespToJson(res.data);
        });

        this.isNextTime = res.data.list.length < pageSize;
        if (this.isNextTime && (this.pollingStartTime <= this.startTimeStamp
        || this.requestInterval === 0)) { // 分片时间已结束
          this.finishPolling = true;
        }

        this.retrievedKeyword = this.retrieveParams.keyword;
        this.tookTime = this.tookTime + Number(res.data.took) || 0;
        this.tableData = { ...res.data, finishPolling: this.finishPolling };
        this.logList = this.logList.concat(parseBigNumberList(res.data.list));
        this.statisticalFieldsData = this.getStatisticalFieldsData(this.logList);
        this.computeRetrieveDropdownData(this.logList);
      } catch (err) {
        this.$refs.resultMainRef.isPageOver = false;
      } finally {
        this.requesting = false;
        if (this.isNextTime) {
          if (this.finishPolling) { // 已请求所有分片时间仍无结果
            this.$refs.resultMainRef.isPageOver = false;
            this.tableLoading = false;
          } else { // 往下一个时间分片获取
            clearTimeout(this.timer);
            this.timer = null;
            this.timer = setTimeout(() => {
              this.$refs.resultMainRef.currentPage = 1;
              this.requestTable();
            }, 500);
          }
        } else {
          clearTimeout(this.timer);
          this.timer = null;
          this.tableLoading = false;
        }
      }
    },
    // 根据表格数据统计字段值及出现次数
    getStatisticalFieldsData(listData) {
      const result = {};
      listData.forEach((dataItem) => {
        this.recursiveObjectData(result, dataItem);
      });
      return result;
    },
    recursiveObjectData(result, dataItem, prefixFieldKey = '') {
      dataItem && Object.entries(dataItem).forEach(([field, value]) => {
        if (typeof value === 'object') {
          this.recursiveObjectData(result, value, `${prefixFieldKey + field}.`);
        } else {
          const fullFieldKey = prefixFieldKey ? prefixFieldKey + field : field;
          const fieldData = result[fullFieldKey] || (result[fullFieldKey] = Object.defineProperties({}, {
            __totalCount: { // 总记录数量
              value: 0,
              writable: true,
            },
            __validCount: { // 有效值数量
              value: 0,
              writable: true,
            },
          }));
          fieldData.__totalCount += 1;
          if (value || value === 0) {
            fieldData.__validCount += 1;
            if (fieldData[value]) {
              fieldData[value] += 1;
            } else {
              fieldData[value] = 1;
            }
          }
        }
      });
    },
    // 更新下拉字段可选值信息
    computeRetrieveDropdownData(listData) {
      listData.forEach((dataItem) => {
        this.recursiveIncreaseData(dataItem);
      });
    },
    recursiveIncreaseData(dataItem, prefixFieldKey = '') {
      dataItem && Object.entries(dataItem).forEach(([field, value]) => {
        if (typeof value === 'object') {
          this.recursiveIncreaseData(value, `${prefixFieldKey + field}.`);
        } else {
          const fullFieldKey = prefixFieldKey ? prefixFieldKey + field : field;
          if (value || value === 0) {
            let fieldData = this.retrieveDropdownData[fullFieldKey];
            if (!fieldData) {
              this.$set(this.retrieveDropdownData, fullFieldKey, Object.defineProperties({}, {
                __fieldType: { // 该字段下的值的数据类型，可能是数值、字符串、布尔值
                  value: typeof value,
                },
              }));
              fieldData = this.retrieveDropdownData[fullFieldKey];
            }
            if (this.notTextTypeFields.includes(field) && !fieldData[value]) {
              // 非 text 类型字段统计可选值，text 则由用户手动输入
              fieldData[value] = 1;
            }
          }
        }
      });
    },
    // 图表
    requestChart() {
      this.$store.commit('retrieve/updateChartKey');
    },
    // 图表款选或双击回正时请求相关数据
    async retrieveWhenChartChange() {
      this.activeTab = 'search';
      this.$refs.resultHeader && this.$refs.resultHeader.pauseRefresh();
      // 接口请求
      try {
        this.tableLoading = true;
        this.resetResult();
        // 表格数据重新轮询
        await this.handleResetTimer();
        await this.requestTable();
      } catch (e) {
        console.warn(e);
        if (!e.message.includes('request canceled')) { // 接口出错、非重复请求被取消
          this.tableLoading = false;
        }
      }
    },

    // 重置轮询
    handleResetTimer() {
      clearTimeout(this.timer);
      this.timer = null;
      this.isPollingStart = false;
      this.finishPolling = false;
      this.$refs.resultMainRef.reset();
    },

    // 重置搜索结果
    resetResult() {
      // 内容
      this.totalCount = 0;
      this.tookTime = 0;
      this.tableData = {};
      // 字段过滤展开
      this.totalFields.forEach((item) => {
        item.filterExpand = false;
      });
      // 字段值统计数据
      this.statisticalFieldsData = {};
      this.logList = [];
    },
    // 控制页面布局宽度
    dragBegin(e) {
      this.isChangingWidth = true;
      this.currentTreeBoxWidth = this.leftPanelWidth;
      this.currentScreenX = e.screenX;
      window.addEventListener('mousemove', this.dragMoving, { passive: true });
      window.addEventListener('mouseup', this.dragStop, { passive: true });
    },
    dragMoving(e) {
      const newTreeBoxWidth = this.currentTreeBoxWidth + e.screenX - this.currentScreenX;
      if (newTreeBoxWidth < this.leftPanelMinWidth) {
        this.leftPanelWidth = 0;
        this.showRetrieveCondition = false;
        this.dragStop();
        // 第一次关闭条件面板时，显示一个只显示一次的初始显示的 tips
        window.addEventListener('mouseup', () => {
          if (!this.hasExpandInitTipsShown) {
            setTimeout(() => {
              this.showExpandInitTips = true;
            }, 40);
          }
        }, { once: true });
      } else if (newTreeBoxWidth >= this.leftPanelMaxWidth) {
        this.leftPanelWidth = this.leftPanelMaxWidth;
      } else {
        this.leftPanelWidth = newTreeBoxWidth;
      }
      // window.bus.$emit('set-chart-width');
    },
    dragStop() {
      this.isChangingWidth = false;
      this.currentTreeBoxWidth = null;
      this.currentScreenX = null;
      window.removeEventListener('mousemove', this.dragMoving);
      window.removeEventListener('mouseup', this.dragStop);
    },
    openRetrieveCondition() {
      // window.bus.$emit('set-chart-width');
      this.leftPanelWidth = this.leftPanelMinWidth;
      this.showRetrieveCondition = true;
    },
    closeRetrieveCondition() {
      this.leftPanelWidth = 0;
      this.showRetrieveCondition = false;
    },
    updateCollectCondition(status) {
      this.collectWidth = status ? 240 : 0;
      localStorage.setItem('isAutoShowCollect', `${status}`);
      this.isShowCollect = status;
      if (!status) {
        this.activeFavorite = {};
        this.activeFavoriteID = -1;
        this.isSqlSearchType = true;
      }
    },
    // 初始 tips 消失后显示普通的 tips
    handleInitTipsHidden() {
      this.hasExpandInitTipsShown = true;
      this.showExpandInitTips = false;
    },
    // 获取全局数据和 判断是否可以保存 已有的日志聚类
    getGlobalsData() {
      if (Object.keys(this.globalsData).length) return;
      this.$http.request('collect/globals').then((res) => {
        this.$store.commit('globals/setGlobalsData', res.data);
      })
        .catch((e) => {
          console.warn(e);
        });
    },
    initToolTipsMessage(config) {
      const { contextAndRealtime, bkmonitor } = config;
      return {
        monitorWeb: bkmonitor.is_active ? this.$t('监控告警') : bkmonitor?.extra.reason,
        realTimeLog: contextAndRealtime.is_active ? this.$t('实时日志') : contextAndRealtime?.extra.reason,
        contextLog: contextAndRealtime.is_active ? this.$t('上下文') : contextAndRealtime?.extra.reason,
      };
    },
    // 点击新增收藏
    handleClickFavorite() {
      // 如果点击过收藏，进行参数判断
      const displayFields = this.visibleFields.map(item => item.field_name);
      const indexItem = this.indexSetList.find(item => item.index_set_id === String(this.indexId));
      const { modules, ips, target_node_type, target_nodes } =  this.retrieveParams.host_scopes;
      // eslint-disable-next-line camelcase
      const host_scopes = { modules, ips, target_node_type, target_nodes }; // 初始化host传参
      if (!modules) host_scopes.modules = [];
      if (!ips) host_scopes.ips = '';
      if (!host_scopes.target_node_type) {
        host_scopes.target_node_type = '';
        host_scopes.target_nodes = [];
      }
      const favoriteData = { // 新增收藏参数
        index_set_id: this.indexId,
        space_uid: this.spaceUid,
        index_set_name: indexItem.index_set_name,
        display_fields: displayFields,
        visible_type: 'public',
        name: '',
        is_enable_display_fields: false,
        params: {
          host_scopes,
          keyword: Boolean(this.retrieveParams.keyword) ? this.retrieveParams.keyword : '*',
          addition: this.retrieveParams.addition,
          search_fields: [],
        },
      };
      this.addFavoriteData = favoriteData;
      this.isShowAddNewCollectDialog = true; // 展示新增弹窗
    },
    // 更新参数更变后的收藏
    async handleUpdateFavorite() {
      try {
        this.favoriteUpdateLoading = true;
        const {
          params,
          name,
          group_id,
          display_fields,
          visible_type,
          id,
        } = this.activeFavorite;
        const { search_fields } = params;
        const { host_scopes, addition, keyword } = this.retrieveParams;
        const data = {
          name,
          group_id,
          display_fields,
          visible_type,
          host_scopes,
          addition,
          keyword,
          search_fields,
        };
        if (!data.search_fields.length) this.isSqlSearchType = true;
        const res = await this.$http.request('favorite/updateFavorite', {
          params: { id },
          data,
        });
        if (res.result) {
          this.$bkMessage({
            message: this.$t('更新成功'),
            theme: 'success',
          });
          if (this.isAutoQuery && this.isSqlSearchType) {
            this.isAfterRequestFavoriteList = true;
          }
        };
      } finally {
        await this.getFavoriteList();
        this.favoriteUpdateLoading = false;
      }
    },
    // 检索头部点击编辑收藏
    handleEditFavorite() {
      if (this.basicLoading) return;
      // 获取检索页面的数据替换当前收藏详情参数
      this.replaceFavoriteData = this.getRetrieveFavoriteData();
      this.isShowAddNewCollectDialog = true;
    },
    // 当前检索监听的收藏参数
    getRetrieveFavoriteData() {
      return {
        params: {
          host_scopes: this.retrieveParams.host_scopes,
          addition: this.retrieveParams.addition,
          keyword: this.retrieveParams.keyword,
        },
        display_fields: this.visibleFields.map(item => item.field_name),
      };
    },

    handleChangeSearchType() {
      if (this.tableLoading) return;
      this.isAutoQuery = !this.isAutoQuery;
      localStorage.setItem('closeAutoQuery', !this.isAutoQuery);
    },
    /** 获取收藏列表 */
    async getFavoriteList() {
      // 第一次显示收藏列表时因路由更变原因 在本页面第一次请求
      try {
        this.favoriteLoading = true;
        const { data } = await this.$http.request('favorite/getFavoriteByGroupList', {
          query: {
            space_uid: this.spaceUid,
            order_type: localStorage.getItem('favoriteSortType') || 'NAME_ASC',
          },
        });
        const provideFavorite = data[0];
        const publicFavorite = data[data.length - 1];
        const sortFavoriteList = data.slice(1, data.length - 1)
          .sort((a, b) => a.group_name.localeCompare(b.group_name));
        const sortAfterList = [provideFavorite, ...sortFavoriteList, publicFavorite];
        this.favoriteList = sortAfterList;
      } catch (err) {
        this.favoriteLoading = false;
        this.favoriteList = [];
      } finally {
        // 获取收藏列表后 若当前不是新检索 则判断当前收藏是否已删除 若删除则变为新检索
        if (this.activeFavoriteID !== -1) {
          let isFindCheckValue = false; // 是否从列表中找到匹配当前收藏的id
          for (const gItem of this.favoriteList) {
            const findFavorites = gItem.favorites.find(item => item.id === this.activeFavoriteID);
            if (!!findFavorites) {
              isFindCheckValue = true; // 找到 中断循环
              break;
            }
          }
          if (!isFindCheckValue) this.handleClickFavoriteItem(undefined); // 未找到 清空当前收藏 变为新检索
        }
        this.favoriteLoading = false;
      }
    },
    handleClickSearchType() {
      if (this.isSqlSearchType) {
        this.$refs.formTipsRef?.instance.set({ trigger: 'click' });
      }
      // 如果当前为sql模式，且检索的keywords和收藏的keywords不一致 则不允许切换
      if (this.isSqlSearchType && !this.isCanUseUiType) return;
      // 切换表单模式或者sql模式
      this.isSqlSearchType = !this.isSqlSearchType;
      // 如果是sql模式切到表单模式 则缓存keywords  表单切回sql模式时回填缓存的keywords
    },
    updateKeyWords(keyword) {
      // 表单模式 更新keywords
      Object.assign(this.retrieveParams, { keyword });
      if (this.isAutoQuery) {
        this.retrieveLog();
      }
    },
    handleSubmitFavorite({ isCreate, resValue }) {
      this.favoriteRequestID += 1; // 编辑或新增刷新收藏列表
      if (isCreate) { // 新建收藏 刷新收藏列表同时高亮显示新增的收藏
        this.handleClickFavoriteItem(resValue);
        if (!this.isShowCollect) this.collectWidth = 240;
        this.isShowCollect = true;
      } else {
        this.initSearchList();
      };
    },
    // 点击收藏列表的收藏
    async handleClickFavoriteItem(value) {
      if (value === undefined) { // 点击为新检索时 清空收藏
        this.activeFavoriteID = -1;
        this.activeFavorite = {};
        this.isSqlSearchType = true;
        this.isFavoriteSearch = false;
        this.clearCondition();
        return;
      }
      // 无host_scopes补充空的 host_scopes
      if (!value.params?.host_scopes?.target_node_type) {
        value.params.host_scopes = { ...value.params?.host_scopes };
        value.params.host_scopes.target_node_type = '';
        value.params.host_scopes.target_nodes = [];
      }
      this.addFavoriteData = {}; // 清空新增收藏的数据
      this.isFavoriteSearch = true;
      this.activeFavorite = value;
      this.activeFavoriteID = value.id;
      this.retrieveFavorite(value);
    },
    // 收藏列表刷新, 判断当前是否有点击活跃的收藏 如有则进行数据更新
    updateActiveFavoriteData(value) {
      this.activeFavorite = value;
      this.initSearchList();
      this.isSqlSearchType = !this.isShowUiType;
    },
    async handleBlurSearchInput(keyword) {
      keyword === '' && (keyword = '*');
      try {
        const res = await this.$http.request('favorite/getSearchFields', {
          data: { keyword },
        });
        this.inputSearchList = res.data.map(item => item.name);
      } catch (err) {
        this.inputSearchList = [];
      }
    },
    // 当点击有表单模式的收藏时 初始化search列表
    initSearchList() {
      if (this.isShowUiType) {
        this.favSearchList = this.activeFavorite.params?.search_fields || [];
        this.handleBlurSearchInput(this.activeFavorite.params?.keyword || '*');
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/scroller.scss';

  .retrieve-container {
    min-width: 1280px;
    height: 100%;

    /*首页*/
    .retrieve-home-container {
      height: 100%;
      background-position: top center;
      background-repeat: no-repeat;
      background-image: url('../../images/index_bg_01.png');
      background-color: #4a4f67;

      .retrieve-home {
        margin: 0 auto;
        padding-top: calc((100vh - 283px) * .2 + 60px);
        width: 1000px;

        .retrieve-home-title {
          margin-bottom: 35px;
          font-size: 30px;
          color: #fff;
        }

        .retrieve-home-condition {
          display: flex;

          .king-select-index-set {
            width: 320px;
            margin-right: 10px;
            border-color: #fff;
          }
        }
      }
    }

    .page-loading-wrap {
      position: absolute;
      top: 0;
      width: 100%;
      height: 4px;
      z-index: 2400;
      overflow: hidden;
      background: pink;

      @keyframes animate-loading-bar {
        0% {
          transform: translateX(0);
          transform: translateX(0);
        }

        to {
          transform: translateX(-50%);
          transform: translateX(-50%);
        }
      }

      .page-loading-bar {
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        position: absolute;
        z-index: 10;
        visibility: visible;
        display: block;
        animation: animate-loading-bar 2s linear infinite;
        background-color: transparent;
        background-image: linear-gradient(
          to right,
          #ff5656 0,
          #ff5656 50%,
          #ff9c01 50%,
          #ff9c01 85%,
          #2dcb56 85%,
          #2dcb56 100%
        );
        background-repeat: repeat-x;
        background-size: 50%;
        width: 200%;
      }
    }

    /*详情页*/
    .retrieve-detail-container {
      position: relative;
      // display: flex;
      height: 100%;

      .result-content {
        display: flex;
        height: calc(100% - 52px);
      }

      .retrieve-condition {
        display: flow-root;
        width: 450px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
        background: #fff;

        .bk-button-group {
          display: flex;
          width: 100%;
          height: 52px;

          .bk-button {
            flex: 1;
            height: 100%;
            border-top: 0;
            background: #fafbfd;
            border-color: #dcdee5;
            box-sizing: content-box;

            &.is-selected {
              background: #fff;
              border-top: none;
              border-bottom: none;
            }

            &.is-selected {
              border-color: #dcdee5;
              color: #3a84ff;
            }

            &:hover {
              border-color: #dcdee5;
            }
          }
        }

        .biz-menu-box {
          position: relative;
          margin: 16px 16px 0;
        }

        .king-tab {
          height: 100%;
          padding-top: 10px;

          .tab-content {
            /* stylelint-disable-next-line declaration-no-important */
            height: calc(100% - 52px) !important;
            overflow-y: auto;
            background-color: #fbfbfb;

            @include scroller;
          }

          .tab-content-item {
            padding: 0 24px;

            &:first-child {
              padding-bottom: 4px;
              background-color: #fff;
            }

            &:last-child {
              padding-top: 6px;
              padding-bottom: 26px;
            }
          }

          &.as-iframe {
            height: calc(100% + 10px);
          }

          .tab-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 24px 18px;
            color: #313238;
            font-size: 16px;

            .tab-title {
              font-size: 14px;
            }

            .icon-edit-line {
              color: #979ba5;
              cursor: pointer;
            }

            .tab-operation {
              display: flex;
              justify-content: space-between;
              align-items: center;
              font-size: 12px;
              user-select: none;

              .search-type {
                width: 60px;
                margin-right: 10px;
                color: #3a84ff;
                transform: translateY(-1px);
                text-align: right;
                cursor: pointer;
              }

              .icon-sort {
                display: inline-block;
                transform: rotate(90deg) translateX(-1px);
              }
            }

            .icon-cog {
              font-size: 18px;
              color: #979ba5;
              cursor: pointer;
            }

            .icon-angle-double-left-line {
              margin-left: 8px;
              color: #979ba5;
              font-size: 16px;
              cursor: pointer;
            }
          }

          .tab-item-title {
            display: flex;
            align-items: center;
            margin: 16px 0 6px;
            line-height: 20px;
            font-size: 12px;
            color: #63656e;

            &.ip-quick-title {
              margin-top: 13px;
            }

            &:first-child {
              margin-top: 0;
            }
          }

          .field-filter-title {
            margin-bottom: 0;
            padding-top: 18px;
            font-size: 14px;
            font-weight: 500;
            color: #313238;
          }

          .flex-item-title {
            display: flex;
            justify-content: space-between;

            .filter-item {
              display: flex;

              span {
                margin-left: 24px;
                color: #3a84ff;
                cursor: pointer;
              }
            }
          }

          .add-filter-condition-container {
            display: flex;
            flex-wrap: wrap;
          }

          .retrieve-button-group {
            position: sticky;
            bottom: 0;
            display: flex;
            align-items: center;
            padding: 20px 0 24px;
            background-color: #fff;
            // z-index: 1;
            ::v-deep .query-btn {
              width: 32px;
              height: 32px;
              background: #fff;
              margin-right: 2px;
              color: #9a9ba5;
              display: flex;
              justify-content: center;

              div {
                transform: translateY(-2px);
              }

              .bk-icon {
                font-size: 16px;
              }
            }

            .query-search {
              width: 80px;
              font-size: 12px
            }

            .favorite-btn-container {
              position: relative;

              .favorite-btn {
                width: 86px;
                margin: 0 8px;
                font-size: 12px
              }

              .favorite-btn-text {
                display: flex;
                align-items: center;
                justify-content: center;
              }

              .catching-ball {
                position: absolute;
                width: 12px;
                height: 12px;
                right: 4px;
                top: -6px;
                z-index: 999;
                border-radius: 50%;
                background: #ea3636;
              }

              .icon {
                margin-right: 2px;
                font-size: 12px;
              }

              .bk-icon, {
                margin-top: -4px;
              }

              .icon-save {
                transform: translateY(1px);
              }
            }

            .clear-params-btn {
              position: relative;
              cursor: pointer;

              .icon-brush {
                position: absolute;
                left: 8px;
                top: 8px;
                font-size: 14px;
                color: #63656e;
                pointer-events: none;
              }
            }

            .loading {
              &.bk-primary {
                /* stylelint-disable-next-line declaration-no-important */
                background: #a3c5fd !important;

                /* stylelint-disable-next-line declaration-no-important */
                border-color: #a3c5fd !important;
                color: #fff;
              }
            }

            .loading-box {
              width: 32px;
              height: 32px;
              cursor: pointer;
              border: 1px solid #c4c6cc;
              border-radius: 2px;
              margin-right: 2px;

              .loading {
                transform: scale(.2) translateY(78px);
              }
            }
          }

          .cut-line {
            margin: 0 8px 0 4px;
            width: 1px;
            height: 32px;
            opacity: 1;
            background: #eceef5;
          }
        }
      }

      .retrieve-result {
        position: relative;
        width: calc(100% - 450px);
        height: 100%;
        background: #f5f6fa;
        z-index: 1;
      }

      .drag-bar {
        position: absolute;
        left: 449px;
        top: 52px;
        width: 1px;
        height: 100%;
        background: #dcdee5;

        .drag-icon {
          position: absolute;
          top: 50%;
          left: -3px;
          width: 7px;
          cursor: col-resize;
          transform: translateY(-50%);
          z-index: 50;
        }

        &.dragging {
          z-index: 100;
        }
      }
    }
  }
</style>

<style lang="scss">
  .auto-query-popover-content {
    display: flex;
    align-items: center;
    padding: 6px 0;
    color: #63656e;

    > span {
      margin: 0 12px 0 4px;
    }

    .confirm-btn {
      margin-left: 12px;
      color: #3a84ff;
      cursor: pointer;
    }
  }

  .condition-filter-popper {
    .tippy-tooltip {
      padding: 0;
    }
  }
</style>
