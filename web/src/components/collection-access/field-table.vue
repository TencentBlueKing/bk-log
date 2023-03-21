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
  <div class="field-table-container" v-bkloading="{ isLoading: isExtracting }">
    <div class="field-method-head" v-if="!isPreviewMode">
      <!-- <span class="field-method-link fr mr10" @click.stop="isReset = true">{{ 重置 }}</span> -->
      <div :class="{ 'table-setting': true, 'disabled-setting': isSettingDisable || isSetDisabled }">
        <div class="fr form-item-flex bk-form-item">
          <!-- <label class="bk-label has-desc" v-bk-tooltips="$t('确认保留原始日志,会存储在log字段. 其他字段提取内容会进行追加')">
            <span>{{ $t('保留原始日志') }}</span>
          </label> -->
          <div class="bk-form-content">
            <bk-checkbox
              :checked="true"
              :true-value="true"
              :false-value="false"
              :disabled="isSettingDisable || isSetDisabled"
              v-model="retainOriginalText"
              @change="handleKeepLog">
              <label class="bk-label has-desc" v-bk-tooltips="$t('确认保留原始日志,会存储在log字段. 其他字段提取内容会进行追加')">
                <span>{{ $t('保留原始日志') }}</span>
              </label>
            </bk-checkbox>
            <!-- <bk-switcher size="small" theme="primary" v-model="retainOriginalText"></bk-switcher> -->
          </div>
        </div>
        <!-- <bk-switcher
          size="small"
          theme="primary"
          class="visible-deleted-btn"
          v-model="deletedVisible"
          @change="visibleHandle">
        </bk-switcher> -->
        <span
          :class="`bk-icon toggle-icon icon-${ deletedVisible ? 'eye-slash' : 'eye'}`"
          data-test-id="fieldExtractionBox_span_hideItem"
          @click="visibleHandle">
        </span>
        <span class="visible-deleted-text">
          {{ $t('已隐藏 {n} 项', { n: deletedNum })}}
        </span>
        <span
          v-if="!isTempField"
          class="field-method-link fr"
          @click.stop="viewStandard">
          {{ $t('查看内置字段') }}
        </span>

      </div>
    </div>

    <div class="preview-panel-left">
      <bk-form :label-width="0" :model="formData" ref="fieldsForm">
        <bk-table
          class="field-table"
          size="small"
          :empty-text="$t('暂无内容')"
          :row-key="extractMethod === 'bk_log_delimiter' ? 'field_index' : 'field_name'"
          :data="deletedVisible ? hideDeletedTable : tableList">
          <template>
            <!-- <bk-table-column -->
            :label="$t('列')"
            align="center"
            :resizable="false"
            width="40"
            v-if="!isPreviewMode && extractMethod === 'bk_log_delimiter'">
            <template slot-scope="props">
              <span>{{ props.row.field_index }}</span>
            </template>
            <!-- </bk-table-column> -->
            <!-- 字段名 -->
            <bk-table-column
              :label="$t('字段名')"
              :render-header="$renderHeader"
              :resizable="false"
              min-width="100">
              <template slot-scope="props">
                <div v-if="isPreviewMode" class="overflow-tips" v-bk-overflow-tips>
                  <span>{{ props.row.field_name }}</span>
                </div>
                <bk-form-item v-else :class="{ 'is-required is-error': props.row.fieldErr }">
                  <bk-input
                    :disabled="props.row.is_delete || extractMethod !== 'bk_log_delimiter' || isSetDisabled"
                    v-model.trim="props.row.field_name"
                    @blur="checkFieldNameItem(props.row)"></bk-input>
                  <template v-if="props.row.fieldErr">
                    <i
                      class="bk-icon icon-exclamation-circle-shape tooltips-icon"
                      style="right: 8px;"
                      v-bk-tooltips.top="props.row.fieldErr">
                    </i>
                  </template>
                </bk-form-item>
              </template>
            </bk-table-column>
            <!-- 重命名 -->
            <bk-table-column
              :render-header="renderHeaderAliasName"
              :resizable="false"
              v-if="isPreviewMode || extractMethod === 'bk_log_json'"
              min-width="100">
              <template slot-scope="props">
                <div v-if="isPreviewMode" class="overflow-tips" v-bk-overflow-tips>
                  <span>{{ props.row.alias_name }}</span>
                </div>
                <bk-form-item
                  v-else
                  :class="{ 'is-required is-error': props.row.aliasErr }">
                  <bk-input
                    :disabled="props.row.is_delete || isSetDisabled"
                    v-model.trim="props.row.alias_name"
                    @blur="checkAliasNameItem(props.row)">
                  </bk-input>
                  <template v-if="props.row.aliasErr">
                    <i
                      class="bk-icon icon-exclamation-circle-shape tooltips-icon"
                      style="right: 8px;"
                      v-bk-tooltips.top="props.row.aliasErr"></i>
                  </template>
                </bk-form-item>
              </template>
            </bk-table-column>
            <!-- 字段说明 -->
            <bk-table-column :render-header="renderHeaderDescription" :resizable="false" min-width="100">
              <template slot-scope="props">
                <div v-if="isPreviewMode" class="overflow-tips" v-bk-overflow-tips>
                  <span>{{ props.row.description }}</span>
                </div>
                <bk-input
                  v-else
                  :disabled="props.row.is_delete || isSetDisabled"
                  v-model.trim="props.row.description"></bk-input>
              </template>
            </bk-table-column>
            <!-- 类型 -->
            <bk-table-column
              :label="$t('类型')"
              :render-header="$renderHeader"
              :resizable="false"
              min-width="100">
              <template slot-scope="props">
                <div v-if="isPreviewMode" class="overflow-tips" v-bk-overflow-tips>
                  <span>{{ props.row.field_type }}</span>
                </div>
                <!-- <bk-form-item v-else
                  :required="true"
                  :rules="props.row.is_delete ? notCheck : rules.field_type"
                  :property="'tableList.' + props.$index + '.field_type'">
                  <bk-select
                    :clearable="false"
                    :disabled="props.row.is_delete"
                    v-model="props.row.field_type"
                    @selected="(value) => {
                      fieldTypeSelect(value, props.row, props.$index)
                    }">
                    <bk-option v-for="option in globalsData.field_data_type"
                      :key="option.id"
                      :id="option.id"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </bk-form-item> -->
                <!-- 替代方案 -->
                <!-- <bk-form-item v-else
                :class="{ 'is-required is-error': props.row.typeErr }"
                 :rules="props.row.is_delete ? notCheck : rules.field_type"
                 :property="'tableList.' + props.$index + '.field_type'"> -->
                <bk-form-item v-else :class="{ 'is-required is-error': props.row.typeErr }">
                  <bk-select
                    :clearable="false"
                    :disabled="props.row.is_delete || isSetDisabled"
                    v-model="props.row.field_type"
                    @selected="(value) => {
                      fieldTypeSelect(value, props.row, props.$index)
                    }">
                    <bk-option
                      v-for="option in globalsData.field_data_type"
                      :key="option.id"
                      :id="option.id"
                      :disabled="isTypeDisabled(props.row, option)"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                  <template v-if="props.row.typeErr">
                    <i
                      class="bk-icon icon-exclamation-circle-shape tooltips-icon"
                      style="right: 8px;"
                      v-bk-tooltips.top="$t('必填项')"></i>
                  </template>
                </bk-form-item>
              </template>
            </bk-table-column>
            <!--<bk-table-column :label="聚合" align="center" :resizable="false" width="50">
              <template slot-scope="props">
                <bk-popover v-if="props.row.is_time" :content="$t('时间字段默认设置可以聚合')">
                  <bk-checkbox
                    disabled
                    v-model="props.row.is_dimension">
                  </bk-checkbox>
                </bk-popover>
                <bk-checkbox v-else
                  :disabled="isPreviewMode || props.row.is_delete || props.row.is_analyzed"
                  v-model="props.row.is_dimension">
                </bk-checkbox>
              </template>
            </bk-table-column>-->
            <!-- 字符串类型下才能设置分词， 分词和维度只能选其中一个，且分词和时间不能同时存在, 选定时间后就同时勾选维度-->
            <!-- 分词 -->
            <bk-table-column :render-header="renderHeaderParticipleName" align="center" :resizable="false" width="50">
              <template slot-scope="props">
                <bk-checkbox
                  :disabled="isPreviewMode
                    || props.row.is_delete
                    || props.row.field_type !== 'string'
                    || props.row.is_time
                    || isSetDisabled"
                  v-model="props.row.is_analyzed">
                </bk-checkbox>
              </template>
            </bk-table-column>
            <!-- 时间 -->
            <bk-table-column
              :label="$t('时间')"
              :render-header="$renderHeader"
              align="center"
              :resizable="false"
              width="60">
              <template slot-scope="props">
                <template v-if="isPreviewMode">
                  <div class="field-date field-date-disable">
                    <i :class="{ 'log-icon': true, 'icon-date-picker': true, active: props.row.is_time }"></i>
                  </div>
                </template>
                <template v-else>
                  <div
                    v-if="props.row.is_delete"
                    :class="['field-date field-date-disable', { 'field-date-active': props.row.is_time }]">
                    <i :class="{ 'log-icon': true, 'icon-date-picker': true, active: props.row.is_time }"></i>
                  </div>
                  <template v-else>
                    <bk-popover
                      v-if="props.row.is_time"
                      :ref="`more${props.$index}`"
                      :distance="3"
                      placement="bottom-start"
                      theme="light"
                      trigger="click"
                      :arrow="false">
                      <div class="field-date field-date-active">
                        <i class="log-icon icon-date-picker"></i>
                      </div>
                      <div slot="content">
                        <ul class="field-dropdown-list" slot="dropdown-content">
                          <li
                            class="dropdown-item"
                            @click.stop="setDateFormat(props.row, props.$index)">
                            {{ '编辑时间格式' }}
                          </li>
                          <li
                            class="dropdown-item"
                            @click.stop="cancelDateFormat(props.row, props.$index)">
                            {{ '取消设为时间' }}
                          </li>
                        </ul>
                      </div>
                    </bk-popover>
                    <template v-else>
                      <div v-if="hasDateField"
                           class="field-date"
                           v-bk-tooltips.right="$t('只能设置一个数据时间，如果要更改请先取消原来的')"
                           @click.stop="setDateFormat(props.row)">
                        <i class="log-icon icon-date-picker"></i>
                      </div>
                      <div v-else class="field-date" @click.stop="setDateFormat(props.row)">
                        <i class="log-icon icon-date-picker"></i>
                      </div>
                    </template>
                  </template>
                </template>
              </template>
            </bk-table-column>
            <!-- 操作 -->
            <bk-table-column
              :label="$t('操作')"
              :render-header="$renderHeader"
              :resizable="false"
              align="center"
              width="60"
              prop="plugin_version"
              v-if="!isPreviewMode && extractMethod !== 'bk_log_regexp'">
              <template slot-scope="props">
                <span
                  class="table-link"
                  :style="`color:${isSetDisabled ? '#dcdee5' : '#3a84ff'};`"
                  @click="isDisableOperate(props.row)">
                  {{ props.row.is_delete ? $t('复原') : $t('隐藏') }}
                </span>
              </template>
            </bk-table-column>
            <div slot="empty" class="empty-text">{{ $t('请先选择字段提取模式') }}</div>
          </template>
        </bk-table>
      </bk-form>
    </div>

    <div class="preview-panel-right">
      <div class="preview-title preview-item">{{ $t('预览（值）') }}</div>
      <template v-if="deletedVisible">
        <div
          class="preview-item"
          v-for="(row, index) in hideDeletedTable"
          :key="index"
          :title="row.value">
          {{ row.value }}
        </div>
      </template>
      <template v-else>
        <div
          class="preview-item"
          v-for="(row, index) in tableList"
          :key="index"
          :title="row.value">
          {{ row.value }}
        </div>
      </template>
    </div>

    <bk-dialog
      v-if="!isPreviewMode"
      v-model="dialogDate"
      width="680"
      ext-cls="field-date-dialog"
      :header-position="'left'"
      :mask-close="false"
      :title="$t('选择时间格式')"
      :auto-close="false"
      @cancel="resetDateDialog">
      <div slot style="width: 560px; padding-left: 12px;">
        <p class="prompt">{{$t('设置了时间格式后将替换默认的数据时间')}}</p>
        <!-- <p class="prompt">时间指<span>数据时间</span>，而非录入时间</p> -->
        <bk-form :label-width="145" :model="dialogField" ref="dateForm">
          <bk-form-item :label="$t('数据时间')" :property="'source_name'">
            <bk-input v-model="dialogField.time_value" :placeholder="$t('字段的预览值')" disabled></bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t('时间格式')"
            required
            :rules="rules.time_format"
            :property="'time_format'">
            <bk-select v-model="dialogField.time_format" searchable :clearable="false" @selected="formatChange">
              <bk-option
                v-for="item in globalsData.field_date_format"
                :id="item.id"
                :name="item.name + ' (' + item.description + ')'"
                :key="item.id">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('时区选择')"
            required
            :rules="rules.time_zone"
            :property="'time_zone'">
            <bk-select v-model="dialogField.time_zone" :clearable="false">
              <bk-option
                v-for="item in globalsData.time_zone"
                :id="item.id"
                :name="item.name"
                :key="item.id">
              </bk-option>
            </bk-select>
          </bk-form-item>
        </bk-form>
      </div>
      <div slot="footer">
        <bk-button
          v-if="!timeCheckResult"
          :icon="checkLoading ? 'loading' : ''"
          theme="primary"
          :disabled="!dialogField.time_value || checkLoading"
          @click.stop="requestCheckTime">
          {{ $t('确定') }}
        </bk-button>
        <bk-button
          v-else
          theme="primary"
          :icon="checkLoading ? 'loading' : ''"
          @click.stop="confirmHandle">
          {{ $t('确定') }}
        </bk-button>
        <bk-button @click.stop="resetDateDialog">{{ $t('取消') }}</bk-button>
      </div>
    </bk-dialog>
    <bk-dialog
      v-model="isReset"
      @confirm="resetField"
      theme="primary"
      :title="$t('重置确认')">
      {{$t('重置将丢失当前的配置信息，重置为上一次保存的配置内容。确认请继续。')}}
    </bk-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'FieldTable',
  props: {
    isEditJson: {
      type: Boolean,
      default: undefined,
    },
    tableType: {
      type: String,
      default: 'edit',
    },
    extractMethod: {
      type: String,
      default: 'bk_log_json',
    },
    deletedVisible: {
      type: Boolean,
      default: true,
    },
    // jsonText: {
    //     type: Array
    // },
    fields: {
      type: Array,
      default: () => [],
    },
    isTempField: {
      type: Boolean,
      default: false,
    },
    isExtracting: {
      type: Boolean,
      default: false,
    },
    retainOriginalValue: {
      type: Boolean,
      default: false,
    },
    isSetDisabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isReset: false,
      dialogDate: false,
      dialogField: {
        time_zone: '', // 默认值 8
        time_format: '',
        time_value: '',
      },
      curRow: {},
      formData: {
        tableList: [],
      },
      timeCheckResult: false,
      checkLoading: false,
      retainOriginalText: true, // 保留原始日志
      rules: {
        field_name: [ // 存在bug，暂时启用
          // {
          //     required: true,
          //     trigger: 'blur'
          // },
          // {
          //     validator: this.checkFieldNameFormat,
          //     trigger: 'blur'
          // },
          // {
          //     validator: this.checkFieldName,
          //     trigger: 'blur'
          // }
        ],
        alias_name: [
          // 目前组件不能拿到其他字段的值，不能通过validator进行验证
          // {
          //     validator: this.checkAliasName,
          //     trigger: 'blur'
          // }
          {
            max: 50,
            trigger: 'blur',
          },
          {
            regex: /^[A-Za-z0-9_]+$/,
            trigger: 'blur',
          },
        ],
        field_type: [
          // {
          //     required: true,
          //     trigger: 'change'
          // }
        ],
        time_zone: [
          {
            required: true,
            trigger: 'change',
          },
        ],
        time_format: [
          {
            required: true,
            trigger: 'change',
          },
        ],
        notCheck: [
          {
            validator() {
              return true;
            },
            trigger: 'change',
          },
        ],
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters('globals', ['globalsData']),
    isSettingDisable() {
      return !this.fields.length;
    },
    hasDateField() {
      return this.tableList.find(item => item.is_time && !item.is_delete);
    },
    deletedNum() {
      return this.tableList.filter(item => item.is_delete).length;
    },
    isPreviewMode() {
      return this.tableType === 'preview';
    },
    tableList() {
      return this.formData.tableList;
    },
    hideDeletedTable() {
      return this.formData.tableList.filter(item => !item.is_delete);
    },
    defaultZone() { // 默认时区
      const item = this.globalsData.time_zone.find(item => item.default);
      return item ? item.id : '';
    },
  },
  watch: {
    fields: {
      deep: true,
      handler() {
        this.reset();
      },
    },
    retainOriginalValue(newVal) {
      this.retainOriginalText = newVal;
    },
  },
  async mounted() {
    this.retainOriginalText = this.retainOriginalValue;
    this.reset();
  },
  methods: {
    reset() {
      let arr = [];
      const copyFields = JSON.parse(JSON.stringify(this.fields)); // option指向地址bug
      const errTemp = {
        fieldErr: '',
        typeErr: false,
        aliasErr: '',
      };
      if (this.extractMethod !== 'bk_log_json') {
        errTemp.aliasErr = false;
      }
      copyFields.reduce((list, item) => {
        list.push(Object.assign({}, errTemp, item));
        return list;
      }, arr);
      arr.forEach(item => item.previous_type = item.field_type);

      if (!this.isPreviewMode) {
        arr = arr.filter(item => !item.is_built_in);
      }

      if (this.isEditJson === false && !this.isTempField) { // 新建JSON时，类型如果不是数字，则默认为字符串
        arr.forEach((item) => {
          if (typeof item.value !== 'number') {
            item.field_type = 'string';
            item.previous_type = 'string';
          }
        });
      }

      // 根据预览值 value 判断不是数字，则默认为字符串
      arr.forEach((item) => {
        const { value, field_type } = item;
        // eslint-disable-next-line camelcase
        if (field_type === '' && value !== '' && this.judgeNumber(value)) {
          item.field_type = 'string';
          item.previous_type = 'string';
        }
      });
      this.formData.tableList.splice(0, this.formData.tableList.length, ...arr);
    },
    resetField() {
      this.$emit('reset');
    },
    setDateFormat(row, $index) {
      if (this.isSetDisabled) return;
      if ($index || $index === 0) {
        this.$refs[`more${$index}`].instance.hide(); // 解决当前版本popover层在dialog层之上的问题
      }
      this.curRow = row;
      const option = {
        time_zone: row.option
          ? (row.option.time_zone || (row.option.time_zone === 0 ? row.option.time_zone : this.defaultZone))
          : this.defaultZone,
        time_format: row.option ? row.option.time_format : '',
        time_value: row.value || '',
      };
      if ((!row.is_time || (row.is_time && row.is_delete)) && this.hasDateField) {
        this.$bkInfo({
          title: this.$t('重设时间列'),
          subTitle: this.$t('将此列设置为时间，会将取消已设为时间的列，是否继续？'),
          type: 'warning',
          confirmFn: () => {
            Object.assign(this.dialogField, option);
            this.dialogDate = true;
            this.timeCheckResult = !!row.is_time;
          },
        });
        return false;
      }
      Object.assign(this.dialogField, option);
      this.timeCheckResult = !!row.is_time;
      this.dialogDate = true;
    },
    confirmHandle() {
      this.$refs.dateForm.validate().then(() => {
        if (!this.timeCheckResult) return;
        if (!this.curRow.is_time) {
          this.formData.tableList.forEach((row) => {
            const isCur = this.extractMethod === 'bk_log_delimiter'
              ? this.curRow.field_index === row.field_index : this.curRow.field_name === row.field_name;
            if (row.is_time && !isCur) {
              this.cancelDateFormat(row);
            }
          });
        }
        this.curRow.is_analyzed = false; // 分词和时间不能同时设置
        this.curRow.is_time = true;
        // this.curRow.is_dimension = true
        Object.assign(
          this.curRow.option,
          { time_zone: this.dialogField.time_zone, time_format: this.dialogField.time_format },
        );
        this.resetDateDialog();
        this.dialogDate = false;
      }, () => {});
    },
    requestCheckTime() {
      this.$refs.dateForm.validate().then(() => {
        this.checkLoading = true;
        const { time_format, time_zone, time_value } = this.dialogField;
        this.$http.request('collect/getCheckTime', {
          params: {
            collector_config_id: this.curCollect.collector_config_id,
          },
          data: {
            time_format,
            time_zone,
            data: time_value,
          },
        }).then(() => {
          this.timeCheckResult = true;
          this.confirmHandle();
        })
          .catch(() => {
            this.timeCheckResult = false;
          })
          .finally(() => {
            this.checkLoading = false;
          });
      });
    },
    cancelDateFormat(row, $index) {
      if ($index || $index === 0) {
        this.$refs[`more${$index}`].instance.hide(); // 解决当前版本popover层在dialog层之上的问题
      }
      row.is_time = false;
      Object.assign(row.option, {
        time_zone: '',
        time_format: '',
      });
    },
    resetDateDialog() {
      this.dialogDate = false;
      Object.assign(this.dialogField, {
        time_zone: '',
        time_format: '',
        time_value: '',
      });
    },
    // 当前字段类型是否禁用
    isTypeDisabled(row, option) {
      if (row.verdict) {
        // 不是数值，相关数值类型选项被禁用
        return ['int', 'long', 'double', 'float'].includes(option.id);
      }
      // 是数值，如果值大于 2147483647 即 2^31 - 1，int 选项被禁用
      return option.id === 'int' && row.value > 2147483647;
    },
    fieldTypeSelect(val, $row, $index) {
      const fieldName = $row.field_name;
      const fieldType = $row.field_type;
      const previousType = $row.previous_type;
      if (fieldType && this.curCollect.table_id) {
        const row = this.fields.find(item => item.field_name === fieldName);
        if (row && row.field_type && row.field_type !== val) {
          const h = this.$createElement;
          this.$bkInfo({
            // title: '修改',
            // subTitle: '修改类型后，会影响到之前采集的数据',
            subHeader: h('p', {
              style: {
                whiteSpace: 'normal',
              },
            }, this.$t('更改字段类型后在同时检索新老数据时可能会出现异常，确认请继续')),
            type: 'warning',
            confirmFn: () => {
              this.formData.tableList[$index].field_type = val;
              this.formData.tableList[$index].previousType = val;
              if (val !== 'string') {
                this.formData.tableList[$index].is_analyzed = false;
              }
              this.checkTypeItem($row);
            },
            cancelFn: () => {
              this.formData.tableList[$index].field_type = previousType;
              if (previousType !== 'string') {
                this.formData.tableList[$index].is_analyzed = false;
              }
              this.checkTypeItem($row);
            },
          });
          return false;
        }
      } else {
        if (val !== 'string') {
          this.formData.tableList[$index].is_analyzed = false;
        }
        this.formData.tableList[$index].field_type = val;
      }
      this.checkTypeItem($row);
    },
    formatChange(val) {
      this.timeCheckResult = false;
      this.dialogField.time_format = val;
    },
    viewStandard() {
      if (this.isSettingDisable) return;

      this.$emit('standard');
    },
    judgeNumber(value) {
      if (value === 0) return false;

      return (value && value !== ' ') ? isNaN(value) : true;
    },
    getData() {
      // const data = JSON.parse(JSON.stringify(this.formData.tableList.filter(row => !row.is_delete)))
      const data = JSON.parse(JSON.stringify(this.formData.tableList));
      data.forEach((item) => {
        // eslint-disable-next-line no-prototype-builtins
        if (item.hasOwnProperty('fieldErr')) {
          delete item.fieldErr;
        }
        // eslint-disable-next-line no-prototype-builtins
        if (item.hasOwnProperty('aliasErr')) {
          delete item.aliasErr;
        }
        // eslint-disable-next-line no-prototype-builtins
        if (item.hasOwnProperty('typeErr')) {
          delete item.typeErr;
        }
      });
      return data;
    },
    // checkFieldNameFormat (val) {
    //     return /^(?!_)(?!.*?_$)^[A-Za-z0-9_]+$/ig.test(val)
    // },
    // checkFieldName (val) {
    //     return this.extractMethod === 'bk_log_json' ?
    //             true : !this.globalsData.field_built_in.find(item => item.id === val.toLocaleLowerCase())
    // },
    checkTypeItem(row) {
      row.typeErr = row.is_delete ? false : !row.field_type;
      return !row.typeErr;
    },
    checkType() {
      return new Promise((resolve, reject) => {
        try {
          let result = true;
          this.formData.tableList.forEach((row) => {
            if (!this.checkTypeItem(row)) {
              result = false;
            }
          });
          if (result) {
            resolve();
          } else {
            console.warn('Type校验错误');
            reject(result);
          }
        } catch (err) {
          console.warn('Type校验错误');
          reject(err);
        }
      });
    },
    checkFieldNameItem(row) {
      const { field_name, is_delete } = row;
      let result = '';
      /* eslint-disable */
      if (!is_delete) {
        if (!field_name) {
          result = this.$t('必填项')
        } else if (this.extractMethod !== 'bk_log_json' && !/^(?!_)(?!.*?_$)^[A-Za-z0-9_]+$/ig.test(field_name)) {
          result = this.$t('只能包含a-z、A-Z、0-9和_，且不能以_开头和结尾')
        } else if (this.extractMethod !== 'bk_log_json' && this.globalsData.field_built_in.find(item => item.id === field_name.toLocaleLowerCase())) {
          result = this.extractMethod === 'bk_log_regexp' ? this.$t('字段名与系统字段重复，必须修改正则表达式') : this.$t('字段名与系统内置字段重复')
        } else {
          result = ''
        }
      } else {
        result = ''
      }
      row.fieldErr = result
      /* eslint-enable */
      return result;
    },
    checkFieldName() {
      return new Promise((resolve, reject) => {
        try {
          let result = true;
          this.formData.tableList.forEach((row) => {
            if (this.checkFieldNameItem(row)) { // 返回 true 的时候未通过
              result = false;
            }
          });
          if (result) {
            resolve();
          } else {
            console.warn('FieldName校验错误');
            reject(result);
          }
        } catch (err) {
          console.warn('FieldName校验错误');
          reject(err);
        }
      });
    },
    checkAliasNameItem(row) {
      const { field_name: fieldName, alias_name: aliasName, is_delete: isDelete } = row;
      if (isDelete) {
        return true;
      }

      if (aliasName) {
        // 设置了别名
        if (!/^(?!^\d)[\w]+$/ig.test(aliasName)) {
          // 别名只支持【英文、数字、下划线】，并且不能以数字开头
          row.aliasErr = this.$t('别名只支持【英文、数字、下划线】，并且不能以数字开头');
          return false;
        }
        if (this.globalsData.field_built_in.find(item => item.id === aliasName.toLocaleLowerCase())) {
          // 别名不能与内置字段名相同
          row.aliasErr = this.$t('别名不能与内置字段名相同');
          return false;
        }
      } else if (this.globalsData.field_built_in.find(item => item.id === fieldName.toLocaleLowerCase())) {
        // 字段名与内置字段冲突，必须设置别名
        row.aliasErr = this.$t('字段名与内置字段冲突，必须设置别名');
        return false;
      }

      row.aliasErr = '';
      return true;
    },
    checkAliasName() {
      return new Promise((resolve, reject) => {
        try {
          let result = true;
          this.formData.tableList.forEach((row) => {
            if (!this.checkAliasNameItem(row)) {
              result = false;
            }
          });
          if (result) {
            resolve();
          } else {
            console.warn('AliasName校验错误');
            reject(result);
          }
        } catch (err) {
          console.warn('AliasName校验错误');
          reject(err);
        }
      });
    },
    validateFieldTable() {
      const promises = [];
      promises.push(this.checkFieldName());
      promises.push(this.checkAliasName());
      promises.push(this.checkType());
      return promises;
    },
    visibleHandle() {
      if (this.isSettingDisable) return;

      this.$emit('deleteVisible', !this.deletedVisible);
    },
    handleKeepLog(value) {
      this.$emit('handleKeepLog', value);
    },
    renderHeaderAliasName(h) {
      return h('div', {
        class: 'render-header',
      }, [
        h('span', { directives: [{ name: 'bk-overflow-tips' }], class: 'title-overflow' }, [this.$t('重命名')]),
        h('span', this.$t('(选填)')),
        h('span', {
          class: 'icon log-icon icon-info-fill',
          directives: [
            {
              name: 'bk-tooltips',
              value: this.$t('非必填字段，填写后将会替代字段名；字段名与内置字段重复时，必须重新命名。'),
            },
          ],
        }),
      ]);
    },
    renderHeaderDescription(h) {
      return h('div', {
        class: 'render-header',
      }, [
        h('span', { directives: [{ name: 'bk-overflow-tips' }], class: 'title-overflow' }, [this.$t('字段说明')]),
        h('span', this.$t('(选填)')),
      ]);
    },
    renderHeaderParticipleName(h) {
      return h('span', {
        directives: [
          {
            name: 'bk-tooltips',
            value: this.$t('选中分词,适用于分词检索,不能用于指标和维度'),
          },
        ],
      }, [
        h('span', {
          class: 'render-Participle title-overflow',
          directives: [{ name: 'bk-overflow-tips' }],
        }, [this.$t('分词')]),
      ]);
    },
    isDisableOperate(row) {
      if (this.isSetDisabled) return;
      row.is_delete = !row.is_delete;
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/mixins/overflow-tips.scss';

  .field-table-container {
    position: relative;
    display: flex;

    .field-method-head {
      position: absolute;
      top: -30px;
      right: 0;
    }

    .field-table {
      .cell {
        padding-left: 5px;
        padding-right: 5px;
      }

      .bk-label {
        display: none;
      }

      .render-header {
        display: flex;
        align-items: center;
        height: 100%;

        span:nth-child(2) {
          color: #979ba5;
        }

        .render-Participle {
          display: inline-block;
          width: 100%;
          text-align: center;
        }

        span:nth-child(3) {
          display: flex;
          justify-content: center;
          align-items: center;
          margin-top: 2px;
          outline: none;
          width: 14px;
          height: 14px;
          font-size: 14px;
        }
      }

      .bk-table-empty-text {
        padding: 12px 0;
      }

      .bk-table-empty-block {
        min-height: 32px;
      }

      .empty-text {
        color: #979ba5;
      }
    }

    .preview-panel-left {
      flex: 1;
    }

    .preview-panel-right {
      width: 335px;
      color: #c4c6cc;
      background: #63656e;
      border-bottom: 1px solid #72757d;
      font-size: 12px;
      border-radius: 0 2px 2px 0;

      .preview-item {
        height: 42px;;
        line-height: 42px;
        padding: 0 10px;
        border-top: 1px solid #72757d;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;

        &:first-child {
          height: 43px;
          border-top: 1px solid transparent;
        }
      }

      .preview-title {
        color: #fff;
      }
    }

    .bk-table .table-link {
      cursor: pointer;
    }

    .field-date {
      display: inline-block;
      padding: 0 10px;
      font-size: 14px;
      outline: none;

      &:hover {
        color: #3a84ff;
        cursor: pointer;
      }

      &.field-date-active {
        color: #3a84ff;

        .icon-date-picker {
          color: #3a84ff;
        }
      }

      &.field-date-disable {
        color: #dcdee5;
        cursor: not-allowed;
      }
    }

    .icon-date-picker {
      color: #979ba5;

      &.active {
        color: #3a84ff;
      }
    }
  }

  .field-date-dialog {
    .prompt {
      margin-bottom: 20px;
      padding: 6px 7px;
      font-size: 12px;
      color: #63656e;
      background: #f6f6f6;

      span {
        font-weight: 600;
        color: #313238;
      }
    }

    .bk-label {
      text-align: left;
    }
  }

  .field-dropdown-list {
    margin: -7px -14px;
    padding: 7px 0;

    .dropdown-item {
      padding: 0 10px;
      line-height: 32px;
      font-size: 12px;
      color: #63656e;
      cursor: pointer;

      &:hover {
        color: #3a84ff;
        background: #e1ecff;
      }
    }
  }

  .header {
    /* stylelint-disable-next-line declaration-no-important */
    white-space: normal !important;
  }
</style>
