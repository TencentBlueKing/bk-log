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
 * @file 通用方法
 * @author  <>
 */

import html2canvas from 'html2canvas';
import JSONBigNumber from 'json-bignumber';

/**
  * 函数柯里化
  *
  * @example
  *     function add (a, b) {return a + b}
  *     curry(add)(1)(2)
  *
  * @param {Function} fn 要柯里化的函数
  *
  * @return {Function} 柯里化后的函数
  */
export function curry(fn) {
  const judge = (...args) => (args.length === fn.length
    ? fn(...args)
    : arg => judge(...args, arg));
  return judge;
}

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
  * 规范化参数
  *
  * @param {Object|string} type vuex type
  * @param {Object} payload vuex payload
  * @param {Object} options vuex options
  *
  * @return {Object} 规范化后的参数
  */
export function unifyObjectStyle(type, payload, options) {
  if (isObject(type) && type.type) {
    options = payload;
    payload = type;
    type = type.type;
  }

  if (process.env.NODE_ENV !== 'production') {
    if (typeof type !== 'string') {
      console.warn(`expects string as the type, but found ${typeof type}.`);
    }
  }

  return { type, payload, options };
}

/**
  * 以 baseColor 为基础生成随机颜色
  *
  * @param {string} baseColor 基础颜色
  * @param {number} count 随机颜色个数
  *
  * @return {Array} 颜色数组
  */
export function randomColor(baseColor, count) {
  const segments = baseColor.match(/[\da-z]{2}/g);
  // 转换成 rgb 数字
  for (let i = 0; i < segments.length; i++) {
    segments[i] = parseInt(segments[i], 16);
  }
  const ret = [];
  // 生成 count 组颜色，色差 20 * Math.random
  for (let i = 0; i < count; i++) {
    ret[i] = `#${
      Math.floor(segments[0] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[1] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[2] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)}`;
  }
  return ret;
}

/**
  * min max 之间的随机整数
  *
  * @param {number} min 最小值
  * @param {number} max 最大值
  *
  * @return {number} 随机数
  */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

/**
  * 异常处理
  *
  * @param {Object} err 错误对象
  * @param {Object} ctx 上下文对象，这里主要指当前的 Vue 组件
  */
export function catchErrorHandler(err, ctx) {
  const { data } = err;
  if (data) {
    if (!data.code || data.code === 404) {
      ctx.exceptionCode = {
        code: '404',
        msg: '当前访问的页面不存在',
      };
    } else if (data.code === 403) {
      ctx.exceptionCode = {
        code: '403',
        msg: 'Sorry，您的权限不足!',
      };
    } else {
      console.error(err);
      ctx.bkMessageInstance = ctx.$bkMessage({
        theme: 'error',
        message: err.message || err.data.msg || err.statusText,
      });
    }
  } else {
    console.error(err);
    ctx.bkMessageInstance = ctx.$bkMessage({
      theme: 'error',
      message: err.message || err.data.msg || err.statusText,
    });
  }
}

/**
  * 获取字符串长度，中文算两个，英文算一个
  *
  * @param {string} str 字符串
  *
  * @return {number} 结果
  */
export function getStringLen(str) {
  let len = 0;
  for (let i = 0; i < str.length; i++) {
    if (str.charCodeAt(i) > 127 || str.charCodeAt(i) === 94) {
      len += 2;
    } else {
      len = len + 1;
    }
  }
  return len;
}

/**
  * 转义特殊字符
  *
  * @param {string} str 待转义字符串
  *
  * @return {string} 结果
  */
export const escape = str => String(str).replace(/([.*+?^=!:${}()|[\]/\\])/g, '\\$1');

/**
  * 对象转为 url query 字符串
  *
  * @param {*} param 要转的参数
  * @param {string} key key
  *
  * @return {string} url query 字符串
  */
export function json2Query(param, key) {
  const mappingOperator = '=';
  const separator = '&';
  let paramStr = '';

  if (param instanceof String || typeof param === 'string'
         || param instanceof Number || typeof param === 'number'
         || param instanceof Boolean || typeof param === 'boolean'
  ) {
    paramStr += separator + key + mappingOperator + encodeURIComponent(param);
  } else {
    Object.keys(param).forEach((p) => {
      const value = param[p];
      const k = (key === null || key === '' || key === undefined)
        ? p
        : key + (param instanceof Array ? `[${p}]` : `.${p}`);
      paramStr += separator + json2Query(value, k);
    });
  }
  return paramStr.substr(1);
}

