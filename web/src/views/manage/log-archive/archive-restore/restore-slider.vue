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
  <div class="restore-slider-container">
    <bk-sideslider
      transfer
      :title="isEdit ? $t('logArchive.editRestore') : $t('logArchive.createRestore')"
      :is-show="showSlider"
      :width="676"
      :quick-close="true"
      :before-close="handleCloseSideslider"
      @animation-end="$emit('hidden')"
      @update:isShow="updateIsShow">
      <div v-bkloading="{ isLoading: sliderLoading }" slot="content" class="restore-slider-content">
        <bk-form
          v-if="!sliderLoading"
          :model="formData"
          :label-width="150"
          :rules="basicRules"
          data-test-id="restore_div_addNewRestore"
          form-type="vertical"
          ref="validateForm"
          class="king-form">
          <bk-form-item :label="$t('索引集名称')" required property="index_set_name">
            <bk-input
              v-model="formData.index_set_name"
              data-test-id="addNewRestore_input_indexSetName"
              :disabled="isEdit"></bk-input>
          </bk-form-item>
          <!-- <bk-alert type="info" :title="$t('logArchive.restoreIndexTip')"></bk-alert> -->
          <bk-form-item
            :label="$t('logArchive.archiveItem')"
            required
            property="archive_config_id">
            <bk-select
              v-model="formData.archive_config_id"
              data-test-id="addNewRestore_select_selectCollector"
              @selected="handleArchiveChange"
              :disabled="isEdit">
              <bk-option
                v-for="option in archiveList"
                :key="option.archive_config_id"
                :id="option.archive_config_id"
                :name="option.collector_config_name"
                :disabled="!option.permission[authorityMap.MANAGE_COLLECTION_AUTH]">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('logArchive.timeRange')"
            required
            property="datePickerValue">
            <bk-date-picker
              format="yyyy-MM-dd HH:mm"
              :placeholder="'选择日期时间范围'"
              :type="'datetimerange'"
              :disabled="isEdit"
              v-model="formData.datePickerValue"
              @change="handleTimeChange">
            </bk-date-picker>
          </bk-form-item>
          <bk-form-item :label="$t('过期时间')" required property="datePickerExpired">
            <bk-date-picker
              v-model="formData.datePickerExpired"
              format="yyyy-MM-dd HH:mm"
              data-test-id="addNewRestore_div_datePickerExpired"
              :options="expiredDatePicker"
              @change="handleExpiredChange">
            </bk-date-picker>
          </bk-form-item>
          <bk-form-item :label="$t('logArchive.notifiedUser')" required property="notice_user">
            <validate-user-selector
              style="width: 500px;"
              data-test-id="addNewRestore_input_notifiedUser"
              v-model="formData.notice_user"
              :api="userApi"
              :disabled="isEdit" />
          </bk-form-item>
          <bk-form-item style="margin-top: 30px;">
            <bk-button
              theme="primary"
              class="king-button mr10"
              data-test-id="addNewRestore_button_submit"
              :loading="confirmLoading"
              @click.stop.prevent="handleConfirm">
              {{ $t('提交') }}
            </bk-button>
            <bk-button
              @click="handleCancel"
              data-test-id="addNewRestore_button_cancel">{{ $t('取消') }}</bk-button>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import ValidateUserSelector from '../../manage-extract/manage-extract-permission/validate-user-selector';
import * as authorityMap from '../../../../common/authority-map';

