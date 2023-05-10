<!--
  - Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for BK-LOG 蓝鲸日志平台:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div class="fields-setting" v-bkloading="{ isLoading: isLoading }">
    <!-- 设置列表字段 -->
    <div class="fields-container">
      <div class="fields-config-container">
        <div v-show="!isShowAddInput" class="add-fields-config" @click="handleClickAddNew">
          <bk-button class="config-btn" :text="true">
            <i class="bk-icon icon-plus-circle-yuan"></i>
            <span>{{$t('新建配置')}}</span>
          </bk-button>
        </div>
        <div v-show="isShowAddInput" class="config-tab-item">
          <bk-input
            :class="['config-input', { 'input-error': isInputError }]"
            v-model="newConfigStr">
          </bk-input>
          <div class="panel-operate">
            <i class="bk-icon icon-check-line" @click="handleAddNewConfig"></i>
            <i class="bk-icon icon-close-line-2" @click="handleCancelNewConfig"></i>
          </div>
        </div>
        <bk-tab
          type="unborder-card"
          ext-cls="config-tab"
          ref="configTabRef"
          :active.sync="activeConfigTab"
          :tab-position="'left'">
          <template v-for="(panel, index) in configTabPanels">
            <bk-tab-panel
              :key="panel.name"
              :name="panel.name"
              :render-label="e => renderHeader(e, panel, index)">
            </bk-tab-panel>
          </template>
        </bk-tab>
      </div>
      <div>
        <div class="fields-tab-container">
          <bk-tab type="unborder-card" :active.sync="activeFieldTab">
            <template v-for="(panel, index) in fieldTabPanels">
              <bk-tab-panel :key="index" v-bind="panel"></bk-tab-panel>
            </template>
          </bk-tab>
        </div>
        <div class="fields-list-container">
          <div class="total-fields-list">
            <div class="title">
              <!-- 待选项列表 全部添加 -->
              <span>{{ $t('待选项列表') + '(' + toSelectLength + ')' }}</span>
              <span class="text-action add-all" @click="addAllField">{{ $t('全部添加') }}</span>
            </div>
            <ul class="select-list">
              <li
                class="select-item"
                style="cursor: pointer;"
                v-for="item in shadowTotal"
                :key="item.field_name"
                v-show="activeFieldTab === 'visible' ? !item.is_display : (!item.isSorted && item.es_doc_values)"
                @click="addField(item)">
                <span class="field-name" v-bk-overflow-tips>{{ getFiledDisplay(item.field_name) }}</span>
                <span class="icon log-icon icon-filled-right-arrow"></span>
              </li>
            </ul>
          </div>
          <!-- 中间的箭头 -->
          <div class="sort-icon">
            <span class="icon log-icon icon-double-arrow"></span>
          </div>
          <!-- 设置显示字段 -->
          <div class="visible-fields-list" v-show="activeFieldTab === 'visible'">
            <div class="title">
              <!-- 已选项列表 -->
              <span>{{ $t('已选项列表') + '(' + shadowVisible.length + ')' }}</span>
              <span class="icon log-icon icon-info-fill" v-bk-tooltips="$t('支持拖拽更改顺序，从上向下对应列表列从左到右顺序')"></span>
              <span class="clear-all text-action" @click="deleteAllField">{{ $t('取消') }}</span>
            </div>
            <vue-draggable class="select-list" v-bind="dragOptions" v-model="shadowVisible">
              <transition-group>
                <li class="select-item" v-for="(item, index) in shadowVisible" :key="item">
                  <span class="icon log-icon icon-drag-dots"></span>
                  <span class="field-name" v-bk-overflow-tips>{{ getFiledDisplay(item) }}</span>
                  <span class="delete text-action" @click="deleteField(item, index)">{{ $t('删除') }}</span>
                </li>
              </transition-group>
            </vue-draggable>
          </div>
          <!-- 设置权重排序 -->
          <div class="sort-fields-list" v-show="activeFieldTab === 'sort'">
            <div class="title">
              <!-- 已选项列表 -->
              <span>{{ $t('已选项列表') + '(' + shadowSort.length + ')' }}</span>
              <span class="icon log-icon icon-info-fill" v-bk-tooltips="$t('支持拖拽更改顺序，排在上面的拥有更高的排序权重')"></span>
              <span class="clear-all text-action" @click="deleteAllField">{{ $t('取消') }}</span>
            </div>
            <div class="sort-list-header">
              <span :style="`width: calc(100% - ${fieldWidth}px); padding-left: 32px;`">{{ $t('字段名') }}</span>
              <span style="min-width: 42px;">{{ $t('状态') }}</span>
              <span style="min-width: 50px;">{{ $t('选择方式') }}</span>
            </div>
            <vue-draggable class="select-list" v-bind="dragOptions" v-model="shadowSort">
              <transition-group>
                <li class="select-item" v-for="(item, index) in shadowSort" :key="item[0]">
                  <span class="icon log-icon icon-drag-dots"></span>
                  <span class="field-name"
                        :style="`width: calc(100% - ${fieldWidth}px);`"
                        v-bk-overflow-tips>{{ getFiledDisplay(item[0]) }}</span>
                  <span class="status">{{ filterStatus(item[1]) }}</span>
                  <span class="option text-action" @click="setOrder(item)">{{ filterOption(item[1]) }}</span>
                  <span class="delete text-action" @click="deleteField(item[0], index)">{{ $t('删除') }}</span>
                </li>
              </transition-group>
            </vue-draggable>
          </div>
        </div>
      </div>
    </div>
    <div class="fields-button-container">
      <bk-button :theme="'primary'" type="submit" class="mr10" @click="confirmModifyFields">
        {{ $t('应用') }}
      </bk-button>
      <bk-button :theme="'default'" type="submit" @click="cancelModifyFields">
        {{ $t('取消') }}
      </bk-button>
    </div>
    <div class="field-alias-setting">
      <span style="margin-right: 4px;">{{ $t('表头显示别名') }}</span>
      <bk-switcher v-model="showFieldAlias" theme="primary" size="small"></bk-switcher>
    </div>
  </div>
