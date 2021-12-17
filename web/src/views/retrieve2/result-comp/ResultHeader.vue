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
    <!-- 重新展开 -->
    <template v-if="!showRetrieveCondition">
      <div
        v-if="showExpandInitTips"
        key="1"
        v-bk-tooltips="expandInitTips"
        class="open-condition"
        @click="$emit('open')">
        <span class="bk-icon icon-angle-double-right"></span>
      </div>
      <div v-else v-bk-tooltips="expandTips" key="2" class="open-condition" @click="$emit('open')">
        <span class="bk-icon icon-angle-double-right"></span>
      </div>
    </template>
    <!-- 收藏查询 -->
    <favorite-card
      :favorite-list="favoriteList"
      :latest-favorite-id="latestFavoriteId"
      @remove="removeFavorite"
      @shouldRetrieve="retrieveFavorite"
    ></favorite-card>
    <!-- 检索结果 -->
    <!-- <div class="result-text"></div> -->
    <!-- 检索日期 -->
    <SelectDate
      :is-home="false"
      :time-range="timeRange"
      :date-picker-value="datePickerValue"
      @update:timeRange="handleTimeRangeChange"
      @update:datePickerValue="handleDateChange"
      @datePickerChange="$emit('datePickerChange')"
    ></SelectDate>
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
      :distance="15">
      <slot name="trigger">
        <div class="more-operation">
          <i class="bk-icon icon-more"></i>
        </div>
      </slot>
      <div slot="content" class="retrieve-setting-container">
        <ul class="list-menu" ref="menu">
          <li
            v-for="menu in settingMenuList"
            class="list-menu-item"
            :key="menu.id"
            @click="handleMenuClick(menu.id)">
            {{ menu.name }}
          </li>
        </ul>
      </div>
    </bk-popover>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import SelectDate from '../condition-comp/SelectDate';
import FavoriteCard from '../condition-comp/FavoriteCard';

export default {
  components: {
    SelectDate,
    FavoriteCard,
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
    favoriteList: {
      type: Array,
      required: true,
    },
    latestFavoriteId: {
      type: [Number, String],
      default: '',
    },
  },
  data() {
    return {
      expandInitTips: {
        content: this.$t('点击重新展开'),
        trigger: 'click',
        showOnInit: true,
        placement: 'bottom',
        onHidden: () => {
          this.$emit('initTipsHidden');
        },
      },
      expandTips: {
        content: this.$t('点击重新展开'),
        placement: 'bottom',
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
        { id: 'extract', name: '字段提取' },
        { id: 'clustering', name: '日志聚类' },
      ],
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
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
  mounted() {
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
  },
  beforeDestroy() {
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },
  methods: {
    removeFavorite(id) {
      this.$emit('remove', id);
    },
    retrieveFavorite(data) {
      this.$emit('retrieveFavorite', data);
    },
    // 日期变化
    handleTimeRangeChange(val) {
      if (val === 'customized') { // 自定义日期关闭自动刷新
        this.setRefreshTime(0);
      }
      this.$emit('update:timeRange', val);
    },
    handleDateChange(val) {
      this.$emit('update:datePickerValue', val);
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
      this.$emit('settingMenuClick', val);
    },
  },
};
</script>

<style lang="scss" scoped>
  .result-header {
    position: absolute;
    display: flex;
    // align-items: center;
    width: 100%;
    height: 52px;
    color: #63656e;
    background: #fff;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
    font-size: 12px;
    z-index: 3000;

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
        content: "";
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
          border-radius: 50%;
          background-color: #e1ecff;
        }
      }
      &::before {
        content: "";
        width: 1px;
        height: 14px;
        background-color: #dcdee5;
        position: absolute;
        left: 0;
        top: 20px;
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
