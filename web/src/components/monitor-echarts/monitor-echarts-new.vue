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
  <div 
    class="monitor-echart-wrap"
    :style="{ 'background-image': backgroundUrl }"
    v-bkloading="{ isLoading: false, zIndex: 2000 }">
    <div v-show="!isFold">
      <div
        class="chart-wrapper"
        tabindex="-1"
        ref="charWrapRef"
        :style="{
          flexDirection: !(chartOption.legend.toTheRight) ? 'column' : 'row',
          minHeight: (height - (chartTitle ? 36 : 0)) + 'px',
          maxHeight: (height - (chartTitle ? 36 : 0)) + 'px' }"
        @blur="handleCharBlur">
        <div
          @dblclick.prevent="handleChartDblClick"
          @click.stop="handleChartClick"
          class="echart-instance"
          ref="chartRef"
          :style="{ height: (chartHeight - 10) + 'px' }">
          <status-chart
            v-if="chartType === 'status'"
            :series="statusSeries">
          </status-chart>
          <text-chart
            v-else-if="chartType === 'text'"
            :series="textSeries">
          </text-chart>
        </div>
        <div
          class="echart-legend"
          :style="{
            maxHeight: ( chartOption.legend.toTheRight ?
              height - (chartTitle ? 36 : 0) - 5 :
              chartOption.legend.maxHeight) + 'px' 
          }">
          <chart-legend
            v-if="legend.show"
            :legend-data="legend.list"
            :legend-type="chartOption.legend.asTable ? 'table' : 'common'"
            :to-the-right="chartOption.legend.toTheRight"
            @legend-event="handleLegendEvent">
          </chart-legend>
        </div>
        <div v-if="chartType === 'pie'" class="echart-pie-center">
          <slot name="chartCenter"></slot>
        </div>
        <chart-annotation
          v-if="chartOption.annotation.show"
          :annotation="annotation">
        </chart-annotation>
      </div>
      <div class="echart-content" v-if="setNoData" v-show="noData">
        <slot name="noData">
          {{emptyText}}
        </slot>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Echarts, { EChartOption } from 'echarts'
import deepMerge from 'deepmerge'
import { debounce } from 'throttle-debounce'
import { addListener, removeListener, ResizeCallback } from 'resize-detector'
import { Vue, Prop, Ref, Component, Watch } from 'vue-property-decorator'
import moment from 'moment'
import { toPng, toBlob } from 'html-to-image'
import ChartLegend from './components/chart-legend.vue'
import ChartTools from './components/chart-tools.vue'
import ChartAnnotation from './components/chart-annotation.vue'
import StatusChart from './components/status-chart.vue'
import TextChart from './components/text-chart.vue'
import { ILegendItem, IMoreToolItem, IAnnotation, IStatusSeries,
  IStatusChartOption, ITextSeries, ITextChartOption, ChartType } from './options/type-interface'
import EchartOptions from './options/echart-options'
import { hexToRgbA } from './utils'
import watermarkMaker from './utils/watermark-maker'
import ChartInView from './utils/chart-in-view'
import { getValueFormat } from './value-formats-package'
import ChartTitle from './components/chart-title-new.vue'
import { Debounce } from '../../components/ip-selector/common/util'
interface ICurValue {
  xAxis: string | number; yAxis: string | number;
  dataIndex: number, color: string; name: string, seriesIndex: number}
@Component({
  name: 'monitor-echarts',
  components: {
    ChartLegend,
    ChartTools,
    ChartAnnotation,
    StatusChart,
    TextChart,
    ChartTitle
  }
})
export default class MonitorEcharts extends Vue {
  @Ref() readonly chartRef!: HTMLDivElement
  @Ref() readonly charWrapRef!: HTMLDivElement

