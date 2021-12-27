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

import { locale, scaledUnits, simpleCountUnit, toFixedUnit, ValueFormatCategory } from './value-formats'
import {
  dateTimeAsIso,
  dateTimeAsUS,
  dateTimeFromNow,
  toClockMilliseconds,
  toClockSeconds,
  toDays,
  toDurationInHoursMinutesSeconds,
  toDurationInMilliseconds,
  toDurationInSeconds,
  toHours,
  toMicroSeconds,
  toMilliSeconds,
  toMinutes,
  toNanoSeconds,
  toSeconds,
  toTimeTicks
} from './date-time-formatters'
import { toHex, sci, toHex0x, toPercent, toPercentUnit } from './arithmetic-formatters'
import { binarySIPrefix, currency, decimalSIPrefix } from './symbol-formatters'

export default (): ValueFormatCategory[] => [
  {
    name: 'Misc',
    formats: [
      { name: 'none', id: 'none', fn: toFixedUnit('') },
      {
        name: 'short',
        id: 'short',
        fn: scaledUnits(1000, ['', ' K', ' Mil', ' Bil', ' Tri', ' Quadr', ' Quint', ' Sext', ' Sept'])
      },
      { name: 'percent (0-100)', id: 'percent', fn: toPercent },
      { name: 'percent (0.0-1.0)', id: 'percentunit', fn: toPercentUnit },
      { name: 'Humidity (%H)', id: 'humidity', fn: toFixedUnit('%H') },
      { name: 'decibel', id: 'dB', fn: toFixedUnit('dB') },
      { name: 'hexadecimal (0x)', id: 'hex0x', fn: toHex0x },
      { name: 'hexadecimal', id: 'hex', fn: toHex },
      { name: 'scientific notation', id: 'sci', fn: sci },
      { name: 'locale format', id: 'locale', fn: locale },
      { name: 'Pixels', id: 'pixel', fn: toFixedUnit('px') }
    ]
  },
  {
    name: 'Acceleration',
    formats: [
      { name: 'Meters/sec²', id: 'accMS2', fn: toFixedUnit('m/sec²') },
      { name: 'Feet/sec²', id: 'accFS2', fn: toFixedUnit('f/sec²') },
      { name: 'G unit', id: 'accG', fn: toFixedUnit('g') }
    ]
  },
  {
    name: 'Angle',
    formats: [
      { name: 'Degrees (°)', id: 'degree', fn: toFixedUnit('°') },
      { name: 'Radians', id: 'radian', fn: toFixedUnit('rad') },
      { name: 'Gradian', id: 'grad', fn: toFixedUnit('grad') },
      { name: 'Arc Minutes', id: 'arcmin', fn: toFixedUnit('arcmin') },
      { name: 'Arc Seconds', id: 'arcsec', fn: toFixedUnit('arcsec') }
    ]
  },
  {
    name: 'Area',
    formats: [
      { name: 'Square Meters (m²)', id: 'areaM2', fn: toFixedUnit('m²') },
      { name: 'Square Feet (ft²)', id: 'areaF2', fn: toFixedUnit('ft²') },
      { name: 'Square Miles (mi²)', id: 'areaMI2', fn: toFixedUnit('mi²') }
    ]
  },
  {
    name: 'Computation',
    formats: [
      { name: 'FLOP/s', id: 'flops', fn: decimalSIPrefix('FLOP/s') },
      { name: 'MFLOP/s', id: 'mflops', fn: decimalSIPrefix('FLOP/s', 2) },
      { name: 'GFLOP/s', id: 'gflops', fn: decimalSIPrefix('FLOP/s', 3) },
      { name: 'TFLOP/s', id: 'tflops', fn: decimalSIPrefix('FLOP/s', 4) },
      { name: 'PFLOP/s', id: 'pflops', fn: decimalSIPrefix('FLOP/s', 5) },
      { name: 'EFLOP/s', id: 'eflops', fn: decimalSIPrefix('FLOP/s', 6) },
      { name: 'ZFLOP/s', id: 'zflops', fn: decimalSIPrefix('FLOP/s', 7) },
      { name: 'YFLOP/s', id: 'yflops', fn: decimalSIPrefix('FLOP/s', 8) }
    ]
  },
  {
    name: 'Concentration',
    formats: [
      { name: 'parts-per-million (ppm)', id: 'ppm', fn: toFixedUnit('ppm') },
      { name: 'parts-per-billion (ppb)', id: 'conppb', fn: toFixedUnit('ppb') },
      { name: 'nanogram per cubic meter (ng/m³)', id: 'conngm3', fn: toFixedUnit('ng/m³') },
      { name: 'nanogram per normal cubic meter (ng/Nm³)', id: 'conngNm3', fn: toFixedUnit('ng/Nm³') },
      { name: 'microgram per cubic meter (μg/m³)', id: 'conμgm3', fn: toFixedUnit('μg/m³') },
      { name: 'microgram per normal cubic meter (μg/Nm³)', id: 'conμgNm3', fn: toFixedUnit('μg/Nm³') },
      { name: 'milligram per cubic meter (mg/m³)', id: 'conmgm3', fn: toFixedUnit('mg/m³') },
      { name: 'milligram per normal cubic meter (mg/Nm³)', id: 'conmgNm3', fn: toFixedUnit('mg/Nm³') },
      { name: 'gram per cubic meter (g/m³)', id: 'congm3', fn: toFixedUnit('g/m³') },
      { name: 'gram per normal cubic meter (g/Nm³)', id: 'congNm3', fn: toFixedUnit('g/Nm³') },
      { name: 'milligrams per decilitre (mg/dL)', id: 'conmgdL', fn: toFixedUnit('mg/dL') },
      { name: 'millimoles per litre (mmol/L)', id: 'conmmolL', fn: toFixedUnit('mmol/L') }
    ]
  },
  {
    name: 'Currency',
    formats: [
      { name: 'Dollars ($)', id: 'currencyUSD', fn: currency('$') },
      { name: 'Pounds (£)', id: 'currencyGBP', fn: currency('£') },
      { name: 'Euro (€)', id: 'currencyEUR', fn: currency('€') },
      { name: 'Yen (¥)', id: 'currencyJPY', fn: currency('¥') },
      { name: 'Rubles (₽)', id: 'currencyRUB', fn: currency('₽') },
      { name: 'Hryvnias (₴)', id: 'currencyUAH', fn: currency('₴') },
      { name: 'Real (R$)', id: 'currencyBRL', fn: currency('R$') },
      { name: 'Danish Krone (kr)', id: 'currencyDKK', fn: currency('kr', true) },
      { name: 'Icelandic Króna (kr)', id: 'currencyISK', fn: currency('kr', true) },
      { name: 'Norwegian Krone (kr)', id: 'currencyNOK', fn: currency('kr', true) },
      { name: 'Swedish Krona (kr)', id: 'currencySEK', fn: currency('kr', true) },
      { name: 'Czech koruna (czk)', id: 'currencyCZK', fn: currency('czk') },
      { name: 'Swiss franc (CHF)', id: 'currencyCHF', fn: currency('CHF') },
      { name: 'Polish Złoty (PLN)', id: 'currencyPLN', fn: currency('PLN') },
      { name: 'Bitcoin (฿)', id: 'currencyBTC', fn: currency('฿') },
      { name: 'South African Rand (R)', id: 'currencyZAR', fn: currency('R') },
      { name: 'Indian Rupee (₹)', id: 'currencyINR', fn: currency('₹') },
      { name: 'South Korean Won (₩)', id: 'currencyKRW', fn: currency('₩') }
    ]
  },
  {
    name: 'Data (IEC)',
    formats: [
      { name: 'bits', id: 'bits', fn: binarySIPrefix('b') },
      { name: 'bytes', id: 'bytes', fn: binarySIPrefix('B') },
      { name: 'kibibytes', id: 'kbytes', fn: binarySIPrefix('B', 1) },
      { name: 'mebibytes', id: 'mbytes', fn: binarySIPrefix('B', 2) },
      { name: 'gibibytes', id: 'gbytes', fn: binarySIPrefix('B', 3) },
      { name: 'tebibytes', id: 'tbytes', fn: binarySIPrefix('B', 4) },
      { name: 'pebibytes', id: 'pbytes', fn: binarySIPrefix('B', 5) }
    ]
  },
  {
    name: 'Data (Metric)',
    formats: [
      { name: 'bits', id: 'decbits', fn: decimalSIPrefix('b') },
      { name: 'bytes', id: 'decbytes', fn: decimalSIPrefix('B') },
      { name: 'kilobytes', id: 'deckbytes', fn: decimalSIPrefix('B', 1) },
      { name: 'megabytes', id: 'decmbytes', fn: decimalSIPrefix('B', 2) },
      { name: 'gigabytes', id: 'decgbytes', fn: decimalSIPrefix('B', 3) },
      { name: 'terabytes', id: 'dectbytes', fn: decimalSIPrefix('B', 4) },
      { name: 'petabytes', id: 'decpbytes', fn: decimalSIPrefix('B', 5) }
    ]
  },
  {
    name: 'Data Rate',
    formats: [
      { name: 'packets/sec', id: 'pps', fn: decimalSIPrefix('pps') },
      { name: 'bits/sec', id: 'bps', fn: decimalSIPrefix('bps') },
      { name: 'bytes/sec', id: 'Bps', fn: decimalSIPrefix('Bs') },
      { name: 'kilobytes/sec', id: 'KBs', fn: decimalSIPrefix('Bs', 1) },
      { name: 'kilobits/sec', id: 'Kbits', fn: decimalSIPrefix('bps', 1) },
      { name: 'megabytes/sec', id: 'MBs', fn: decimalSIPrefix('Bs', 2) },
      { name: 'megabits/sec', id: 'Mbits', fn: decimalSIPrefix('bps', 2) },
      { name: 'gigabytes/sec', id: 'GBs', fn: decimalSIPrefix('Bs', 3) },
      { name: 'gigabits/sec', id: 'Gbits', fn: decimalSIPrefix('bps', 3) },
      { name: 'terabytes/sec', id: 'TBs', fn: decimalSIPrefix('Bs', 4) },
      { name: 'terabits/sec', id: 'Tbits', fn: decimalSIPrefix('bps', 4) },
      { name: 'petabytes/sec', id: 'PBs', fn: decimalSIPrefix('Bs', 5) },
      { name: 'petabits/sec', id: 'Pbits', fn: decimalSIPrefix('bps', 5) }
    ]
  },
  {
    name: 'Date & Time',
    formats: [
      { name: 'YYYY-MM-DD HH:mm:ss', id: 'dateTimeAsIso', fn: dateTimeAsIso },
      { name: 'MM/DD/YYYY h:mm:ss a', id: 'dateTimeAsUS', fn: dateTimeAsUS },
      { name: 'From Now', id: 'dateTimeFromNow', fn: dateTimeFromNow }
    ]
  },
  {
    name: 'Energy',
    formats: [
      { name: 'Watt (W)', id: 'watt', fn: decimalSIPrefix('W') },
      { name: 'Kilowatt (kW)', id: 'kwatt', fn: decimalSIPrefix('W', 1) },
      { name: 'Megawatt (MW)', id: 'megwatt', fn: decimalSIPrefix('W', 2) },
      { name: 'Gigawatt (GW)', id: 'gwatt', fn: decimalSIPrefix('W', 3) },
      { name: 'Milliwatt (mW)', id: 'mwatt', fn: decimalSIPrefix('W', -1) },
      { name: 'Watt per square meter (W/m²)', id: 'Wm2', fn: toFixedUnit('W/m²') },
      { name: 'Volt-ampere (VA)', id: 'voltamp', fn: decimalSIPrefix('VA') },
      { name: 'Kilovolt-ampere (kVA)', id: 'kvoltamp', fn: decimalSIPrefix('VA', 1) },
      { name: 'Volt-ampere reactive (var)', id: 'voltampreact', fn: decimalSIPrefix('var') },
      { name: 'Kilovolt-ampere reactive (kvar)', id: 'kvoltampreact', fn: decimalSIPrefix('var', 1) },
      { name: 'Watt-hour (Wh)', id: 'watth', fn: decimalSIPrefix('Wh') },
      { name: 'Watt-hour per Kilogram (Wh/kg)', id: 'watthperkg', fn: decimalSIPrefix('Wh/kg') },
      { name: 'Kilowatt-hour (kWh)', id: 'kwatth', fn: decimalSIPrefix('Wh', 1) },
      { name: 'Kilowatt-min (kWm)', id: 'kwattm', fn: decimalSIPrefix('W-Min', 1) },
      { name: 'Ampere-hour (Ah)', id: 'amph', fn: decimalSIPrefix('Ah') },
      { name: 'Kiloampere-hour (kAh)', id: 'kamph', fn: decimalSIPrefix('Ah', 1) },
      { name: 'Milliampere-hour (mAh)', id: 'mamph', fn: decimalSIPrefix('Ah', -1) },
      { name: 'Joule (J)', id: 'joule', fn: decimalSIPrefix('J') },
      { name: 'Electron volt (eV)', id: 'ev', fn: decimalSIPrefix('eV') },
      { name: 'Ampere (A)', id: 'amp', fn: decimalSIPrefix('A') },
      { name: 'Kiloampere (kA)', id: 'kamp', fn: decimalSIPrefix('A', 1) },
      { name: 'Milliampere (mA)', id: 'mamp', fn: decimalSIPrefix('A', -1) },
      { name: 'Volt (V)', id: 'volt', fn: decimalSIPrefix('V') },
      { name: 'Kilovolt (kV)', id: 'kvolt', fn: decimalSIPrefix('V', 1) },
      { name: 'Millivolt (mV)', id: 'mvolt', fn: decimalSIPrefix('V', -1) },
      { name: 'Decibel-milliwatt (dBm)', id: 'dBm', fn: decimalSIPrefix('dBm') },
      { name: 'Ohm (Ω)', id: 'ohm', fn: decimalSIPrefix('Ω') },
      { name: 'Kiloohm (kΩ)', id: 'kohm', fn: decimalSIPrefix('Ω', 1) },
      { name: 'Megaohm (MΩ)', id: 'Mohm', fn: decimalSIPrefix('Ω', 2) },
      { name: 'Farad (F)', id: 'farad', fn: decimalSIPrefix('F') },
      { name: 'Microfarad (µF)', id: 'µfarad', fn: decimalSIPrefix('F', -2) },
      { name: 'Nanofarad (nF)', id: 'nfarad', fn: decimalSIPrefix('F', -3) },
      { name: 'Picofarad (pF)', id: 'pfarad', fn: decimalSIPrefix('F', -4) },
      { name: 'Femtofarad (fF)', id: 'ffarad', fn: decimalSIPrefix('F', -5) },
      { name: 'Henry (H)', id: 'henry', fn: decimalSIPrefix('H') },
      { name: 'Millihenry (mH)', id: 'mhenry', fn: decimalSIPrefix('H', -1) },
      { name: 'Microhenry (µH)', id: 'µhenry', fn: decimalSIPrefix('H', -2) },
      { name: 'Lumens (Lm)', id: 'lumens', fn: decimalSIPrefix('Lm') }
    ]
  },
  {
    name: 'Flow',
    formats: [
      { name: 'Gallons/min (gpm)', id: 'flowgpm', fn: toFixedUnit('gpm') },
      { name: 'Cubic meters/sec (cms)', id: 'flowcms', fn: toFixedUnit('cms') },
      { name: 'Cubic feet/sec (cfs)', id: 'flowcfs', fn: toFixedUnit('cfs') },
      { name: 'Cubic feet/min (cfm)', id: 'flowcfm', fn: toFixedUnit('cfm') },
      { name: 'Litre/hour', id: 'litreh', fn: toFixedUnit('L/h') },
      { name: 'Litre/min (L/min)', id: 'flowlpm', fn: toFixedUnit('L/min') },
      { name: 'milliLitre/min (mL/min)', id: 'flowmlpm', fn: toFixedUnit('mL/min') },
      { name: 'Lux (lx)', id: 'lux', fn: toFixedUnit('lux') }
    ]
  },
  {
    name: 'Force',
    formats: [
      { name: 'Newton-meters (Nm)', id: 'forceNm', fn: decimalSIPrefix('Nm') },
      { name: 'Kilonewton-meters (kNm)', id: 'forcekNm', fn: decimalSIPrefix('Nm', 1) },
      { name: 'Newtons (N)', id: 'forceN', fn: decimalSIPrefix('N') },
      { name: 'Kilonewtons (kN)', id: 'forcekN', fn: decimalSIPrefix('N', 1) }
    ]
  },
  {
    name: 'Hash Rate',
    formats: [
      { name: 'hashes/sec', id: 'Hs', fn: decimalSIPrefix('H/s') },
      { name: 'kilohashes/sec', id: 'KHs', fn: decimalSIPrefix('H/s', 1) },
      { name: 'megahashes/sec', id: 'MHs', fn: decimalSIPrefix('H/s', 2) },
      { name: 'gigahashes/sec', id: 'GHs', fn: decimalSIPrefix('H/s', 3) },
      { name: 'terahashes/sec', id: 'THs', fn: decimalSIPrefix('H/s', 4) },
      { name: 'petahashes/sec', id: 'PHs', fn: decimalSIPrefix('H/s', 5) },
      { name: 'exahashes/sec', id: 'EHs', fn: decimalSIPrefix('H/s', 6) }
    ]
  },
  {
    name: 'Mass',
    formats: [
      { name: 'milligram (mg)', id: 'massmg', fn: decimalSIPrefix('g', -1) },
      { name: 'gram (g)', id: 'massg', fn: decimalSIPrefix('g') },
      { name: 'kilogram (kg)', id: 'masskg', fn: decimalSIPrefix('g', 1) },
      { name: 'metric ton (t)', id: 'masst', fn: toFixedUnit('t') }
    ]
  },
  {
    name: 'length',
    formats: [
      { name: 'millimeter (mm)', id: 'lengthmm', fn: decimalSIPrefix('m', -1) },
      { name: 'feet (ft)', id: 'lengthft', fn: toFixedUnit('ft') },
      { name: 'meter (m)', id: 'lengthm', fn: decimalSIPrefix('m') },
      { name: 'kilometer (km)', id: 'lengthkm', fn: decimalSIPrefix('m', 1) },
      { name: 'mile (mi)', id: 'lengthmi', fn: toFixedUnit('mi') }
    ]
  },
  {
    name: 'Pressure',
    formats: [
      { name: 'Millibars', id: 'pressurembar', fn: decimalSIPrefix('bar', -1) },
      { name: 'Bars', id: 'pressurebar', fn: decimalSIPrefix('bar') },
      { name: 'Kilobars', id: 'pressurekbar', fn: decimalSIPrefix('bar', 1) },
      { name: 'Hectopascals', id: 'pressurehpa', fn: toFixedUnit('hPa') },
      { name: 'Kilopascals', id: 'pressurekpa', fn: toFixedUnit('kPa') },
      { name: 'Inches of mercury', id: 'pressurehg', fn: toFixedUnit('"Hg') },
      { name: 'PSI', id: 'pressurepsi', fn: scaledUnits(1000, ['psi', 'ksi', 'Mpsi']) }
    ]
  },
  {
    name: 'Radiation',
    formats: [
      { name: 'Becquerel (Bq)', id: 'radbq', fn: decimalSIPrefix('Bq') },
      { name: 'curie (Ci)', id: 'radci', fn: decimalSIPrefix('Ci') },
      { name: 'Gray (Gy)', id: 'radgy', fn: decimalSIPrefix('Gy') },
      { name: 'rad', id: 'radrad', fn: decimalSIPrefix('rad') },
      { name: 'Sievert (Sv)', id: 'radsv', fn: decimalSIPrefix('Sv') },
      { name: 'milliSievert (mSv)', id: 'radmsv', fn: decimalSIPrefix('mSv', -1) },
      { name: 'microSievert (µSv)', id: 'radusv', fn: decimalSIPrefix('µSv', -2) },
      { name: 'rem', id: 'radrem', fn: decimalSIPrefix('rem') },
      { name: 'Exposure (C/kg)', id: 'radexpckg', fn: decimalSIPrefix('C/kg') },
      { name: 'roentgen (R)', id: 'radr', fn: decimalSIPrefix('R') },
      { name: 'Sievert/hour (Sv/h)', id: 'radsvh', fn: decimalSIPrefix('Sv/h') },
      { name: 'milliSievert/hour (mSv/h)', id: 'radmsvh', fn: decimalSIPrefix('Sv/h', -1) },
      { name: 'microSievert/hour (µSv/h)', id: 'radusvh', fn: decimalSIPrefix('Sv/h', -2) }
    ]
  },
  {
    name: 'Temperature',
    formats: [
      { name: 'Celsius (°C)', id: 'celsius', fn: toFixedUnit('°C') },
      { name: 'Fahrenheit (°F)', id: 'fahrenheit', fn: toFixedUnit('°F') },
      { name: 'Kelvin (K)', id: 'kelvin', fn: toFixedUnit('K') }
    ]
  },
  {
    name: 'Time',
    formats: [
      { name: 'Hertz (1/s)', id: 'hertz', fn: decimalSIPrefix('Hz') },
      { name: 'nanoseconds (ns)', id: 'ns', fn: toNanoSeconds },
      { name: 'microseconds (µs)', id: 'µs', fn: toMicroSeconds },
      { name: 'milliseconds (ms)', id: 'ms', fn: toMilliSeconds },
      { name: 'seconds (s)', id: 's', fn: toSeconds },
      { name: 'minutes (m)', id: 'm', fn: toMinutes },
      { name: 'hours (h)', id: 'h', fn: toHours },
      { name: 'days (d)', id: 'd', fn: toDays },
      { name: 'duration (ms)', id: 'dtdurationms', fn: toDurationInMilliseconds },
      { name: 'duration (s)', id: 'dtdurations', fn: toDurationInSeconds },
      { name: 'duration (hh:mm:ss)', id: 'dthms', fn: toDurationInHoursMinutesSeconds },
      { name: 'Timeticks (s/100)', id: 'timeticks', fn: toTimeTicks },
      { name: 'clock (ms)', id: 'clockms', fn: toClockMilliseconds },
      { name: 'clock (s)', id: 'clocks', fn: toClockSeconds }
    ]
  },
  {
    name: 'Throughput',
    formats: [
      { name: 'counts/sec (cps)', id: 'cps', fn: simpleCountUnit('cps') },
      { name: 'ops/sec (ops)', id: 'ops', fn: simpleCountUnit('ops') },
      { name: 'requests/sec (rps)', id: 'reqps', fn: simpleCountUnit('reqps') },
      { name: 'reads/sec (rps)', id: 'rps', fn: simpleCountUnit('rps') },
      { name: 'writes/sec (wps)', id: 'wps', fn: simpleCountUnit('wps') },
      { name: 'I/O ops/sec (iops)', id: 'iops', fn: simpleCountUnit('iops') },
      { name: 'counts/min (cpm)', id: 'cpm', fn: simpleCountUnit('cpm') },
      { name: 'ops/min (opm)', id: 'opm', fn: simpleCountUnit('opm') },
      { name: 'reads/min (rpm)', id: 'rpm', fn: simpleCountUnit('rpm') },
      { name: 'writes/min (wpm)', id: 'wpm', fn: simpleCountUnit('wpm') }
    ]
  },
  {
    name: 'Velocity',
    formats: [
      { name: 'meters/second (m/s)', id: 'velocityms', fn: toFixedUnit('m/s') },
      { name: 'kilometers/hour (km/h)', id: 'velocitykmh', fn: toFixedUnit('km/h') },
      { name: 'miles/hour (mph)', id: 'velocitymph', fn: toFixedUnit('mph') },
      { name: 'knot (kn)', id: 'velocityknot', fn: toFixedUnit('kn') }
    ]
  },
  {
    name: 'Volume',
    formats: [
      { name: 'millilitre (mL)', id: 'mlitre', fn: decimalSIPrefix('L', -1) },
      { name: 'litre (L)', id: 'litre', fn: decimalSIPrefix('L') },
      { name: 'cubic meter', id: 'm3', fn: toFixedUnit('m³') },
      { name: 'Normal cubic meter', id: 'Nm3', fn: toFixedUnit('Nm³') },
      { name: 'cubic decimeter', id: 'dm3', fn: toFixedUnit('dm³') },
      { name: 'gallons', id: 'gallons', fn: toFixedUnit('gal') }
    ]
  }
]
