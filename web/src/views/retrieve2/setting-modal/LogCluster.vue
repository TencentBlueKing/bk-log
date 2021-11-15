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
    <bk-form :label-width="200">
      <!-- 聚类字段 -->
      <bk-form-item
        :label="$t('retrieveSetting.clusterField')"
        :required="true"
        :property="''">
        <br>
        <div class="form-item">
          <bk-select
            v-model="formData.clustering_fields" class="ml200" style="width: 482px;" :disabled="!globalEditable">
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
              class="ml200"
              type="number"
              style="width: 94px; overflow: hidden;"
              v-model="formData.max_log_length"
              :min="1"
              :max="2000000"
              :precision="0"
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
            <div class="filter-rule filter-rule-item" v-for="(item, index) of formData.filter_rules" :key="index">
              <bk-select
                class="icon-box and-or mr-neg1"
                v-if="formData.filter_rules.length !== 0 && index !== 0 && item.fields_name !== ''"
                :clearable="false"
                v-model="item.logic_operator"
                :disabled="!globalEditable">
                <bk-option v-for="option in comparedList"
                           :key="option.id"
                           :id="option.id"
                           :name="option.name">
                </bk-option>
              </bk-select>

              <bk-select
                class="min-100 mr-neg1"
                v-model="item.fields_name"
                :clearable="false"
                :disabled="!globalEditable"
                :popover-min-width="150">
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
                v-if="item.fields_name !== ''"
                v-model="item.op"
                placeholder=" "
                class="icon-box mr-neg1"
                style="color: #3A84FF;"
                :disabled="!globalEditable"
                :clearable="false"
                :popover-min-width="60">
                <bk-option v-for="option in conditionList"
                           :key="option.id"
                           :id="option.id"
                           :name="option.name">
                </bk-option>
              </bk-select>

              <bk-input
                v-if="item.fields_name !== ''"
                v-model="item.value"
                class="mr-neg1"
                placeholder=" "
                :disabled="!globalEditable">
              </bk-input>
            </div>
            <button v-if="isShowAddFilterIcon"
                    class="icon-box"
                    :disabled="!globalEditable"
                    @click="addFilterRule">
              <i class="bk-icon icon-plus-line"></i>
            </button>
          </div>
        </div>
        <!-- 聚类规则 -->
        <RuleTable
          ref="ruleTableRef"
          :global-editable="globalEditable"
          :table-str="formData.predefined_varibles"
          :default-data="defaultData" />

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
            @click="resetPage">
            {{ $t('dataManage.Reset') }}
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
      :show-footer="false">
      <div class="submit-dialog-container">
        <p class="submit-dialog-title">{{$t('retrieveSetting.saveToTakeEffect')}}</p>
        <p class="submit-dialog-text">该保存需要**时候生效,请耐心等待</p>
        <bk-button
          theme="primary"
          class="submit-dialog-btn"
          @click="isShowSubmitDialog = false">
          {{$t('retrieveSetting.iSee')}}</bk-button>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import RuleTable from './RuleTable';

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
      default: () => {},
    },
  },
  data() {
    return {
      clusterField: [], // 聚类字段
      globalLoading: true,
      formData: {
        min_members: '', // 最小日志数量
        max_dist_list: '', // 敏感度
        predefined_varibles: '', //	预先定义的正则表达式
        delimeter: '', // 分词符
        max_log_length: 1, // 最大日志长度
        is_case_sensitive: 1, // 是否大小写忽略
        clustering_fields: '', // 聚合字段
        filter_rules: [],
      },
      defaultData: {},
      dataFingerprint: true, // 数据指纹
      isShowAddFilterIcon: true, // 是否显示过滤规则增加按钮
      isShowSubmitDialog: false, // 是否展开保存弹窗
      isHandle: false, // 保存loading
      filterSelectList: [], // 过滤条件选项
      conditionList: [ // 过滤条件对比
        { id: '=', name: '=' },
        { id: '!=', name: '!=' },
      ],
      comparedList: [
        { id: 'and', name: 'AND' },
        { id: 'or', name: 'OR' },
      ],
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
        if (val.slice(-1)[0].fields_name !== '' && val.length === 1) {
          this.isShowAddFilterIcon = true;
        }
        if (val.slice(-1)[0].fields_name === '') {
          this.isShowAddFilterIcon = false;
        }
        if (val.slice(-1)[0].value.length > 0) {
          this.isShowAddFilterIcon = true;
        }
      },
    },
  },
  mounted() {
    this.initPage();
    this.initSelectList();
  },
  methods: {
    async initPage() {
      try {
        const res = await this.$http.request('/logClustering/getConfig', {
          params: {
            index_set_id: this.$route.params.indexId,
          },
        });
        Object.assign(this.formData, res.data);
        this.defaultData = res.data;
        this.globalLoading = false;
      } catch (error) {
        this.$http.request('/logClustering/getDefaultConfig')
          .then((res) => {
            Object.assign(this.formData, res.data);
            this.defaultData = res.data;
          })
          .catch((e) => {
            console.warn(e);
          })
          .finally(() => {
            this.globalLoading = false;
          });
      }
    },
    // 获取下拉框元素
    initSelectList() {
      this.clusterField = this.totalFields.filter(fitem => fitem.is_analyzed)
        .map((el) => {
          const item = {};
          item.name = el.field_name;
          item.id = el.field_name;
          return item;
        },
        );
      this.filterSelectList = this.totalFields.map((el) => {
        const item = {};
        item.id = el.field_name;
        item.name = el.field_name;
        return item;
      });
    },
    addFilterRule() {
      this.formData.filter_rules.push({
        fields_name: '', // 过滤规则字段名
        op: '=', // 过滤规则操作符号
        value: '', // 过滤规则字段值
        logic_operator: 'and',
      });
    },
    handleSubmit() {
      this.isHandle = true;
      this.isShowSubmitDialog = true;
      const {
        collector_config_id,
        collector_config_name_en,
        index_set_id,
        bk_biz_id,
      } = this.indexSetItem;
      this.formData.predefined_varibles =  this.$refs.ruleTableRef.ruleArrToBase64();
      this.$http.request('/logClustering/changeConfig', {
        params: {
          index_set_id,
        },
        data: {
          ...this.formData,
          collector_config_id,
          collector_config_name_en,
          index_set_id,
          bk_biz_id },
      })
        .then(() => {
          this.isShowSubmitDialog = true;
        })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.isHandle = false;
        });
    },
    handleDeleteSelect(index) {
      this.formData.filter_rules.splice(index, 1);
    },
    resetPage() {
      this.$emit('reset-page');
    },
  },
};
</script>

