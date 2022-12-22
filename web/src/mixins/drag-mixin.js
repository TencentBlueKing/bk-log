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
  data() {
    return {
      minIntroWidth: 300, // 最小宽度
      maxIntroWidth: 480, // 默认最大宽度
      introWidth: 400, // 侧边栏宽度
      isDraging: false, // 是否正在拖拽
      currentTreeBoxWidth: null, // 当前侧边宽度
    };
  },
  methods: {
    // 控制页面布局宽度
    dragBegin(e) {
      this.currentTreeBoxWidth = this.introWidth;
      this.currentScreenX = e.screenX;
      window.addEventListener('mousemove', this.dragMoving, { passive: true });
      window.addEventListener('mouseup', this.dragStop, { passive: true });
    },
    dragMoving(e) {
      this.isDraging = true;
      const newTreeBoxWidth = this.currentTreeBoxWidth - e.screenX + this.currentScreenX;
      if (newTreeBoxWidth < this.minIntroWidth) {
        this.introWidth = this.minIntroWidth;
      } else if (newTreeBoxWidth >= this.maxIntroWidth) {
        this.introWidth = this.maxIntroWidth;
      } else {
        this.introWidth = newTreeBoxWidth;
      }
    },
    dragStop() {
      this.isDraging = false;
      this.currentTreeBoxWidth = null;
      this.currentScreenX = null;
      window.removeEventListener('mousemove', this.dragMoving);
      window.removeEventListener('mouseup', this.dragStop);
    },
  },
};
