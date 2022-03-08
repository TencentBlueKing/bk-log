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
  <div class="bk-charts-container" id="container">
    <line-tooltips
      :data-list="dataList"
      @clickTooltips="clickTooltips"
      class="tool" />
  </div>
</template>

<script>
import BaseSettings from '../base-settings';
import BKChart from '@blueking/bkcharts';
import LineTooltips from './line-tooltips.vue';

export default {
  components: {
    LineTooltips,
  },
  extends: BaseSettings,
  props: {
    series: { type: Array, default: () => ([]) },
    labels: { type: Array, default: () => ([]) },
    lineColor: { type: Array, default: () => ([]) },
  },
  data() {
    return {
      lastNum: '',
      firstClick: true,
      color: BKChart.helpers.color,
      defaultDataSet: {
        label: '',
        backgroundColor: '#3a84ff',
        borderColor: '#3a84ff',
        data: [],
        fill: false,
        pointRadius: 1,
        status: true,
        tension: 0.4,
      },
      defaultTooltips: {
        mode: 'point',
        caretSize: 0,
        caretPadding: 10,
        cornerRadius: 2,
        intersect: false,
        callbacks: {
          beforeTitle: (tooltipItem, data) => data.datasets[tooltipItem[0].datasetIndex].label,
          label: tooltipItem => tooltipItem.value,
        },
        backgroundColor: '#000000',
      },
      dataList: [],
    };
  },
  computed: {
    seriesData() {
      return this.series;
    },
    chartConfig() {
      return {
        labels: this.labels || [],
        datasets: this.series.map(ds => Object.assign({}, this.defaultDataSet, ds)).slice(0, 10),
      };
    },
    titleConfig() {
      return typeof this.title !== 'object' ? { display: false, text: '' } : this.title;
    },
    legendConfig() {
      return Object.assign({}, { display: false }, this.legend);
    },
    tooltipsConfig() {
      return Object.assign({}, { animateScale: true, animateRotate: true }, this.defaultTooltips);
    },
  },
  watch: {
    series: {
      handler: 'handleDataChanged',
      immediate: true,
    },
  },
  created() {
    this.series.forEach((item, index) => {
      Object.assign(item, {
        status: index < 10,
        fill: false,
        backgroundColor: this.lineColor[index % this.lineColor.length],
        borderColor: this.lineColor[index % this.lineColor.length],
        tension: 0.4,
      });
    });
    this.dataList = JSON.parse(JSON.stringify(this.series));
  },
  mounted() {
    this.type = 'line';
    this.init(this.$el);
  },
  methods: {
    handleDataChanged() {
      this.$nextTick(() => {
        if (!this.instance) {
          this.renderInstance();
        } else {
          this.update(this.chartConfig.datasets);
        }
      });
    },
    renderInstance() {
      this.renderChart(this.chartConfig, {
        responsive: this.responsive,
        plugins: {
          legend: this.legendConfig,
          title: this.titleConfig,
        },
        // tooltips: this.tooltipsConfig
      });
    },
    renderChart(chartConfig, opts) {
      this.instance = new BKChart(this.context, {
        type: this.type,
        data: chartConfig,
        options: opts,
      });
    },
    clickTooltips(item, ind, type) {
      if (type === 'shift') {
        if (!this.dataList[ind].status) {
          this.chartConfig.datasets.push(item);
          this.dataList[ind].status = true;
        }
      } else {
        if (item.status) {
          if (this.chartConfig.datasets.length === 1) {
            this.chartConfig.datasets.splice(0, 1);
            this.chartConfig.datasets = JSON.parse(JSON.stringify(this.series));
            this.chartConfig.datasets.forEach((item, index) => {
              this.dataList[index].status = true;
            });
          } else {
            if (this.firstClick || this.chartConfig.datasets.length === this.dataList.length) {
              this.chartConfig.datasets.forEach((element, index) => {
                this.dataList[index].status = false;
              });
              this.chartConfig.datasets.splice(0, this.chartConfig.datasets.length);
              this.chartConfig.datasets.push(item);
              this.firstClick = false;
              item.status = !item.status;
            } else {
              this.dataList[ind].status = false;
              this.chartConfig.datasets.forEach((ite, ind) => {
                if (item.label === ite.label) {
                  this.chartConfig.datasets.splice(ind, 1);
                }
              });
            }
          }
        } else {
          if (this.chartConfig.datasets.length === 1) {
            this.dataList[this.lastNum].status = false;
          } else {
            this.dataList.forEach((item, index) => {
              this.dataList[index].status = false;
            });
          }
          this.chartConfig.datasets.splice(0, this.chartConfig.datasets.length);
          this.chartConfig.datasets.push(item);
          item.status = !item.status;
        }
        this.lastNum = ind;
      }
      this.instance.update();
    },
  },
};
</script>

<style lang="scss" scoped>
  #container {
    position: relative;
    padding-bottom: 60px;
  }

  .tool {
    position: absolute;
    bottom: 0px;
  }
</style>
