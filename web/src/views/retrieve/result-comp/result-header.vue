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
  <div class="result-header">
    <!-- 检索左侧 -->
    <div class="result-left">
      <div class="icon-container">
        <bk-popover
          ref="showFavoriteBtnRef"
          :disabled="showCollectIntroGuide"
          :tippy-options="expandTips">
          <div
            :class="[
              'result-icon-box',
              {
                'light-icon': !isShowCollect,
                'disabled': showCollectIntroGuide
              }
            ]"
            @click="handleClickResultIcon('collect')">
            <span class="bk-icon icon-star"></span>
          </div>
          <div slot="content">
            {{`${isShowCollect ? $t('点击收起') : $t('点击展开')}${$t('收藏')}`}}
          </div>
        </bk-popover>
        <bk-popover
          ref="showSearchBtnRef"
          :tippy-options="collectTips">
          <div
            :class="['result-icon-box',{ 'light-icon': !showRetrieveCondition }]"
            @click="handleClickResultIcon('search')">
            <span class="bk-icon log-icon icon-jiansuo"></span>
          </div>
          <div slot="content">
            {{`${showRetrieveCondition ? $t('点击收起') : $t('点击展开')}${$t('检索')}`}}
          </div>
        </bk-popover>
      </div>
      <div class="biz-menu-box" id="bizSelectorGuide" v-if="!isAsIframe">
        <biz-menu-select theme="light"></biz-menu-select>
      </div>
    </div>
    <!-- 检索结果 -->
    <!-- <div class="result-text"></div> -->
    <!-- 检索日期 -->
    <div class="result-right">
      <time-range :value="datePickerValue" @change="handleTimeRangeChange" />
      <!-- 自动刷新 -->
      <bk-popover
        ref="autoRefreshPopper"
        trigger="click"
        placement="bottom-start"
        theme="light bk-select-dropdown"
        animation="slide-toggle"
        :offset="0"
        :distance="15"
        :on-show="handleDropdownShow"
        :on-hide="handleDropdownHide">
        <slot name="trigger">
          <div class="auto-refresh-trigger">
            <span
              :class="['log-icon', isAutoRefresh ? 'icon-auto-refresh' : 'icon-refresh-icon']"
              data-test-id="retrieve_span_periodicRefresh"
              @click.stop="$emit('shouldRetrieve')"></span>
            <span :class="isAutoRefresh && 'active-text'">{{refreshTimeText}}</span>
            <span class="bk-icon icon-angle-down" :class="refreshActive && 'active'"></span>
          </div>
        </slot>
        <div slot="content" class="bk-select-dropdown-content auto-refresh-content">
          <div class="bk-options-wrapper">
            <ul class="bk-options bk-options-single">
              <li v-for="item in refreshTimeList"
                  :key="item.id"
                  :class="['bk-option', refreshTimeout === item.id && 'is-selected']"
                  @click="handleSelectRefreshTimeout(item.id)">
                <div class="bk-option-content">{{item.name}}</div>
              </li>
            </ul>
          </div>
        </div>
      </bk-popover>
      <bk-popover
        v-if="isAiopsToggle"
        trigger="click"
        placement="bottom-end"
        theme="light bk-select-dropdown"
        animation="slide-toggle"
        :offset="0"
        :distance="11">
        <slot name="trigger">
          <div class="more-operation">
            <i class="bk-icon log-icon icon-more"></i>
          </div>
        </slot>
        <div slot="content" class="retrieve-setting-container">
          <ul class="list-menu" ref="menu">
            <li
              v-for="menu in showSettingMenuList"
              class="list-menu-item"
              :key="menu.id"
              @click="handleMenuClick(menu.id)">
              {{ menu.name }}
            </li>
          </ul>
        </div>
      </bk-popover>
    </div>
    <step-box
      v-if="showCollectIntroGuide"
      placement="bottom"
      :has-border="true"
      :tip-styles="{
        top: '50px',
        left: '14px',
      }"
    >
      <div slot="title">{{ $t('检索收藏功能支持分组和管理') }}</div>
      <template slot="action">
        <div class="action-text" @click="handleCloseGuide">{{ $t('知道了') }}</div>
      </template>
    </step-box>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import BizMenuSelect from '@/components/biz-menu';
import TimeRange from '../../../components/time-range/time-range';
import StepBox from '@/components/step-box';

