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
  <div class="monitor-echart-wrap"
       :style="{ 'background-image': backgroundUrl }">
    <div class="echart-header" v-if="chartTitle || $slots.title">
      <slot name="title">
        <div class="header-title">{{chartTitle}}{{chartUnit ? `（${chartUnit}）` : ''}}</div>
      </slot>
      <div class="header-tools" v-if="!!chart && !noData">
        <slot name="tools">
          <i v-if="false" class="icon-monitor icon-mc-mark tools-icon"></i>
        </slot>
      </div>
    </div>
    <div class="chart-wrapper"
         ref="charWrapRef"
         :style="{ flexDirection: !showExtremum ? 'column' : 'row', minHeight: (height - (chartTitle ? 36 : 0)) + 'px', maxHeight: (height - (chartTitle ? 36 : 0)) + 'px' }"
         @dblclick="handleChartDblClick"
         @click="handleChartClick">
      <div class="echart-instance" ref="chartRef" :style="{ minHeight: chartHeight + 'px', maxHeight: chartHeight + 'px' }" />
      <div class="echart-legend" :style="{ maxHeight: ( showExtremum ? height - (chartTitle ? 36 : 0) - 5 : 30) + 'px', marginRight: showExtremum ? '20px' : '2px' }">
        <chart-legend
          v-if="legend.show"
          :legend-data="legend.list"
          :legend-type="showExtremum ? 'table' : 'common'"
          @legend-event="handleLegendEvent">
        </chart-legend>
      </div>
      <div v-if="chartType === 'pie'" class="echart-pie-center">
        <slot name="chartCenter"></slot>
      </div>
    </div>
    <div class="echart-content" v-if="setNoData" v-show="noData">
      <slot name="noData">
        {{emptyText}}
      </slot>
    </div>
  </div>
</template>
<script lang="ts">
import Echarts, { EChartOption, ECharts } from 'echarts'
import deepMerge from 'deepmerge'
import { debounce } from 'throttle-debounce'
import { addListener, removeListener, ResizeCallback } from 'resize-detector'
import { Vue, Prop, Ref, Component, Watch } from 'vue-property-decorator'
import moment from 'moment'
import ChartLegend from './components/chart-legend.vue'
import { ILegendItem } from './options/type-interface'
import EchartOptions from './options/echart-options'
interface IAnnotation {x: number; y: number; show: boolean; title: string; name: string; color: string }
interface ICurValue {
  xAxis: string | number; yAxis: string | number;
  dataIndex: number, color: string; name: string, seriesIndex: number}

@Component({
  name: 'monitor-mobile-echarts',
  components: {
    ChartLegend
  }
})
export default class MonitorMobileEcharts extends Vue {
  @Ref() readonly chartRef!: HTMLDivElement
  @Ref() readonly charWrapRef!: HTMLDivElement

  chart: Echarts.ECharts = null
  resizeHandler: ResizeCallback<HTMLDivElement>
  unwatchOptions: () => void
  unwatchSeries: () => void
  chartTitle = ''
  chartUnit = ''
  intersectionObserver: IntersectionObserver = null
  needObserver = true
  loading = false
  noData = false
  timeRange: string[] = []
  curValue: ICurValue = { xAxis: '', yAxis: '', dataIndex: -1, color: '', name: '', seriesIndex: -1 }
  refleshIntervalInstance = 0
  chartOptionInstance = null
  hasInitChart = false
  legend: {show: boolean; list: ILegendItem[]} = {
    show: false,
    list: []
  }
  // echarts配置项
  @Prop()  readonly options: Echarts.EChartOption
  // echarts配置项是否深度监听
  @Prop({ default: true }) readonly watchOptionsDeep: boolean
  // 是否自动resize
  @Prop({ default: true }) readonly autoresize: boolean
  // 是使用组件内的无数据设置
  @Prop({ default: true }) readonly setNoData: boolean
  // 是否显示极值
  @Prop({ default: false }) readonly showExtremum: boolean
  // 图表刷新间隔
  @Prop({ default: 0 }) readonly refleshInterval: number
  // 图表类型
  @Prop({ default: 'line' }) readonly chartType: 'line' | 'bar'
  // 图表title
  @Prop({ default: '' }) readonly title: string
  // 图表单位
  @Prop({ default: '' }) readonly unit: string

  @Prop({ default: false }) readonly showLegend: boolean
  // 图表系列数据
  @Prop() readonly series: EChartOption.SeriesLine | EChartOption.SeriesBar

  // 背景图
  @Prop({
    type: String,
    default() {
      return `url('${(window as any).site_url}api/signature.png')`
    }
  })
  backgroundUrl: String

