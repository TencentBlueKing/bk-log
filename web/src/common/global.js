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

// 全局函数
const getTopWindow = function () {
  try {
    if (window.top?.document) {
      console.log('TOP窗口对象获取成功');
      return window.top;
    }
    console.log('TOP窗口对象获取失败，已切换到当前窗口对象');
    return window;
  } catch (err) {
    console.log(err);
    console.log('TOP窗口对象获取失败，已切换到当前窗口对象');
    return window;
  }
};

const topWindow = getTopWindow();
const openLoginDialog = function () {
  const loginData = {
    loginUrl: '',
    width: '400',
    height: '400',
  };
  window.parent.bus.$emit('show-login-modal', loginData);
};
const closeLoginDialog = function () {
  try {
    window.parent.bus.$emit('close-login-modal');
    window.parent.location.reload();
  } catch (err) {
    console.log(err);
  }
};

try {
  window.top.BLUEKING.corefunc.open_login_dialog = openLoginDialog;
  window.top.BLUEKING.corefunc.close_login_dialog = closeLoginDialog;
  console.log('弹窗方法已注册到TOP窗口', window.top.BLUEKING.corefunc.close_login_dialog);
} catch (_) {
  topWindow.BLUEKING = {
    corefunc: {
      open_login_dialog: openLoginDialog,
      close_login_dialog: closeLoginDialog,
    },
  };
  window.open_login_dialog = openLoginDialog;
  window.close_login_dialog = closeLoginDialog;
  console.log('弹窗方法已注册到当前窗口', window.close_login_dialog);
}
