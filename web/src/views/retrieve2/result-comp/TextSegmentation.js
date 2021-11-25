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

import EventPopover from './EventPopover.vue';

export default {
  props: {
    content: {
      type: [String, Number],
      required: true,
    },
    fieldType: {
      type: String,
      default: '',
    },
    menuClick: Function,
  },
  render() {
    const { content, fieldType,  menuClick } = this;
    const renderHtml = () => {
      // text keyword 支持分词
      if (['text'].includes(fieldType)) {
        let value = content;
        const reg = /([.,&*+:;?^=!$<>{}()|[\]/\\|\s\r\n\t]|[-])/;
        // 高亮显示
        const markVal = content.match(/(?<=<mark>).*?(?=<\/mark>)/g) || [];
        if (markVal) {
          value = String(value).replace(/<mark>/g, '')
            .replace(/<\/mark>/g, '');
        }
        const formatterList = value.split(reg);
        const resHtml = formatterList.map((item) => {
          if (item === '') return;

          // 分割符号直接返回
          if (reg.test(item)) return item;

          // 高亮内容
          if (markVal.includes(item)) {
            return <EventPopover onEventClick={event => menuClick(event, item)}><mark>{item}</mark></EventPopover>;
          }

          return <EventPopover onEventClick={event => menuClick(event, item)}><span>{item}</span></EventPopover>;
        });

        return resHtml;
      }

      return <EventPopover onEventClick={event => menuClick(event, content)}>{content}</EventPopover>;
    };

    return (
      <span>
        {renderHtml()}
      </span>
    );
  },
};
