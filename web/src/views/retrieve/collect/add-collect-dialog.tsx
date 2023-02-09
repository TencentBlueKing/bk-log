/* eslint-disable camelcase */
/* eslint-disable no-useless-escape */
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
  Ref,
  Model,
} from 'vue-property-decorator';
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
} from 'bk-magic-vue';
import $http from '../../../api';
import './add-collect-dialog.scss';

interface IProps {
  value: boolean;
  favoriteID: number;
  addFavoriteData: object;
  replaceData?: object;
  isClickFavoriteEdit?: boolean;
  visibleFields: Array<any>;
  favoriteList: Array<any>;
}

@Component
export default class CollectDialog extends tsc<IProps> {
  @Model('change', { type: Boolean, default: false }) value: IProps['value'];
  @Prop({ type: Number, default: -1 }) favoriteID: number; // 编辑收藏ID
  @Prop({ type: Object, default: () => ({}) }) addFavoriteData: object; // 新增收藏的数据
  @Prop({ type: Object, default: () => ({}) }) replaceData: object; // 替换收藏的params数据
  @Prop({ type: Boolean, default: false }) isClickFavoriteEdit: boolean; // 当前编辑的收藏是否是点击活跃的
  @Prop({ type: Array, default: () => [] }) visibleFields: Array<any>; // 字段
  @Prop({ type: Array, default: () => [] }) favoriteList: Array<any>; // 收藏列表
  @Ref('validateForm') validateFormRef: Form;
  @Ref('checkInputForm') checkInputFormRef: Form;
  searchFieldsList = []; // 表单模式显示字段
  isDisableSelect = false; // 是否禁用 所属组下拉框
  isShowAddGroup = true;
  // groupName = '';
  verifyData = {
    groupName: '',
  };
  baseFavoriteData = {
    // 收藏参数
    space_uid: -1,
    index_set_id: -1,
    name: '',
    group_id: null,
    created_by: '',
    params: {
      host_scopes: {
        modules: [],
        ips: '',
        target_nodes: [],
        target_node_type: '',
      },
      addition: [],
      keyword: null,
      search_fields: [],
    },
    is_enable_display_fields: false,
    index_set_name: '',
    visible_type: 'public',
    display_fields: [],
  };
  favoriteData = {
    // 收藏参数
    space_uid: -1,
    index_set_id: -1,
    name: '',
    group_id: null,
    created_by: '',
    params: {
      host_scopes: {
        modules: [],
        ips: '',
        target_nodes: [],
        target_node_type: '',
      },
      addition: [],
      keyword: null,
      search_fields: [],
    },
    is_enable_display_fields: false,
    index_set_name: '',
    visible_type: 'public',
    display_fields: [],
  };
  publicGroupList = []; // 可见状态为公共的时候显示的收藏组
  privateGroupList = []; // 个人收藏 group_name替换为本人
  unknownGroupID = 0;
  privateGroupID = 0;
  switchVal = true;
  groupList = []; // 组列表
  formLoading = false;
  groupNameMap = {
    unknown: window.mainComponent.$t('未分组'),
    private: window.mainComponent.$t('个人收藏'),
  }
  public rules = {
    name: [
      {
        required: true,
        trigger: 'blur',
      },
      {
        validator: this.checkSpecification,
        message: window.mainComponent.$t('收藏名不规范'),
        trigger: 'blur',
      },
      {
        validator: this.checkRepeatName,
        message: window.mainComponent.$t('收藏名重复'),
        trigger: 'blur',
      },
      {
        validator: this.checkCannotUseName,
        message: window.mainComponent.$t('保留名称，不可使用'),
        trigger: 'blur',
      },
    ],
  };

