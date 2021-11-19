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
  <div>
    <!-- 聚类规则 -->
    <div class="container-item table-container">
      <p style="height: 32px">{{$t('retrieveSetting.clusterRule')}}</p>
      <div class="table-operate">
        <bk-button
          size="small"
          :class="globalEditable ? 'btn-hover' : ''"
          :disabled="!globalEditable"
          @click="isShowAddRule = true">
          {{$t('添加')}}
        </bk-button>
        <bk-button
          size="small"
          :class="globalEditable ? 'btn-hover' : ''"
          :disabled="!globalEditable"
          @click="reductionRule">
          {{$t('retrieveSetting.restoreDefault')}}
        </bk-button>
        <bk-button
          size="small"
          :class="globalEditable ? 'btn-hover' : ''"
          :disabled="!globalEditable"
          @click="debugging">
          {{$t('调试')}}
        </bk-button>
      </div>

      <div class="cluster-table">
        <div class="table-row flbc">
          <div class="row-left">
            <div class="row-left-index">{{$t('序号')}}</div>
            <div class="row-left-regular">{{$t('retrieveSetting.regularExpression')}}</div>
          </div>
          <div class="row-right flbc">
            <div>{{$t('retrieveSetting.placeholder')}}</div>
            <div>{{$t('retrieveSetting.operate')}}</div>
          </div>
        </div>

        <div v-if="rulesList.length > 0" v-bkloading="{ isLoading: tableLoading }">
          <vue-draggable v-bind="dragOptions" v-model="rulesList">
            <transition-group>
              <li class="table-row table-row-li flbc" v-for="(item, index) in rulesList" :key="item._index">
                <div class="row-left">
                  <div class="row-left-index">
                    <span class="icon log-icon icon-drag-dots"></span><span>{{index}}</span>
                  </div>
                  <div>
                    <bk-popover theme="light" placement="top"
                                :disabled="item._isLeftOverFlow"
                                :content="Object.values(item)[0]">
                      <p class="row-left-regular"
                         :style="`color:${item._isHighlight ? '#FE5376' : '#63656E'}`"
                         :ref="`regular-${index}`">{{Object.values(item)[0]}}</p>
                    </bk-popover>
                  </div>
                </div>
                <div class="row-right flbc">
                  <div>
                    <bk-popover theme="light" placement="top"
                                :disabled="item._isRightOverFlow"
                                :content="Object.keys(item)[0]">
                      <p class="row-right-item"
                         :ref="`placeholder-${index}`">{{Object.keys(item)[0]}}</p>
                    </bk-popover>
                  </div>
                  <div>
                    <bk-button
                      :disabled="!globalEditable" theme="primary" text style="margin-right: 10px;"
                      @click="clusterEdit(index)">
                      {{$t('编辑')}}
                    </bk-button>
                    <bk-button
                      :disabled="!globalEditable" theme="primary" text
                      @click="clusterRemove(index)">
                      {{$t('删除')}}
                    </bk-button>
                  </div>
                </div>
              </li>
            </transition-group>
          </vue-draggable>
        </div>
        <div v-else class="no-cluster-rule">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <div>{{$t('retrieveSetting.ruleEmpty')}}</div>
        </div>
      </div>
    </div>
    <!-- 原始日志 -->
    <div class="container-item">
      <p style="height: 32px">{{$t('configDetails.originalLog')}}</p>
      <div class="log-style">
        <bk-input
          placeholder=" "
          data-test-id=""
          :disabled="!globalEditable"
          :type="'textarea'"
          :rows="3"
          :input-style="{
            'background-color': '#313238',
            height: '100px',
            'line-height': '24px',
            color: '#C4C6CC',
            borderRadius: '2px'
          }"
          v-model.trim="logOriginal">
        </bk-input>
      </div>
    </div>
    <!-- 效果 -->
    <div class="container-item">
      <p style="height:32px">{{$t('retrieveSetting.effect')}}</p>
      <bk-input
        placeholder=" "
        data-test-id=""
        :disabled="!globalEditable"
        :type="'textarea'"
        :rows="3"
        :input-style="{
          'background-color': '#FAFBFD',
          height: '100px',
          'line-height': '24px',
          color: '#000000',
          borderRadius: '2px'
        }"
        v-model.trim="effectOriginal">
      </bk-input>
    </div>
    <!-- 添加规则dialog -->
    <bk-dialog
      v-model="isShowAddRule"
      ext-cls="add-rule"
      :header-position="'left'"
      :width="640"
      :title="isEditRuls ? $t('retrieveSetting.editingRules') : $t('retrieveSetting.addRule')"
      :mask-close="false"
      @after-leave="cancelAddRuleContent">
      <bk-form :label-width="200">
        <bk-form-item
          :label="$t('retrieveSetting.regularExpression')"
          :required="true"
          :property="''">
          <br>
          <bk-input
            v-model="regular"
            style="width: 560px"
            :disabled="isRuleCorrect"
            :class="`ml200 ${rules.isRegular ? '' : 'tagRulesColor'}`"
          ></bk-input>
          <p class="ml200">{{$t('retrieveSetting.sample')}}: char {#char_name#}</p>
        </bk-form-item>
        <bk-form-item
          :label="$t('retrieveSetting.placeholder')"
          :required="true"
          :property="''">
          <br>
          <bk-input
            v-model="placeholder"
            style="width: 560px"
            :disabled="isRuleCorrect"
            :class="`ml200 ${rules.isPlaceholder ? '' : 'tagRulesColor'}`"
          ></bk-input>
          <p class="ml200">{{$t('retrieveSetting.sample')}}: char {#char_name#}</p>
        </bk-form-item>
      </bk-form>
      <template slot="footer">
        <div class="flbc">
          <div class="inspection-status">
            <div class="inspection-status" v-if="isClickSubmit">
              <div>
                <bk-spin v-if="isDetection" class="spin" size="mini"></bk-spin>
                <span v-else
                      :class="['bk-icon spin', isRuleCorrect ? 'icon-check-circle-shape' : 'icon-close-circle-shape']"
                      :style="`color:${isRuleCorrect ? '#45E35F' : '#FE5376'}`"></span>
              </div>
              <span style="margin-left: 24px;">
                {{detectionStr}}
              </span>
            </div>
          </div>

          <div>
            <bk-button
              theme="primary"
              :disabled="isDetection"
              @click="handleRuleSubmit">
              {{isRuleCorrect ? $t('保存') : $t('retrieveSetting.testSyntax')}}</bk-button>
            <bk-button @click="isShowAddRule = false">{{$t('取消')}}</bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>
  </div>
</template>
<script>
import VueDraggable from 'vuedraggable';
export default {
  components: {
    VueDraggable,
  },
  props: {
    globalEditable: {
      type: Boolean,
      default: true,
    },
    defaultData: {
      type: Object,
      require: true,
    },
    tableStr: {
      type: String,
      require: true,
    },
  },
  data() {
    return {
      rulesList: [],
      tableLoading: false,
      regular: '', // 添加聚类规则正则
      placeholder: '', // 添加聚类规则占位符
      logOriginal: '', // 日志源
      effectOriginal: '',
      isShowAddRule: false, // 是否展开添加规则弹窗
      isRuleCorrect: false, // 检测语法是否通过
      isEditRuls: false, // 编辑聚类规则
      editRulsIndex: 0, // 当前编辑的index
      isClickSubmit: false, // 是否点击添加
      isDetection: false, // 是否在检测
      detectionStr: '',
      rules: {
        isRegular: true,
        isPlaceholder: true,
      },
      dragOptions: {
        animation: 150,
        tag: 'ul',
        handle: '.icon-drag-dots',
        'ghost-class': 'sortable-ghost-class',
      },
    };
  },
  watch: {
    tableStr: {
      handler(val) {
        this.rulesList = this.base64ToRuleArr(val);
        setTimeout(() => {
          this.setTableIsOverFlow(this.rulesList);
        }, 500);
      },
    },
  },
  mounted() {
  },
  methods: {
    // 还原
    reductionRule() {
      const ruleArr = this.base64ToRuleArr(this.tableStr);
      if (ruleArr.length > 0) {
        this.rulesList = ruleArr;
        this.showTableLoading();
      }
    },
    showTableLoading() {
      this.tableLoading = true;
      setTimeout(() => {
        this.tableLoading = false;
        this.setTableIsOverFlow(this.rulesList);
      }, 500);
    },
    clusterEdit(index) {
      const [key, val] = Object.entries(this.rulesList[index])[0];
      this.regular = val;
      this.placeholder = key;
      this.editRulsIndex = index;
      this.isEditRuls = true;
      this.isShowAddRule = true;
    },
    clusterRemove(index) {
      this.$bkInfo({
        title: this.$t('retrieveSetting.ruleDeleteTips'),
        confirmFn: () => {
          this.rulesList.splice(index, 1);
          this.showTableLoading();
        },
      });
    },
    // 聚类规则点击提交时检测
    handleRuleSubmit() {
      try {
        // eslint-disable-next-line no-eval
        this.rules.isRegular = eval(`/${this.regular}/`) instanceof RegExp;
      } catch (e) {
        this.rules.isRegular = false;
      }
      this.rules.isPlaceholder = /^[a-zA-z]+$/.test(this.placeholder);
      if (this.isRuleCorrect) {
        this.showTableLoading();
        const newRuleObj = {};
        newRuleObj[this.placeholder] = this.regular;
        newRuleObj._index = new Date().getTime();
        if (this.isEditRuls) {
          this.rulesList.splice(this.editRulsIndex, 1, newRuleObj);
        } else {
          this.rulesList.push(newRuleObj);
        }
        this.isShowAddRule = false;
      } else {
        this.isDetection = true;
        this.isClickSubmit = true;
        this.detectionStr = this.$t('retrieveSetting.inspection');
        setTimeout(() => {
          this.isDetection = false;
          if (this.rules.isRegular && this.rules.isPlaceholder) {
            this.isRuleCorrect = true;
            this.detectionStr = this.$t('retrieveSetting.inspectionSuccess');
          } else {
            this.isRuleCorrect = false;
            this.detectionStr = this.$t('retrieveSetting.inspectionFail');
          }
        }, 1000);
      }
    },
    cancelAddRuleContent() {
      this.regular = '';
      this.placeholder = '';
      this.isRuleCorrect = false;
      this.isEditRuls = false;
      this.isClickSubmit = false;
      this.rules.isPlaceholder = true;
      this.rules.isRegular = true;
    },
    // base64转聚类规则数组
    base64ToRuleArr(str) {
      try {
        const ruleStr =  window.atob(str);
        const ruleArr = JSON.parse(ruleStr);
        const ruleNewArr = [];
        ruleArr.forEach((el, index) => {
          const itemObj = {};
          const key = el.match(/[^:]*/)[0];
          const newReg = new RegExp(`(?<=${key}:)[^"]+`);
          let val = JSON.stringify(el.match(newReg)[0]);
          val = val.substring(1, val.length - 1);
          itemObj[key] = val;
          itemObj._index = index;
          itemObj._isLeftOverFlow = true;
          itemObj._isRightOverFlow = true;
          itemObj._isHighlight = false;
          ruleNewArr.push(itemObj);
        });
        return ruleNewArr;
      } catch (e) {
        return [];
      }
    },
    // 聚类规则数组转base64
    ruleArrToBase64(arr = []) {
      arr.length === 0 && (arr = this.rulesList);
      try {
        const ruleNewArr = [];
        arr.forEach((el) => {
          const key = Object.keys(el)[0];
          const val = Object.values(el)[0];
          ruleNewArr.push(`"${key}:${val}"`);
        });
        const ruleArrStr = `[${ruleNewArr.join(' ,')}]`;
        return window.btoa(ruleArrStr);
      } catch (error) {
        return '';
      }
    },
    setTableIsOverFlow(arr) {
      this.$nextTick(() => {
        arr.forEach((el, index) => {
          el._isLeftOverFlow = this.isOverFlow(index);
          el._isRightOverFlow = this.isOverFlow(index, 'placeholder');
        });
      });
    },
    isOverFlow(index, type = 'regular') {
      return this.$refs[`${type}-${index}`][0]?.offsetWidth >= this.$refs[`${type}-${index}`][0]?.scrollWidth;
    },
    debugging() {
      this.tableLoading = true;
      const inputData = {
        dtEventTimeStamp: Date.parse(new Date()) / 1000,
        log: this.logOriginal,
        uuid: this.generationUUID(),
      };
      const { min_members, delimeter, max_log_length, is_case_sensitive } = this.defaultData;
      const predefinedVaribles = this.ruleArrToBase64(this.rulesList);
      const query = {
        min_members,
        delimeter,
        max_log_length,
        is_case_sensitive,
        input_data: [inputData],
        max_dist_list: 0.5,
        predefined_varibles: predefinedVaribles,
      };
      this.$http.request('/logClustering/preview', { data: { ...query } })
        .then((res) => {
          const { data: { patterns, token_with_regex } } = res;
          this.effectOriginal = patterns[0].pattern;
          this.highlightPredefined(token_with_regex);
        })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.tableLoading = false;
        });
    },
    highlightPredefined(tokenRegex = {}) {
      tokenRegex && Object.entries(tokenRegex).forEach((regexItem) => {
        this.rulesList.forEach((listItem) => {
          const [regexKey, regexVal] = regexItem;
          const [listKey, listVal] =  Object.entries(listItem)[0];
          if (regexKey === listKey && regexVal === JSON.parse(`"${listVal}"`)) {
            listItem._isHighlight = true;
          }
        });
      });
    },
    generationUUID() {
      const tempUrl = URL.createObjectURL(new Blob());
      const uuid = tempUrl.toString();
      URL.revokeObjectURL(tempUrl);
      return uuid.substr(uuid.lastIndexOf('/') + 1);
    },
  },
};
</script>
<style lang="scss" scoped>

  .container-item {
    margin-bottom: 40px;

    &.table-container {
      position: relative;
    }

    .cluster-table {
      border: 1px solid #dcdee5;
      border-bottom: none;
      border-radius: 2px;
    }
  }

  .table-row {
    height: 44px;
    border-bottom: 1px solid #dcdee5;
    background-color: #fafbfd;
    .icon {
      margin: 0 10px 0 4px;
    }

    .icon-drag-dots {
      width: 16px;
      text-align: left;
      font-size: 14px;
      color: #979ba5;
      cursor: move;
      opacity: 0;
      transition: opacity 0.2s linear;
    }
    &.sortable-ghost-class {
      background: #eaf3ff;
      transition: background 0.2s linear;
    }

    &:hover {
      background: #eaf3ff;
      transition: background 0.2s linear;

      .icon-drag-dots {
        opacity: 1;
        transition: opacity 0.2s linear;
      }
    }

    &.table-row-li {
      background-color: #ffffff;
      transition: background 0.3s;

      &:hover {
        background-color: #f0f1f5;
      }
    }

    .row-left {
      display: flex;

      .row-left-index {
        width: 120px;
        margin-left: 14px;
      }

      .row-left-regular {
        width: 600px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        cursor: pointer;
      }
    }

    .row-right > div {
      width: 150px;
      .row-right-item {
        width: 130px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        cursor: pointer;
      }
    }
  }

  .table-operate {
    position: absolute;
    right: 0;
    top: 0;

    .bk-button {
      border-radius: 3px;
      margin-left: 2px;
      padding: 0;
    }

    .btn-hover {
      &:hover {
        color: #3a84ff;
        border: 1px solid #3a84ff;
      }
    }
  }

  .no-cluster-rule {
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border-bottom: 1px solid #dcdee5;
    .icon-empty {
      color: #c3cdd7;
      font-size: 80px;
    }
  }

  .log-style {
    height: 100px;

    /deep/.bk-form-textarea:focus {
      background-color: #313238 !important;
      border-radius: 2px;
    }
    /deep/.bk-form-textarea[disabled] {
      background-color: #313238 !important;
      border-radius: 2px;
    }
    /deep/.bk-textarea-wrapper {
      border: none;
    }
  }

  .add-rule {
    .bk-form {
      margin-left: 15px;
      width: 560px;
      /deep/.bk-label {
        text-align: left;
      }
    }
    .inspection-status {
      display: flex;
      position: relative;
      .bk-icon {
        font-size: 18px;
      }
      .spin {
        top: 2px;
        position: absolute;
      }
      font-size: 14px;
    }
  }

  .ml200 {
    margin-left: -200px;
  }

  .tagRulesColor {
    /deep/.bk-form-input {
      border-color: #ff5656 !important;
    }
  }

  .flbc {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

</style>
