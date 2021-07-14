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

const methods = {
  install(Vue) {
    Vue.prototype.$easeScroll = function (to = 0, duration = 300, target = window) {
      const start = target === window ? target.scrollY : target.scrollTop;
      const beginTime = Date.now();

      requestAnimationFrame(animate);

      function animate() {
        const nowTime = Date.now();
        const time = nowTime - beginTime;
        target.scrollTo({
          top: computeCoordinate(time, start, to, duration),
        });
        if (time < duration) {
          requestAnimationFrame(animate);
        }
      }

      function computeCoordinate(time, start, to, duration) { // 计算滚动绝对纵坐标
        let factor = Math.pow(time / duration, 2); // 系数为 1 就是 linear 效果
        if (factor > 1) factor = 1;
        return start + (to - start) * factor;
      }
    };
  },
};

export default methods;
