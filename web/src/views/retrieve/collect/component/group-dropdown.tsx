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
import { Component, Prop, Inject, Ref } from 'vue-property-decorator';
import { Input, Button, Popover } from 'bk-magic-vue';
import { IGroupItem, IFavoriteItem } from '../collect-index';
import './group-dropdown.scss';

interface IProps {
  dropType: string;
  groupList: IGroupItem[];
  groupName: string;
  isHoverTitle: boolean;
  data: IGroupItem | IFavoriteItem;
}

@Component
export default class CollectGroup extends tsc<IProps> {
  @Inject('handleUserOperate') handleUserOperate;

  @Prop({ type: String, default: 'group' }) dropType: string; // 分组类型
  @Prop({ type: String, default: '' }) groupName: string; // 组名
  @Prop({ type: Boolean, default: false }) isHoverTitle: boolean; // 鼠标是否经过表头
  @Prop({ type: Array, default: () => [] }) groupList: IGroupItem[]; // 组列表
  @Prop({ type: Object, required: true }) data: IGroupItem | IFavoriteItem; // 所有数据
  @Ref('operate') private readonly operatePopoverRef: Popover; // 操作列表实例
  @Ref('groupMoveList') private readonly groupMoveListPopoverRef: Popover; // 移动到分组实例
  @Ref('titleDrop') private readonly titlePopoverRef: Popover; // 操作列表实例

  isShowNewGroupInput = false; // 是否展示新建分组
  isShowResetGroupName = false; // 是否展示重命名组名
  groupEditName = ''; // 创建分组名称
  operatePopoverInstance = null; // 收藏操作实例例
  groupListPopoverInstance = null; // 分组列表实例
  titlePopoverInstance = null; // 表头列表实例

  get unPrivateGroupList() {
    // 去掉个人组的组列表
    return this.groupList.slice(1);
  }

  get userMeta() {
    // 用户信息
    return this.$store.state.userMeta;
  }

  get showGroupList() {
    // 根据用户名判断是否时自己创建的收藏 若不是自己的则去除个人组选项
    return this.userMeta.username !== this.data.created_by
      ? this.unPrivateGroupList
      : this.groupList;
  }

  get isGroupDrop() {
    // 是否是组操作
    return this.dropType === 'group';
  }
  /** 重命名 */
  handleResetGroupName(e) {
    e.stopPropagation();
    this.handleUserOperate('reset-group-name', {
      group_id: this.data.group_id,
      group_new_name: this.groupEditName,
    });
    this.groupEditName = '';
    this.isShowResetGroupName = false;
  }
  /** 新增组 */
  handleChangeGroupInputStatus(e, type) {
    e.stopPropagation();
    type === 'add' && this.handleUserOperate('add-group', this.groupEditName);
    this.isShowNewGroupInput = false;
  }
  handleClickLi(type: string, value?: any) {
    if (type === 'move-favorite') {
      // 如果是移动到其他组 则更新移动的ID
      Object.assign(this.data, { group_id: value });
    }
    this.handleUserOperate(type, this.data);
    // 进行完操作时 清除组或者操作列表实例
    this.operatePopoverInstance?.destroy();
    this.operatePopoverInstance = null;
    this.groupListPopoverInstance?.destroy();
    this.groupListPopoverInstance = null;
    this.clearStatus(); // 清空状态
  }
  /** 点击移动分组操作 */
  handleClickMoveGroup(e) {
    // 判断当前是否有实例 如果有实例 则给操作列表常驻显示
    if (!this.groupListPopoverInstance) {
      this.groupListPopoverInstance = this.$bkPopover(e.target, {
        content: this.groupMoveListPopoverRef,
        trigger: 'click',
        interactive: true,
        theme: 'light shield',
        arrow: false,
        boundary: 'viewport',
        hideOnClick: true,
        offset: -1,
        distance: 2,
        sticky: true,
        placement: 'right-start',
        extCls: 'more-container',
        onHidden: () => {
          // 删除实例
          if (!this.operatePopoverInstance?.props.hideOnClick) {
            this.operatePopoverInstance?.destroy();
            this.operatePopoverInstance = null;
          }
          this.groupListPopoverInstance?.destroy();
          this.groupListPopoverInstance = null;
        },
      });
      this.groupListPopoverInstance.show(100);
      // 点击移动到其他分组时 操作列表要不受移动到分组的点击影响
      this.operatePopoverInstance.set({
        hideOnClick: false,
      });
    } else {
      this.operatePopoverInstance.set({
        hideOnClick: true,
      });
    }
  }
  /** 点击收藏的icon  显示更多操作 */
  handleClickIcon(e) {
    if (!this.operatePopoverInstance) {
      this.operatePopoverInstance = this.$bkPopover(e.target, {
        content: this.operatePopoverRef,
        interactive: true,
        theme: 'light shield',
        arrow: false,
        boundary: 'viewport',
        hideOnClick: true, // 先是可被外部点击隐藏
        distance: 4,
        sticky: true,
        placement: 'bottom-start',
        extCls: 'more-container',
        onHidden: () => {
          this.operatePopoverInstance?.destroy();
          this.operatePopoverInstance = null;
          this.clearStatus(); // 清空状态
        },
      });
      this.operatePopoverInstance.show(100);
    }
  }
  handleHoverIcon(e) {
    if (!this.titlePopoverInstance) {
      this.titlePopoverInstance = this.$bkPopover(e.target, {
        content: this.titlePopoverRef,
        interactive: true,
        theme: 'light',
        arrow: false,
        placement: 'bottom-start',
        boundary: 'viewport',
        extCls: 'more-container',
        distance: 4,
        onHidden: () => {
          this.titlePopoverInstance?.destroy();
          this.titlePopoverInstance = null;
          this.clearStatus(); // 清空状态
        },
      });
      this.titlePopoverInstance.show(100);
    }
  }

