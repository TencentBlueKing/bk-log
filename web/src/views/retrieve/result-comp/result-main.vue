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
  <div class="result-scroll-container" ref="scrollContainer" @scroll.passive="handleScroll">
    <!-- 检索结果 -->
    <div class="result-text">
      <i18n path="检索结果（找到 {0} 条结果，用时{1}毫秒) {2}">
        <span class="total-count">{{ totalCount }}</span>
        <span>{{tookTime}}</span>
        <template v-if="showAddMonitor">
          <span>
            , <i18n path="将搜索条件 {0}">
              <a href="javascript:void(0);" class="monitor-link" @click="jumpMonitor">
                {{ $t('添加为监控') }}
                <span class="log-icon icon-lianjie"></span>
              </a>
            </i18n>
          </span>
        </template>
      </i18n>
    </div>
    <div class="result-main">
      <result-chart
        :retrieve-params="retrieveParams"
        :picker-time-range="pickerTimeRange"
        :date-picker-value="datePickerValue"
        @change-queue-res="changeQueueRes"
        @change-total-count="changeTotalCount" />
      <bk-divider class="divider-line"></bk-divider>
      <result-table-panel
        ref="resultTablePanel"
        v-bind="$attrs"
        v-on="$listeners"
        :retrieve-params="retrieveParams"
        :total-count="totalCount"
        :queue-status="queueStatus"
        :table-list="tableList"
        :origin-table-list="originTableList"
        :kv-show-fields-list="kvShowFieldsList"
        :is-page-over="isPageOver" />
    </div>
    <!-- 滚动到顶部 -->
    <div class="fixed-scroll-top-btn" v-show="showScrollTop" @click="scrollToTop">
      <i class="bk-icon icon-angle-up"></i>
    </div>
  </div>
</template>

<script>
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';
import ResultChart from './result-chart';
import ResultTablePanel from '../result-table-panel';
import { mapState } from 'vuex';
import { setFieldsWidth, parseBigNumberList } from '@/common/util';

