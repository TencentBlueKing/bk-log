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
  <div
    data-test-id="custom_div_addNewCustomBox"
    v-bkloading="{ isLoading: containerLoading }"
    :class="`custom-create-container ${isOpenWindow ? 'is-active-details' : ''}`">
    <bk-form :label-width="103" :model="formData" ref="validateForm">
      <div class="create-form">
        <div class="form-title">{{$t('基础信息')}}</div>
        <!-- 数据ID -->
        <bk-form-item required :label="$t('customReport.dataID')" :property="'bk_data_id'" v-if="isEdit">
          <bk-input class="form-input" disabled v-model="formData.bk_data_id"></bk-input>
        </bk-form-item>
        <!-- <bk-form-item :label="$t('customReport.token')" required :property="'name'">
          <bk-input class="form-input" :disabled="true" v-model="formData.name"></bk-input>
        </bk-form-item> -->
        <!-- 数据名称 -->
        <bk-form-item
          required
          :disabled="submitLoading"
          :label="$t('customReport.dataName')"
          :property="'collector_config_name'"
          :rules="baseRules.collector_config_name">
          <bk-input
            class="form-input"
            data-test-id="addNewCustomBox_input_dataName"
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
                :data-test-id="`addNewCustomBox_button_typeTo${item.id}`"
                :class="`${formData.custom_type === item.id ? 'is-selected' : ''}`"
                :disabled="isEdit"
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
            data-test-id="addNewCustomBox_input_englishName"
            v-model="formData.collector_config_name_en"
            :disabled="submitLoading || isEdit"
            :placeholder="$t('dataSource.en_name_tips')"></bk-input>
        </bk-form-item>
        <!-- 数据分类 -->
        <bk-form-item
          required
          :label="$t('customReport.dataClassification')"
          :property="'category_id'"
          :rules="baseRules.category_id">
          <bk-select
            style="width: 320px;"
            v-model="formData.category_id"
            data-test-id="addNewCustomBox_select_selectDataCategory"
            :disabled="submitLoading">
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
            data-test-id="addNewCustomBox_input_description"
            :disabled="submitLoading"
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
            data-test-id="addNewCustomBox_select_selectDataLink"
            :clearable="false"
            :disabled="submitLoading || isEdit">
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
            data-test-id="addNewCustomBox_select_storageCluster"
            v-model="formData.storage_cluster_id"
            :clearable="false"
            :disabled="submitLoading || isEdit"
            @selected="handleSelectStorageCluster">
            <bk-option
              v-for="(item, index) in storageList"
              class="custom-no-padding-option"
              :id="item.storage_cluster_id"
              :name="item.storage_cluster_name"
              :key="index">
              <div
                v-if="!(item.permission && item.permission.manage_es_source)"
                class="option-slot-container no-authority"
                @click.stop>
                <span class="text">{{item.storage_cluster_name}}</span>
                <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
              </div>
              <div v-else class="option-slot-container">
                <span>{{ item.storage_cluster_name }}</span>
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
            disabled
            v-model="formData.collector_config_name_en"
            data-test-id="addNewCustomBox_input_configName"
            maxlength="50"
            minlength="5"
            :placeholder="$t('dataManage.input_number')">
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
            data-test-id="addNewCustomBox_select_expireDate"
            :clearable="false"
            :disabled="submitLoading">
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
            data-test-id="addNewCustomBox_input_copyNumber"
            v-model="formData.storage_replies"
            class="copy-number-input"
            type="number"
            :max="3"
            :min="0"
            :precision="0"
            :clearable="false"
            :show-controls="true"
            :disabled="submitLoading"
            @blur="changeCopyNumber"
          ></bk-input>
        </bk-form-item>
        <!-- 热数据\冷热集群存储期限 -->
        <bk-form-item :label="$t('热数据')" class="hot-data-form-item">
          <bk-select
            style="width: 320px;"
            data-test-id="addNewCustomBox_select_selectHotData"
            v-model="formData.allocation_min_days"
            :clearable="false"
            :disabled="!selectedStorageCluster.enable_hot_warm || submitLoading">
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

    <intro-panel
      :data="formData"
      :is-open-window="isOpenWindow"
      @handleActiveDetails="handleActiveDetails"></intro-panel>

    <div class="submit-btn">
      <bk-button
        class="fl"
        theme="primary"
        :loading="submitLoading"
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
import IntroPanel from './components/IntroPanel';

