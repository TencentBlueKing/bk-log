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
  <!-- 设置-日志聚类 -->
  <div class="setting-log-cluster" v-bkloading="{ isLoading: globalLoading }">
    <bk-form
      ref="validateForm"
      form-type="vertical"
      :label-width="200"
      :model="formData">
      <!-- 聚类字段 -->
      <bk-form-item
        :label="$t('聚类字段')"
        :required="true"
        :rules="rules.clustering_fields"
        :property="'clustering_fields'">
        <div class="setting-item ">
          <bk-select
            data-test-id="LogCluster_div_selectField"
            v-model="formData.clustering_fields"
            style="width: 482px;"
            :disabled="!globalEditable"
            :clearable="false">
            <bk-option
              v-for="option in clusterField"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
          <span
            v-bk-tooltips="{
              content: $t('只能基于一个字段进行聚类，并且字段是为text的分词类型，默认为log字段'),
              placements: ['right'],
              delay: 300
            }">
            <span class="bk-icon icon-info"></span>
          </span>
        </div>
      </bk-form-item>

      <div class="setting-item ">
        <span class="left-word">{{$t('忽略数字')}}</span>
        <span style="color: #979ba5;">{{$t('前端忽略所有的数字')}}</span>
      </div>
      <div class="setting-item ">
        <span class="left-word">{{$t('忽略字符')}}</span>
        <span style="color: #979ba5;">{{$t('前端忽略数字和所有的常见符号，只保留日志具体内容')}}</span>
      </div>
      <div class="setting-item ">
        <span class="left-word">{{$t('数据指纹')}}</span>
        <div @click="handleChangeFinger">
          <span
            v-bk-tooltips="$t('暂时未开放聚类关闭功能，如有关闭需求，可联系平台管理员')"
            class="top-middle"
            :disabled="!isShowFingerTips">
            <bk-switcher
              class="left-word"
              theme="primary"
              size="large"
              v-model="fingerSwitch"
              data-test-id="LogCluster_div_isOpenSignature"
              :disabled="!globalEditable || configData.extra.signature_switch"
              :pre-check="() => false">
            </bk-switcher>
          </span>
        </div>
        <bk-alert
          style="width: 800px"
          type="info"
          :title="$t('通过AI学习能力，提取日志的数据指纹实现日志聚类，注意训练时间越久效果越好，存储将增加10%')"></bk-alert>
      </div>

      <!-- 字段长度 -->
      <div class="rule-container">
        <bk-form-item
          required
          :label="$t('最大字段长度')"
          :rules="rules.max_log_length"
          :property="'max_log_length'">
          <div class="setting-item ">
            <bk-input
              type="number"
              style="width: 94px;"
              v-model="formData.max_log_length"
              data-test-id="LogCluster_input_fieldLength"
              :min="1"
              :max="2000000"
              :precision="0"
              :disabled="!globalEditable"></bk-input>
            <span style="margin-left: 8px">{{$t('字节')}}</span>
            <span
              v-bk-tooltips="{
                content: $t('聚类字段的最大长度，如果超过这个长度将直接丢弃，设置越大将消耗更多的资源'),
                placements: ['right'],
                delay: 300
              }">
              <span class="bk-icon icon-info"></span>
            </span>
          </div>
        </bk-form-item>
        <!-- 过滤规则 -->
        <div style="margin-bottom: 40px;">
          <p style="height: 32px">{{$t('过滤规则')}}</p>
          <div class="filter-rule">
            <div class="filter-rule filter-rule-item" v-for="(item, index) of formData.filter_rules" :key="index">
              <bk-select
                class="icon-box and-or mr-neg1"
                v-if="formData.filter_rules.length !== 0 && index !== 0 && item.fields_name !== ''"
                v-model="item.logic_operator"
                :clearable="false"
                :disabled="!globalEditable">
                <bk-option
                  v-for="option in comparedList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>

              <bk-select
                v-model="item.fields_name"
                v-if="!isCloseSelect"
                :clearable="false"
                :disabled="!globalEditable"
                :popover-min-width="150"
                :class="['min-100 mr-neg1 above', item.fields_name === '' && isFieldsError ? 'rule-error' : '']"
                @change="handleFieldChange(index)"
                @blur="blurFilter">
                <bk-option
                  v-for="option in filterSelectList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
                <div slot="extension" @click="handleDeleteSelect(index)" style="cursor: pointer;">
                  <i class="bk-icon icon-close-circle"></i>{{$t('删除')}}
                </div>
              </bk-select>

              <bk-select
                v-if="item.fields_name !== ''"
                v-model="item.op"
                class="icon-box mr-neg1"
                style="color: #3a84ff;"
                :disabled="!globalEditable"
                :clearable="false"
                :popover-min-width="100">
                <bk-option
                  v-for="option in conditionList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>

              <div @click="handleInputTag(index)">
                <bk-tag-input
                  v-if="item.fields_name !== ''"
                  v-model="item.value"
                  allow-create
                  allow-auto-match
                  :placeholder="$t('请输入')"
                  :class="['mr-neg1 min-100 above', !item.value.length && isFilterRuleError ? 'rule-error' : '']"
                  :list="item.valueList"
                  :content-width="232"
                  :max-data="1"
                  @blur="handleValueBlur"
                  trigger="focus">
                </bk-tag-input>
              </div>
            </div>
            <button
              v-if="isShowAddFilterIcon"
              class="icon-box"
              :disabled="!globalEditable"
              @click="addFilterRule">
              <i class="bk-icon icon-plus-line"></i>
            </button>
          </div>
        </div>
        <!-- 聚类规则 -->
        <rule-table
          ref="ruleTableRef"
          v-on="$listeners"
          :global-editable="globalEditable"
          :table-str="defaultData.predefined_varibles"
          :default-data="defaultData"
          :clean-config="cleanConfig" />

        <bk-form-item>
          <bk-button
            theme="primary"
            data-test-id="LogCluster_button_submit"
            :title="$t('保存')"
            :disabled="!globalEditable"
            :loading="isHandle"
            @click.stop.prevent="handleSubmit">
            {{ $t('保存') }}
          </bk-button>
          <bk-button
            style="margin-left: 8px"
            data-test-id="LogCluster_button_reset"
            :disabled="!globalEditable"
            :title="$t('重置')"
            @click="resetPage">
            {{ $t('重置') }}
          </bk-button>
        </bk-form-item>
      </div>
    </bk-form>
    <!-- 保存dialog -->
    <bk-dialog
      width="360"
      v-model="isShowSubmitDialog"
      header-position="left"
      ext-cls="submit-dialog"
      :mask-close="false"
      :show-footer="false">
      <div class="submit-dialog-container">
        <p class="submit-dialog-title">{{$t('保存待生效')}}</p>
        <p class="submit-dialog-text">{{$t('该保存需要1小时生效,请耐心等待')}}</p>
        <bk-button
          theme="primary"
          class="submit-dialog-btn"
          @click="isShowSubmitDialog = false">
          {{$t('我知道了')}}</bk-button>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import RuleTable from './rule-table';

