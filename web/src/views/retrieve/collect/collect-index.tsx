/* eslint-disable no-useless-escape */
/* eslint-disable no-case-declarations */
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
import {
  Component,
  Emit,
  Prop,
  PropSync,
  Watch,
  Ref,
} from 'vue-property-decorator';
import { Input, Popover, Button, Radio, RadioGroup } from 'bk-magic-vue';
import CollectContainer from './collect-container';
import ManageGroupDialog from './manage-group-dialog';
import AddCollectDialog from './add-collect-dialog';
import { copyMessage, deepClone } from '../../../common/util';
import $http from '../../../api';
import './collect-index.scss';

interface IProps {
  collectWidth: number;
  isShowCollect: boolean;
  favoriteRequestID: number;
  activeFavoriteID: number;
  visibleFields: Array<any>;
  favoriteList: any;
  favoriteLoading: boolean;
}

export interface IGroupItem {
  group_id: number;
  group_name: string;
  group_type?: visibleType;
  favorites?: IFavoriteItem[];
}

export interface IFavoriteItem {
  id: number;
  created_by: string;
  space_uid: number;
  index_set_id: number;
  name: string;
  group_id: number;
  visible_type: visibleType;
  params: object;
  is_active: boolean;
  display_fields: string[];
}

type visibleType = 'private' | 'public' | 'unknown';

@Component
export default class CollectIndex extends tsc<IProps> {
  @PropSync('width', { type: Number }) collectWidth: number;
  @PropSync('isShow', { type: Boolean }) isShowCollect: boolean;
  @Prop({ type: Number, required: true }) favoriteRequestID: number;
  @Prop({ type: Boolean, required: true }) favoriteLoading: boolean;
  @Prop({ type: Array, required: true }) favoriteList: any;
  @Prop({ type: Number, required: true }) activeFavoriteID: number;
  @Prop({ type: Array, default: () => [] }) visibleFields: Array<any>;
  @Ref('popoverGroup') popoverGroupRef: Popover;
  @Ref('popoverSort') popoverSortRef: Popover;

  collectMinWidth = 160; // 收藏最小栏宽度
  collectMaxWidth = 400; // 收藏栏最大宽度
  currentTreeBoxWidth = null; // 当前收藏容器的宽度
  currentScreenX = null;
  isChangingWidth = false; // 是否正在拖拽
  isShowManageDialog = false; // 是否展示管理弹窗
  isSearchFilter = false; // 是否搜索过滤
  isShowAddNewFavoriteDialog = false; // 是否展示编辑收藏弹窗
  collectLoading = false; // 分组容器loading
  isShowGroupTitle = true; // 是否展示分组头部
  searchVal = ''; // 搜索
  groupName = ''; // 新增组
  privateGroupID = 0; // 私人组ID
  unknownGroupID = 0; // 公开组ID
  baseSortType = 'NAME_ASC'; // 排序参数
  sortType = 'NAME_ASC'; // 展示的排序参数
  editFavoriteID = -1; // 点击编辑时的收藏ID
  groupSortList = [
    // 排序展示列表
    {
      name: `${window.mainComponent.$t('按名称')} A - Z ${window.mainComponent.$t('排序')}`,
      id: 'NAME_ASC',
    },
    {
      name: `${window.mainComponent.$t('按名称')} Z - A ${window.mainComponent.$t('排序')}`,
      id: 'NAME_DESC',
    },
    {
      name: window.mainComponent.$t('按更新时间排序'),
      id: 'UPDATED_AT_DESC',
    },
  ];
  tippyOption = {
    trigger: 'click',
    interactive: true,
    theme: 'light',
  };
  groupList: IGroupItem[] = []; // 分组列表
  collectList: IGroupItem[] = []; // 收藏列表
  filterCollectList: IGroupItem[] = []; // 搜索的收藏列表

  get spaceUid() {
    return this.$store.state.spaceUid;
  }

  get isClickFavoriteEdit() {
    return this.editFavoriteID === this.activeFavoriteID;
  }

  @Watch('isShowCollect')
  async handleShowCollect(value) {
    if (value) {
      this.baseSortType = localStorage.getItem('favoriteSortType') || 'NAME_ASC';
      this.sortType = this.baseSortType;
      this.getFavoriteList();
    } else {
      this.collectList = [];
      this.filterCollectList = [];
      this.groupList = [];
      this.searchVal = '';
    }
  }

