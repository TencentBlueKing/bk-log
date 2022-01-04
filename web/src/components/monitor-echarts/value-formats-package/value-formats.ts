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

import getCategories from './categories'
import { DecimalCount } from '../types/display-value'
import { toDateTimeValueFormatter } from './date-time-formatters'
import { getOffsetFromSIPrefix, decimalSIPrefix, currency } from './symbol-formatters'


export interface FormattedValue {
  text: string;
  prefix?: string;
  suffix?: string;
}

export function formattedValueToString(val: FormattedValue): string {
  return `${val.prefix ?? ''}${val.text}${val.suffix ?? ''}`
}

export type ValueFormatter = (
  value: number,
  decimals?: DecimalCount,
  scaledDecimals?: DecimalCount,
  timeZone?
) => FormattedValue;

export interface ValueFormat {
  name: string;
  id: string;
  fn: ValueFormatter;
}

export interface ValueFormatCategory {
  name: string;
  formats: ValueFormat[];
}

interface ValueFormatterIndex {
  [id: string]: ValueFormatter;
}

// Globals & formats cache
let categories: ValueFormatCategory[] = []
const index: ValueFormatterIndex = {}
let hasBuiltIndex = false

export function toFixed(value: number, decimals?: DecimalCount): string {
  if (value === null) {
    return ''
  }
  if (value === Number.NEGATIVE_INFINITY || value === Number.POSITIVE_INFINITY) {
    return value.toLocaleString()
  }

  const factor = decimals ? Math.pow(10, Math.max(0, decimals)) : 1
  const formatted = String(Math.round(value * factor) / factor)

  // if exponent return directly
  if (formatted.indexOf('e') !== -1 || value === 0) {
    return formatted
  }

  // If tickDecimals was specified, ensure that we have exactly that
  // much precision; otherwise default to the value's own precision.
  if (decimals != null) {
    const decimalPos = formatted.indexOf('.')
    const precision = decimalPos === -1 ? 0 : formatted.length - decimalPos - 1
    if (precision < decimals) {
      return (precision ? formatted : `${formatted}.`) + String(factor).substr(1, decimals - precision)
    }
  }

  return formatted
}

export function toFixedScaled(
  value: number,
  decimals: DecimalCount,
  scaledDecimals: DecimalCount,
  additionalDecimals: number,
  ext?: string
): FormattedValue {
  if (scaledDecimals === null || scaledDecimals === undefined) {
    return { text: toFixed(value, decimals), suffix: ext }
  }
  return {
    text: toFixed(value, scaledDecimals + additionalDecimals),
    suffix: ext
  }
}

export function toFixedUnit(unit: string, asPrefix?: boolean): ValueFormatter {
  return (size: number, decimals?: DecimalCount) => {
    if (size === null) {
      return { text: '' }
    }
    const text = toFixed(size, decimals)
    if (unit) {
      if (asPrefix) {
        return { text, prefix: unit }
      }
      return { text, suffix: ` ${unit}` }
    }
    return { text }
  }
}

// Formatter which scales the unit string geometrically according to the given
// numeric factor. Repeatedly scales the value down by the factor until it is
// less than the factor in magnitude, or the end of the array is reached.
export function scaledUnits(factor: number, extArray: string[]): ValueFormatter {
  return (size: number, decimals: DecimalCount = 2, scaledDecimals?: DecimalCount) => {
    if (size === null) {
      return { text: '' }
    }
    if (size === Number.NEGATIVE_INFINITY || size === Number.POSITIVE_INFINITY || isNaN(size)) {
      return { text: size.toLocaleString() }
    }

    let steps = 0
    const limit = extArray.length

    while (Math.abs(size) >= factor) {
      steps += 1
      size /= factor

      if (steps >= limit) {
        return { text: 'NA' }
      }
    }

    if (steps > 0 && scaledDecimals !== null && scaledDecimals !== undefined) {
      decimals = scaledDecimals + (3 * steps)
    }

    return { text: toFixed(size, decimals), suffix: extArray[steps] }
  }
}

export function locale(value: number, decimals: DecimalCount): FormattedValue {
  if (value === null) {
    return { text: '' }
  }
  return {
    text: value.toLocaleString(undefined, { maximumFractionDigits: decimals as number })
  }
}

export function simpleCountUnit(symbol: string): ValueFormatter {
  const units = ['', 'K', 'M', 'B', 'T']
  const scaler = scaledUnits(1000, units)
  return (size: number, decimals?: DecimalCount, scaledDecimals?: DecimalCount) => {
    if (size === null) {
      return { text: '' }
    }
    const v = scaler(size, decimals, scaledDecimals)
    v.suffix += ` ${symbol}`
    return v
  }
}

function buildFormats() {
  categories = getCategories()

  // eslint-disable-next-line no-restricted-syntax
  for (const cat of categories) {
    // eslint-disable-next-line no-restricted-syntax
    for (const format of cat.formats) {
      index[format.id] = format.fn
    }
  }

  // Resolve units pointing to old IDs
  [{ from: 'farenheit', to: 'fahrenheit' }].forEach((alias) => {
    const f = index[alias.to]
    if (f) {
      index[alias.from] = f
    }
  })

  hasBuiltIndex = true
}

export function getValueFormat(id?: string | null): ValueFormatter {
  if (!hasBuiltIndex) {
    buildFormats()
  }
  if (!id || id === 'none') {
    return index.short
  }
  const fmt = index[id]

  if (!fmt && id) {
    const idx = id.indexOf(':')

    if (idx > 0) {
      const key = id.substring(0, idx)
      const sub = id.substring(idx + 1)

      if (key === 'prefix') {
        return toFixedUnit(sub, true)
      }

      if (key === 'time') {
        return toDateTimeValueFormatter(sub)
      }

      if (key === 'si') {
        const offset = getOffsetFromSIPrefix(sub.charAt(0))
        const unit = offset === 0 ? sub : sub.substring(1)
        return decimalSIPrefix(unit, offset)
      }

      if (key === 'count') {
        return simpleCountUnit(sub)
      }

      if (key === 'currency') {
        return currency(sub)
      }
    }

    return index.short
  }

  return fmt
}

export function getValueFormatterIndex(): ValueFormatterIndex {
  if (!hasBuiltIndex) {
    buildFormats()
  }

  return index
}

export function getValueFormats() {
  if (!hasBuiltIndex) {
    buildFormats()
  }

  return categories.map(cat => ({
    text: cat.name,
    submenu: cat.formats.map(format => ({
      text: format.name,
      value: format.id
    }))
  }))
}

export function getCategoryListById(id: string): {id: string; name: string}[] {
  if (!hasBuiltIndex) {
    buildFormats()
  }
  const category = categories.find(item => item.formats.some(child => child.id === id))
  if (!category) return categories[0].formats.map(({ id, name }) => ({ id, name }))
  return category.formats.map(({ id, name }) => ({ id, name }))
}
