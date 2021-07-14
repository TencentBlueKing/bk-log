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
 * 获取Cookie
 * @param {String} name
 */
export const getCookie = (name) => {
  const reg = new RegExp(`(^|)${name}=([^;]*)(;|$)`);
  const data = document.cookie.match(reg);
  if (data) {
    return unescape(data[2]);
  }
  return null;
};
export const deleteCookie = (name, path, domain) => {
  if (getCookie(name)) {
    document.cookie = `${name}=${
      (path) ? `;path=${path}` : ''
    }${(domain) ? `;domain=${domain}` : ''
    };expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  }
};
/**
 * 深拷贝
 * @param {Object} obj
 * @param {Map} hash
 */
export const deepClone = (obj, hash = new WeakMap()) => {
  if (Object(obj) !== obj) return obj;
  if (obj instanceof Set) return new Set(obj);
  if (hash.has(obj)) return hash.get(obj);
  const result = obj instanceof Date ? new Date(obj)
    : obj instanceof RegExp ? new RegExp(obj.source, obj.flags)
      : obj.constructor ? new obj.constructor()
        : Object.create(null);
  hash.set(obj, result);
  if (obj instanceof Map) {
    Array.from(obj, ([key, val]) => result.set(key, deepClone(val, hash)));
  }
  return Object.assign(result, ...Object.keys(obj).map(key => ({ [key]: deepClone(obj[key], hash) })));
};

/**
 * 生成随机数
 * @param {Number} n
 */
export const random = (n) => { // 生成n位长度的字符串
  const str = 'abcdefghijklmnopqrstuvwxyz0123456789'; // 可以作为常量放到random外面
  let result = '';
  for (let i = 0; i < n; i++) {
    result += str[parseInt(Math.random() * str.length)];
  }
  return result;
};

export const isPostiveInt = val => /^[1-9][0-9]*$/.test(`${val}`);

/**
 * 命名转换
 * @param {Object} data  数据源
 * @param {Boolean} flag 转换方向 default: false; false: snake_case命名转换为camelCase命名 true: camelCase命名转snake_case命名
 */
export const transformDataKey = (data = {}, flag = false) => {
  if (!['[object Array]', '[object Object]'].includes(Object.prototype.toString.call(data))) return data;
  const result = {};
  if (Array.isArray(data)) {
    return data.map(item => transformDataKey(item, flag));
  }
  Object.keys(data).forEach((key) => {
    const matchList = flag ? key.match(/([A-Z])/g) : key.match(/(_[a-zA-Z])/g);
    let newKey = key;
    const item = data[key];
    if (matchList) {
      matchList.forEach((set) => {
        if (flag) {
          newKey = newKey.replace(set, `_${set
            .toLocaleLowerCase()}`);
        } else {
          newKey = newKey.replace(set, set.replace('_', '').toLocaleUpperCase());
        }
      });
    }
    if (item && typeof item === 'object' && Object.keys(item).length) {
      result[newKey] = transformDataKey(item, flag);
    } else {
      result[newKey] = item;
    }
  });

  return result;
};
export const copyText = (text, errorMsg) => {
  const textarea = document.createElement('textarea');
  document.body.appendChild(textarea);
  textarea.value = text;
  textarea.select();
  if (document.execCommand('copy')) {
    document.execCommand('copy');
  } else {
    errorMsg('浏览器不支持此功能，请使用谷歌浏览器。');
  }
  document.body.removeChild(textarea);
};

/**
 * 类型检测工具
 */
export const typeTools = {
  isArray: obj => Object.prototype.toString.call(obj) === '[object Array]',
  isObject: obj => Object.prototype.toString.call(obj) === '[object Object]',
  isNumber: obj => Object.prototype.toString.call(obj) === '[object Number]',
  isString: obj => Object.prototype.toString.call(obj) === '[object String]',
  isFunction: obj => Object.prototype.toString.call(obj) === '[object Function]',
  isBoolean: obj => Object.prototype.toString.call(obj) === '[object Boolean]',
  isNull: obj => obj === null || obj === '' || obj === undefined,
  isNotNull: obj => !this.isNull(obj),
};

/**
 * 时间格式化
 * @param {Date} time
 * @param {String} fmt yyyy-MM-dd hh:mm:ss
 */
export const formatDatetime = (time, fmt) => {
  const obj = {
    'M+': time.getMonth() + 1, // 月份
    'd+': time.getDate(), // 日
    'h+': time.getHours(), // 小时
    'm+': time.getMinutes(), // 分
    's+': time.getSeconds(), // 秒
    'q+': Math.floor((time.getMonth() + 3) / 3), // 季度
    S: time.getMilliseconds(), // 毫秒
  };
  if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (`${time.getFullYear()}`).substr(4 - RegExp.$1.length));
  for (const key in obj) {
    if (new RegExp(`(${key})`).test(fmt)) fmt = fmt.replace(
      RegExp.$1,
      (RegExp.$1.length === 1) ? (obj[key]) : ((`00${obj[key]}`).substr((`${obj[key]}`).length)),
    );
  }
  return fmt;
};

// 获取url中的参数
export const getUrlParam = (name) => {
  const reg = new RegExp(`(^|&)${name}=([^&]*)(&|$)`); // 构造一个含有目标参数的正则表达式对象
  const r = window.location.search.substr(1).match(reg); // 匹配目标参数
  if (r != null) return decodeURI(r[2]); return null; // 返回参数值
};

/**
 * 大数字转换为带单位的数字，如： 12100 转换成 12K
 * @param {*} num 数字
 * @param {*} digits 保留小数点位数
 */
export const transfromNum = (num, digits = 0) => {
  if (!num) return num;
  const si = [
    { value: 1, symbol: '' },
    { value: 1E3, symbol: 'K' },
    { value: 1E6, symbol: 'M' },
    { value: 1E9, symbol: 'G' },
    { value: 1E12, symbol: 'T' },
    { value: 1E15, symbol: 'P' },
    { value: 1E18, symbol: 'E' },
  ];
  const rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
  let i;
  for (i = si.length - 1; i > 0; i--) {
    if (num >= si[i].value) {
      break;
    }
  }
  return (num / si[i].value).toFixed(digits).replace(rx, '$1') + si[i].symbol;
};
/**
* 防抖装饰器
* @param [delay: number] 延时ms
* @returns descriptor
*/
export const Debounce = (delay = 200) => (target, key, descriptor) => {
  const originFunction = descriptor.value;
  const getNewFunction = () => {
    let timer;
    const newFunction = function (...args) {
      if (timer) window.clearTimeout(timer);
      timer = setTimeout(() => {
        originFunction.call(this, args);
      }, delay);
    };
    return newFunction;
  };
  descriptor.value = getNewFunction();
  return descriptor;
};
/**
 * 判断是否是对象
 *
 * @param {Object} obj 待判断的
 *
 * @return {boolean} 判断结果
 */
export function isObject(obj) {
  return obj !== null && typeof obj === 'object';
}
/**
 * 排序数组对象
 * 排序规则：1. 数字 => 2. 字母 => 3. 中文
 * @param {*} arr
 * @param {*} key
 */
export const sort = (arr, key) => {
  if (!Array.isArray(arr)) return;
  const reg = /^[0-9a-zA-Z]/;
  return arr.sort((pre, next) => {
    if (isObject(pre) && isObject(next) && key) {
      if (reg.test(pre[key]) && !reg.test(next[key])) {
        return -1;
      } if (!reg.test(pre[key]) && reg.test(next[key])) {
        return 1;
      }
      return pre[key].localeCompare(next[key]);
    }
    return (`${pre}`).toString().localeCompare((`${pre}`));
  });
};

/**
 * 绑定事件
 *
 * @param {Object} elem DOM 元素
 * @param {string} type 事件名称
 * @param {Function} handler 事件处理函数
 */
export function addEvent(elem, type, handler) {
  if (!elem) {
    return;
  }
  if (elem.addEventListener) {
    elem.addEventListener(type, handler, false);
  } else if (elem.attachEvent) {
    elem.attachEvent(`on${type}`, handler);
  } else {
    elem[`on${type}`] = handler;
  }
}
export const hexToRgbA = (hex, apacity = 1) => {
  let c;
  if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
    c = hex.substring(1).split('');
    if (c.length === 3) {
      c = [c[0], c[0], c[1], c[1], c[2], c[2]];
    }
    c = `0x${c.join('')}`;
    return `rgba(${[(c >> 16) & 255, (c >> 8) & 255, c & 255].join(',')},${apacity})`;
  }
  throw new Error('Bad Hex');
};