export default {
  components: {
    ValidateUserSelector,
  },
  props: {
    showSlider: {
      type: Boolean,
      default: false,
    },
    editRestore: {
      type: Object,
      default: null,
    },
    archiveId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      confirmLoading: false,
      sliderLoading: false,
      userApi: window.BK_LOGIN_URL,
      customRetentionDay: '', // 自定义过期天数
      retentionDaysList: [], // 过期天数列表
      archiveList: [],
      formData: {
        index_set_name: '',
        archive_config_id: '',
        datePickerValue: [],
        datePickerExpired: '',
        expired_time: '',
        notice_user: [],
        start_time: '',
        end_time: '',
      },
      basicRules: {},
      requiredRules: {
        required: true,
        trigger: 'blur',
      },
      expiredDatePicker: {
        disabledDate(time) {
          return time.getTime() < Date.now();
        },
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      user: 'uesr',
      globalsData: 'globals/globalsData',
    }),
    authorityMap() {
      return authorityMap;
    },
    isEdit() {
      return this.editRestore !== null;
    },
  },
  watch: {
    showSlider(val) {
      if (val) {
        this.sliderLoading = this.isEdit;
        this.getArchiveList();
        this.updateDaysList();
        if (this.isEdit) {
          const {
            index_set_name,
            archive_config_id,
            expired_time,
            notice_user,
            start_time,
            end_time,
          } = this.editRestore;
          Object.assign(this.formData, {
            index_set_name,
            archive_config_id,
            expired_time,
            notice_user,
            start_time,
            end_time,
            // eslint-disable-next-line camelcase
            datePickerValue: [start_time, end_time],
            datePickerExpired: expired_time,
          });
        } else {
          const { userMeta } = this.$store.state;
          if (userMeta && userMeta.username) {
            this.formData.notice_user.push(userMeta.username);
          }
        }

        if (this.archiveId) { // 从归档列表新增回溯
          this.formData.archive_config_id = this.archiveId;
        }
      } else {
        // 清空表单数据
        this.formData = {
          index_set_name: '',
          archive_config_id: '',
          datePickerValue: [],
          expired_time: '',
          datePickerExpired: '',
          notice_user: [],
        };
      }
    },
  },
  created() {
    this.basicRules = {
      index_set_name: [this.requiredRules],
      archive_config_id: [this.requiredRules],
      datePickerExpired: [this.requiredRules],
      datePickerValue: [
        {
          validator: (val) => {
            if (val.length) {
              return !!val.every(item => item);
            }
            return false;
          },
          trigger: 'blur',
        },
      ],
      notice_user: [
        {
          validator: (val) => {
            return !!val.length;
          },
          trigger: 'blur',
        },
      ],
    };
  },
  methods: {
    getArchiveList() {
      const query = {
        bk_biz_id: this.bkBizId,
      };
      this.$http.request('archive/getAllArchives', { query }).then((res) => {
        this.archiveList = res.data || [];
        if (!this.isEdit) {
          this.formData.archive_config_id = res.data[0].archive_config_id || '';
          this.handleArchiveChange(res.data[0].archive_config_id);
        }
      })
        .finally(() => {
          this.sliderLoading = false;
        });
    },
    updateIsShow(val) {
      this.$emit('update:showSlider', val);
    },
    handleCancel() {
      this.$emit('update:showSlider', false);
    },
    handleTimeChange(val) {
      this.formData.start_time = val[0];
      this.formData.end_time = val[1];
    },
    handleExpiredChange(val) {
      this.formData.expired_time = val;
    },
    handleArchiveChange(nval) {
      const selectArchive = this.archiveList.find(el => el.archive_config_id === nval);
      const date = new Date();
      const year = date.getFullYear();
      const month = (date.getMonth() * 1) + 1 >= 10 ? (date.getMonth() * 1) + 1 : `0${date.getMonth() * 1 + 1}`;
      const day = date.getDate() >= 10 ? date.getDate() : `0${date.getDate()}`;
      const hour = date.getHours() >= 10 ? date.getHours() : `0${date.getHours()}`;
      const min = date.getMinutes() >= 10 ? date.getMinutes() : `0${date.getMinutes()}`;
      const dateStr = `${year}${month}${day}${hour}${min}`;
      this.formData.index_set_name  = selectArchive ? `${selectArchive?.collector_config_name}-回溯-${dateStr}` : '';
    },
    updateDaysList() {
      const retentionDaysList = [...this.globalsData.storage_duration_time].filter((item) => {
        return item.id;
      });
      this.retentionDaysList = retentionDaysList;
    },
    // 输入自定义过期天数
    enterCustomDay(val) {
      const numberVal = parseInt(val.trim(), 10);
      const stringVal = numberVal.toString();
      if (numberVal) {
        if (!this.retentionDaysList.some(item => item.id === stringVal)) {
          this.retentionDaysList.push({
            id: stringVal,
            name: stringVal + this.$t('天'),
          });
        }
        this.formData.snapshot_days = stringVal;
        this.customRetentionDay = '';
        document.body.click();
      } else {
        this.customRetentionDay = '';
        this.messageError(this.$t('请输入有效数值'));
      }
    },
    async handleConfirm() {
      try {
        await this.$refs.validateForm.validate();
        let url = '/archive/createRestore';
        let paramsData = {
          ...this.formData,
          bk_biz_id: this.bkBizId,
        };
        const params = {};
        delete paramsData.datePickerValue;
        delete paramsData.datePickerExpired;
        this.confirmLoading = true;

        if (this.isEdit) {
          url = '/archive/editRestore';
          const { expired_time } = this.formData;
          const { restore_config_id } = this.editRestore;

          paramsData = {
            expired_time,
            restore_config_id,
          };
          // eslint-disable-next-line camelcase
          params.restore_config_id = restore_config_id;
        }

        await this.$http.request(url, {
          data: paramsData,
          params,
        });

        this.$bkMessage({
          theme: 'success',
          message: this.$t('保存成功'),
          delay: 1500,
        });
        this.$emit('updated');
      } catch (e) {
        console.warn(e);
      } finally {
        this.confirmLoading = false;
      }
    },
    async handleCloseSideslider() {
      return await this.showDeleteAlert();
    },
    /**
     * @desc: 如果提交可用则点击遮罩时进行二次确认弹窗
     */
    showDeleteAlert() {
      return new Promise((reject) => {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('pageLeaveTips'),
          confirmFn: () => {
            reject(true);
          },
          close: () => {
            reject(false);
          },
        });
      });
    },
  },
};
</script>

<style lang="scss">
  .restore-slider-content {
    min-height: 394px;
    height: calc(100vh - 60px);

    .bk-form.bk-form-vertical {
      padding: 10px 0 36px 36px;

      .bk-form-item {
        width: 500px;
        margin-top: 18px;
      }

      .bk-alert {
        width: 500px;
        margin-top: 12px;
      }

      .bk-select,
      .bk-date-picker {
        width: 300px;
      }

      .user-selector {
        /* stylelint-disable-next-line declaration-no-important */
        width: 500px !important;
      }
    }
  }
</style>