export default {
  components: {
    BizMenuSelect,
    TimeRange,
    StepBox,
  },
  props: {
    showRetrieveCondition: {
      type: Boolean,
      required: true,
    },
    showExpandInitTips: {
      type: Boolean,
      required: true,
    },
    retrieveParams: {
      type: Object,
      required: true,
    },
    timeRange: {
      type: String,
      required: true,
    },
    datePickerValue: {
      type: Array,
      required: true,
    },
    latestFavoriteId: {
      type: [Number, String],
      default: '',
    },
    indexSetItem: {
      type: Object,
      required: true,
    },
    isAsIframe: {
      type: Boolean,
      required: true,
    },
    isShowCollect: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      expandTips: {
        placement: 'bottom',
        trigger: 'mouseenter',
        onHidden: () => {
          this.$emit('initTipsHidden');
        },
      },
      expandText: '',
      collectTips: {
        placement: 'bottom',
        trigger: 'mouseenter',
        onHidden: () => {
          this.isFirstCloseCollect = true;
        },
      },
      refreshActive: false, // 自动刷新下拉激活
      refreshTimer: null, // 自动刷新定时器
      refreshTimeout: 0, // 0 这里表示关闭自动刷新
      refreshTimeList: [{
        id: 0, name: this.$t('dataManage.Refresh'),
      }, {
        id: 60000, name: '1m',
      }, {
        id: 300000, name: '5m',
      }, {
        id: 900000, name: '15m',
      }, {
        id: 1800000, name: '30m',
      }, {
        id: 3600000, name: '1h',
      }, {
        id: 7200000, name: '2h',
      }, {
        id: 86400000, name: '1d',
      }],
      settingMenuList: [
        // { id: 'index', name: '全文索引' },
        { id: 'extract', name: this.$t('字段清洗') },
        { id: 'clustering', name: this.$t('日志聚类') },
      ],
      accessList: {
        baseInfo: this.$t('配置信息'),
        dataStorage: this.$t('数据存储'),
        usageDetails: this.$t('使用详情'),
        dataStatus: this.$t('数据状态'),
        fieldInfo: this.$t('字段信息'),
        collectionStatus: this.$t('采集状态'),
      },
      routeNameList: { // 路由跳转name
        log: 'manage-collection',
        custom: 'custom-report-detail',
        manage: 'bkdata-index-set-manage',
        indexManage: 'log-index-set-manage',
      },
      logDetailKey: ['baseInfo', 'collectionStatus', 'dataStorage', 'dataStatus', 'usageDetails'], // 日志采集li列表
      bkdataDetailKey: ['baseInfo', 'usageDetails', 'fieldInfo'], // 计算平台 li列表
      esDetailKey: ['baseInfo', 'usageDetails', 'fieldInfo'], // 第三方ES li列表
      setIndexDetailKey: ['baseInfo', 'usageDetails', 'fieldInfo'], // 索引集li列表
      customDetailKey: ['baseInfo', 'dataStorage', 'dataStatus', 'usageDetails'], // 自定义上报li列表
      detailJumpRouteKey: 'log', // 路由key log采集列表 custom自定义上报 es、bkdata、setIndex 第三方ED or 计算平台 or 索引集
      isFirstCloseCollect: false,
      showSettingMenuList: [],
      showCollectIntroGuide: false,
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
      userGuideData: state => state.userGuideData,
    }),
    refreshTimeText() {
      return this.refreshTimeList.find(item => item.id === this.refreshTimeout).name;
    },
    isAutoRefresh() {
      return this.refreshTimeout !== 0;
    },
    isAiopsToggle() { // 日志聚类总开关
      if (window.FEATURE_TOGGLE.bkdata_aiops_toggle !== 'on') return false;
      const aiopsBizList = window.FEATURE_TOGGLE_WHITE_LIST?.bkdata_aiops_toggle;

      return aiopsBizList ? aiopsBizList.some(item => item.toString() === this.bkBizId) : false;
    },
  },
  watch: {
    indexSetItem: {
      immediate: true,
      handler(val) {
        this.setShowLiList(val);
      },
    },
  },
  created() {
    this.showCollectIntroGuide = this.userGuideData?.function_guide?.search_favorite ?? false;
  },
  mounted() {
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
    window.bus.$on('changeTimeByChart', this.handleChangeTimeByChart);
  },
  beforeDestroy() {
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    window.bus.$off('changeTimeByChart', this.handleChangeTimeByChart);
  },
  methods: {
    removeFavorite(id) {
      this.$emit('remove', id);
    },
    // retrieveFavorite(data) {
    //   this.$emit('retrieveFavorite', data);
    // },
    // 日期变化
    handleTimeRangeChange(val) {
      this.$emit('update:datePickerValue', val);
      this.setRefreshTime(0);
      this.$emit('datePickerChange');
    },
    handleChangeTimeByChart(val) {
      this.handleTimeRangeChange(val);
      window.bus.$emit('retrieveWhenChartChange');
    },
    // 自动刷新
    handleDropdownShow() {
      this.refreshActive = true;
    },
    handleDropdownHide() {
      this.refreshActive = false;
    },
    handleSelectRefreshTimeout(timeout) {
      this.setRefreshTime(timeout);
      this.$refs.autoRefreshPopper.instance.hide();
    },
    // 清除定时器，供父组件调用
    pauseRefresh() {
      clearTimeout(this.refreshTimer);
    },
    // 如果没有参数就是检索后恢复自动刷新
    setRefreshTime(timeout = this.refreshTimeout) {
      clearTimeout(this.refreshTimer);
      this.refreshTimeout = timeout;
      if (timeout) {
        this.refreshTimer = setTimeout(() => {
          this.$emit('shouldRetrieve');
        }, timeout);
      }
    },
    handleVisibilityChange() { // 窗口隐藏时取消轮询，恢复时恢复轮询（原来是自动刷新就恢复自动刷新，原来不刷新就不会刷新）
      document.hidden ? clearTimeout(this.refreshTimer) : this.setRefreshTime();
    },
    handleMenuClick(val) {
      // 不属于新开页面的操作
      if (['index', 'extract', 'clustering'].includes(val)) {
        this.$emit('settingMenuClick', val);
        return;
      };
      const params = {};
      if (['manage', 'indexManage'].includes(this.detailJumpRouteKey)) {
        params.indexSetId = this.indexSetItem?.index_set_id;
      } else {
        params.collectorId = this.indexSetItem?.collector_config_id;
      }
      const { href } = this.$router.resolve({
        name: this.routeNameList[this.detailJumpRouteKey],
        params,
        query: {
          type: val,
          spaceUid: this.$store.state.spaceUid,
          backRoute: 'retrieve',
        },
      });
      window.open(href, '_blank');
    },
    setShowLiList(setItem) {
      if (JSON.stringify(setItem) === '{}') return;
      if (setItem.scenario_id === 'log') { // 索引集类型为采集项或自定义上报
        if (setItem.collector_scenario_id === null) { // 若无日志类型 则类型为索引集
          this.initJumpRouteList('setIndex');
          return;
        }
        // 判断是否是自定义上报类型
        this.initJumpRouteList(setItem.collector_scenario_id === 'custom' ? 'custom' : 'log');
        return;
      }
      // 当scenario_id不为log（采集项，索引集，自定义上报）时，不显示字段设置
      this.initJumpRouteList(setItem.scenario_id, true);
    },
    /**
     * @desc: 初始化选择列表
     * @param {String} detailStr 当前索引集类型
     * @param {Boolean} isFilterExtract 是否过滤字段设置
     */
    initJumpRouteList(detailStr, isFilterExtract = false) {
      if (!['log', 'es', 'bkdata', 'custom', 'setIndex'].includes(detailStr)) {
        this.showSettingMenuList = this.settingMenuList;
        return;
      };
      if (['es', 'bkdata'].includes(detailStr)) {
        this.detailJumpRouteKey = 'manage';
      } else if (detailStr === 'setIndex') {
        this.detailJumpRouteKey = 'indexManage';
      } else {
        this.detailJumpRouteKey = detailStr;
      }
      this.showSettingMenuList = this.settingMenuList.filter(item => (isFilterExtract ? item.id !== 'extract' : true));
      const extraRouteList = this[`${detailStr}DetailKey`].reduce((pre, cur) => {
        pre.push({
          id: cur,
          name: this.accessList[cur],
        });
        return pre;
      }, []);
      this.showSettingMenuList = this.showSettingMenuList.concat(extraRouteList);
    },
    handleClickResultIcon(type) {
      if (type === 'collect') {
        this.$emit('updateCollectCondition', !this.isShowCollect);
      } else {
        this.showRetrieveCondition ? this.$emit('closeRetrieveCondition') : this.$emit('open');
      }
    },
    handleCloseGuide() {
      this.$http.request('meta/updateUserGuide', {
        data: { function_guide: 'search_favorite' },
      })
        .then(() => {
          this.showCollectIntroGuide = false;
          this.updateUserGuide();
        })
        .catch((e) => {
          console.warn(e);
        });
    },
    /** 更新用户指引 */
    updateUserGuide() {
      this.$http.request('meta/getUserGuide').then((res) => {
        this.$store.commit('setUserGuideData', res.data);
      });
    },
  },
};
</script>

