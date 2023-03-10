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
  <div class="custom-input">
    <div 
      class="custom-input-left"
      :style="{ width: isNaN(leftPanelWidth) ? leftPanelWidth : `${leftPanelWidth}px` }">
      <bk-input
        class="ip-text"
        :placeholder="$t('多个IP以回车为分隔符')"
        type="textarea"
        v-model="ipdata"
        @change="handleDataChange"
        @keydown.native="handleInputKeydown">
      </bk-input>
      <div class="err-tips" v-if="errList.length">{{ $t('IP格式有误或不存在，检查后重试！') }}</div>
      <bk-button class="ip-parse" theme="primary" outline @click="handleParseIp">
        {{ $t('点击解析') }}
      </bk-button>
    </div>
    <div class="custom-input-right ml20">
      <ip-list-table
        ref="table"
        :get-search-table-data="getTableData"
        :ip-list-table-config="customInputTableConfig"
        :get-default-selections="getDefaultSelections"
        :limit="limit"
        :slot-height="showTableTab ? 36 : 0"
        @check-change="handleTableCheckChange">
        <template #tab>
          <ul class="table-tab" v-if="showTableTab">
            <li 
              :class="['table-tab-item', { active: ipTab.active === item.id }]"
              v-for="item in ipTab.list"
              :key="item.id"
              @click="handleTabClick(item)">
              {{ item.name }}
              <span class="count">{{ `(${tabData[item.id] ? tabData[item.id].length : 0})` }}</span>
            </li>
          </ul>
        </template>
      </ip-list-table>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit, Ref } from 'vue-property-decorator'
import IpSelectorTable from '../components/ip-selector-table.vue'
import { ITableConfig, ITableCheckData, SearchDataFuncType, IClassifyTab } from '../types/selector-type'
import IpListTable from './ip-list.vue'
import { defaultSearch } from '../common/util'

// 手动输入
@Component({
  name: 'custom-input',
  components: {
    IpSelectorTable,
    IpListTable
  }
})
export default class CustomInput extends Vue {
  // 表格搜索数据
  @Prop({ type: Function, required: true }) private readonly getSearchTableData!: SearchDataFuncType
  @Prop({ default: () => [], type: Array }) private readonly customInputTableConfig!: ITableConfig[]
  @Prop({ type: Function }) private readonly getDefaultSelections!: Function
  // 每页数
  @Prop({ default: 10, type: Number }) private readonly limit!: number
  @Prop({ default: 240, type: [Number, String] }) private readonly leftPanelWidth!: number | string
  @Prop({ default: false, type: Boolean }) private readonly showTableTab!: boolean

  @Ref('table') private readonly tableRef!: IpListTable

  private errList: string[] = []
  private temErrList: string[] = []
  private goodList: string[] = []
  private ipdata = ''
  private ipMatch = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])(\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])){3}$/

  private ipTab: IClassifyTab = {
    active: 'inner',
    list: []
  }
  private tabData = {
    inner: [],
    outer: [],
    other: []
  }

  private created() {
    this.ipTab.list = [
      {
        id: 'inner',
        name: this.$t('内网IP')
      },
      {
        id: 'outer',
        name: this.$t('外网IP')
      },
      {
        id: 'other',
        name: this.$t('其他IP')
      }
    ]
  }

  private handleTabClick(item: any) {
    this.ipTab.active = item.id
    this.tableRef && this.tableRef.handleGetDefaultData()
  }

  @Emit('check-change')
  private handleTableCheckChange(data: ITableCheckData) {
    return data
  }

  private handleDataChange() {
    this.goodList = []
    this.errList = []
  }

  private handleParseIp() {
    if (this.ipdata && this.ipdata.length) {
      this.ipTab.active = 'inner'
      const ipList = this.ipdata.split(/[\r\n]+/gm)
      const errList = new Set<string>()
      const goodList = new Set<string>()
      ipList.forEach((ip) => {
        ip = ip.trim()
        if (ip.match(this.ipMatch)) {
          goodList.add(ip)
        } else {
          ip.length > 0 && errList.add(ip)
        }
      })
      if (errList.size > 0 && goodList.size === 0) {
        this.ipdata = Array.from(errList).join('\n')
        this.errList = Array.from(errList)
      } else {
        // 缓存当前错误IP
        this.temErrList = Array.from(errList)
      }
      this.goodList = Array.from(goodList)
      this.goodList.length && this.tableRef.handleGetDefaultData('input-change')
    }
  }

  private async getTableData(params: any, type = '') {
    try {
      if (!this.goodList.length) return { total: 0, data: [] }
      const reqParams = {
        ipList: this.goodList,
        ...params
      }
      if (type === 'input-change') {
        // 解析输入IP
        await this.handleParseDataChange(reqParams, type)
      }
      const data = defaultSearch(this.tabData[this.ipTab.active], params.tableKeyword || '')
      return {
        total: data.length,
        data
      }
    } catch (err) {
      console.log(err)
      return {
        total: 0,
        data: []
      }
    }
  }

  private async handleParseDataChange(reqParams: any, type: string) {
    const res = await this.getSearchTableData(reqParams, type)
    // 分类数据
    this.tabData = res.data.reduce((pre, next) => {
      if (!!next.is_innerip) {
        pre.inner.push(next)
      } else if (!!next.is_outerip) {
        pre.outer.push(next)
      } else if (!!next.is_external_ip) {
        pre.other.push(next)
      }
      return pre
    }, { inner: [], outer: [], other: [] })

    this.goodList.forEach((ip) => {
      // 对比返回值，找到全部错误IP
      !res.data.some(item => item.ip === ip) && this.temErrList.push(ip)
    })
    this.errList = [...this.temErrList]
    this.ipdata = this.errList.join('\n')
    this.temErrList = []
    this.ipTab.active = ['inner', 'outer', 'other'].find(item => this.tabData[item] && this.tabData[item].length)
    setTimeout(() => {
      // 默认选择全部数据
      this.tableRef.selectionAllData()
    }, 0)
  }

  private handleInputKeydown(e: KeyboardEvent) {
    if (e.key === 'enter') {
      return true
    }
    if (e.ctrlKey || e.shiftKey || e.metaKey) {
      return true
    }
    if (!e.key.match(/[0-9.\s|,;]/) && !e.key.match(/(backspace|enter|ctrl|shift|tab)/mi)) {
      e.preventDefault()
    }
  }

  // eslint-disable-next-line @typescript-eslint/member-ordering
  public handleGetDefaultSelections() {
    this.tableRef && this.tableRef.handleGetDefaultSelections()
  }
}
</script>

<style lang="scss" scoped>
  :deep(.bk-textarea-wrapper) {
    height: 100%;

    .bk-form-textarea {
      height: 100%;
    }
  }

  .custom-input {
    display: flex;
    color: #63656e;

    &-left {
      // flex-basis: 240px;
      display: flex;
      flex-direction: column;
      padding-bottom: 26px;

      .ip-text {
        flex: 1;
      }

      .ip-parse {
        margin-top: 16px;
        font-size: 12px;
      }

      .err-tips {
        width: 100%;
        color: #ea3636;
        text-align: left;
        margin-top: 2px;
      }
    }

    &-right {
      flex: 1;
      overflow: auto;
    }
  }
</style>
