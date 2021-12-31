/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import { TranslateResult } from 'vue-i18n'
import Vue, { VNode } from 'vue'

export type IpType = 'TOPO' | 'INSTANCE' | 'SERVICE_TEMPLATE' | 'SET_TEMPLATE' | 'DYNAMIC_GROUP'

// tab数据源
export interface IPanel {
  name: string // tab唯一标识（要和components目录的文件名保持一致，作为后面动态组件的name）
  label: string | TranslateResult // tab默认显示文本
  hidden?: boolean // tab是否显示
  disabled?: boolean // tab是否禁用
  keepAlive?: boolean // 是否缓存
  tips?: string | TranslateResult
  component?: Vue // 组件对象（默认根据name从layout里面获取）
  type?: IpType // 当前tab对于的类型（目前对于后端来说只有两种，只是前端选择方式不一样）
}

export interface IEventsMap {
  [key: string]: Function
}

export interface IMenu {
  id: string | number
  label: string | TranslateResult
  readonly?: boolean
  disabled?: boolean
  hidden?: boolean
}

export interface INodeData extends IMenu {
  data: any // 原始数据
  children?: INodeData[]
}

export interface IPreviewData {
  id: IpType
  name: string | TranslateResult
  data: any[]
  dataNameKey?: string
}

export interface ISearchData extends INodeData {
  path?: string
}

export type IPerateFunc = (item: IPreviewData) => IMenu[]

export interface ILayoutComponents {
  [key: string]: Vue
}

export interface ISearchDataOption {
  idKey: string
  nameKey: string
  pathKey: string
}

export interface IPreviewDataOption {
  nameKey?: string
}

export interface ITreeNode {
  id: string | number
  name: string
  level: string | number
  children: ITreeNode[]
  data?: any
  parent?: ITreeNode
}

export interface ITableConfig {
  prop: string
  label: string | TranslateResult
  render?: (row: any, column: any, $index: number) => VNode
  hidden?: boolean
  minWidth?: number
}

export interface IAgentStatusData {
  count?: number
  status: string
  display: string | TranslateResult
  errorCount?: number
}
// 0 未选 1 半选 2 全选
export type CheckValue = 0 | 1 | 2

export type CheckType = 'current' | 'all'

export interface IPagination {
  limit: number
  count: number
  current: number
  limitList: any[]
}

export interface ITemplateDataOptions {
  idKey?: string
  labelKey?: string
  childrenKey?: string
}

export interface IGroupDataOptions {
  idKey?: string
  labelKey?: string
  childrenKey?: string
}

/**
 *layout组件搜索函数的类型
 * @param params 接口参数
 */
// eslint-disable-next-line max-len
export type SearchDataFuncType = (params: any, type?: string) => Promise<{ total: number, data: any[] }>

export interface IipListParams {
  current: number
  limit: number
  tableKeyword: string
}

export interface ITableCheckData {
  excludeData?: any[]
  selections: any[]
  checkType?: CheckType
  checkValue?: CheckValue
}

export interface IClassifyTab {
  active: string
  list: { id: 'inner' | 'outer' | 'other', name: TranslateResult }[]
}
