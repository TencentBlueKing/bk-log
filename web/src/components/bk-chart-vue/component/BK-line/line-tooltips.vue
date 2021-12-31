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
  <div id="tooltips">
    <template v-for="(item, ind) in dataList">
      <span
        :key="ind"
        :class="['tooltips-item', { 'tooltips-disabled': !item.status }]"
        @click="clickTooltips(item, ind)">
        <i
          class="tooltips-tips"
          :style="`background: ${item.backgroundColor}`"
          @click.shift.stop="clickShiftTooltips(item, ind, 'shift')"
        ></i><span @click.shift.stop="clickShiftTooltips(item, ind, 'shift')">{{item.label}}</span></span>
    </template>
  </div>
</template>
<script>
import BaseSettings from '../base-settings';
export default {
  name: 'line-tooltips',
  extends: BaseSettings,
  props: {
    dataList: { type: Array, default: () => ([]) },
  },
  methods: {
    clickTooltips(item, ind) {
      this.$emit('clickTooltips', item, ind);
    },
    clickShiftTooltips(item, ind, type) {
      this.$emit('clickTooltips', item, ind, type);
    },
  },
};
</script>
<style lang="scss" scoped>
  #tooltips {
    height: 60px;
    margin-top: 20px;
    overflow-y: auto;
    padding: 0 30px;

    .tooltips-item {
      display: inline-block;
      height: 20px;
      line-height: 20px;
      font-size: 12px;
      margin-right: 32px;
      padding-bottom: 10px;
      cursor: pointer;
      color: #6e7079;

      .tooltips-tips {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
        margin-top: 1px;
      }
    }

    .tooltips-disabled {
      color: #dcdee5;

      .tooltips-tips {
        /* stylelint-disable-next-line declaration-no-important */
        background: #dcdee5 !important;
      }
    }
  }
</style>