export default {
  name: 'custom-report-create',
  components: {
    IntroPanel,
  },
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
      isOpenWindow: true, // 是否展开使用列表
      isSubmit: false, // 是否提交
      containerLoading: false, // 全局loading
      isEdit: false, // 是否是编辑
      submitLoading: false,
      collectorId: null,
      formData: {
        bk_data_id: '',
        collector_config_name: '',
        collector_config_name_en: '',
        custom_type: 'log',
        data_link_id: '',
        storage_cluster_id: '',
        retention: '',
        allocation_min_days: '0',
        storage_replies: 1,
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
    defaultRetention() {
      const { storage_duration_time } = this.globalsData;
      // eslint-disable-next-line camelcase
      return storage_duration_time && storage_duration_time.filter(item => item.default === true)[0].id;
    },
  },
  watch: {
    linkConfigurationList: {
      deep: true,
      handler(val) {
        const { params: { collectorId } } = this.$route;
        if (val.length > 0 && !collectorId) {
          this.formData.data_link_id = val[0]?.data_link_id;
        }
      },
    },
  },
  mounted() {
    this.containerLoading = true;
    Promise.all([this.getLinkData(), this.getStorage(), this.initFormData()]).then(() => {
      this.containerLoading = false;
    });
  },
  methods: {
    handleChangeType(id) {
      this.formData.custom_type = id;
    },
    handleSubmitChange() {
      this.$refs.validateForm.validate().then(() => {
        this.submitLoading = true;
        this.$http.request(`custom/${this.isEdit ? 'setCustom' : 'createCustom'}`, {
          params: {
            collector_config_id: this.collectorId,
          },
          data: {
            ...this.formData,
            storage_replies: Number(this.formData.storage_replies),
            allocation_min_days: Number(this.formData.allocation_min_days),
            bk_biz_id: Number(this.bkBizId),
          },
        })
          .then((res) => {
            res.result && this.messageSuccess(this.$t('保存成功'));
            this.isSubmit = true;
            this.cancel();
          })
          .finally(() => {
            this.submitLoading = false;
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
    async initFormData() {
      const { params: { collectorId }, name } = this.$route;
      if (collectorId && name === 'custom-report-edit') {
        this.isEdit = true;
        this.collectorId = collectorId;
        const res = await this.$http.request('collect/details', {
          params: {
            collector_config_id: collectorId,
          },
        });
        const {
          collector_config_name,
          collector_config_name_en,
          custom_type,
          data_link_id,
          storage_cluster_id,
          retention,
          allocation_min_days,
          storage_replies,
          category_id,
          description,
          bk_data_id,
        } = res.data;
        Object.assign(this.formData, {
          collector_config_name,
          collector_config_name_en,
          custom_type,
          data_link_id,
          storage_cluster_id,
          retention: retention ? `${retention}` : this.defaultRetention,
          allocation_min_days,
          storage_replies,
          category_id,
          description,
          bk_data_id,
        });
      } else {
        const { retention } =  this.formData;
        Object.assign(this.formData, {
          retention: retention ? `${retention}` : this.defaultRetention,
        });
      }
    },
    cancel() {
      this.$router.back(-1);
    },
    handleActiveDetails(state) {
      this.isOpenWindow = state;
    },
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit) {
      this.$bkInfo({
        title: this.$t('pageLeaveTips'),
        confirmFn: () => {
          next();
        },
      });
      return;
    }
    next();
  },
};
</script>

<style lang="scss">
@import "@/scss/mixins/clearfix";
@import "@/scss/mixins/flex";
@import '@/scss/mixins/scroller';
@import '@/scss/storage';

.custom-create-container {
  padding:0 24px;
  transition: padding 0.5s;
  &.is-active-details{
    padding:0 420px 0 24px;
  }
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
    // .tips_storage {
    //   width: 560px;
    //   background-color: rgb(239, 248, 255);
    //   border: 1px solid deepskyblue;
    //   font-size: 12px;
    //   padding: 10px;
    //   margin-top: 15px;
    //   div {
    //     line-height: 24px;
    //     color: #63656e;
    //   }
    // }
    // .copy-number-input{
    //   width:100px;
    //   .input-number-option{
    //     top: 2px;
    //   }
    // }
    // .hot-data-form-item {
    //   .bk-form-content {
    //     display: flex;
    //     align-items: center;
    //     .disable-tips {
    //       margin-left: 10px;
    //       font-size: 12px;
    //       color: #63656e;
    //       a {
    //         color: #3a84ff;
    //       }
    //     }
    //   }
    // }
  }
  .submit-btn {
    width: 140px;
    margin: 20px 20px 100px ;
    @include clearfix;
  }
}
</style>
