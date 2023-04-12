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
  <div v-if="scenarioId !== 'wineventlog'">
    <bk-form
      ref="validateForm"
      :label-width="getLabelWidth"
      :form-type="showType"
      :model="subFormData">
      <div v-if="!isStandardOutput">
        <!-- 日志路径 -->
        <div class="form-div mt log-paths" v-for="(log, index) in logPaths" :key="index">
          <bk-form-item
            required
            :label="index === 0 ? $t('日志路径') : ''"
            :rules="rules.paths"
            :property="'params.paths.' + index + '.value'">
            <div class="flex-ac">
              <bk-input
                v-model="log.value"
                data-test-id="sourceLogBox_input_addLogPath"
              ></bk-input>
              <div class="ml9">
                <i class="bk-icon icon-plus-circle-yuan icons"
                   data-test-id="sourceLogBox_i_newAddLogPath"
                   @click="addLog"></i>
                <i
                  :class="['bk-icon icon-minus-circle-shape icons ml9', { disable: logPaths.length === 1 }] "
                  data-test-id="sourceLogBox_i_deleteAddLogPath"
                  @click="delLog(index)"></i>
              </div>
            </div>
            <div class="tips" v-if="index === 0">
              <i18n path="日志文件的绝对路径，可使用 {0}">
                <span class="font-gray">{{ $t('通配符') }}</span>
              </i18n>
            </div>
          </bk-form-item>
        </div>
        <!-- 日志字符集 -->
        <bk-form-item class="mt" :label="$t('字符集')" required>
          <bk-select
            data-test-id="sourceLogBox_div_changeLogCharacterTet"
            style="width: 320px;"
            searchable
            v-model="subFormData.data_encoding"
            :clearable="false">
            <bk-option
              v-for="(option, ind) in globalsData.data_encoding"
              :key="ind"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </div>
      <!-- 过滤内容 -->
      <div :class="[
        'config-item',
        'filter-content',
        showType === 'horizontal' && 'horizontal-item',
        isEnLanguage && 'en-span'
      ]">
        <span v-bk-tooltips="$t('为减少传输和存储成本，可以过滤掉部分内容,更复杂的可在“清洗”功能中完成')">
          <span class="filter-title">{{$t('过滤内容')}}</span>
        </span>
        <bk-radio-group v-model="subFormData.params.conditions.type" @change="chooseType">
          <bk-radio value="match" style="margin-right: 8px">{{$t('字符串过滤')}}</bk-radio>
          <bk-radio value="separator">{{$t('分隔符过滤')}}</bk-radio>
        </bk-radio-group>
        <template v-if="isClickTypeRadio">
          <div class="flex-ac filter-select">
            <bk-select
              :clearable="false"
              v-if="isString" v-model="subFormData.params.conditions.match_type">
              <bk-option id="include" :name="$t('include(保留匹配字符串)')"></bk-option>
              <bk-option id="exclude" :name="$t('exclude(过滤匹配字符串)')" disabled>
                <span v-bk-tooltips.right="$t('正在开发中')">{{ $t('exclude(过滤匹配字符串)') }}</span>
              </bk-option>
            </bk-select>
            <bk-input
              v-show="isString"
              v-model="subFormData.params.conditions.match_content"
              style="margin-left: 8px;"></bk-input>
            <bk-select
              style="width: 320px; height: 32px"
              v-if="!isString"
              v-model="subFormData.params.conditions.separator">
              <bk-option
                v-for="(option, index) in globalsData.data_delimiter"
                :key="index"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
          <div class="tips" v-show="!isString">{{ $t('复杂的过滤条件（超过5个）会影响机器性能') }}</div>
          <div class="form-div" v-if="!isString">
            <div class="choose-table">
              <div class="choose-table-item choose-table-item-head">
                <div class="left">{{ $t('第几列') }}</div>
                <div class="main">{{ $t('等于') }}</div>
                <div class="right">{{ $t('增/删') }}</div>
              </div>
              <div class="choose-table-item-body">
                <div class="choose-table-item" v-for="(item, index) in separatorFilters" :key="index">
                  <div class="left">
                    <bk-form-item
                      label="" :rules="rules.separator_filters"
                      :property="'params.conditions.separator_filters.' + index + '.fieldindex'">
                      <bk-input style="width: 100px;" v-model="item.fieldindex"></bk-input>
                    </bk-form-item>
                  </div>
                  <div :class="['main', { line: separatorFilters.length > 1 }] ">
                    <bk-form-item
                      label="" :rules="rules.separator_filters"
                      :property="'params.conditions.separator_filters.' + index + '.word'">
                      <bk-input v-model="item.word"></bk-input>
                    </bk-form-item>
                  </div>
                  <div class="right">
                    <i class="bk-icon icon-plus-circle-yuan icons" @click="addItem"></i>
                    <i
                      :class="['bk-icon icon-minus-circle-shape icons ml9',
                               { disable: separatorFilters.length === 1 }]"
                      @click="delItem(index)">
                    </i>
                  </div>
                </div>
                <div class="choose-select" v-if="separatorFilters && separatorFilters.length > 1">
                  <bk-select class="select-div" v-model="type" @selected="changeType">
                    <bk-option id="and" :name="$t('并')"></bk-option>
                    <bk-option id="or" :name="$t('或')"></bk-option>
                  </bk-select>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
      <!-- 段日志正则调试 -->
      <div v-if="hasMultilineReg" class="multiline-log-container">
        <div class="row-container">
          <bk-form-item
            :label="$t('行首正则')"
            :rules="rules.notEmptyForm"
            required
            property="params.multiline_pattern">
            <div class="flex-ac">
              <bk-input
                data-test-id="sourceLogBox_input_beginningRegular"
                v-model.trim="subFormData.params.multiline_pattern"
              ></bk-input>
              <bk-button
                text size="small"
                class="king-button"
                data-test-id="sourceLogBox_button_debugging"
                @click="showRegDialog = true">
                {{ $t('调试') }}
              </bk-button>
            </div>
          </bk-form-item>
        </div>
        <div :class="['row-container', 'second',showType === 'horizontal' && 'pl115']">
          <i18n path="最多匹配{0}行，最大耗时{1}秒" class="i18n-style">
            <bk-form-item :rules="rules.maxLine" property="params.multiline_max_lines">
              <bk-input
                v-model="subFormData.params.multiline_max_lines"
                data-test-id="sourceLogBox_input_mostMatches"
                type="number"
                :precision="0"
                :show-controls="false">
              </bk-input>
            </bk-form-item>
            <bk-form-item :rules="rules.maxTimeout" property="params.multiline_timeout">
              <bk-input
                v-model="subFormData.params.multiline_timeout"
                data-test-id="sourceLogBox_input_maximumTimeConsuming"
                type="number"
                :precision="0"
                :show-controls="false">
              </bk-input>
            </bk-form-item>
          </i18n>
        </div>
        <multiline-reg-dialog
          :old-pattern.sync="subFormData.params.multiline_pattern"
          :show-dialog.sync="showRegDialog">
        </multiline-reg-dialog>
      </div>
    </bk-form>
  </div>
  <!-- win event日志类型 -->
  <div v-else>
    <!-- 日志种类 -->
    <bk-form
      ref="validateForm"
      :label-width="getLabelWidth"
      :form-type="showType"
      :model="subFormData"
      class="mt">
      <bk-form-item
        :label="$t('日志种类')"
        data-test-id="sourceLogBox_div_logSpecies"
        required>
        <bk-checkbox-group
          v-model="selectLogSpeciesList"
          @change="otherBlurRules">
          <div class="species-item">
            <bk-checkbox
              v-for=" (item, index) in logSpeciesList"
              :disabled="selectLogSpeciesList.length === 1 && selectLogSpeciesList[0] === item.id"
              :value="item.id"
              :key="index">
              {{item.name}}
            </bk-checkbox>
            <bk-tag-input
              v-model="otherSpeciesList"
              free-paste
              :class="otherRules ? 'tagRulesColor' : ''"
              :allow-auto-match="true"
              :has-delete-icon="true"
              :allow-create="true"
              @blur="otherBlurRules"
              @remove="otherBlurRules">
            </bk-tag-input>
          </div>
        </bk-checkbox-group>
      </bk-form-item>
    </bk-form>
    <!-- win-过滤内容 -->
    <div :class="['config-item','mt', showType === 'horizontal' && 'win-content', isEnLanguage && 'en-span']">
      <span v-bk-tooltips="$t('为减少传输和存储成本，可以过滤掉部分内容,更复杂的可在“清洗”功能中完成')">
        <span class="filter-title">{{$t('过滤内容')}}</span>
      </span>
      <div class="form-div win-filter" v-for="(item, index) in eventSettingList" :key="index">
        <bk-select
          class="select-div"
          v-model="item.type"
          :clearable="false"
          @selected="tagBlurRules(item, index)">
          <bk-option
            v-for="option in selectEventList"
            :key="option.id"
            :id="option.id"
            :disabled="option.isSelect"
            :name="option.name">
          </bk-option>
        </bk-select>
        <bk-tag-input
          class="tag-input"
          v-model="item.list"
          free-paste
          :class="item.isCorrect ? '' : 'tagRulesColor'"
          :allow-auto-match="true"
          :has-delete-icon="true"
          :allow-create="true"
          @blur="tagBlurRules(item, index)"
          @remove="tagBlurRules(item, index)">
        </bk-tag-input>
        <div class="ml9">
          <i :class="
               ['bk-icon icon-plus-circle-yuan icons',
                { disable: eventSettingList.length === selectEventList.length }]"
             @click="addWinEvent"
          ></i>
          <i
            :class="['bk-icon icon-minus-circle-shape icons ml9', { disable: eventSettingList.length === 1 }] "
            @click="delWinEvent(index)"></i>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import MultilineRegDialog from './multiline-reg-dialog';