/**
  * 字符串转换为驼峰写法
  *
  * @param {string} str 待转换字符串
  *
  * @return {string} 转换后字符串
  */
export function camelize(str) {
  return str.replace(/-(\w)/g, (strMatch, p1) => p1.toUpperCase());
}

/**
  * 获取元素的样式
  *
  * @param {Object} elem dom 元素
  * @param {string} prop 样式属性
  *
  * @return {string} 样式值
  */
export function getStyle(elem, prop) {
  if (!elem || !prop) {
    return false;
  }

  // 先获取是否有内联样式
  let value = elem.style[camelize(prop)];

  if (!value) {
    // 获取的所有计算样式
    let css = '';
    if (document.defaultView && document.defaultView.getComputedStyle) {
      css = document.defaultView.getComputedStyle(elem, null);
      value = css ? css.getPropertyValue(prop) : null;
    }
  }

  return String(value);
}

/**
  *  获取元素相对于页面的高度
  *
  *  @param {Object} node 指定的 DOM 元素
  */
export function getActualTop(node) {
  let actualTop = node.offsetTop;
  let current = node.offsetParent;

  while (current !== null) {
    actualTop += current.offsetTop;
    current = current.offsetParent;
  }

  return actualTop;
}

/**
  *  获取元素相对于页面左侧的宽度
  *
  *  @param {Object} node 指定的 DOM 元素
  */
export function getActualLeft(node) {
  let actualLeft = node.offsetLeft;
  let current = node.offsetParent;

  while (current !== null) {
    actualLeft += current.offsetLeft;
    current = current.offsetParent;
  }

  return actualLeft;
}

/**
  * document 总高度
  *
  * @return {number} 总高度
  */
export function getScrollHeight() {
  let scrollHeight = 0;
  let bodyScrollHeight = 0;
  let documentScrollHeight = 0;

  if (document.body) {
    bodyScrollHeight = document.body.scrollHeight;
  }

  if (document.documentElement) {
    documentScrollHeight = document.documentElement.scrollHeight;
  }

  scrollHeight = (bodyScrollHeight - documentScrollHeight > 0) ? bodyScrollHeight : documentScrollHeight;

  return scrollHeight;
}

/**
  * 滚动条在 y 轴上的滚动距离
  *
  * @return {number} y 轴上的滚动距离
  */
export function getScrollTop() {
  let scrollTop = 0;
  let bodyScrollTop = 0;
  let documentScrollTop = 0;

  if (document.body) {
    bodyScrollTop = document.body.scrollTop;
  }

  if (document.documentElement) {
    documentScrollTop = document.documentElement.scrollTop;
  }

  scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;

  return scrollTop;
}

/**
  * 浏览器视口的高度
  *
  * @return {number} 浏览器视口的高度
  */
export function getWindowHeight() {
  const windowHeight = document.compatMode === 'CSS1Compat'
    ? document.documentElement.clientHeight
    : document.body.clientHeight;

  return windowHeight;
}

/**
  * 深拷贝扩展对象
  * @param target
  * @param ...sources
  * @returns {object}
  */
export function deepAssign(target, ...sources) {
  const sourcesArray = [...sources];
  const { length } = sourcesArray;
  if (typeof target !== 'object' && typeof target !== 'function') {
    target = {};
  }
  if (length === 0) {
    target = this;
  }

  sourcesArray.forEach((source) => {
    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        const targetValue = target[key];
        if (Array.isArray(targetValue)) {
          target[key].push(...(source[key] || []));
        } else if (typeof targetValue === 'object') {
          target[key] = deepAssign.call(targetValue, source[key]);
        } else {
          target[key] = source[key];
        }
      }
    }
  });

  return target;
}

/**
  * 将dom解析成png图片并下载
  * @param {Element} element
  * @param {String} filename 默认文件名
  */
export function convertDomToPng(element, filename = 'download') {
  let imgUrl;
  html2canvas(element).then((canvas) => {
    imgUrl = canvas.toDataURL('image/png');
  })
    .finally(() => {
      const eleLink = document.createElement('a');
      eleLink.href = imgUrl;
      eleLink.download = filename;
      document.body.appendChild(eleLink);
      eleLink.click();
      document.body.removeChild(eleLink);
    });
}
export function projectManage(menuProject, projectName, childName) {
  let project = '';
  try {
    menuProject.forEach((res) => {
      if (res.id === projectName && res.children) {
        res.children.forEach((item) => {
          if (item.id === childName) {
            project = item.project_manage;
          }
        });
      }
    });
  } catch (e) {
    console.log(e);
  }
  return project;
}

