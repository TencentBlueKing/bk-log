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
  <div class="step-storage" v-bkloading="{ isLoading: basicLoading }">
    <bk-form :label-width="115" :model="formData" ref="validateForm" data-test-id="storage_form_storageBox">
      <bk-form-item
        :label="$t('dataSource.storage_cluster_name')"
        required
        property="storage_cluster_id"
        :rules="rules.cluster_id">
        <bk-select
          style="width: 320px;"
          data-test-id="storageBox_select_storageCluster"
          v-model="formData.storage_cluster_id"
          :disabled="isUnmodifiable"
          :clearable="false"
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
      <div class="form-div mt">
        <bk-form-item
          :label="$t('configDetails.storageIndexName')"
          class="form-inline-div"
          :rules="rules.table_id"
          :property="'table_id'">
          <!-- <div class="prefix">{{formData.table_id_prefix}}</div> -->
          <bk-input
            style="width: 320px"
            :placeholder="$t('dataManage.input_number')"
            :disabled="isUnmodfyIndexName"
            v-model="formData.table_id"
            maxlength="50"
            minlength="5">
            <template slot="prepend">
              <div class="group-text">{{formData.table_id_prefix}}</div>
            </template>
          </bk-input>
        </bk-form-item>
        <!-- <div class="tips">{{ $t('dataManage.start_bk') }}</div> -->
      </div>
      <!-- 过期时间 -->
      <bk-form-item :label="$t('configDetails.expirationTime')">
        <bk-select
          style="width: 320px;"
          v-model="formData.retention"
          :clearable="false"
          data-test-id="storageBox_select_selectExpiration">
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
              data-test-id="storageBox_input_customDayNumber"
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
          :max="3"
          :min="0"
          :precision="0"
          v-model="formData.storage_replies"
          style="width:100px;"
          type="number"
          :clearable="false"
          :show-controls="true"
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
          :disabled="!selectedStorageCluster.enable_hot_warm">
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
      <bk-form-item
        v-if="accessUserManage"
        :label="$t('indexSetList.jurisdiction')"
        required
        :property="'view_roles'"
        :rules="rules.view_roles"
        style="width: 435px;">
        <bk-select
          style="width: 320px;"
          data-test-id="storageBox_select_viewPermission"
          v-model="formData.view_roles"
          searchable
          multiple
          :placeholder="$t('btn.select')"
          show-select-all>
          <bk-option
            v-for="(role, index) in roleList"
            :key="index"
            :id="role.group_id"
            :name="role.group_name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item>
        <bk-button
          theme="default"
          data-test-id="storageBox_button_previousPage"
          :title="$t('dataManage.last')"
          class="mr10"
          :disabled="isLoading"
          @click="prevHandler">
          {{$t('dataManage.last')}}
        </bk-button>
        <bk-button
          theme="primary"
          data-test-id="storageBox_button_nextPage"
          @click.stop.prevent="finish"
          :loading="isLoading"
          :disabled="!collectProject">
          {{$t('dataManage.perform')}}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { projectManages } from '@/common/util';
import storageMixin from '@/mixins/storageMixin';

