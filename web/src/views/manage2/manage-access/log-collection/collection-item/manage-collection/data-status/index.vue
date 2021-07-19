<template>
  <div class="data-status-container">
    <section class="partial-content">
      <div class="main-title">
        {{ $t('数据趋势') }}
      </div>
      <div class="charts-container">
        <MinuteChart />
        <DailyChart />
      </div>
    </section>
    <section class="partial-content">
      <div class="main-title">
        {{ $t('数据采样') }}
        <div class="refresh-button" @click="fetchDataSampling">
          <span class="bk-icon icon-refresh"></span>
          <span>{{ $t('刷新') }}</span>
        </div>
      </div>
      <DataSampling :data="dataSamplingList" :loading="dataSamplingLoading" />
    </section>
  </div>
</template>

<script>
import DataSampling from './DataSampling';
import MinuteChart from './MinuteChart';
import DailyChart from './DailyChart';

export default {
  components: {
    DataSampling,
    MinuteChart,
    DailyChart,
  },
  data() {
    return {
      dataSamplingLoading: true,
      dataSamplingList: [],
    };
  },
  created() {
    this.fetchDataSampling();
  },
  methods: {
    // 数据采样
    async fetchDataSampling() {
      try {
        this.dataSamplingLoading = true;
        const dataSamplingRes = await this.$http.request('source/dataList', {
          params: {
            collector_config_id: this.$route.params.collectorId,
          },
        });
        this.dataSamplingList = dataSamplingRes.data;
      } catch (e) {
        console.warn(e);
        this.dataSamplingList = [];
      } finally {
        this.dataSamplingLoading = false;
      }
    },
  },
};
</script>