  handleResetGroupTitleName() {
    this.isShowResetGroupName = true;
    this.groupEditName = this.groupName;
  }

  clearStatus() {
    this.isShowNewGroupInput = false;
    this.isShowResetGroupName = false;
    this.groupEditName = '';
  }

  render() {
    const groupDropList = () => (
      <div style={{ display: 'none' }}>
        <ul class="dropdown-list" ref="titleDrop">
          {this.isShowResetGroupName ? (
            <li class="add-new-group-input">
              <Input
                clearable
                placeholder={this.$t('请输入组名')}
                vModel={this.groupName}
                maxlength={10}>
              </Input>
              <div class="operate-button">
                <Button text onClick={e => this.handleResetGroupName(e)}>
                  {this.$t('确定')}
                </Button>
              </div>
            </li>
          ) : (
            <li onClick={() => this.handleResetGroupTitleName()}>
              {this.$t('重命名')}
            </li>
          )}
          <li
            class="eye-catching"
            onClick={() => this.handleClickLi('dismiss-group')}
          >
            {this.$t('解散分组')}
          </li>
        </ul>
      </div>
    );
    const collectDropList = () => (
      <div style={{ display: 'none' }}>
        <ul class="dropdown-list" ref="operate">
          <li onClick={() => this.handleClickLi('share')}>{this.$t('分享')}</li>
          <li onClick={() => this.handleClickLi('edit-favorite')}>
            {this.$t('编辑')}
          </li>
          <li onClick={() => this.handleClickLi('create-copy')}>
            {this.$t('创建副本')}
          </li>
          <li class="move-group" onClick={this.handleClickMoveGroup}>
            {this.$t('移动至分组')}
            <span class="bk-icon icon-angle-right more-icon"></span>
          </li>
          <li onClick={() => this.handleClickLi('remove-group')}>
            {this.$t('从该组移除')}
          </li>
          <li
            class="eye-catching"
            onClick={() => this.handleClickLi('delete-favorite')}
          >
            {this.$t('删除')}
          </li>
        </ul>
      </div>
    );
    const groupList = () => (
      <div style={{ display: 'none' }}>
        <ul class="group-dropdown-list" ref="groupMoveList">
          {this.showGroupList.map(item => (
            <li
              onClick={() => this.handleClickLi('move-favorite', item.group_id)}
            >
              {item.group_name}
            </li>
          ))}
          {this.isShowNewGroupInput ? (
            <li class="add-new-group-input">
              <Input
                clearable
                placeholder={this.$t('请输入组名')}
                vModel={this.groupEditName}
                maxlength={10}>
              </Input>
              <div class="operate-button">
                <Button text onClick={e => this.handleChangeGroupInputStatus(e, 'add')}>
                  {this.$t('确定')}
                </Button>
                <span onClick={e => this.handleChangeGroupInputStatus(e, 'cancel')}>
                  {this.$t('取消')}
                </span>
              </div>
            </li>
          ) : (
            <li class="add-new-group" onClick={() => (this.isShowNewGroupInput = true)}>
              <span>
                <span class="bk-icon icon-close-circle"></span>
                <span>{this.$t('新建分组')}</span>
              </span>
            </li>
          )}
        </ul>
      </div>
    );
    return (
      <div>
        {this.isGroupDrop ? (
          <div>
            <div class="more-container" onMouseenter={this.handleHoverIcon}>
              {!this.isHoverTitle ? (
                <span class="title-number">{this.data.favorites.length}</span>
              ) : (
                <div class="more-box">
                  <span class="bk-icon icon-more"></span>
                </div>
              )}
            </div>
            {groupDropList()}
          </div>
        ) : (
          <div>
            <div class="more-container">
              {this.$slots.default ?? (
                <div
                  class={[
                    'more-box',
                    { 'is-click': !!this.operatePopoverInstance },
                  ]}
                  onMouseenter={this.handleClickIcon}
                >
                  <span class="bk-icon icon-more"></span>
                </div>
              )}
            </div>
            {collectDropList()}
            {groupList()}
          </div>
        )}
      </div>
    );
  }
}
