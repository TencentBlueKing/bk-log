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
  <div class="chart-tools">
    <i class="icon-monitor icon-mc-mark tools-icon" @click.self="handleCollectChart"></i>
    <i class="icon-monitor icon-mc-camera tools-icon" @click.self="handleStoreImage"></i>
    <i v-if="needFullScreen" class="icon-monitor icon-fullscreen tools-icon" :class="[isFullScreen ? 'icon-unfull-screen' : 'icon-fullscreen']" @click.self="handleFullScreen"></i>
    <i v-if="moreList.length" style="margin-right: 0" class="icon-monitor icon-mc-more tools-icon" @click="handleMoreClick"></i>
    <div v-show="false">
      <ul class="tool-list" ref="moreTools">
        <template v-for="item in moreToolsList">
          <li
            class="tool-list-item"
            v-show="moreList.indexOf(item.id) > -1"
            :key="item.name"
            @click="handleMoreItemClick(item)">{{!item.checked ? item.name : item.nextName || item.name}}
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>
<script lang="ts">
import { Vue, Component, Prop, Emit } from 'vue-property-decorator'
import { IMoreToolItem, MoreChartToolItem } from '../options/type-interface'
@Component({
  name: 'ChartTools'
})
export default class ChartTools extends Vue {
  @Prop({ default: false }) needFullScreen: boolean
  @Prop({ default: false }) isFullScreen: boolean
  @Prop({ default: () => [] }) moreList: MoreChartToolItem[]
  moreToolInstance: any = null
  moreToolsList: IMoreToolItem[] = []
  created() {
    this.moreToolsList = [
      {
        name: '检索',
        checked: false,
        id: 'explore'
      },
      {
        name: 'Y轴固定最小值0',
        checked: false,
        id: 'set',
        nextName: 'Y轴自适应'
      },
      {
        name: '添加策略',
        checked: false,
        id: 'strategy'
      },
      {
        name: '面积图',
        checked: false,
        id: 'area',
        nextName: '线性图'
      }
    ]
  }
  beforeDestroy() {
    this.handleDestroy()
  }
  @Emit('store-img')
  handleStoreImage(e) {
    return e
  }
  @Emit('collect-chart')
  handleCollectChart(e) {
    return e
  }
  @Emit('full-screen')
  handleFullScreen(e) {
    return e
  }
  handleToArea() {
    this.$emit('transform-area')
  }
  handleMoreClick(e: MouseEvent) {
    this.moreToolInstance = this.$bkPopover(e.target, {
      content: this.$refs.moreTools,
      trigger: 'click',
      arrow: false,
      theme: 'light common-monitor monitor-chart',
      maxWidth: 520,
      offset: '50, -6',
      sticky: true,
      duration: [275, 0],
      interactive: true
    })
    this.moreToolInstance && this.moreToolInstance.show(100)
  }
  @Emit('tool-item')
  handleMoreItemClick(item: IMoreToolItem) {
    item.checked = !item.checked
    this.handleDestroy()
    return { ...item }
  }
  handleDestroy() {
    if (this.moreToolInstance) {
      this.moreToolInstance.hide(0)
      this.moreToolInstance.destroy()
      this.moreToolInstance = null
    }
  }
}
</script>
<style lang="scss" scoped>
  .chart-tools {
    display: flex;

    .tools-icon {
      margin-right: 8px;

      &:hover {
        cursor: pointer;
        color: #3a84ff;
      }
    }
  }

  .monitor-chart-theme {
    /* stylelint-disable-next-line declaration-no-important */
    background: white !important;
    z-index: 999;

    .tool-list {
      display: flex;
      flex-direction: column;
      padding: 6px 0;
      overflow: auto;
      background-color: white;

      &-item {
        flex: 0 0 32px;
        display: flex;
        align-items: center;
        padding: 0 10px 0 15px;
        color: #63656e;

        &:hover {
          cursor: pointer;
          color: #3a84ff;
          background-color: #eaf3ff;
        }
      }
    }
  }
</style>