  // echarts配置项
  @Prop()  readonly options: Echarts.EChartOption | IStatusChartOption | ITextChartOption
  // echarts配置项是否深度监听
  @Prop({ default: true }) readonly watchOptionsDeep: boolean
  // 是否自动resize
  @Prop({ default: true }) readonly autoresize: boolean
  // 是否需要设置全屏
  @Prop({ default: true }) readonly needFullScreen: boolean
  // 是有fullscreen递归
  @Prop({ default: true }) readonly needChild: boolean
  // 是使用组件内的无数据设置
  @Prop({ default: true }) readonly setNoData: boolean
  // 图表刷新间隔
  @Prop({ default: 0 }) readonly refleshInterval: number
  // 图表类型
  @Prop({ default: 'line' }) readonly chartType: ChartType
  // 图表title
  @Prop({ default: '' }) readonly title: string
  @Prop({ default: '' }) readonly subtitle: string
  // 图表系列数据
  @Prop() readonly series: EChartOption.SeriesLine | EChartOption.SeriesBar | IStatusSeries | ITextSeries

  // 背景图
  @Prop({
    type: String,
    default() {
      return window.graph_watermark ? `url('${watermarkMaker(window.user_name || window.username)}')` : ''
    }
  })
  backgroundUrl: String

  // 获取图标数据
  @Prop() getSeriesData: (timeFrom?: string, timeTo?: string, range?: boolean) => Promise<void>

  @Prop({
    default: () => [
      '#A3C5FD', // 0: pale green
      '#EAB839', // 1: mustard
      '#6ED0E0', // 2: light blue
      '#EF843C', // 3: orange
      '#E24D42', // 4: red
      '#1F78C1', // 5: ocean
      '#BA43A9', // 6: purple
      '#705DA0', // 7: violet
      '#508642', // 8: dark green
      '#CCA300', // 9: dark sand
      '#447EBC',
      '#C15C17',
      '#890F02',
      '#0A437C',
      '#6D1F62',
      '#584477',
      '#B7DBAB',
      '#F4D598',
      '#70DBED',
      '#F9BA8F',
      '#F29191',
      '#82B5D8',
      '#E5A8E2',
      '#AEA2E0',
      '#629E51',
      '#E5AC0E',
      '#64B0C8',
      '#E0752D',
      '#BF1B00',
      '#0A50A1',
      '#962D82',
      '#614D93',
      '#9AC48A',
      '#F2C96D',
      '#65C5DB',
      '#F9934E',
      '#EA6460',
      '#5195CE',
      '#D683CE',
      '#806EB7',
      '#3F6833',
      '#967302',
      '#2F575E',
      '#99440A',
      '#58140C',
      '#052B51',
      '#511749',
      '#3F2B5B',
      '#E0F9D7',
      '#FCEACA',
      '#CFFAFF',
      '#F9E2D2',
      '#FCE2DE',
      '#BADFF4',
      '#F9D9F9',
      '#DEDAF7']
  })
  // 图标系列颜色集合
  colors: string[]

  @Prop({
    default() {
      return this.$tc('暂无数据')
    }
  })
  emptyText: string

  // 图表高度
  @Prop({ default: 165 }) height: number | string
  @Prop({ default: 1, type: Number }) lineWidth: number

  @Prop({ default: localStorage.getItem('chartIsFold') === 'true' }) isFold: boolean

