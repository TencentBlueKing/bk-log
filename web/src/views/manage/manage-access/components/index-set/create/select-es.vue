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
  <bk-dialog
    v-model="showDialog"
    header-position="left"
    :title="$t('新增索引')"
    :width="680"
    :mask-close="false"
    :show-footer="false">
    <div class="slot-container">
      <bk-form
        :model="formData"
        :label-width="100"
        :rules="formRules"
        ref="formRef">
        <bk-form-item
          :label="$t('索引')"
          required
          property="resultTableId"
          class="add-index-input-container">
          <bk-input
            v-model.trim="formData.resultTableId"
            placeholder="log_search_*"
            class="king-input"
            @focus="handleFocus"
            @enter="handleSearch"></bk-input>
          <bk-button
            class="king-button"
            :loading="searchLoading"
            :disabled="!formData.resultTableId || formData.resultTableId === '*'"
            @click="handleSearch">
            {{ $t('搜索') }}
          </bk-button>
          <div class="error-tips-container" v-if="indexErrorText">
            <span class="log-icon icon-info-fill" v-bk-tooltips="{ width: 440, content: indexErrorText }"></span>
          </div>
          <div class="input-tips">{{ $t('支持“*”匹配，不支持其他特殊符号') }}</div>
        </bk-form-item>
        <bk-form-item label="">
          <div class="result-tips" v-if="matchedTableIds.length">
            <i class="bk-icon icon-check-circle-shape"></i>
            {{ $t('成功匹配 {x} 条索引', { x: matchedTableIds.length }) }}
          </div>
          <bk-table
            v-bkloading="{ isLoading: tableLoading }"
            :data="matchedTableIds"
            max-height="400">
            <bk-table-column
              :label="$t('索引')"
              property="result_table_id"
              min-width="490">
            </bk-table-column>
            <div slot="empty">
              <empty-status :empty-type="emptyType" @operation="handleOperation" />
            </div>
          </bk-table>
        </bk-form-item>
        <bk-form-item
          :label="$t('时间字段')"
          required
          property="time_field">
          <bk-select
            :value="formData.time_field"
            searchable
            :clearable="false"
            @selected="handleSelectedTimeField">
            <bk-option
              v-for="item in timeFields"
              :key="item.field_name"
              :id="item.field_name"
              :name="item.field_name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          :label="$t('时间格式')"
          required
          property="time_field_unit"
          v-if="formData.time_field_type === 'long'">
          <bk-select
            v-model="formData.time_field_unit"
            searchable
            :clearable="false">
            <bk-option
              v-for="item in timeUnits"
              :key="item.id"
              :id="item.id"
              :name="item.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <div slot="empty">
          <empty-status :empty-type="emptyType" @operation="handleOperation" />
        </div>
      </bk-form>
      <div slot="footer" class="button-footer">
        <bk-button
          class="king-button"
          theme="primary"
          :loading="confirmLoading"
          @click="handleConfirm">
          {{ $t('添加') }}
        </bk-button>
        <bk-button class="king-button" @click="handleCancel">{{ $t('取消') }}</bk-button>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import { mapState } from 'vuex';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    EmptyStatus,
  },
  props: {
    parentData: {
      type: Object,
      required: true,
    },
    timeIndex: {
      type: Object,
      default: null,
    },
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      showDialog: false,
      tableLoading: false,
      searchLoading: false,
      confirmLoading: false,
      indexErrorText: '',
      emptyType: 'empty',
      matchedTableIds: [], // 匹配到的索引 id，result table id list
      timeFields: [], // 字段类型为 date 或 long 的字段
      formData: {
        resultTableId: '',
        time_field: '',
        time_field_type: '',
        time_field_unit: 'microsecond',
      },
      timeUnits: [
        { name: this.$t('秒（second）'), id: 'second' },
        { name: this.$t('毫秒（millisecond）'), id: 'millisecond' },
        { name: this.$t('微秒（microsecond）'), id: 'microsecond' },
      ],
      formRules: {
        resultTableId: [{
          required: true,
          trigger: 'blur',
        }, {
          validator: val => val && val !== '*',
          trigger: 'blur',
        }],
        time_field: [{
          required: true,
          trigger: 'change',
        }, {
          validator: (val) => {
            if (!this.timeIndex) return true;
            return this.timeIndex.time_field === val;
          },
          message: this.$t('时间字段需要保持一致'),
          trigger: 'change',
        }],
        time_field_unit: [{
          required: true,
          trigger: 'change',
        }],
      },
    };
  },
  computed: {
    ...mapState(['spaceUid', 'bkBizId']),
  },
  methods: {
    openDialog() {
      this.showDialog = true;
      this.$refs.formRef.clearError();
      Object.assign(this, {
        tableLoading: false,
        searchLoading: false,
        confirmLoading: false,

        indexErrorText: '',
        matchedTableIds: [], // 匹配到的索引 id，result table id list
        timeFields: [], // 字段类型为 date 或 long 的字段
        formData: {
          resultTableId: '',
          time_field: '',
          time_field_type: '',
          time_field_unit: 'microsecond',
        },
      });
    },
    handleOperation(type) {
      if (type === 'clear-filter') {
        this.formData.resultTableId = '*';
        this.emptyType = 'empty';
        this.handleSearch();
        return;
      }

      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.handleSearch();
        return;
      }
    },
    // 如果result_table_id为空，在光标后自动追加*
    handleFocus(value, event) {
      if (!this.formData.resultTableId) {
        this.formData.resultTableId = '*';
        setTimeout(() => {
          event.target.setSelectionRange(0, 0);
        }, 50);
      }
    },
    // 匹配索引和字段
    async handleSearch() {
      if (!this.formData.resultTableId || this.formData.resultTableId === '*') {
        return;
      }
      this.emptyType = 'search-empty';
      this.indexErrorText = '';
      this.formData.time_field = '';
      this.formData.time_field_type = '';
      this.formData.time_field_unit = 'microsecond';
      this.searchLoading = true;
      this.tableLoading = true;
      const [idRes, fieldRes] = await Promise.all([this.fetchList(), this.fetchInfo()]);
      this.matchedTableIds = idRes;
      this.timeFields = fieldRes;
      this.searchLoading = false;
      this.tableLoading = false;
    },
    async fetchList() {
      try {
        const res = await this.$http.request('/resultTables/list', {
          query: {
            scenario_id: this.scenarioId,
            bk_biz_id: this.bkBizId,
            storage_cluster_id: this.parentData.storage_cluster_id,
            result_table_id: this.formData.resultTableId,
          },
        });
        return res.data;
      } catch (e) {
        console.warn(e);
        this.indexErrorText += e.message;
        this.emptyType = '500';
        return [];
      }
    },
    async fetchInfo() {
      try {
        const res = await this.$http.request('/resultTables/info', {
          params: {
            result_table_id: this.formData.resultTableId,
          },
          query: {
            scenario_id: this.scenarioId,
            bk_biz_id: this.bkBizId,
            storage_cluster_id: this.parentData.storage_cluster_id,
          },
        });
        const timeFields = res.data.fields.filter(item => item.field_type === 'date' || item.field_type === 'long');
        // 如果已经添加了索引，回填三个字段（禁止更改字段名）
        if (this.timeIndex) {
          const find = timeFields.find(item => item.field_name === this.timeIndex.time_field);
          if (find) {
            Object.assign(this.formData, this.timeIndex);
          }
        }
        return timeFields;
      } catch (e) {
        console.warn(e);
        this.indexErrorText += e.message;
        this.emptyType = '500';
        return [];
      }
    },
    // 选择时间字段
    handleSelectedTimeField(fieldName) {
      this.formData.time_field = fieldName;
      this.formData.time_field_type = this.timeFields.find(item => item.field_name === fieldName).field_type;
    },
    // 确认添加
    async handleConfirm() {
      try {
        await this.$refs.formRef.validate();
        this.confirmLoading = true;
        const data = {
          scenario_id: this.scenarioId,
          storage_cluster_id: this.parentData.storage_cluster_id,
          basic_indices: this.parentData.indexes.map(item => ({
            index: item.result_table_id,
            time_field: this.formData.time_field,
            time_field_type: this.formData.time_field_type,
          })),
          append_index: {
            index: this.formData.resultTableId,
            time_field: this.formData.time_field,
            time_field_type: this.formData.time_field_type,
          },
        };
        await this.$http.request('/resultTables/adapt', { data });
        this.$emit('selected', {
          bk_biz_id: this.bkBizId,
          result_table_id: this.formData.resultTableId,
        });
        this.$emit('update:timeIndex', {
          time_field: this.formData.time_field,
          time_field_type: this.formData.time_field_type,
          time_field_unit: this.formData.time_field_unit,
        });
        this.showDialog = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.confirmLoading = false;
      }
    },
    handleCancel() {
      this.showDialog = false;
    },
  },
};
</script>

<style scoped lang="scss">
  .slot-container {
    padding-right: 40px;

    ::v-deep .bk-form {
      .bk-label {
        text-align: left;
      }

      .bk-form-content {
        position: relative;
      }
    }

    .add-index-input-container {
      position: relative;

      .king-input {
        width: calc(100% - 90px);
      }

      .king-button {
        position: absolute;
        top: 0;
        right: 0;
      }

      .error-tips-container {
        position: absolute;
        top: 0;
        right: -32px;
      }

      .log-icon {
        font-size: 18px;
        cursor: pointer;
        color: #ea3636;
      }

      .input-tips {
        color: #979ba5;
        font-size: 12px;
        line-height: 14px;
        margin-top: 2px;
      }
    }

    .result-tips {
      position: absolute;
      top: 7px;
      right: 14px;
      z-index: 10;
      font-size: 12px;
      color: #2dcb56;
      padding-left: 12px;
    }

    .button-footer {
      text-align: right;
      margin-top: 20px;

      .king-button {
        width: 86px;

        &:first-child {
          margin-right: 8px;
        }
      }
    }
  }
</style>