import { mapGetters } from 'vuex';
import { deepClone } from '../../../monitor-echarts/utils';
export default {
  components: {
    MultilineRegDialog,
  },
  props: {
    showType: {
      type: String,
      default: 'horizontal',
    },
    configData: {
      type: Object,
      required: true,
    },
    scenarioId: {
      type: String,
      required: true,
    },
    currentEnvironment: {
      type: String,
      require: true,
    },
    configLength: {
      type: Number,
      require: true,
    },
    isCloneOrUpdate: {
      type: Boolean,
      require: true,
    },
  },
  data() {
    return {
      rules: {
        paths: [ // 日志路径
          {
            required: true,
            trigger: 'change',
          },
        ],
        separator_filters: [ // 分隔符过滤条件
          {
            validator: (value) => {
              const isFillOneSide = this.separatorFilters.some((item) => {
                return (item.fieldindex && !item.word) || (!item.fieldindex && item.word);
              });
              if (isFillOneSide) return Boolean(value);
              return true;
            },
            trigger: 'blur',
          },
        ],
        notEmptyForm: [ // 不能为空的表单
          {
            required: true,
            trigger: 'blur',
          },
        ],
        maxLine: [ // 最多匹配行数
          {
            validator: (val) => {
              if (val > 1000) {
                this.formData.params.multiline_max_lines = '1000';
              } else if (val < 1) {
                this.formData.params.multiline_max_lines = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
        maxTimeout: [ // 最大耗时
          {
            validator: (val) => {
              if (val > 10) {
                this.formData.params.multiline_timeout = '10';
              } else if (val < 1) {
                this.formData.params.multiline_timeout = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
      },
      subFormData: {
        data_encoding: 'UTF-8', // 日志字符集
        params: {
          multiline_pattern: '', // 行首正则, char
          multiline_max_lines: '50', // 最多匹配行数, int
          multiline_timeout: '2', // 最大耗时, int
          paths: [ // 日志路径
            { value: '' },
          ],
          conditions: {
            type: 'match', // 过滤方式类型
            match_type: 'include', // 过滤方式 可选字段 include, exclude
            match_content: '',
            separator: '|',
            separator_filters: [ // 分隔符过滤条件
              { fieldindex: '', word: '', op: '=', logic_op: 'and' },
            ],
          },
          winlog_name: [], // windows事件名称
          winlog_level: [], // windows事件等级
          winlog_event_id: [], // windows事件id
        },
      },
      type: 'and',
      showRegDialog: false, // 显示段日志调试弹窗
      otherRules: false, // 是否有其他规则
      logSpeciesList: [{
        id: 'Application',
        name: this.$t('应用程序(Application)'),
      }, {
        id: 'Security',
        name: this.$t('安全(Security)'),
      }, {
        id: 'System',
        name: this.$t('系统(System)'),
      }, {
        id: 'Other',
        name: this.$t('其他'),
      }],
      selectLogSpeciesList: ['Application', 'Security', 'System', 'Other'],
      otherSpeciesList: [],
      selectEventList: [
        {
          id: 'winlog_event_id',
          name: this.$t('事件ID'),
          isSelect: false,
        },
        {
          id: 'winlog_level',
          name: this.$t('级别'),
          isSelect: false,
        },
      ],
      eventSettingList: [
        { type: 'winlog_event_id', list: [], isCorrect: true },
      ],
      isFirst: true,
    };
  },
  computed: {
    ...mapGetters('globals', ['globalsData']),
    // 分隔符字段过滤条件
    separatorFilters() {
      const { params } = this.subFormData;
      return params.conditions.separator_filters || [{
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      }];
    },
    // 是否打开行首正则功能
    hasMultilineReg() {
      return this.scenarioId === 'section';
    },
    // 日志路径
    logPaths() {
      const { params } = this.subFormData;
      return params.paths || [];
    },
    // 是否为字符串过滤
    isString() {
      return this.subFormData.params.conditions.type === 'match';
    },
    // 是否点击过过滤内容单选框
    isClickTypeRadio() {
      return this.subFormData.params.conditions.type !== '';
    },
    // 获取label宽度
    getLabelWidth() {
      return this.showType === 'horizontal' ? 115 : 200;
    },
    // 是否是标准输出
    isStandardOutput() {
      return this.currentEnvironment === 'std_log_config';
    },
    // win日志类型是否有报错
    winCannotPass() {
      return this.eventSettingList.some(el => el.isCorrect === false) || this.otherRules;
    },
    getWinParamsData() { // wineventlog日志类型时进行params属性修改
      const winParams = {};
      const { selectLogSpeciesList, otherSpeciesList, eventSettingList } = this;
      const cloneSpeciesList = deepClone(selectLogSpeciesList);
      if (cloneSpeciesList.includes('Other')) {
        cloneSpeciesList.splice(cloneSpeciesList.indexOf('Other'), 1);
      }
      winParams.winlog_name = cloneSpeciesList.concat(otherSpeciesList);
      eventSettingList.forEach((el) => {
        winParams[el.type] = el.list;
      });
      return winParams;
    },
    isEnLanguage() {
      return this.$store.state.isEnLanguage;
    },
  },
  watch: {
    subFormData: {
      deep: true,
      handler(val) {
        const { data_encoding, params } = val;
        this.$emit('configChange', { data_encoding, params });
      },
    },
    configLength() {
      Object.assign(this.subFormData, this.configData);
    },
  },
  created() {
    Object.assign(this.subFormData, this.configData);
    if (this.isCloneOrUpdate) {
      const { params } = this.subFormData;
      // 分隔符过滤条件 and/or 初始值
      if (params.conditions?.type === 'separator') {
        this.type = params.conditions.separator_filters[0].logic_op;
      }
      if (this.scenarioId !== 'wineventlog') {
        if (params.paths.length > 0) {
          params.paths = typeof params.paths[0] === 'string' ? params.paths.map(item => ({ value: item })) : params.paths;
        } else { // 兼容原日志路径为空列表
          params.paths = [{ value: '' }];
        }
      } else {
        const otherList = params.winlog_name.filter(v => ['Application', 'Security', 'System'].indexOf(v) === -1);
        if (otherList.length > 0) {
          this.otherSpeciesList = otherList;
          this.selectLogSpeciesList = params.winlog_name.filter(v => ['Application', 'Security', 'System'].includes(v));
          this.selectLogSpeciesList.push('Other');
        } else {
          this.selectLogSpeciesList = params.winlog_name;
        }

        delete params.ignore_older;
        delete params.max_bytes;
        delete params.tail_files;

        const newEventSettingList = [];
        for (const [key, val] of Object.entries(params)) {
          if (key !== 'winlog_name' && val[0] !== '') {
            newEventSettingList.push({
              type: key,
              list: val,
              isCorrect: true,
            });
          }
        }
        if (newEventSettingList.length !== 0) {
          this.eventSettingList = newEventSettingList;
        }
        this.selectDisabledChange();
      }
    }
  },
  methods: {
    // 修改分隔符过滤的并&或
    changeType(value) {
      this.type = value;
      this.subFormData.params.conditions.separator_filters.map((item) => {
        item.logic_op = value;
      });
    },
    addLog() {
      this.subFormData.params.paths.push({ value: '' });
    },
    delLog(index) {
      if (this.subFormData.params.paths.length > 1) {
        this.subFormData.params.paths.splice(this.subFormData.params.paths.findIndex((item, ind) => ind === index), 1);
      }
    },
    chooseType(value) {
      this.subFormData.params.conditions.type = value;
      const conditions = this.subFormData.params.conditions || {};
      if (!this.isString && conditions.separator_filters.length < 1) {
        Object.assign(conditions, {
          separator_filters: [ // 分隔符过滤条件
            { fieldindex: '', word: '', op: '=', logic_op: this.type },
          ],
        });
      }
    },
    addItem() {
      this.subFormData.params.conditions.separator_filters.push({
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      });
    },
    delItem(index) {
      const { separator_filters } = this.subFormData.params.conditions;
      if (separator_filters.length > 1) {
        separator_filters.splice(separator_filters.findIndex((item, ind) => index === ind), 1);
      };
    },
    addWinEvent() {
      const eventType = this.eventSettingList.map(el => el.type);
      const selectType = this.selectEventList.map(el => el.id);
      if (eventType.length !== selectType.length) {
        const selectFilter = selectType.filter(v => eventType.indexOf(v) === -1);
        this.eventSettingList.push({ type: selectFilter[0], list: [], isCorrect: true });
        this.selectDisabledChange(true);
      }
    },
    delWinEvent(index) {
      if (this.eventSettingList.length > 1) {
        this.eventSettingList.splice(this.eventSettingList.findIndex((el, ind) => index === ind), 1);
        this.selectDisabledChange(false);
      }
    },
    selectDisabledChange(state = true) {
      if (this.eventSettingList.length === 1) {
        this.selectEventList.forEach(el => el.isSelect = false);
      }
      if (this.eventSettingList.length === this.selectEventList.length) {
        this.selectEventList.forEach(el => el.isSelect = true);
      }
      for (const eItem of this.eventSettingList) {
        for (const sItem of this.selectEventList) {
          if (eItem.type === sItem.id) {
            sItem.isSelect = state;
          }
        }
      }
    },
    otherBlurRules(input, tags) {
      if (!tags) return;
      this.otherRules = !tags.every(el => /^[a-zA-Z /]*$/.test(el));
      tags.length === 0 && (this.otherRules = false);
      const slist = this.selectLogSpeciesList;
      if (slist.length === 1 && slist[0] === 'Other' && !this.otherSpeciesList.length) {
        this.otherRules = true;
      }
    },
    tagBlurRules(item, index) {
      switch (item.type) {
        case 'winlog_event_id':
          this.eventSettingList[index].isCorrect =  item.list.every(el => /^[\d -]+$/.test(el));
          break;
        case 'winlog_level':
          this.eventSettingList[index].isCorrect =  item.list.every(el => /^[A-Za-z]+$/.test(el));
          break;
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.horizontal-item {
  padding: 20px 0;
  position: relative;
  left: 115px;
  max-width: 80%;

  > span {
    color: #90929a;
    font-size: 14px;
    position: absolute;
    left: -80px;
    top: 23px;
  }

  &.en-span span {
    left: -112px;
  }

  .filter-select {
    margin-top: 11px;
  }

  .bk-select {
    width: 184px;
    height: 32px;
  }
}

.i18n-style {
  display: flex;
  align-items: center;
}

.filter-title {
  display: inline-block;
  border-bottom: 1px dashed #000;
  margin-bottom: 8px;
}
</style>