  // chart: Echarts.ECharts = null
  resizeHandler: ResizeCallback<HTMLDivElement>
  unwatchOptions: () => void
  unwatchSeries: () => void
  chartTitle = ''
  chartSubTitle = ''
  intersectionObserver: IntersectionObserver = null
  needObserver = true
  loading = false
  noData = false
  isFullScreen = false
  timeRange: string[] = []
  childProps = {}
  annotation:  IAnnotation = { x: 0, y: 0, show: false, title: '', name: '', color: '', list: [] }
  curValue: ICurValue = { xAxis: '', yAxis: '', dataIndex: -1, color: '', name: '', seriesIndex: -1 }
  refleshIntervalInstance = 0
  chartOptionInstance = null
  hasInitChart = false
  legend: {show: boolean; list: ILegendItem[]} = {
    show: false,
    list: []
  }
  statusSeries: IStatusSeries[] = [] // status图表数据
  textSeries: ITextSeries = {} // status图表数据
  curChartOption: any
  chart = null
  clickTimer = null
  timer = null
  isFinish = true
  chartInView: ChartInView = null
  initStatus: Boolean = true
  chartData: any = []
  // 监控图表默认配置
  get defaultOptions() {
    if (['bar', 'line'].includes(this.chartType)) {
      return {
        tooltip: {
          axisPointer: {
            type: 'cross',
            axis: 'auto',
            label: {
              show: false,
              formatter: (params) => {
                if (this.chartType !== 'line') return
                if (params.axisDimension === 'y') {
                  this.curValue.yAxis = params.value
                } else {
                  this.curValue.xAxis = params.value
                  this.curValue.dataIndex = params.seriesData && params.seriesData.length
                    ? params.seriesData[0].dataIndex
                    : -1
                }
              }
            },
            crossStyle: {
              color: 'transparent',
              opacity: 0,
              width: 0
            }
          },
          appendToBody: true,
          formatter: this.handleSetTooltip,
          position: (pos, params, dom, rect, size) => {
            if (!this.chartInView || this.chartInView.chartInTop === undefined) {
              const domRect = this.$el.getBoundingClientRect()
              if (!this.chartInView) {
                this.chartInView = new ChartInView(domRect.y < 100, domRect.bottom + 20 >= window.innerHeight, domRect)
              } else {
                this.chartInView.setCharInView(domRect.y < 100, domRect.bottom + 20 >= window.innerHeight, domRect)
              }
            }
            const position = {}
            let isLeft = +(pos[0] + size.contentSize[0] < size.viewSize[0])
            const isBig = pos[1] > (size.viewSize[1] / 2)
            if (this.chartInView.chartInBottom || (!this.chartInView.chartInTop && isBig)) {
              isLeft = +(pos[0] + size.contentSize[0] + this.chartInView.rect.x < window.innerWidth - 30)
              position[['right', 'left'][isLeft]] = isLeft ? pos[0] + 20 : size.viewSize[0] - pos[0] + 20
              return {
                ...position,
                bottom: size.viewSize[1] - pos[1] + 20
              }
            }
            position[['right', 'left'][isLeft]] = isLeft ? pos[0] + 20 : size.viewSize[0] - pos[0] + 20
            return {
              ...position,
              bottom: pos[1] + -20
            }
          }
        }
      }
    }
    return {}
  }
  get chartOption(): any {
    return deepMerge({
      legend: {
        asTable: false, // 是否转换为table图例
        toTheRight: false, // 图例位置在右侧
        maxHeight: 30 // 图例最大高度 只对toTheRight为false有效
      },
      tool: {
        show: true, // 工具栏是否显示
        moreList: ['explore', 'set', 'strategy', 'area'], // 要显示的多工具栏的配置id 空数组则为不显示
        list: ['save', 'screenshot', 'fullscreen', 'explore', 'set', 'strategy', 'area']
      },
      annotation: {
        show: false, // 是否显示annotation
        list: ['ip', 'process', 'strategy'] // 要显示的anotation配置id 空数组则为不显示
      }
    }, this.options || {}, {
      arrayMerge: (destinationArray, sourceArray)  => sourceArray
    })
  }
  get chartHeight() {
    let { height } = this
    if (this.chartTitle) {
      height =  Number(height) - 36
    }
    if (!this.chartOption.legend.toTheRight && this.legend.show) {
      height =  Number(height) - this.chartOption.legend.maxHeight
    }
    return height
  }
  get isEchartsRender() {
    return !['status', 'text'].includes(this.chartType)
  }
  @Watch('loading')
  onLoadingChange(v) {
    this.$emit('chart-loading', this.loading)
  }
  @Watch('height')
  onHeightChange() {
    this.chart && this.chart.resize()
  }
  @Watch('refleshInterval', { immediate: true })
  onRefleshIntervalChange(v) {
    if (this.refleshIntervalInstance) {
      window.clearInterval(this.refleshIntervalInstance)
    }
    if (v <= 0 || !this.getSeriesData) return
    this.refleshIntervalInstance = window.setInterval(() => {
      this.chart && this.handleSeriesData()
    }, this.refleshInterval)
  }
  @Watch('series')
  onSeriesChange(v) {
    this.handleSetChartData(deepMerge({}, { series: v }))
  }

