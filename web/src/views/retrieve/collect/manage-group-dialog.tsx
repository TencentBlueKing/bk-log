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
import { Component, Emit, Watch, Model } from 'vue-property-decorator';
import {
  Dialog,
  Switcher,
  Option,
  Table,
  TableColumn,
  Checkbox,
  Input,
  Select,
  TableSettingContent,
  DropdownMenu,
  Tag,
} from 'bk-magic-vue';
import FingerSelectColumn from '../result-table-panel/log-clustering/components/finger-select-column.vue';
import ManageInput from './component/manage-input';
import $http from '../../../api';
import { deepClone, random, formatDate } from '../../../common/util';
import './manage-group-dialog.scss';

interface IProps {
  value?: boolean;
}

interface IFavoriteItem {
  id: number;
  created_by: string;
  space_uid: number;
  index_set_id: number;
  name: string;
  group_id: number;
  group_name: string;
  keyword: string;
  index_set_name: string;
  search_fields: string[];
  is_active: boolean;
  visible_type: string;
  display_fields: string[];
  is_enable_display_fields: boolean;
  search_fields_select_list?: any[];
  visible_option: any[];
  group_option: any[];
  params: Record<string, any>;
}

const settingFields = [ // 设置显示的字段
  {
    id: 'name',
    label: window.mainComponent.$t('收藏名'),
    disabled: true,
  },
  {
    id: 'group_name',
    label: window.mainComponent.$t('所属组'),
    disabled: true,
  },
  {
    id: 'visible_type',
    label: window.mainComponent.$t('可见范围'),
  },
  {
    id: 'display_fields',
    label: window.mainComponent.$t('表单模式'),
  },
  {
    id: 'is_show_switch',
    label: window.mainComponent.$t('显示字段'),
  },
  {
    id: 'updated_by',
    label: window.mainComponent.$t('变更人'),
  },
  {
    id: 'updated_at',
    label: window.mainComponent.$t('变更时间'),
  },
];

@Component
export default class GroupDialog extends tsc<IProps> {
  @Model('change', { type: Boolean, default: false }) value: IProps['value'];
  searchValue = ''; // 搜索字段
  tableLoading = false;
  isShowDeleteDialog = false;
  tableList: IFavoriteItem[] = []; // 表格数据;
  operateTableList: IFavoriteItem[] = []; // 用户操作操作缓存表格数据;
  submitTableList: IFavoriteItem[] = []; // 修改提交的表格数据;
  searchAfterList: IFavoriteItem[] = []; // 用于全选或者多选或搜索过滤后的表格数组;
  deleteTableIDList = []; // 删除收藏的表格ID
  tableDialog = false;
  selectFavoriteList = []; // 列的头部的选择框收藏ID列表
  groupList = []; // 组列表
  unPrivateList = []; // 无个人组的收藏列表
  privateList = []; // 个人组列表 只有个人的列表
  checkValue = 0; // 0为不选 1为半选 2为全选
  groupName = ''; // 输入框组名
  unknownGroupID = 0;
  privateGroupID = 0;
  isCannotValueChange = false; // 用于分组时不进行数据更新
  maxHeight = 300;
  tippyOption = {
    trigger: 'click',
    interactive: true,
    theme: 'light',
  };
  isShowAddGroup = true;
  cannotComparedData = [ // 不进行对比的字段 （前端操作缓存自加的字段）
    'search_fields_select_list',
    'visible_option',
    'group_option',
    'group_option_private',
    'is_group_disabled',
  ];
  sourceFilters = []; // 所属组数组
  updateSourceFilters = []; // 更变人过滤数组

  tableKey = random(10);

  unPrivateOptionList = [ // 非本人创建的收藏的可见范围数组
    { name: window.mainComponent.$t('公开'), id: 'public' },
  ];
  allOptionList = [ // 本人创建的收藏的可见范围数组
    { name: window.mainComponent.$t('公开'), id: 'public' },
    { name: window.mainComponent.$t('仅本人'), id: 'private' },
  ];

  tableSetting = {
    fields: settingFields,
    selectedFields: settingFields.slice(0, 5),
    size: 'small',
  };

  get spaceUid() {
    return this.$store.state.spaceUid;
  }

  get getUserName() { // 当前用户名称
    return this.$store.state.userMeta?.username || '';
  }

