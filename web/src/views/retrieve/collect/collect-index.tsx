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

import { Component as tsc } from "vue-tsx-support";
import {
  Component,
  Emit,
  Prop,
  PropSync,
  Watch,
  Ref,
} from "vue-property-decorator";
import { Input, Popover, Button, Radio, RadioGroup } from "bk-magic-vue";
import CollectContainer from "./collect-container";
import ManageGroupDialog from "./manage-group-dialog";
import AddCollectDialog from "./add-collect-dialog";
import { copyMessage, deepClone } from "../../../common/util";
import $http from "../../../api";
import "./collect-index.scss";

interface IProps {
  collectWidth: number;
  isShowCollect: boolean;
  indexId: string;
  activeFavorite: IFavoriteItem;
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

type visibleType = "private" | "public" | "unknown";

@Component
export default class CollectIndex extends tsc<IProps> {
  @PropSync("width", { type: Number }) collectWidth: number;
  @PropSync("isShow", { type: Boolean }) isShowCollect: boolean;
  @Prop({ type: String, required: true }) indexId: string;
  @Prop({ type: Object, default: () => ({}) }) activeFavorite: IFavoriteItem;
  @Ref("popoverGroup") popoverGroupRef: Popover;
  @Ref("popoverSort") popoverSortRef: Popover;

  collectMinWidth = 240; // 收藏最小栏宽度
  collectMaxWidth = 500; // 收藏栏最大宽度
  currentTreeBoxWidth = null; // 当前收藏容器的宽度
  currentScreenX = null;
  isChangingWidth = false; // 是否正在拖拽
  isShowManageDialog = false; // 是否展示管理弹窗
  isSearchFilter = false; // 是否搜索过滤
  isShowAddNewFavoriteDialog = false; // 是否展示编辑收藏弹窗
  collectLoading = false; // 分组容器loading
  isShowGroupTitle = true; // 是否展示分组头部
  searchVal = ""; // 搜索
  groupName = ""; // 新增组
  privateGroupID = 0; // 私人组ID
  unknownGroupID = 0; // 公开组ID
  activeFavoriteID = -1; // 当前点击的收藏ID
  baseSortType = "NAME_ASC"; // 排序参数
  sortType = "NAME_ASC"; // 展示的排序参数
  editFavoriteID = -1; // 点击编辑时的收藏ID
  groupSortList = [
    // 排序展示列表
    {
      name: `${this.$t("按名称")} A - Z ${this.$t("排序")}`,
      id: "NAME_ASC",
    },
    {
      name: `${this.$t("按名称")} Z - A ${this.$t("排序")}`,
      id: "NAME_DESC",
    },
    {
      name: this.$t("按更新时间排序"),
      id: "UPDATED_AT_DESC",
    },
  ];
  tippyOption = {
    trigger: "click",
    interactive: true,
    theme: "light",
  };
  groupList: IGroupItem[] = []; // 分组列表
  collectList: IGroupItem[] = []; // 收藏列表
  filterCollectList: IGroupItem[] = []; // 搜索的收藏列表

  get spaceUid() {
    return this.$store.state.spaceUid;
  }

  @Watch("isShowCollect")
  async handleShowCollect(value) {
    if (value) {
      this.baseSortType = localStorage.getItem("favoriteSortType") || "NAME_ASC";
      this.sortType = this.baseSortType;
      this.getFavoriteData();
    } else {
      this.collectList = [];
      this.filterCollectList = [];
      this.groupList = [];
    }
  }

  @Watch("indexId")
  async handleChangeIndexSet(value) {
    this.collectList = [];
    this.filterCollectList = [];
    this.groupList = [];
    if (!this.isShowCollect) return;
    this.getFavoriteData();
  }

  @Watch("activeFavorite", { deep: true })
  handleWatchFavorite(value) {
    this.activeFavoriteID = value !== null ? this.activeFavorite?.id : 0;
  }

  @Emit("handleClick")
  handleClickFavorite(value) {
    return value;
  }

