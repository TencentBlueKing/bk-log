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
import { Input, Popover, Button, Radio, RadioGroup, Form, FormItem } from 'bk-magic-vue';
import CollectContainer from './collect-container';
import ManageGroupDialog from './manage-group-dialog';
import AddCollectDialog from './add-collect-dialog';
import { copyMessage, deepClone } from '../../../common/util';
import $http from '../../../api';
import './collect-index.scss';

interface IProps {
  collectWidth: number;
  isShowCollect: boolean;
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
  @Prop({ type: Boolean, required: true }) favoriteLoading: boolean;
  @Prop({ type: Array, required: true }) favoriteList: any;
  @Prop({ type: Number, required: true }) activeFavoriteID: number;
  @Prop({ type: Array, default: () => [] }) visibleFields: Array<any>;
  @Ref('popoverGroup') popoverGroupRef: Popover;
  @Ref('popoverSort') popoverSortRef: Popover;
  @Ref('checkInputForm') private readonly checkInputFormRef: Form; // 移动到分组实例

  collectMinWidth = 160; // 收藏最小栏宽度
  collectMaxWidth = 400; // 收藏栏最大宽度
  currentTreeBoxWidth = null; // 当前收藏容器的宽度
  currentScreenX = null;
  isChangingWidth = false; // 是否正在拖拽
  isShowManageDialog = false; // 是否展示管理弹窗
  isSearchFilter = false; // 是否搜索过滤
  isShowAddNewFavoriteDialog = false; // 是否展示编辑收藏弹窗
  collectLoading = false; // 分组容器loading
  searchVal = ''; // 搜索
  // groupName = ''; // 新增组
  privateGroupID = 0; // 私人组ID
  unknownGroupID = 0; // 公开组ID
  baseSortType = 'NAME_ASC'; // 排序参数
  sortType = 'NAME_ASC'; // 展示的排序参数
  editFavoriteID = -1; // 点击编辑时的收藏ID
  groupNameMap = {
    unknown: window.mainComponent.$t('未分组'),
    private: window.mainComponent.$t('个人收藏'),
  }
  verifyData = {
    groupName: '',
  };
  groupSortList = [
    // 排序展示列表
    {
      name: window.mainComponent.$t('按名称 {n} 排序', { n: 'A - Z' }),
      id: 'NAME_ASC',
    },
    {
      name: window.mainComponent.$t('按名称 {n} 排序', { n: 'Z - A' }),
      id: 'NAME_DESC',
    },
    {
      name: window.mainComponent.$t('按更新时间排序'),
      id: 'UPDATED_AT_DESC',
    },
  ];
  public rules = {
    groupName: [
      {
        validator: this.checkName,
        message: window.mainComponent.$t('{n}不规范, 包含特殊符号', { n: window.mainComponent.$t('组名') }),
        trigger: 'blur',
      },
      {
        validator: this.checkExistName,
        message: window.mainComponent.$t('组名重复'),
        trigger: 'blur',
      },
      {
        required: true,
        message: window.mainComponent.$t('必填项'),
        trigger: 'blur',
      },
      {
        max: 30,
        message: window.mainComponent.$t('不能多于30个字符'),
        trigger: 'blur',
      },
    ],
  };
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

