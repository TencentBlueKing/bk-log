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
  <div class="dynamic-group" v-bkloading="{ isLoading }">
    <div 
      class="dynamic-group-left"
      :style="{ width: isNaN(leftPanelWidth) ? leftPanelWidth : `${leftPanelWidth}px` }">
      <bk-input
        clearable
        right-icon="bk-icon icon-search"
        :placeholder="dynamicGroupPlaceholder"
        v-model="searchValue"
        @change="handleGroupSearchChange">
      </bk-input>
      <bk-virtual-scroll :list="currentGroupData" :item-height="32" class="group-list">
        <template #default="{ data }">
          <li class="group-list-item"
              :class="{ 'active': selectionIds.includes(data[groupOptions.idKey]) }"
              @click="handleGroupClick(data)">
            <div class="item-name">
              <bk-checkbox :checked="selectionIds.includes(data[groupOptions.idKey])"></bk-checkbox>
              <span class="label" :title="data[groupOptions.labelKey]">
                {{ data[groupOptions.labelKey] }}
              </span>
            </div>
          </li>
        </template>
      </bk-virtual-scroll>
    </div>
    <div class="dynamic-group-right ml20">
      <IpListTable
        ref="table"
        :get-search-table-data="getTableData"
        :ip-list-table-config="groupTableConfig"
        :show-selection-column="false"
        :disabled-loading="isLoading"
        :empty-text="emptyText"
        :handle-agent-status="handleAgentStatus">
      </IpListTable>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue, Ref, Emit, Watch } from 'vue-property-decorator'
import { Debounce, defaultSearch } from '../common/util'
import IpSelectorTable from '../components/ip-selector-table.vue'
import IpListTable from './ip-list.vue'
import {
  IGroupDataOptions,
  ITableConfig,
  SearchDataFuncType,
  IipListParams,
  ITableCheckData 
} from '../types/selector-type'
import { TranslateResult } from 'vue-i18n'

// 服务模板
@Component({
  name: 'dynamic-group',
  components: {
    IpSelectorTable,
    IpListTable
  }
})
export default class DynamicGroup extends Vue {
  // 获取组件初始化数据
  @Prop({ type: Function, required: true }) private readonly getDefaultData!: Function
  // 表格搜索数据
  @Prop({ type: Function, required: true }) private readonly getSearchTableData!: SearchDataFuncType
  @Prop({ type: Function }) private readonly getSearchGroupData!: Function
  @Prop({ type: Function }) private readonly getDefaultSelections!: Function
  @Prop({ type: Function }) private readonly handleAgentStatus!: Function

  @Prop({ default: '', type: String }) private readonly dynamicGroupPlaceholder!: string
  @Prop({ default: () => ({
    idKey: 'bk_inst_id',
    childrenKey: 'instances_count',
    labelKey: 'bk_inst_name'
  }), type: Object }) private readonly groupOptions!: IGroupDataOptions
  // 表格字段配置
  @Prop({ default: () => [], type: Array }) private readonly groupTableConfig!: ITableConfig[]
  @Prop({ default: 240, type: [Number, String] }) private readonly leftPanelWidth!: number | string

  @Ref('table') private readonly tableRef!: IpListTable

  private searchValue = ''
  private tplData: any[] = []
  // 默认为true是为了阻止 IpListTable 组件loading
  private isLoading = true
  private selectionIds: (string | number)[] = []
  private emptyText: TranslateResult = ''

  private get currentGroupData() {
    if (this.getSearchGroupData) {
      return this.tplData
    }
    return defaultSearch(this.tplData, this.searchValue)
  }

  @Watch('selectionIds')
  private handleSelectionIdsChange() {
    this.emptyText = !!this.selectionIds.length ? this.$t('查无数据') : this.$t('请选择')
  }

  private created() {
    this.emptyText = this.$t('请选择')
  }

  private mounted() {
    this.handleGetDefaultData()
  }

  private async handleGetDefaultData() {
    try {
      this.isLoading = true
      const data = await this.getDefaultData()
      this.tplData = data || []
      this.handleGetDefaultSelections()
      this.selectionIds.length && this.tableRef && this.tableRef.handleGetDefaultData('selection-change')
    } catch (err) {
      console.log(err)
      return []
    } finally {
      this.isLoading = false
    }
  }

  @Debounce(300)
  private async handleGroupSearchChange() {
    if (this.getSearchGroupData) {
      try {
        const data = await this.getSearchGroupData({ searchValue: this.searchValue })
        this.tplData = data || []
      } catch (err) {
        console.log(err)
        this.tplData = []
      }
    }
  }

  private async getTableData(params: IipListParams, type?: string) {
    try {
      const { idKey = 'bk_inst_id' } = this.groupOptions
      const selections = this.tplData.filter(item => this.selectionIds.includes(item[idKey]))
      const reqParams = {
        selections,
        ...params
      }
      return await this.getSearchTableData(reqParams, type)
    } catch (err) {
      console.log(err)
      return {
        total: 0,
        data: []
      }
    }
  }

  private handleGroupClick(item: any) {
    const { idKey = 'bk_inst_id' } = this.groupOptions
    const itemId = item[idKey]
    const index = this.selectionIds.findIndex(id => id === itemId)
    if (index > -1) {
      this.selectionIds.splice(index, 1)
    } else {
      this.selectionIds.push(itemId)
    }
    this.handleCheckChange()
    this.tableRef && this.tableRef.handleGetDefaultData('selection-change')
  }

  @Emit('check-change')
  private handleCheckChange(): ITableCheckData {
    const { idKey = 'bk_inst_id' } = this.groupOptions
    return {
      selections: this.tplData.filter(item => this.selectionIds.includes(item[idKey]))
    }
  }

  private getChildrenCount(item: any) {
    const { childrenKey = 'nodes_count' } = this.groupOptions
    if (Array.isArray(item[childrenKey])) {
      return item[childrenKey].length
    }
    return item[childrenKey]
  }
  // eslint-disable-next-line @typescript-eslint/member-ordering
  public handleGetDefaultSelections() {
    const { idKey = 'bk_inst_id' } = this.groupOptions
    this.selectionIds = this.tplData.reduce((pre, next) => {
      if (this.getDefaultSelections && !!this.getDefaultSelections(next)) {
        pre.push(next[idKey])
      }
      return pre
    }, [])
  }
}
</script>
<style lang="scss" scoped>
.dynamic-group {
  display: flex;
  color: #63656e;
  &-left {
    display: flex;
    flex-direction: column;
    width: 0;
    .group-list {
      flex: 1;
      margin: 12px 0;
    }
    .group-list-item {
      height: 32px;
      line-height: 32px;
      display: flex;
      justify-content: space-between;
      cursor: pointer;
      padding: 0 10px;
      border-radius: 2px;
      .item-name {
        display: flex;
        align-items: center;
        overflow: hidden;
        .label {
          margin-left: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          flex: 1;
        }
      }
      .count {
        height: 20px;
        line-height: 20px;
        background: #f0f1f5;
        padding: 0 5px;
        display: inline-block;
      }
      &:hover {
        background: #f5f6fa;
      }
    }
  }
  &-right {
    flex: 1;
    overflow: auto;
  }
}
</style>