  get selectCount() {
    // 当前选择的数据的数量
    return this.selectFavoriteList.length;
  }

  get showFavoriteCount() {
    return this.searchAfterList.length;
  }

  @Watch('selectFavoriteList', { deep: true })
  watchSelectListLength(list) {
    // 监听选择数据的数量 改变全选的check状态
    if (!list.length) {
      this.checkValue = 0;
      return;
    }
    if (list.length === this.searchAfterList.length) {
      this.checkValue = 2;
      return;
    }
    this.checkValue = 1;
  }

  @Emit('change') // 展示或者隐藏弹窗
  handleShowChange(value = false) {
    return value;
  }

  @Emit('submit') // 更新成功
  handleSubmitChange(value = false) {
    return value;
  }

  mounted() {
    const initTableHeight = parseInt(`${(document.body.clientHeight * 0.8)  - 240}`);
    this.maxHeight = initTableHeight > this.maxHeight ? initTableHeight : this.maxHeight;
  }

  async handleValueChange(value) {
    if (value) {
      // 展开
      await this.getGroupList();
      this.getFavoriteList();
    } else {
      // 关闭
      this.tableList = [];
      this.operateTableList = [];
      this.submitTableList = [];
      this.selectFavoriteList = [];
      this.groupList = [];
      this.updateSourceFilters = [];
      this.searchAfterList = [];
      this.handleShowChange();
    }
  }

