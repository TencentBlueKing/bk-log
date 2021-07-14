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

type InTopOrBottom = boolean | undefined
export default class ChartInView {
  public chartInTop: InTopOrBottom
  public chartInBottom: InTopOrBottom
  public timer: any
  public rect: DOMRect
  public constructor(inTop: InTopOrBottom, inBottom: InTopOrBottom, rect: DOMRect) {
    this.setCharInView(inTop, inBottom, rect)
  }
  public setCharInView(inTop: InTopOrBottom, inBottom: InTopOrBottom, rect: DOMRect) {
    this.chartInTop = inTop
    this.chartInBottom = inBottom
    this.rect = rect
    this.timer && clearTimeout(this.timer)
    this.timer = setTimeout(() => {
      this.chartInTop = undefined
      this.chartInBottom = undefined
    }, 5000)
  }
}