<style lang="scss">
  .result-header {
    display: flex;
    justify-content: space-between;
    // align-items: center;
    width: 100%;
    height: 48px;
    color: #63656e;
    background: #fff;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
    font-size: 12px;
    position: relative;

    &:after {
      position: absolute;
      bottom: 0;
      width: 100%;
      height: 4px;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
      content: '';
      z-index: 1000;
    }

    .result-left {
      display: flex;
      align-items: center;

      .icon-container {
        position: relative;
        margin: 17px 25px 17px 14px;
        background: #f0f1f5;
        border-radius: 2px;
        display: flex;

        > :first-child {
          margin-right: 2px;
        }

        &::after {
          content: '';
          width: 1px;
          height: 14px;
          background-color: #dcdee5;
          position: absolute;
          right: -25px;
          top: 6px;
        }

        .result-icon-box {
          width: 32px;
          height: 24px;
          line-height: 20px;
          text-align: center;
          font-size: 14px;
          color: #fff;
          background: #699df4;
          border-radius: 2px;
          cursor: pointer;

          &.light-icon {
            background: #f0f1f5;
            color: #63656e;
          }

          .icon-jiansuo {
            display: inline-block;
            transform: translateY(2px);
            font-size: 18px;
          }

          &.disabled {
            cursor: not-allowed;

            /* stylelint-disable-next-line declaration-no-important */
            pointer-events: none !important;
          }

          &.light-icon:hover {
            background: #dcdee5;
          }
        }
      }

      .biz-menu-box {
        position: relative;
      }
    }

    .result-right {
      display: flex;
      align-items: center;
    }

    .open-condition {
      flex-shrink: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 49px;
      height: 100%;
      border-right: 1px solid #f0f1f5;
      font-size: 24px;
      cursor: pointer;
      color: #979ba5;

      &:hover {
        color: #3a84ff;
      }
    }

    .result-text {
      width: 100%;
    }

    .time-range-wrap {
      display: flex;
      align-items: center;
      position: relative;

      &::before {
        content: '';
        width: 1px;
        height: 14px;
        background-color: #dcdee5;
        position: absolute;
        left: 0;
        top: 8px;
      }
    }

    .auto-refresh-trigger {
      display: flex;
      align-items: center;
      height: 52px;
      white-space: nowrap;
      line-height: 22px;
      cursor: pointer;

      .log-icon {
        padding: 0 5px 0 17px;
        font-size: 14px;
        color: #63656e;;
      }

      .active-text {
        color: #3a84ff;
      }

      .icon-angle-down {
        margin: 0 10px;
        font-size: 22px;
        color: #63656e;
        transition: transform .3s;

        &.active {
          transform: rotate(-180deg);
          transition: transform .3s;
        }
      }

      &:hover > span {
        color: #3a84ff;
      }

      &::before {
        content: '';
        width: 1px;
        height: 14px;
        background-color: #dcdee5;
        position: absolute;
        left: 0;
        top: 20px;
      }
    }

    .more-operation {
      display: flex;
      align-items: center;
      padding: 0 16px 0 12px;
      height: 52px;
      white-space: nowrap;
      line-height: 22px;
      cursor: pointer;

      .icon-more {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 30px;
        height: 30px;
        overflow: hidden;
        font-size: 18px;

        &:hover {
          color: #0083ff;
          cursor: pointer;
          border-radius: 2px;
          background-color: #e1ecff;
        }
      }

      &::before {
        content: '';
        width: 1px;
        height: 14px;
        background-color: #dcdee5;
        position: absolute;
        left: 0;
        top: 20px;
      }
    }

    .step-box {
      min-height: 60px;
      z-index: 1001;

      .target-arrow {
        /* stylelint-disable-next-line declaration-no-important */
        top: -5px !important;

        /* stylelint-disable-next-line declaration-no-important */
        left: 10px !important;
        border-top: 1px solid #dcdee5;
        border-left: 1px solid #dcdee5;
      }
    }
  }

  .auto-refresh-content {
    width: 84px;

    .bk-options .bk-option-content {
      padding: 0 13px;
    }
  }

  .retrieve-setting-container {
    .list-menu {
      display: flex;
      flex-direction: column;
      padding: 6px 0;
      background-color: white;
      color: #63656e;

      &-item {
        display: flex;
        align-items: center;
        padding: 0 10px;
        height: 32px;
        min-width: 150px;

        &:hover {
          cursor: pointer;
          background-color: #eaf3ff;
          color: #3a84ff;
        }
      }
    }
  }
</style>
