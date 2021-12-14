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
  <div class="custom-create-container">
    <bk-form :label-width="103" :model="formData" ref="validateForm">
      <div class="create-form">
        <div class="form-title">{{$t('基础信息')}}</div>
        <!-- 数据ID -->
        <bk-form-item required :label="$t('customReport.dataID')" :property="'dataID'">
          <bk-input class="form-input" disabled v-model="formData.dataID"></bk-input>
        </bk-form-item>
        <!-- <bk-form-item :label="$t('customReport.token')" required :property="'name'">
          <bk-input class="form-input" :disabled="true" v-model="formData.name"></bk-input>
        </bk-form-item> -->
        <!-- 数据名称 -->
        <bk-form-item
          required
          :disabled="isSubmit"
          :label="$t('customReport.dataName')"
          :property="'collector_config_name'"
          :rules="baseRules.collector_config_name">
          <bk-input
            class="form-input"
            v-model="formData.collector_config_name"
            show-word-limit
            maxlength="50"></bk-input>
        </bk-form-item>
        <!-- 数据类型 -->
        <bk-form-item required :label="$t('customReport.typeOfData')" :property="'name'">
          <div style="margin-top: -4px">
            <div class="bk-button-group">
              <bk-button
                v-for=" (item,index) of globalsData.databus_custom"
                :key="index"
                :class="`${formData.custom_type === item.id ? 'is-selected' : ''}`"
                @click="handleChangeType(item.id)">
                {{item.name}}
              </bk-button>
            </div>
            <p class="group-tip" slot="tip">{{$t('customReport.typeTips')}}</p>
          </div>
        </bk-form-item>
        <bk-form-item
          required
          :label="$t('customReport.englishName')"
          :property="'collector_config_name_en'"
          :rules="baseRules.collector_config_name_en">
          <bk-input
            class="form-input"
            show-word-limit
            maxlength="50"
            v-model="formData.collector_config_name_en"
            :disabled="isSubmit"
            :placeholder="$t('dataSource.en_name_tips')"></bk-input>
        </bk-form-item>
        <!-- 数据分类 -->
        <!-- :rules="rules.category_id" -->
        <bk-form-item
          required
          :label="$t('customReport.dataClassification')"
          :property="'category_id'"
          :rules="baseRules.category_id">
          <bk-select
            style="width: 320px;"
            v-model="formData.category_id"
            :disabled="isSubmit">
            <template v-for="(item, index) in globalsData.category">
              <bk-option-group :id="item.id" :name="item.name" :key="index">
                <bk-option
                  v-for="(option, key) in item.children"
                  :key="key"
                  :id="option.id"
                  :name="`${item.name}-${option.name}`"> {{ option.name }}
                </bk-option>
              </bk-option-group>
            </template>
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.instruction')">
          <bk-input
            class="form-input"
            type="textarea"
            v-model="formData.description"
            :disabled="isSubmit"
            :placeholder="$t('customReport.notEntered')"
            :maxlength="100"></bk-input>
        </bk-form-item>
      </div>

      <div class="create-form">
        <div class="form-title">{{$t('customReport.storageSettings')}}</div>
        <!-- 数据链路 -->
        <bk-form-item
          required
          :label="$t('customReport.dataLink')"
          :rules="storageRules.data_link_id"
          :property="'data_link_id'">
          <bk-select
            style="width: 320px;"
            v-model="formData.data_link_id"
            :clearable="false"
            :disabled="isSubmit">
            <bk-option
              v-for="item in linkConfigurationList"
              :key="item.data_link_id"
              :id="item.data_link_id"
              :name="item.link_group_name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <!-- 存储集群 -->
        <bk-form-item
          required
          property="storage_cluster_id"
          :label="$t('dataSource.storage_cluster_name')"
          :rules="storageRules.cluster_id">
          <bk-select
            style="width: 320px;"
            data-test-id="storageBox_select_storageCluster"
            v-model="formData.storage_cluster_id"
            :clearable="false"
            :disabled="isSubmit"
            @selected="handleSelectStorageCluster">
            <bk-option
              v-for="(item, index) in storageList"
              class="custom-no-padding-option"
              :id="item.storage_cluster_id"
              :name="item.storage_cluster_name"
              :disabled="isItsm && curCollect.can_use_independent_es_cluster && item.registered_system === '_default'"
              :key="index">
              <div
                v-if="!(item.permission && item.permission.manage_es_source)"
                class="option-slot-container no-authority"
                @click.stop>
                <span class="text">{{item.storage_cluster_name}}</span>
                <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
              </div>
              <div v-else class="option-slot-container">
                <span v-bk-tooltips="{
                  content: $t('容量评估需要使用独立的ES集群'),
                  placement: 'right',
                  disabled: !(isItsm &&
                    curCollect.can_use_independent_es_cluster &&
                    item.registered_system === '_default')
                }">{{ item.storage_cluster_name }}</span>
              </div>
            </bk-option>
          </bk-select>
          <div class="tips_storage" v-if="formData.storage_cluster_id">
            <!-- eslint-disable-next-line vue/camelcase -->
            <div v-for="(tip, index) in tip_storage" :key="index">{{index + 1}}. {{tip}}</div>
          <!--eslint-enable-->
          </div>
        </bk-form-item>
        <!-- 索引集名称 -->
        <bk-form-item
          :label="$t('configDetails.storageIndexName')"
          class="form-inline-div"
          :rules="storageRules.table_id"
          :property="'table_id'">
          <!-- <div class="prefix">{{formData.table_id_prefix}}</div> -->
          <bk-input
            style="width: 320px"
            :placeholder="$t('dataManage.input_number')"
            disabled
            v-model="formData.collector_config_name_en"
            maxlength="50"
            minlength="5">
            <template slot="prepend">
              <div class="group-text">{{`${bkBizId}_bklog_`}}</div>
            </template>
          </bk-input>
        </bk-form-item>
        <!-- 过期时间 -->
        <bk-form-item :label="$t('configDetails.expirationTime')">
          <bk-select
            style="width: 320px;"
            v-model="formData.retention"
            :clearable="false"
            :disabled="isSubmit">
            <div slot="trigger" class="bk-select-name">
              {{ formData.retention + $t('天') }}
            </div>
            <template v-for="(option, index) in retentionDaysList">
              <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
            </template>
            <div slot="extension" style="padding: 8px 0;">
              <bk-input
                v-model="customRetentionDay"
                size="small"
                type="number"
                :placeholder="$t('输入自定义天数')"
                :show-controls="false"
                @enter="enterCustomDay($event, 'retention')"
              ></bk-input>
            </div>
          </bk-select>
        </bk-form-item>
        <!-- 副本数 -->
        <bk-form-item :label="$t('configDetails.copyNumber')">
          <bk-input
            v-model="formData.storage_replies"
            style="width:100px;"
            type="number"
            :max="3"
            :min="0"
            :precision="0"
            :clearable="false"
            :show-controls="true"
            :disabled="isSubmit"
            @blur="changeCopyNumber"
          ></bk-input>
        </bk-form-item>
        <!-- 热数据\冷热集群存储期限 -->
        <bk-form-item :label="$t('热数据')" class="hot-data-form-item">
          <bk-select
            style="width: 320px;"
            data-test-id="storageBox_select_selectHotData"
            v-model="formData.allocation_min_days"
            :clearable="false"
            :disabled="!selectedStorageCluster.enable_hot_warm || isSubmit">
            <template v-for="(option, index) in hotDataDaysList">
              <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
            </template>
            <div slot="extension" style="padding: 8px 0;">
              <bk-input
                v-model="customHotDataDay"
                size="small"
                type="number"
                data-test-id="storageBox_input_customize"
                :placeholder="$t('输入自定义天数')"
                :show-controls="false"
                @enter="enterCustomDay($event, 'hot')"
              ></bk-input>
            </div>
          </bk-select>
          <span v-if="!selectedStorageCluster.enable_hot_warm" class="disable-tips">
            {{$t('该集群未开启热数据设置')}}
            <a href="javascript:void(0);" @click="jumpToEsAccess">{{$t('前往ES源进行设置')}}</a>
          </span>
        </bk-form-item>
      </div>
    </bk-form>

    <div :class="`right-button ${isOpenWindow ? 'button-active' : ''}`"
         @click="isOpenWindow = !isOpenWindow">
      <i :class="`bk-icon icon-angle-double-${isOpenWindow ? 'right' : 'left'}`"></i>
    </div>
    <div :class="`right-window ${isOpenWindow ? 'window-active' : ''}`">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-html="customTypeIntro"></div>
    </div>

    <div class="submit-btn">
      <bk-button
        class="fl"
        theme="primary"
        :loading="isSubmit"
        @click="handleSubmitChange">
        {{$t('提交')}}
      </bk-button>
      <bk-button
        class="fr"
        theme="default"
        @click="cancel">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import storageMixin from '@/mixins/storageMixin';
