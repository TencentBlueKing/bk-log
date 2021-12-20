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
