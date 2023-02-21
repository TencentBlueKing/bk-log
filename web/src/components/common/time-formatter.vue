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
  <div class="time-format-container">
    <span class="switch-label">{{ $t('时间') }}</span>
    <bk-switcher
      theme="primary"
      :value="isFormatDate"
      @change="handleChange"
      v-bk-tooltips="$t('btn.timeFormatTips')"
    ></bk-switcher>
    <!-- <transition name="fade">
      <span class="time-zone-text" v-if="isFormatDate">{{$t('retrieve.time_zone') + timeZone}}</span>
    </transition> -->
  </div>
</template>

<script>
import jsCookie from 'js-cookie';

export default {
  data() {
    return {
      timeZone: new Date().toString()
        .slice(24, 33),
    };
  },
  computed: {
    // 是否转换日期类型字段格式
    isFormatDate() {
      return this.$store.state.isFormatDate;
    },
  },
  methods: {
    handleChange(val) {
      jsCookie.set('operation', String(val));
      this.$store.commit('updateIsFormatDate', val);
    },
  },
};
</script>

<style lang="scss" scoped>
  .time-format-container {
    display: flex;
    align-items: center;
    font-size: 14px;
    color: #63656e;

    .switch-label {
      margin-right: 6px;
      color: #63656e;
      font-size: 12px;
    }

    .time-zone-text {
      margin-left: 8px;
    }
  }
</style>
