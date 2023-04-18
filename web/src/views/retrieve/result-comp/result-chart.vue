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
  <div
    :class="['monitor-echarts-container', { 'is-fold': isFold }]"
    data-test-id="retrieve_div_generalTrendEcharts"
    v-bkloading="{ isLoading: false }">
    <chart-title
      ref="chartTitle"
      :title="$t('总趋势')"
      :menu-list="chartOptions.tool.list"
      :is-fold="isFold"
      :loading="isLoading || !finishPolling"
      @toggle-expand="toggleExpand"
      @menu-click="handleMoreToolItemSet">
    </chart-title>
    <MonitorEcharts
      v-if="isRenderChart"
      v-show="!isFold && !isLoading"
      ref="chartRef"
      chart-type="bar"
      :is-fold="isFold"
      :title="$t('总趋势')"
      :key="chartKey"
      :line-width="2"
      :options="chartOptions"
      :get-series-data="getSeriesData"
      @dblclick="handleDbClick"
      @chart-loading="handleChartLoading" />
    <div v-if="isEmptyChart && !isFold" class="chart-empty">
      <svg
        class="icon-chart"
        viewBox="0 0 1024 1024"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        width="256"
        height="256">
        <path d="M128 160h64v640h704v64H128z"></path>
        <path d="M307.2 636.8l-44.8-44.8 220.8-220.8 137.6 134.4 227.2-227.2 44.8 44.8-272 272-137.6-134.4z"></path>
      </svg>
      <span class="text">{{ $t('暂无数据') }}</span>
    </div>
    <div
      class="converge-cycle"
      v-if="!isEmptyChart && !isFold"
      v-en-style="'left: 110px'">
      <span>{{ $t('汇聚周期') }}</span>
      <bk-select
        style="width: 80px"
        v-model="chartInterval"
        :clearable="false"
        behavior="simplicity"
        ext-cls="select-custom"
        size="small"
        data-test-id="generalTrendEcharts_div_selectCycle"
        @change="handleIntervalChange">
        <bk-option
          v-for="option in intervalArr"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
    </div>
  </div>
</template>

<script>
import { formatDate } from '@/common/util';
import indexSetSearchMixin from '@/mixins/indexSet-search-mixin';
import MonitorEcharts from '@/components/monitor-echarts/monitor-echarts-new';
import ChartTitle from '@/components/monitor-echarts/components/chart-title-new.vue';

