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

import { IChartInstance } from './type-interface'
import MonitorBaseSeries from './base-chart-option'
import deepMerge from 'deepmerge'
export default class MonitorPieSeries extends  MonitorBaseSeries implements IChartInstance {
  public defaultOption: any
  public defaultSeriesData: {name: string; value: number}[] = [{
    name: '北京',
    value: 0
  }, {
    name: '天津',
    value: 0
  }, {
    name: '上海',
    value: 0
  }, {
    name: '重庆',
    value: 0
  }, {
    name: '河北',
    value: 0
  }, {
    name: '河南',
    value: 0
  }, {
    name: '云南',
    value: 0
  }, {
    name: '辽宁',
    value: 0
  }, {
    name: '黑龙江',
    value: 0
  }, {
    name: '湖南',
    value: 0
  }, {
    name: '安徽',
    value: 0
  }, {
    name: '山东',
    value: 0
  }, {
    name: '新疆',
    value: 0
  }, {
    name: '江苏',
    value: 0
  }, {
    name: '浙江',
    value: 0
  }, {
    name: '江西',
    value: 0
  }, {
    name: '湖北',
    value: 0
  }, {
    name: '广西',
    value: 0
  }, {
    name: '甘肃',
    value: 0
  }, {
    name: '山西',
    value: 0
  }, {
    name: '内蒙古',
    value: 0
  }, {
    name: '陕西',
    value: 0
  }, {
    name: '吉林',
    value: 0
  }, {
    name: '福建',
    value: 0
  }, {
    name: '贵州',
    value: 0
  }, {
    name: '广东',
    value: 0
  }, {
    name: '青海',
    value: 0
  }, {
    name: '西藏',
    value: 0
  }, {
    name: '四川',
    value: 0
  }, {
    name: '宁夏',
    value: 0
  }, {
    name: '海南',
    value: 0
  }, {
    name: '台湾',
    value: 0
  }, {
    name: '香港',
    value: 0
  }, {
    name: '澳门',
    value: 0
  }]
  public constructor(props: any) {
    super(props)
    this.defaultOption = {}
  }
  public getOptions(data: any, otherOptions = {}) {
    const { series } = data || {}
    const hasSeries = series && series.length > 0
    const legendData: any[] = []
    const options =  {
      tooltip: {
        show: true,
        formatter: (params: any) => {
          if (params.value) {
            return `<div>
            <strong>${params.seriesName}</strong>
            <div>${params.value}</div>
            </div>`
          }
          return ''
        }
      },
      series: hasSeries ? series.map((item: any) => {
        const itemData = item.data || []
        const seriesData = this.defaultSeriesData.map((set) => {
          const matchItem = itemData.find((s: any) => s.name === set.name)
          if (matchItem) {
            return {
              ...set,
              ...matchItem
            }
          }
          return {
            ...set,
            itemStyle: {
              borderColor: '#c4c6cc',
              borderWidth: 1
            },
            emphasis: {
              itemStyle: {
                color: '#f7f7f7',
                areaColor: '#f7f7f7',
                borderColor: '#c4c6cc',
                borderWidth: 1
              }
            }
          }
        })
        return {
          ...item,
          type: 'map',
          mapType: 'china',
          roam: false,
          data: seriesData,
          right: 50
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
}
