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

export default {
  functional: true,
  props: {
    item: {
      type: String,
      required: true,
    },
    filterKey: {
      type: String,
      required: true,
    },
    ignoreCase: {
      type: Boolean,
      default: false,
    },
  },
  render(h, c) {
    const { item, filterKey, ignoreCase } = c.props;

    const handleMatch = (key) => {
      let filtKey = filterKey;
      const keyVal = ignoreCase ? key : key.toLowerCase();
      filtKey = ignoreCase ? filtKey : filtKey.toLowerCase();
      return keyVal.indexOf(filtKey);
    };

    const index = handleMatch(item);
    const { length } = filterKey;
    const left = item.slice(0, index);
    const match = item.slice(index, index + length);
    const right = item.slice(index + length);
    return (
            <span style="white-space: normal;word-break: break-all;">
                <span>{left}</span>
                <span style="background: yellow;color: #313238;">{match}</span>
                <span>{right}</span>
            </span>
    );
  },
};
