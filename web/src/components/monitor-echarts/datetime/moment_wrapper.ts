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

/* eslint-disable max-len */
/* eslint-disable id-blacklist, no-restricted-imports, @typescript-eslint/ban-types */
import moment, { Moment, MomentInput, DurationInputArg1 } from 'moment'
export interface DateTimeBuiltinFormat {
  __momentBuiltinFormatBrand: any;
}
export const { ISO_8601 } = moment
export type DateTimeInput = Date | string | number | Array<string | number> | DateTime; // null | undefined
export type FormatInput = string | DateTimeBuiltinFormat | undefined;
export type DurationInput = string | number | DateTimeDuration;
export type DurationUnit =
  | 'year'
  | 'years'
  | 'y'
  | 'month'
  | 'months'
  | 'M'
  | 'week'
  | 'weeks'
  | 'w'
  | 'day'
  | 'days'
  | 'd'
  | 'hour'
  | 'hours'
  | 'h'
  | 'minute'
  | 'minutes'
  | 'm'
  | 'second'
  | 'seconds'
  | 's'
  | 'millisecond'
  | 'milliseconds'
  | 'ms'
  | 'quarter'
  | 'quarters'
  | 'Q';

export interface DateTimeLocale {
  firstDayOfWeek: () => number;
}

export interface DateTimeDuration {
  asHours: () => number;
  hours: () => number;
  minutes: () => number;
  seconds: () => number;
  asSeconds: () => number;
}

export interface DateTime extends Object {
  add: (amount?: DateTimeInput, unit?: DurationUnit) => DateTime;
  set: (unit: DurationUnit, amount: DateTimeInput) => void;
  diff: (amount: DateTimeInput, unit?: DurationUnit, truncate?: boolean) => number;
  endOf: (unitOfTime: DurationUnit) => DateTime;
  format: (formatInput?: FormatInput) => string;
  fromNow: (withoutSuffix?: boolean) => string;
  from: (formaInput: DateTimeInput) => string;
  isSame: (input?: DateTimeInput, granularity?: DurationUnit) => boolean;
  isValid: () => boolean;
  local: () => DateTime;
  locale: (locale: string) => DateTime;
  startOf: (unitOfTime: DurationUnit) => DateTime;
  subtract: (amount?: DateTimeInput, unit?: DurationUnit) => DateTime;
  toDate: () => Date;
  toISOString: () => string;
  isoWeekday: (day?: number | string) => number | string;
  valueOf: () => number;
  unix: () => number;
  utc: () => DateTime;
  utcOffset: () => number;
  hour?: () => number;
  minute?: () => number;
}

export const setLocale = (language: string) => {
  moment.locale(language)
}

export const getLocaleData = (): DateTimeLocale => moment.localeData()

export const isDateTime = (value: any): value is DateTime => moment.isMoment(value)

export const toUtc = (input?: DateTimeInput, formatInput?: FormatInput): DateTime => moment.utc(input as MomentInput, formatInput) as DateTime

export const toDuration = (input?: DurationInput, unit?: DurationUnit): DateTimeDuration => moment.duration(input as DurationInputArg1, unit) as DateTimeDuration

export const dateTime = (input?: DateTimeInput, formatInput?: FormatInput): DateTime => moment(input as MomentInput, formatInput) as DateTime

export const dateTimeAsMoment = (input?: DateTimeInput) => dateTime(input) as Moment

export const dateTimeForTimeZone = (
  timezone?,
  input?: DateTimeInput,
  formatInput?: FormatInput
): DateTime => {
  if (timezone === 'utc') {
    return toUtc(input, formatInput)
  }

  return dateTime(input, formatInput)
}
