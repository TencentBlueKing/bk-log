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
  <div class="topo-search">
    <bk-input
      clearable
      right-icon="bk-icon icon-search"
      :placeholder="placeholder"
      :value="value"
      @change="handleValueChange"
      @click.native="handleInputClick">
    </bk-input>
    <!--搜索结果-->
    <div class="topo-search-result"
         v-show="showPanel"
         v-bk-clickoutside="handleClickoutside"
         :style="{ width: `${resultWidth}px` }">
      <template v-if="searchData.length">
        <div class="result-title">
          <span>{{ $t('搜索结果') }}</span>
          <bk-button text class="select-all" @click="handleCheckOrClearAll">
            {{ searchData.length === selections.length ? $t('取消全选') : $t('全选') }}
          </bk-button>
        </div>
        <bk-virtual-scroll
          :list="searchData"
          :item-height="58"
          :style="{ height: `${height}px` }">
          <template #default="{ data }">
            <div class="result-panel-item" @click="handleItemClick(data)">
              <div class="item-left">
                <span class="item-left-name">
                  {{ data.label }}
                </span>
                <span class="item-left-path">
                  {{ data.path }}
                </span>
              </div>
              <div class="item-right">
                <span :class="['checkbox', { 'is-checked': getCheckStatus(data) }]"></span>
              </div>
            </div>
          </template>
        </bk-virtual-scroll>
      </template>
      <div v-else class="result-empty">
        {{ $t('无数据') }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Model, Emit, Watch } from 'vue-property-decorator'
import { Debounce } from '../common/util'
import { ISearchData, ISearchDataOption } from '../types/selector-type'

@Component({
  name: 'topo-search'
})
export default class TopoSearch extends Vue {
  @Model('change', { default: '', type: String }) private readonly value!: string
  @Prop({ default: '', type: String }) private readonly placeholder!: string
  @Prop({ type: Function, required: true }) private readonly searchMethod!: Function
  @Prop({ default: 380, type: [Number, String] }) private readonly resultWidth!: number | string
  @Prop({ default: 300, type: Number }) private readonly height!: number
  @Prop({ default: () => ({}), type: Object }) private readonly options!: ISearchDataOption
  @Prop({ default: () => [], type: Array }) private readonly defaultSelectionIds!: (string|number)[]

  private showPanel = false
  private searchData: ISearchData[] = []
  private selections: ISearchData[] = []
  private isLoading = false

  private get dataOptions() {
    const options: ISearchDataOption = {
      idKey: 'id',
      nameKey: 'name',
      pathKey: 'node_path'
    }
    return Object.assign(options, this.options)
  }

  @Watch('defaultSelectionIds', { immediate: true })
  private handleDefaultSelectionsChange() {
    this.selections = this.searchData.filter(item => this.defaultSelectionIds.includes(item.id))
  }

  @Emit('change')
  private handleValueChange(v: string) {
    this.handleSearch(v)
    return v
  }

  @Emit('hide')
  private handleClickoutside() {
    this.showPanel = false
  }
  @Emit('show')
  private handleInputClick() {
    this.value !== '' && (this.showPanel = true)
  }

  @Emit('check-change')
  private handleItemClick(item: ISearchData) {
    const index = this.selections.findIndex(select => select.id === item.id)
    if (index > -1) {
      this.selections.splice(index, 1)
    } else {
      this.selections.push(item)
    }
    return {
      selections: this.selections.map(select => select.data),
      excludeData: this.searchData.reduce((pre, next) => {
        if (this.selections.some(item => item.id === next.id)) return pre

        pre.push(next.data)
        return pre
      }, [])
    }
  }

  @Emit('check-change')
  private handleCheckOrClearAll() {
    this.selections = this.selections.length === this.searchData.length
      ? []
      : [...this.searchData]
    return {
      selections: this.selections.map(select => select.data),
      excludeData: !!this.selections.length ? [] : this.searchData.map(item => item.data)
    }
  }

  private getCheckStatus(item: ISearchData) {
    return this.selections.some(select => select.id === item.id)
  }

  // eslint-disable-next-line @typescript-eslint/member-ordering
  @Debounce(300)
  public async handleSearch(keyword: string) {
    this.showPanel = true
    if (!this.searchMethod || keyword === '') {
      this.searchData = []
      this.showPanel = false
      return
    }
    this.isLoading = true
    const data = await this.searchMethod(keyword).catch((err: any) => {
      console.log(err)
      return []
    })
    this.isLoading = false

    const { idKey, nameKey, pathKey } = this.dataOptions
    this.searchData = Array.isArray(data)
      ? data.map((item, index) => {
        const data: ISearchData = {
          data: item,
          id: item[idKey] || index,
          label: item[nameKey],
          path: pathKey ? item[pathKey] : ''
        }
        return data
      })
      : []

    this.selections = this.searchData.filter(item => this.defaultSelectionIds.includes(item.id))
  }
}
</script>

<style lang="scss" scoped>
  .topo-search {
    position: relative;

    &-result {
      position: absolute;
      top: 34px;
      min-width: 100%;
      height: auto;
      background: #fff;
      margin: 0;
      z-index: 2500;
      border-radius: 2px;
      border: 1px solid #dcdee5;
      transition: all .3s ease;
      box-shadow: 0 2px 6px rgba(51,60,72,.1);
      text-align: left;

      .result-title {
        display: flex;
        justify-content: space-between;
        color: #c4c6cc;
        height: 32px;
        line-height: 32px;
        padding: 0 20px;

        .select-all {
          font-size: 12px;
        }
      }

      .result-panel {
        overflow: auto;
      }

      .result-panel-item {
        display: flex;
        justify-content: space-between;
        height: 58px;
        padding: 0 20px;
        cursor: pointer;

        &:hover {
          background: #e1ecff;
        }

        .item-left {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;

          &-name {
            font-weight: 700;
            color: #63656e;
            line-height: 16px;
          }

          &-path {
            color: #979ba5;
            line-height: 16px;
          }
        }

        .item-right {
          display: flex;
          flex-direction: column;
          justify-content: center;

          .checkbox {
            position: relative;
            display: inline-block;
            vertical-align: middle;
            width: 16px;
            height: 16px;
            border: 1px solid #979ba5;
            border-radius: 2px;

            &.is-checked {
              border-color: #3a84ff;
              background-color: #3a84ff;
              background-clip: border-box;

              &::after {
                content: '';
                position: absolute;
                top: 1px;
                left: 4px;
                width: 4px;
                height: 8px;
                border: 2px solid #fff;
                border-left: 0;
                border-top: 0;
                transform-origin: center;
                transform: rotate(45deg) scaleY(1);
              }
            }
          }
        }
      }

      .result-empty {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
      }
    }
  }
</style>
