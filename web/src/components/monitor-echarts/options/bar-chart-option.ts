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

import { ILegendItem, IChartInstance } from './type-interface'
import MonitorBaseSeries from './base-chart-option'
import deepMerge from 'deepmerge'
import { lineOrBarOptions } from './echart-options-config'
export default class MonitorLineSeries extends  MonitorBaseSeries implements IChartInstance {
  public defaultOption: any
  public constructor(props: any) {
    super(props)
    this.defaultOption = deepMerge(deepMerge(lineOrBarOptions, {
      color: this.colors,
      yAxis: {
        axisLabel: {
          formatter: this.handleYxisLabelFormatter
        }
      }
    }, { arrayMerge: this.overwriteMerge }), this.chartOption, { arrayMerge: this.overwriteMerge })
  }
  public getOptions(data: any, otherOptions = {}): any {
    let { series } = data || {}
    series = deepMerge([], series)
    const hasSeries = series && series.length > 0
    const formatterFunc = hasSeries && series[0].data && series[0].data.length
      ? this.handleSetFormatterFunc(series[0].data)
      : null

    const { maxThreshold, minThreshold } = this.handleGetMaxAndMinThreholds(series)

    const legendData: any = []
    const options =  {
      xAxis: {
        axisLabel: {
          formatter: hasSeries && formatterFunc ? formatterFunc : '{value}'
        }
      },
      yAxis: {
        max: (v: {min: number, max: number}) => Math.max(v.max, maxThreshold),
        min: Math.min(0, minThreshold)
      },
      legend: {
        show: false
      },
      series: hasSeries ? series.map((item: any, index: number) => {
        const legendItem: ILegendItem = {
          name: String(item.name),
          max: 0,
          min: 0,
          avg: 0,
          total: 0,
          color: this.colors[index % this.colors.length],
          show: true
        }
        item.data.forEach((seriesItem: any) => {
          if (seriesItem?.length && seriesItem[1]) {
            const curValue = +seriesItem[1]
            legendItem.max = Math.max(legendItem.max, curValue)
            legendItem.min = Math.min(+legendItem.min, curValue)
            legendItem.total = (legendItem.total + curValue)
          }
        })
        legendItem.avg = +(legendItem.total / item.data.length).toFixed(2)
        legendItem.total = +(legendItem.total).toFixed(2)
        legendData.push(legendItem)

        let markLine = {}
        let markArea = {}
        if (item?.thresholds?.length) {
          markLine = this.handleSetThresholdLine(item.thresholds)
          markArea = this.handleSetThresholdArea(item.thresholds)
        }
        return {
          ...item,
          type: this.chartType,
          barMinHeight: 4,
          z: 4,
          markLine,
          markArea
        }
      }) : []
    }
    return {
      options: deepMerge(deepMerge(
        this.defaultOption, otherOptions,
        { arrayMerge: this.overwriteMerge }
      ), options, { arrayMerge: this.overwriteMerge }),
      legendData
    }
  }

  // 设置阈值线
  private handleSetThresholdLine(thresholdLine: any[]) {
    return {
      symbol: [],
      label: {
        show: true,
        position: 'insideStartTop'
      },
      lineStyle: {
        color: '#FD9C9C',
        type: 'dashed',
        distance: 3,
        width: 1
      },
      data: thresholdLine.map((item: any) => ({
        ...item,
        label: {
          show: true,
          formatter(v: any) {
            return v.name || ''
          }
        }
      }))
    }
  }

  private handleGetMaxAndMinThreholds(series: any[] = []) {
    let thresholdList = series.filter((set: any) => set?.thresholds?.length).map((set: any) => set.thresholds)
    thresholdList  = thresholdList.reduce((pre: any, cur: any, index: number) => {
      pre.push(...cur.map((set: any) => set.yAxis))
      if (index === thresholdList.length - 1) {
        return Array.from(new Set(pre))
      }
      return pre
    }, [])
    return {
      minThreshold: Math.min(...thresholdList),
      maxThreshold: Math.max(...thresholdList)
    }
  }

  private handleSetThresholdArea(thresholdLine: any[]) {
    const data = this.handleSetThresholdAreaData(thresholdLine)
    return {
      label: {
        show: false
      },
      data
    }
  }

  private handleSetThresholdAreaData(thresholdLine: any[]) {
    const threshold = thresholdLine.filter(item => item.method && !['eq', 'neq'].includes(item.method))

    const openInterval = ['gte', 'gt'] // 开区间
    const closedInterval = ['lte', 'lt'] // 闭区间

    const data = []
    // eslint-disable-next-line @typescript-eslint/prefer-for-of
    for (let index = 0; index < threshold.length; index++) {
      const current = threshold[index]
      const nextThreshold = threshold[index + 1]
      // 判断是否为一个闭合区间
      let yAxis = undefined
      if (openInterval.includes(current.method) && nextThreshold && nextThreshold.condition === 'and'
        && closedInterval.includes(nextThreshold.method) && (nextThreshold.yAxis >= current.yAxis)) {
        yAxis = nextThreshold.yAxis
        index += 1
      } else if (closedInterval.includes(current.method) && nextThreshold && nextThreshold.condition === 'and'
      && openInterval.includes(nextThreshold.method) && (nextThreshold.yAxis <= current.yAxis)) {
        yAxis = nextThreshold.yAxis
        index += 1
      } else if (openInterval.includes(current.method)) {
        yAxis = 'max'
      } else if (closedInterval.includes(current.method)) {
        yAxis = current.yAxis < 0 ? current.yAxis : 0
      }

      yAxis !== undefined && data.push([
        {
          ...current
        },
        {
          yAxis,
          y: yAxis === 'max' ? '0%' : ''
        }
      ])
    }
    return data
  }
}