  mounted() {
    if (this.isFold) {
      this.chartTitle = this.title
    }
    this.init()
  }

  init() {
    if (this.series) {
      this.initChart()
      this.handleSetChartData(deepMerge({}, { series: this.series }))
    } else if (this.chartOption && this.chartOption.series && this.chartOption.series.length) {
      this.initChart()
      this.handleSetChartData(deepMerge({}, this.chartOption))
    }
    if (this.getSeriesData) {
      this.registerObserver()
      this.intersectionObserver.observe(this.$el)
    }
  }

  activated() {
    if (this.autoresize) {
      this.chart && this.chart.resize()
    }
  }
  beforeDestroy() {
    this.timeRange = []
    this.unwatchSeries && this.unwatchSeries()
    this.unwatchOptions && this.unwatchOptions()
    if (this.intersectionObserver) {
      this.intersectionObserver.unobserve(this.$el)
      this.intersectionObserver.disconnect()
    }
    this.annotation.show = false
    this.refleshIntervalInstance && window.clearInterval(this.refleshIntervalInstance)
    clearTimeout(this.timer)
    this.timer = null
  }
  destroyed() {
    this.chart && this.destroy()
  }
  initChart() {
    this.chartTitle = this.title
    this.chartSubTitle = this.subtitle
    if (this.isEchartsRender) {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const echarts = require('echarts')
      // if (this.chartType === 'map') {
      //   // eslint-disable-next-line @typescript-eslint/no-require-imports
      //   require('./map/china')
      // }
      if (this.chartRef) {
        const chart: any = echarts.init(this.chartRef)
        this.chart = chart
        if (this.autoresize) {
          const handler = debounce(300, false, () => this.resize())
          this.resizeHandler = async () => {
            await this.$nextTick()
            this.chartRef && this.chartRef.offsetParent !== null && handler()
          }
          addListener(this.chartRef, this.resizeHandler)
        }
      }
      // const chart: any = echarts.init(this.chartRef)
      // this.chart = chart
      // if (this.autoresize) {
      //   const handler = debounce(300, false, () => this.resize())
      //   this.resizeHandler = async () => {
      //     await this.$nextTick()
      //     this.chartRef && this.chartRef.offsetParent !== null && handler()
      //   }
      //   addListener(this.chartRef, this.resizeHandler)
      // }
    }
    this.initPropsWatcher()
  }
  // 注册Intersection监听
  registerObserver(): void {
    this.intersectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (this.needObserver) {
          // if (entry.intersectionRatio > 0) {
          //   this.handleSeriesData()
          // } else {
          //   // 解决临界点、慢滑不加载数据问题
          //   const { top, bottom } = this.$el.getBoundingClientRect()
          //   if (top === 0 && bottom === 0) return
          //   const { innerHeight } = window
          //   const isVisiable = (top > 0 && top <= innerHeight) || (bottom >= 0 && bottom < innerHeight)
          //   isVisiable && this.handleSeriesData()
          // }
          this.handleSeriesData()
        }
      })
    })
  }

  // 终止轮询
  handleCloseTimer() {
    if (this.timer) {
      this.isFinish = true
      clearTimeout(this.timer)
    }
  }

  handleChangeInterval() {
    this.isFinish = true
    clearTimeout(this.timer)
    this.timer = null
    setTimeout(() => {
      this.handleSeriesData()
    }, 500);
  }

  @Debounce(300)
  // 获取seriesData
  async handleSeriesData(startTime?: string, endTime?: string) {
    if (this.isFinish) this.loading = true

    this.intersectionObserver && this.intersectionObserver.unobserve(this.$el)
    this.intersectionObserver && this.intersectionObserver.disconnect()
    this.needObserver = false
    try {
      const isRange = (startTime && startTime.length > 0) && (endTime && endTime.length > 0)
      const data = await this.getSeriesData(startTime, endTime, isRange).catch(() => ({ series: [] }))
      this.isFinish = data ? data[0] && data[0].isFinish : true
      !this.chart && this.initChart()
      if (!this.isEchartsRender
      || (Array.isArray(data) && data.length && data.some(item => item))
      || (data && Object.prototype.hasOwnProperty.call(data, 'series') && data.series.length)) {
        // await this.handleSetChartData(data)
        this.chartData.splice(0, this.chartData.length, ...data);
        if (!this.isFold) this.handleSetChartData(this.chartData)
      } else if (this.isFinish){
        this.noData = true
      }
    } catch (e) {
      console.info(e)
      // this.noData = true
    } finally {
      this.chartTitle = this.title
      this.chartSubTitle = this.subtitle
      this.loading = false
      
      if (this.isFinish) {
        clearTimeout(this.timer)
        return
      }
      this.timer = setTimeout(async () => {
        this.handleSeriesData()
      }, 500);
    }
  }
  handleTransformSeries(data) {
    if (data?.series) {
      return data
    }
    const mapData = {}
    return {
      series: data.map(({ datapoints, target, ...item }) => {
        const formatDataOpt = datapoints.map(data => {
          if (data.indexOf(0) > -1) {
            const res = data
            res.splice(data.indexOf(0), 1, null)
            return res
          }
          return data
        })
        mapData[target] !== undefined ? (mapData[target] += 1) : (mapData[target] = 0)
        return { ...item,
          data: formatDataOpt.map(set => (Array.isArray(set) ? set.slice().reverse() : [])),
          name: !mapData[target] ? target : target + mapData[target]
        }
      })
    }
  }
  // 设置chart配置
  async handleSetChartData(data) {
    return new Promise((resolve) => {
      if (!this.chart) {
        this.initChart()
      }
      if (this.isEchartsRender) {
        const series: any = deepMerge([], data || [])
        const hasSeries = (series && series.length > 0
        && series.some(item => (item.datapoints && item.datapoints.length)))
        || (series && Object.prototype.hasOwnProperty.call(series, 'series') && series.series.length)
        this.chartOptionInstance = new EchartOptions({
          lineWidth: this.lineWidth,
          chartType: this.chartType,
          colors: this.colors,
          showExtremum: this.chartOption.legend.asTable,
          chartOption: this.chartOption })
        const optionData = this.chartOptionInstance.getOptions(this.handleTransformSeries(series), {})   
        optionData.options.xAxis.axisLine.show = false;
        optionData.options.xAxis.axisTick.show = false;
        optionData.options.yAxis.axisLine.show = false;
        if (['bar', 'line'].includes(this.chartType)) {
          this.legend.show = hasSeries && optionData.legendData.length > 0
        } else {
          // eslint-disable-next-line no-nested-ternary
          this.legend.show = optionData.options.lengend
            ? (Object.prototype.hasOwnProperty.call(optionData.options.lengend, 'show')
              ? optionData.options.lengend.show
              :  true)
            : false
        }
        this.legend.list = optionData.legendData || []
        this.legend.list = []
        this.legend.show = false
        if (this.chartOption.grid) {
          optionData.options.grid.bottom = (this.chartOption.grid as EChartOption.Grid).bottom
        }
        setTimeout(() => {
          if (this.chart) {
            const optSeries = optionData.options.series
            const optData = optSeries[0] ? optSeries[0].data : []
            const isEmptyData = optData.every(val => val.includes(null))

            if (isEmptyData) optionData.options.yAxis.max = 1
            
            this.chart.setOption(deepMerge(optionData.options, this.defaultOptions) as EChartOption, {
              notMerge: true,
              lazyUpdate: false,
              silent: false
            })
            if (!this.hasInitChart) {
              this.hasInitChart = true
              if (optionData.options.toolbox) {
                this.initChartAction()
                this.chart.on('dataZoom', async (event) => {
                  this.loading = true
                  const [batch] = event.batch
                  if (batch.startValue && batch.endValue) {
                    const timeFrom = moment(+batch.startValue.toFixed(0)).format('YYYY-MM-DD HH:mm:ss')
                    const timeTo = moment(+batch.endValue.toFixed(0)).format('YYYY-MM-DD HH:mm:ss')
                    this.timeRange = [timeFrom, timeTo]
                    if (this.getSeriesData) {
                      this.chart.dispatchAction({
                        type: 'restore'
                      })
                      this.handleCloseTimer()
                      await this.handleSeriesData(timeFrom, timeTo)
                    }
                    this.$emit('data-zoom', this.timeRange)
                  }
                  this.loading = false
                })
              }
              this.initChartEvent()
            }
            this.noData = !hasSeries
            resolve()
            this.curChartOption = Object.freeze(Object.assign({}, this.chart.getOption()))
          }
        }, 320)
      } else if (this.chartType === 'status') {
        this.statusSeries = data || []
        this.curChartOption = {}
        resolve()
      } else if (this.chartType === 'text') {
        const setData = Array.isArray(data) ? data[0] : data
        const value = (setData?.datapoints || []).reduce((pre, cur) => {
          if (pre === '') {
            return typeof cur[0] === 'number' ? cur[0] : ''
          }
          return  typeof cur[0] === 'number' ? Math.max(pre, cur[0]) : pre
        }, '')
        const formater = getValueFormat(setData?.unit || '')(+value)
        this.textSeries = {
          value: +formater.text || '',
          unit: formater.suffix
        }
        this.curChartOption = {}
        resolve()
      }
    })
  }

  // 设置tooltip
  handleSetTooltip(params) {
    // if (!params || params.length < 1 || params.every(item => item.value[1] === null)) {
    if (!params || params.length < 1) {
      this.chartType === 'line' && (this.curValue = {
        color: '',
        name: '',
        seriesIndex: -1,
        dataIndex: -1,
        xAxis: '',
        yAxis: ''
      })
      return
    }
    const pointTime = moment(params[0].axisValue).format('YYYY-MM-DD HH:mm:ss')
    const data = params.map(item => {
      const value = item.value[1] === null ? 0 : item.value[1]
      return ({ color: item.color, seriesName: item.seriesName, value: value })
    })
      .sort((a, b) => Math.abs(a.value - (+this.curValue.yAxis)) - Math.abs(b.value - (+this.curValue.yAxis)))
    const liHtmls = params.slice().sort((a, b) => b.value[1] - a.value[1])
      .map((item) => {
        let markColor = 'color: \'#fafbfd\';'
        if (data[0].value === item.value[1]) {
          markColor = 'color: \'#ffffff\';font-weight: bold;'
          this.chartType === 'line' && (this.curValue = {
            color: item.color,
            name: item.seriesName,
            seriesIndex: item.seriesIndex,
            dataIndex: item.dataIndex,
            xAxis: item.value[0],
            yAxis: item.value[1]
          })
        }
        // if (item.value[1] === null) return ''
        const curSeries = this.curChartOption.series[item.seriesIndex]
        const unitFormater = curSeries.unitFormatter || (v => ({ text: v }))
        const precision = curSeries.unit !== 'none' && +curSeries?.precision < 1 ?  2 : +curSeries?.precision
        const valueObj = unitFormater(item.value[1] === null ? 0 : item.value[1], precision)
        return `<li style="display: flex;align-items: center;">
           <span style="background-color:${item.color};margin-right: 4px;width: 6px;height: 6px; border-radius: 50%;"></span>
           <span style="${markColor} flex: 1;">${valueObj.text} ${valueObj.suffix || ''}</span>
          </li>`
      })
    return `<div style="z-index:12; border-radius: 6px">
        <p style="text-align:center;margin: 0 0 5px 0;font-weight: bold;">${pointTime}</p>
        <ul style="padding: 0;margin: 0;">${liHtmls.join('')}</ul>
      </div>`
  }

  // 双击触发重置选择数据
  handleChartDblClick() {
    clearTimeout(this.clickTimer)
    if (this.timeRange.length > 0) {
      this.timeRange = []
      this.chart.dispatchAction({
        type: 'restore'
      })
      // this.getSeriesData && setTimeout(() => {
      //   this.handleSeriesData()
      // }, 100)
    }
    this.$emit('dblclick')
  }

  // 单击图表触发
  handleChartClick() {
    clearTimeout(this.clickTimer)
    this.clickTimer = setTimeout(() => {
      this.$emit('click')
      if (!this.chartOption.annotation.show) {
        return
      }
      if (this.chartType === 'line' && this.chart && this.curValue.dataIndex >= 0) {
        const { series } = this.chart.getOption() as any
        if (series?.length) {
          const setPixel = this.chart.convertToPixel(
            { seriesIndex: this.curValue.seriesIndex },
            [this.curValue.xAxis, this.curValue.yAxis]
          )
          const { dimensions = {}, metric = {} } = series[this.curValue.seriesIndex]
          const { annotation } = this.chartOption
          const chartWidth = this.chart.getWidth()
          this.annotation = {
            x: setPixel[0] + 10 + 220 > chartWidth ? setPixel[0] - 10 - 220 : setPixel[0] + 10,
            y: setPixel[1] + 5,
            title: moment(this.curValue.xAxis).format('YYYY-MM-DD HH:mm:ss'),
            name: this.curValue.name,
            color: this.curValue.color,
            show: true,
            list: [
              {
                id: 'ip',
                show: annotation.list.includes('ip') && !!dimensions.bk_target_ip,
                value: `${dimensions.bk_target_ip}${dimensions.bk_target_cloud_id
                  ? `-${dimensions.bk_target_cloud_id}`
                  : ''}`
              },
              {
                id: 'process',
                show: annotation.list.includes('process') && (!!dimensions.process_name || !!dimensions.display_name),
                value: {
                  processId: dimensions.process_name || dimensions.display_name || '',
                  id: `${dimensions.bk_target_ip}-${dimensions.bk_target_cloud_id}`
                }
              },
              {
                id: 'strategy',
                show: annotation.list.includes('strategy') && !!metric.metric_field,
                value: `${metric.result_table_id}.${metric.metric_field}`
              }
            ]
          }
          this.charWrapRef.focus()
          this.chart.dispatchAction({ type: 'hideTip' })
        }
      } else {
        this.annotation.show = false
      }
    }, 300)
  }
  // 点击更多工具栏触发
  handleMoreToolItemSet(item: IMoreToolItem) {
    switch (item.id) {
      case 'save':
        this.handleCollectChart()
        break
      case 'screenshot':
        this.handleStoreImage()
        break
      case 'fullscreen':
        this.handleFullScreen()
        break
      case 'area':
        this.handleTransformArea(item.checked)
        break
      case 'set':
        this.handleSetYAxisSetScale(!item.checked)
        break
      case 'explore':
        this.handleExplore()
        break
      case 'strategy':
        this.handleAddStrategy()
        break
      default:
        break
    }
  }
  // 图表的展开收起
  handleToggleExpand (isShow) {
    if (!isShow && this.initStatus) {
      this.initStatus = false
      this.handleSetChartData(this.chartData)
    }
  }
  handleSetYAxisSetScale(needScale) {
    this.$emit('on-yaxis-set-scale', needScale)
    if (this.chartType === 'line' && this.chart) {
      const options = this.chart.getOption()
      this.chart.setOption({
        ...options,
        yAxis: {
          scale: needScale,
          min: needScale ? 'dataMin' : 0
        }
      })
    }
  }
  handleTransformArea(isArea: boolean) {
    this.$emit('on-transform-area', isArea)
    if (this.chartType === 'line' && this.chart) {
      const options = this.chart.getOption()
      this.chart.setOption({
        ...options,
        series: options.series.map((item, index) => ({
          ...item,
          areaStyle: {
            color: isArea ? hexToRgbA(this.colors[index % this.colors.length], 0.2) : 'transparent'
          }
        }))
      })
    }
  }
  handleExplore() {
    this.$emit('export-data-retrieval')
  }
  handleAddStrategy() {
    this.$emit('add-strategy')
  }
  handleCharBlur() {
    this.annotation.show = false
  }

  handleLegendEvent({ actionType, item }: {actionType: string; item: ILegendItem}) {
    if (this.legend.list.length < 2) {
      return
    }
    if (actionType === 'shift-click') {
      this.chart.dispatchAction({
        type: !item.show  ? 'legendSelect' : 'legendUnSelect',
        name: item.name
      })
      item.show = !item.show
    } else if (actionType === 'click') {
      const hasOtherShow = this.legend.list.some(set => set.name !== item.name && set.show)
      this.legend.list.forEach((legend) => {
        this.chart.dispatchAction({
          type: legend.name === item.name || !hasOtherShow ? 'legendSelect' : 'legendUnSelect',
          name: legend.name
        })
        legend.show = legend.name === item.name || !hasOtherShow
      })
    }
  }

  // 下载图表为png图片
  handleStoreImage() {
    if (window.navigator.msSaveOrOpenBlob) {
      toBlob(this.$el as HTMLDivElement).then(blob => window.navigator.msSaveOrOpenBlob(blob, `${this.title}.png`))
        .catch(() => {})
    } else {
      toPng(this.$el as HTMLDivElement).then((dataUrl) => {
        const tagA = document.createElement('a')
        tagA.download = `${this.title}.png`
        tagA.href = dataUrl
        document.body.appendChild(tagA)
        tagA.click()
        tagA.remove()
      })
        .catch(() => {})
    }
  }

  handleCollectChart() {
    this.$emit('collect-chart')
  }

  // 设置全屏
  handleFullScreen() {
    this.$emit('full-screen')
  }

  // resize
  resize(options: EChartOption = null) {
    this.chartRef && this.delegateMethod('resize', options)
  }

  dispatchAction(payload) {
    this.delegateMethod('dispatchAction', payload)
  }

  delegateMethod(name: string, ...args) {
    return this.chart[name](...args)
  }

  delegateGet(methodName: string) {
    return this.chart[methodName]()
  }

  // 初始化Props监听
  initPropsWatcher() {
    this.unwatchOptions = this.$watch(
      'options',
      (v, ov) => {
        if (this.getSeriesData) {
          const newV = Object.assign({}, v, { tool: 0, legend: 0, annotation: 0 })
          const oldV = Object.assign({}, ov, { tool: 0, legend: 0, annotation: 0 })
          JSON.stringify(newV) !== JSON.stringify(oldV) && this.handleSeriesData()
        } else {
          this.handleSetChartData(deepMerge({}, { series: this.series }))
        }
      }, { deep: !this.watchOptionsDeep }
    )
  }

  // 初始化chart事件
  initChartEvent() {
    this.chart.on('click', (e) => {
      this.$emit('chart-click', e)
    })
  }

  // 初始化chart Action
  initChartAction() {
    this.dispatchAction({
      type: 'takeGlobalCursor',
      key: 'dataZoomSelect',
      dataZoomSelectActive: true
    })
  }

  // echarts 实例销毁
  destroy() {
    if (this.autoresize && this.chartRef) {
      removeListener(this.chartRef, this.resizeHandler)
    }
    this.delegateMethod('dispose')
    this.chart = null
  }
}
</script>

<style lang="scss" scoped>
  .monitor-echart-wrap {
    position: relative;
    background-repeat: repeat;
    background-position: top;
    background-color: #fff;
    border-radius: 2px;
    width: 100%;
    height: 100%;
    color: #63656e;
    padding: 18px 24px 24px;

    .echart-header {
      display: flex;
      align-items: center;
      min-width: 100%;
      color: #63656e;
      font-weight: 700;
    }

    .chart-wrapper {
      position: relative;
      display: flex;

      .echart-instance {
        min-width: 100px;
        height: 260px;
        flex: 1;
        display: flex;
        overflow: hidden;
      }

      .echart-legend {
        margin-left: 16px;
        margin-top: 8px;
        overflow: auto;
      }

      .echart-pie-center {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate3d(-50%, -50%, 0);
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }

    .echart-content {
      position: absolute;
      left: 1px;
      right: 1px;
      top: 36px;
      bottom: 1px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0);
    }
  }
</style>