export default {
  components: {
    ResultChart,
    ResultTablePanel,
  },
  mixins: [tableRowDeepViewMixin],
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    tookTime: {
      type: Number,
      required: true,
    },
    tableData: {
      type: Object,
      required: true,
    },
    indexSetList: {
      type: Array,
      required: true,
    },
    pickerTimeRange: {
      type: Array,
      default: () => [],
    },
    datePickerValue: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      originTableList: [],
      tableList: [],
      throttle: false, // 滚动节流 是否进入cd
      isPageOver: false, // 前端分页加载是否结束
      finishPolling: false,
      count: 0, // 数据总条数
      pageSize: 50, // 每页展示多少数据
      currentPage: 1, // 当前加载了多少页
      totalCount: 0,
      scrollHeight: 0,
      limitCount: 0,
      queueStatus: false,
      showScrollTop: false, // 显示滚动到顶部icon
      isInit: false,
      kvShowFieldsList: [],
    };
  },
  computed: {
    ...mapState({
      bkBizId: state => state.bkBizId,
    }),
    showAddMonitor() {
      return Boolean(window.MONITOR_URL && this.$store.state.topMenu.some(item => item.id === 'monitor'));
    },
  },
  watch: {
    tableData(data) {
      this.finishPolling = data && data.finishPolling;
      if (data?.list?.length) {
        if (this.isInit) {
          // 根据接口 data.fields ==> item.max_length 设置各个字段的宽度比例
          setFieldsWidth(this.visibleFields, data.fields, 500);
          this.isInit = true;
        }
        const list = parseBigNumberList(data.list);
        const originLogList = parseBigNumberList(data.origin_log_list);
        this.count += data.list.length;
        this.kvShowFieldsList = Object.keys(data.fields || []);
        this.tableList.push(...list);
        this.originTableList.push(...originLogList);
        this.$nextTick(() => {
          this.$refs.scrollContainer.scrollTop = this.newScrollHeight;
        });
        this.isPageOver = false;
      }
    },
  },
  methods: {
    // 跳转到监控
    jumpMonitor() {
      const indexSetId = this.$route.params.indexId;
      const params = {
        bizId: this.$store.state.bkBizId,
        indexSetId,
        scenarioId: '',
        indexStatement: this.retrieveParams.keyword, // 查询语句
        dimension: [], // 监控维度
        condition: [], // 监控条件
      };
      const indexSet = this.indexSetList.find(item => item.index_set_id === indexSetId);
      if (indexSet) {
        params.scenarioId = indexSet.category_id;
      }
      this.retrieveParams.addition.forEach((item) => {
        params.condition.push({
          condition: 'and',
          key: item.field,
          method: item.operator === 'eq' ? 'is' : item.operator,
          value: item.value,
        });
      });
      const urlArr = [];
      for (const key in params) {
        if (key === 'dimension' || key === 'condition') {
          urlArr.push(`${key}=${encodeURI(JSON.stringify(params[key]))}`);
        } else {
          urlArr.push(`${key}=${params[key]}`);
        }
      }
      window.open(`${window.MONITOR_URL}/?${urlArr.join('&')}#/strategy-config/add`, '_blank');
    },
    reset() {
      this.newScrollHeight = 0;
      this.$nextTick(() => {
        this.$refs.scrollContainer.scrollTop = this.newScrollHeight;
      });
      this.count = 0;
      this.currentPage = 1;
      this.originTableList = [];
      this.tableList = [];
      this.isInit = false;
      this.finishPolling = false;
    },
    // 滚动到顶部
    scrollToTop() {
      this.$easeScroll(0, 300, this.$refs.scrollContainer);
    },
    handleScroll() {
      if (this.throttle || this.isPageOver || this.$refs.resultTablePanel.active === 'clustering') {
        return;
      }
      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;
        const el = this.$refs.scrollContainer;
        this.showScrollTop = el.scrollTop > 550;
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 20) {
          if (this.count === this.limitCount || this.finishPolling) return;

          this.isPageOver = true;
          this.currentPage += 1;
          this.newScrollHeight = el.scrollTop;
          this.$emit('request-table-data');
        }
      }, 200);
    },
    changeTotalCount(count) {
      this.totalCount = count;
    },
    changeQueueRes(status) {
      this.queueStatus = status;
    },
  },
};
</script>

<style lang="scss" scoped>
  // @import '../../../scss/mixins/scroller.scss';

  .result-scroll-container {
    height: 100%;
    overflow: auto;

    &::-webkit-scrollbar {
      width: 10px;
      height: 4px;
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 5px;
      border-style: dashed;
      border-left-width: 3px;
      border-color: transparent;
      background-color: #ddd;
      background-clip: padding-box;
    }

    &::-webkit-scrollbar-thumb:hover {
      background: #ddd;
    }
  }

  .result-text {
    font-size: 12px;
    color: #63656e;
    padding: 10px 20px;

    .monitor-link {
      color: #3a84ff;
    }

    .total-count {
      color: #f00;
    }
  }

  .result-main {
    margin: 0 16px 16px;
    min-height: calc(100% - 54px);
    background-color: #fff;
  }

  .divider-line {
    /* stylelint-disable-next-line declaration-no-important */
    margin: 0 !important;
  }

  .fixed-scroll-top-btn {
    position: fixed;
    bottom: 24px;
    right: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 36px;
    height: 36px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .2);
    border: 1px solid #dde4eb;
    border-radius: 4px;
    color: #63656e;
    background: #f0f1f5;
    cursor: pointer;
    z-index: 2100;
    transition: all .2s;

    &:hover {
      color: #fff;
      background: #979ba5;
      transition: all .2s;
    }

    .bk-icon {
      font-size: 20px;
      font-weight: bold;
    }
  }
</style>
