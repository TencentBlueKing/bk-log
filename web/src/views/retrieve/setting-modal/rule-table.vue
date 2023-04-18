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
      <p style="height: 32px">{{$t('聚类规则')}}</p>
      <div class="table-operate">
        <bk-button
          size="small"
          style="min-width: 48px"
          data-test-id="LogCluster_button_addNewRules"
          :class="globalEditable ? 'btn-hover' : ''"
          :disabled="!globalEditable"
          @click="isShowAddRule = true">
          {{$t('添加')}}
        </bk-button>
        <bk-button
          size="small"
          style="min-width: 72px"
          data-test-id="LogCluster_button_reductionRules"
          :class="globalEditable ? 'btn-hover' : ''"
          :disabled="!globalEditable"
          @click="reductionRule">
          {{$t('还原默认')}}
        </bk-button>
      </div>

      <div class="cluster-table" data-test-id="LogCluster_div_rulesTable">
        <div class="table-row flbc">
          <div class="row-left">
            <div class="row-left-index">{{$t('序号')}}</div>
            <div class="row-left-regular">{{$t('正则表达式')}}</div>
          </div>
          <div class="row-right flbc">
            <div>{{$t('占位符')}}</div>
            <div>{{$t('操作')}}</div>
          </div>
        </div>

        <div v-if="rulesList.length > 0" v-bkloading="{ isLoading: tableLoading }">
          <vue-draggable v-bind="dragOptions" v-model="rulesList">
            <transition-group>
              <li class="table-row table-row-li flbc" v-for="(item, index) in rulesList" :key="item.__Index__">
                <div class="row-left">
                  <div class="row-left-index">
                    <span class="icon log-icon icon-drag-dots"></span><span>{{index}}</span>
                  </div>
                  <div class="regular-container">
                    <register-column :context="Object.values(item)[0]" :root-margin="'-180px 0px 0px 0px'">
                      <cluster-event-popover
                        :is-cluster="false"
                        :placement="'top'"
                        @eventClick="(operation) => handleMenuClick( operation, item )">
                        <span class="row-left-regular" :style="`color:${item._isHighlight_ ? '#FE5376' : '#63656E'}`">
                          {{Object.values(item)[0]}}</span>
                      </cluster-event-popover>
                    </register-column>
                  </div>
                </div>
                <div class="row-right flbc">
                  <div><span class="row-right-item" :ref="`placeholder-${index}`">{{Object.keys(item)[0]}}</span></div>
                  <div class="rule-btn">
                    <bk-button
                      style="margin-right: 10px;" theme="primary" text
                      :disabled="!globalEditable"
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
          <empty-status empty-type="empty" :show-text="false">
            <div>{{$t('暂无聚类规则')}}</div>
          </empty-status>
        </div>
      </div>
    </div>
    <!-- 原始日志 -->
    <div class="container-item debug-container">
      <div class="debug-tool" @click="handleClickDebugButton">
        <span>{{$t('调试工具')}}</span>
        <span :class="['bk-icon','icon-angle-double-down', isClickAlertIcon ? 'bk-icon-rotate' : '']"></span>
      </div>

      <bk-alert
        v-show="isClickAlertIcon"
        class="debug-alert"
        type="warning"
        :title="$t('调试需要等待1分钟以上，在此区间不可进行其余操作')"
        closable></bk-alert>

      <div class="fl-jfsb" v-show="isClickAlertIcon">
        <p style="height: 32px">{{$t('原始日志')}}</p>
        <bk-button
          size="small"
          style="min-width: 48px"
          :class="(logOriginal !== '' && rulesList.length !== 0) ? 'btn-hover' : ''"
          :disabled="!globalEditable || logOriginal === '' || rulesList.length === 0"
          :loading="debugRequest"
          @click="debugging">
          {{$t('调试')}}
        </bk-button>
      </div>

      <div class="log-style" v-show="isClickAlertIcon">
        <bk-input
          placeholder=" "
          :disabled="!globalEditable || logOriginalRequest"
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
    <div class="container-item" v-show="isClickAlertIcon">
      <p style="height: 32px">{{$t('效果')}}</p>
      <div class="effect-container" v-bkloading="{ isLoading: debugRequest, size: 'mini' }">{{effectOriginal}}</div>
    </div>
    <!-- 添加规则dialog -->
    <bk-dialog
      width="640"
      v-model="isShowAddRule"
      ext-cls="add-rule"
      header-position="left"
      :title="isEditRules ? $t('编辑规则') : $t('添加规则')"
      :mask-close="false"
      @after-leave="cancelAddRuleContent">
      <bk-form
        ref="addRulesRef"
        form-type="vertical"
        :model="addRulesData">
        <bk-form-item
          required
          :label="$t('正则表达式')"
          :property="'regular'"
          :rules="rules.regular">
          <bk-input v-model="addRulesData.regular" style="width: 560px"></bk-input>
          <p>{{$t('样例')}}：\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}</p>
        </bk-form-item>
        <bk-form-item
          required
          :label="$t('占位符')"
          :property="'placeholder'"
          :rules="rules.placeholder">
          <bk-input v-model="addRulesData.placeholder" style="width: 560px"></bk-input>
          <p>{{$t('样例')}}：IP</p>
        </bk-form-item>
      </bk-form>
      <template slot="footer">
        <div class="flbc">
          <div class="inspection-status">
            <div class="inspection-status" v-if="isClickSubmit">
              <div>
                <bk-spin v-if="isDetection" class="spin" size="mini"></bk-spin>
                <span
                  v-else
                  :class="['bk-icon spin', isRuleCorrect ? 'icon-check-circle-shape' : 'icon-close-circle-shape']"
                  :style="`color:${isRuleCorrect ? '#45E35F' : '#FE5376'}`"></span>
              </div>
              <span style="margin-left: 24px;">{{detectionStr}}</span>
            </div>
          </div>

          <div>
            <bk-button
              theme="primary"
              :disabled="isDetection"
              @click="handleRuleSubmit">
              {{isRuleCorrect ? $t('保存') : $t('检测语法')}}</bk-button>
            <bk-button @click="isShowAddRule = false">{{$t('取消')}}</bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>
  </div>
