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
  <div class="chart-container" v-bkloading="{ isLoading: loading, zIndex: 0 }">
    <div class="chart-header">
      <div class="title">{{ type }}</div>
      <bk-button text style="font-size: 12px;" v-if="type === $t('检索耗时统计') && retrieveTimeGuide" @click="goToGuide">
        {{ $t('耗时优化指引 >') }}
      </bk-button>
    </div>
    <div class="chart-canvas-container" ref="chartRef"></div>
    <bk-exception v-if="isEmpty" class="king-exception" type="empty" scene="part"></bk-exception>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import i18n from '@/language/i18n';

const defaultOption = {
  textStyle: {
    color: '#63656E',
  },
  grid: {
    x: 20,
    y: 10,
    x2: 20,
    y2: 30,
    left: '2%',   // 与容器左侧的距离
    containLabel: true,
  },
};

export default {
  props: {
    type: {
      type: String,
      required: true,
      validator: (val) => {
        return [i18n.t('使用次数趋势'), i18n.t('用户使用频次'), i18n.t('检索耗时统计')].includes(val);
      },
    },
    loading: {
      type: Boolean,
      default: true,
    },
    chartData: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      isEmpty: false,
      retrieveTimeGuide: window.RETRIEVE_TIME_OPTIMIZE_GUIDE_URL,
    };
  },
  watch: {
    chartData: {
      handler(val) {
        if (val) {
          this.updateChart(val);
        }
      },
      immediate: true,
    },
  },
  mounted() {
    let timer = 0;
    this.resizeChart = () => {
      if (!timer) {
        timer = setTimeout(() => {
          timer = 0;
          if (this.instance && !this.instance.isDisposed()) {
            this.instance.resize();
          }
        }, 400);
      }
    };
    window.addEventListener('resize', this.resizeChart);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
  },
  methods: {
    updateChart(chartData) {
      if (!chartData.values.length || chartData.values.every(item => item === 0)) {
        if (this.instance && !this.instance.isDisposed()) {
          this.instance.dispose();
        }
        this.isEmpty = true;
        return;
      }

      this.isEmpty = false;
      if (!this.instance || this.instance.isDisposed()) {
        this.instance = echarts.init(this.$refs.chartRef);
      }
      switch (this.type) {
        case this.$t('使用次数趋势'):
          this.setLineChart({
            labels: chartData.labels.map((item) => {
              const date = new Date(item);
              const mm = (`0${date.getMonth() + 1}`).slice(-2);
              const dd = (`0${date.getDate()}`).slice(-2);
              return mm + dd;
            }),
            values: chartData.values,
          });
          break;
        case this.$t('用户使用频次'):
          this.setBarChart(chartData);
          break;
        case this.$t('检索耗时统计'):
          this.setPieChart(chartData);
      }
    },
    // 折线图 使用次数趋势
    setLineChart(chartData) {
      this.instance.setOption(Object.assign({}, defaultOption, {
        xAxis: {
          data: chartData.labels,
          axisTick: {
            alignWithLabel: true,
          },
          axisLabel: {
            align: 'center',
          },
          axisLine: {
            lineStyle: {
              color: '#DCDEE5',
            },
          },
        },
        yAxis: {
          type: 'value',
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          splitLine: {
            lineStyle: {
              color: '#DCDEE5',
              type: 'dashed',
            },
          },
        },
        series: [{
          data: chartData.values,
          type: 'line',
          symbol: 'none',
          itemStyle: {
            color: '#339DFF',
          },
        }],
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line',
            axis: 'auto',
          },
        },
      }));
    },
    // 柱状图 用户使用频次
    setBarChart(chartData) {
      this.instance.setOption(Object.assign({}, defaultOption, {
        xAxis: {
          type: 'category',
          data: chartData.labels,
          axisTick: {
            alignWithLabel: true,
          },
          axisLabel: {
            align: 'center',
          },
          axisLine: {
            lineStyle: {
              color: '#DCDEE5',
            },
          },
        },
        yAxis: {
          type: 'value',
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          splitLine: {
            lineStyle: {
              color: '#DCDEE5',
              type: 'dashed',
            },
          },
        },
        series: [{
          data: chartData.values,
          type: 'bar',
          barMaxWidth: 24,
          itemStyle: {
            color: '#339DFF',
          },
        }],
        tooltip: {
          trigger: 'item',
        },
      }));
    },
    // 饼图，检索耗时统计
    setPieChart(chartData) {
      const colors = ['#B568FF', '#3BCE95', '#339DFF'];
      const newChartData = chartData.values
        .map((value, index) => ({
          value,
          name: chartData.labels[index],
          itemStyle: {
            color: colors[index],
          },
        }))
        .filter(item => Boolean(item.value));
      this.instance.setOption(Object.assign({}, defaultOption, {
        tooltip: {
          trigger: 'item',
          formatter: '{b} <br/>{a} {d}%',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'middle',
        },
        series: [{
          name: this.$t('占比'),
          type: 'pie',
          radius: '50%',
          data: newChartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        }],
      }));
    },
    goToGuide() {
      window.open(this.retrieveTimeGuide, '_blank');
    },
  },
};
</script>
