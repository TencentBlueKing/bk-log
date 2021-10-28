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
  <div class="setting-log-cluster">
    <bk-form :label-width="200">
      <!-- 聚类字段 -->
      <bk-form-item
        :label="$t('retrieveSetting.clusterField')"
        :required="true"
        :property="''">
        <br>
        <div class="form-item">
          <bk-select v-model="value" class="ml200" style="width: 482px;" :disabled="!globalEditable">
            <bk-option v-for="option in clusterField"
                       :key="option.id"
                       :id="option.id"
                       :name="option.name">
            </bk-option>
          </bk-select>
          <span
            v-bk-tooltips="{
              content: '提示信息1',
              placements: ['right'],
              delay: 300
            }">
            <span class="bk-icon icon-info"></span>
          </span>
        </div>
      </bk-form-item>

      <div class="form-item">
        <span class="left-word">{{$t('retrieveSetting.ignoreNumbers')}}</span>
        <span style="color:#979BA5">说明文字说明文字说明文字说明文字说明文字</span>
      </div>
      <div class="form-item">
        <span class="left-word">{{$t('retrieveSetting.ignoreCharacters')}}</span>
        <span style="color:#979BA5">说明文字说明文字说明文字说明文字说明文字</span>
      </div>
      <div class="form-item">
        <span class="left-word">{{$t('retrieveSetting.dataFingerprint')}}</span>
        <bk-switcher
          class="left-word" theme="primary" size="large"
          v-model="dataFingerprint"
          :disabled="!globalEditable">
        </bk-switcher>
        <bk-alert style="width: 780px" type="info" :title="$t('retrieveSetting.clusterPrompt')"></bk-alert>
      </div>
      <!-- 字段长度 -->
      <div class="rule-container">
        <bk-form-item
          :label="$t('retrieveSetting.fieldLength')"
          :required="true"
          :property="''">
          <br>
          <div class="form-item">
            <bk-input
              class="ml200" type="number" style="width: 94px; overflow: hidden;"
              v-model="value"
              :disabled="!globalEditable"></bk-input>
            <span style="margin-left: 8px">{{$t('retrieveSetting.byte')}}</span>
            <span
              v-bk-tooltips="{
                content: '提示信息2',
                placements: ['right'],
                delay: 300
              }">
              <span class="bk-icon icon-info"></span>
            </span>
          </div>
        </bk-form-item>
        <!-- 过滤规则 -->
        <div class="container-item">
          <p style="height: 32px">{{$t('retrieveSetting.filtrationRule')}}</p>
          <div class="filter-rule">
            <div class="filter-rule filter-rule-item" v-for="(item, index) of filterList" :key="index">
              <bk-select
                class="icon-box and-or mr-neg1"
                v-if="filterList.length !== 0 && index !== 0 && item.select !== ''"
                :clearable="false"
                :disabled="!globalEditable"
                v-model="item.compared"
                placeholder=" ">
                <bk-option v-for="option in comparedList"
                           :key="option.id"
                           :id="option.id"
                           :name="option.name">
                </bk-option>
              </bk-select>

              <bk-select
                class="min-100 mr-neg1"
                :clearable="false"
                :disabled="!globalEditable"
                v-model="item.select">
                <bk-option v-for="option in filterSelectList"
                           :key="option.id"
                           :id="option.id"
                           :name="option.name">
                </bk-option>
                <div slot="extension" @click="handleDeleteSelect(index)" style="cursor: pointer;">
                  <i class="bk-icon icon-close-circle"></i>{{$t('删除')}}
                </div>
              </bk-select>

              <bk-select
                v-if="item.select !== ''"
                class="icon-box mr-neg1"
                style="color: #3A84FF;"
                :disabled="!globalEditable"
                :clearable="false"
                :popover-min-width="120"
                v-model="item.condition"
                placeholder=" ">
                <bk-option v-for="option in conditionList"
                           :key="option.id"
                           :id="option.id"
                           :name="option.name">
                </bk-option>
              </bk-select>

              <bk-tag-input
                class="min-100 mr-neg1"
                v-if="item.select !== ''"
                v-model="item.inputList"
                placeholder=" "
                :disabled="!globalEditable"
                :list="inputSelectList"
                :trigger="'focus'"
                :allow-create="true"
                :allow-auto-match="true"
                :has-delete-icon="true">
              </bk-tag-input>
            </div>
            <div v-if="isShowAddFilterIcon"
                 class="icon-box"
                 @click="addFilterRule">
              <i class="bk-icon icon-plus-line"></i>
            </div>
          </div>
        </div>
        <!-- 聚类规则 -->
        <div class="container-item table-container">
          <p style="height: 32px">{{$t('retrieveSetting.clusterRule')}}</p>
          <div class="table-operate">
            <bk-button
              size="small"
              :class="globalEditable ? 'btn-hover' : ''"
              :disabled="!globalEditable"
              @click="addRule">
              {{$t('添加')}}
            </bk-button>
            <bk-button
              size="small"
              :class="globalEditable ? 'btn-hover' : ''"
              :disabled="!globalEditable">
              {{$t('retrieveSetting.restoreDefault')}}
            </bk-button>
            <bk-button
              size="small"
              :class="globalEditable ? 'btn-hover' : ''"
              :disabled="!globalEditable">
              {{$t('调试')}}
            </bk-button>
          </div>

          <div class="cluster-table">
            <div class="table-row flbc">
              <div class="row-left">
                <div>{{$t('序号')}}</div>
                <div>{{$t('retrieveSetting.regularExpression')}}</div>
              </div>
              <div class="row-right flbc">
                <div>{{$t('retrieveSetting.placeholder')}}</div>
                <div>{{$t('retrieveSetting.operate')}}</div>
              </div>
            </div>

            <div v-if="tableData.length > 0">
              <vue-draggable v-bind="dragOptions" v-model="tableData">
                <transition-group>
                  <li class="table-row table-row-li flbc" v-for="(item, index) in tableData" :key="item.index">
                    <div class="row-left">
                      <div><span class="icon log-icon icon-drag-dots"></span><span>{{item.index}}</span></div>
                      <div>{{item.regular}}</div>
                    </div>
                    <div class="row-right flbc">
                      <div>{{item.placeholder}}</div>
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
            <div v-else class="table-row">
              <div>暂无聚类规则</div>
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
            :disabled="true"
            :type="'textarea'"
            :rows="3"
            :input-style="{
              'background-color': '#FAFBFD',
              height: '100px',
              'line-height': '24px',
              color: '#000000',
              borderRadius: '2px'
            }"
            v-model.trim="logOriginal">
          </bk-input>
        </div>
      </div>

      <bk-form-item class="submit-button">
        <bk-button
          theme="primary"
          :title="$t('保存')"
          :disabled="!globalEditable"
          :loading="isHandle"
          @click.stop.prevent="handleSubmit">
          {{ $t('保存') }}
        </bk-button>
        <bk-button
          theme="default"
          :disabled="!globalEditable"
          :title="$t('dataManage.Reset')"
          @click="cancel">
          {{ $t('dataManage.Reset') }}
        </bk-button>
      </bk-form-item>
    </bk-form>

    <bk-dialog
      v-model="isShowAddRule"
      :header-position="addRuleConfigure.position"
      :width="addRuleConfigure.width"
      :title="isEditRuls ? $t('retrieveSetting.editingRules') : $t('retrieveSetting.addRule')"
      :mask-close="false"
      @after-leave="isEditRuls = false;dealyShowCheck = false;isClickSubmit = false"
      ext-cls="add-rule">
      <bk-form :label-width="200">
        <bk-form-item
          :label="$t('retrieveSetting.regularExpression')"
          :required="true"
          :property="''">
          <br>
          <bk-input v-model="regular" class="ml200" style="width: 560px"></bk-input>
          <p class="ml200">{{$t('retrieveSetting.sample')}}: char {#char_name#}</p>
        </bk-form-item>
        <bk-form-item
          :label="$t('retrieveSetting.placeholder')"
          :required="true"
          :property="''">
          <br>
          <bk-input v-model="placeholder" class="ml200" style="width: 560px"></bk-input>
          <p class="ml200">{{$t('retrieveSetting.sample')}}: char {#char_name#}</p>
        </bk-form-item>
      </bk-form>
      <template slot="footer">
        <div class="flbc">
          <div class="inspection-status">
            <div style="margin-right: 25px">
              <bk-spin class="absl" v-if="isShowSpin" size="mini"></bk-spin>
              <span v-if="dealyShowCheck" class="bk-icon icon-check-circle-shape absl" style="color: #45E35F;"></span>
            </div>
            <span v-if="isClickSubmit">
              {{addRuleConfigure.isDetection ?
                $t('retrieveSetting.inspection') : $t('retrieveSetting.inspectionSuccess')}}
            </span>
          </div>
          <div>
            <bk-button
              theme="primary"
              :disabled="addRuleConfigure.isDetection"
              @click="handleRuleSubmit">
              {{isRuleCorrect ? $t('保存') : $t('retrieveSetting.testSyntax')}}</bk-button>
            <bk-button @click="handleRuleCancel">{{$t('取消')}}</bk-button>
          </div>
        </div>
      </template>
    </bk-dialog>

    <bk-dialog
      width="360"
      v-model="isShowSubmitDialog"
      header-position="left"
      ext-cls="submit-dialog"
      :show-footer="false">
      <div class="submit-dialog-container">
        <p class="submit-dialog-title">{{$t('retrieveSetting.saveToTakeEffect')}}</p>
        <p class="submit-dialog-text">该保存需要**时候生效,请耐心等待</p>
        <bk-button
          theme="primary"
          class="submit-dialog-btn"
          @click="handleRuleCancel">
          {{$t('retrieveSetting.iSee')}}</bk-button>
      </div>
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
  },
  data() {
    return {
      clusterField: [], // 聚类字段
      tableData: [{
        index: 0,
        regular: '11111111111111111111111111111111111111',
        placeholder: 1,
      }],
      filterList: [], // 过滤条件数组
      filterSelectList: [
        { id: '1', name: '日志路径' },
        { id: '2', name: 'gse索引' },
        { id: '3', name: '云区域ID' },
      ],
      conditionList: [
        { id: '>', name: '>' },
        { id: '<', name: '<' },
        { id: '=', name: '=' },
      ],
      comparedList: [
        { id: 'AND', name: 'AND' },
        { id: 'OR', name: 'OR' },
      ],
      inputSelectList: [
        { id: '1', name: 'AND' },
        { id: '2', name: 'OR' },
      ],
      regular: '', // 添加聚类规则正则
      placeholder: '', // 添加聚类规则占位符
      formData: {},
      logOriginal: '', // 日志源
      rules: {},
      dataFingerprint: true, // 数据指纹
      value: '',
      isHandle: false,
      isShowAddRule: false, // 是否展开添加规则弹窗
      isShowSubmitDialog: false, // 保存弹窗
      isRuleCorrect: false, // 检测语法
      isShowAddFilterIcon: true, // 是否显示过滤规则增加按钮
      isEditRuls: false, // 是否编辑聚类规则
      isShowSpin: false,
      dealyShowCheck: false,
      isClickSubmit: false,
      addRuleConfigure: {
        width: 640,
        position: 'left',
        isDetection: false,
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
    filterList: {
      deep: true,
      handler(val) {
        if (val.length === 0) {
          this.isShowAddFilterIcon = true;
        }
        if (val.slice(-1)[0].select !== '' && val.length === 1) {
          this.isShowAddFilterIcon = true;
        }
        if (val.slice(-1)[0].select === '') {
          this.isShowAddFilterIcon = false;
        }
        if (val.slice(-1)[0].inputList.length > 0) {
          this.isShowAddFilterIcon = true;
        }
      },
    },
  },
  methods: {
    handleSubmit() {
      this.isShowSubmitDialog = true;
    },
    cancel() {},
    addFilterRule() {
      this.filterList.push({
        select: '',
        compared: 'AND',
        condition: '=',
        inputList: [],
      });
    },
    addRule() {
      this.isShowAddRule = true;
    },
    clusterEdit() {
      this.isEditRuls = true;
      this.isShowAddRule = true;
    },
    clusterRemove(index) {
      this.tableData.splice(index, 1);
    },
    handleDeleteSelect(index) {
      this.filterList.splice(index, 1);
    },
    handleRuleSubmit() {
      if (this.isRuleCorrect) {
        this.tableData.push({
          index: this.tableData.length,
          regular: this.regular,
          placeholder: this.placeholder,
        });
        this.isShowAddRule = false;
        setTimeout(() => {
          this.regular = '';
          this.placeholder = '';
          this.isRuleCorrect = false;
        }, 300);
      } else {
        this.addRuleConfigure.isDetection = true;
        this.isShowSpin = true;
        this.isClickSubmit = true;
        setTimeout(() => {
          this.addRuleConfigure.isDetection = false;
          this.isRuleCorrect = true;
          this.isShowSpin = false;
          this.dealyShowCheck = true;
        }, 2000);
      }
    },
    handleRuleCancel() {
      this.isShowAddRule = false;
    },
  },
};
</script>

<style lang="scss" scoped>
/deep/ .bk-label {
  text-align: left;
}
// .setting-log-cluster {}
.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 25px;

  .left-word {
    font-weight: 700;
    font-size: 15px;
    margin-right: 16px;
  }

  .bk-icon {
    margin-left: 8px;
    font-size: 18px;
    color: #979ba5;
  }
}

.rule-container {
  padding: 0 16px;

  .container-item {
    margin-bottom: 40px;

    &.table-container{
      position: relative;
    }

    .cluster-table {
      border: 1px solid #dcdee5;
      border-bottom: none;
      border-radius: 2px;
    }
  }

  .filter-rule{
    display: flex;
    flex-wrap: wrap;
    .icon-box{
      min-width: 32px;
      height: 32px;
      /deep/.bk-select-name{
        padding: 0 !important;
      }
      font-size: 14px;
      line-height: 30px;
      text-align: center;
      cursor: pointer;
      border:1px solid #C4C6CC;
    }
  }
  .filter-rule-item{
    margin-bottom: 6px;
    /deep/.bk-select-angle{
      display: none;
    }
    /deep/.bk-select{
      border-radius: 0;
    }
    /deep/.bk-tag-input{
      border-radius: 0;
    }
    .and-or{
      min-width: 62px;
      color: #FF9C01;
      font-size: 12px;
    }
    .min-100{
      min-width: 100px;
    }
    .mr-neg1{
      margin-right: -1px;
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
      overflow: hidden;

      > :first-child {
        width: 120px;
        margin-left: 14px;
      }

      > :last-child {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .row-right > div {
      width: 150px;
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
      &:hover{
        color: #3a84ff;
        border: 1px solid #3a84ff;
      }
    }
  }
}

.log-style {
  height: 100px;

  /deep/.bk-form-textarea:focus {
    background-color: #313238 !important;
    border-radius: 2px;
  }
  /deep/.bk-form-textarea[disabled]{
     background-color: #313238 !important;
    border-radius: 2px;
  }
  /deep/.bk-textarea-wrapper {
    border: none;
  }
}

.submit-button {
  margin: 40px 0 40px -200px;
}

.add-rule {
  .bk-form {
    margin-left: 15px;
    width: 560px;
  }
  .inspection-status{
    display: flex;
    position: relative;
    .bk-icon{
      font-size: 18px;
    }
    .absl{
      top: 2px;
      position: absolute;
    }
    font-size: 14px;
  }
}

.submit-dialog{
  /deep/.bk-dialog-tool{
    display: none;
  }

  .submit-dialog-container{
    /deep/ .bk-button{
      margin-left: 100px;
    }
    .submit-dialog-title{
      font-weight: 700;
      font-size: 16px;
      margin-bottom: 7px;
    }
    .submit-dialog-text{
      margin-bottom: 22px;
    }
    /deep/.submit-dialog-btn{
      margin-left: 224px;
    }
  }
}

.ml200 {
  margin-left: -200px;
}

.flbc {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

</style>
