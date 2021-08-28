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

import moment from 'moment'
import { IChartOptionPorps, ChartType } from './type-interface'
export default class EchartsSeries {
  public  lineWidth = 1
  public chartType: ChartType
  public colors: string[] = []
  public showExtremum = false
  public chartOption = {}
  public constructor({ chartType, colors, showExtremum, chartOption, lineWidth }: IChartOptionPorps) {
    this.chartType = chartType
    this.colors = colors
    this.showExtremum = showExtremum
    this.chartOption = chartOption || {}
    this.lineWidth = lineWidth || 1
  }
  // 设置x轴label formatter方法
  public handleSetFormatterFunc(seriesData: any) {
    let formatterFunc = null
    const minX = Array.isArray(seriesData[0]) ? seriesData[0][0] : seriesData[0].x
    const [maxX] = seriesData[seriesData.length - 1]
    minX && maxX && (formatterFunc = (v: any) => {
      // 用绝对值兼容倒叙的情况
      const duration = Math.abs(moment.duration(moment(maxX).diff(moment(minX))).asSeconds())
      if (duration < 60 * 60 * 24) {
        return moment(v).format('HH:mm:ss')
          .replace(/:00$/, '')
      } if (duration < 60 * 60 * 24 * 2) {
        return moment(v).format('HH:mm')
      } if (duration < 60 * 60 * 24 * 8) {
        return moment(v).format('MM-DD HH:mm')
      } if (duration <= 60 * 60 * 24 * 30 * 12) {
        return moment(v).format('MM-DD')
      }
      return moment(v).format('YYYY-MM-DD')
    })
    return formatterFunc
  }
  public overwriteMerge(destinationArray: any, sourceArray: any) {
    return sourceArray
  }
  public handleYxisLabelFormatter(num: number): string {
    const si = [
      { value: 1, symbol: '' },
      { value: 1E3, symbol: 'K' },
      { value: 1E6, symbol: 'M' },
      { value: 1E9, symbol: 'G' },
      { value: 1E12, symbol: 'T' },
      { value: 1E15, symbol: 'P' },
      { value: 1E18, symbol: 'E' }
    ]
    const rx = /\.0+$|(\.[0-9]*[1-9])0+$/
    let i
    for (i = si.length - 1; i > 0; i--) {
      if (num >= si[i].value) {
        break
      }
    }
    return (num / si[i].value).toFixed(3).replace(rx, '$1') + si[i].symbol
  }
}