<style lang="scss" scoped>

  /deep/ .bk-label {
    text-align: left;
  }
  .setting-log-cluster {
    padding: 0 20px;
  }
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
  .filter-rule {
    display: flex;
    flex-wrap: wrap;
    .icon-box {
      min-width: 32px;
      height: 32px;
      background: #FFFFFF;
      /deep/.bk-select-name {
        padding: 0 !important;
      }
      font-size: 14px;
      line-height: 28px;
      text-align: center;
      cursor: pointer;
      border: 1px solid #c4c6cc;
    }
  }
  .filter-rule-item {
    margin-bottom: 6px;
    /deep/.bk-select-angle {
      display: none;
    }
    /deep/.bk-select {
      border-radius: 0;
    }
    /deep/.bk-form-control {
      width: 100px;
      border-radius: 0;
    }
    .and-or {
      min-width: 62px;
      color: #ff9c01;
      font-size: 12px;
    }
    .min-100 {
      min-width: 100px;
    }
    .mr-neg1 {
      margin-right: -1px;
    }
  }
  .rule-container {
    padding: 0 16px;
  }
  .submit-dialog {
    /deep/.bk-dialog-tool {
      display: none;
    }

    .submit-dialog-container {
      /deep/ .bk-button {
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
      /deep/.submit-dialog-btn {
        margin-left: 224px;
      }
    }
  }

  .container-item {
    margin-bottom: 40px;
  }

  .submit-button {
    margin: 40px 0 40px -200px;
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