  get allFavoriteNumber() {
    return this.favoriteList.reduce((pre: number, cur) => (pre += cur.favorites.length, pre), 0);
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


  @Emit('handleClick')
  handleClickFavorite(value) {
    return value;
  }

  @Emit('isRefreshFavorite')
  handleUpdateActiveFavoriteData(value) {
    return value;
  }

  @Emit('favoriteDialogSubmit')
  handleSubmitFavoriteData({ isCreate, resValue }) {
    return {
      isCreate,
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
          subTitle: this.$t('当前收藏名为 {n}，确认是否删除？', { n: value.name }),
          type: 'warning',
          confirmFn: async () => {
            await this.deleteFavorite(value.id);
            this.getFavoriteList();
          },
        });
        break;
      case 'dismiss-group': // 解散分组
        this.$bkInfo({
          title: this.$t('当前分组名为 {n}，确认是否解散？', { n: value.group_name }),
          subTitle: `${this.$t('解散分组后，原分组内的收藏将移至未分组中。')}`,
          type: 'warning',
          confirmFn: async () => {
            await this.deleteGroup(value.group_id);
            this.getFavoriteList();
          },
        });
        break;
      case 'share': {
        let shareUrl = window.SITE_URL;
        if (!shareUrl.startsWith('/')) shareUrl = `/${shareUrl}`;
        if (!shareUrl.endsWith('/')) shareUrl += '/';
        const params = encodeURIComponent(JSON.stringify({ ...value.params }));
        shareUrl = `${window.location.origin + shareUrl}#/retrieve/${value.index_set_id}?spaceUid=${value.space_uid}&retrieveParams=${params}`;
        copyMessage(shareUrl, this.$t('复制成功'));
      }
        break;
      case 'drag-move-end':
        // $http.request('favorite/groupUpdateOrder', {
        //   data: {
        //     space_uid: this.spaceUid,
        //     group_order: value,
        //   },
        // });
        break;
      case 'create-copy': {
        const {
          index_set_id,
          params,
          name,
          group_id,
          display_fields,
          visible_type,
          is_enable_display_fields,
        } = value;
        const { host_scopes, addition, keyword, search_fields } = params;
        const data = {
          name: `${name} ${this.$t('副本')}`,
          group_id,
          display_fields,
          visible_type,
          host_scopes,
          addition,
          keyword,
          search_fields,
          is_enable_display_fields,
          index_set_id,
          space_uid: this.spaceUid,
        };
        $http.request('favorite/createFavorite', { data }).then((res) => {
          this.showMessagePop(this.$t('创建成功'));
          this.handleSubmitFavoriteData({ isCreate: true, resValue: res.data });
        });
      }
        break;
      default:
    }
  }
  checkName() {
    if (this.verifyData.groupName.trim() === '') return true;
    return /^[\u4e00-\u9fa5_a-zA-Z0-9`~!@#$%^&*()_\-+=<>?:"\s{}|,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]+$/im.test(this.verifyData.groupName.trim());
  }
  checkExistName() {
    return !this.groupList.some(item => item.group_name === this.verifyData.groupName);
  }
  /** 新增组 */
  handleClickGroupBtn(clickType: string) {
    if (clickType === 'add') {
      this.checkInputFormRef.validate().then(async () => {
        if (!this.verifyData.groupName.trim()) return;
        await this.handleUpdateGroupName({ group_new_name: this.verifyData.groupName });
        this.getFavoriteList();
        this.popoverGroupRef.hideHandler();
        setTimeout(() => {
          this.verifyData.groupName = '';
        }, 500);
      });
    }
    if (clickType === 'cancel') {
      this.popoverGroupRef.hideHandler();
      this.checkInputFormRef.clearError();
    };
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

  handleInputSearchFavorite() {
    if (this.searchVal === '') this.handleSearchFavorite();
  }

  /** 新增或更新组名 */
  async handleUpdateGroupName(groupObj, isCreate = true) {
    const { group_id, group_new_name } = groupObj;
    const params = { group_id };
    const data = { name: group_new_name, space_uid: this.spaceUid };
    const requestStr = isCreate ? 'createGroup' : 'updateGroupName';
    await $http.request(`favorite/${requestStr}`, {
      params,
      data,
    }).then(() => {
      this.showMessagePop(this.$t('操作成功'));
    });
  }

  handleInitFavoriteList(value) {
    this.collectList = value.map(item => ({
      ...item,
      group_name: this.groupNameMap[item.group_type] ?? item.group_name,
    }));
    this.groupList = value.map(item => ({
      group_id: item.group_id,
      group_name: this.groupNameMap[item.group_type] ?? item.group_name,
      group_type: item.group_type,
    }));
    this.unknownGroupID = this.groupList[this.groupList.length - 1]?.group_id;
    this.privateGroupID = this.groupList[0]?.group_id;
    this.handleSearchFavorite();
    // 当前只有未分组和个人收藏时 判断未分组是否有数据 如果没有 则不展示未分组
    if (this.collectList.length === 2 && !this.collectList[1].favorites.length) {
      this.collectList = [this.collectList[0]];
    }
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
    await $http.request('favorite/deleteGroup', {
      params: { group_id },
    }).then(() => {
      this.showMessagePop(this.$t('操作成功'));
    });
  }

  /** 删除收藏 */
  async deleteFavorite(favorite_id) {
    await $http.request('favorite/deleteFavorite', {
      params: { favorite_id },
    }).then(() => {
      this.showMessagePop(this.$t('删除成功'));
    });
  }

  showMessagePop(message, theme = 'success') {
    this.$bkMessage({
      message,
      theme,
    });
  }

  /** 更新收藏 */
  async handleUpdateFavorite(favoriteData) {
    const {
      params,
      name,
      group_id,
      display_fields,
      visible_type,
      id,
    } = favoriteData;
    const { ip_chooser, addition, keyword, search_fields } = params;
    const data = {
      name,
      group_id,
      display_fields,
      visible_type,
      ip_chooser,
      addition,
      keyword,
      search_fields,
    };
    await $http.request('favorite/updateFavorite', {
      params: { id },
      data,
    }).then(() => {
      this.showMessagePop(this.$t('操作成功'));
    });
  }
  handleGroupKeyDown(value: string, event) {
    if (event.code === 'Tab' && !!value) {
      this.handleUserOperate({
        type: 'add-group',
        value,
      });
      this.popoverGroupRef.hideHandler();
      setTimeout(() => {
        this.verifyData.groupName = '';
      }, 500);
    }
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
      localStorage.setItem('isAutoShowCollect', 'false');
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
          activeFavoriteID={this.activeFavoriteID}
          isSearchFilter={this.isSearchFilter}
          collectLoading={this.collectLoading || this.favoriteLoading}
          on-change={this.handleUserOperate}>
          <div class="search-container">
            <div class="fl-jcsb">
              <span class="search-title fl-jcsb">
                {this.$t('收藏查询')}
                <span class="favorite-number">{this.allFavoriteNumber}</span>
              </span>
              <span
                class="bk-icon log-icon icon-wholesale-editor"
                onClick={() => (this.isShowManageDialog = true)}
              ></span>
            </div>
            <div class="search-box fl-jcsb">
              <Input
                right-icon="bk-icon icon-search"
                vModel={this.searchVal}
                placeholder={this.$t('搜索收藏名')}
                on-enter={this.handleSearchFavorite}
                onKeyup={this.handleInputSearchFavorite}
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
                    <Form
                      labelWidth={0}
                      style={{ width: '100%' }}
                      ref="checkInputForm"
                      {...{
                        props: {
                          model: this.verifyData,
                          rules: this.rules,
                        },
                      }}>
                      <FormItem property="groupName">
                        <Input
                          clearable
                          placeholder={this.$t('{n}, （长度30个字符）', { n: this.$t('请输入组名') })}
                          vModel={this.verifyData.groupName}
                          onKeydown={this.handleGroupKeyDown}
                          onEnter={() => this.handleClickGroupBtn('add')}>
                        </Input>
                      </FormItem>
                    </Form>
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
                    <span style={{ fontSize: '14px', marginTop: '8px' }}>{this.$t('收藏名排序')}</span>
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
          <div
            class={`new-search ${this.activeFavoriteID === -1 && 'active'}`}
            onClick={() => this.handleClickFavorite(undefined)}>
            <span class="bk-icon icon-enlarge-line"></span>
            <span>{this.$t('新检索')}</span>
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
          favoriteList={this.favoriteList}
          isClickFavoriteEdit={this.isClickFavoriteEdit}
          visibleFields={this.visibleFields}
          onSubmit={this.handleSubmitFavoriteData} />
      </div>
    );
  }
}
