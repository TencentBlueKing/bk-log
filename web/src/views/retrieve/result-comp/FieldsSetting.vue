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
          <span>{{ $t('retrieve.toSelectedList') + '(' + toSelectLength + ')' }}</span>
          <span class="text-action add-all" @click="addAllField">{{ $t('retrieve.addAllFields') }}</span>
        </div>
        <ul class="select-list">
          <li
            class="select-item"
            v-for="item in shadowTotal"
            :key="item.field_name"
            v-show="activeFieldTab === 'visible' ? !item.is_display : (!item.isSorted && item.es_doc_values)">
            <span class="field-name" v-bk-overflow-tips>{{ getFiledDisplay(item.field_name) }}</span>
            <span class="icon log-icon icon-filled-right-arrow" @click="addField(item)"></span>
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
          <span>{{ $t('retrieve.selectedList') + '(' + shadowVisible.length + ')' }}</span>
          <span class="icon log-icon icon-info-fill" v-bk-tooltips="$t('retrieve.visibleTips')"></span>
          <span class="clear-all text-action" @click="deleteAllField">{{ $t('retrieve.clear') }}</span>
        </div>
        <vue-draggable class="select-list" v-bind="dragOptions" v-model="shadowVisible">
          <transition-group>
            <li class="select-item" v-for="(item, index) in shadowVisible" :key="item">
              <span class="icon log-icon icon-drag-dots"></span>
              <span class="field-name" v-bk-overflow-tips>{{ getFiledDisplay(item) }}</span>
              <span class="delete text-action" @click="deleteField(item, index)">{{ $t('btn.delete') }}</span>
            </li>
          </transition-group>
        </vue-draggable>
      </div>
      <!-- 设置权重排序 -->
      <div class="sort-fields-list" v-show="activeFieldTab === 'sort'">
        <div class="title">
          <!-- 已选项列表 -->
          <span>{{ $t('retrieve.selectedList') + '(' + shadowSort.length + ')' }}</span>
          <span class="icon log-icon icon-info-fill" v-bk-tooltips="$t('retrieve.sortTips')"></span>
          <span class="clear-all text-action" @click="deleteAllField">{{ $t('retrieve.clear') }}</span>
        </div>
        <div class="sort-list-header">
          <span style="width: calc(100% - 146px);padding-left: 32px;">{{ $t('retrieve.fieldName') }}</span>
          <span style="width: 42px;">{{ $t('retrieve.status') }}</span>
          <span style="width: 50px;">{{ $t('retrieve.option') }}</span>
        </div>
        <vue-draggable class="select-list" v-bind="dragOptions" v-model="shadowSort">
          <transition-group>
            <li class="select-item" v-for="(item, index) in shadowSort" :key="item[0]">
              <span class="icon log-icon icon-drag-dots"></span>
              <span class="field-name" v-bk-overflow-tips>{{ getFiledDisplay(item[0]) }}</span>
              <span class="status">{{ filterStatus(item[1]) }}</span>
              <span class="option text-action" @click="setOrder(item)">{{ filterOption(item[1]) }}</span>
              <span class="delete text-action" @click="deleteField(item[0], index)">{{ $t('btn.delete') }}</span>
            </li>
          </transition-group>
        </vue-draggable>
      </div>
    </div>
    <div class="fields-button-container">
      <bk-button :theme="'primary'" type="submit" class="mr10" @click="confirmModifyFields">
        {{ $t('btn.save') }}
      </bk-button>
      <bk-button :theme="'default'" type="submit" @click="cancelModifyFields">
        {{ $t('btn.cancel') }}
      </bk-button>
    </div>
    <div class="field-alias-setting">
      <span style="margin-right: 4px;">{{ $t('显示别名') }}</span>
      <bk-switcher v-model="showFieldAlias" theme="primary" size="small"></bk-switcher>
    </div>
  </div>
</template>

<script>
import VueDraggable from 'vuedraggable';

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
      isLoading: true,
      showFieldAlias: localStorage.getItem('showFieldAlias') === 'true',
      shadowTotal: [],
      shadowVisible: [],
      shadowSort: [],
      activeFieldTab: 'visible',
      fieldTabPanels: [
        { name: 'visible', label: this.$t('retrieve.setVisible') },
        { name: 'sort', label: this.$t('retrieve.setSort') },
      ],
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
  },
  created() {
    this.requestFields();
  },
  methods: {
    async requestFields() {
      try {
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: { index_set_id: this.$route.params.indexId },
          query: {
            start_time: this.retrieveParams.start_time,
            end_time: this.retrieveParams.end_time,
            is_realtime: 'True',
          },
        });
        this.shadowSort = res.data.sort_list;
        this.shadowTotal = res.data.fields;
        this.shadowTotal.forEach((fieldInfo) => {
          this.shadowSort.forEach((item) => {
            if (fieldInfo.field_name === item[0]) {
              fieldInfo.isSorted = true;
            }
          });
        });
        // 后台给的 display_fields 可能有无效字段 所以进行过滤，获得排序后的字段
        this.shadowVisible = res.data.display_fields.map((displayName) => {
          for (const field of res.data.fields) {
            if (field.field_name === displayName) {
              return displayName;
            }
          }
        }).filter(Boolean);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    getFiledDisplay(name) {
      const alias = this.fieldAliasMap[name];
      if (alias && alias !== name) {
        return `${name}(${alias})`;
      }
      return name;
    },
    async confirmModifyFields() {
      if (this.shadowVisible.length === 0) {
        this.messageWarn(this.$t('retrieve.mustSetVisible'));
        return;
      }
      this.$store.commit('updateClearTableWidth', 1);
      this.$emit('confirm', this.shadowVisible, this.showFieldAlias);
      this.$http.request('retrieve/postFieldsConfig', {
        params: { index_set_id: this.$route.params.indexId },
        data: { display_fields: this.shadowVisible, sort_list: this.shadowSort },
      }).catch((e) => {
        console.warn(e);
      });
    },
    cancelModifyFields() {
      this.$emit('cancel');
    },
    filterStatus(val) {
      if (val === 'desc') {
        return this.$t('retrieve.desc');
      } if (val === 'asc') {
        return this.$t('retrieve.asc');
      }
      return '';
    },
    filterOption(val) {
      if (val === 'desc') {
        return this.$t('retrieve.setAsc');
      } if (val === 'asc') {
        return this.$t('retrieve.setDesc');
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
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .fields-setting {
    position: relative;

    .fields-tab-container {
      width: 723px;
      padding: 10px 24px 0;
    }

    .fields-list-container {
      display: flex;
      width: 723px;
      padding: 0 24px 30px;
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
        width: 360px;

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
      width: 723px;
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
