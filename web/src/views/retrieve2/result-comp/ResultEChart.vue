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
  <div class="monitor-echarts-container" v-bkloading="{ isLoading }">
    <MonitorEcharts
      v-if="isRenderChart"
      v-show="!isLoading"
      ref="chartRef"
      chart-type="bar"
      :title="$t('总趋势')"
      :key="chartKey"
      :line-width="2"
      :options="chartOptions"
      :get-series-data="getSeriesData"
      @toggle-expand="toggleExpand"
      @dblclick="handleDbClick" />
    <div v-if="isEmptyChart && !isFold" class="chart-empty">
      <svg class="icon-chart" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="256" height="256">
        <path d="M128 160h64v640h704v64H128z"></path>
        <path d="M307.2 636.8l-44.8-44.8 220.8-220.8 137.6 134.4 227.2-227.2 44.8 44.8-272 272-137.6-134.4z"></path>
      </svg>
      <span class="text">{{ $t('暂无数据') }}</span>
    </div>
    <div class="converge-cycle" v-if="!isEmptyChart && !isFold">
      <span>{{ $t('retrieve.convergeCycle') }}</span>
      <bk-select
        style="width: 80px"
        v-model="retrieveParams.interval"
        :clearable="false"
        ext-cls="select-custom"
        size="small"
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
import MonitorEcharts from '@/components/monitor-echarts/monitor-echarts-new';

export default {
  components: {
    MonitorEcharts,
  },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
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
    };
  },
  computed: {
    chartKey() {
      return this.$store.state.retrieve.chartKey;
    },
  },
  watch: {
    chartKey: {
      handler() {
        this.isRenderChart = true;
        this.isLoading = false;
      },
    },
  },
  mounted() {
    window.bus.$on('openChartLoading', this.openChartLoading);
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
      this.$refs.chartRef.handleSeriesData();
    },
    // 需要更新图表数据
    async getSeriesData(startTime, endTime) {
      if (startTime && endTime) {
        // 框选时间范围
        window.bus.$emit('changeTimeByChart', [startTime, endTime], 'customized');
      } else {
        // 初始化请求
      }

      this.isEmptyChart = false;
      const res = await this.$http.request('retrieve/getLogChartList', {
        params: { index_set_id: this.$route.params.indexId },
        data: this.retrieveParams,
      });
      // eslint-disable-next-line camelcase
      const originChartData = res.data.aggs?.group_by_histogram?.buckets || [];
      this.isEmptyChart = originChartData.length < 1;
      return [{
        datapoints: originChartData.map(item => ([item.doc_count, item.key])),
        target: '',
      }];
    },
    // 双击回到初始化时间范围
    handleDbClick() {
      const { cacheDatePickerValue, cacheTimeRange } = this.$store.state.retrieve;
      if (
        cacheDatePickerValue[0] !== this.retrieveParams.start_time
                    || cacheDatePickerValue[1] !== this.retrieveParams.end_time
                    || cacheTimeRange !== this.retrieveParams.time_range
      ) {
        setTimeout(() => {
          this.$refs.chartRef.handleSeriesData();
          window.bus.$emit('changeTimeByChart', cacheDatePickerValue, cacheTimeRange);
        }, 100);
      }
    },
    toggleExpand(isFold) {
      this.isFold = isFold;
      localStorage.setItem('chartIsFold', isFold);
    },
  },
};
</script>

<style lang="scss" scoped>
  .monitor-echarts-container {
    position: relative;
    margin: 0 20px;
    width: calc(100% - 40px);
    // height: 310px;
    // height: 200px;
    // border: 1px solid #DCDEE5;
    background-color: #fff;
    overflow: hidden;

    /deep/ .echart-legend {
      display: flex;
      justify-content: center;
    }

    .converge-cycle {
      position: absolute;
      top: 21px;
      left: 80px;
      font-size: 12px;
      color: #63656e;
      display: inline-block;
      margin-left: 32px;

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
  }
</style>
