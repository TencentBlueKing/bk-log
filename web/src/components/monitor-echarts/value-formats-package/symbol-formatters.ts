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

import { scaledUnits, ValueFormatter } from './value-formats';
import { DecimalCount } from '../types/display-value';

export function currency(symbol: string, asSuffix?: boolean): ValueFormatter {
  const units = ['', 'K', 'M', 'B', 'T'];
  const scaler = scaledUnits(1000, units);
  return (size: number, decimals?: DecimalCount, scaledDecimals?: DecimalCount) => {
    if (size === null) {
      return { text: '' };
    }
    const scaled = scaler(size, decimals, scaledDecimals);
    if (asSuffix) {
      scaled.suffix = symbol;
    } else {
      scaled.prefix = symbol;
    }
    return scaled;
  };
}

export function getOffsetFromSIPrefix(c: string): number {
  switch (c) {
    case 'f':
      return -5;
    case 'p':
      return -4;
    case 'n':
      return -3;
    case 'μ': // Two different unicode chars for µ
    case 'µ':
      return -2;
    case 'm':
      return -1;
    case '':
      return 0;
    case 'k':
      return 1;
    case 'M':
      return 2;
    case 'G':
      return 3;
    case 'T':
      return 4;
    case 'P':
      return 5;
    case 'E':
      return 6;
    case 'Z':
      return 7;
    case 'Y':
      return 8;
  }
  return 0;
}

export function binarySIPrefix(unit: string, offset = 0): ValueFormatter {
  const prefixes = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'].slice(offset);
  const units = prefixes.map(p => ` ${p}${unit}`);
  return scaledUnits(1024, units);
}

export function decimalSIPrefix(unit: string, offset = 0): ValueFormatter {
  let prefixes = ['f', 'p', 'n', 'µ', 'm', '', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'];
  prefixes = prefixes.slice(5 + (offset || 0));
  const units = prefixes.map(p => ` ${p}${unit}`);
  return scaledUnits(1000, units);
}
