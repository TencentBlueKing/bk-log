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
  <div class="retrieve-container" v-bkloading="{ isLoading: basicLoading }">
    <!-- 初始化加载时显示这个空的盒子 避免先显示内容 再显示无权限页面 -->
    <div v-if="!hasAuth && !authPageInfo && !isNoIndexSet" style="height: 100%;background: #f4f7fa;"></div>
    <!-- 单独的申请权限页面 -->
    <AuthPage
      v-if="!hasAuth && authPageInfo && !isNoIndexSet"
      :info="authPageInfo"
      style="background: #f4f7fa;">
    </AuthPage>
    <!-- 检索页首页 -->
    <div v-if="hasAuth && isRetrieveHome" class="retrieve-home-container">
      <div class="retrieve-home">
        <div class="retrieve-home-title">{{ $t('nav.retrieve') }}</div>
        <div class="retrieve-home-condition">
          <!-- 选择索引集 -->
          <SelectIndexSet
            class="king-select-index-set"
            :index-id="indexId"
            :index-set-list="indexSetList"
            :basic-loading.sync="basicLoading"
            @selected="handleSelectIndex"
            @updateIndexSetList="updateIndexSetList"
          ></SelectIndexSet>
          <!-- 选择日期 -->
          <SelectDate
            :time-range.sync="retrieveParams.time_range"
            :date-picker-value="datePickerValue"
            @update:datePickerValue="handleDateChange"
            @datePickerChange="retrieveWhenDateChange"
          ></SelectDate>
        </div>
        <!-- 首页搜索框 -->
        <RetrieveInput
          v-model="retrieveParams.keyword"
          :show-history.sync="showHistory"
          :history-list="historyList"
          :is-search-allowed="isSearchAllowed"
          @focus="showHistory = true"
          @retrieve="retrieveLog"
        ></RetrieveInput>
      </div>
      <!-- eslint-disable vue/no-v-html -->
      <div v-if="footerHtml" v-html="footerHtml"></div>
      <!--eslint-enable-->
    </div>
    <!-- 检索页详情页 -->
    <div v-if="(hasAuth || isNoIndexSet) && !isRetrieveHome" class="retrieve-detail-container">
      <!-- 检索详情页左侧 -->
      <div v-show="showRetrieveCondition" class="retrieve-condition" :style="{ width: leftPanelWidth + 'px' }">
        <!-- 监控显示的 tab 切换 -->
        <div v-if="asIframe" class="bk-button-group">
          <bk-button @click="handleCheckMonitor">{{ $t('指标检索') }}</bk-button>
          <bk-button class="is-selected">{{ $t('日志检索') }}</bk-button>
          <bk-button @click="handleCheckEvent">{{ $t('事件检索') }}</bk-button>
        </div>

        <div class="king-tab" :class="asIframe && 'as-iframe'">
          <div class="tab-header">{{ $t('数据查询') }}
            <bk-popover
              ref="queryTipPopover"
              placement="bottom"
              theme="light"
              :transfer="true"
              trigger="click">
              <span class="bk-icon icon-cog" @click="toggleCog"></span>
              <div slot="content" class="auto-query-popover-content">
                <span>{{ $t('是否开启自动查询') }}</span>
                <span class="bk-icon icon-info"></span>
                <bk-switcher v-model="isAutoQuery" theme="primary" size="small" @change="switchAutoQuery"></bk-switcher>
                <span class="confirm-btn" v-if="!isHideAutoQueryTips" @click="toggleNotice">{{ $t('知道了') }}</span>
              </div>
            </bk-popover>
          </div>
          <div class="tab-content">
            <div class="tab-content-item">
              <!-- 选择索引集 -->
              <div class="tab-item-title">{{ $t('索引集') }}</div>
              <SelectIndexSet
                :index-id="indexId"
                :index-set-list="indexSetList"
                :basic-loading.sync="basicLoading"
                @selected="handleSelectIndex"
                @updateIndexSetList="updateIndexSetList"
              ></SelectIndexSet>
              <!-- 查询语句 -->
              <QueryStatement></QueryStatement>
              <RetrieveDetailInput
                v-model="retrieveParams.keyword"
                :is-auto-query="isAutoQuery"
                :retrieved-keyword="retrievedKeyword"
                :dropdown-data="retrieveDropdownData"
                :history-records="statementSearchrecords"
                @updateSearchParam="updateSearchParam"
                @retrieve="retrieveLog" />
              <!-- 添加过滤条件 -->
              <div class="tab-item-title flex-item-title">
                <span>{{ $t('过滤条件') }}</span>
                <div class="filter-item">
                  <span v-if="showIpQuick" @click="openIpQuick">{{ $t('添加IP') }}</span>
                  <FilterConditionItem
                    :filter-condition="retrieveParams.addition"
                    :total-fields="totalFields"
                    :field-alias-map="fieldAliasMap"
                    :statistical-fields-data="statisticalFieldsData"
                    @addFilterCondition="addFilterCondition"
                    @removeFilterCondition="removeFilterCondition"
                  ></FilterConditionItem>
                </div>
              </div>
              <div class="add-filter-condition-container">
                <IpQuick
                  v-if="showIpQuick"
                  ref="ipQuick"
                  :host-scopes="retrieveParams.host_scopes"
                  @confirm="handleSaveIpQuick"
                ></IpQuick>
                <div class="cut-line" v-if="showFilterCutline"></div>
                <template v-for="(item, index) in retrieveParams.addition">
                  <FilterConditionItem
                    :key="item.field + 1"
                    :edit-index="index"
                    :is-add="false"
                    :edit-data="item"
                    :filter-condition="retrieveParams.addition"
                    :total-fields="totalFields"
                    :field-alias-map="fieldAliasMap"
                    :statistical-fields-data="statisticalFieldsData"
                    @addFilterCondition="addFilterCondition"
                    @removeFilterCondition="removeFilterCondition"
                  ></FilterConditionItem>
                </template>
              </div>
              <!-- 查询收藏清空按钮 -->
              <div class="retrieve-button-group">
                <bk-button
                  v-if="isAutoQuery"
                  v-cursor="{ active: isSearchAllowed === false }"
                  theme="primary"
                  style="width: 86px;"
                  @click="retrieveLog">
                  <span class="log-icon icon-zidongchaxun" style="margin-right: 4px;font-size: 18px;"></span>
                  {{ $t('查询') }}
                </bk-button>
                <bk-button
                  v-else
                  v-cursor="{ active: isSearchAllowed === false }"
                  theme="primary"
                  style="width: 86px;"
                  icon="search"
                  @click="retrieveLog">
                  {{ $t('查询') }}
                </bk-button>
                <bk-popover
                  ref="favoritePopper"
                  trigger="click"
                  placement="top"
                  theme="light"
                  :on-show="handleFavoritePopperShow">
                  <bk-button style="margin: 0 8px;">
                    <span style="display: flex;align-items: center">
                      <span
                        class="bk-icon icon-star"
                        style="margin-right: 6px;margin-top: -4px;font-size: 16px;">
                      </span>
                      <span>{{ $t('收藏') }}</span>
                    </span>
                  </bk-button>
                  <FavoritePopper
                    v-if="showFavoritePopperContent"
                    :is-loading="favoritePopperLoading"
                    :panel-width="leftPanelWidth"
                    slot="content"
                    @add="addFavorite"
                    @close="closeFavoritePopper"
                  ></FavoritePopper>
                </bk-popover>
                <bk-button @click="clearCondition">{{ $t('清空') }}</bk-button>
              </div>
            </div>
            <div class="tab-content-item">
              <!-- 字段过滤 -->
              <div class="tab-item-title" style="color: #313238;">{{ $t('字段过滤') }}</div>
              <FieldFilter
                :total-fields="totalFields"
                :visible-fields="visibleFields"
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
      <div class="retrieve-result" :style="{ width: 'calc(100% - ' + leftPanelWidth + 'px)' }">
        <ResultHeader
          ref="resultHeader"
          :show-retrieve-condition="showRetrieveCondition"
          :show-expand-init-tips="showExpandInitTips"
          :retrieve-params="retrieveParams"
          :time-range.sync="retrieveParams.time_range"
          :date-picker-value="datePickerValue"
          :favorite-list="favoriteList"
          :latest-favorite-id="latestFavoriteId"
          @remove="removeFavorite"
          @shouldRetrieve="retrieveLog"
          @retrieveFavorite="retrieveFavorite"
          @initTipsHidden="handleInitTipsHidden"
          @open="openRetrieveCondition"
          @update:datePickerValue="handleDateChange"
          @datePickerChange="retrieveWhenDateChange"
        ></ResultHeader>
        <NoIndexSet v-if="isNoIndexSet"></NoIndexSet>
        <ResultMain
          ref="resultMainRef"
          v-else
          :render-table="renderTable"
          :table-loading="tableLoading"
          :retrieve-params="retrieveParams"
          :took-time="tookTime"
          :index-set-list="indexSetList"
          :table-data="tableData"
          :visible-fields="visibleFields"
          :field-alias-map="fieldAliasMap"
          :show-field-alias="showFieldAlias"
          :show-context-log="showContextLog"
          :show-realtime-log="showRealtimeLog"
          :show-web-console="showWebConsole"
          :bk-monitor-url="bkmonitorUrl"
          :async-export-usable="asyncExportUsable"
          :async-export-usable-reason="asyncExportUsableReason"
          @request-table-data="requestTableData"
          @fieldsUpdated="handleFieldsUpdated"
          @shouldRetrieve="retrieveLog"
          @addFilterCondition="addFilterCondition"
        ></ResultMain>
      </div>
      <!-- 可拖拽页面布局宽度 -->
      <div
        v-show="showRetrieveCondition"
        ref="dragBar"
        :class="['drag-bar', isChangingWidth && 'dragging']"
        :style="{ left: leftPanelWidth - 1 + 'px' }">
        <img
          src="../../images/icons/drag-icon.svg"
          alt=""
          draggable="false"
          class="drag-icon"
          @mousedown.left="dragBegin">
      </div>
    </div>
  </div>
