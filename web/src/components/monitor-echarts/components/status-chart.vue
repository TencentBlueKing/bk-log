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
  <ul class="status-chart">
    <template v-if="series.length">
      <template v-for="(item, index) in series">
        <bk-popover
          :content="statusList[item.status]"
          placement="top"
          :key="index">
          <li
            class="status-chart-item"
            :class="`status-${item.status}`">
            {{item.value}}
          </li>
        </bk-popover>
      </template>
    </template>
    <div v-else class="status-chart-empty">
      --
    </div>
  </ul>
</template>
<script lang="ts">
import { Vue, Prop, Component } from 'vue-property-decorator'
@Component({
  name: 'StatusChart'
})
export default class StatusChart extends Vue {
  // 端口列表
  @Prop({ default() {
    return []
  } }) readonly series: {value: string, status: string}[]
  private statusList: any[]
  created() {
    this.statusList = [this.$t('正常'), this.$t('停用'), this.$t('异常')]
  }
}
</script>
<style lang="scss" scoped>
  $statusFontColor: #10c178 #c4c6cc #ffb848;
  $statusBgColor: #e7f9f2 #f0f1f5 #ffe8c3;

  .status-chart {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 0;

    &-item {
      display: flex;
      padding: 5px 14px;
      align-items: center;
      justify-content: center;
      line-height: 20px;
      font-size: 12px;
      border-radius: 2px;
      margin: 0 2px 2px 0;
      height: 30px;

      @for $i from 0 through 2 {
        &.status-#{$i} {
          background: nth($statusBgColor, $i + 1);
          color: nth($statusFontColor, $i + 1);

          &:hover {
            background: nth($statusFontColor, $i + 1);
            color: white;
            cursor: pointer;
          }
        }
      }
    }

    &-empty {
      color: #dcdee5;
      font-size: 50px;
      line-height: 30px;
    }
  }
</style>
