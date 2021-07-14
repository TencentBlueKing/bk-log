<!--
  - Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for BK-LOG 蓝鲸日志平台:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div class="auth-page-container">
    <img src="../../images/lock-radius.svg" alt="lock" class="lock-icon">
    <div class="title">{{authNames + $t('无权限访问')}}</div>
    <div class="detail">{{$t('你没有相应资源的访问权限')}}</div>
    <bk-button
      v-if="info.apply_url"
      class="king-button"
      theme="primary"
      @click="confirmPageApply">{{$t('去申请')}}</bk-button>
  </div>
</template>

<script>
export default {
  props: {
    info: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      authNames: '',
    };
  },
  created() {
    try {
      const actionNames = this.info.apply_data.actions.map(action => action.name);
      this.authNames = `【${actionNames.join('，')}】`;
    } catch (e) {
      console.warn('403返回数据格式不对', e);
    }
  },
  methods: {
    confirmPageApply() {
      window.open(this.info.apply_url);
    },
  },
};
</script>

<style lang="scss" scoped>
  .auth-page-container {
    display: flex;
    flex-flow: column;
    align-items: center;
    height: 100%;

    .lock-icon {
      margin-top: 128px;
    }

    .title {
      margin-top: 26px;
      line-height: 28px;
      font-size: 20px;
      font-weight: 500;
      color: #313238;
    }

    .detail {
      margin-top: 30px;
      line-height: 20px;
      font-size: 14px;
      color: #979ba5;
    }

    .king-button {
      margin-top: 30px;
    }
  }
</style>