export default {
  name: 'custom-report-create',
  mixins: [storageMixin],
  data() {
    return {
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      customRetentionDay: '', // 过期时间天数
      customHotDataDay: 0, // 热数据天数
      retentionDaysList: [], // 过期时间列表
      hotDataDaysList: [], // 热数据
      linkConfigurationList: [], // 数据链路
      storageList: [], // 存储集群
      selectedStorageCluster: {}, // 选择的es集群
      isOpenWindow: false, // 是否展开使用列表
      isBaseRulesValidate: false,
      isStorageRulesValidate: false,
      isSubmit: false,
      formData: {
        dataID: 1,
        collector_config_name: '',
        collector_config_name_en: '',
        custom_type: 'log',
        data_link_id: '',
        storage_cluster_id: '',
        retention: 7,
        allocation_min_days: '0',
        storage_replies: 0,
        category_id: '',
        description: '',
      },
      tip_storage: [],
      baseRules: {
        collector_config_name: [ // 采集名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
        ],
        collector_config_name_en: [ // 采集英文名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
          {
            min: 5,
            trigger: 'blur',
          },
          {
            regex: /^[A-Za-z0-9_]+$/,
            trigger: 'blur',
          },
        ],
        category_id: [ // 数据分类
          {
            required: true,
            trigger: 'blur',
          },
        ],
      },
      storageRules: {
        data_link_id: [
          {
            required: true,
            trigger: 'blur',
          },
        ],
        table_id: [
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
          {
            min: 5,
            trigger: 'blur',
          },
          {
            regex: /^[A-Za-z0-9_]+$/,
            trigger: 'blur',
          },
        ],
        cluster_id: [{
          validator(val) {
            return val !== '';
          },
          trigger: 'change',
        }],
      },
    };
  },
  computed: {
    ...mapGetters({
      projectId: 'projectId',
      bkBizId: 'bkBizId',
      globalsData: 'globals/globalsData',
    }),
    dataTypeList() {
      const { databus_custom: databusCustom } = this.globalsData;
      return databusCustom || [];
    },
    customTypeIntro() {
      const curType = this.dataTypeList.find(type => type.id === this.dataType);
      return curType ? curType.introduction : '';
    },
  },
  watch: {
  },
  mounted() {
    this.getLinkData();
    this.getStorage();
  },
  methods: {
    handleChangeType(id) {
      this.formData.custom_type = id;
    },
    handleSubmitChange() {
      this.$refs.validateForm.validate().then(() => {
        this.isSubmit = true;
        this.$http.request('custom/createCustom', {
          data: {
            ...this.formData,
            storage_replies: Number(this.formData.storage_replies),
            allocation_min_days: Number(this.formData.allocation_min_days),
            bk_biz_id: Number(this.bkBizId),
          },
        })
          .then((res) => {
            const { result } = res;
            result && this.messageSuccess(this.$t('保存成功'));
          })
          .finally(() => {
            this.isSubmit = false;
          });
      }, () => {});
    },
    // 数据链路
    async getLinkData() {
      try {
        this.tableLoading = true;
        const res = await this.$http.request('linkConfiguration/getLinkList', {
          query: {
            bk_biz_id: this.bkBizId,
          },
        });
        this.linkConfigurationList = res.data.filter(item => item.is_active);
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    cancel() {
      this.$router.back(-1);
    },
  },
};
</script>

<style lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/mixins/flex";
@import '../../../../scss/mixins/scroller';

.custom-create-container {
  padding:0 24px;
  .create-form {
    background: #fff;
    padding: 24px 37px;
    margin-top: 20px;
    border-radius: 2px;
    border: 1px solid #dcdee5;
    .form-title {
      font-size: 14px;
      color: #63656e;
      font-weight: 700;
      margin-bottom: 24px;
    }
    .form-input {
      width: 320px;
    }
    .group-tip {
      font-size: 12px;
      color: #979ba5;
    }
    .cluster-alert {
      margin-top: 20px;
      padding-top: 8px;
      width: 529px;
      height: 50px;
    }
    .tips_storage {
      width: 540px;
      background-color: rgb(239, 248, 255);
      border: 1px solid deepskyblue;
      font-size: 12px;
      padding: 10px;
      margin-top: 15px;
      div {
        line-height: 24px;
        color: #63656e;
      }
    }
    .hot-data-form-item {
      .bk-form-content {
        display: flex;
        align-items: center;
        .disable-tips {
          margin-left: 10px;
          font-size: 12px;
          color: #63656e;
          a {
            color: #3a84ff;
          }
        }
      }
    }
  }
  .right-button{
    width: 24px;
    height: 96px;
    border-radius: 8px 0 0 8px;
    border: 1px solid #dcdee5;
    border-right: none;
    background-color: #fafbfd;
    cursor: pointer;
    position: fixed;
    right: 0;
    top: calc(50vh - 48px);
    transition:right .5s;
    &.button-active{
      right: 400px;
    }
    @include flex-center;
  }
  .right-window{
    width: 400px;
    height: 100vh;
    background: #fff;
    border: 1px solid #dcdee5;
    position: fixed;
    right: -400px;
    top: 102px;
    z-index: 99;
    color: #63656e;
    transition:right .5s;
    padding: 16px 24px 0;
    &.window-active{
      right: 0;
    }
    h1 {
      font-size: 12px;
      font-weight: 700;
      margin: 26px 0 10px;
      &:first-child {
        margin-top: 0;
      }
    }
    ul {
      margin-left: 10px;
      li {
        margin-top: 8px;
        list-style: inside;
        font-size: 12px;
      }
    }
    p {
      font-size: 12px;
    }
    pre {
      margin: 0;
      margin-top: 6px;
      padding: 10px 14px;
      background: #f4f4f7;
      overflow-x: auto;
      @include scroller;
    }
  }
  .submit-btn {
    width: 140px;
    margin: 20px 20px 100px ;
    @include clearfix;
  }
}
</style>