  /** 多选是否选中 */
  getCheckedStatus(row) {
    return this.selectFavoriteList.includes(row.id);
  }
  /** 多选操作 */
  handleRowCheckChange(row, status) {
    if (status) {
      this.selectFavoriteList.push(row.id);
    } else {
      const index = this.selectFavoriteList.findIndex(item => item === row.id);
      this.selectFavoriteList.splice(index, 1);
    }
  }
  /** 搜索 */
  handleSearchFilter() {
    if (this.tableLoading) return;
    this.tableLoading = true;
    let searchList;
    if (this.searchValue !== '') {
      searchList = this.operateTableList.filter(item => item.name.includes(this.searchValue),
      );
    } else {
      searchList = this.operateTableList;
    }
    setTimeout(() => {
      this.tableLoading = false;
      // 赋值搜索过后的列表
      this.searchAfterList = searchList;
      this.selectFavoriteList = [];
    }, 500);
  }
  /** 全选操作 */
  handleSelectionChange(value) {
    this.selectFavoriteList = value
      ? this.searchAfterList.map(item => item.id)
      : [];
  }
  /** 多选移动至分组操作 */
  handleClickMoveGroup(value) {
    this.selectFavoriteList.forEach((item) => {
      this.operateListChange({ id: item }, { group_id: value.group_id, is_group_disabled: false });
    });
  }
  /** 获取字段下拉框列表请求 */
  async getSearchFieldsList(keyword: string) {
    return await $http.request('favorite/getSearchFields', {
      data: { keyword },
    });
  }
  /** 获取收藏请求 */
  async getFavoriteList() {
    try {
      this.tableLoading = true;
      const res = await $http.request('favorite/getFavoriteList', {
        query: {
          space_uid: this.spaceUid,
          order_type: 'NAME_ASC',
        },
      });
      const updateSourceFiltersSet = new Set();
      const initList = res.data.map((item) => {
        const visible_option = item.created_by === this.getUserName ? this.allOptionList : this.unPrivateOptionList;
        const search_fields_select_list = item.search_fields.map(item => ({ name: item })); // 初始化表单字段
        const is_group_disabled = item.visible_type === 'private';
        if (!updateSourceFiltersSet.has(item.updated_by)) updateSourceFiltersSet.add(item.updated_by);
        return {
          ...item,
          search_fields_select_list,
          group_option: this.unPrivateList,
          group_option_private: this.privateList,
          visible_option,
          is_group_disabled,
        };
      });
      this.updateSourceFilters = [...updateSourceFiltersSet].map(item => ({
        text: item,
        value: item,
      }));
      this.tableList = res.data;
      this.operateTableList = initList;
      this.searchAfterList = initList;
    } catch (error) {
    } finally {
      this.tableLoading = false;
      this.handleSearchFilter();
    }
  }
  /** 获取组列表 */
  async getGroupList(isAddGroup = false) {
    try {
      const res = await $http.request('favorite/getGroupList', {
        query: {
          space_uid: this.spaceUid,
        },
      });
      this.groupList = res.data.map(item => ({
        group_id: item.id,
        group_name: item.name,
        group_type: item.group_type,
      }));
      this.unPrivateList = this.groupList.slice(1); // 去除个人组的列表
      this.privateList = this.groupList.slice(0, 1); // 个人组列表
      this.sourceFilters = res.data.map(item => ({
        text: item.name,
        value: item.name,
      }));
      this.unknownGroupID = this.groupList[this.groupList.length - 1]?.group_id;
      this.privateGroupID = this.groupList[0]?.group_id;
    } catch (error) {
      console.warn(error);
    } finally {
      if (isAddGroup) { // 如果是新增组 则刷新操作表格的组列表
        this.operateTableList = this.operateTableList.map(item => ({
          ...item,
          group_option: this.unPrivateList,
          group_option_private: this.privateList,
        }));
        this.handleSearchFilter();
      }
    }
  }
  /** 显示字段选择操作 */
  handleChangeSearchList(row, nVal: string[]) {
    this.operateListChange(row, { search_fields: nVal });
  }
  /** 更改收藏名 */
  handleChangeFavoriteName(row, name) {
    this.operateListChange(row, { name });
  }
  /** 是否同时显示字段操作 */
  handleSwitchChange(row, value) {
    this.operateListChange(row, { is_enable_display_fields: value });
  }
  /** 新增或更新组名 */
  async handleAddGroupName() {
    const data = { name: this.groupName, space_uid: this.spaceUid };
    try {
      const res = await $http.request('favorite/createGroup', { data });
      if (res.result) {
        this.$bkMessage({
          theme: 'success',
          message: this.$t('新增成功'),
        });
        this.getGroupList(true);
      }
    } catch (error) {
    } finally {
      this.isShowAddGroup = true;
      this.groupName = '';
    }
  }
  /** 获取显示字段下拉框列表 */
  async handleClickFieldsList(row, status: boolean) {
    if (status) {
      try {
        const res = await this.getSearchFieldsList(row.keyword);
        this.operateListChange(row, { search_fields_select_list: res.data });
      } catch (error) {
        console.warn(error);
      }
    }
  }
  /** 修改可选范围 */
  handleSelectVisible(row, nVal: string) {
    const group_id = nVal !== 'public' ? this.privateGroupID : this.unknownGroupID;
    const group_name = this.groupList.find(item => item.group_id === group_id).group_name;
    this.operateListChange(row, {
      visible_type: nVal,
      is_group_disabled: nVal === 'private',
      group_name,
      group_id,
    });
  }
  /** 单独修改组 */
  handleChangeGroup(row) {
    const visible_type = row.group_id === this.privateGroupID ? 'private' : 'public';
    this.operateListChange(row, { visible_type });
  }
  /** 用户操作 */
  operateListChange(row, operateObj = {}) {
    if (this.isCannotValueChange) return;

    // 搜索展示用的列表和操作缓存的列表同时更新数据
    for (const listName of ['searchAfterList', 'operateTableList']) {
      const index = this[listName].findIndex(item => item.id === row.id);
      if (index >= 0) Object.assign(this[listName][index], row, operateObj);
      if (listName === 'operateTableList') this.submitDataCompared(row, index, operateObj);
    }
  }
  /** 提交数据对比 */
  submitDataCompared(row, operateIndex, operateObj) {
    const submitIndex = this.submitTableList.findIndex(
      item => item.id === row.id,
    );
    if (submitIndex >= 0) {
      // 操作已添加到更新列表的值 进行数据对比
      Object.assign(this.submitTableList[submitIndex], row, operateObj);
      const comparedSubData = deepClone(this.submitTableList[submitIndex]);
      this.deleteSubmitData(comparedSubData, this.cannotComparedData); // 前端加的参数 不做对比
      const tableData = this.tableList[operateIndex];
      if (JSON.stringify(tableData) === JSON.stringify(comparedSubData)) {
        this.submitTableList.splice(submitIndex, 1); // 判断数据是否相同 相同则删除提交更新里的值
      }
    } else {
      // 第一次操作相同的列 添加到提交更新列表
      const comparedData = deepClone(this.operateTableList[operateIndex]);
      this.deleteSubmitData(comparedData, this.cannotComparedData); // 前端加的参数 不做对比
      const tableData = this.tableList[operateIndex];
      // 判断操作过后的值和表格里的是否相同 不同则添加到提交更新列表
      if (JSON.stringify(comparedData) !== JSON.stringify(tableData)) {
        this.submitTableList.push(comparedData);
      }
    }
  }
  /** 删除不做对比的参数 */
  deleteSubmitData(data: object, list: string[]) {
    list.forEach(item => delete data[item]);
  }

