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
  <table v-if="legendType === 'table'" class="chart-legend">
    <colgroup>
      <col style="width: 100%" />
    </colgroup>
    <thead>
      <tr>
        <th
          v-for="title in headList"
          :key="title"
          style="text-align: right"
          @click="handleSortChange(title)">
          {{title}}
          <span class="caret-wrapper">
            <i 
              class="sort-caret is-asc"
              @click.self.stop="handleSortChange(title, 1)" 
              :class="{ active: sortTitle === title && sort === 1 }">
            </i>
            <i 
              class="sort-caret is-desc"
              @click.self.stop="handleSortChange(title, 2)"
              :class="{ active: sortTitle === title && sort === 2 }">
            </i>
          </span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in list" :key="index">
        <td v-for="title in headList" :key="title">
          <div
            class="content-wrapper"
            :style="{ 'width': title === 'Min' ? '228px' : '68px' }">
            <div
              v-if="title === 'Min'"
              class="legend-metric"
              @click="(e) => handleLegendEvent(e,'click', item)"
              @mouseenter="(e) => handleLegendEvent(e,'highlight', item)"
              @mouseleave="(e) => handleLegendEvent(e,'downplay', item)">
              <span class="metric-label" :style="{ backgroundColor: item.show ? item.color : '#ccc' }"></span>
              <span 
                v-bk-overflow-tips="{ placement: 'top', 'offset': '100, 0' }" class="metric-name" 
                :style="{ color: item.show ? '#63656e' : '#ccc' }">
                {{item.name}}
              </span>
            </div>
            <div class="legend-value">
              {{item[title.toLocaleLowerCase()]}}
            </div>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
  <div v-else class="common-legend">
    <div
      class="common-legend-item"
      v-for="(legend, index) in legendData"
      :key="index"
      @click="(e) => handleLegendEvent(e,'click', legend)"
      @mouseenter="(e) => handleLegendEvent(e,'highlight', legend)"
      @mouseleave="(e) => handleLegendEvent(e,'downplay', legend)">
      <span class="legend-icon" :style="{ backgroundColor: legend.show ? legend.color : '#ccc' }"></span>
      <div class="legend-name" :style="{ color: legend.show ? '#63656e' : '#ccc' }">{{legend.name}}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit, Watch } from 'vue-property-decorator'
import { ILegendItem } from '../options/type-interface'

@Component({
  name: 'chart-legend'
})

export default class ChartLegend extends Vue {
  @Prop({ required: true }) readonly legendData: ILegendItem[]
  @Prop({ default: 'common' }) readonly legendType: 'common' | 'table'
  headList: string[] = ['Min', 'Max', 'Avg']
  list:  ILegendItem[] = []
  sort = 0
  sortTitle = ''
  @Watch('legendData', { immediate: true })
  handleLegendDataChange() {
    this.handleSortChange()
  }

  @Emit('legend-event')
  handleLegendEvent(e, actionType: string, item: ILegendItem) {
    let eventType = actionType
    if (e.shiftKey && actionType === 'click') {
      eventType = 'shift-click'
    }
    return { actionType: eventType, item }
  }
  handleSortChange(title?: 'Min'| 'Max'| 'Avg', sort?) {
    this.sortTitle = title || ''
    if (title) {
      if (typeof sort === 'number') {
        this.sort = sort
      } else {
        this.sort = (this.sort + 1) % 3
      }
    }
    if (this.sort === 0 || !title) {
      this.list =  this.legendData
      return
    }
    const sortId = title.toLocaleLowerCase()
    this.list = this.legendData.slice().sort((a, b) => {
      const [aVal] = (a[sortId].match(/\d+\.?\d+/) || [0])
      const [bVal] = (b[sortId].match(/\d+\.?\d+/) || [0])
      if (this.sort === 1) {
        return +aVal - +bVal
      }
      return +bVal - +aVal
    })
  }
}
</script>

<style lang="scss" scoped>
  .chart-legend {
    font-size: 12px;
    border-collapse: collapse;
    line-height: 26px;
    color: #63656e;
    overflow: auto;
    user-select: none;
    min-width: 400px;

    tr {
      height: 26px;
    }

    thead tr,
    tr:nth-child(even) {
      background: #f5f6fa;
    }

    th {
      white-space: nowrap;
      padding: 0 12px;
      font-weight: bold;

      &:hover {
        cursor: pointer;
        background-color: #f0f1f5;
      }

      .caret-wrapper {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        height: 20px;
        flex: 20px 0 0;
        vertical-align: middle;
        cursor: pointer;
        position: relative;
        top: -1px;
        margin-left: 4px;

        .sort-caret {
          width: 0;
          height: 0;
          border: 5px solid transparent;
          position: absolute;
          margin-left: 4px;

          &:hover {
            cursor: pointer;
          }

          &.is-asc {
            border-bottom-color: #c0c4cc;
            top: -1px;

            &.active {
              border-bottom-color: #63656e;
            }
          }

          &.is-desc {
            border-top-color: #c0c4cc;
            bottom: -1px;

            &.active {
              border-top-color: #63656e;
            }
          }
        }
      }
    }

    td {
      display: table-cell;
      white-space: nowrap;
      padding: 0 6px;
      text-align: right;

      .content-wrapper {
        display: flex;
        align-items: center;
        text-align: right;

        .legend-metric {
          text-align: left;
          margin-right: 9px;
          display: inline-flex;
          align-items: center;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;

          .metric-label {
            display: inline-block;
            width: 12px;
            height: 4px;
            background-color: violet;
            margin-right: 6px;
            min-width: 12px;
          }

          .metric-name {
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
          }

          &:hover {
            color: #999;
            cursor: pointer;
          }
        }

        .legend-value {
          margin-left: auto;
          text-align: right;
        }
      }
    }
  }

  .common-legend {
    &-item {
      float: left;
      white-space: nowrap;
      margin-left: 10px;
      display: flex;
      align-items: center;
      line-height: 16px;
      font-size: 12px;

      .legend-icon {
        width: 12px;
        height: 4px;
        background-color: violet;
        margin-right: 6px;
      }

      &:hover {
        color: #999;
        cursor: pointer;
      }
    }
  }
</style>
