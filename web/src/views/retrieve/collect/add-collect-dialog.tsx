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
  Ref,
  Model,
} from "vue-property-decorator";
import {
  Dialog,
  Form,
  FormItem,
  Input,
  RadioGroup,
  Radio,
  Select,
  Option,
  CheckboxGroup,
  Checkbox,
  Switcher,
  Tag,
} from "bk-magic-vue";
import $http from "../../../api";
import "./add-collect-dialog.scss";

interface IProps {
  value?: boolean;
  favoriteID?: number;
  addFavoriteData?: object;
}

@Component
export default class CollectDialog extends tsc<IProps> {
  @Model("change", { type: Boolean, default: false }) value: IProps["value"];
  @Prop({ type: Number, default: -1 }) favoriteID: number;
  @Prop({ type: Object, default: () => ({}) }) addFavoriteData: object;
  @Ref("validateForm") validateFormRef: Form;
  searchFieldsList = []; // 表单模式显示字段
  isDisableSelect = false; // 是否禁用 所属组下拉框
  favoriteData = {
    // 收藏参数
    space_uid: -1,
    index_set_id: -1,
    name: "",
    group_id: 0,
    created_by: '',
    params: {
      host_scopes: {
        modules: [],
        ips: '',
      },
      addition: [],
      keyword: null,
      search_fields: [],
    },
    is_enable_display_fields: true,
    index_set_name: "",
    visible_type: "public",
    display_fields: [],
  };
  unknownGroupID = 0;
  privateGroupID = 0;
  switchVal = true;
  groupList = []; // 组列表
  formLoading = false;
  public rules = {
    name: [
      {
        required: true,
        trigger: "blur",
      }
    ],
  };

  get spaceUid() {
    return this.$store.state.spaceUid;
  }

  get isCreateFavorite() { // 根据传参判断新增还是编辑
    return Boolean(Object.keys(this.addFavoriteData).length);
  }

  get userName() { // 当前用户数据
    return this.$store.state.userMeta?.username;
  }

  get isCannotChangeVisible() {
    return !this.isCreateFavorite && this.favoriteData.created_by !== this.userName;
  }

  handleSelectGroup(nVal) {
    let visible_type = "public";
    this.isDisableSelect = false;
    nVal === this.privateGroupID && (visible_type = "private");
    nVal === this.privateGroupID && (this.isDisableSelect = true);
    Object.assign(this.favoriteData, { visible_type });
  }

  @Emit("change")
  handleShowChange(value = false) {
    return value;
  }

  @Emit("submit")
  handleSubmitChange(value) {
    return value;
  }

  async handleValueChange(value) {
    if (value) {
      await this.requestGroupList(); // 获取组列表
      if (this.isCreateFavorite) {
        // 判断是否是新增
        Object.assign(this.favoriteData, this.addFavoriteData); // 合并新增收藏详情
      } else {
        await this.getFavoriteData(this.favoriteID); //获取收藏详情
      }
      this.getSearchFieldsList(this.favoriteData.params.keyword); // 获取表单模式显示字段
      this.isDisableSelect = this.favoriteData.visible_type === "private";
    } else {
      this.handleSubmitChange(false);
      this.handleShowChange();
    }
  }

  handleClickRadio(value: string) {
    if (value === "private") {
      this.isDisableSelect = true;
      this.favoriteData.group_id = this.privateGroupID;
      this.favoriteData.visible_type = "private";
    } else {
      this.isDisableSelect = false;
      this.favoriteData.group_id = this.unknownGroupID;
      this.favoriteData.visible_type = "public";
    }
  }

  handleSubmitFormData() {
    this.validateFormRef.validate().then(
      () => {
        if (!this.unknownGroupID) return;
        const isCreate = this.favoriteID === -1;
        if (!this.favoriteData.group_id) this.favoriteData.group_id = this.unknownGroupID;
        this.handleUpdateFavorite(this.favoriteData, isCreate);
      },
      () => {}
    );
  }

  async getSearchFieldsList(keyword: string) {
    try {
      const res = await $http.request("favorite/getSearchFields", {
        data: { keyword },
      });
      this.searchFieldsList = res.data;
    } catch (error) {}
  }

