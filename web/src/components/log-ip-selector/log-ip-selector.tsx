/* eslint-disable no-unused-vars */
/* eslint-disable camelcase */
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

import { Component as tsc } from 'vue-tsx-support';
import { Component, Prop } from 'vue-property-decorator';
import $http from '../../api';
import create from '@blueking/ip-selector/dist/vue2.6.x';
import '@blueking/ip-selector/dist/styles/vue2.6.x.css';
import { VNode } from 'vue';
const BkIpSelector = create({});
export type CommomParams = Record<string, any>;
export type IObjectType = 'HOST' | 'SERVICE';
export type INodeType  = 'TOPO' | 'INSTANCE';

export interface IMeta {
  bk_biz_id: number
  scope_id: string
  scope_type: 'biz'
}

export interface INode {
  instance_id: number
  object_id: 'module' | 'set' | 'biz'
  meta: IMeta
}
export interface IHost {
  host_id: number
  meta: IMeta
}
export interface ITarget {
  // node_type = 'INSTANCE' => bk_host_id  ||  'TOPO' => bk_obj_id && bk_inst_id
  bk_biz_id: number,
  bk_obj_id?: 'set' | 'module'
  bk_inst_id?: number
  bk_host_id?: number
  biz_inst_id?: string
  path?: string
  children?: ITarget[];
  meta?: IMeta
}

export interface ITreeItem extends INode {
  count: number
  expanded: boolean
  object_name: string
  instance_name: string
  child: ITreeItem[]
}
export interface IFetchNode {
  node_list: INode[]
}

export type IStatic = 'alive_count' | 'not_alive_count' | 'total_count';

export type IStatistics = Record<IStatic, number>;

export interface IQuery {
  start?: number
  page_size?: number
  search_content?: string
  node_list: INode[];
  saveScope?: boolean;
  // 以上 IP-selector标准参数
  all_scope?: boolean
  search_limit?: {
    node_list?: INode[]
    host_ids?: number[]
  } // 灰度策略的限制范围
}
export interface ISelectorValue {
  dynamic_group_list: Record<string, any>[]
  host_list: IHost[]
  node_list: INode[]
}
export interface IScope {
  // object_type?: IObjectType
  node_type: INodeType
  nodes: ITarget[]
}

/**
 * 转换成标准的IP选择器的选中数据
 */
