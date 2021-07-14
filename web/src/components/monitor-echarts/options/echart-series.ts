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

import { ILegendItem, ChartType } from './type-interface'
export default class EchartsSeries {
  public chartType: Partial<ChartType>
  public series = []
  public colors = []
  public constructor(chartType: ChartType, seriesData = [], colors = []) {
    this.chartType = chartType
    this.series = seriesData
    this.colors = colors
  }

  public getSeriesOption(plotBands = [], thresholdLine = []) {
    const hasPlotBand = Array.isArray(plotBands) && plotBands.length > 0
    const legendData: ILegendItem[] = []
    const series = this.series.map((item: any, index) => {
      let showSymbol = hasPlotBand
      const legendItem: ILegendItem = {
        name: String(item.name),
        max: 0,
        min: 0,
        avg: 0,
        total: 0,
        color: this.colors[index % this.colors.length],
        show: true
      }
      item.data.forEach((seriesItem: any, seriesIndex: number) => {
        if (seriesItem?.length && seriesItem[1]) {
          const pre = item.data[seriesIndex - 1]
          const next = item.data[seriesIndex + 1]
          const curValue = +seriesItem[1]
          legendItem.max = Math.max(legendItem.max, curValue)
          legendItem.min = Math.min(+legendItem.min, curValue)
          legendItem.total = (legendItem.total + curValue)
          if (hasPlotBand && plotBands.some((set: any) => set.from === seriesItem[0])) {
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
            const hasBrother = pre && next && pre.length && next.length && !pre[1] && !next[1]
            item.data[seriesIndex] = {
              symbolSize: hasBrother ? 4 : 1,
              value: [seriesItem[0], seriesItem[1]],
              itemStyle: {
                borderWidth: hasBrother ? 4 : 1,
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
        smooth: 0.2
      }
      if (thresholdLine?.length) {
        seriesItem.markLine = this.handleSetThresholdLine(thresholdLine)
      }
      if (plotBands?.length) {
        seriesItem.markArea = this.handleSetThresholdBand(plotBands)
      }
      legendData.push(legendItem)
      return seriesItem
    })
    return { legendData, series }
  }
  // 设置阈值线
  public handleSetThresholdLine(thresholdLine: {value: number, name: string}[]) {
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
      data: thresholdLine.map(item => ({
        name: item.name,
        yAxis: item.value
      }))
    }
  }
  // 设置阈值面板
  public handleSetThresholdBand(plotBands: {to: number, from: number}[]) {
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
          yAxis: 0
        }, {
          xAxis: item.to || 'max',
          yAxis: 'max' // this.delegateGet('getModel').getComponent('yAxis').axis.scale._extent[1]
        }]
      )),
      opacity: 0.1
    }
  }
}
