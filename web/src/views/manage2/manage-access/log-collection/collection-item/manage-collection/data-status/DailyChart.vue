<template>
  <div class="chart-container" v-bkloading="{ isLoading: basicLoading, zIndex: 0 }">
    <div class="chart-header">
      <div class="title">{{ $t('日数据量') }}</div>
      <div class="date-picker">
        <SelectDate
          is-daily
          :time-range.sync="retrieveParams.time_range"
          :date-picker-value="datePickerValue"
          @update:datePickerValue="handleDateChange"
          @datePickerChange="fetchChartData" />
        <div class="refresh-button" @click="fetchChartData">
          <span class="bk-icon icon-refresh"></span>
          <span>{{ $t('刷新') }}</span>
        </div>
      </div>
    </div>
    <div class="chart-canvas-container big-chart" ref="chartRef"></div>
    <bk-exception v-if="isEmpty" class="king-exception" type="empty" scene="part"></bk-exception>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import moment from 'moment';
import SelectDate from './SelectDate';
import { formatDate } from '@/common/util';
import { mapGetters } from 'vuex';

export default {
  components: {
    SelectDate,
  },
  data() {
    const currentTime = Date.now();
    const startTime = formatDate(currentTime - 7 * 86400000).slice(0, 10);
    const endTime = formatDate(currentTime).slice(0, 10);

    return {
      isEmpty: false,
      basicLoading: true,
      datePickerValue: [startTime, endTime], // 日期选择器
      retrieveParams: {
        bk_biz_id: this.$store.state.bkBizId,
        keyword: '*',
        time_range: 'custom',
        start_time: startTime, // 时间范围，格式 YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
        end_time: endTime,
        host_scopes: {
          modules: [],
          ips: '',
        },
        addition: [],
        begin: 0,
        size: 500,
        interval: '1d',
      },
    };
  },
  computed: {
    ...mapGetters('collect', ['curCollect']),
  },
  created() {
    this.fetchChartData();
  },
  mounted() {
    let timer = 0;
    this.resizeChart = () => {
      if (!timer) {
        timer = setTimeout(() => {
          timer = 0;
          if (this.instance && !this.instance.isDisposed()) {
            this.instance.resize();
          }
        }, 400);
      }
    };
    window.addEventListener('resize', this.resizeChart);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
  },
  methods: {
    // 获取数据
    async fetchChartData() {
      try {
        this.basicLoading = true;
        const res = await this.$http.request('retrieve/getLogChartList', {
          params: { index_set_id: this.curCollect.index_set_id },
          data: Object.assign({}, this.retrieveParams, {
            start_time: `${this.retrieveParams.start_time} 00:00:00`,
            end_time: `${this.retrieveParams.end_time} 23:59:59`,
          }),
        });
        const originChartData = res.data.aggs?.group_by_histogram?.buckets || [];
        const chartData = {
          labels: [],
          values: [],
        };
        originChartData.forEach((item) => {
          chartData.labels.push(item.key_as_string);
          chartData.values.push(item.doc_count);
        });
        this.updateChart(chartData);
      } catch (e) {
        console.warn(e);
        this.updateChart(null);
      } finally {
        this.basicLoading = false;
      }
    },
    // 初始化图表
    updateChart(chartData) {
      if (!chartData || !chartData.values.length) {
        if (this.instance && !this.instance.isDisposed()) {
          this.instance.dispose();
        }
        this.isEmpty = true;
        return;
      }

      this.isEmpty = false;
      if (!this.instance || this.instance.isDisposed()) {
        this.instance = echarts.init(this.$refs.chartRef);
      }

      this.instance.setOption({
        xAxis: {
          type: 'category',
          data: chartData.labels,
          axisTick: {
            alignWithLabel: true,
          },
          axisLabel: {
            align: 'center',
            formatter(value) {
              return moment(value).format('MM-DD');
            },
          },
          axisLine: {
            lineStyle: {
              color: '#DCDEE5',
            },
          },
        },
        yAxis: {
          type: 'value',
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          splitLine: {
            lineStyle: {
              color: '#DCDEE5',
              type: 'dashed',
            },
          },
        },
        series: [{
          data: chartData.values,
          type: 'bar',
          barMaxWidth: 24,
          itemStyle: {
            color: '#339DFF',
          },
        }],
        tooltip: {
          trigger: 'item',
        },
        textStyle: {
          color: '#63656E',
        },
        grid: {
          x: 40,
          y: 10,
          x2: 40,
          y2: 40,
        },
      });
    },

    // 检索参数：日期改变
    handleDateChange(val) {
      this.datePickerValue = val;
      Object.assign(this.retrieveParams, {
        start_time: val[0],
        end_time: val[1],
      });
    },
  },
};
</script>