export default {
  components: {
    MonitorEcharts,
    ChartTitle,
  },
  mixins: [indexSetSearchMixin],
  props: {
    retrieveParams: {
      type: Object,
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
      timeRange: [],
      isFold: localStorage.getItem('chartIsFold') === 'true',
      intervalArr: [
        { id: 'auto', name: 'auto' },
        { id: '1m', name: '1 min' },
        { id: '5m', name: '5 min' },
        { id: '1h', name: '1 h' },
        { id: '1d', name: '1d' },
      ],
      chartOptions: {
        tool: {
          list: ['screenshot'],
        },
        useUTC: false,
        xAxis: {
          axisLine: {
            show: true,
            lineStyle: {
              color: '#666',
            },
          },
          axisLabel: {
            align: 'center',
          },
          axisTick: {
            show: true,
          },
        },
        yAxis: {
          axisLine: {
            show: true,
            lineStyle: {
              color: '#666',
              type: 'dashed',
            },
          },
        },
      },
      isLoading: false,
      isRenderChart: false,
      isEmptyChart: true,
      optionData: [],
      totalCount: 0,
    };
  },
  computed: {
    chartKey() {
      this.getInterval();
      return this.$store.state.retrieve.chartKey;
    },
    // chartInterval() {
    //   return this.retrieveParams.interval;
    // },
  },
  watch: {
    chartKey: {
      handler() {
        this.$refs.chartRef && this.$refs.chartRef.handleCloseTimer();
        this.totalCount = 0;
        this.isRenderChart = true;
        this.isLoading = false;
        this.finishPolling = false;
        this.isStart = false;
      },
    },
    totalCount(newVal) {
      this.$emit('change-total-count', newVal);
    },
    finishPolling(newVal) {
      this.$emit('change-queue-res', newVal);
    },
    'retrieveParams.interval'(newVal) {
      this.chartInterval = newVal;
    },
  },
  mounted() {
    window.bus.$on('openChartLoading', this.openChartLoading);
    this.chartInterval = this.retrieveParams.interval;
  },
  beforeDestroy() {
    window.bus.$on('openChartLoading', this.openChartLoading);
  },
  methods: {
    openChartLoading() {
      this.isLoading = true;
    },
    // 汇聚周期改变
    handleIntervalChange() {
      // this.getInterval();
      // this.finishPolling = true;
      // this.$refs.chartRef.handleCloseTimer();
      // this.totalCount = 0;
      // setTimeout(() => {
      //   this.finishPolling = false;
      //   this.isStart = false;
      //   this.$refs.chartRef.handleChangeInterval();
      // }, 500);
      this.$store.commit('retrieve/updateChartKey');
    },
    // 需要更新图表数据
    async getSeriesData(startTime, endTime) {
      if (startTime && endTime) {
        this.timeRange = [startTime, endTime];
        this.finishPolling = false;
        this.isStart = false;
        this.totalCount = 0;
        // 框选时间范围
        window.bus.$emit('changeTimeByChart', [startTime, endTime], 'customized');
      } else {
        // 初始化请求
      }

      // 轮循结束
      if (this.finishPolling) return;

      const { startTimeStamp, endTimeStamp } = this.getRealTimeRange();
      // 请求间隔时间
      this.requestInterval = this.isStart ? this.requestInterval
        : this.handleRequestSplit(startTimeStamp, endTimeStamp);
      if (!this.isStart) {
        this.isEmptyChart = false;

        // 获取坐标分片间隔
        this.handleIntervalSplit(startTimeStamp, endTimeStamp);

        // 获取分片起止时间
        const curStartTimestamp = this.getIntegerTime(startTimeStamp);
        const curEndTimestamp = this.getIntegerTime(endTimeStamp);

        // 获取分片结果数组
        this.optionData = this.getTimeRange(curStartTimestamp, curEndTimestamp);

        this.pollingEndTime = endTimeStamp;
        this.pollingStartTime = this.pollingEndTime - this.requestInterval;

        if (this.pollingStartTime < startTimeStamp || this.requestInterval === 0) {
          this.pollingStartTime = startTimeStamp;
          // 轮询结束
          this.finishPolling = true;
        }
        this.isStart = true;
      } else {
        this.pollingEndTime = this.pollingStartTime;
        this.pollingStartTime = this.pollingStartTime - this.requestInterval;

        if (this.pollingStartTime < Date.parse(this.retrieveParams.start_time)) {
          this.pollingStartTime = Date.parse(this.retrieveParams.start_time);
        }
      }

      if (!!this.$route.params?.indexId) { // 从检索切到其他页面时 表格初始化的时候路由中indexID可能拿不到 拿不到 则不请求图表
        const res = await this.$http.request('retrieve/getLogChartList', {
          params: { index_set_id: this.$route.params.indexId },
          data: {
            ...this.retrieveParams,
            time_range: 'customized',
            interval: this.interval,
            // 每次轮循的起始时间
            start_time: formatDate(this.pollingStartTime),
            end_time: formatDate(this.pollingEndTime),
          },
        });
        const originChartData = res.data.aggs?.group_by_histogram?.buckets || [];
        const targetArr = originChartData.map((item) => {
          this.totalCount = this.totalCount + item.doc_count;
          return ([item.doc_count, item.key]);
        });

        if (this.pollingStartTime <= Date.parse(this.retrieveParams.start_time)) {
        // 轮询结束
          this.finishPolling = true;
        }

        for (let i = 0; i < targetArr.length; i++) {
          for (let j = 0; j < this.optionData.length; j++) {
            if (this.optionData[j][1] === targetArr[i][1] && targetArr[i][0] > 0) {
              // 根据请求结果匹配对应时间下数量叠加
              this.optionData[j][0] = this.optionData[j][0] + targetArr[i][0];
            }
          }
        }
      } else {
        this.finishPolling = true;
      }

      return [{
        datapoints: this.optionData,
        target: '',
        isFinish: this.finishPolling,
      }];
    },
    // 双击回到初始化时间范围
    handleDbClick() {
      const { cacheDatePickerValue, cacheTimeRange } = this.$store.state.retrieve;

      if (this.timeRange.length) {
        this.timeRange = [];
        setTimeout(() => {
          window.bus.$emit('changeTimeByChart', cacheDatePickerValue, cacheTimeRange);
          this.finishPolling = true;
          this.totalCount = 0;
          this.$refs.chartRef.handleCloseTimer();
          setTimeout(() => {
            this.finishPolling = false;
            this.isStart = false;
            this.$store.commit('retrieve/updateChartKey');
          }, 100);
        }, 100);
      }
    },
    toggleExpand(isFold) {
      this.isFold = isFold;
      localStorage.setItem('chartIsFold', isFold);
      this.$refs.chartRef.handleToggleExpand(isFold);
    },
    handleMoreToolItemSet(event) {
      this.$refs.chartRef.handleMoreToolItemSet(event);
    },
    handleChartLoading(isLoading) {
      this.isLoading = isLoading;
    },
  },
};
</script>

<style lang="scss">
  .monitor-echarts-container {
    position: relative;
    height: 160px;
    background-color: #fff;
    overflow: hidden;

    &.is-fold {
      height: 60px;
    }

    :deep(.echart-legend) {
      display: flex;
      justify-content: center;
    }

    .converge-cycle {
      position: absolute;
      top: 17px;
      left: 80px;
      font-size: 12px;
      color: #63656e;
      display: inline-block;
      margin-left: 24px;

      .select-custom {
        display: inline-block;
        margin-left: 5px;
        vertical-align: middle;
      }
    }

    .chart-empty {
      position: absolute;
      top: 0;
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      background: #fff;

      .icon-chart {
        width: 38px;
        height: 38px;
        fill: #dcdee6;
      }

      .text {
        color: #979ba5;
        font-size: 14px;
      }
    }

    .title-wrapper {
      padding: 14px 24px 0;
    }

    .monitor-echart-wrap {
      height: 106px;
      padding-top: 0;
      padding-bottom: 0;

      .chart-wrapper {
        /* stylelint-disable-next-line declaration-no-important */
        min-height: 116px !important;

        /* stylelint-disable-next-line declaration-no-important */
        max-height: 116px !important;
      }
    }
  }
</style>
