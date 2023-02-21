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
  <div :id="id" class="fields-config-tippy" v-bkloading="{ isLoading }">
    <!-- 字段显示设置 -->
    <div class="config-title">{{$t('设置显示与排序')}}</div>
    <div class="field-list-container">
      <!-- 已选字段 -->
      <div class="field-list">
        <div class="list-title">
          <i18n path="显示字段（已选 {0} / {1})">
            <span>{{displayFieldNames.length}}</span>
            <span>{{limitCount}}</span>
          </i18n>
        </div>
        <vue-draggable v-bind="dragOptions" v-model="displayFieldNames">
          <transition-group>
            <li class="list-item display-item" v-for="(field, index) in displayFieldNames" :key="field">
              <span class="icon log-icon icon-drag-dots"></span>
              <div class="field_name">{{ field }}</div>
              <div
                :class="['operate-button', disabledRemove && 'disabled']"
                @click="removeItem(index)">{{$t('删除')}}
              </div>
            </li>
          </transition-group>
        </vue-draggable>
      </div>
      <!-- 其他字段 -->
      <div class="field-list">
        <div class="list-title">{{$t('其他字段')}}</div>
        <ul>
          <li class="list-item rest-item" v-for="field in restFieldNames" :key="field">
            <div class="field_name">{{ field }}</div>
            <div :class="['operate-button', disabledAdd && 'disabled']" @click="addItem(field)">{{$t('添加')}}</div>
          </li>
        </ul>
      </div>
    </div>
    <div class="config-buttons">
      <!-- 确定、取消按钮 -->
      <bk-button
        size="small"
        style="margin-right: 8px;"
        theme="primary"
        @click="handleConfirm">{{$t('确定')}}</bk-button>
      <bk-button size="small" style="margin-right: 24px;" @click="handleCancel">{{$t('取消')}}</bk-button>
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
    id: {
      type: String,
      required: true,
    },
    isLoading: {
      type: Boolean,
      required: true,
    },
    total: {
      type: Array,
      required: true,
    },
    display: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      limitCount: 5, // 最多显示多少字段
      totalFieldNames: [], // 所有的字段名
      displayFieldNames: [], // 展示的字段名

      dragOptions: {
        animation: 150,
        tag: 'ul',
        handle: '.icon-drag-dots',
        'ghost-class': 'sortable-ghost-class',
      },
    };
  },
  computed: {
    restFieldNames() {
      return this.totalFieldNames.filter(field => !this.displayFieldNames.includes(field));
    },
    // 最少显示一个字段
    disabledRemove() {
      return this.displayFieldNames.length <= 1;
    },
    // 超过最大显示量禁止添加字段
    disabledAdd() {
      return this.displayFieldNames.length >= this.limitCount;
    },
  },
  watch: {
    total() {
      this.totalFieldNames = [...this.total];
      this.displayFieldNames = [...this.display];
    },
  },
  methods: {
    /**
     * 移除某个显示字段
     * @param {Number} index
     */
    removeItem(index) {
      !this.disabledRemove && this.displayFieldNames.splice(index, 1);
    },
    /**
     * 增加某个字段名
     * @param {String} fieldName
     */
    addItem(fieldName) {
      !this.disabledAdd && this.displayFieldNames.push(fieldName);
    },
    handleConfirm() {
      this.$emit('confirm', this.displayFieldNames);
    },
    handleCancel() {
      this.$emit('cancel');
    },
  },
};
</script>

<style lang="scss">
  .fields-config-tippy > .tippy-tooltip {
    padding: 0;
    border: 1px solid #dcdee5;

    .fields-config-tippy {
      .config-title {
        padding: 20px 24px 0;
        color: #313238;
        font-size: 20px;
        line-height: 28px;
        font-weight: normal;
      }

      .field-list-container {
        max-height: 400px;
        padding: 10px 24px;
        overflow: auto;
        color: #63656e;

        .field-list {
          .list-title,
          .list-item,
          .operate-button {
            line-height: 32px;
          }

          .list-item {
            position: relative;
            display: flex;
            align-items: center;
            padding-left: 12px;
            margin-bottom: 2px;
            background-color: #f5f6fa;

            &.display-item {
              .icon-drag-dots {
                width: 16px;
                text-align: left;
                font-size: 14px;
                color: #979ba5;
                cursor: move;
                transition: opacity .2s linear;
              }
            }

            .operate-button {
              position: absolute;
              top: 0;
              right: 0;
              width: 40px;
              text-align: center;
              cursor: pointer;

              &:hover {
                color: #3a84ff;
              }

              &.disabled {
                color: #dcdee5;
                cursor: not-allowed;
              }
            }
          }
        }
      }

      .config-buttons {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 50px;
        background: #fafbfd;
        border-top: 1px solid #dcdee5;
      }
    }
  }
</style>