export function projectManages(menuList, id) {
  for (const menu of menuList) {
    if (menu.id === id) {
      return menu.project_manage;
    }
    if (menu.children) {
      const recursiveResult = projectManages(menu.children, id);
      if (recursiveResult !== undefined) {
        return recursiveResult;
      }
    }
  }
  return undefined;
}

/**
  * 设置显示字段的最小宽度，此方法会修改第一个参数的数据
  * @param {Array} visibleFieldsList
  * @param {Object} fieldsWidthInfo
  * @param {Number} minWidth 固定最小宽度
  */
export function setFieldsWidth(visibleFieldsList, fieldsWidthInfo, minWidth = 1000) {
  // const totalUnit = visibleFieldsList.forEach(item => {
  //     const key = item.field_name
  //     const maxLength = fieldsWidthInfo[key].max_length || 0
  //     rowObj[key] = maxLength
  //     rowWidth.push(maxLength)
  // })
  const rowObj = {};
  const rowWidth = [];
  visibleFieldsList.forEach((item) => {
    const key = item.field_name;
    // eslint-disable-next-line camelcase
    const maxLength = fieldsWidthInfo[key]?.max_length || 0;
    rowObj[key] = maxLength;
    rowWidth.push(maxLength);
  });
  const rowNum = rowWidth.length;
  const allWidth = rowWidth.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
  if (Math.ceil(allWidth * 6.5) <= minWidth - rowNum * 20) {
    visibleFieldsList.forEach((fieldInfo) => {
      const key = fieldInfo.field_name;
      rowObj[key] = rowObj[key] < 9 ? 9 : rowObj[key];
      rowObj[key] = rowObj[key] > 30 ? rowObj[key] / 1.5 : rowObj[key];
      fieldInfo.minWidth = rowObj[key] / allWidth * (minWidth - rowNum * 20);
    });
  } else {
    const half = Math.ceil(rowNum / 2);
    const proportion = [];
    for (const key in rowObj) {
      const width = rowObj[key] * 6.5;
      if (width >= Math.floor(half / rowNum * minWidth)) {
        proportion.push(half);
      } else if (width <= Math.floor(1 / rowNum * minWidth)) {
        proportion.push(1);
      } else {
        proportion.push(Math.floor(width * rowNum / minWidth));
      }
    }
    const proportionNum = proportion.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
    visibleFieldsList.forEach((fieldInfo, index) => {
      fieldInfo.minWidth = minWidth * (proportion[index] / proportionNum);
    });
  }
}

/**
  * 返回日期格式 2020-04-13 09:15:14
  * @param {Number | String | Date} val
  * @return {String}
  */
export function formatDate(val) {
  const date = new Date(val);

  if (isNaN(date.getTime())) {
    console.warn('无效的时间');
    return '';
  }

  const yyyy = date.getFullYear();
  const mm = (`0${date.getMonth() + 1}`).slice(-2);
  const dd = (`0${date.getDate()}`).slice(-2);
  const time = date.toTimeString().slice(0, 8);
  return `${yyyy}-${mm}-${dd} ${time}`;
}

/**
  * 格式化文件大小
  * @param {Number | String} size
  * @return {String}
  */
export function formatFileSize(size) {
  const value = Number(size);
  if (size && !isNaN(value)) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB'];
    let index = 0;
    let k = value;
    if (value >= 1024) {
      while (k > 1024) {
        k = k / 1024;
        index = index + 1;
      }
    }
    return `${(k).toFixed(2)}${units[index]}`;
  }
  return '0';
}

/**
  * 读取Blob格式返回数据
  * @param {*} response
  */
export function readBlobResponse(response) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = function () {
      resolve(reader.result);
    };

    reader.onerror = function () {
      reject(reader.error);
    };

    reader.readAsText(response);
  });
}

/**
  * 读取Blob格式返回Json数据
  * @param {*} resp
  */
export function readBlobRespToJson(resp) {
  return readBlobResponse(resp).then(resText => Promise.resolve(JSONBigNumber.parse(resText)));
}

