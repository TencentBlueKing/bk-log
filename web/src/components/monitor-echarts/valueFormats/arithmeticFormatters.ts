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

import { toFixed, FormattedValue } from './valueFormats'
import { DecimalCount } from '../types/displayValue'

export function toPercent(size: number, decimals?: DecimalCount): FormattedValue {
  if (size === null) {
    return { text: '' }
  }
  return { text: toFixed(size, decimals < 3 ? decimals : 2), suffix: '%' }
}

export function toPercentUnit(size: number, decimals?: DecimalCount): FormattedValue {
  if (size === null) {
    return { text: '' }
  }

  return { text: toFixed(100 * size, decimals < 3 ? decimals : 2), suffix: '%' }
}

export function toHex0x(value: number, decimals: DecimalCount = 2): FormattedValue {
  if (value == null) {
    return { text: '' }
  }
  const asHex = toHex(value, decimals)
  if (asHex.text.substring(0, 1) === '-') {
    asHex.text = `-0x${asHex.text.substring(1)}`
  } else {
    asHex.text = `0x${asHex.text}`
  }
  return asHex
}

export function toHex(value: number, decimals: DecimalCount = 2): FormattedValue {
  if (value == null) {
    return { text: '' }
  }
  return {
    text: parseFloat(toFixed(value, decimals))
      .toString(16)
      .toUpperCase()
  }
}

export function sci(value: number, decimals: DecimalCount = 2): FormattedValue {
  if (value == null) {
    return { text: '' }
  }
  return { text: value.toExponential(decimals as number) }
}
