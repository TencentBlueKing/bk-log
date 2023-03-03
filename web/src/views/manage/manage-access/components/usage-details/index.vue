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
  <div class="usage-details-container">
    <section class="partial-content">
      <div class="main-title">
        {{ $t('使用统计') }}
        <!-- :disabled="timesChartLoading || frequencyChartLoading || spentChartLoading" -->
        <time-range :value="chartDateValue" @change="handleDateValueChange" />
      </div>
      <div class="charts-container">
        <chart-component
          :type="$t('使用次数趋势')"
          :loading="timesChartLoading"
          :chart-data="timesChartData" />
        <chart-component
          :type="$t('用户使用频次')"
          :loading="frequencyChartLoading"
          :chart-data="frequencyChartData" />
        <chart-component
          :type="$t('检索耗时统计')"
          :loading="spentChartLoading"
          :chart-data="spentChartData" />
      </div>
    </section>

    <section class="partial-content">
      <div class="main-title">
        {{ $t('检索记录') }}
        <!-- :disabled="tableLoading" -->
        <time-range :value="tableDateValue" @change="handleTableDateValueChange" />
      </div>
      <bk-table
        v-bkloading="{ isLoading: tableLoading }"
        :max-height="526"
        :data="tableData"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange">
        <bk-table-column :label="$t('时间')" min-width="10">
          <template slot-scope="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('执行人')"
          prop="created_by"
          min-width="10"></bk-table-column>
        <bk-table-column :label="$t('查询语句')" min-width="20">
          <div class="table-ceil-container" slot-scope="{ row }">
            <span class="table-view-span-detail" v-bk-overflow-tips>{{ row.query_string }}</span>
          </div>
        </bk-table-column>
        <bk-table-column :label="$t('耗时(s)')" prop="duration" min-width="6">
          <template slot-scope="{ row }">
            {{ (row.duration / 1000).toFixed(3) }}
          </template>
        </bk-table-column>
        <div slot="empty">
          <empty-status empty-type="empty" />
        </div>
      </bk-table>
    </section>
  </div>
</template>

<script>
import { formatDate } from '@/common/util';
import ChartComponent from './chart-component';
import TimeRange from '@/components/time-range/time-range';
import { handleTransformToTimestamp } from '@/components/time-range/utils';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    ChartComponent,
    TimeRange,
    EmptyStatus,
  },
  props: {
    indexSetId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      formatDate,
      timesChartLoading: true,
      timesChartData: null,
      frequencyChartLoading: true,
      frequencyChartData: null,
      spentChartLoading: true,
      spentChartData: null,
      chartDateValue: ['now-7d', 'now'],
      tableLoading: true,
      tableData: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      tableDateValue: ['now-2d', 'now'],
    };
  },
  created() {
    this.initPage();
  },
  methods: {
    initPage() {
      this.fetchChartData();
      this.fetchTableData();
    },
    fetchChartData() {
      const tempList = handleTransformToTimestamp(this.chartDateValue);
      const payload = {
        params: {
          index_set_id: this.indexSetId,
        },
        query: {
          start_time: formatDate(tempList[0] * 1000),
          end_time: formatDate(tempList[1] * 1000),
        },
      };
      this.fetchTimesChart(payload);
      this.fetchFrequencyChart(payload);
      this.fetchSpentChart(payload);
    },
    /**
     * @desc 使用统计时间筛选
     * @param { Array } val
     */
    handleDateValueChange(val) {
      this.chartDateValue = val;
      this.fetchChartData();
    },
    /**
     * @desc 检索记录时间筛选
     * @param { Array } val
     */
    handleTableDateValueChange(val) {
      this.tableDateValue = val;
      this.fetchTableData();
    },
    async fetchTimesChart(payload) {
      try {
        this.timesChartLoading = true;
        const res = await this.$http.request('indexSet/getIndexTimes', payload);
        this.timesChartData = res.data;
      } catch (e) {
        console.warn(e);
        this.timesChartData = [];
      } finally {
        this.timesChartLoading = false;
      }
    },
    async fetchFrequencyChart(payload) {
      try {
        this.frequencyChartLoading = true;
        const res = await this.$http.request('indexSet/getIndexFrequency', payload);
        this.frequencyChartData = res.data;
      } catch (e) {
        console.warn(e);
        this.frequencyChartData = [];
      } finally {
        this.frequencyChartLoading = false;
      }
    },
    async fetchSpentChart(payload) {
      try {
        this.spentChartLoading = true;
        const res = await this.$http.request('indexSet/getIndexSpent', payload);
        this.spentChartData = res.data;
      } catch (e) {
        console.warn(e);
        this.spentChartData = [];
      } finally {
        this.spentChartLoading = false;
      }
    },
    async fetchTableData() {
      try {
        this.tableLoading = true;
        const tempList = handleTransformToTimestamp(this.tableDateValue);
        const res = await this.$http.request('indexSet/getIndexHistory', {
          params: {
            index_set_id: this.indexSetId,
          },
          query: {
            start_time: formatDate(tempList[0] * 1000),
            end_time: formatDate(tempList[1] * 1000),
            page: this.pagination.current,
            pagesize: this.pagination.limit,
          },
        });
        this.pagination.count = res.data.total;
        this.tableData = res.data.list;
      } catch (e) {
        console.warn(e);
        this.pagination.current = 1;
        this.pagination.count = 0;
        this.tableData.splice(0);
      } finally {
        this.tableLoading = false;
      }
    },
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        this.fetchTableData();
      }
    },
    handlePageLimitChange(limit) {
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.fetchTableData();
    },
  },
};
</script>

<style lang="scss" scoped>
  .chart-container {
    /* stylelint-disable-next-line declaration-no-important */
    width: calc((100% - 32px) / 3) !important;
  }

  .usage-details-container {
    .time-range-wrap {
      font-weight: normal;
      font-size: 12px;
    }
  }
</style>