export function bigNumberToString(value) {
  return (value || {})._isBigNumber
    ? value.toString().length < 16
      ? Number(value) : (value).toString() : value;
}

export function formatBigNumListValue(value) {
  if (Object.prototype.toString.call(value) === '[object Object]' && value !== null && !value._isBigNumber) {
    const obj = {};
    if (value instanceof Array) {
      return obj[value] = parseBigNumberList(value);
    }
    Object.keys(value).forEach((opt) => {
      obj[opt] = Object.prototype.toString.call(obj[opt]) === '[object Object]' && obj[opt] !== null && !obj[opt]._isBigNumber
        ? formatBigNumListValue(obj[opt]) : bigNumberToString(value[opt] || '');
    });
    return obj;
  }
  return bigNumberToString(value || '');
}

export function parseBigNumberList(lsit) {
  return (lsit || []).map(item => Object.keys(item || {})
    .reduce((output, key) => {
      return {
        ...output,
        [key]: formatBigNumListValue(item[key]),
      };
    }, {}));
}

/**
  * 生成随机数
  * @param {Number} n
  */
export const random = (n) => { // 生成n位长度的字符串
  const str = 'abcdefghijklmnopqrstuvwxyz0123456789'; // 可以作为常量放到random外面
  let result = '';
  for (let i = 0; i < n; i++) {
    result += str[parseInt(Math.random() * str.length, 10)];
  }
  return result;
};

/**
 * @desc: 复制文本
 * @param {*} val 文本
 * @param {*} alertMsg 弹窗文案
 */
export const copyMessage = (val, alertMsg) => {
  try {
    const input = document.createElement('input');
    input.setAttribute('value', val);
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    window.mainComponent.messageSuccess(alertMsg ? alertMsg : window.mainComponent.$t('复制成功'));
  } catch (e) {
    console.warn(e);
  }
};

/**
 * @desc: 字符串转base64
 * @param { String } str
 */
export const base64Encode = (str) => {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
    (match, p1) => String.fromCharCode(`0x${p1}`)));
};

/**
 * @desc: base64转字符串
 * @param { String } str
 */
export const base64Decode = (str) => {
  return decodeURIComponent(atob(str).split('')
    .map(c => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
    .join(''));
};

export const makeMessage = (message, traceId) => {
  const resMsg = `
    ${traceId || '--'} ：
    ${message}
  `;
  message && console.log(`
  ------------------【日志】------------------
  【TraceID】：${traceId}
  【Message】：${message}
  ----------------------------------------------
  `);
  return resMsg;
};

export class Storage {
  /** 过期时长 */
  express = null;
  constructor(express) {
    this.express = express;
  }
  /** 设置缓存 */
  set(key, value, express = this.express) {
    const data = {
      value,
      updateTime: Date.now(),
      express,
    };
    localStorage.setItem(key, JSON.stringify(data));
  }
  /** 获取缓存 */
  get(key) {
    const dataStr = localStorage.getItem(key);
    if (!dataStr) return null;
    const data = JSON.parse(dataStr);
    const nowTime = Date.now();
    if (data.express && data.express < (nowTime - data.updateTime)) {
      this.remove(key);
      return null;
    }
    return data.value;
  }
  /** 移除缓存 */
  remove(key) {
    localStorage.removeItem(key);
  }
}


/**
 * 深拷贝
 * @param {Object} obj
 * @param {Map} hash
 */
export const deepClone = (obj, hash = new WeakMap()) => {
  if (Object(obj) !== obj) return obj;
  if (obj instanceof Set) return new Set(obj);
  if (hash.has(obj)) return hash.get(obj);
  const result =    obj instanceof Date
    ? new Date(obj)
    : obj instanceof RegExp
      ? new RegExp(obj.source, obj.flags)
      : obj.constructor
        ? new obj.constructor()
        : Object.create(null);
  hash.set(obj, result);
  if (obj instanceof Map) {
    Array.from(obj, ([key, val]) => result.set(key, deepClone(val, hash)));
  }
  return Object.assign(result, ...Object.keys(obj).map(key => ({ [key]: deepClone(obj[key], hash) })));
};

export const clearTableFilter =  (refInstance) => {
  if (refInstance.$refs.tableHeader.filterPanels) {
    const filterPanels = refInstance.$refs.tableHeader.filterPanels;
    for (const key in filterPanels) {
      filterPanels[key].handleReset();
    };
  }
};