export function toSelectorNode(nodes: ITarget[], nodeType: INodeType) {
  if (!nodeType || nodes.some(node => node.meta)) return nodes;
  if (nodeType === 'INSTANCE') {
    return nodes.map(item => ({
      host_id: item.bk_host_id,
      meta: {
        scope_type: 'biz',
        scope_id: `${item.bk_biz_id}`,
        bk_biz_id: item.bk_biz_id,
      },
    }));
  }
  return nodes.map(item => ({
    object_id: item.bk_obj_id,
    instance_id: item.bk_inst_id,
    meta: {
      scope_type: 'biz',
      scope_id: `${item.bk_biz_id}`,
      bk_biz_id: item.bk_biz_id,
    },
  }));
}
export type IpSelectorMode = 'dialog' | 'section';
export type IpSelectorNameStyle = 'camelCase' | 'kebabCase';
export type IpSelectorService = {
  fetchTopologyHostCount?: (params: CommomParams) => Promise<any>
  fetchTopologyHostsNodes?: (params: CommomParams) => Promise<any>
  fetchTopologyHostIdsNodes?: (params: CommomParams) => Promise<any>
  fetchHostsDetails?: (params: CommomParams) => Promise<any>
  fetchHostCheck?: (params: CommomParams) => Promise<any>
  fetchNodesQueryPath?: (params: CommomParams) => Promise<any>
  fetchHostAgentStatisticsNodes?: (params: CommomParams) => Promise<any>
  fetchDynamicGroups?: (params: CommomParams) => Promise<any>
  fetchHostsDynamicGroup?: (params: CommomParams) => Promise<any>
  fetchHostAgentStatisticsDynamicGroups?: (params: CommomParams) => Promise<any>
  fetchCustomSettings?: (params: CommomParams) => Promise<any>
  updateCustomSettings?: (params: CommomParams) => Promise<any>
  fetchConfig?: (params: CommomParams) => Promise<any>
};
export type IpSelectorConfig = {
  // 需要支持的面板（'staticTopo', 'dynamicTopo', 'dynamicGroup', 'manualInput'）
  panelList?: string[];
  // 面板选项的值是否唯一
  unqiuePanelValue?: boolean,
  // 字段命名风格（'camelCase', 'kebabCase'）
  nameStyle?: IpSelectorNameStyle;
  // 自定义主机列表列
  hostTableCustomColumnList?: IpSelectorHostTableCustomColumn[],
  hostMemuExtends?: IpSelectorHostMemuExtend[],
  // 主机列表显示列（默认值：['ip', 'ipv6', 'alive', 'osName']），按配置顺序显示列
  // 内置所有列的 key ['ip', 'ipv6', 'cloudArea', 'alive', 'hostName',
  //  'osName', 'coludVerdor', 'osType', 'hostId', 'agentId']
  hostTableRenderColumnList?: string[]
};
export type IpSelectorHostTableCustomColumn = {
  key: string;
  index: number;
  width: string;
  label: string;
  renderHead: (h) => VNode,
  field: string,
  renderCell: (h, row) => VNode,
};
export type IpSelectorHostMemuExtend = {
  name?: string;
  action?: () => void
};
export interface IMonitorIpSelectorProps {
  panelList?: string[];
  value?: Record<string, any>;
  hostTableCustomColumnList?: IpSelectorHostTableCustomColumn[];
  hostMemuExtends?: IpSelectorHostMemuExtend[];
  hostTableRenderColumnList?: string[];
  originalValue?: Record<string, any>;
  mode?: IpSelectorMode;
  nameStyle?: IpSelectorNameStyle;
  showDialog?: boolean;
  unqiuePanelValue?: boolean;
  showView?: boolean;
  showViewDiff?: boolean;
  readonly?: boolean;
  disableDialogSubmitMethod?: Function;
  disableHostMethod?: Function;
  viewSearchKey?: string;
  service?: IpSelectorService;
  height?: number;
}
export interface IMonitorIpSelectorEvents {
  onChange: (v: Record<string, INode[]>) => void
}
@Component
export default class MonitorIpSelector extends tsc<IMonitorIpSelectorProps> {
  // 需要支持的面板（'staticTopo', 'dynamicTopo', 'dynamicGroup', 'manualInput'）
  @Prop({ default: () => ['staticTopo', 'dynamicTopo', 'dynamicGroup', 'manualInput'], type: Array }) panelList: string[];
  @Prop({ default: () => ({}), type: Object }) value: Record<string, any>;
  // 自定义主机列表列
  @Prop({ type: Array }) hostTableCustomColumnList: IpSelectorHostTableCustomColumn[];
  // 自定义menu
  @Prop({ type: Array }) hostMemuExtends: IpSelectorHostMemuExtend[];
  // 主机列表显示列（默认值：['ip', 'ipv6', 'alive', 'osName']），按配置顺序显示列
  // 内置所有列的 key ['ip', 'ipv6', 'cloudArea', 'alive', 'hostName', 'osName', 'coludVerdor', 'osType', 'hostId', 'agentId']
  @Prop({ type: Array }) hostTableRenderColumnList: string[];
  // 编辑状态的初始值，用于和最新选择的值进行对比
  @Prop({ type: Object }) originalValue: Record<string, any>;
  // IP 选择的交互模式
  @Prop({ default: 'section', type: String }) mode: IpSelectorMode;
  // 字段命名风格（'camelCase', 'kebabCase'）
  @Prop({ default: 'camelCase', type: String }) nameStyle: IpSelectorNameStyle;
  // mode 为 dialog 时弹出 dialog
  @Prop({ default: false, type: Boolean }) showDialog: boolean;
  // 面板选项的值是否唯一
  @Prop({ default: true, type: Boolean }) unqiuePanelValue: boolean;
  // IP 选择完成后是否显示结果
  @Prop({ default: false, type: Boolean }) showView: boolean;
  // 是否在选择结果面板显示数据对比
  @Prop({ default: false, type: Boolean }) showViewDiff: boolean;
  // 只读
  @Prop({ default: false, type: Boolean }) readonly: boolean;
  // Dialog 确定按钮是否禁用
  @Prop({ type: Function }) disableDialogSubmitMethod: Function;
  // 静态拓扑主机是否禁用
  @Prop({ type: Function }) disableHostMethod: Function;
  // 在选择结果面板搜索主机
  @Prop({ default: '', type: String }) viewSearchKey: string;
  // 覆盖组件初始的数据源配置
  @Prop({ type: Object }) service: IpSelectorService;
  // 高度
  @Prop({ type: Number }) height: number;