  @Watch('favoriteList', { deep: true })
  watchFavoriteData(value) {
    this.handleInitFavoriteList(value);
  }


  @Watch('favoriteRequestID')
  async handleChangeIndexSet() {
    if (!this.isShowCollect) return;
    this.collectList = [];
    this.filterCollectList = [];
    this.groupList = [];
    this.getFavoriteList();
  }

  @Emit('handleClick')
  handleClickFavorite(value) {
    return value;
  }

  @Emit('isRefreshFavorite')
  handleUpdateActiveFavoriteData(value) {
    return value;
  }

  @Emit('favoriteDialogSubmit')
  handleSubmitFavoriteData({ isEdit, resValue }) {
    return {
      isEdit,
      resValue,
    };
  }

  @Emit('requestFavoriteList')
  getFavoriteList() {};

  async handleUserOperate(obj) {
    const { type, value } = obj;
    switch (type) {
      case 'click-favorite': // 点击收藏
        this.handleClickFavorite(value);
        break;
      case 'add-group': // 新增组
        await this.handleUpdateGroupName({ group_new_name: value });
        this.getFavoriteList();
        break;
      case 'reset-group-name': // 重命名
        const isCanRename = /^[\u4e00-\u9fa5_a-zA-Z0-9`~!@#$%^&*()_\-+=<>?:"{}|,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]+$/im.test(value);
        if (!isCanRename) {
          this.showMessagePop(this.$t('组名不规范'), 'error');
          return;
        }
        await this.handleUpdateGroupName(value, false);
        this.getFavoriteList();
        break;
      case 'move-favorite': // 移动收藏
        const visible_type = value.group_id === this.privateGroupID ? 'private' : 'public';
        Object.assign(value, { visible_type });
        await this.handleUpdateFavorite(value);
        this.getFavoriteList();
        break;
      case 'remove-group': // 从组中移除收藏（移动至未分组）
        Object.assign(value, {
          visible_type: 'public',
          group_id: this.unknownGroupID,
        });
        await this.handleUpdateFavorite(value);
        this.getFavoriteList();
        break;
      case 'edit-favorite': // 编辑收藏
        this.editFavoriteID = value.id;
        this.isShowAddNewFavoriteDialog = true;
        break;
      case 'delete-favorite': // 删除收藏
        this.$bkInfo({
          subTitle: `${this.$t('当前收藏为')}${value.name}，${this.$t('是否删除')}？`,
          type: 'warning',
          confirmFn: async () => {
            await this.deleteFavorite(value.id);
            this.getFavoriteList();
          },
        });
        break;
      case 'dismiss-group': // 解散分组
        this.$bkInfo({
          title: `${this.$t('当前分组为')}${value.group_name}，${this.$t('是否解散')}？`,
          subTitle: `${this.$t('解散文案')}`,
          type: 'warning',
          confirmFn: async () => {
            await this.deleteGroup(value.group_id);
            this.getFavoriteList();
          },
        });
        break;
      case 'share':
        let shareUrl = window.SITE_URL;
        if (!shareUrl.startsWith('/')) shareUrl = `/${shareUrl}`;
        if (!shareUrl.endsWith('/')) shareUrl += '/';
        const params = encodeURIComponent(JSON.stringify({ ...value.params }));
        shareUrl = `${window.location.origin + shareUrl}#/retrieve/${value.index_set_id}?spaceUid=${value.space_uid}&retrieveParams=${params}`;
        copyMessage(shareUrl, this.$t('复制成功'));
        break;
      case 'drag-move-end':
        try {
          await $http.request('favorite/groupUpdateOrder', {
            data: {
              space_uid: this.spaceUid,
              group_order: value,
            },
          });
        } catch (error) {}
        break;
      default:
    }
  }
  /** 新增组 */
  async handleClickGroupBtn(clickType: string) {
    if (clickType === 'add') {
      await this.handleUpdateGroupName({ group_new_name: this.groupName });
      this.getFavoriteList();
    }
    setTimeout(() => {
      this.groupName = '';
    }, 500);
    this.popoverGroupRef.hideHandler();
  }

  /** 排序 */
  handleClickSortBtn(clickType: string) {
    if (clickType === 'sort') {
      this.baseSortType = this.sortType;
      localStorage.setItem('favoriteSortType', this.sortType);
      this.getFavoriteList();
    } else {
      setTimeout(() => {
        this.sortType = this.baseSortType;
      }, 500);
    }
    this.popoverSortRef.hideHandler();
  }

  /** 收藏搜索 */
  handleSearchFavorite(isRequest = false) {
    if (isRequest) this.collectLoading = true;
    if (this.searchVal === '') {
      this.filterCollectList = this.collectList;
      this.isSearchFilter = false;
      return;
    }
    this.isSearchFilter = true;
    this.filterCollectList = this.collectList
      .map(item => ({
        ...item,
        favorites: item.favorites.filter(
          fItem => fItem.created_by.includes(this.searchVal)
            || fItem.name.includes(this.searchVal),
        ),
      }))
      .filter(item => item.favorites.length);
    setTimeout(() => {
      if (isRequest) this.collectLoading = false;
    }, 500);
  }

  /** 新增或更新组名 */
  async handleUpdateGroupName(groupObj, isCreate = true) {
    const { group_id, group_new_name } = groupObj;
    const params = { group_id };
    const data = { name: group_new_name, space_uid: this.spaceUid };
    const requestStr = isCreate ? 'createGroup' : 'updateGroupName';
    try {
      const res = await $http.request(`favorite/${requestStr}`, {
        params,
        data,
      });
      if (res.result) this.showMessagePop(this.$t('操作成功'));
    } catch (error) {}
  }

  handleInitFavoriteList(value) {
    this.collectList = value;
    this.groupList = value.map(item => ({
      group_id: item.group_id,
      group_name: item.group_name,
      group_type: item.group_type,
    }));
    this.unknownGroupID = this.groupList[this.groupList.length - 1]?.group_id;
    this.privateGroupID = this.groupList[0]?.group_id;
    this.handleSearchFavorite();
    this.isShowGroupTitle = !(this.collectList.length === 2 && !this.collectList[0].favorites.length);
    this.filterCollectList = deepClone(this.collectList);
    if (this.activeFavoriteID >= 0) { // 获取列表后 判断当前是否有点击的活跃收藏 如果有 则进行数据更新
      let isFind = false;
      for (const cItem of this.collectList) {
        if (isFind) break;
        for (const fItem of cItem.favorites) {
          if (fItem.id === this.activeFavoriteID) {
            isFind = true;
            this.handleUpdateActiveFavoriteData(fItem);
            break;
          }
        }
      }
    }
  };

  /** 解散分组 */
  async deleteGroup(group_id) {
    try {
      const res = await $http.request('favorite/deleteGroup', {
        params: { group_id },
      });
      if (res.result) this.showMessagePop(this.$t('操作成功'));
    } catch (error) {}
  }

  /** 删除收藏 */
  async deleteFavorite(favorite_id) {
    try {
      const res = await $http.request('favorite/deleteFavorite', {
        params: { favorite_id },
      });
      if (res.result) this.showMessagePop(this.$t('删除成功'));
    } catch (error) {}
  }


  showMessagePop(message, theme = 'success') {
    this.$bkMessage({
      message,
      theme,
    });
  }

  /** 更新收藏 */
  async handleUpdateFavorite(favoriteData) {
    try {
      const {
        params,
        name,
        group_id,
        display_fields,
        visible_type,
        id,
      } = favoriteData;
      const {
        // host_scopes,
        ip_chooser,
        addition,
        keyword,
        search_fields,
      } = params;
      const data = {
        name,
        group_id,
        display_fields,
        visible_type,
        // host_scopes,
        ip_chooser,
        addition,
        keyword,
        search_fields,
      };
      const res = await $http.request('favorite/updateFavorite', {
        params: { id },
        data,
      });
      if (res.result) this.showMessagePop(this.$t('操作成功'));
    } catch (error) {}
  }

  /** 控制页面布局宽度 */
  dragBegin(e) {
    this.isChangingWidth = true;
    this.currentTreeBoxWidth = this.collectWidth;
    this.currentScreenX = e.screenX;
    window.addEventListener('mousemove', this.dragMoving, { passive: true });
    window.addEventListener('mouseup', this.dragStop, { passive: true });
  }
  dragMoving(e) {
    const newTreeBoxWidth =      this.currentTreeBoxWidth + e.screenX - this.currentScreenX;
    if (newTreeBoxWidth < this.collectMinWidth) {
      this.collectWidth = 0;
      this.isShowCollect = false;
      this.dragStop();
    } else if (newTreeBoxWidth >= this.collectMaxWidth) {
      this.collectWidth = this.collectMaxWidth;
    } else {
      this.collectWidth = newTreeBoxWidth;
    }
  }
  dragStop() {
    this.isChangingWidth = false;
    this.currentTreeBoxWidth = null;
    this.currentScreenX = null;
    window.removeEventListener('mousemove', this.dragMoving);
    window.removeEventListener('mouseup', this.dragStop);
  }
  render() {
    return (
      <div class="retrieve-collect-index">
        <CollectContainer
          dataList={this.filterCollectList}
          groupList={this.groupList}
          isShowGroupTitle={this.isShowGroupTitle}
          activeFavoriteID={this.activeFavoriteID}
          isSearchFilter={this.isSearchFilter}
          collectLoading={this.collectLoading || this.favoriteLoading}
          on-change={this.handleUserOperate}
        >
          <div class="search-container">
            <div class="fl-jcsb">
              <span class="search-title">{this.$t('收藏查询')}</span>
              <span
                class="bk-icon icon-cog"
                onClick={() => (this.isShowManageDialog = true)}
              ></span>
            </div>
            <div class="search-box fl-jcsb">
              <Input
                right-icon="bk-icon icon-search"
                vModel={this.searchVal}
                on-enter={this.handleSearchFavorite}
                on-right-icon-click={this.handleSearchFavorite}
              ></Input>
              <div class="fl-jcsb operate-box">
                <Popover
                  ref="popoverGroup"
                  tippy-options={this.tippyOption}
                  placement="bottom-start"
                  ext-cls="new-group-popover">
                  <span class="bk-icon icon-plus-circle"></span>
                  <div slot="content">
                    <Input
                      clearable
                      placeholder={this.$t('请输入组名')}
                      vModel={this.groupName}
                      maxlength={10}
                    ></Input>
                    <div class="operate-button">
                      <Button text onClick={() => this.handleClickGroupBtn('add')}>
                        {this.$t('确定')}
                      </Button>
                      <span onClick={() => this.handleClickGroupBtn('cancel')}>
                        {this.$t('取消')}
                      </span>
                    </div>
                  </div>
                </Popover>
                <Popover
                  ref="popoverSort"
                  tippy-options={this.tippyOption}
                  placement="bottom-start"
                  ext-cls="sort-group-popover">
                  <div class="icon-box">
                    <span class="bk-icon icon-sort"></span>
                  </div>
                  <div slot="content">
                    <RadioGroup vModel={this.sortType} class="sort-group-container">
                      {this.groupSortList.map(item => (
                        <Radio value={item.id}>{item.name}</Radio>
                      ))}
                    </RadioGroup>
                    <div class="operate-button">
                      <Button theme="primary" onClick={() => this.handleClickSortBtn('sort')}>
                        {this.$t('确定')}
                      </Button>
                      <Button onClick={() => this.handleClickSortBtn('cancel')}>
                        {this.$t('取消')}
                      </Button>
                    </div>
                  </div>
                </Popover>
              </div>
            </div>
          </div>
        </CollectContainer>
        <div
          class={['drag-border', { 'drag-ing': this.isChangingWidth }]}
          onMousedown={this.dragBegin}
        ></div>
        <ManageGroupDialog
          vModel={this.isShowManageDialog}
          onSubmit={value => value && this.getFavoriteList()} />
        <AddCollectDialog
          vModel={this.isShowAddNewFavoriteDialog}
          favoriteID={this.editFavoriteID}
          isClickFavoriteEdit={this.isClickFavoriteEdit}
          visibleFields={this.visibleFields}
          onSubmit={this.handleSubmitFavoriteData} />
      </div>
    );
  }
}
