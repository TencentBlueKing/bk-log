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

/* eslint-disable no-underscore-dangle */
import { DirectiveOptions } from 'vue'
import { DirectiveBinding } from 'vue/types/options'
import { addListener, removeListener } from 'resize-detector'

interface ICustomElements extends HTMLElement {
  __mutation__?: MutationObserver
}

export const mutation: DirectiveOptions = {
  bind: (el: ICustomElements, binding: DirectiveBinding) => {
    const options: MutationObserverInit = {
      attributes: true, childList: true, subtree: true
    }
    const observer = new MutationObserver(binding.value)
    observer.observe(el, options)
    el.__mutation__ = observer
  },
  unbind: (el: ICustomElements) => {
    el.__mutation__?.disconnect()
  }
}

export const resize: DirectiveOptions = {
  bind: (el: HTMLElement, binding: DirectiveBinding) => {
    addListener(el, binding.value)
  },
  unbind: (el: HTMLElement, binding: DirectiveBinding) => {
    removeListener(el, binding.value)
  }
}

export default {
  mutation,
  resize
}