</template>

<script>
import SelectIndexSet from './condition-comp/SelectIndexSet';
import SelectDate from './condition-comp/SelectDate';
import RetrieveInput from './condition-comp/RetrieveInput';
import RetrieveDetailInput from './condition-comp/RetrieveDetailInput';
import QueryStatement from './condition-comp/QueryStatement';
import FilterConditionItem from './condition-comp/FilterConditionItem';
import IpQuick from './condition-comp/IpQuick';
import FieldFilter from './condition-comp/FieldFilter';
import FavoritePopper from './condition-comp/FavoritePopper';
import ResultHeader from './result-comp/ResultHeader';
import NoIndexSet from './result-comp/NoIndexSet';
import ResultMain from './result-comp/ResultMain';
import AuthPage from '@/components/common/auth-page';
import { formatDate } from '@/common/util';
import indexSetSearchMixin from '@/mixins/indexSetSearchMixin';
import { mapGetters, mapState } from 'vuex';

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
    FieldFilter,
    FavoritePopper,
    ResultHeader,
    ResultMain,
    AuthPage,
    NoIndexSet,
  },
  mixins: [indexSetSearchMixin],
  data() {
    const currentTime = Date.now();
    const startTime = formatDate(currentTime - 15 * 60 * 1000);
    const endTime = formatDate(currentTime);

    return {
      hasAuth: false,
      authPageInfo: null,
      isSearchAllowed: null, // true 有权限，false 无权限，null 未知权限
      renderTable: true, // 显示字段更新后手动触发重新渲染表格
      basicLoading: false, // view loading
      tableLoading: false, // 表格 loading
      requesting: false,
      isRetrieveHome: !this.$route.params.indexId?.toString() && !this.$route.params.from, // 检索首页
      isNoIndexSet: false,
      showRetrieveCondition: true, // 详情页显示检索左侧条件
      showExpandInitTips: false, // 展开初始tips
      hasExpandInitTipsShown: false,
      activeTab: 'search', // 检索左侧条件 tab - 数据查询：search；收藏记录：record。
      footerHtml: '', // 页脚内容
      isChangingWidth: false, // 拖拽
      leftPanelWidth: 450, // 左栏默认宽度
      leftPanelMinWidth: 300, // 左栏最小宽度
      leftPanelMaxWidth: 750, // 左栏最大宽度
      indexId: '', // 当前选择的索引ID
      indexSetList: [], // 索引集列表,
      datePickerValue: [startTime, endTime], // 日期选择器
      retrievedKeyword: '*', // 记录上一次检索的关键字，避免输入框失焦时重复检索
      retrieveParams: { // 检索参数
        bk_biz_id: this.$store.state.bkBizId,
        keyword: '*', // 搜索关键字
        // 自定义时间范围，10m 表示最近 10 分钟，10h 表示最近 10 小时，10d 表示最近 10 天
        // 当 time_range === 'customized' 时，检索时间范围为 start_time ~ end_time
        time_range: '15m',
        start_time: startTime, // 时间范围，格式 YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
        end_time: endTime, // 时间范围
        // ip 快选，modules 和 ips 只能修改其一，另一个传默认值
        host_scopes: {
          // 拓扑选择模块列表，单个模块格式 {bk_inst_id: 2000003580, bk_obj_id: 'module'}
          modules: [],
          // 手动输入 ip，多个 ip 用英文 , 分隔
          ips: '',
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
      favoriteList: [], // 收藏记录
      latestFavoriteId: '', // 最新添加的收藏历史，高亮显示
      isFavoriteSearch: false,
      favoritePopperLoading: false,
      showFavoritePopperContent: false, // 显示收藏记录按钮浮层
      statisticalFieldsData: {}, // 字段可选值统计
      retrieveDropdownData: {}, // 检索下拉字段可选值统计
      statementSearchrecords: [], // 查询语句历史记录
      ipTopoSwitch: true, // IP快选功能相关
      totalFields: [], // 表格字段
      visibleFields: [], // 显示的排序后的字段
      notTextTypeFields: [], // 字段类型不为 text 的字段
      fieldAliasMap: {},
      showFieldAlias: localStorage.getItem('showFieldAlias') === 'true',
      tookTime: 0, // 耗时
      totalCount: 0, // 结果条数
      tableData: {}, // 表格结果
      showContextLog: false, // 上下文
      showRealtimeLog: false, // 实时日志
      showWebConsole: false, // BCS 容器
      bkmonitorUrl: '', // 监控主机详情地址
      asyncExportUsable: true, // 是否支持异步导出
      asyncExportUsableReason: '', // 无法异步导出原因
      isInitPage: true,
      isAutoQuery: localStorage.getItem('closeAutoQuery') !== 'true',
      isHideAutoQueryTips: localStorage.getItem('hideAutoQueryTips') === 'true',
      showConditionPopperContent: false,
      isPollingStart: false,
      startTimeStamp: 0,
      endTimeStamp: 0,
      originLogList: [], // 当前搜索结果的原始日志
      isNextTime: false,
      timer: null,
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      projectId: state => state.projectId,
      currentMenu: state => state.currentMenu,
      storedIndexID: state => state.indexId, // 路由切换时缓存当前选择的索引
    }),
    ...mapGetters(['asIframe', 'iframeQuery']),
    // 是否显示IP快选功能模块
    showIpQuick() {
      return this.ipTopoSwitch;
    },
    showFilterCutline() {
      const { host_scopes, addition } = this.retrieveParams;
      return (host_scopes.modules.length || host_scopes.ips.length) && addition.length;
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
      // eslint-disable-next-line camelcase
      this.isSearchAllowed = !!option?.permission?.search_log;
      this.resetRetrieveCondition();
      this.$store.commit('updateIndexId', val);
      val && this.requestSearchHistory(val);
    },
    projectId() {
      this.indexId = '';
      this.indexSetList.splice(0);
      this.favoriteList.splice(0);
      this.totalFields.splice(0);
      this.retrieveParams.bk_biz_id = this.bkBizId;
      this.fetchPageData();
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
    'retrieveParams.keyword'() {
      if (!this.isFavoriteSearch) this.latestFavoriteId = '';
    },
    'retrieveParams.host_scopes.ips': {
      deep: true,
      handler() {
        if (!this.isFavoriteSearch) this.latestFavoriteId = '';
      },
    },
    'retrieveParams.host_scopes.modules': {
      deep: true,
      handler() {
        if (!this.isFavoriteSearch) this.latestFavoriteId = '';
      },
    },
    'retrieveParams.addition': {
      deep: true,
      handler() {
        if (!this.isFavoriteSearch) this.latestFavoriteId = '';
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
    this.fetchPageData();
  },
  mounted() {
    if (!this.isHideAutoQueryTips) {
      this.checkAutoQueryTips();
    }
    window.bus.$on('retrieveWhenChartChange', this.retrieveWhenChartChange);
  },
  beforeDestroy() {
    window.bus.$off('retrieveWhenChartChange', this.retrieveWhenChartChange);
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
    switchAutoQuery(data) {
      localStorage.setItem('closeAutoQuery', !data);
      if (!this.isHideAutoQueryTips) {
        localStorage.setItem('hideAutoQueryTips', true);
        this.isHideAutoQueryTips = true;
      }
    },
    // 切换到监控指标检索
    handleCheckMonitor() {
      window.parent.postMessage('datarieval-click', '*');
    },
    // 切换到监控事件检索
    handleCheckEvent() {
      window.parent.postMessage('event-click', '*');
    },
    fetchPageData() {
      if (this.projectId) {
        this.requestIndexSetList();
      }
    },

    updateIndexSetList() {
      this.$http.request('retrieve/getIndexSetList', {
        query: {
          project_id: this.projectId,
        },
      }).then((res) => {
        if (res.data.length) { // 有索引集
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            // eslint-disable-next-line camelcase
            if (item.permission?.search_log) {
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
      this.basicLoading = true;
      this.$http.request('retrieve/getIndexSetList', {
        query: {
          project_id: this.projectId,
        },
      }).then((res) => {
        if (res.data.length) { // 有索引集
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            // eslint-disable-next-line camelcase
            if (item.permission?.search_log) {
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

          // 如果都没有权限直接显示页面无权限
          // eslint-disable-next-line camelcase
          if (!this.indexSetList[0]?.permission?.search_log) {
            this.$store.dispatch('getApplyData', {
              action_ids: ['search_log'],
              resources: [],
            }).then((res) => {
              this.authPageInfo = res.data;
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


          const indexId = this.$route.params.indexId?.toString();
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
            if (this.asIframe) { // 监控 iframe
              if (this.iframeQuery.indexId) {
                if (this.indexSetList.some(item => item.index_set_id === this.iframeQuery.indexId)) {
                  this.indexId = this.iframeQuery.indexId;
                }
              }
              this.retrieveLog();
            } else {
              const queryObj = {
                projectId: window.localStorage.getItem('project_id'),
                bizId: window.localStorage.getItem('bk_biz_id'),
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
          this.requestFavoriteList();
        } else { // 无索引集
          this.isRetrieveHome = false;
          this.isNoIndexSet = true;
          const queryObj = {
            projectId: window.localStorage.getItem('project_id'),
            bizId: window.localStorage.getItem('bk_biz_id'),
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
    // 切换索引
    handleSelectIndex(val) {
      this.indexId = val;
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
      this.originLogList = [];
      // 字段相关
      this.totalFields.splice(0);
    },

    // 检索参数：日期改变
    handleDateChange(val) {
      this.datePickerValue = val;
      Object.assign(this.retrieveParams, {
        start_time: val[0],
        end_time: val[1],
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

    // 添加过滤条件
    addFilterCondition(field, operator, value, index) {
      const startIndex = index > -1 ? index : this.retrieveParams.addition.length;
      const deleteCount = index > -1 ? 1 : 0;
      this.retrieveParams.addition.splice(startIndex, deleteCount, { field, operator, value });
      if (this.isAutoQuery) {
        this.retrieveLog();
      }
    },
    removeFilterCondition(field) {
      const index = this.retrieveParams.addition.findIndex(item => item.field === field);
      this.retrieveParams.addition.splice(index, 1);
      this.retrieveLog();
    },

    // 打开 ip 快选弹窗
    openIpQuick() {
      this.$refs.ipQuick.openDialog();
    },

    // IP 快选
    handleSaveIpQuick(data) {
      this.retrieveParams.host_scopes = data;
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
        },
        addition: [],
      });
      this.retrieveLog();
    },

    // 收藏记录，和业务相关
    requestFavoriteList(isAddLater = false) {
      this.$http.request('retrieve/getRetrieveFavorite', {
        query: {
          project_id: this.projectId,
        },
      }).then((res) => {
        this.favoriteList = res.data;
        if (isAddLater) { // 新增后需标记最新的高亮显示
          this.latestFavoriteId = this.favoriteList[0] && this.favoriteList[0].favorite_search_id;
        }
      })
        .catch((e) => {
          console.warn(e);
          this.favoriteList.splice(0);
        });
    },
    // 搜索记录
    retrieveFavorite({ indexId, params, id }) {
      this.isFavoriteSearch = true;
      if (this.indexSetList.find(item => item.index_set_id === indexId)) {
        this.indexId = indexId;
        this.latestFavoriteId = id;
        this.retrieveLog(params);
      } else {
        this.messageError(this.$t('没有找到该记录下相关索引集'));
      }
    },
    // 删除收藏记录
    removeFavorite(id) {
      this.$bkInfo({
        title: `${this.$t('确定要删除')}？`,
        confirmFn: () => {
          this.$http.request('retrieve/deleteRetrieveFavorite', {
            params: { id },
          }).then(() => {
            const index = this.favoriteList.findIndex(item => item.favorite_search_id === id);
            this.favoriteList.splice(index, 1);
            this.messageSuccess(this.$t('删除成功'));
          })
            .catch((e) => {
              console.warn(e);
            });
        },
      });
    },
    handleFavoritePopperShow() {
      this.showFavoritePopperContent = false;
      this.$nextTick(() => {
        this.showFavoritePopperContent = true;
      });
    },
    handleConditionPopperShow() {
      this.showConditionPopperContent = false;
      this.$nextTick(() => {
        this.showConditionPopperContent = true;
      });
    },
    handleConditionPopperHide() {
      this.showConditionPopperContent = false;
    },
    // 添加收藏记录
    addFavorite(description) {
      this.favoritePopperLoading = true;
      this.$http.request('retrieve/postRetrieveFavorite', {
        data: {
          index_set_id: this.indexId,
          project_id: this.projectId,
          description,
          keyword: this.retrieveParams.keyword.trim(),
          host_scopes: this.retrieveParams.host_scopes,
          addition: this.retrieveParams.addition,
        },
      }).then(() => {
        this.requestFavoriteList(true);
        this.closeFavoritePopper();
      })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.favoritePopperLoading = false;
        });
    },
    // 关闭收藏浮层
    closeFavoritePopper() {
      this.$refs.favoritePopper.instance.hide();
    },

    // 检索日志
    async retrieveLog(historyParams) {
      if (!this.indexId) {
        return;
      }
      await this.$nextTick();
      this.showHistory = false;
      this.activeTab = 'search';
      this.$refs.resultHeader && this.$refs.resultHeader.pauseRefresh();

      // 是否有检索的权限
      const paramData = {
        action_ids: ['search_log'],
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
        if (!this.showIpQuick) {
          this.retrieveParams.host_scopes.ips = '';
        }
      }
      // 通过 url 查询参数设置检索参数
      let queryParams = {};
      const queryParamsStr = {};
      const urlRetrieveParams = this.$route.query.retrieveParams;
      if (urlRetrieveParams) {
        try {
          queryParams = JSON.parse(decodeURIComponent(urlRetrieveParams));
        } catch (e) {
          console.warn('url 查询参数解析失败', e);
        }
      } else { // 兼容之前的语法
        // const shouldCoverParamFields = ['keyword', 'host_scopes', 'addition']
        // for (const field of shouldCoverParamFields) {
        //     const param = this.$route.query[field] // 指定查询参数
        //     if (param) {
        //         queryParams[field] = field === 'keyword'
        //             ? decodeURIComponent(param)
        //             : JSON.parse(decodeURIComponent(param))
        //     }
        // }

        const shouldCoverParamFields = ['keyword', 'host_scopes', 'addition', 'start_time', 'end_time', 'time_range'];
        for (const field of shouldCoverParamFields) {
          if (this.isInitPage) {
            const param = this.$route.query[field]; // 指定查询参数
            if (param) {
              queryParams[field] = ['keyword', 'start_time', 'end_time', 'time_range'].includes(field)
                ? decodeURIComponent(param)
                : JSON.parse(decodeURIComponent(param));

              queryParamsStr[field] = param;
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
                if (this.retrieveParams[field].ips !== '' || this.retrieveParams[field].modules.length) {
                  queryParamsStr[field] = (JSON.stringify(this.retrieveParams[field]));
                }
                break;
              default:
                break;
            }
          }
        }
      }
      // 进入检索详情页
      this.isRetrieveHome = false;
      const queryObj = {
        projectId: window.localStorage.getItem('project_id'),
        bizId: window.localStorage.getItem('bk_biz_id'),
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
          this.isInitPage = false;
        }

        this.retrieveParams.keyword = this.retrieveParams.keyword.trim();
        this.requestChart();

        await this.handleResetTimer();
        await this.requestTable();
        this.requestSearchHistory(this.indexId);
      } catch (e) {
        console.warn(e);
        if (!e.message.includes('request canceled')) { // 接口出错、非重复请求被取消
          this.tableLoading = false;
        }
      } finally {
        // 搜索完毕后，如果开启了自动刷新，会在 timeout 后自动刷新
        this.$refs.resultHeader && this.$refs.resultHeader.setRefreshTime();
        this.isFavoriteSearch = false;
      }
    },

    // 请求字段
    async requestFields() {
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
        res.data.fields.forEach((item) => {
          item.minWidth = 0;
          item.filterExpand = false; // 字段过滤展开
          item.filterVisible = true; // 字段过滤搜索字段名是否显示
          if (item.field_type !== 'text') {
            notTextTypeFields.push(item.field_name);
          }
        });
        this.notTextTypeFields = notTextTypeFields;

        // 如果没有 ip_topo_switch 字段默认给 true，如果有该字段根据该字段控制
        this.ipTopoSwitch = res.data.ip_topo_switch === undefined || res.data.ip_topo_switch;
        this.showContextLog = res.data.context_search_usable;
        this.showRealtimeLog = res.data.realtime_search_usable;
        this.showWebConsole = res.data.bcs_web_console_usable === true;
        this.bkmonitorUrl = res.data.bkmonitor_url;
        this.asyncExportUsable = res.data.async_export_usable;
        this.asyncExportUsableReason = res.data.async_export_usable_reason;

        this.totalFields = res.data.fields;
        // 后台给的 display_fields 可能有无效字段 所以进行过滤，获得排序后的字段
        this.visibleFields = res.data.display_fields.map((displayName) => {
          for (const field of res.data.fields) {
            if (field.field_name === displayName) {
              return field;
            }
          }
        }).filter(Boolean);

        const fieldAliasMap = {};
        res.data.fields.forEach((item) => {
          fieldAliasMap[item.field_name] = item.field_alias || item.field_name;
        });
        this.fieldAliasMap = fieldAliasMap;
      } catch (e) {
        this.ipTopoSwitch = true;
        this.showContextLog = false;
        this.showRealtimeLog = false;
        this.showWebConsole = false;
        this.bkmonitorUrl = '';
        this.asyncExportUsable = true;
        this.asyncExportUsableReason = '';
        this.totalFields.splice(0);
        this.visibleFields.splice(0);
        throw e;
      }
    },
    // 字段设置更新了
    async handleFieldsUpdated(displayFieldNames, showFieldAlias) {
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
        const res = await this.$http.request('retrieve/getLogTableList', {
          params: { index_set_id: this.indexId },
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
        });

        this.isNextTime = res.data.list.length < pageSize;
        if (this.isNextTime && (this.pollingStartTime <= this.startTimeStamp
        || this.requestInterval === 0)) { // 分片时间已结束
          this.finishPolling = true;
        }

        this.retrievedKeyword = this.retrieveParams.keyword;
        this.tookTime = this.tookTime + res.data.took || 0;
        this.tableData = { ...res.data, finishPolling: this.finishPolling };
        this.originLogList = this.originLogList.concat(res.data.origin_log_list);
        this.statisticalFieldsData = this.getStatisticalFieldsData(this.originLogList);
        this.computeRetrieveDropdownData(this.originLogList);
      } catch (err) {
        this.$refs.resultMainRef.isPageOver = false;
      } finally {
        this.tableLoading = false;
        this.requesting = false;
        if (this.isNextTime) {
          if (this.finishPolling) { // 已请求所有分片时间仍无结果
            this.$refs.resultMainRef.isPageOver = false;
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
        await this.requestFields();
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
      this.originLogList = [];
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
      window.bus.$emit('set-chart-width');
    },
    dragStop() {
      this.isChangingWidth = false;
      this.currentTreeBoxWidth = null;
      this.currentScreenX = null;
      window.removeEventListener('mousemove', this.dragMoving);
      window.removeEventListener('mouseup', this.dragStop);
    },
    openRetrieveCondition() {
      window.bus.$emit('set-chart-width');
      this.leftPanelWidth = this.leftPanelMinWidth;
      this.showRetrieveCondition = true;
    },
    // 初始 tips 消失后显示普通的 tips
    handleInitTipsHidden() {
      this.hasExpandInitTipsShown = true;
      this.showExpandInitTips = false;
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

    /*详情页*/
    .retrieve-detail-container {
      position: relative;
      display: flex;
      height: 100%;

      .retrieve-condition {
        display: flow-root;
        width: 450px;
        height: 100%;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
        background: #fff;

        .bk-button-group {
          display: flex;
          width: 100%;
          height: 52px;

          .bk-button {
            flex:1;
            height: 100%;
            background: #fafbfd;

            &.is-selected{
              background: #ffffff;
              border-top: none;
              border-bottom: none;
            }
          }
        }

        .king-tab {
          // height: 100%;
          // padding-top: 10px;
          // &.as-iframe {
          //     height: calc(100% - 48px);
          // }
          // /deep/ .bk-tab-label-list {
          //     width: 100%;
          //     .bk-tab-label-item {
          //         width: 50%;
          //         &:after {
          //             left: 36px;
          //             width: calc(100% - 72px);
          //         }
          //     }
          // }
          // /deep/ .bk-tab-section {
          //     padding: 0;
          //     height: calc(100% - 42px);
          //     .bk-tab-content {
          //         height: 100%;
          //         overflow-y: auto;
          //         @include scroller;
          //     }
          // }
          // /deep/ .data-search {
          //     position: relative;
          //     padding: 0 20px 0;
          //     overflow-y: auto;
          //     @include scroller;
          //     .tab-item-title {
          //         display: flex;
          //         align-items: center;
          //         margin: 15px 0 6px;
          //         line-height: 20px;
          //         font-size: 12px;
          //         color: #63656E;
          //         &.ip-quick-title {
          //             margin-top: 13px;
          //         }
          //     }
          //     .add-filter-condition-container {
          //         display: flex;
          //         flex-wrap: wrap;
          //     }
          //     .retrieve-button-group {
          //         position: sticky;
          //         bottom: 0;
          //         display: flex;
          //         align-items: center;
          //         padding: 16px 0 20px;
          //         background-color: #FFF;
          //         z-index: 1;
          //     }
          // }

          height: 100%;
          padding-top: 10px;

          .tab-content {
            height: calc(100% - 50px);
            // padding: 0 24px;
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
            }
          }

          &.as-iframe {
            height: calc(100% - 48px);
          }

          .tab-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 24px 12px;
            color: #313238;
            font-size: 14px;
            border-bottom: 1px solid #cacedb;

            .icon-cog {
              font-size: 18px;
              color: #979ba5;
              cursor: pointer;
            }
          }

          .tab-item-title {
            display: flex;
            align-items: center;
            margin: 0 0 6px;
            padding-top: 15px;
            line-height: 20px;
            font-size: 12px;
            color: #63656e;

            &.ip-quick-title {
              margin-top: 13px;
            }
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
            padding: 16px 0 20px;
            background-color: #fff;
            // z-index: 1;
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
        top: 0;
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
        }

        &.dragging {
          z-index: 3001;
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

    .bk-icon {
      margin: 0 12px 0 4px;
      color: #979ba5;
      font-size: 14px;
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