  ipSelectorServices: IpSelectorService = {};
  ipSelectorConfig: IpSelectorConfig = {};
  created() {
    this.ipSelectorServices = {
      fetchTopologyHostCount: this.fetchTopologyHostCount, // 拉取topology
      fetchTopologyHostsNodes: this.fetchTopologyHostsNodes, // 静态拓扑 - 选中节点
      fetchNodesQueryPath: this.fetchNodesQueryPath, // 动态拓扑 - 勾选节点
      fetchHostAgentStatisticsNodes: this.fetchHostAgentStatisticsNodes, // 动态拓扑 - 勾选节点
      fetchTopologyHostIdsNodes: this.fetchTopologyHostIdsNodes, // 根据多个拓扑节点与搜索条件批量分页查询所包含的主机
      fetchHostsDetails: this.fetchHostsDetails, // 静态 - IP选择回显(host_id查不到时显示失效)
      fetchHostCheck: this.fetchHostCheck, // 手动输入 - 根据用户手动输入的`IP`/`IPv6`/`主机名`/`host_id`等关键字信息获取真实存在的机器信息
      // fetchDynamicGroups: IpChooserTopo.fetchDynamicGroup,
      // fetchHostsDynamicGroup: IpChooserTopo.fetchDynamicGroupHost,
      // fetchHostAgentStatisticsDynamicGroups: IpChooserTopo.fetchBatchGroupAgentStatistics,
      fetchCustomSettings: this.fetchCustomSettings,
      updateCustomSettings: this.updateCustomSettings,
      fetchConfig: this.fetchConfig,
      ...this.service,
    };
    this.ipSelectorConfig = {
      // 需要支持的面板（'staticTopo', 'dynamicTopo', 'dynamicGroup', 'manualInput'）
      panelList: this.panelList ?? [
        'staticTopo',
        'dynamicTopo',
        'dynamicGroup',
        'manualInput',
      ],
      // 面板选项的值是否唯一
      unqiuePanelValue: this.unqiuePanelValue,
      // 字段命名风格（'camelCase', 'kebabCase'）
      nameStyle: this.nameStyle,
      // 自定义主机列表列
      hostTableCustomColumnList: this.hostTableCustomColumnList ?? [],
      hostMemuExtends: this.hostMemuExtends ??  [],
      // 主机列表显示列（默认值：['ip', 'ipv6', 'alive', 'osName']），按配置顺序显示列
      // 内置所有列的 key ['ip', 'ipv6', 'cloudArea', 'alive', 'hostName',
      //  'osName', 'coludVerdor', 'osType', 'hostId', 'agentId']
      hostTableRenderColumnList: this.hostTableRenderColumnList ?? [],
    };
  }
  // 拉取topology
  async fetchTopologyHostCount(node?: INode): Promise<ITreeItem[]> {
    const data = {
      scope_list: [{
        scope_type: 'space',
        scope_id: this.$store.state.spaceUid,
      }],
    };
    const res = await $http.request('ipChooser/trees', { data });
    return res?.data || [];
  }

  // 选中节点(根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息)
  async fetchTopologyHostsNodes(params: IQuery) {
    const { search_content, ...p } = params;
    const res = await $http.request('ipChooser/queryHosts', { data: search_content ? params : p });
    console.log(res?.data);
    return res?.data || [];
  }

  fetchTopologyHostIdsNodes(params: IQuery) {
    // const { search_content, ...p } = params;
    // return queryHostIdInfosIpChooserTopo(search_content ? params : p);
  }

  // 动态拓扑 - 勾选节点(查询多个节点拓扑路径)
  async fetchNodesQueryPath(node: IFetchNode): Promise<Array<INode>[]> {
    console.info(node, '--------');
    return [];
    // return IpChooserTopo.queryPath({ action: this.action, node_list: node.node_list }, {
    //   cancelPrevious: false
    // });
  }
  // 动态拓扑 - 勾选节点(获取多个拓扑节点的主机 Agent 状态统计信息)
  async fetchHostAgentStatisticsNodes(node: IFetchNode): Promise<{ agent_statistics: IStatistics, node: INode }[]> {
    console.info(node, '--------');
    return [];
    // return IpChooserTopo.agentStatistics({ action: this.action, node_list: node.node_list });
  }
  fetchHostsDetails(node) {
    // return detailsIpChooserHost({
    //   all_scope: true,
    //   ...node,
    // });
  }
  // 手动输入
  fetchHostCheck(node: IFetchNode) {
    // const params = { ...node, all_scope: true, saveScope: true };
    // return checkIpChooserHost(params);
  }
  async fetchCustomSettings(params: CommomParams) {
    // console.info('fetchCustomSettings : ', params);
    return [];
  }
  async updateCustomSettings(params: CommomParams) {
    console.info('updateCustomSettings : ', params);
    return [];
  }
  async fetchConfig() {
    return {
      // CMDB 动态分组链接
      bk_cmdb_dynamic_group_url: 'http:xx.yy.zz.com/#/business/1/custom-query',
      // CMDB 拓扑节点链接
      bk_cmdb_static_topo_url: 'http:xx.yy.zz.com/#/business/1/custom-query',
    };
  }
  change(value: Record<string, INode[]>) {
    this.$emit('change', value);
  }
  render() {
    return <BkIpSelector
      mode={this.mode}
      value={this.value}
      originalValue={this.originalValue}
      showView={this.showView}
      showDialog={this.showDialog}
      showViewDiff={this.showViewDiff}
      viewSearchKey={this.viewSearchKey}
      readonly={this.readonly}
      disableDialogSubmitMethod={this.disableDialogSubmitMethod}
      disableHostMethod={this.disableHostMethod}
      height={this.height ?? '100%'}
      service={this.ipSelectorServices}
      config={this.ipSelectorConfig}
    />;
  }
}
