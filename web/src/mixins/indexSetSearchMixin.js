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

import moment from 'moment';

export default {
  data() {
    return {
      finishPolling: false,
      pollingStartTime: 0,
      pollingEndTime: 0,
      requestInterval: 0, // 请求间隔时间
      interval: 'auto',
      intervalMap: {
        '5s': 5,
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '12h': 43200,
        '1d': 86400,
      },
    };
  },
  methods: {
    // 坐标分片规则
    handleIntervalSplit(startTime, endTime) {
      if (this.retrieveParams.interval !== 'auto') {
        this.interval = this.retrieveParams.interval;
        return;
      }
      const duration = (endTime - startTime) / (3600 * 1000);
      if (duration < 1) { // 小于1小时 1min
        this.interval = '1m';
      } else if (duration < 6) { // 小于6小时 5min
        this.interval = '5m';
      } else if (duration < 72) { // 小于72小时 1hour
        this.interval = '1h';
      } else { // 大于72小时 1day
        this.interval = '1d';
      }
    },
    handleRequestSplit(startTime, endTime) {
      const duration = (endTime - startTime) / (3600 * 1000);
      if (duration < 6) { // 小于6小时 一次性请求
        return 0;
      } if (duration < 48) { // 小于24小时 6小时间隔
        return 21600000;
      }  // 大于1天 按0.5天请求
      return 86400000 / 2;
    },
    // 获取实际查询开始和结束时间
    getRealTimeRange() {
      // 先判断是否 快捷时间 筛选
      const { time_range } = this.retrieveParams;
      // eslint-disable-next-line camelcase
      if (time_range === 'customized') {
        return {
          startTimeStamp: new Date(this.retrieveParams.start_time.replace(/-/g, '/')).getTime(),
          endTimeStamp: new Date(this.retrieveParams.end_time.replace(/-/g, '/')).getTime(),
        };
      }

      return {
        startTimeStamp: Date.now() - (this.intervalMap[time_range] * 1000),
        endTimeStamp: Date.now(),
      };
    },
    // 获取轮询时间间隔
    getInterval() {
      if (this.retrieveParams.interval !== 'auto') { // 若选择了汇聚周期则使用retrieveParams
        this.interval = this.retrieveParams.interval;
        return;
      }

      this.interval = '1h';
    },
    // 获取时间分片数组
    getTimeRange(startTime, endTime) {
      // 根据时间范围获取和横坐标分片
      const rangeArr = [];
      const range = (this.intervalMap[this.interval]) * 1000;
      for (let index = endTime; index >= startTime; index = index - range) {
        rangeArr.push([0, index]);
      }

      return rangeArr;
    },
    // 时间向下取整
    getIntegerTime(tiem) {
      if (this.interval === '1d') { // 如果周期是 天 则特殊处理
        const step = moment(tiem).format('YYYY-MM-DD');
        return Date.parse(`${step} 00:00:00`);
      }

      const step = (this.intervalMap[this.interval]) * 1000;
      return Math.floor(tiem / step) * step;
    },
  },
};
