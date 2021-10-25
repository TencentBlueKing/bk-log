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
  <div style="position: relative">
    <div class="icon-sty">
      <span class="log-icon icon-camera-fill" :class="initialCallShow ? '' : 'click-stop'" @click="clickIcon"></span>
      <span :class="!initialCallShow ? 'rotate-from' : 'rotate'">
        <i class="bk-icon icon-angle-up" @click="handleToggleCallShow"></i>
      </span>
    </div>
    <div class="chart-views" ref="imageDom" v-if="initialCall && initialCallShow">
      <BKLine
        :height="'100px'"
        :width="'600px'"
        :line-color="lineColor"
        :series="dataList"
        :labels="labels"
        v-if="chartCut === 'line'">
      </BKLine>
      <TakeDemo :conum="conumData" v-else></TakeDemo>
    </div>
    <div class="chart-blank" v-else></div>
  </div>
</template>
<script>
import { convertDomToPng } from '@/common/util';
import moment from 'moment';
import {
  BKLine,
} from '@/components/bkChartVue/Components/index.js';
import TakeDemo from './Takefigure';
export default {
  name: 'chart-view',
  components: {
    BKLine,
    TakeDemo,
    // Scatter
  },
  props: {
    chartData: {
      type: Object,
      default: () => {},
    },
    charDotData: {
      type: Object,
      default: () => {},
    },
    chartCut: {
      type: String,
      default: '',
    },
    fieldName: {
      type: String,
      default: '',
    },
    initialCall: {
      type: Boolean,
      default: false,
    },
    initialCallShow: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      lineColor: ['#2ae0c8', '#fe6673', '#ffd591', '#fad8be', '#acf6ef', '#ffc20e', '#3A84FF', '#722ed1', '#eb2f96', '#2db7f5', '#07a2a4', '#9a7fd1', '#588dd5', '#f5994e', '#c05050', '#59678c', '#c9ab00', '#7eb00a', '#6f5553', '#c14089'],
      dataSets: [],
      labels: [],
      dataList: [],
      clickTooltips: [],
      conumData: {},
      ticks: {
        callback(label) {
          return moment(label).format('YY-MM-DD HH:mm:ss');
        },
      },
    };
  },
  watch: {
    fieldName(val) {
      if (this.chartData[val]) {
        this.chartAssignment();
      }
    },
    initialCall(val) {
      if (val) {
        this.chartAssignment();
      }
    },
    chartData(val) {
      if (val['tags.result_code'] && val['tags.result_code'].datasets) {
        val['tags.result_code'].datasets.forEach((item) => {
          const data = [];
          item.data.forEach((res) => {
            data.push(res.value);
          });
          item.data = data;
        });
      }
    },
  },
  methods: {
    chartAssignment() {
      if (this.chartCut === 'line') {
        this.labels = this.chartData[this.fieldName]?.labels || [];
        this.dataList = this.chartData[this.fieldName]?.datasets || [];
      } else {
        this.conumData = this.chartData[this.fieldName] || {};
      }
      // this.dataSets = this.charDotData.scatter
    },
    clickIcon() {
      if (this.initialCallShow) {
        convertDomToPng(this.$refs.imageDom);
      }
    },
    handleToggleCallShow() {
      this.$emit('toggle-call-show');
    },
  },
};
</script>
<style lang="scss" scoped>
  .chart-views {
    width: 100%;
    padding: 50px 24px 10px;
    border: 1px solid #ddd;
  }

  .icon-sty {
    position: absolute;
    right: 50px;
    top: 20px;
    line-height: 14px;

    .log-icon {
      background-color: #fff;
      color: #979ba5;
      transform: scale(1.2);
    }

    i:hover {
      color: #3a84ff;
      transition: color .2s;
    }

    .click-stop {
      color: #ccc!important;
    }

    span {
      margin-left: 10px;
      display: inline-block;
      height: 14px;
      width: 16px;
      background: #979ba5;
      border-radius: 2px;
      cursor: pointer;
      transition: background .2s;

      .bk-icon {
        line-height: 14px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #fff;
        font-weight: bold;
      }

      &:hover {
        color: #3a84ff;
        transition: background .2s;
      }
    }
  }

  .chart-blank {
    height: 60px;
    border: 1px solid #ddd;
  }

  .rotate-from {
    .bk-icon {
      transform: rotate(180deg);
      transition: transform .2s;
    }
  }

  .rotate {
    .bk-icon {
      transition: transform .2s;
    }
  }
</style>
