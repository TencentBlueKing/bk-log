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
import { getValueFormat, ValueFormatter  } from '../value-formats-package'
export default class MonitorLineSeries extends  MonitorBaseSeries implements IChartInstance  {
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
  // 设置折线图
  public getOptions(data: any, otherOptions: any = {}) {
    const { series } = data || {}
    const hasSeries = series && series.length > 0
    const formatterFunc = hasSeries && series[0].data && series[0].data.length
      ? this.handleSetFormatterFunc(series[0].data)
      : null
    const { series: newSeries, legendData } = this.getSeriesData(series)
    const [firstSery] = newSeries || []
    const { canScale, minThreshold, maxThreshold }  = this.handleSetThreholds(series)
    const options = {
      yAxis: {
        scale: canScale,
        axisLabel: {
          formatter: newSeries.every((item: any) => item.unit && item.unit === firstSery.unit) ? (v: any) => {
            const obj = getValueFormat(firstSery.unit)(v, firstSery.precision)
            return obj.text + (obj.suffix || '')
          } : this.handleYxisLabelFormatter
        },
        max: (v: {min: number, max: number}) => Math.max(v.max, maxThreshold),
        min: (v: {min: number, max: number}) => Math.min(v.min, minThreshold),
        splitNumber: 4,
        minInterval: 1
      },
      xAxis: {
        axisLabel: {
          formatter: hasSeries && formatterFunc ? formatterFunc : '{value}'
        }
      },
      legend: {
        show: false
      },
      series: hasSeries ? newSeries : []
    }
    return {
      options: deepMerge(deepMerge(
        this.defaultOption, otherOptions,
        { arrayMerge: this.overwriteMerge }
      ), options, { arrayMerge: this.overwriteMerge }),
      legendData
    }
  }
  private getSeriesData(seriess: any = []) {
    const legendData: ILegendItem[] = []
    const seriesData: any = deepMerge([], seriess)
    const series = seriesData.map((item: any, index: number) => {
      let showSymbol = !!item?.markPoints?.every((set: any) => set?.length === 2)
      const hasLegend = !!item.name
      const legendItem: ILegendItem = {
        name: String(item.name),
        max: 0,
        min: '',
        avg: 0,
        total: 0,
        color: item.color ||  this.colors[index % this.colors.length],
        show: true
      }
      const unitFormatter = getValueFormat(item.unit || '')
      const precision = this.handleGetMinPrecision(
        item.data.filter((set: any) => typeof set[1] === 'number').map(set => set[1])
        , unitFormatter, item.unit
      )
      item.data.forEach((seriesItem: any, seriesIndex: number) => {
        if (seriesItem?.length && seriesItem[1]) {
          const pre = item.data[seriesIndex - 1]
          const next = item.data[seriesIndex + 1]
          if (typeof seriesItem[1] === 'number') {
            const curValue = +seriesItem[1]
            legendItem.max = Math.max(legendItem.max, curValue)
            legendItem.min = legendItem.min === '' ? curValue : Math.min(+legendItem.min, curValue)
            legendItem.total = (legendItem.total + curValue)
          }
          if (item?.markPoints?.some((set: any) => set[1] === seriesItem[0])) {
            item.data[seriesIndex] = {
              symbolSize: 12,
              value: [seriesItem[0], seriesItem[1]],
              itemStyle: {
                borderWidth: 6,
                enabled: true,
                shadowBlur: 0,
                opacity: 1
              },
              label: {
                show: false
              }
            }
          } else {
            const hasNoBrother = (!pre && !next)
            || (pre && next && pre.length && next.length && pre[1] === null && next[1] === null)
            if (hasNoBrother) {
              showSymbol = true
            }
            item.data[seriesIndex] = {
              symbolSize: hasNoBrother ? 4 : 1,
              value: [seriesItem[0], seriesItem[1]],
              itemStyle: {
                borderWidth: hasNoBrother ? 4 : 1,
                enabled: true,
                shadowBlur: 0,
                opacity: 1
              }
            }
          }
        } else if (seriesItem.symbolSize) {
          showSymbol = true
        }
      })
      legendItem.avg = +(legendItem.total / item.data.length).toFixed(2)
      legendItem.total = +(legendItem.total).toFixed(2)
      const seriesItem = {
        ...item,
        type: this.chartType,
        showSymbol,
        symbol: 'circle',
        z: 4,
        smooth: 0.2,
        unitFormatter,
        precision,
        lineStyle: {
          width: this.lineWidth || 1
        }
      }
      if (item?.markTimeRange?.length) {
        seriesItem.markArea = this.handleSetThresholdBand(item.markTimeRange)
      }
      if (item?.thresholds?.length) {
        seriesItem.markLine = this.handleSetThresholdLine(item.thresholds)
        seriesItem.markArea = deepMerge(seriesItem.markArea, this.handleSetThresholdArea(item.thresholds))
      }
      if (hasLegend) {
        Object.keys(legendItem).forEach((key) => {
          if (['min', 'max', 'avg', 'total'].includes(key)) {
            const set = unitFormatter(legendItem[key], item.unit !== 'none' && precision < 1 ? 2 : precision)
            legendItem[key] = set.text + (set.suffix || '')
          }
        })
        legendData.push(legendItem)
      }
      return seriesItem
    })
    return { legendData, series }
  }
  // 设置阈值线
  private handleSetThresholdLine(thresholdLine: []) {
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
  // 设置阈值面板
  private handleSetThresholdBand(plotBands: {to: number, from: number}[]) {
    return {
      silent: true,
      show: true,
      itemStyle: {
        color: '#FFF5EC',
        borderWidth: 1,
        borderColor: '#FFE9D5',
        shadowColor: '#FFF5EC',
        shadowBlur: 0
      },
      data: plotBands.map(item => (
        [{
          xAxis: item.from,
          y: 'max'
        }, {
          xAxis: item.to || 'max',
          y: '0%'
        }]
      )),
      opacity: 0.1
    }
  }

  private handleGetMinPrecision(data: number[], formattter: ValueFormatter, unit: string) {
    if (!data || data.length === 0) {
      return 0
    }
    data.sort()
    const len = data.length
    if (data[0] === data[len - 1]) {
      if (unit === 'none') return 0
      const setList =  String(data[0]).split('.')
      return  (!setList || setList.length < 2) ? 2 : setList[1].length
    }
    let precision = 0
    let sampling = []
    const middle = Math.ceil(len / 2)
    sampling.push(data[0])
    sampling.push(data[Math.ceil((middle) / 2)])
    sampling.push(data[middle])
    sampling.push(data[middle + Math.floor((len - middle) / 2)])
    sampling.push(data[len - 1])
    sampling = Array.from(new Set(sampling.filter(n => n !== undefined)))
    while (precision < 5) {
      // eslint-disable-next-line no-loop-func
      const samp =  sampling.reduce((pre, cur) => {
        pre[formattter(cur, precision).text] = 1
        return pre
      }, {})
      if (Object.keys(samp).length >= sampling.length) {
        return precision
      }
      precision += 1
    }
    return precision
  }

  handleSetThreholds(series: any) {
    let thresholdList = series.filter((set: any) => set?.thresholds?.length).map((set: any) => set.thresholds)
    thresholdList  = thresholdList.reduce((pre: any, cur: any, index: number) => {
      pre.push(...cur.map((set: any) => set.yAxis))
      if (index === thresholdList.length - 1) {
        return Array.from(new Set(pre))
      }
      return pre
    }, [])
    return {
      canScale: thresholdList.every((set: number) => set > 0),
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
