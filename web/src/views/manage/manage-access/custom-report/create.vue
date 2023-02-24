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
    ref="addNewCustomBoxRef"
    v-bkloading="{ isLoading: containerLoading }"
    :style="`padding-right: ${introWidth + 20}px;`"
    class="custom-create-container">
    <bk-form
      :label-width="103"
      :model="formData"
      ref="validateForm">
      <div class="create-form">
        <div class="form-title">{{$t('基础信息')}}</div>
        <!-- 数据ID -->
        <bk-form-item
          required
          :label="$t('数据ID')"
          :property="'bk_data_id'"
          v-if="isEdit">
          <bk-input
            class="form-input"
            disabled
            v-model="formData.bk_data_id">
          </bk-input>
        </bk-form-item>
        <!-- <bk-form-item :label="$t('数据token')" required :property="'name'">
          <bk-input class="form-input" :disabled="true" v-model="formData.name"></bk-input>
        </bk-form-item> -->
        <!-- 数据名称 -->
        <bk-form-item
          required
          :disabled="submitLoading"
          :label="$t('数据名称')"
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
        <bk-form-item
          required
          :label="$t('数据类型')"
          :property="'name'">
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
            <p class="group-tip" slot="tip">{{$t('自定义上报数据，可以通过采集器，或者指定协议例如otlp等方式进行上报，自定义上报有一定的使用要求，具体可以查看使用说明')}}</p>
          </div>
        </bk-form-item>
        <bk-form-item
          required
          ext-cls="en-bk-form"
          :icon-offset="120"
          :label="$t('英文名')"
          :property="'collector_config_name_en'"
          :rules="baseRules.collector_config_name_en">
          <div class="en-name-box">
            <div>
              <bk-input
                class="form-input"
                show-word-limit
                maxlength="50"
                data-test-id="addNewCustomBox_input_englishName"
                v-model="formData.collector_config_name_en"
                :disabled="submitLoading || isEdit"
                :placeholder="$t('支持数字、字母、下划线，长短5～50字符')"></bk-input>
              <span v-if="!isTextValid" class="text-error">{{formData.collector_config_name_en}}</span>
            </div>
            <span v-bk-tooltips.top="$t('自动转换成正确的英文名格式')">
              <bk-button v-if="!isTextValid" text @click="handleEnConvert">{{$t('自动转换')}}</bk-button>
            </span>
          </div>
        </bk-form-item>
        <!-- 数据分类 -->
        <bk-form-item
          required
          :label="$t('数据分类')"
          :property="'category_id'"
          :rules="baseRules.category_id">
          <bk-select
            style="width: 500px;"
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
        <bk-form-item :label="$t('说明')">
          <bk-input
            class="form-input"
            type="textarea"
            v-model="formData.description"
            data-test-id="addNewCustomBox_input_description"
            :disabled="submitLoading"
            :placeholder="$t('未输入')"
            :maxlength="100"></bk-input>
        </bk-form-item>
      </div>
      <!-- 存储设置 -->
      <div class="create-form">
        <div class="form-title">{{$t('存储设置')}}</div>
        <!-- 存储集群 -->
        <bk-form-item
          required
          :label="$t('存储集群')"
          :property="'data_link_id'">
          <cluster-table
            :table-list="clusterList"
            :is-change-select="true"
            :storage-cluster-id.sync="formData.storage_cluster_id" />
          <cluster-table
            table-type="exclusive"
            style="margin-top: 20px;"
            :table-list="exclusiveList"
            :is-change-select="true"
            :storage-cluster-id.sync="formData.storage_cluster_id" />
        </bk-form-item>
        <!-- 数据链路 -->
        <bk-form-item
          required
          v-if="!isCloseDataLink"
          :label="$t('数据链路')"
          :rules="storageRules.data_link_id"
          :property="'data_link_id'">
          <bk-select
            style="width: 500px;"
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
        <!-- 索引集名称 -->
        <bk-form-item
          :label="$t('存储索引名')"
          class="form-inline-div"
          :rules="storageRules.table_id"
          :property="'table_id'">
          <bk-input
            style="width: 500px;"
            disabled
            v-model="formData.collector_config_name_en"
            data-test-id="addNewCustomBox_input_configName"
            maxlength="50"
            minlength="5"
            :placeholder="$t('英文或者数字，5～50长度')">
            <template slot="prepend">
              <div class="group-text">{{showGroupText}}</div>
            </template>
          </bk-input>
        </bk-form-item>
        <!-- 过期时间 -->
        <bk-form-item :label="$t('过期时间')">
          <bk-select
            style="width: 500px;"
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
                :placeholder="$t('输入自定义天数，按 Enter 确认')"
                :show-controls="false"
                @enter="enterCustomDay($event, 'retention')"
              ></bk-input>
            </div>
          </bk-select>
        </bk-form-item>
        <!-- 副本数 -->
        <bk-form-item :label="$t('副本数')">
          <bk-input
            data-test-id="addNewCustomBox_input_copyNumber"
            v-model="formData.storage_replies"
            class="copy-number-input"
            type="number"
            :max="replicasMax"
            :min="0"
            :precision="0"
            :clearable="false"
            :show-controls="true"
            :disabled="submitLoading"
            @blur="changeCopyNumber"
          ></bk-input>
        </bk-form-item>
        <!-- 分片数 -->
        <bk-form-item :label="$t('分片数')">
          <bk-input
            v-model="formData.es_shards"
            class="copy-number-input"
            type="number"
            :max="shardsMax"
            :min="1"
            :precision="0"
            :clearable="false"
            :show-controls="true"
            :disabled="submitLoading"
            @blur="changeShardsNumber"
          ></bk-input>
        </bk-form-item>
        <!-- 热数据\冷热集群存储期限 -->
        <bk-form-item
          :label="$t('热数据天数')"
          class="hot-data-form-item"
          v-if="selectedStorageCluster.enable_hot_warm">
          <bk-select
            style="width: 320px;"
            data-test-id="addNewCustomBox_select_selectHotData"
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
                :placeholder="$t('输入自定义天数，按 Enter 确认')"
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

    <div
      :class="['intro-container',isDraging && 'draging-move']"
      :style="`width: ${ introWidth }px`">
      <div :class="`drag-item ${!introWidth && 'hidden-drag'}`" :style="`right: ${introWidth - 18}px`">
        <span
          class="bk-icon icon-more"
          @mousedown.left="dragBegin"></span>
      </div>
      <intro-panel
        :data="formData"
        :is-open-window="isOpenWindow"
        @handleActiveDetails="handleActiveDetails" />
    </div>

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
import storageMixin from '@/mixins/storage-mixin';
import dragMixin from '@/mixins/drag-mixin';
import IntroPanel from './components/intro-panel';
import clusterTable from '@/components/collection-access/components/cluster-table';