  /** 更新收藏 */
  async handleUpdateFavorite(subData, isCreate = true) {
    const {
      index_set_id,
      params,
      name,
      group_id,
      display_fields,
      visible_type,
      id,
      is_enable_display_fields,
    } = subData;
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
      is_enable_display_fields,
    };
    const requestStr = isCreate ? "createFavorite" : "updateFavorite";
    try {
      const res = await $http.request(`favorite/${requestStr}`, {
        params: { id },
        data,
      });
      if (res.result) {
        this.handleShowChange();
        this.handleSubmitChange(true);
      } else {
        this.handleSubmitChange(false);
      }
    } catch (error) {}
  }

  /** 获取组列表 */
  async requestGroupList() {
    try {
      const res = await $http.request("favorite/getGroupList", {
        query: {
          space_uid: this.spaceUid,
        },
      });
      this.groupList = res.data;
      this.unknownGroupID = this.groupList[this.groupList.length - 1]?.id;
      this.privateGroupID = this.groupList[0]?.id;
    } catch (error) {}
  }
  /** 获取收藏详情 */
  async getFavoriteData(id) {
    this.formLoading = true;
    try {
      const res = await $http.request("favorite/getFavorite", {
        params: { id },
      });
      Object.assign(this.favoriteData, res.data);
    } catch (error) {}
    finally {
      this.formLoading = false;
    }
  }

  render() {
    return (
      <Dialog
        value={this.value}
        title={
          this.isCreateFavorite ? this.$t("新增收藏") : this.$t("编辑收藏")
        }
        header-position="left"
        ext-cls="add-collect-dialog"
        render-directive="if"
        width={640}
        mask-close={false}
        auto-close={false}
        on-value-change={this.handleValueChange}
        on-confirm={this.handleSubmitFormData}
      >
        <Form
          form-type="vertical"
          ref="validateForm"
          v-bkloading={{ isLoading: this.formLoading }}
          {...{
            props: {
              model: this.favoriteData,
              rules: this.rules,
            },
          }}
        >
          <div class="edit-information">
            <span>{this.$t("索引集")}</span>
            <span>{this.favoriteData.index_set_name}</span>
          </div>
          <div class="edit-information">
            <span>{this.$t("查询语句")}</span>
            <span>{this.favoriteData.params.keyword}</span>
          </div>
          <div class="form-item-container">
            <FormItem label={this.$t("收藏名")} required property="name">
              <Input
                class="collect-name"
                vModel={this.favoriteData.name}
                placeholder={`${this.$t('最多输入')} 20 ${this.$t('个字符')}`}
                maxlength={20}
              ></Input>
            </FormItem>
            <FormItem
              class="collect-radio"
              label={this.$t("可见范围")}
              required
            >
              <RadioGroup
                vModel={this.favoriteData.visible_type}
                on-change={this.handleClickRadio}
              >
                <Radio value={"public"}>{this.$t("公开")}</Radio>
                <Radio value={"private"} disabled={this.isCannotChangeVisible}>{this.$t("仅本人")}</Radio>
              </RadioGroup>
            </FormItem>
          </div>
          <div class="form-item-container">
            <FormItem label={this.$t("所属组")}>
              <Select
                vModel={this.favoriteData.group_id}
                disabled={this.isDisableSelect}
                on-change={this.handleSelectGroup}
              >
                {this.groupList.map((item) => (
                  <Option id={item.id} key={item.id} name={item.name}></Option>
                ))}
              </Select>
            </FormItem>
          </div>
          <FormItem label={this.$t("表单模式显示字段")}>
            <div class="explanation-field">
              {this.$t("表单模式显示字段文案")}
            </div>
            <CheckboxGroup vModel={this.favoriteData.params.search_fields}>
              {this.searchFieldsList.map((item) => (
                <Checkbox value={item.name}>{item.name}</Checkbox>
              ))}
            </CheckboxGroup>
          </FormItem>
          <FormItem
            label={this.$t("是否同时显示字段")}
            ext-cls="filed-label"
            desc-icon="bk-icon icon-info"
            desc-type="icon"
            desc={{
              content: `${this.$t("是否同时显示字段文案")}`,
              placements: ["right"],
            }}
          >
            <div class="filed-container">
              <Switcher
                vModel={this.favoriteData.is_enable_display_fields}
                theme="primary"
              ></Switcher>
              <span class="current-filed">{this.$t("当前字段")}：</span>
              {this.favoriteData.display_fields.map((item) => (
                <Tag>{item}</Tag>
              ))}
            </div>
          </FormItem>
        </Form>
      </Dialog>
    );
  }
}