export default {
  components: {
    RuleTable,
  },
  props: {
    globalEditable: {
      type: Boolean,
      default: true,
    },
    totalFields: {
      type: Array,
      default: () => [],
    },
    indexSetItem: {
      type: Object,
      require: true,
    },
    configData: {
      type: Object,
      require: true,
    },
    cleanConfig: {
      type: Object,
      require: true,
    },
    statisticalFieldsData: { // 过滤条件字段可选值关系表
      type: Object,
      required: true,
      default: {},
    },
  },
  data() {
    return {
      clusterField: [], // 聚类字段
      globalLoading: false,
      fingerSwitch: false, // 数据指纹
      isShowAddFilterIcon: true, // 是否显示过滤规则增加按钮
      isShowSubmitDialog: false, // 是否展开保存弹窗
      isHandle: false, // 保存loading
      filterSelectList: [], // 过滤条件选项
      isFilterRuleError: false, // 过滤规则未填警告
      isFieldsError: false, // 未选过滤条件字段警告
      isCloseSelect: false, // 过滤规则下拉框隐藏
      defaultData: {},
      rules: {
        clustering_fields: [{
          required: true,
          trigger: 'blur',
        }],
        max_log_length: [{
          required: true,
          trigger: 'blur',
        }],
      },
      formData: {
        min_members: 0, // 最小日志数量
        max_dist_list: '', // 敏感度
        predefined_varibles: '', //	预先定义的正则表达式
        delimeter: '', // 分词符
        max_log_length: 1, // 最大日志长度
        is_case_sensitive: 1, // 是否大小写忽略
        clustering_fields: '', // 聚类字段
        filter_rules: [], // 过滤规则
        signature_enable: false,
      },
      conditionList: [ // 过滤条件对比
        { id: '=', name: '=' },
        { id: '!=', name: '!=' },
        { id: 'LIKE', name: 'LIKE' },
        { id: 'NOT LIKE', name: 'NOT LIKE' },
      ],
      comparedList: [
        { id: 'and', name: 'AND' },
        { id: 'or', name: 'OR' },
      ],
      operateIndex: 0, // 赋值过滤字段的操作的当前下标
      isShowFingerTips: false,
      isActive: false,
    };
  },
  watch: {
    'formData.filter_rules': {
      deep: true,
      handler(val) {
        if (val.length === 0) {
          this.isShowAddFilterIcon = true;
          return;
        }
        if ((val.slice(-1)[0].fields_name !== '' && val.length === 1) || val.slice(-1)[0].value.length > 0) {
          this.isShowAddFilterIcon = true;
        }
        if (val.slice(-1)[0].fields_name === '') {
          this.isShowAddFilterIcon = false;
        }
        this.isFilterRuleError = false;
      },
    },
  },
  mounted() {
    this.initList();
  },
  methods: {
    /**
     * @desc: 数据指纹请求
     * @param { Boolean } isDefault 是否请求默认值
     */
    async requestCluster(isDefault = false) {
      this.globalLoading = true;
      try {
        const params = { index_set_id: this.$route.params.indexId };
        const data = { collector_config_id: this.configID };
        const baseUrl = '/logClustering';
        const requestBehindUrl = isDefault ? '/getDefaultConfig' : '/getConfig';
        const requestUrl = `${baseUrl}${requestBehindUrl}`;
        const res =  await this.$http.request(requestUrl, !isDefault && { params, data });
        this.initFilterShow(res);
        const {
          collector_config_name_en,
          min_members,
          max_dist_list,
          predefined_varibles,
          delimeter,
          max_log_length,
          is_case_sensitive,
          clustering_fields,
          filter_rules,
        } = res.data;
        const assignObj = {
          collector_config_name_en,
          min_members,
          max_dist_list,
          predefined_varibles,
          delimeter,
          max_log_length,
          is_case_sensitive,
          clustering_fields,
          filter_rules,
        };
        Object.assign(this.formData, assignObj);
        Object.assign(this.defaultData, assignObj);
        // 当前回填的字段如果在聚类字段列表里找不到则赋值为空需要用户重新赋值
        const isHaveFieldsItem = this.clusterField.find(item => item.id === res.data.clustering_fields);
        if (!isHaveFieldsItem) {
          this.formData.clustering_fields = '';
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.globalLoading = false;
      }
    },
    initList() {
      const { extra, is_active: isActive } = this.configData;
      this.isActive = isActive;
      const { extra: { collector_config_id: configID } } = this.cleanConfig;
      this.configID = configID;
      this.fingerSwitch = extra.signature_switch;
      this.isShowFingerTips = extra.signature_switch;
      this.formData.clustering_fields = extra.clustering_fields;
      this.clusterField = this.totalFields
        .filter(item => item.is_analyzed)
        .map((el) => {
          const { field_name: id, field_alias: alias } = el;
          return { id, name: alias ? `${id}(${alias})` : id };
        });
      this.filterSelectList = this.totalFields
        .filter(item => !/^__dist/.test(item.field_name) && item.field_type !== '__virtual__')
        .map((el) => {
          const { field_name: id, field_alias: alias } = el;
          return { id, name: alias ? `${id}(${alias})` : id };
        });
      // 日志聚类且数据指纹同时打开则不请求默认值
      if (isActive) {
        this.requestCluster(false);
      }
    },
    /**
     * @desc: 数据指纹开关
     */
    handleChangeFinger() {
      if (!this.globalEditable) return;

      if (this.fingerSwitch) {
        this.fingerSwitch = false;
        // this.$bkInfo({
        //   title: this.$t('是否关闭数据指纹'),
        //   confirmFn: () => {
        //     this.fingerSwitch = false;
        //   },
        // });
      } else {
        // 当前如果是计算平台则直接请求 计算平台无configID
        if (this.indexSetItem.scenario_id === 'bkdata') {
          this.fingerSwitch = true;
          this.requestCluster(true);
          return;
        }
        if (!this.configID) {
          this.$bkInfo({
            title: this.$t('当前索引集为非采集项,无法设置数据指纹'),
            confirmFn: () => {},
          });
          return;
        }
        this.fingerSwitch = true;
        this.requestCluster(true);
      }
    },
    addFilterRule() {
      this.formData.filter_rules.push({
        fields_name: '', // 过滤规则字段名
        op: '=', // 过滤规则操作符号
        value: [], // 过滤规则字段值
        logic_operator: 'and',
        valueList: [],
      });
    },
    blurFilter() {
      if (this.formData.filter_rules.length > 0) {
        this.isFilterRuleError = this.formData.filter_rules.some(el => el.value.length === 0);
        this.isFieldsError = this.formData.filter_rules.some(el => el.fields_name === '');
      };
    },
    handleSubmit() {
      this.blurFilter();
      this.$refs.validateForm.validate().then(() => {
        if (this.isFilterRuleError || this.isFieldsError) return;
        this.isHandle = true;
        const { index_set_id, bk_biz_id } = this.indexSetItem;
        const {
          collector_config_name_en,
          min_members,
          max_dist_list,
          predefined_varibles,
          delimeter,
          max_log_length,
          is_case_sensitive,
          clustering_fields,
          filter_rules,
        } = this.formData;
        const paramsData = {
          collector_config_name_en,
          min_members,
          max_dist_list,
          predefined_varibles,
          delimeter,
          max_log_length,
          is_case_sensitive,
          clustering_fields,
          filter_rules,
        };
        // 获取子组件传来的聚类规则数组base64字符串
        paramsData.predefined_varibles = this.$refs.ruleTableRef.ruleArrToBase64();
        // 过滤规则数组形式转成字符串形式传参
        paramsData.filter_rules = paramsData.filter_rules.map(item => ({
          fields_name: item.fields_name,
          logic_operator: item.logic_operator,
          op: item.op,
          value: (item.value.length ? item.value[0] : ''),
        }));
        this.$http.request('/logClustering/changeConfig', {
          params: {
            index_set_id,
          },
          data: {
            ...paramsData,
            signature_enable: this.fingerSwitch,
            collector_config_id: this.configID,
            index_set_id,
            bk_biz_id,
          },
        })
          .then(() => {
            this.$emit('updateLogFields');
            this.isShowSubmitDialog = true;
          })
          .finally(() => {
            this.isHandle = false;
          });
      }, () => {});
    },
    // 字段改变
    handleFieldChange(index) {
      this.operateItemIndex = index;
      const operateItem = this.formData.filter_rules[index];
      operateItem.value = [];
      operateItem.valueList = [];
      if (operateItem.fields_name && this.statisticalFieldsData[operateItem.fields_name]) {
        const fieldValues = Object.keys(this.statisticalFieldsData[operateItem.fields_name]);
        if (fieldValues?.length) {
          operateItem.valueList = fieldValues.map(item => ({ id: item, name: item }));
        }
      }
    },
    /**
     * @desc: 赋值过滤字段的下标
     * @param { Number } index 下标
     */
    handleInputTag(index) {
      this.operateIndex = index;
    },
    handleValueBlur(val) {
      const operateItem = this.formData.filter_rules[this.operateIndex];
      if (!operateItem.value.length && val !== '') {
        operateItem.value.push(val);
      }
    },
    initFilterShow(res) {
      res.data.filter_rules = res.data.filter_rules || [];
      res.data.filter_rules.forEach((item) => {
        item.value = [item.value];
        if (JSON.stringify(this.statisticalFieldsData) === '{}') return;
        const fieldValues = Object.keys(this.statisticalFieldsData[item.fields_name]);
        item.valueList = fieldValues?.length ? fieldValues.map(item => ({ id: item, name: item })) : [] ;
      });
    },
    handleDeleteSelect(index) {
      this.formData.filter_rules.splice(index, 1);
      this.isCloseSelect = true;
      // 删除非最后一条过滤规则时隐藏下拉框
      this.$nextTick(() => {
        this.isCloseSelect = false;
      });
    },
    resetPage() {
      this.$emit('resetPage');
    },
  },
};
</script>

<style lang="scss" scoped>
  .setting-log-cluster {
    padding: 0 20px;

    .setting-item {
      display: flex;
      align-items: center;
      margin-bottom: 25px;

      .left-word {
        font-weight: 700;
        font-size: 14px;
        margin-right: 16px;
      }

      .bk-icon {
        margin-left: 8px;
        font-size: 18px;
        color: #979ba5;
      }
    }

    .filter-rule {
      display: flex;
      flex-wrap: wrap;

      .icon-box {
        min-width: 32px;
        height: 32px;
        background: #fff;
        font-size: 14px;
        line-height: 28px;
        text-align: center;
        cursor: pointer;
        border: 1px solid #c4c6cc;

        ::v-deep .bk-select-name {
          /* stylelint-disable-next-line declaration-no-important */
          padding: 0 !important;
        }

        .icon-plus-line {
          color: #3a84ff;
        }
      }
    }

    .filter-rule-item {
      margin-bottom: 6px;

      ::v-deep .bk-select-angle {
        display: none;
      }

      ::v-deep .bk-select {
        border-radius: 0;
      }

      ::v-deep .bk-form-control {
        width: 140px;
        border-radius: 0;
      }

      .and-or {
        min-width: 62px;
        font-size: 12px;
        color: #ff9c01;
      }

      .min-100 {
        min-width: 100px;
        max-height: 32px;
      }

      .mr-neg1 {
        position: relative;
        margin-right: -1px;
      }

      .above {
        z-index: 99;
      }
    }

    .rule-container {
      padding: 0 16px;
    }

    .rule-error {
      ::v-deep .bk-tag-input {
        border-color: #ff5656;
      }

      &.bk-select {
        /* stylelint-disable-next-line declaration-no-important */
        border-color: #ff5656 !important;
      }
    }
  }

  .submit-dialog {
    ::v-deep .bk-dialog-tool {
      display: none;
    }

    .submit-dialog-container {
      ::v-deep .bk-button {
        margin-left: 100px;
      }

      .submit-dialog-title {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 7px;
      }

      .submit-dialog-text {
        margin-bottom: 22px;
      }

      ::v-deep .submit-dialog-btn {
        margin-left: 224px;
      }
    }
  }
</style>