</template>
<script>
import VueDraggable from 'vuedraggable';
import RegisterColumn from '@/views/retrieve/result-comp/register-column';
import ClusterEventPopover from '@/views/retrieve/result-table-panel/log-clustering/components/cluster-event-popover';
import { copyMessage, base64Encode, base64Decode } from '@/common/util';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    VueDraggable,
    ClusterEventPopover,
    RegisterColumn,
    EmptyStatus,
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
    cleanConfig: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      rulesList: [],
      tableLoading: false,
      logOriginal: '', // 日志源
      effectOriginal: '',
      isShowAddRule: false, // 是否展开添加规则弹窗
      isRuleCorrect: false, // 检测语法是否通过
      isEditRules: false, // 编辑聚类规则
      editRulesIndex: 0, // 当前编辑的index
      isClickSubmit: false, // 是否点击添加
      isDetection: false, // 是否在检测
      debugRequest: false, // 调试中
      detectionStr: '',
      isClickAlertIcon: false,
      addRulesData: {
        regular: '', // 添加聚类规则正则
        placeholder: '', // 添加聚类规则占位符
      },
      rules: {
        regular: [{
          validator: this.checkRegular,
          required: true,
          trigger: 'blur',
        }],
        placeholder: [{
          regex: /^(?!.*:)\S+/,
          required: true,
          trigger: 'blur',
        }],
      },
      logOriginalRequest: false, // 原始日志是否正在请求
      isFirstInitLogOrigin: false, // 是否第一次点击调试工具按钮
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
      },
    },
    addRulesData: {
      deep: true,
      handler() {
        this.resetDetection();
      },
    },
    debugRequest(val) {
      this.$emit('debugRequestChange', val);
    },
  },
  beforeDestroy() {
    this.$emit('debugRequestChange', false);
  },
  methods: {
    reductionRule() {
      const ruleArr = this.base64ToRuleArr(this.tableStr);
      if (ruleArr.length > 0) {
        this.rulesList = ruleArr;
        this.showTableLoading();
      }
    },
    clusterEdit(index) {
      const [key, val] = Object.entries(this.rulesList[index])[0];
      Object.assign(this.addRulesData, { regular: val, placeholder: key });
      this.editRulesIndex = index;
      this.isEditRules = true;
      this.isShowAddRule = true;
    },
    clusterRemove(index) {
      this.$bkInfo({
        title: this.$t('是否删除该条规则？'),
        confirmFn: () => {
          this.rulesList.splice(index, 1);
          this.showTableLoading();
        },
      });
    },
    /**
     * @desc: 添加规则dialog
     */
    handleRuleSubmit() {
      if (this.isRuleCorrect) {
        this.showTableLoading();
        const newRuleObj = {};
        const { regular, placeholder } = this.addRulesData;
        newRuleObj[placeholder] = regular;
        // 添加渲染列表时不重复的key值
        newRuleObj.__Index__ = new Date().getTime();
        if (this.isEditRules) {
          // 编辑规则替换编辑对象
          this.rulesList.splice(this.editRulesIndex, 1, newRuleObj);
        } else {
          // 检测正则和占位符是否都重复 重复则不添加
          const isRepeat = this.isRulesRepeat(newRuleObj);
          !isRepeat && this.rulesList.push(newRuleObj);
        }
        this.isShowAddRule = false;
      } else {
        // 第一次点击检查时显示文案变化
        this.isDetection = true;
        this.isClickSubmit = true;
        this.detectionStr = this.$t('检验中');
        setTimeout(() => {
          this.isDetection = false;
          this.$refs.addRulesRef.validate().then(() => {
            this.isRuleCorrect = true;
            this.detectionStr = this.$t('检验成功');
          }, () => {
            this.isRuleCorrect = false;
            this.detectionStr = this.$t('检测失败');
          });
        }, 1000);
      }
    },
    /**
     * @desc: 关闭添加规则弹窗重置参数
     */
    cancelAddRuleContent() {
      this.isRuleCorrect = false;
      this.isEditRules = false;
      this.isClickSubmit = false;
      Object.assign(this.addRulesData, { regular: '', placeholder: '' });
      this.$refs.addRulesRef.clearError();
    },
    base64ToRuleArr(str) {
      try {
        const ruleList = JSON.parse(base64Decode(str));
        const ruleNewList =  ruleList.reduce((pre, cur, index) => {
          const itemObj = {};
          const key = cur.match(/[^:]*/)[0];
          itemObj[key] = cur.split(`${key}:`)[1];
          itemObj.__Index__ = index;
          itemObj._isHighlight_ = false;
          pre.push(itemObj);
          return pre;
        }, []);
        return ruleNewList;
      } catch (e) {
        return [];
      }
    },
    ruleArrToBase64(arr = []) {
      arr.length === 0 && (arr = this.rulesList);
      try {
        const ruleNewList = arr.reduce((pre, cur) => {
          const key = Object.keys(cur)[0];
          const val = Object.values(cur)[0];
          const rulesStr = JSON.stringify(`${key}:${val}`);
          pre.push(rulesStr);
          return pre;
        }, []);
        const ruleArrStr = `[${ruleNewList.join(' ,')}]`;
        return base64Encode(ruleArrStr);
      } catch (error) {
        return '';
      }
    },
    debugging() {
      this.debugRequest = true;
      this.effectOriginal = '';
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
          const  { patterns, token_with_regex }  = res.data[0];
          this.effectOriginal = patterns[0].pattern;
          this.highlightPredefined(token_with_regex);
        })
        .finally(() => {
          this.debugRequest = false;
        });
    },
    /**
     * @desc: 调试返回值占位符和正则都匹配则高亮
     */
    highlightPredefined(tokenRegex = {}) {
      Object.entries(tokenRegex).forEach((regexItem) => {
        this.rulesList.forEach((listItem) => {
          listItem._isHighlight_ = false;
          const [regexKey, regexVal] = regexItem;
          const [listKey, listVal] =  Object.entries(listItem)[0];
          if (regexKey === listKey && regexVal === listVal) {
            listItem._isHighlight_ = true;
          }
        });
      });
    },
    /**
     * @desc: 检测规则和占位符是否重复
     * @param { Object } newRules 检测对象
     * @returns { Boolean }
     */
    isRulesRepeat(newRules = {}) {
      return this.rulesList.some((listItem) => {
        const [regexKey, regexVal] = Object.entries(newRules)[0];
        const [listKey, listVal] =  Object.entries(listItem)[0];
        return regexKey === listKey && regexVal === listVal;
      });
    },
    handleClickDebugButton() {
      this.isClickAlertIcon = !this.isClickAlertIcon;
      // 请求了一次原始日志后就不再请求
      if (!this.isFirstInitLogOrigin) {
        this.getLogOriginal();
      }
      this.isFirstInitLogOrigin = true;
    },
    /**
     * @desc: 获取原始日志内容
     */
    getLogOriginal() {
      const { extra: { collector_config_id: collectorConfigId } } = this.cleanConfig;
      if (!collectorConfigId) return;
      this.logOriginalRequest = true;
      this.$http.request('source/dataList', {
        params: {
          collector_config_id: collectorConfigId,
        },
      }).then((res) => {
        if (res.data && res.data.length) {
          const data = res.data[0];
          this.logOriginal = data.etl.data || '';
        }
      })
        .catch(() => {
        })
        .finally(() => {
          this.logOriginalRequest = false;
        });
    },
    async checkRegular(val) {
      const result = await this.checkRegularRequest(val);
      return result;
    },
    // 检测英文名是否可用
    async checkRegularRequest(val) {
      try {
        const res =  await this.$http.request('logClustering/checkRegexp', {
          data: { regexp: val },
        });
        if (res.data) {
          return res.data;
        }
      } catch (error) {
        return false;
      }
    },
    handleMenuClick(option, item) {
      copyMessage(Object.values(item)[0]);
    },
    generationUUID() {
      const tempUrl = URL.createObjectURL(new Blob());
      const uuid = tempUrl.toString();
      URL.revokeObjectURL(tempUrl);
      return uuid.substr(uuid.lastIndexOf('/') + 1);
    },
    resetDetection() {
      this.isDetection = false;
      this.isClickSubmit = false;
      this.isRuleCorrect = false;
    },
    showTableLoading() {
      this.tableLoading = true;
      setTimeout(() => {
        this.tableLoading = false;
      }, 500);
    },
  },
};
</script>
<style lang="scss" scoped>
  @import '@/scss/mixins/flex.scss';

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

    .effect-container {
      height: 100px;
      padding: 5px 10px;
      font-size: 12px;
      background: #fafbfd;
      line-height: 24px;
      color: #000;
      border: 1px solid#DCDEE5;
      border-radius: 2px;
    }

    &.debug-container {
      margin-top: -24px;

      .debug-tool {
        display: flex;
        align-items: center;
        font-size: 14px;
        margin-bottom: 4px;
        color: #3a84ff;
        cursor: pointer;

        .bk-icon {
          display: inline-block;
          font-size: 24px;
        }

        .bk-icon-rotate {
          transform: rotateZ(180deg);
        }
      }

      .debug-alert {
        margin-bottom: 8px;
      }
    }
  }

  .table-row {
    min-height: 44px;
    border-bottom: 1px solid #dcdee5;
    background-color: #fafbfd;
    font-size: 12px;

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

    &.table-row-li {
      background-color: #fff;
      transition: background .3s;

      &:hover {
        background-color: #f0f1f5;
      }
    }

    .row-left {
      display: flex;
      align-items: center;

      .row-left-index {
        width: 80px;
        margin-left: 14px;
      }

      .regular-container {
        width: 600px;
        padding: 2px 10px 2px 2px;
        word-break: break-all;

        .row-left-regular {
          cursor: pointer;
        }
      }
    }

    .row-right > div {
      width: 100px;

      .row-right-item {
        display: inline-block;
        word-break: break-all;
      }

      .bk-button-text {
        font-size: 12px;
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

    :deep(.bk-form-textarea:focus) {
      /* stylelint-disable-next-line declaration-no-important */
      background-color: #313238 !important;
      border-radius: 2px;
    }

    :deep(.bk-form-textarea[disabled]) {
      /* stylelint-disable-next-line declaration-no-important */
      background-color: #313238 !important;
      border-radius: 2px;
    }

    :deep(.bk-textarea-wrapper) {
      border: none;
    }
  }

  .add-rule {
    .bk-form {
      margin-left: 15px;
      width: 560px;

      :deep(.bk-label) {
        text-align: left;
      }
    }

    .inspection-status {
      display: flex;
      position: relative;
      font-size: 14px;

      .bk-icon {
        font-size: 18px;
      }

      .spin {
        top: 2px;
        position: absolute;
      }
    }
  }

  .flbc {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .fl-jfsb {
    @include flex-justify(space-between);
  }
</style>
