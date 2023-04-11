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

import moment, { DurationInputArg2 } from 'moment';
import { TimeRangeType } from './time-range';
import i18n from '../../language/i18n';

/** 相对时间范围格式正则 */
export const CUSTOM_TIME_RANGE_REG = /^now(([-+])(\d+)([m|h|d|w|M|y|Y]))?(\/[m|h|d|w|M|y|Y|fy])?/;

type TimeType = 'from' | 'to';

type TimestampsType = [number, number];

/** 处理时间范围的对象 */
export class TimeRange {
  /** 实例化的时间范围对象 */
  value: moment.Moment[] = [];

  constructor(times: TimeRangeType) {
    this.init(times);
  }

  /** 初始化时间对象 */
  init(times: TimeRangeType) {
    this.value = times.map((item, index) => this.transformTimeString(item, !index ? 'from' : 'to'));
  }

  /** 时间转换 */
  transformTimeString(timeStr: string, type: TimeType): moment.Moment {
    let momentRes: moment.Moment = null;
    /** 相对时间范围 */
    const match = timeStr.match(CUSTOM_TIME_RANGE_REG);
    
    if (!!match) {
      momentRes = moment();
      const [target,, method, num, dateType, boundary] = match;
      /** 过去时间 */
      if (method === '-' && num && dateType) {
        momentRes = momentRes.subtract(+num, dateType as DurationInputArg2);
      }
      /** 未来时间 */
      if (method === '+' && num && dateType) {
        momentRes = momentRes.add(+num, dateType as DurationInputArg2);
      }
      /** 获取完整时间段 */
      if (!!boundary) {
        type === 'from' && momentRes.startOf(boundary.replace('/', '') as moment.unitOfTime.StartOf);
        type === 'to' && momentRes.endOf(boundary.replace('/', '') as moment.unitOfTime.StartOf);
      }
      /** 相对时间格式错误 */
      if (target !== timeStr) {
        momentRes = moment(null);
      }
    } else { /** 绝对时间范围 */
      const time = intTimestampStr(timeStr);
      momentRes = moment(time);
    }
    return momentRes.isValid() ? momentRes : null;
  }

  /** 格式化时间范围 */
  format(str = 'YYYY-MM-DD HH:mm:ss'): TimeRangeType {
    return this.value.map(item => item?.format?.(str) || null) as TimeRangeType;
  }
  /** 格式化成秒 */
  unix(): TimestampsType {
    return this.value.map(item => item?.unix?.() || null) as TimestampsType;
  }
}

/** 字符串的时间戳(毫秒)转为数字类型 */
export const intTimestampStr = (str): number | null => {
  const isTimestamp = /^\d{1}$|^([1-9]\d{1,12})$/.test(str);
  return isTimestamp ? parseInt(str, 10) : str;
};

/** 将格式为 ['now-1d', 'now'] 转换为 ['YYYY-MM-DD HH:mm:ss', 'YYYY-MM-DD HH:mm:ss'] */
export const handleTransformTime = (value: TimeRangeType): TimeRangeType => {
  const timeRange = new TimeRange(value);
  return timeRange.format('YYYY-MM-DD HH:mm:ss');
};

/** 转换成秒 */
// eslint-disable-next-line max-len
export const handleTransformToTimestamp = (value: TimeRangeType): TimestampsType => {
  const timeRange = new TimeRange(value);
  return timeRange.unix();
};

/** 时间区间快捷选项 */
export const shortcuts = [
  {
    text: i18n.t('近{n}分钟', { n: 5 }),
    value: ['now-5m', 'now']
  },
  {
    text: i18n.t('近{n}分钟', { n: 15 }),
    value: ['now-15m', 'now']
  },
  {
    text: i18n.t('近{n}分钟', { n: 30 }),
    value: ['now-30m', 'now']
  },
  {
    text: i18n.t('近{n}小时', { n: 1 }),
    value: ['now-1h', 'now']
  },
  {
    text: i18n.t('近{n}小时', { n: 3 }),
    value: ['now-3h', 'now']
  },
  {
    text: i18n.t('近{n}小时', { n: 6 }),
    value: ['now-6h', 'now']
  },
  {
    text: i18n.t('近{n}小时', { n: 12 }),
    value: ['now-12h', 'now']
  },
  {
    text: i18n.t('近{n}小时', { n: 24 }),
    value: ['now-24h', 'now']
  },
  {
    text: i18n.t('近{n}天', { n: 2 }),
    value: ['now-2d', 'now']
  },
  {
    text: i18n.t('近{n}天', { n: 7 }),
    value: ['now-7d', 'now']
  },
  {
    text: i18n.t('近{n}天', { n: 30 }),
    value: ['now-30d', 'now']
  },
  {
    text: i18n.t('今天'),
    value: ['now/d', 'now/d']
  },
  {
    text: i18n.t('昨天'),
    value: ['now-1d/d', 'now-1d/d']
  },
  {
    text: i18n.t('前天'),
    value: ['now-2d/d', 'now-2d/d']
  },
  {
    text: i18n.t('本周'),
    value: ['now/w', 'now/w']
  }
];

/** 默认的时间范围：近一小时 */
export const DEFAULT_TIME_RANGE: TimeRangeType = ['now-1h', 'now'];