export default {
  name: 'CustomReportCreate',
  components: {
    IntroPanel,
    clusterTable,
  },
  mixins: [storageMixin, dragMixin],
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
        storage_replies: 0,
        category_id: '',
        description: '',
        es_shards: 0,
      },
      replicasMax: 7,
      shardsMax: 7,
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
            message: this.$t('不能多于50个字符'),
            trigger: 'blur',
          },
          {
            min: 5,
            message: this.$t('不能少于5个字符'),
            trigger: 'blur',
          },
          {
            validator: this.checkEnNameValidator,
            message: this.$t('只支持输入字母，数字，下划线'),
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
      clusterList: [], // 共享集群
      exclusiveList: [], // 独享集群
      editStorageClusterID: null,
      isTextValid: true,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      globalsData: 'globals/globalsData',
    }),
    defaultRetention() {
      const { storage_duration_time } = this.globalsData;
      // eslint-disable-next-line camelcase
      return storage_duration_time && storage_duration_time.filter(item => item.default === true)[0].id;
    },
    isCloseDataLink() {
      // 没有可上报的链路时，编辑采集配置链路ID为0或null时，隐藏链路配置框，并且不做空值校验。
      return !this.linkConfigurationList.length || (this.isEdit && !this.formData.data_link_id);
    },
    showGroupText() {
      return Number(this.bkBizId) > 0 ? `${this.bkBizId}_bklog_` : `space_${Math.abs(Number(this.bkBizId))}_bklog_`;
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
  created() {
    const { params: { collectorId }, name } = this.$route;
    if (collectorId && name === 'custom-report-edit') {
      this.collectorId = collectorId;
      this.isEdit = true;
    }
  },
  mounted() {
    this.containerLoading = true;
    Promise.all([this.getLinkData(), this.getStorage()]).then(() => {
      this.initFormData();
    })
      .finally(() => {
        this.containerLoading = false;
      });
    this.$nextTick(() => {
      this.maxIntroWidth = this.$refs.addNewCustomBoxRef.clientWidth - 380;
    });
  },
  methods: {
    handleChangeType(id) {
      this.formData.custom_type = id;
    },
    handleSubmitChange() {
      if (this.formData.storage_cluster_id === '') {
        this.$bkMessage({
          theme: 'error',
          message: this.$t('请选择集群'),
        });
        return;
      }
      this.$refs.validateForm.validate().then(() => {
        this.submitLoading = true;
        if (this.isCloseDataLink) delete this.formData.data_link_id;
        this.$http.request(`custom/${this.isEdit ? 'setCustom' : 'createCustom'}`, {
          params: {
            collector_config_id: this.collectorId,
          },
          data: {
            ...this.formData,
            storage_replies: Number(this.formData.storage_replies),
            allocation_min_days: Number(this.formData.allocation_min_days),
            es_shards: Number(this.formData.es_shards),
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
      if (this.isEdit) {
        const res = await this.$http.request('collect/details', {
          params: {
            collector_config_id: this.collectorId,
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
          storage_shards_nums,
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
          es_shards: storage_shards_nums,
        });
        // 缓存编辑时的集群ID
        // eslint-disable-next-line camelcase
        this.editStorageClusterID = storage_cluster_id;
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
      this.introWidth = state ? 360 : 0;
    },
    checkEnNameValidator(val) {
      this.isTextValid = new RegExp(/^[A-Za-z0-9_]+$/).test(val);
      return this.isTextValid;
    },
    handleEnConvert() {
      const str = this.formData.collector_config_name_en;
      const convertStr = str.split('').reduce((pre, cur) => {
        if (cur === '-') cur = '_';
        if (!/\w/.test(cur)) cur = '';
        return pre += cur;
      }, '');
      this.formData.collector_config_name_en = convertStr;
      this.$refs.validateForm.validate().then(() => {
        this.isTextValid = true;
      })
        .catch(() => {
          if (convertStr.length < 5) this.isTextValid = true;
        });
    },
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit) {
      this.$bkInfo({
        title: this.$t('是否放弃本次操作？'),
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
  @import '@/scss/mixins/clearfix';
  @import '@/scss/mixins/flex';
  @import '@/scss/mixins/scroller';
  @import '@/scss/storage';

  .custom-create-container {
    padding: 0 24px;

    .en-bk-form {
      width: 680px;

      .en-name-box {
        align-items: center;

        @include flex-justify(space-between);
      }

      .text-error {
        display: inline-block;
        position: absolute;
        top: 6px;
        left: 12px;
        font-size: 12px;
        color: transparent;
        pointer-events: none;

        /* stylelint-disable-next-line declaration-no-important */
        text-decoration: red wavy underline !important;
      }
    }

    .create-form {
      background: #fff;
      padding: 24px 37px;
      margin-top: 20px;
      border-radius: 2px;
      border: 1px solid #dcdee5;
      overflow-x: hidden;

      .form-title {
        font-size: 14px;
        color: #63656e;
        font-weight: 700;
        margin-bottom: 24px;
      }

      .form-input {
        width: 500px;
      }

      .group-tip {
        font-size: 12px;
        color: #979ba5;
      }
    }

    .submit-btn {
      width: 140px;
      margin: 20px 20px 100px ;

      @include clearfix;
    }

    .intro-container {
      position: fixed;
      top: 99px;
      right: 0;
      z-index: 999;
      height: calc(100vh - 99px);
      overflow: hidden;
      border-left: 1px solid transparent;

      .drag-item {
        width: 20px;
        height: 40px;
        display: inline-block;
        color: #c4c6cc;
        position: absolute;
        z-index: 100;
        right: 304px;
        top: 48%;
        user-select: none;
        cursor: col-resize;

        &.hidden-drag {
          display: none;
        }

        .icon-more::after {
          content: '\e189';
          position: absolute;
          left: 0;
          top: 12px;
        }
      }

      &.draging-move {
        border-left-color: #3a84ff;
      }
    }
  }
</style>
