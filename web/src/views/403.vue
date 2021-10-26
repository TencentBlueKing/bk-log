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
  <div class="exception-box">
    <!-- 请联系业务管理人员申请业务权限 -->
    <template v-if="$route.name === 'notTraceIndex'">
      <div class="notTraceIndex">
        <img src="../../src/images/nodata.png" alt="">
        <p>{{ $t('当前业务没有接入调用链日志，') }}<span @click="notTraceIndex">{{ $t('了解接入详情') }}</span></p>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  methods: {
    notTraceIndex() {
      this.$router.push({
        name: 'log-index-set',
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .exception-box {
    text-align: center;
    margin: auto;

    img {
      max-width: 25%;
      margin: 150px 0 10px;
    }
  }

  .notTraceIndex {
    margin-top: 100px;

    p {
      font-size: 14px;

      span {
        color: #318dff;
        cursor: pointer;
      }
    }
  }
</style>
