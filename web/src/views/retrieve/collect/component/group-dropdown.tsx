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
import { Component, Prop, Inject } from "vue-property-decorator";
import { Input, Button } from "bk-magic-vue";
import { IGroupItem, IFavoriteItem } from "../collect-index";
import "./group-dropdown.scss";

interface IProps {
  dropType: string;
  groupList: IGroupItem[];
  data: IGroupItem | IFavoriteItem;
}

@Component
export default class CollectGroup extends tsc<IProps> {
  @Inject("handleUserOperate") handleUserOperate;

  @Prop({ type: String, default: "group" }) dropType: string;
  @Prop({ type: Array, default: () => [] }) groupList: IGroupItem[];
  @Prop({ type: Object, required: true }) data: IGroupItem | IFavoriteItem;
  isExpand = false;
  nameValue = "";
  isShowNewGroupInput = false;
  isShowGroupUl = false;
  isShowResetGroupName = false;
  groupName = "";

  get unPrivateGroupList() {
    return this.groupList.slice(1);
  }

  get userMeta() {
    return this.$store.state.userMeta;
  }

  get showGroupList() {
    return this.userMeta.username !== this.data.created_by
      ? this.unPrivateGroupList
      : this.groupList;
  }

  /**
   * @description: 处理自动收起
   * @param {*} evt
   */
  handleClickOutSide(evt: Event) {
    const targetEl = evt.target as HTMLBaseElement;
    if (this.$el.contains(targetEl)) return;
    this.clearStatus();
  }
  /** 重命名 */
  handleResetGroupName(e) {
    e.stopPropagation();
    this.handleUserOperate("reset-group-name", {
      group_id: this.data.group_id,
      group_new_name: this.groupName,
    });
    this.groupName = "";
    this.isShowResetGroupName = false;
  }
  /** 新增组 */
  handleChangeGroupInputStatus(e, type) {
    e.stopPropagation();
    type === "add" && this.handleUserOperate("add-group", this.groupName);
    this.isShowNewGroupInput = false;
  }
  handleClickLi(type: string, value?: any) {
    if (type === "move-favorite") {
      Object.assign(this.data, { group_id: value });
    }
    this.handleUserOperate(type, this.data);
    this.clearStatus();
  }

  clearStatus() {
    this.isExpand = false;
    this.isShowGroupUl = false;
    this.isShowNewGroupInput = false;
    this.isShowResetGroupName = false;
    this.groupName = "";
  }

  /**
   * @description: 展开更多
   */
  handleExpandMore(val = !this.isExpand) {
    this.isExpand = val;
    if (this.isExpand) {
      document.addEventListener("click", this.handleClickOutSide, false);
    } else {
      document.removeEventListener("click", this.handleClickOutSide, false);
    }
  }
  render() {
    const groupDropList = () => (
      <ul class="dropdown-list">
        <li class="add-new-group-input" v-show={this.isShowResetGroupName}>
          <Input
            clearable
            placeholder={this.$t("请输入组名")}
            vModel={this.groupName}
            maxlength={10}
          ></Input>
          <div class="operate-button">
            <Button text onClick={(e) => this.handleResetGroupName(e)}>
              {this.$t("确定")}
            </Button>
            <span onClick={() => (this.isShowResetGroupName = false)}>
              {this.$t("取消")}
            </span>
          </div>
        </li>
        <li
          v-show={!this.isShowResetGroupName}
          onClick={() => (this.isShowResetGroupName = true)}
        >
          {this.$t("重命名")}
        </li>
        <li onClick={() => this.handleClickLi("dismiss-group")}>
          {this.$t("解散分组")}
        </li>
      </ul>
    );
    const collectDropList = () => (
      <ul
        class="dropdown-list"
        style={`display: ${this.isExpand ? "block" : ""}`}
      >
        <li onClick={() => this.handleClickLi("share")}>{this.$t("分享")}</li>
        <div class="more-group-container">
          <li class="move-group" onClick={() => (this.isShowGroupUl = true)}>
            {this.$t("移动至分组")}
            <span class="bk-icon icon-angle-right more-icon"></span>
          </li>
          <div class="group-div"></div>
          <ul
            class="group-dropdown-list"
            style={`display: ${this.isShowGroupUl ? "block" : ""}`}
          >
            {this.showGroupList.map((item) => (
              <li
                onClick={() =>
                  this.handleClickLi("move-favorite", item.group_id)
                }
              >
                {item.group_name}
              </li>
            ))}
            <li class="add-new-group-input" v-show={this.isShowNewGroupInput}>
              <Input
                clearable
                placeholder={this.$t("请输入组名")}
                vModel={this.groupName}
                maxlength={10}
              ></Input>
              <div class="operate-button">
                <Button
                  text
                  onClick={(e) => this.handleChangeGroupInputStatus(e, "add")}
                >
                  {this.$t("确定")}
                </Button>
                <span
                  onClick={(e) =>
                    this.handleChangeGroupInputStatus(e, "cancel")
                  }
                >
                  {this.$t("取消")}
                </span>
              </div>
            </li>
            <li
              class="add-new-group"
              v-show={!this.isShowNewGroupInput}
              onClick={() => (this.isShowNewGroupInput = true)}
            >
              <span>
                <span class="bk-icon icon-close-circle"></span>
                <span>{this.$t("新建分组")}</span>
              </span>
            </li>
          </ul>
        </div>
        <li onClick={() => this.handleClickLi("remove-group")}>
          {this.$t("从该组移除")}
        </li>
        <li onClick={() => this.handleClickLi("edit-favorite")}>
          {this.$t("编辑")}
        </li>
        <li onClick={() => this.handleClickLi("delete-favorite")}>
          {this.$t("删除")}
        </li>
      </ul>
    );
    return (
      <div
        class={["more-container", { "is-group": this.dropType === "group" }]}
      >
        {this.$slots.default ?? (
          <div
            class={["more-box", { "is-click": this.isExpand }]}
            onClick={this.handleExpandMore}
          >
            <span class="bk-icon icon-more"></span>
          </div>
        )}
        <div style="height: 4px; width: 100%; position: absolute;"></div>
        {this.dropType === "group" ? groupDropList() : collectDropList()}
      </div>
    );
  }
}