  handleDeleteFavorite(row) {
    this.$bkInfo({
      subTitle: `${this.$t('当前收藏为')}${row.name}，${this.$t('是否删除')}？`,
      type: 'warning',
      confirmFn: () => {
        this.deleteTableIDList.push(row.id);
        // 删除收藏 把展示的表格, 操作表格, 提交表格, 以及基础表格统一删除
        for (const listName of [
          'searchAfterList',
          'operateTableList',
          'submitTableList',
          'tableList',
        ]) {
          const index = this[listName].findIndex(item => item.id === row.id);
          if (index >= 0) this[listName].splice(index, 1);
        }
        // 当前选中选择删除
        const index = this.selectFavoriteList.findIndex(item => item === row.id);
        if (index >= 0) this.selectFavoriteList.splice(index, 1);
      },
    });
  }
  /** 点击确定提交管理弹窗数据 */
  handleSubmitTableData() {
    this.tableLoading = true;
    Promise.all([this.batchDeleteFavorite(), this.batchUpdateFavorite()])
      .then(() => {
        this.handleValueChange(false);
        this.handleSubmitChange(true);
      })
      .finally(() => {
        this.tableLoading = false;
      });
  }

  async batchDeleteFavorite() {
    // 删除接口
    // 若没有删除则不请求
    if (!this.deleteTableIDList.length) return;
    try {
      await $http.request('favorite/batchFavoriteDelete', {
        data: {
          id_list: this.deleteTableIDList,
        },
      });
    } catch (error) {}
  }

  async batchUpdateFavorite() {
    // 更新收藏接口
    // 若没有更新收藏则不请求
    if (!this.submitTableList.length) return;
    const params = this.submitTableList.map(item => ({
      id: item.id,
      name: item.name,
      keyword: item.keyword,
      group_id: item.group_id,
      search_fields: item.search_fields,
      visible_type: item.visible_type,
      display_fields: item.display_fields,
      is_enable_display_fields: item.is_enable_display_fields,
      // host_scopes: item.params.host_scopes,
      ip_chooser: item.params.ip_chooser,
      addition: item.params.addition,
    }));
    try {
      await $http.request('favorite/batchFavoriteUpdate', {
        data: {
          params,
        },
      });
    } catch (error) {}
  }
  /** 所属组和变更人分组操作 */
  sourceFilterMethod(value, row, column) {
    const property = column.property;
    this.isCannotValueChange = true;
    setTimeout(() => {
      // 因为操作组会导致数据更变 即不改变数据
      this.isCannotValueChange = false;
    }, 500);
    return row[property] === value;
  }

  handleSettingChange({ fields, size }) {
    this.tableSetting.selectedFields = fields;
    this.tableSetting.size = size;
  }

  checkFields(field) {
    return this.tableSetting.selectedFields.some(item => item.id === field);
  }

  renderHeader(h) {
    return h(FingerSelectColumn, {
      class: {
        'header-checkbox': true,
      },
      props: {
        value: this.checkValue,
        disabled: !this.searchAfterList.length,
      },
      on: {
        change: this.handleSelectionChange,
      },
    });
  }

  renderHeaderTable(h) {
    return h('div', {
      class: 'render-header',
    }, [
      h('span', {
        class: 'header-tips',
        directives: [
          {
            name: 'bk-tooltips',
            value: this.$t('表单模式显示字段文案'),
          },
        ],
      }, this.$t('表单模式')),
    ]);
  }

  renderHeaderFields(h) {
    return h('div', {
      class: 'render-header',
    }, [
      h('span', {
        class: 'header-tips',
        directives: [
          {
            name: 'bk-tooltips',
            value: this.$t('是否同时显示字段文案'),
          },
        ],
      }, this.$t('显示字段')),
    ]);
  }

