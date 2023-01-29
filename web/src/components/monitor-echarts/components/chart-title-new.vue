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
  <div class="title-wrapper">
    <div
      ref="chartTitle"
      class="chart-title"
      tabindex="0"
      @click.stop="handleShowMenu"
      @blur="showMenu = false">
      <div class="main-title">
        <span class="bk-icon icon-down-shape" :class="{ 'is-flip': isFold }"></span>
        <div class="title-name">{{title}}</div>
      </div>
      <div v-if="subtitle" class="sub-title">
        {{subtitle}}
      </div>
    </div>
    <bk-spin v-if="loading && !isFold" class="chart-spin"></bk-spin>
    <div class="menu-list" v-else-if="!isFold">
      <span 
        class="log-icon icon-xiangji" 
        @click.stop="handleMenuClick({id: 'screenshot'})"
        data-test-id="generalTrendEcharts_span_downloadEcharts">
      </span>
    </div>
    <!-- <chart-menu
      v-show="showMenu"
      :list="menuList"
      @menu-click="handleMenuClick"
      :style="{ left: menuLeft + 'px' }">
    </chart-menu> -->
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref } from 'vue-property-decorator'
import ChartMenu from './chart-menu.vue'

@Component({
  name: 'chart-title',
  components: {
    ChartMenu
  }
})
export default class ChartTitle extends Vue {
  @Prop({ default: '' }) title: string
  @Prop({ default: '' }) subtitle: string
  @Prop({ default: () => [] }) menuList: string[]
  @Prop({ default: localStorage.getItem('chartIsFold') === 'true' }) isFold: boolean
  @Prop({ default: true }) loading: boolean
  @Ref('chartTitle') chartTitleRef: HTMLDivElement
  private showMenu = false
  private menuLeft = 0
  handleShowMenu(e: MouseEvent) {
    this.$emit('toggle-expand', !this.isFold)

    // this.showMenu = !this.showMenu
    // const rect = this.chartTitleRef.getBoundingClientRect()
    // this.menuLeft = rect.width  - 185 < e.layerX ? rect.width  - 185 : e.layerX
  }
  handleMenuClick(item) {
    this.showMenu = false
    this.$emit('menu-click', item)
  }
}
</script>
<style lang="scss" scoped>
  .title-wrapper {
    position: relative;
    width: 100%;
    flex: 1;

    .chart-title {
      padding: 4px 10px;
      margin-left: -10px;
      border-radius: 2px;
      color: #63656e;
      font-size: 12px;
      cursor: pointer;

      &:hover {
        .main-title {
          &::after {
            display: flex;
          }
        }
      }

      .main-title {
        font-weight: 700;
        display: flex;
        align-items: center;
        flex-wrap: nowrap;

        .title-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          line-height: 20px;
          height: 20px;
        }

        .icon-down-shape {
          margin-right: 8px;
          transition: transform .3s;

          &.is-flip {
            transform: rotate(-90deg);
            transition: transform .3s;
          }
        }

        &::after {
          /* stylelint-disable-next-line declaration-no-important */
          font-family: 'icon-monitor' !important;
          content: '\e61c';
          font-size: 20px;
          width: 24px;
          height: 16px;
          align-items: center;
          justify-content: center;
          color: #979ba5;
          margin-right: auto;
          display: none;
        }
      }

      .sub-title {
        line-height: 16px;
        height: 16px;
        color: #979ba5;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .menu-list {
      position: absolute;
      top: 24px;
      right: 36px;

      .log-icon {
        font-size: 14px;
        color: #979ba5;
        cursor: pointer;
      }
    }

    .chart-spin {
      position: absolute;
      top: 24px;
      right: 36px;
    }
  }
</style>