export default {
  mixins: [storageMixin],
  props: {
    operateType: String,
    curStep: {
      type: Number,
      default: 1,
    },
    collectorId: String,
    isCleanField: Boolean,
  },
  data() {
    return {
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      refresh: false,
      // eslint-disable-next-line no-useless-escape
      isLoading: false,
      basicLoading: true,
      isUnmodifiable: false,
      isUnmodfyIndexName: false,
      roleList: [],
      fieldType: '',
      deletedVisible: true,
      copysText: {},
      jsonText: {},
      defaultSettings: {
        isShow: false,
      },
      logOriginal: '',
      params: { // 此处为可以变动的数据，如果调试成功，则将此条件保存至formData，保存时还需要对比此处与formData是否有差异
        etl_config: 'bk_log_text',
        etl_params: {
          separator_regexp: '',
          separator: '',
        },
      },
      formData: { // 最后一次正确的结果，保存以此数据为准
        table_id: '',
        etl_config: 'bk_log_text',
        etl_params: {
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
          // separator_field_list: ''
        },
        fields: [],
        view_roles: [],
        retention: '',
        storage_replies: 1,
        allocation_min_days: '0',
        storage_cluster_id: '',
      },
      selectedStorageCluster: {}, // 选择的es集群
      retentionDaysList: [], // 过期天数列表
      customRetentionDay: '', // 自定义过期天数
      hotDataDaysList: [], // 冷热集群存储期限列表
      customHotDataDay: '', // 自定义冷热集群存储期限天数
      rules: {
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
        view_roles: [{
          validator(val) {
            return val.length >= 1;
          },
          trigger: 'change',
        }],
      },
      storage_capacity: '',
      tips_storage: [],
      tip_storage: [],
      storageList: [],
      dialogVisible: false,
      rowTemplate: {
        alias_name: '',
        description: '',
        field_type: '',
        is_analyzed: false,
        is_built_in: false,
        is_delete: false,
        is_dimension: false,
        is_time: false,
        value: '',
        option: {
          time_format: '',
          time_zone: '',
        },
      },
      stashCleanConf: null, // 清洗缓存,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      projectId: 'projectId',
      curCollect: 'collect/curCollect',
      globalsData: 'globals/globalsData',
      accessUserManage: 'accessUserManage',
    }),
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
    defaultRetention() {
      const { storage_duration_time } = this.globalsData;
      // eslint-disable-next-line camelcase
      return storage_duration_time && storage_duration_time.filter(item => item.default === true)[0].id;
    },
  },
  async mounted() {
    this.getStorage();
  },
  methods: {
    // 存储入库
    fieldCollection() {
      const {
        etl_config,
        table_id,
        storage_cluster_id,
        retention,
        storage_replies,
        allocation_min_days,
        view_roles,
        fields,
        etl_params,
      } = this.formData;
      this.isLoading = true;
      const data = {
        etl_config,
        table_id,
        storage_cluster_id,
        retention: Number(retention),
        storage_replies: Number(storage_replies),
        allocation_min_days: Number(allocation_min_days),
        view_roles,
        etl_params: {
          retain_original_text: etl_params.retain_original_text,
          separator_regexp: etl_params.separator_regexp,
          separator: etl_params.separator,
        },
        fields,
      };
      /* eslint-disable */
      if (etl_config !== 'bk_log_text') {
        const etlParams = {
          retain_original_text: etl_params.retain_original_text
        }
        if (etl_config === 'bk_log_delimiter') {
          etlParams.separator = etl_params.separator
        }
        if (etl_config === 'bk_log_regexp') {
          etlParams.separator_regexp = etl_params.separator_regexp
        }
        data.etl_params = etlParams
        // data.fields = this.$refs.fieldTable.getData()
      }
      /* eslint-enable */
      this.isLoading = true;
      this.$http.request('collect/fieldCollection', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
        data,
      }).then((res) => {
        if (res.code === 0) {
          // this.storageList = res.data
          // this.formData.storage_cluster_id = this.storageList[0].storage_cluster_id
          this.isLoading = false;
          if (res.data) {
            this.$store.commit('collect/updateCurCollect', Object.assign({}, this.formData, data, res.data));
            this.$emit('changeIndexSetId', res.data.index_set_id || '');
          }
          this.$emit('change-submit', true);
          if (this.isCleanField) {
            this.messageSuccess(this.$t('保存成功'));
            this.$emit('stepChange', 'back');
          } else {
            this.$emit('stepChange');
          }
        }
      })
        .finally(() => {
          this.isLoading = false;
        });
    },
    // 完成按钮
    finish() {
      const promises = [this.checkStore()];
      Promise.all(promises).then(() => {
        this.fieldCollection();
      }, (validator) => {
        console.warn('保存失败', validator);
      });
    },
    // 存储校验
    checkStore() {
      return new Promise((resolve, reject) => {
        if (!this.isUnmodifiable) {
          this.$refs.validateForm.validate().then((validator) => {
            resolve(validator);
          })
            .catch((err) => {
              console.warn('存储校验错误');
              reject(err);
            });
        } else {
          resolve();
        }
      });
    },
    prevHandler() {
      const step = this.isCleanField ? 1 : this.curStep - 1;
      this.$emit('stepChange', step);
    },
    // 获取详情
    getDetail() {
      const tsStorageId = this.formData.storage_cluster_id;
      const {
        table_id,
        storage_cluster_id,
        retention,
        storage_replies,
        allocation_min_days,
        table_id_prefix,
        view_roles,
        etl_config,
        etl_params,
        fields,
        collector_config_name_en,
      } = this.curCollect;
      const option = { time_zone: '', time_format: '' };
      const copyFields = fields ? JSON.parse(JSON.stringify(fields)) : [];
      copyFields.forEach((row) => {
        row.value = '';
        if (row.is_delete) {
          const copyRow = Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), JSON.parse(JSON.stringify(row)));
          Object.assign(row, copyRow);
        }
        if (row.option) {
          row.option = Object.assign({}, option, row.option || {});
        } else {
          row.option = Object.assign({}, option);
        }
      });
      /* eslint-disable */
      this.params.etl_config = etl_config
      Object.assign(this.params.etl_params, {
        separator_regexp: etl_params.separator_regexp || '',
        separator: etl_params.separator || ''
      })
      console.log(table_id);
      console.log(storage_cluster_id);
      this.isUnmodifiable = !!(table_id || storage_cluster_id)
      this.isUnmodfyIndexName = !!(table_id || storage_cluster_id || collector_config_name_en)
      this.fieldType = etl_config || 'bk_log_text'
      // this.switcher = etl_config ? etl_config !== 'bk_log_text' : false
      /* eslint-enable */
      Object.assign(this.formData, {
        // eslint-disable-next-line camelcase
        table_id: table_id ? table_id : collector_config_name_en ? collector_config_name_en : '',
        storage_cluster_id,
        table_id_prefix,
        etl_config: this.fieldType,
        etl_params: Object.assign({
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
          // separator_field_list: ''
                    }, etl_params ? JSON.parse(JSON.stringify(etl_params)) : {}), // eslint-disable-line
        fields: copyFields.filter(item => !item.is_built_in),
        retention: retention ? `${retention}` : this.defaultRetention,
        storage_replies,
        // eslint-disable-next-line camelcase
        allocation_min_days: allocation_min_days ? `${allocation_min_days}` : '0',
        view_roles,
      });

      if (this.stashCleanConf) {
        // 缓存清洗配置
        Object.assign(this.formData, {
          etl_config: this.stashCleanConf.clean_type,
          etl_params: this.stashCleanConf.etl_params,
          fields: this.stashCleanConf.etl_fields,
        });
      }
      this.formData.storage_cluster_id = this.formData.storage_cluster_id === null
        ? tsStorageId : this.formData.storage_cluster_id;

      this.basicLoading = false;
    },
  },
};
</script>
<style lang="scss">
  @import '@/scss/mixins/clearfix';

  .step-storage {
    margin-top: 30px;
    position: relative;
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
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

    .form-div {
      display: flex;
      margin: 20px 0;

      .form-inline-div {
        white-space: nowrap;

        .bk-form-content {
          display: flex;
          flex-wrap: nowrap;
        }
      }

      .prefix {
        font-size: 14px;
        line-height: 32px;
        color: #858790;
        margin-right: 8px;
        min-width: 80px;
        text-align: right;
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
</style>
