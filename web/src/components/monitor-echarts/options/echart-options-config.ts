/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

export const lineOrBarOptions = {
  useUTC: true,
  title: {
    text: '',
    show: false,
    textAlign: 'auto',
    textVerticalAlign: 'auto',
    left: 'left',
    top: 12,
    padding: [0, 0, 0, 16],
    textStyle: {
      color: '#63656E',
      fontSize: 12,
      fontWeight: 'bold'
    },
    subtext: null,
    subtextStyle: {
      color: '#979BA5',
      fontSize: 12,
      fontWeight: 'bold',
      align: 'left'
    }
  },
  color: [],
  legend: {
    type: 'scroll',
    bottom: 0,
    show: true,
    itemGap: 12,
    itemWidth: 12,
    itemHeight: 8,
    padding: [5, 5, 0, 0],
    selectedMode: 'multiple',
    textStyle: {
      color: '#63656E',
      fontSize: 12
    },
    icon: 'rect'
  },
  tooltip: {
    show: true,
    trigger: 'axis',
    axisPointer: {
      type: 'line',
      label: {
        backgroundColor: '#6a7985'
      }
    },
    transitionDuration: 0,
    alwaysShowContent: false,
    backgroundColor: 'rgba(0,0,0,0.8)',
    borderWidth: 0,
    textStyle: {
      fontSize: 12
    },
    extraCssText: 'border-radius: 0'
  },
  toolbox: {
    showTitle: false,
    itemSize: 0,
    iconStyle: {
      color: '#979ba5',
      fontSize: 14,
      borderWidth: 0,
      shadowColor: '#979ba5',
      shadowOffsetX: 0,
      shadowOffsetY: 0
    },
    feature: {
      saveAsImage: {
        icon: 'path://'
      },
      dataZoom: {
        icon: {
          zoom: 'path://',
          back: 'path://'
        },
        show: true,
        yAxisIndex: [],
        iconStyle: {
          opacity: 0
        }
      },
      restore: { icon: 'path://' }
    }
  },
  grid: {
    containLabel: true,
    left: 0,
    right: 26,
    top: 16,
    bottom: 0,
    backgroundColor: 'transparent'
  },
  xAxis: {
    type: 'time',
    boundaryGap: false,
    axisTick: {
      show: false
    },
    axisLine: {
      show: false,
      lineStyle: {
        color: '#ccd6eb',
        width: 1,
        type: 'solid'
      }
    },
    axisLabel: {
      fontSize: 12,
      color: '#979BA5',
      showMinLabel: false,
      showMaxLabel: false,
      align: 'left'
    },
    splitLine: {
      show: false
    },
    minInterval: 60 * 1000,
    splitNumber: 10,
    scale: true
  },
  yAxis: {
    type: 'value',
    axisLine: {
      show: false,
      lineStyle: {
        color: '#ccd6eb',
        width: 1,
        type: 'solid'
      }
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#979BA5'
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: '#F0F1F5',
        type: 'dashed'
      }
    },
    scale: false,
    // splitNumber: 3,
    z: 3
  },
  series: [],
  animation: true
}

export const pieOptions: any = {
  lengend: {
    show: false
  },
  tooltip: {
    trigger: 'item'
  },
  series: [
    {
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: 'center'
      },
      labelLine: {
        show: false
      }
    }
  ]
}