  // 获取图标数据
  @Prop() getSeriesData: (timeFrom?: string, timeTo?: string, range?: boolean) => Promise<void>

  @Prop({
    default: () => ['#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80', '#8d98b3',
      '#e5cf0d', '#97b552', '#95706d', '#dc69aa', '#07a2a4', '#9a7fd1', '#588dd5',
      '#f5994e', '#c05050', '#59678c', '#c9ab00', '#7eb00a', '#6f5553', '#c14089']
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
  @Prop({ default: 310 }) height: number | string

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
          formatter: this.handleSetTooltip
        }
      }
    }
    return {}
  }

  get chartHeight() {
    let { height } = this
    if (this.chartTitle) {
      height -= 36
    }
    if (!this.showExtremum && this.legend.show) {
      height -= 30
    }
    return height
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
      this.handleSeriesData()
    }, this.refleshInterval)
  }
  @Watch('series')
  onSeriesChange(v) {
    this.handleSetChartData(deepMerge({}, { series: v }))
  }

  mounted() {
    if (this.series) {
      this.initChart()
      this.handleSetChartData(deepMerge({}, { series: this.series }))
    } else if (this.options && this.options.series && this.options.series.length) {
      this.initChart()
      this.handleSetChartData(deepMerge({}, this.options))
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
    this.refleshIntervalInstance && window.clearInterval(this.refleshIntervalInstance)
  }
  destroyed() {
    this.chart && this.destroy()
  }
  initChart() {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const echarts = require('echarts')
    const chart: any = echarts.init(this.chartRef)
    // chart.setOption({}, true)
    this.chartTitle = this.title
    this.chart = chart
    this.chartUnit = this.unit
    if (this.autoresize) {
      const handler = debounce(300, false, () => this.resize())
      this.resizeHandler = async () => {
        await this.$nextTick()
        this.chartRef && this.chartRef.offsetParent !== null && handler()
      }
      addListener(this.chartRef, this.resizeHandler)
    }
    this.initPropsWatcher()
  }
  // 注册Intersection监听
  registerObserver(): void {
    this.intersectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (this.needObserver) {
          if (entry.intersectionRatio > 0) {
            this.handleSeriesData()
          } else {
            // 解决临界点、慢滑不加载数据问题
            const { top, bottom } = this.$el.getBoundingClientRect()
            if (top === 0 && bottom === 0) return
            const { innerHeight } = window
            const isVisiable = (top > 0 && top <= innerHeight) || (bottom >= 0 && bottom < innerHeight)
            isVisiable && this.handleSeriesData()
          }
        }
      })
    })
  }

  // 获取seriesData
  async handleSeriesData(startTime?: string, endTime?: string) {
    this.loading = true
    this.intersectionObserver && this.intersectionObserver.unobserve(this.$el)
    this.intersectionObserver && this.intersectionObserver.disconnect()
    this.needObserver = false
    try {
      const isRange = (startTime && startTime.length > 0) && (endTime && endTime.length > 0)
      const data = await this.getSeriesData(startTime, endTime, isRange).catch(() => ({}))
      if (data && Object.keys(data).length) {
        await this.handleSetChartData(data)
      } else {
        this.noData = true
      }
    } catch (e) {
      console.info(e)
      this.noData = true
    } finally {
      this.loading = false
    }
  }

  // 设置chart配置
  async handleSetChartData(data) {
    return new Promise((resolve) => {
      if (!this.chart) {
        this.initChart()
      }
      const { unit, title, series } = data || {}
      title && !this.title && (this.chartTitle = title.text)
      this.chartUnit = unit || this.unit || ''
      const hasSeries = series && series.length > 0 && series.some(item => item.data && item.data.length)
      this.chartOptionInstance = new EchartOptions({
        chartType: this.chartType,
        colors: this.colors,
        showExtremum: this.showExtremum,
        chartOption: this.options })
      const optionData = this.chartOptionInstance.getOptions(data, {})
      if (['bar', 'line'].includes(this.chartType)) {
        this.legend.show = this.showLegend && hasSeries && optionData.legendData.length > 0
      } else {
        // eslint-disable-next-line no-nested-ternary
        this.legend.show = optionData.options.lengend
          ? (Object.prototype.hasOwnProperty.call(optionData.options.lengend, 'show')
            ? optionData.options.lengend.show
            :  true)
          : false
      }
      this.legend.list = optionData.legendData || []
      if (this.options && this.options.grid) {
        optionData.options.grid.bottom = (this.options.grid as EChartOption.Grid).bottom
      }
      setTimeout(() => {
        this.chart.setOption(deepMerge(optionData.options, this.defaultOptions) as EChartOption, {
          notMerge: false,
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
                const timeFrom = moment(+batch.startValue.toFixed(0)).format('YYYY-MM-DD HH:mm')
                const timeTo = moment(+batch.endValue.toFixed(0)).format('YYYY-MM-DD HH:mm')
                this.timeRange = [timeFrom, timeTo]
                if (this.getSeriesData) {
                  this.chart.dispatchAction({
                    type: 'restore'
                  })
                  await this.handleSeriesData(timeFrom, timeTo)
                }
              }
              this.loading = false
            })
          }
          this.initChartEvent()
        }
        this.noData = !hasSeries
        resolve()
      }, 320)
    })
  }

  // 设置tooltip
  handleSetTooltip(params) {
    if (!params || params.length < 1 || params.every(item => item.value[1] === null)) {
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
    const data = params.map(item => ({ color: item.color, seriesName: item.seriesName, value: item.value[1] }))
      .sort((a, b) => Math.abs(a.value - (+this.curValue.yAxis)) - Math.abs(b.value - (+this.curValue.yAxis)))

    const liHtmls = params.map((item) => {
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
      if (item.value[1] === null) return ''
      return `<li style="display: flex;align-items: center;">
                <span
                 style="background-color:${item.color};margin-right: 10px;width: 6px;height: 6px; border-radius: 50%;">
                </span>
                <span style="${markColor}">${item.seriesName}:</span>
                <span style="${markColor} flex: 1;margin-left: 5px;">
                ${item.value[1]}${this.chartUnit || this.unit}</span>
                </li>`
    })
    return `<div style="z-index:12; border-radius: 6px">
            <p style="text-align:center;margin: 0 0 5px 0;font-weight: bold;">
                ${pointTime}
            </p>
            <ul style="padding: 0;margin: 0;">
                ${liHtmls.join('')}
            </ul>
            </div>`
  }

  // 双击触发重置选择数据
  handleChartDblClick() {
    if (this.timeRange.length > 0) {
      this.timeRange = []
      this.chart.dispatchAction({
        type: 'restore'
      })
      this.getSeriesData && setTimeout(() => {
        this.handleSeriesData()
      }, 100)
    }
    this.$emit('dblclick')
  }

  // 单击图表触发
  handleChartClick() {
    this.$emit('click')
  }

  handleLegendEvent({ actionType, item }: {actionType: string; item: ILegendItem}) {
    if (['highlight', 'downplay'].includes(actionType)) {
      this.chart.dispatchAction({
        type: actionType,
        seriesName: item.name
      })
    } else if (actionType === 'shift-click') {
      this.chart.dispatchAction({
        type: actionType,
        name: item.name
      })
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
      () => {
        if (this.getSeriesData) {
          this.handleSeriesData()
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
    background-position: center;
    background-size: contain;
    background-color: #fff;
    border-radius: 2px;
    width: 100%;
    height: 100%;
    color: #63656e;

    .echart-header {
      display: flex;
      align-items: center;
      height: 36px;
      min-width: 100%;
      padding-left: 16px;
      color: #63656e;
      font-weight: 700;

      .header-title {
        font-weight: 700;
        flex: 1;
      }

      .header-tools {
        margin-left: auto;
        display: flex;
        align-items: center;
        min-height: 36px;
        font-size: 16px;
        margin-right: 10px;
        color: #979ba5;
        font-weight: normal;

        .tools-icon {
          margin-right: 8px;

          &:hover {
            cursor: pointer;
            color: #3a84ff;
          }
        }
      }
    }

    .chart-wrapper {
      position: relative;
      display: flex;

      .echart-instance {
        min-width: 100px;
        height: 310px;
        flex: 1;
      }

      .echart-annotation {
        position: absolute;
        height: 156px;
        width: 220px;
        background: white;
        border-radius: 2px;
        box-shadow: 0px 4px 12px 0px rgba(0,0,0,.2);
        z-index: 99;
        font-size: 12px;
        color: #63656e;

        &-title {
          margin: 6px 0 0 16px;
          line-height: 20px;
        }

        &-name {
          margin-top: 2px;
          padding-left: 18px;
          height: 20px;
          display: flex;
          align-items: center;
          font-weight: 700;
          border-bottom: 1px solid #f0f1f5;

          .name-mark {
            flex: 0 0 12px;
            height: 4px;
            margin-right: 10px;
          }
        }

        &-list {
          display: flex;
          flex-direction: column;

          .list-item {
            flex: 0 0 30px;
            display: flex;
            align-items: center;
            padding-left: 18px;

            .item-icon {
              font-size: 14px;
              margin-right: 10px;
            }

            &:hover {
              background-color: #e1ecff;
              cursor: pointer;
              color: #3a84ff;
            }
          }
        }
      }

      .echart-legend {
        margin-right: 20px;
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