  async handleUserOperate(obj) {
    const { type, value } = obj;
    switch (type) {
      case "click-favorite": // 点击收藏
        this.activeFavoriteID = value.id;
        this.handleClickFavorite(value);
        break;
      case "add-group": // 新增组
        await this.handleUpdateGroupName({ group_new_name: value });
        this.getFavoriteData();
        break;
      case "reset-group-name": // 重命名
        await this.handleUpdateGroupName(value, false);
        this.getFavoriteData();
        break;
      case "move-favorite": // 移动收藏
        const visible_type =
          value.group_id === this.privateGroupID ? "private" : "public";
        Object.assign(value, { visible_type });
        await this.handleUpdateFavorite(value);
        this.getFavoriteData();
        break;
      case "remove-group": // 从组中移除收藏（移动至未分组）
        Object.assign(value, {
          visible_type: "public",
          group_id: this.unknownGroupID,
        });
        await this.handleUpdateFavorite(value);
        this.getFavoriteData();
        break;
      case "edit-favorite": // 编辑收藏
        this.editFavoriteID = value.id;
        this.isShowAddNewFavoriteDialog = true;
        break;
      case "delete-favorite": // 删除收藏
        await this.deleteFavorite(value.id);
        this.getFavoriteData();
        break;
      case "dismiss-group": // 解散分组
        await this.deleteGroup(value.group_id);
        this.getFavoriteData();
        break;
      case "share":
        let shareUrl = window.SITE_URL;
        if (!shareUrl.startsWith('/')) shareUrl = `/${shareUrl}`;
        if (!shareUrl.endsWith('/')) shareUrl += '/';
        const params = encodeURIComponent(JSON.stringify({ ...value.params }));
        shareUrl = `${window.location.origin + shareUrl}#/retrieve/${value.index_set_id}?spaceUid=${value.space_uid}&retrieveParams=${params}`;
        copyMessage(shareUrl, this.$t("复制成功"));
        break;
      case "drag-move-end":
        try {
          await $http.request("favorite/groupUpdateOrder", {
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
    if (clickType === "add") {
      await this.handleUpdateGroupName({ group_new_name: this.groupName });
      this.getFavoriteData();
    }
    setTimeout(() => {
      this.groupName = "";
    }, 500);
    this.popoverGroupRef.hideHandler();
  }

  /** 排序 */
  handleClickSortBtn(clickType: string) {
    if (clickType === "sort") {
      this.baseSortType = this.sortType;
      localStorage.setItem("favoriteSortType", this.sortType);
      this.getFavoriteData();
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
    if (this.searchVal === "") {
      this.filterCollectList = this.collectList;
      this.isSearchFilter = false;
      return;
    }
    this.isSearchFilter = true;
    this.filterCollectList = this.collectList
      .map((item) => ({
        ...item,
        favorites: item.favorites.filter(
          (fItem) =>
            fItem.created_by.includes(this.searchVal) ||
            fItem.name.includes(this.searchVal)
        ),
      }))
      .filter((item) => item.favorites.length);
    setTimeout(() => {
      if (isRequest) this.collectLoading = false;
    }, 500);
  }

  /** 新增或更新组名 */
  async handleUpdateGroupName(groupObj, isCreate = true) {
    const { group_id, group_new_name } = groupObj;
    const params = { group_id };
    const data = { name: group_new_name, space_uid: this.spaceUid };
    const requestStr = isCreate ? "createGroup" : "updateGroupName";
    try {
      const res = await $http.request(`favorite/${requestStr}`, {
        params,
        data,
      });
      if (res.result) this.showMessagePop(this.$t("操作成功"));
    } catch (error) {}
  }

  /** 获取收藏列表 */
  async getFavoriteList() {
    try {
      this.collectLoading = true;
      const res = await $http.request("favorite/getFavoriteByGroupList", {
        query: {
          space_uid: this.spaceUid,
          order_type: this.baseSortType,
        },
      });
      this.collectList = res.data;
      this.handleSearchFavorite();
      this.isShowGroupTitle = !(
        this.collectList.length === 2 && !this.collectList[0].favorites.length
      );
    } catch (error) {
    } finally {
      this.collectLoading = false;
    }
  }

  /** 获取组列表 */
  async getGroupList(isInit = false) {
    try {
      const res = await $http.request("favorite/getGroupList", {
        query: {
          space_uid: this.spaceUid,
        },
      });
      this.groupList = res.data.map((item) => ({
        group_id: item.id,
        group_name: item.name,
        group_type: item.group_type,
      }));
      if (isInit) {
        this.unknownGroupID = this.groupList[this.groupList.length - 1]?.group_id;
        this.privateGroupID = this.groupList[0]?.group_id;
      }
    } catch (error) {}
  }

  /** 解散分组 */
  async deleteGroup(group_id) {
    try {
      const res = await $http.request("favorite/deleteGroup", {
        params: { group_id },
      });
      if (res.result) this.showMessagePop(this.$t("操作成功"));
    } catch (error) {}
  }

  /** 删除收藏 */
  async deleteFavorite(favorite_id) {
    try {
      const res = await $http.request("favorite/deleteFavorite", {
        params: { favorite_id },
      });
      if (res.result) this.showMessagePop(this.$t("删除成功"));
    } catch (error) {}
  }

  async getFavoriteData() {
    Promise.all([this.getFavoriteList(), this.getGroupList(true)]).then(()=>{
      this.filterCollectList = deepClone(this.collectList);
    })
  }

  showMessagePop(message, theme = "success") {
    this.$bkMessage({
      message,
      theme,
    });
  }

  /** 更新收藏 */
  async handleUpdateFavorite(favoriteData) {
    try {
      const {
        index_set_id,
        params,
        name,
        group_id,
        display_fields,
        visible_type,
        id,
      } = favoriteData;
      const { host_scopes, addition, keyword, search_fields } = params;
      const data = {
        index_set_id,
        name,
        group_id,
        display_fields,
        visible_type,
        host_scopes,
        addition,
        keyword,
        search_fields,
        space_uid: this.spaceUid,
      };
      const res = await $http.request("favorite/updateFavorite", {
        params: { id },
        data,
      });
      if (res.result) this.showMessagePop(this.$t("操作成功"));
    } catch (error) {}
  }

  /** 控制页面布局宽度 */
  dragBegin(e) {
    this.isChangingWidth = true;
    this.currentTreeBoxWidth = this.collectWidth;
    this.currentScreenX = e.screenX;
    window.addEventListener("mousemove", this.dragMoving, { passive: true });
    window.addEventListener("mouseup", this.dragStop, { passive: true });
  }
  dragMoving(e) {
    const newTreeBoxWidth =
      this.currentTreeBoxWidth + e.screenX - this.currentScreenX;
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
    window.removeEventListener("mousemove", this.dragMoving);
    window.removeEventListener("mouseup", this.dragStop);
  }
  render() {
    return (
      <div class="retrieve-collect-index">
        {this.isShowCollect ? (
          <CollectContainer
            dataList={this.filterCollectList}
            groupList={this.groupList}
            isShowGroupTitle={this.isShowGroupTitle}
            activeFavoriteID={this.activeFavoriteID}
            isSearchFilter={this.isSearchFilter}
            collectLoading={this.collectLoading}
            on-change={this.handleUserOperate}
          >
            <div class="search-container">
              <div class="fl-jcsb">
                <span class="search-title">{this.$t("收藏查询")}</span>
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
                    ext-cls="new-group-popover"
                  >
                    <span class="bk-icon icon-plus-circle"></span>
                    <div slot="content">
                      <Input
                        clearable
                        placeholder={this.$t("请输入组名")}
                        vModel={this.groupName}
                        maxlength={10}
                      ></Input>
                      <div class="operate-button">
                        <Button
                          text
                          onClick={() => this.handleClickGroupBtn("add")}
                        >
                          {this.$t("确定")}
                        </Button>
                        <span
                          onClick={() => this.handleClickGroupBtn("cancel")}
                        >
                          {this.$t("取消")}
                        </span>
                      </div>
                    </div>
                  </Popover>
                  <Popover
                    ref="popoverSort"
                    tippy-options={this.tippyOption}
                    placement="bottom-start"
                    ext-cls="sort-group-popover"
                  >
                    <div class="icon-box">
                      <span class="bk-icon icon-sort"></span>
                    </div>
                    <div slot="content">
                      <RadioGroup
                        vModel={this.sortType}
                        class="sort-group-container"
                      >
                        {this.groupSortList.map((item) => (
                          <Radio value={item.id}>{item.name}</Radio>
                        ))}
                      </RadioGroup>
                      <div class="operate-button">
                        <Button
                          theme="primary"
                          onClick={() => this.handleClickSortBtn("sort")}
                        >
                          {this.$t("确定")}
                        </Button>
                        <Button
                          onClick={() => this.handleClickSortBtn("cancel")}
                        >
                          {this.$t("取消")}
                        </Button>
                      </div>
                    </div>
                  </Popover>
                </div>
              </div>
            </div>
          </CollectContainer>
        ) : undefined}
        <div
          class={["drag-border", { "drag-ing": this.isChangingWidth }]}
          onMousedown={this.dragBegin}
        ></div>
        <ManageGroupDialog 
          vModel={this.isShowManageDialog}
          on-submit={(value) => value && this.getFavoriteData()} />
        <AddCollectDialog
          vModel={this.isShowAddNewFavoriteDialog}
          favoriteID={this.editFavoriteID}
          on-submit={(value) => value && this.getFavoriteData()}
        />
      </div>
    );
  }
}
