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
import { Component, Prop, Inject } from 'vue-property-decorator';
import { formatDate } from '../../../common/util';
import GroupDropdown from './component/group-dropdown';
import { IGroupItem, IFavoriteItem } from './collect-index';
import './collect-group.scss';

interface ICollectProps {
  collectItem: IGroupItem;
  groupList: IGroupItem[];
  activeFavoriteID: number;
  isShowGroupTitle: boolean;
  isSearchFilter: boolean;
}

@Component
export default class CollectGroup extends tsc<ICollectProps> {
  @Prop({ type: Object, required: true }) collectItem: IGroupItem; // 组的收藏列表
  @Prop({ type: Number, required: true }) activeFavoriteID: number; // 点击的活跃ID
  @Prop({ type: Boolean, default: true }) isShowGroupTitle: boolean; // 是否展示组标题
  @Prop({ type: Boolean, default: false }) isSearchFilter: boolean; // 是否搜索过
  @Prop({ type: Array, default: () => [] }) groupList: IGroupItem[]; // 组列表
  @Inject('handleUserOperate') handleUserOperate;
  isHiddenList = false; // 是否不显示列表
  isHoverTitle = false;
  clickDrop = false; // 点击侧边更多
  favoriteMessageInstance = null;

  get isCannotChange() {
    return ['private', 'unknown'].includes(this.collectItem.group_type);
  }
  get isShowTitleIcon() {
    return this.collectItem.group_type !== 'unknown';
  }

  handleClickCollect(item: IFavoriteItem) {
    setTimeout(() => {
      this.clickDrop = false;
    }, 100);
    if (this.clickDrop) return;
    this.clickDrop = false;
    this.handleUserOperate('click-favorite', item);
  }
  handleHoverTitle(type: boolean) {
    if (!type) {
      setTimeout(() => {
        this.isHoverTitle = type;
      }, 200);
      return;
    }
    this.isHoverTitle = type;
  }
  handleHoverFavoriteName(e, item) {
    if (!this.favoriteMessageInstance) {
      this.favoriteMessageInstance = this.$bkPopover(e.target, {
        content: `<div style="font-size: 12px;">
                  <p>${this.$t('创建人')}: ${item.created_by || '--'}</p>
                  <p>${this.$t('修改人')}: ${item.updated_by || '--'}</p>
                  <p>${this.$t('更新时间')}: ${formatDate(item.updated_at)}</p>
                </div>`,
        arrow: true,
        placement: 'top',
        onHidden: () => {
          this.favoriteMessageInstance?.destroy();
          this.favoriteMessageInstance = null;
        },
      });
      this.favoriteMessageInstance.show(500);
    }
  }

  render() {
    const groupDropdownSlot = (groupName) => {
      return !this.isCannotChange ? (
        <GroupDropdown
          data={this.collectItem}
          group-list={this.groupList}
          group-name={groupName}
          is-hover-title={this.isHoverTitle} />
      ) : <span class="title-number">{this.collectItem.favorites.length}</span>;
    };
    const collectDropdownSlot = item => (
      <div onClick={() => (this.clickDrop = true)}>
        <GroupDropdown
          drop-type={'collect'}
          data={item}
          group-list={this.groupList} />
      </div>
    );
    return (
      <div class="retrieve-collect-group">
        {this.isShowGroupTitle ? (
          <div
            class={[
              'group-title fl-jcsb',
              {
                'is-active': !this.isHiddenList,
                'is-move-cur': !this.isSearchFilter && !this.isCannotChange,
              },
            ]}
            onMouseenter={() => this.handleHoverTitle(true)}
            onMouseleave={() => this.handleHoverTitle(false)}>
            <span class="group-cur" onClick={() => (this.isHiddenList = !this.isHiddenList)}>
              <span class={['bk-icon icon-play-shape', { 'is-active': !this.isHiddenList }]}></span>
              <span>{this.collectItem.group_name}</span>
            </span>
            {groupDropdownSlot(this.collectItem.group_name)}
          </div>
        ) : undefined}
        <div class={['group-list', { 'list-hidden': this.isHiddenList }]}>
          {this.collectItem.favorites.map((item, index) => (
            <div
              key={index}
              class={['group-item', { active: item.id === this.activeFavoriteID }]}
              onClick={() => this.handleClickCollect(item)}>
                <div class={{
                  'group-item-left': true,
                  'active-name': item.id === this.activeFavoriteID,
                }}>
                    <div class="fav-name" onMouseenter={e => this.handleHoverFavoriteName(e, item)}>
                      <span>{item.name}</span>
                      {!item.is_active ? (
                        <span v-bk-tooltips={{ content: this.$t('数据源不存在'), placement: 'right' }}>
                          <span class="bk-icon log-icon icon-shixiao"></span>
                        </span>
                      ) : undefined}
                    </div>
                  {collectDropdownSlot(item)}
                </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
}
