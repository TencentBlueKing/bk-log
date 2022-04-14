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
      <div class="add-collection-title">{{ $t('集群选择') }}</div>
      <cluster-table
        :table-list="clusterList"
        :storage-cluster-id.sync="formData.storage_cluster_id"
      />
      <cluster-table
        :table-list="exclusiveList"
        :table-title-type="false"
        :storage-cluster-id.sync="formData.storage_cluster_id" />

      <div class="add-collection-title">{{ $t('存储信息') }}</div>
      <!-- 存储索索引名 -->
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
      <!-- 热数据\冷热集群存储期限 -->
      <bk-form-item :label="$t('热数据天数')" class="hot-data-form-item">
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
      <!-- 副本数 -->
      <bk-form-item :label="$t('configDetails.copyNumber')">
        <bk-input
          class="copy-number-input"
          v-model="formData.storage_replies"
          type="number"
          :max="3"
          :min="0"
          :precision="0"
          :clearable="false"
          :show-controls="true"
          @blur="changeCopyNumber"
        ></bk-input>
      </bk-form-item>
      <div class="capacity-assessment">
        <div class="button-text" @click="isShowAssessment = !isShowAssessment">
          <span>{{ $t('容量评估') }}</span>
          <span :class="['bk-icon','icon-angle-double-down',isShowAssessment && 'is-active']"></span>
        </div>
        <div class="capacity-message">
          <span class="bk-icon icon-info"></span>
          <span style="font-size: 12px;">{{ $t('当前主机数较多，建议进行容量评估') }}</span>
        </div>
      </div>

      <div v-show="isShowAssessment">
        <div class="capacity-illustrate">
          <p class="illustrate-title">{{$t('容量说明')}}</p>
          <p>容量计算公式：单机日志增量主机数量存储转化率分片数（日志保留天数 + 1）</p>
          <p>存储转化率（1.5）：即原始日志增加日志采集元数据并存储到ES到实际占有的空间</p>
          <p>分片数（2）：1个主分片+1个副本数，避免节点故障导致数据丢失</p>
        </div>

        <bk-form-item required :label="$t('每日单台日志量')">
          <bk-input
            style="width: 320px;"
            v-model="formData.assessment_config.log_assessment"
          ></bk-input>
        </bk-form-item>

        <div class="need-approval">
          <bk-checkbox
            class="bk-checkbox"
            v-model="formData.assessment_config.need_approval">
            {{$t('需要审批')}}
          </bk-checkbox>
          <bk-alert
            style="width: 607px"
            type="warning"
            title="勾选需要审批后需等待审批通过后，才会继续进行存储流程">
          </bk-alert>
        </div>

        <bk-form-item :label="$t('审批人')">
          <span class="approver">{{$t('集群负责人')}}（ {{getApprover}} ）</span>
        </bk-form-item>
      </div>
      <!-- 查看权限 -->
      <!-- <bk-form-item
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
      </bk-form-item> -->
      <bk-form-item style="margin-top: 32px">
        <bk-button
          theme="default"
          class="mr10"
          data-test-id="storageBox_button_previousPage"
          :title="$t('dataManage.last')"
          :disabled="isLoading"
          @click="prevHandler">
          {{$t('dataManage.last')}}
        </bk-button>
        <bk-button
          theme="primary"
          class="mr10"
          data-test-id="storageBox_button_nextPage"
          :loading="isLoading"
          :disabled="!collectProject"
          @click.stop.prevent="finish">
          {{$t('dataManage.perform')}}
        </bk-button>
        <bk-button
          theme="default"
          @click="cancel">
          {{$t('取消')}}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { projectManages } from '@/common/util';
import storageMixin from '@/mixins/storage-mixin';
import ClusterTable from './components/cluster-table';

export default {
  components: {
    ClusterTable,
  },
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
      basicLoading: false,
      isUnmodifiable: false,
      isUnmodfyIndexName: false,
      // roleList: [],
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
        assessment_config: {
          log_assessment: '',
          need_approval: false,
          approvals: [],
        },
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
      clusterList: [], // 平台集群
      exclusiveList: [], // 独享集群
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
      isShowAssessment: false,
      activeItem: {},
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
    getApprover() {
      return this.formData.assessment_config.approvals.join(', ');
    },
  },
  watch: {
    'formData.storage_cluster_id': {
      handler(val) {
        this.activeItem = this.storageList.find(item => item.storage_cluster_id === val);
      },
    },
  },
  async mounted() {
    this.getStorage(true);
  },
  methods: {
    // 获取采集项清洗基础配置缓存 用于存储入库提交
    getCleanStash() {
      this.$http.request('clean/getCleanStash', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
      }).then((res) => {
        if (res.data) {
          this.stashCleanConf = res.data;
        }
      })
        .finally(() => {
          this.getDetail();
        });
    },
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
        assessment_config,
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
        assessment_config: {
          log_assessment: assessment_config.log_assessment,
          need_approval: assessment_config.need_approval,
          approvals: assessment_config.approvals,
        },
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
    cancel() {
      this.$router.push({
        name: 'collection-item',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/clearfix';
  @import '@/scss/storage.scss';
  @import '@/scss/mixins/flex.scss';

  .step-storage {
    position: relative;
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .bk-label {
      font-size: 12px;
    }

    .tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
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

    .add-collection-title {
      width: 100%;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
      padding-bottom: 10px;
      margin: 30px 0 20px 0;
    }

    .capacity-assessment {
      margin: 20px 0;
      font-size: 14px;

      @include flex-align;

      .icon-angle-double-down {
        font-size: 24px;

        &.is-active {
          transform: rotateZ(180deg) translateY(-2px);
        }
      }

      .button-text {
        @include flex-align;
      }

      .capacity-message {
        color: #63656e;
        margin-left: 20px;
      }
    }

    .capacity-illustrate {
      height: 104px;
      background: #fafbfd;
      border: 1px solid #dcdee5;
      border-radius: 2px;
      padding: 12px 20px;
      margin-bottom: 20px;

      .illustrate-title {
        font-weight: 700;
      }

      p {
        color: #63656e;
        margin-bottom: 4px;
        font-size: 12px;
      }
    }

    .need-approval {
      margin: 12px 0 12px 116px;

      @include flex-align;

      .bk-checkbox-text {
        font-size: 12px;
        margin-right: 12px;
      }
    }

    .approver {
      font-size: 12px;
    }
  }
</style>
