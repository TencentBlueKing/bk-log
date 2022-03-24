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

/**
 * 判断属性props是否存在obj中
 * @param obj
 * @param props
 */
export const hasOwnProperty = (obj: any, props: string | string[]) => {
  if (Array.isArray(props)) {
    return props.every(str => Object.prototype.hasOwnProperty.call(obj, str));
  }
  return Object.prototype.hasOwnProperty.call(obj, props);
};
/**
 * 防抖装饰器
 * @param delay
 */
export const Debounce = (delay = 200) => (target: any, key: string, descriptor: PropertyDescriptor) => {
  const originFunction = descriptor.value;
  const getNewFunction = () => {
    let timer: any;
    const newFunction = function (...args: any[]) {
      if (timer) window.clearTimeout(timer);
      timer = setTimeout(() => {
        originFunction.call(this, ...args);
      }, delay);
    };
    return newFunction;
  };
  descriptor.value = getNewFunction();
  return descriptor;
};

/**
 * 关键字搜索
 * @param data
 * @param keyword
 */
export const defaultSearch = (data: any[], keyword: string) => {
  if (!Array.isArray(data) || keyword.trim() === '') return data;
  return data.filter(item => Object.keys(item).some((key) => {
    if (typeof item[key] === 'string') {
      return item[key].indexOf(keyword.trim()) > -1;
    }
    return false;
  }));
};

export default {
  hasOwnProperty,
  Debounce,
  defaultSearch,
};