  public groupNameRules = {
    groupName: [
      {
        validator: this.checkName,
        message: window.mainComponent.$t('组名不规范, 只支持输入中文、英文、数字、特殊符号.'),
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

  get showGroupList() {
    return this.favoriteData.visible_type === 'public' ? this.publicGroupList : this.privateGroupList;
  }

  get favStrList() {
    return this.favoriteList.reduce((pre, cur) => { // 获取所有收藏的名字新增时判断是否重命名
      pre = pre.concat(cur.favorites.map(item => item.name));
      return pre;
    }, []);
  }

  @Emit('change')
  handleShowChange(value = false) {
    return value;
  }

  @Emit('submit')
  handleSubmitChange(isCreate: boolean, resValue?: object) {
    return {
      isCreate,
      resValue,
    };
  }

  checkName() {
    if (this.verifyData.groupName.trim() === '') return true;
    return /^[\u4e00-\u9fa5_a-zA-Z0-9`~!@#$%^&*()_\-+=<>?:"{}|\s,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]+$/im.test(this.verifyData.groupName.trim());
  }

  checkExistName() {
    return !this.groupList.some(item => item.name === this.verifyData.groupName);
  }

  /** 判断是否收藏名是否重复 */
  checkRepeatName() {
    if (!this.isCreateFavorite) return true;
    return !this.favStrList.includes(this.favoriteData.name);
  }
  /** 检查收藏语法是否正确 */
  checkSpecification() {
    return /^[\u4e00-\u9fa5_a-zA-Z0-9`~!@#$%^&*()_\-+=<>?:"{}|\s,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]+$/im.test(this.favoriteData.name.trim());
  }
  /** 检查是否有内置名称不能使用 */
  checkCannotUseName() {
    return ![this.$t('个人收藏'), this.$t('未分组')].includes(this.favoriteData.name.trim());
  }

  handleSelectGroup(nVal: number) {
    const visible_type = nVal === this.privateGroupID ? 'private' : 'public';
    this.isDisableSelect = nVal === this.privateGroupID;
    Object.assign(this.favoriteData, { visible_type });
  }

  async handleValueChange(value) {
    if (value) {
      await this.requestGroupList(); // 获取组列表
      if (this.isCreateFavorite) {
        // 判断是否是新增
        Object.assign(this.favoriteData, this.addFavoriteData); // 合并新增收藏详情
        this.favoriteData.params.search_fields = [];
      } else {
        await this.getFavoriteData(this.favoriteID); // 获取收藏详情
      }
      this.getSearchFieldsList(this.favoriteData.params.keyword); // 获取表单模式显示字段
      this.isDisableSelect = this.favoriteData.visible_type === 'private';
    } else {
      this.favoriteData = this.baseFavoriteData;
      this.searchFieldsList = [];
      this.handleShowChange();
    }
  }

  /** 新增组 */
  handleCreateGroup() {
    this.checkInputFormRef.validate().then(async () => {
      const data = { name: this.verifyData.groupName, space_uid: this.spaceUid };
      try {
        const res = await $http.request('favorite/createGroup', {
          data,
        });
        if (res.result) {
          this.$bkMessage({
            message: this.$t('操作成功'),
            theme: 'success',
          });
          this.requestGroupList(true, this.verifyData.groupName);
        }
      } catch (error) {} finally {
        this.isShowAddGroup = true;
        this.verifyData.groupName = '';
      }
    });
  }

  handleClickRadio(value: string) {
    if (value === 'private') {
      this.isDisableSelect = true;
      this.favoriteData.group_id = this.privateGroupID;
      this.favoriteData.visible_type = 'private';
    } else {
      this.isDisableSelect = false;
      this.favoriteData.group_id = this.unknownGroupID;
      this.favoriteData.visible_type = 'public';
    }
  }

  handleSubmitFormData() {
    this.validateFormRef.validate().then(
      () => {
        if (!this.unknownGroupID) return;
        if (!this.favoriteData.group_id) this.favoriteData.group_id = this.unknownGroupID;
        this.handleUpdateFavorite(this.favoriteData);
      },
    );
  }

  handleClickDisplayFields(value) {
    if (!value) { // 如果关闭 则更新当前显示的显示字段
      if (this.isCreateFavorite || this.isClickFavoriteEdit) {
        this.favoriteData.display_fields = this.visibleFields.map(item => item.field_name);
      }
    }
  }

  async getSearchFieldsList(keyword: string) {
    keyword === '' && (keyword = '*');
    try {
      const res = await $http.request('favorite/getSearchFields', {
        data: { keyword },
      });
      this.searchFieldsList = res.data.map(item => ({
        ...item,
        name: item.is_full_text_field ? `${this.$t('全文检索')}${!!item.repeat_count ? `(${item.repeat_count})` : ''}` : item.name,
        chName: item.name,
      }));
    } catch (error) {}
  }

  /** 更新收藏 */
  async handleUpdateFavorite(subData) {
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
      name,
      group_id,
      display_fields,
      visible_type,
      host_scopes,
      addition,
      keyword,
      search_fields,
      is_enable_display_fields,
    };
    if (this.isCreateFavorite) {
      Object.assign(data, {
        index_set_id,
        space_uid: this.spaceUid,
      });
    }
    const requestStr = this.isCreateFavorite ? 'createFavorite' : 'updateFavorite';
    try {
      const res = await $http.request(`favorite/${requestStr}`, {
        params: { id },
        data,
      });
      if (res.result) {
        this.handleSubmitChange(this.isCreateFavorite, res.data);
        this.handleShowChange();
      }
    } catch (error) {}
  }

  /** 获取组列表 */
  async requestGroupList(isAddGroup = false, groupName?) {
    try {
      const res = await $http.request('favorite/getGroupList', {
        query: {
          space_uid: this.spaceUid,
        },
      });
      this.groupList = res.data.map(item => ({
        ...item,
        name: this.groupNameMap[item.group_type] ?? item.name,
      }));
      this.publicGroupList = this.groupList.slice(1, this.groupList.length);
      this.privateGroupList = [this.groupList[0]];
      this.unknownGroupID = this.groupList[this.groupList.length - 1]?.id;
      this.privateGroupID = this.groupList[0]?.id;
    } catch (error) {} finally {
      if (isAddGroup) {
        this.favoriteData.group_id = this.groupList.find(item => item.name === groupName)?.id;
      }
    }
  }
  /** 获取收藏详情 */
  async getFavoriteData(id) {
    this.formLoading = true;
    try {
      const res = await $http.request('favorite/getFavorite', { params: { id } });
      const assignData = res.data;
      if (JSON.stringify(this.replaceData) !== '{}') { // 替换收藏 会把检索的params传过来
        Object.assign(assignData.params, this.replaceData.params);
      }
      Object.assign(this.favoriteData, assignData);
    } finally {
      this.formLoading = false;
    }
  }

  render() {
    return (
      <Dialog
        value={this.value}
        title={ this.isCreateFavorite ? this.$t('新增收藏') : this.$t('编辑收藏') }
        ok-text={ this.isCreateFavorite ? this.$t('确定') : this.$t('保存') }
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
            <span>{this.$t('索引集')}</span>
            <span>{this.favoriteData.index_set_name}</span>
          </div>
          <div class="edit-information">
            <span>{this.$t('查询语句')}</span>
            <span>{this.favoriteData.params.keyword}</span>
          </div>
          <div class="form-item-container">
            <FormItem label={this.$t('收藏名')} required property="name">
              <Input
                class="collect-name"
                vModel={this.favoriteData.name}
                placeholder={'填写收藏名（长度30个字符）'}
                maxlength={30}
              ></Input>
            </FormItem>
            <FormItem
              class="collect-radio"
              label={this.$t('可见范围')}
              required>
              <RadioGroup
                vModel={this.favoriteData.visible_type}
                on-change={this.handleClickRadio}>
                <Radio value={'public'}>{this.$t('公开')}({this.$t('本业务可见')})</Radio>
                <Radio value={'private'} disabled={this.isCannotChangeVisible}>{this.$t('私有')}({this.$t('仅个人可见')})</Radio>
              </RadioGroup>
            </FormItem>
          </div>
          <div class="form-item-container">
            <FormItem label={this.$t('所属组')}>
              <span v-bk-tooltips={{ content: this.$t('私有Tips'), disabled: !this.isDisableSelect }}>
                <Select
                  vModel={this.favoriteData.group_id}
                  disabled={this.isDisableSelect}
                  on-change={this.handleSelectGroup}
                  ext-popover-cls="add-new-page-container"
                  searchable
                >
                  {this.showGroupList.map(item => (
                    <Option id={item.id} key={item.id} name={item.name}></Option>
                  ))}
                  <div slot="extension">
                    {this.isShowAddGroup ? (
                      <div class="select-add-new-group" onClick={() => this.isShowAddGroup = false}>
                        <div><i class="bk-icon icon-plus-circle"></i> {this.$t('新增')}</div>
                      </div>
                    ) : (
                      <li class="add-new-page-input" style={{ padding: '6px 0' }}>
                        <Form
                          labelWidth={0}
                          style={{ width: '100%' }}
                          ref="checkInputForm"
                          {...{
                            props: {
                              model: this.verifyData,
                              rules: this.groupNameRules,
                            },
                          }}>
                          <FormItem property="groupName">
                            <Input
                              clearable
                              placeholder={this.$t('请输入组名')}
                              vModel={this.verifyData.groupName}
                              maxlength={10}
                            ></Input>
                          </FormItem>
                        </Form>
                        <div class="operate-button">
                          <span class="bk-icon icon-check-line" onClick={() => this.handleCreateGroup()}></span>
                          <span class="bk-icon icon-close-line-2" onClick={() => {
                            this.isShowAddGroup = true;
                            this.verifyData.groupName = '';
                          }}></span>
                        </div>
                      </li>
                    )}
                  </div>
                </Select>
              </span>
            </FormItem>
          </div>
          <FormItem label={this.$t('表单模式')}>
            <div class="explanation-field">
              {this.$t('表单模式显示字段文案')}
            </div>
            <CheckboxGroup vModel={this.favoriteData.params.search_fields}>
              {this.searchFieldsList.map(item => (
                <Checkbox value={item.chName}>{item.name}</Checkbox>
              ))}
            </CheckboxGroup>
          </FormItem>
          <FormItem
            label={this.$t('是否同时显示字段')}
            ext-cls="filed-label"
            desc-icon="bk-icon icon-info"
            desc-type="icon"
            desc={{
              content: `${this.$t('是否同时显示字段文案')}`,
              placements: ['right'],
            }}
          >
            <div class="filed-container">
              <Switcher
                vModel={this.favoriteData.is_enable_display_fields}
                theme="primary"
                on-change={value => this.handleClickDisplayFields(value)}
              ></Switcher>
              <span class="current-filed">{this.$t('当前字段')}：</span>
              {this.favoriteData.display_fields.map(item => (
                <Tag>{item}</Tag>
              ))}
            </div>
          </FormItem>
        </Form>
      </Dialog>
    );
  }
}
