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
  <div class="original-log-panel">
    <div class="original-log-panel-tools">
      <div class="bk-button-group">
        <bk-button
          :class="!showOriginalLog ? 'is-selected' : ''"
          @click="contentType = 'table'"
          size="small">
          {{ $t('表格') }}
        </bk-button>
        <bk-button
          :class="showOriginalLog ? 'is-selected' : ''"
          @click="contentType = 'original'"
          size="small">
          {{ $t('原始') }}
        </bk-button>
      </div>
      <div class="tools-more">
        <div :style="`margin-right: ${showOriginalLog ? 0 : 26}px`">
          <span class="switch-label">{{ $t('换行') }}</span>
          <bk-switcher v-model="isWrap" theme="primary"></bk-switcher>
        </div>
        <time-formatter v-show="!showOriginalLog" />
        <div class="operation-icons">
          <export-log
            v-bind="$attrs"
            :retrieve-params="retrieveParams"
            :total-count="totalCount"
            :queue-status="queueStatus"
            :async-export-usable="asyncExportUsable"
            :async-export-usable-reason="asyncExportUsableReason">
          </export-log>
          <bk-popover
            v-if="!showOriginalLog"
            ref="fieldsSettingPopper"
            trigger="click"
            placement="bottom-end"
            theme="light bk-select-dropdown"
            animation="slide-toggle"
            :offset="0"
            :distance="15"
            :on-show="handleDropdownShow"
            :on-hide="handleDropdownHide">
            <slot name="trigger">
              <div class="operation-icon">
                <span class="icon log-icon icon-set-icon"></span>
              </div>
            </slot>
            <div slot="content" class="fields-setting-container">
              <fields-setting
                v-if="showFieldsSetting"
                v-on="$listeners"
                :field-alias-map="$attrs['field-alias-map']"
                :retrieve-params="retrieveParams"
                @setPopperInstance="setPopperInstance"
                @modifyFields="modifyFields"
                @confirm="confirmModifyFields"
                @cancel="closeDropdown" />
            </div>
          </bk-popover>
        </div>
      </div>
    </div>

    <table-log
      v-bind="$attrs"
      v-on="$listeners"
      :is-wrap="isWrap"
      :show-original="showOriginalLog"
      :retrieve-params="retrieveParams" />
  </div>
</template>

<script>
import TimeFormatter from '@/components/common/time-formatter';
import TableLog from './table-log.vue';
import FieldsSetting from '../../result-comp/fields-setting';
import ExportLog from '../../result-comp/export-log.vue';

export default {
  components: {
    TimeFormatter,
    TableLog,
    FieldsSetting,
    ExportLog,
  },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    totalCount: {
      type: Number,
      default: 0,
    },
    queueStatus: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      contentType: 'table',
      isWrap: true,
      showFieldsSetting: false,
      showAsyncExport: false, // 异步下载弹窗
      exportLoading: false,
    };
  },
  computed: {
    showOriginalLog() {
      return this.contentType === 'original';
    },
    asyncExportUsable() {
      return this.$attrs['async-export-usable'];
    },
    asyncExportUsableReason() {
      return this.$attrs['async-export-usable-reason'];
    },
  },
  methods: {
    // 字段设置
    handleDropdownShow() {
      this.showFieldsSetting = true;
    },
    handleDropdownHide() {
      this.showFieldsSetting = false;
    },
    confirmModifyFields(displayFieldNames, showFieldAlias) {
      this.modifyFields(displayFieldNames, showFieldAlias);
      this.closeDropdown();
    },
    /** 更新显示字段 */
    modifyFields(displayFieldNames, showFieldAlias) {
      this.$emit('fieldsUpdated', displayFieldNames, showFieldAlias);
    },
    closeDropdown() {
      this.showFieldsSetting = false;
      this.$refs.fieldsSettingPopper.instance.hide();
    },
    setPopperInstance(status = true) {
      this.$refs.fieldsSettingPopper.instance.set({
        hideOnClick: status,
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '@/scss/mixins/flex.scss';

  .original-log-panel {
    .original-log-panel-tools {
      display: flex;
      justify-content: space-between;
    }

    .tools-more {
      @include flex-center;

      .switch-label {
        margin-right: 2px;
        color: #63656e;
        font-size: 12px;
      }
    }

    .operation-icons {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-left: 16px;

      .operation-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        margin-left: 10px;
        cursor: pointer;
        border: 1px solid #c4c6cc;
        transition: boder-color .2s;
        border-radius: 2px;
        outline: none;

        &:hover {
          border-color: #979ba5;
          transition: boder-color .2s;
        }

        &:active {
          border-color: #3a84ff;
          transition: boder-color .2s;
        }

        .log-icon {
          width: 16px;
          font-size: 16px;
          color: #979ba5;
        }
      }

      .disabled-icon {
        background-color: #fff;
        border-color: #dcdee5;
        cursor: not-allowed;

        &:hover,
        .log-icon {
          border-color: #dcdee5;
          color: #c4c6cc;
        }
      }
    }
  }
</style>