</template>

<script>
import VueDraggable from 'vuedraggable';
import fieldsSettingOperate from './fields-setting-operate';
import { deepClone } from '@/components/monitor-echarts/utils';

export default {
  components: {
    VueDraggable,
  },
  props: {
    fieldAliasMap: {
      type: Object,
      default() {
        return {};
      },
    },
    retrieveParams: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      showFieldAlias: localStorage.getItem('showFieldAlias') === 'true',
      shadowTotal: [],
      shadowVisible: [],
      shadowSort: [],
      shadowAllTotal: [], // 所有字段
      newConfigStr: '', // 新增配置配置名
      isShowAddInput: false, // 是否展示新增配置输入框
      currentClickConfigID: 0, // 当前配置项ID
      activeFieldTab: 'visible',
      activeConfigTab: 'default', // 当前活跃的配置配置名
      isConfirmSubmit: false, // 是否点击保存
      isInputError: false, // 新建配置名称是否不合法
      fieldTabPanels: [
        { name: 'visible', label: this.$t('设置显示字段') },
        { name: 'sort', label: this.$t('设置排序权重') },
      ],
      configTabPanels: [], // 配置列表
      dragOptions: {
        animation: 150,
        tag: 'ul',
        handle: '.icon-drag-dots',
        'ghost-class': 'sortable-ghost-class',
      },
    };
  },
  computed: {
    toSelectLength() {
      if (this.activeFieldTab === 'visible') {
        return this.shadowTotal.length - this.shadowVisible.length;
      }
      let totalLength = 0;
      this.shadowTotal.forEach((fieldInfo) => {
        if (fieldInfo.es_doc_values) {
          totalLength += 1;
        }
      });
      return totalLength - this.shadowSort.length;
    },
    filedSettingConfigID() { // 当前索引集的显示字段ID
      return this.$store.state.retrieve.filedSettingConfigID;
    },
    currentClickConfigData() { // 当前选中的配置
      return this.configTabPanels.find(item => item.id === this.currentClickConfigID) || this.configTabPanels[0];
    },
    fieldWidth() {
      return this.$store.state.isEnLanguage ? '170' : '146';
    },
  },
  watch: {
    newConfigStr() {
      this.isInputError = false;
    },
  },
  created() {
    this.requestFields();
  },
  methods: {
    /** 请求字段 */
    async requestFields() {
      this.isLoading = true;
      try {
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: { index_set_id: this.$route.params.indexId },
          query: {
            start_time: this.retrieveParams.start_time,
            end_time: this.retrieveParams.end_time,
            is_realtime: 'True',
          },
        });
        this.shadowAllTotal = res.data.fields.map(item => ({ ...item, is_display: false }));
      } catch (e) {
        console.warn(e);
      } finally {
        this.currentClickConfigID = this.filedSettingConfigID;
        this.initRequestConfigListShow();
      }
    },
    getFiledDisplay(name) {
      const alias = this.fieldAliasMap[name];
      if (alias && alias !== name) {
        return `${name}(${alias})`;
      }
      return name;
    },
    /** 带config列表请求的初始化 */
    async initRequestConfigListShow() {
      await this.getFiledConfigList();
      this.initShadowFields();
    },
    /** 保存或应用 */
    async confirmModifyFields() {
      if (this.shadowVisible.length === 0) {
        this.messageWarn(this.$t('显示字段不能为空'));
        return;
      }
      try {
        const confirmConfigData = {
          editStr: this.currentClickConfigData.name,
          sort_list: this.shadowSort,
          display_fields: this.shadowVisible,
          id: this.currentClickConfigData.id,
        };
        this.isConfirmSubmit = true;
        await this.handleUpdateConfig(confirmConfigData);
        // 判断当前应用的config_id 与 索引集使用的config_id是否相同 不同则更新config
        if (this.currentClickConfigID !== this.filedSettingConfigID) {
          await this.submitFieldsSet(this.currentClickConfigID);
        }
        this.$store.commit('updateClearTableWidth', 1);
        // 判断当前页, 如果是排序时 不更新字段
        const isRequestFields = this.activeFieldTab !== 'sort';
        this.$emit('confirm', this.shadowVisible, this.showFieldAlias, isRequestFields);
      } catch (error) {
        console.warn(error);
      } finally {
        this.isConfirmSubmit = false;
      }
    },
    /** 更新config */
    async submitFieldsSet(configID) {
      await this.$http.request('retrieve/postFieldsConfig', {
        params: { index_set_id: this.$route.params.indexId },
        data: { display_fields: this.shadowVisible, sort_list: this.shadowSort, config_id: configID },
      }).catch((e) => {
        console.warn(e);
      });
    },
    cancelModifyFields() {
      this.$emit('cancel');
    },
    filterStatus(val) {
      if (val === 'desc') {
        return this.$t('降序');
      } if (val === 'asc') {
        return this.$t('升序');
      }
      return '';
    },
    filterOption(val) {
      if (val === 'desc') {
        return this.$t('设为升序');
      } if (val === 'asc') {
        return this.$t('设为降序');
      }
      return '';
    },
    addField(fieldInfo) {
      if (this.activeFieldTab === 'visible') {
        fieldInfo.is_display = true;
        this.shadowVisible.push(fieldInfo.field_name);
      } else {
        fieldInfo.isSorted = true;
        this.shadowSort.push([fieldInfo.field_name, 'asc']);
      }
    },
    deleteField(fieldName, index) {
      const arr = this.shadowTotal;
      if (this.activeFieldTab === 'visible') {
        this.shadowVisible.splice(index, 1);
        for (let i = 0; i < arr.length; i++) {
          if (arr[i].field_name === fieldName) {
            arr[i].is_display = false;
            return;
          }
        }
      } else {
        this.shadowSort.splice(index, 1);
        for (let i = 0; i < arr.length; i++) {
          if (arr[i].field_name === fieldName) {
            arr[i].isSorted = false;
            return;
          }
        }
      }
    },
    addAllField() {
      if (this.activeFieldTab === 'visible') {
        this.shadowTotal.forEach((fieldInfo) => {
          if (!fieldInfo.is_display) {
            fieldInfo.is_display = true;
            this.shadowVisible.push(fieldInfo.field_name);
          }
        });
      } else {
        this.shadowTotal.forEach((fieldInfo) => {
          if (!fieldInfo.isSorted && fieldInfo.es_doc_values) {
            fieldInfo.isSorted = true;
            this.shadowSort.push([fieldInfo.field_name, 'asc']);
          }
        });
      }
    },
    deleteAllField() {
      if (this.activeFieldTab === 'visible') {
        this.shadowTotal.forEach((fieldInfo) => {
          fieldInfo.is_display = false;
          this.shadowVisible.splice(0, this.shadowVisible.length);
        });
      } else {
        this.shadowTotal.forEach((fieldInfo) => {
          fieldInfo.isSorted = false;
          this.shadowSort.splice(0, this.shadowSort.length);
        });
      }
    },
    setOrder(item) {
      item[1] = item[1] === 'asc' ? 'desc' : 'asc';
      this.$forceUpdate();
    },
    renderHeader(h, row, index) {
      row.index = index;
      return h(fieldsSettingOperate, {
        props: {
          configItem: row,
        },
        on: {
          operateChange: this.handleLeftOperateChange,
          setPopperInstance: this.setPopperInstance,
        },
      });
    },
    /** 用户操作 */
    handleLeftOperateChange(type, configItem) {
      switch (type) {
        case 'click':
          this.currentClickConfigID = configItem.id;
          this.initShadowFields();
          break;
        case 'delete':
          this.handleDeleteConfig(configItem.id);
          break;
        case 'edit':
          this.handleEditConfigName(configItem.index);
          break;
        case 'update':
          this.handleUpdateConfig(configItem);
          break;
        case 'cancel':
          this.handleCancelEditConfig(configItem.index);
          break;
      }
    },
    /** 编辑配置 */
    handleEditConfigName(index) {
      this.configTabPanels.forEach(item => item.isShowEdit = false);
      this.configTabPanels[index].isShowEdit = true;
      this.isShowAddInput = false;
    },
    /** 点击新增配置 */
    handleClickAddNew() {
      this.configTabPanels.forEach(item => item.isShowEdit = false);
      this.isShowAddInput = true;
    },
    /** 新增配置 */
    handleAddNewConfig() {
      if (!this.newConfigStr) {
        this.isInputError = true;
        return;
      };
      const configValue = this.configTabPanels[0];
      configValue.editStr = this.newConfigStr;
      this.handleUpdateConfig(configValue, true);
    },
    /** 取消新增配置 */
    handleCancelNewConfig() {
      this.newConfigStr = '';
      this.isShowAddInput = false;
      this.isInputError = false;
    },
    /** 取消编辑配置 */
    handleCancelEditConfig(index) {
      this.configTabPanels[index].editStr = this.configTabPanels[index].name;
      this.configTabPanels[index].isShowEdit = false;
    },
    /** 更新配置 */
    async handleUpdateConfig(updateItem, isCreate = false) {
      const requestStr = isCreate ? 'create' : 'update';
      const data = {
        name: updateItem.editStr,
        sort_list: updateItem.sort_list,
        display_fields: updateItem.display_fields,
        config_id: undefined,
      };
      if (!isCreate) data.config_id = updateItem.id;
      try {
        await this.$http.request(`retrieve/${requestStr}FieldsConfig`, {
          params: { index_set_id: this.$route.params.indexId },
          data,
        });
        if (this.activeFieldTab === 'sort') {
          this.$emit('shouldRetrieve', undefined, false); // 不请求图表
        }
      } catch (error) {} finally {
        if (!this.isConfirmSubmit) this.initRequestConfigListShow();
        this.newConfigStr = '';
        this.isShowAddInput = false;
      }
    },
    /** 删除配置 */
    async handleDeleteConfig(configID) {
      try {
        await this.$http.request('retrieve/deleteFieldsConfig', {
          params: { index_set_id: this.$route.params.indexId },
          data: { config_id: configID },
        });
      } catch (error) {} finally {
        this.initRequestConfigListShow();
        this.newConfigStr = '';
        if (this.filedSettingConfigID === configID) {
          this.currentClickConfigID = this.configTabPanels[0].id;
          // 若删除的元素id与使用当前使用的config_id相同则直接刷新显示字段
          this.$store.commit('updateClearTableWidth', 1);
          const { display_fields } = this.configTabPanels[0];
          this.$emit('modifyFields', display_fields, this.showFieldAlias);
        }
      }
    },
    /** 初始化显示字段 */
    initShadowFields() {
      this.activeConfigTab = this.currentClickConfigData.name;
      this.shadowTotal = deepClone(this.shadowAllTotal);
      this.shadowSort = deepClone(this.currentClickConfigData.sort_list);
      this.shadowTotal.forEach((fieldInfo) => {
        this.shadowSort.forEach((item) => {
          if (fieldInfo.field_name === item[0]) {
            fieldInfo.isSorted = true;
          }
        });
      });
      // 后台给的 display_fields 可能有无效字段 所以进行过滤，获得排序后的字段
      this.shadowVisible = this.currentClickConfigData.display_fields.map((displayName) => {
        for (const field of this.shadowTotal) {
          if (field.field_name === displayName) {
            field.is_display = true;
            return displayName;
          }
        }
      }).filter(Boolean);
    },
    /** 获取配置列表 */
    async getFiledConfigList() {
      this.isLoading = true;
      try {
        const res = await this.$http.request('retrieve/getFieldsListConfig', {
          params: { index_set_id: this.$route.params.indexId },
        });
        this.configTabPanels = res.data.map(item => ({
          ...item,
          isShowEdit: false,
          editStr: item.name,
        }));
      } catch (error) {} finally {
        this.isLoading = false;
      }
    },
    setPopperInstance(status) {
      this.$emit('setPopperInstance', status);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .fields-setting {
    position: relative;

    .fields-container {
      display: flex;

      .fields-config-container {
        .add-fields-config {
          height: 40px;
          border-right: 1px solid #dcdee5;
          color: #3a84ff;
          cursor: pointer;

          .config-btn {
            width: 100%;
            height: 100%;
            line-height: 100%;
            padding-left: 24px;
            text-align: left;

            .bk-icon {
              transform: translateY(-2px);
            }
          }
        }

        .config-tab {
          width: 100%;
          height: calc(100% - 40px);
          overflow-y: auto;
        }

        .config-tab-item {
          width: 100%;
          height: 40px;
          padding: 0 12px 0 4px;
          display: flex;
          align-items: center;
          justify-content: space-between;

          .config-input {
            width: 100px;
          }

          .input-error {
            :deep(.bk-form-input) {
              border: 1px solid #d7473f;
            }
          }

          .panel-name {
            max-width: 100px;
            padding-left: 20px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
          }

          .panel-operate, {
            color: #979ba5;
            margin-left: 10px;
            font-size: 14px;
            cursor: pointer;

            .edit-icon:hover {
              color: #3a84ff;
            }

            .icon-check-line {
              color: #3a84ff;
            }

            .icon-close-line-2 {
              color: #d7473f;
            }
          }
        }

        :deep(.bk-tab-label) {
          width: 100%;
        }

        :deep(.bk-tab-label-item) {
          text-align: left;

          /* stylelint-disable-next-line declaration-no-important */
          line-height: 40px !important;
          padding: 0;
          color: #63656e;

          &:hover {
            background: #f0f1f5;
          }
        }

        :deep(.bk-tab-header) {
          padding: 0 0 10px;
          min-width: 160px;
          width: 100%;
          // &::after {
          //   display: none;
          // }
          &::before {
            display: none;
          }
        }

        :deep(.active) {
          color: #3a84ff;

          /* stylelint-disable-next-line declaration-no-important */
          background: #e1ecff !important;
        }

        :deep(.bk-tab-section) {
          display: none;
        }
      }
    }

    .fields-tab-container {
      width: 723px;
      padding: 10px 24px 0;
    }

    .fields-list-container {
      display: flex;
      width: 723px;
      padding: 0 24px 14px;
      margin-top: -20px;

      .total-fields-list,
      .visible-fields-list,
      .sort-fields-list {
        width: 320px;
        height: 319px;
        border: 1px solid #dcdee5;

        .text-action {
          font-size: 12px;
          color: #3a84ff;
          cursor: pointer;
        }

        .title {
          position: relative;
          display: flex;
          align-items: center;
          height: 41px;
          line-height: 40px;
          padding: 0 16px;
          border-bottom: 1px solid #dcdee5;
          color: #313238;

          .icon-info-fill {
            margin-left: 8px;
            font-size: 14px;
            color: #979ba5;
            outline: none;
          }

          .add-all,
          .clear-all {
            position: absolute;
            top: 0;
            right: 16px;
          }
        }

        .select-list {
          height: 276px;
          padding: 10px 0;
          overflow: auto;

          @include scroller;

          .select-item {
            display: flex;
            align-items: center;
            padding: 0 16px;
            line-height: 32px;
            font-size: 12px;

            .icon-drag-dots {
              width: 16px;
              text-align: left;
              font-size: 14px;
              color: #979ba5;
              cursor: move;
              opacity: 0;
              transition: opacity .2s linear;
            }

            &.sortable-ghost-class {
              background: #eaf3ff;
              transition: background .2s linear;
            }

            &:hover {
              background: #eaf3ff;
              transition: background .2s linear;

              .icon-drag-dots {
                opacity: 1;
                transition: opacity .2s linear;
              }
            }
          }
        }
      }

      .total-fields-list .select-list .select-item {
        .field-name {
          width: calc(100% - 24px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .icon-filled-right-arrow {
          width: 24px;
          text-align: right;
          font-size: 16px;
          transform: scale(.5);
          transform-origin: right center;
          color: #3a84ff;
          cursor: pointer;
          opacity: 0;
          transition: opacity .2s linear;
        }

        &:hover .icon-filled-right-arrow {
          opacity: 1;
          transition: opacity .2s linear;
        }
      }

      .visible-fields-list .select-list .select-item {
        .field-name {
          // 16 38
          width: calc(100% - 54px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .delete {
          width: 38px;
          text-align: right;
        }
      }

      .sort-fields-list {
        flex-shrink: 0;

        .sort-list-header {
          display: flex;
          align-items: center;
          height: 31px;
          line-height: 30px;
          font-size: 12px;
          background: rgba(250, 251, 253, 1);
          border-bottom: 1px solid rgba(221, 228, 235, 1);
        }

        .select-list .select-item {
          .field-name {
            // 16 42 50 38
            width: calc(100% - 146px);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .status {
            width: 42px;
          }

          .option {
            width: 50px;
          }

          .delete {
            width: 38px;
            text-align: right;
          }
        }
      }

      .sort-icon {
        flex-shrink: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 35px;

        .icon-double-arrow {
          font-size: 12px;
          color: #989ca5;
        }
      }
    }

    .fields-button-container {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      width: 100%;
      height: 51px;
      padding: 0 24px;
      background-color: #fafbfd;
      border-top: 1px solid #dcdee5;
      border-radius: 0 0 2px 2px;
    }

    .field-alias-setting {
      position: absolute;
      top: 10px;
      right: 20px;
      display: flex;
      align-items: center;
      height: 42px;
    }
  }
</style>