  render() {
    const expandSlot = {
      default: ({ row }) => (
        <div class="expand-container">
          <div class="expand-information">
            <span>{this.$t('索引集')}</span>
            <span>{row.index_set_name}</span>
          </div>
          <div class="expand-information">
            <span>{this.$t('查询语句')}</span>
            <span>{row.keyword}</span>
          </div>
          <div class="expand-information">
            <span>{this.$t('查询显示字段')}:</span>
            {row.display_fields.map(item => (
              <Tag>{item}</Tag>
            ))}
          </div>
        </div>
      ),
    };
    const nameSlot = {
      default: ({ row }) => [
        <div class="group-container">
          <Checkbox
            class="group-check-box"
            checked={this.getCheckedStatus(row)}
            on-change={status => this.handleRowCheckChange(row, status)}
          ></Checkbox>
          <ManageInput
            favorite-data={row}
            on-change={val => this.handleChangeFavoriteName(row, val)}
          ></ManageInput>
        </div>,
      ],
    };
    const groupSlot = {
      default: ({ row }) => [
        <Select
          vModel={row.group_id}
          searchable
          clearable={false}
          disabled={row.is_group_disabled}
          popover-min-width={200}
          ext-popover-cls="add-new-page-container"
          on-change={() => this.handleChangeGroup(row)}
        >
          {row[
            row.visible_type === 'private'
              ? 'group_option_private'
              : 'group_option'
          ].map(item => (
            <Option
              id={item.group_id}
              key={item.group_id}
              name={item.group_name}
            ></Option>
          ))}
          <div slot="extension">
            {this.isShowAddGroup ? (
              <div class="select-add-new-group" onClick={() => (this.isShowAddGroup = false)}>
                <div>
                  <i class="bk-icon icon-plus-circle"></i>
                  {this.$t('新增')}
                </div>
              </div>
            ) : (
              <li class="add-new-page-input">
                <Input
                  vModel={this.groupName}
                  maxlength={10}
                  behavior={'simplicity'}
                ></Input>
                <div class="operate-button">
                  <span class="bk-icon icon-check-line" onClick={() => this.handleAddGroupName()}></span>
                  <span class="bk-icon icon-close-line-2" onClick={() => {
                    this.isShowAddGroup = true;
                    this.groupName = '';
                  }}></span>
                </div>
              </li>
            )}
          </div>
        </Select>,
      ],
    };
    const visibleSlot = {
      default: ({ row }) => [
        <Select
          vModel={row.visible_type}
          on-selected={nVal => this.handleSelectVisible(row, nVal)}
          clearable={false}
        >
          {row.visible_option.map(item => (
            <Option id={item.id} key={item.id} name={item.name}></Option>
          ))}
        </Select>,
      ],
    };
    const selectTagSlot = {
      default: ({ row }) => [
        <Select
          vModel={row.search_fields}
          searchable
          multiple
          display-tag
          placeholder={' '}
          clearable={false}
          on-change={nVal => this.handleChangeSearchList(row, nVal)}
          on-toggle={status => this.handleClickFieldsList(row, status)}
        >
          {row.search_fields_select_list.map(item => (
            <Option id={item.name} key={item.name} name={item.name}></Option>
          ))}
        </Select>,
      ],
    };
    const switchSlot = {
      default: ({ row }) => [
        <div class="switch-container">
          <Switcher
            vModel={row.is_enable_display_fields}
            theme="primary"
            on-change={value => this.handleSwitchChange(row, value)}
          ></Switcher>
        </div>,
      ],
    };
    const deleteSlot = {
      default: ({ row }) => [
        <div class="switcher-box">
          <div class="delete" onClick={() => this.handleDeleteFavorite(row)}>
            <span class="bk-icon icon-delete"></span>
          </div>
        </div>,
      ],
    };
    return (
      <Dialog
        value={this.value}
        title={this.$t('管理')}
        header-position="left"
        render-directive="if"
        mask-close={false}
        ext-cls="manage-group"
        width={960}
        confirm-fn={this.handleSubmitTableData}
        on-value-change={this.handleValueChange}
      >
        <div class={`top-operate ${!this.selectCount && 'is-not-select'}`}>
          <div class="favorite-size">
            {this.$t('共')}&nbsp;
            <span class="size-weight">{this.showFavoriteCount}</span>
            &nbsp;{this.$t('个收藏')}
          </div>
          <Input
            class="operate-input"
            right-icon="bk-icon icon-search"
            vModel={this.searchValue}
            on-enter={this.handleSearchFilter}
            on-right-icon-click={this.handleSearchFilter}
          ></Input>
        </div>
        {this.selectCount ? (
          <div class="table-top-operate">
            <span>
              {this.$t('当前已选择')}
              <span class="operate-message">{this.selectCount}</span>
              {this.$t('条数据')}
            </span>
            <DropdownMenu trigger="click">
              <div class="dropdown-trigger-text" slot="dropdown-trigger">
                <span class="operate-click">
                  ，&nbsp;{this.$t('移至分组')}
                  <span class="bk-icon icon-down-shape"></span>
                </span>
              </div>
              <div class="dropdown-list" slot="dropdown-content">
                <ul class="search-li">
                  {this.unPrivateList.map(item => (
                    <li onClick={() => this.handleClickMoveGroup(item)}>
                      {item.group_name}
                    </li>
                  ))}
                </ul>
              </div>
            </DropdownMenu>
          </div>
        ) : undefined}
        <Table
          data={this.searchAfterList}
          size="small"
          render-directive="if"
          header-border={true}
          border={true}
          ext-cls={`${!this.selectCount && 'is-not-select'}`}
          empty-text={this.$t('暂无数据')}
          max-height={this.maxHeight}
          v-bkloading={{ isLoading: this.tableLoading }}
        >
          <TableColumn
            width="64"
            type="expand"
            render-header={this.renderHeader}
            scopedSlots={expandSlot}
          ></TableColumn>

          <TableColumn
            label={this.$t('收藏名')}
            key={'column_name'}
            width="160"
            prop={'name'}
            class-name="group-input"
            label-class-name="group-title"
            scopedSlots={nameSlot}
          ></TableColumn>

          {this.checkFields('group_name') ? (
            <TableColumn
              label={this.$t('所属组')}
              width="112"
              key={'column_group_name'}
              prop={'group_name'}
              scopedSlots={groupSlot}
              label-class-name="group-title"
              class-name="group-select"
              filters={this.sourceFilters}
              filter-multiple={false}
              filter-method={this.sourceFilterMethod}
            ></TableColumn>
          ) : undefined}

          {this.checkFields('visible_type') ? (
            <TableColumn
              label={this.$t('可见范围')}
              width="112"
              key={'column_visible_type'}
              prop={'visible_type'}
              scopedSlots={visibleSlot}
              label-class-name="group-title"
              class-name="group-select"
            ></TableColumn>
          ) : undefined}

          {this.checkFields('display_fields') ? (
            <TableColumn
              label={this.$t('表单模式')}
              render-header={this.renderHeaderTable}
              key={'column_search_fields'}
              prop={'search_fields'}
              scopedSlots={selectTagSlot}
              label-class-name="group-title"
              class-name="group-select"
            ></TableColumn>
          ) : undefined}

          {this.checkFields('updated_by') ? (
            <TableColumn
              label={this.$t('变更人')}
              prop={'updated_by'}
              key={'column_update_by'}
              filters={this.updateSourceFilters}
              filter-multiple={false}
              filter-method={this.sourceFilterMethod}
            ></TableColumn>
          ) : undefined}

          {this.checkFields('updated_at') ? (
            <TableColumn
              label={this.$t('变更时间')}
              prop={'updated_at'}
              key={'column_update_time'}
              scopedSlots={{
                default: ({ row }) => [
                  <span>{formatDate(row.updated_at)}</span>,
                ],
              }}
            ></TableColumn>
          ) : undefined}

          {this.checkFields('is_show_switch') ? (
            <TableColumn
              label={this.$t('显示字段')}
              render-header={this.renderHeaderFields}
              class-name="group-input"
              max-width="120"
              label-class-name="group-title"
              key={'column_switch'}
              scopedSlots={switchSlot}
            ></TableColumn>
          ) : undefined}

          <TableColumn
            width="0"
            key={'column_delete'}
            scopedSlots={deleteSlot}
          ></TableColumn>

          <TableColumn type="setting">
            <TableSettingContent
              key={`${this.tableKey}__settings`}
              fields={this.tableSetting.fields}
              size={this.tableSetting.size}
              selected={this.tableSetting.selectedFields}
              on-setting-change={this.handleSettingChange}
            ></TableSettingContent>
          </TableColumn>
        </Table>
      </Dialog>
    );
  }
}
