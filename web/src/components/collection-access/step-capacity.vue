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
  <!-- <div
    v-if="!showApplyResult"
    v-bkloading="{ isLoading: applyLoading }"
    class="step-capacity-container"
    data-test-id="addNewCollectionItem_div_capacityContaineBox">
    <bk-form
      class="king-form"
      ref="formRef"
      form-type="vertical"
      :label-width="260"
      :model="formData"
      :rules="rules">
      <div class="form-double-container">
        <bk-form-item
          :label="$t('期待接入日期')"
          required
          property="expect_access_data">
          <bk-date-picker
            v-model="formData.expect_access_data" format="yyyy-MM-dd"
            data-test-id="capacityContaineBox_div_selectExpectedDate"
          ></bk-date-picker>
        </bk-form-item>
        <bk-form-item
          :label="$t('预计接入的主机数量')"
          required
          property="expect_host_size">
          <bk-input
            v-model="formData.expect_host_size"
            type="number"
            data-test-id="capacityContaineBox_input_estimatedNumber"
            :show-controls="false"
            :clearable="true">
          </bk-input>
        </bk-form-item>
      </div>
      <div class="form-double-container">
        <bk-form-item
          :label="$t('单条日志大小(Bytes)')"
          required
          property="single_log_size">
          <bk-input
            v-model="formData.single_log_size"
            type="number"
            data-test-id="capacityContaineBox_input_logSize"
            :show-controls="false"
            :clearable="true">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('单机流量峰值(KB/s)')"
          required
          property="single_host_peak">
          <bk-input
            v-model="formData.single_host_peak"
            type="number"
            data-test-id="capacityContaineBox_input_peakFlow"
            :show-controls="false"
            :clearable="true">
          </bk-input>
        </bk-form-item>
      </div>
      <div class="form-double-container">
        <bk-form-item
          :label="$t('单机增长日志量(G)')"
          required
          property="single_host_log_volume">
          <bk-input
            v-model="formData.single_host_log_volume"
            type="number"
            data-test-id="capacityContaineBox_input_increaseLogVolume"
            :show-controls="false"
            :clearable="true">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('日志保留天数')"
          required
          property="log_keep_days">
          <bk-input
            v-model="formData.log_keep_days"
            type="number"
            :show-controls="false"
            :clearable="true"
            data-test-id="capacityContaineBox_input_logRetentionDays"
          ></bk-input>
        </bk-form-item>
      </div>
      <div class="form-double-container">
        <bk-form-item
          :label="$t('热数据天数')"
          required
          property="hot_data_days">
          <bk-input
            v-model="formData.hot_data_days"
            type="number"
            :show-controls="false"
            :clearable="true"
            data-test-id="capacityContaineBox_input_hotDataDays"
          ></bk-input>
        </bk-form-item>
      </div>
      <bk-form-item :label="$t('容量说明')" class="text-form-item">
        <div class="capacity-description-container">
          <div>{{ $t('容量计算公式：') }}</div>
          <div class="content formula">
            <div class="column">
              <span>{{ $t('单机日志增量') }}</span>
              <span v-if="showComputedCapacity">{{ formData.single_host_log_volume }}</span>
            </div>
            <div class="column" v-if="showComputedCapacity">
              <span> * </span>
              <span> * </span>
            </div>
            <div class="column">
              <span>{{ $t('主机数量') }}</span>
              <span v-if="showComputedCapacity">{{ formData.expect_host_size }}</span>
            </div>
            <div class="column" v-if="showComputedCapacity">
              <span> * </span>
              <span> * </span>
            </div>
            <div class="column">
              <span>{{ $t('存储转化率') }}</span>
              <span v-if="showComputedCapacity">1.5</span>
            </div>
            <div class="column" v-if="showComputedCapacity">
              <span> * </span>
              <span> * </span>
            </div>
            <div class="column">
              <span>{{ $t('分片数') }}</span>
              <span v-if="showComputedCapacity">2</span>
            </div>
            <div class="column" v-if="showComputedCapacity">
              <span> * </span>
              <span> * </span>
            </div>
            <div class="column">
              <span>{{ $t('(日志保留天数 + 1)') }}</span>
              <span v-if="showComputedCapacity">{{ Number(formData.log_keep_days) + 1 }}</span>
            </div>
            <template v-if="showComputedCapacity">
              <div class="column">
                <span style="height: 18px;"></span>
                <span> = </span>
              </div>
              <div class="column">
                <span style="height: 18px;"></span>
                <span>{{ computedCapacity }}(GB)</span>
              </div>
            </template>
          </div>
          <div v-if="computedCapacity > maxCapacity || formData.single_host_peak > maxHostPeak">{{ $t('注意：') }}</div>
          <div v-if="computedCapacity > maxCapacity" class="content red">{{ $t('需要申请单独的ES集群') }}</div>
          <div v-if="formData.single_host_peak > maxHostPeak" class="content">{{ $t('采集器最大处理能力') }}</div>
          <div>{{ $t('说明：') }}</div>
          <div class="content">{{ $t('说明存储转化率') }}</div>
          <div class="content">{{ $t('说明分片数') }}</div>
        </div>
      </bk-form-item>
      <bk-form-item :label="$t('申请原因')" required property="apply_reason" class="text-form-item">
        <bk-input
          v-model="formData.apply_reason"
          type="textarea"
          :clearable="true"
          data-test-id="capacityContaineBox_input_applicationReason"
        ></bk-input>
      </bk-form-item>
    </bk-form>
    <div class="button-container">
      <template v-if="isApplySuccess">
        <bk-button style="margin-right: 10px;" @click="$emit('stepChange', 1)">{{ $t('上一步') }}</bk-button>
        <bk-button
          class="king-submit-button"
          theme="primary"
          data-test-id="capacityContaineBox_button_nextPage"
          :loading="submitLoading"
          @click="handleNext">
          {{ $t('下一步') }}
        </bk-button>
        <bk-button
          @click="handleCancel"
          data-test-id="capacityContaineBox_button_cancel"
        >{{ $t('返回列表') }}</bk-button>
      </template>
      <template v-else>
        <bk-button
          class="king-submit-button"
          theme="primary"
          :loading="submitLoading"
          data-test-id="capacityContaineBox_button_submit"
          @click="handleSubmit">
          {{ $t('提交') }}
        </bk-button>
        <bk-button
          @click="handleCancel"
          data-test-id="capacityContaineBox_button_cancel"
        >{{ $t('返回列表') }}</bk-button>
      </template>
    </div>
  </div> -->
  <div
    class="approval-detail-container">
    <bk-exception type="building">
      <div class="approval-text">
        <span>{{ applyData.collect_itsm_status_display }}</span>
        <a :href="applyData.ticket_url"
           class="button-text"
           target="_blank"
           data-test-id="capacityContaineBox_a_viewApprovalDetails">
          {{ $t('点击查看审批详情') }}
          <span class="log-icon icon-lianjie"></span>
        </a>
      </div>
    </bk-exception>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data() {
    return {
      maxCapacity: Number(window.ES_STORAGE_CAPACITY),
      maxHostPeak: 10240, // 单机流量峰值超过 10M 警告
      formData: {
        expect_access_data: '', // 期待接入日期 2020-01-01
        single_log_size: '', // 单条日志大小(bytes)
        single_host_peak: '', // 单机流量峰值(KB/s)
        single_host_log_volume: '', // 单机增长日志量(G)
        expect_host_size: '', // 预计接入的主机数量
        log_keep_days: '', // 日志保留天数
        hot_data_days: '', // 热数据天数
        apply_reason: '', // 申请原因
      },
      rules: {
        expect_access_data: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        single_log_size: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        single_host_peak: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        single_host_log_volume: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        expect_host_size: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        log_keep_days: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        hot_data_days: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        apply_reason: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
      },
      showApplyResult: false, // 显示审批详情/结果页面
      isApplySuccess: false, // 单据申请成功
      applyData: null, // 单据申请状态、数据
      applyLoading: false, // 获取单据申请数据 loading
      submitLoading: false, // 提交表单 loading
    };
  },
  computed: {
    ...mapGetters('collect', ['curCollect']),
    showComputedCapacity() {
      return this.formData.single_host_log_volume
              && this.formData.expect_host_size
              && this.formData.log_keep_days;
    },
    computedCapacity() {
      const logVolume = Number(this.formData.single_host_log_volume) || 0;
      const hostCount = Number(this.formData.expect_host_size) || 0;
      const keepDays = Number(this.formData.log_keep_days) || 0;
      const result = logVolume * hostCount * 3 * (keepDays + 1);
      return result.toFixed(0);
    },
  },
  created() {
    if (this.operateType === 'add') {
      // 新增、创建单据
    } else {
      switch (this.curCollect.itsm_ticket_status) {
        case 'not_apply':
          // 编辑、但是未创建单据，需要创建单据
          break;
        case 'applying':
          // 单据正在审批，查询单据状态
          this.showApplyResult = true;
          this.getApplyData();
          break;
        case 'fail_apply':
          // 单据被拒，重新创建单据
          break;
        case 'success_apply':
          this.isApplySuccess = true;
          this.getApplyData();
          // 审批通过，查询之前申请的数据，如果用户再对其修改，需要重新申请，如果不修改，进入下一步采集接入
          break;
      }
    }
  },
  methods: {
    // 1、编辑未完成采集项，之前已经申请过 ITSM 单据，查询单据状态
    // 2、编辑已通过审批的采集项，获取申请的数据回填表单
    async getApplyData() {
      try {
        this.applyLoading = true;
        const res = await this.$http.request('collect/queryItsmTicket', {
          params: {
            collector_config_id: this.curCollect.collector_config_id,
          },
        });
        if (this.isApplySuccess) {
          this.formDataCache = {
            expect_access_data: res.data.expect_access_data,
            single_log_size: res.data.single_log_size,
            single_host_peak: res.data.single_host_peak,
            single_host_log_volume: res.data.single_host_log_volume,
            expect_host_size: res.data.expect_host_size,
            log_keep_days: res.data.log_keep_days,
            hot_data_days: res.data.hot_data_days,
            apply_reason: res.data.apply_reason,
          };
          Object.assign(this.formData, this.formDataCache);
        } else {
          this.applyData = res.data;
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.applyLoading = false;
      }
    },
    async handleSubmit() {
      try {
        this.submitLoading = true;
        await this.$refs.formRef.validate();
        const res = await this.$http.request('collect/applyItsmTicket', {
          params: {
            collector_config_id: this.curCollect.collector_config_id,
          },
          data: {
            ...this.formData,
            expect_access_data: this.formatDate(this.formData.expect_access_data),
          },
        });
        this.applyData = res.data;
        this.showApplyResult = true;
      } catch (e) {
        console.warn(e);
      } finally {
        this.submitLoading = false;
      }
    },
    formatDate(date) {
      try {
        const yyyy = date.getFullYear();
        const mm = (`0${date.getMonth() + 1}`).slice(-2);
        const dd = (`0${date.getDate()}`).slice(-2);
        return `${yyyy}-${mm}-${dd}`;
      } catch (e) {
        console.warn('无效的时间', e);
        return '';
      }
    },
    async handleNext() {
      if (this.judgeIsModified()) { // 修改了表单，重新提交
        return this.handleSubmit();
      }
      // 没有修改，第一步调用了 only_update，这里需要调用 update，再进入下一步采集接入
      try {
        this.submitLoading = true;
        await this.$http.request('collect/updateCollection', JSON.parse(sessionStorage.getItem('collectionUpdateData')));
        this.$emit('stepChange', 3);
      } catch (e) {
        console.warn(e);
      } finally {
        this.submitLoading = false;
      }
    },
    // 判断之前提交的已经通过的单据是否被修改
    judgeIsModified() {
      const newFormData = {
        ...this.formData,
        expect_access_data: this.formatDate(this.formData.expect_access_data),
      };
      for (const key of Object.keys(newFormData)) {
        if (newFormData[key] !== this.formDataCache[key]) {
          return true;
        }
      }
      return false;
    },
    handleCancel() {
      this.$router.push({
        name: 'collection-item',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .step-capacity-container {
    height: 100%;

    .king-form {
      padding: 24px 60px;

      .form-double-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 800px;

        .bk-form-item {
          width: 350px;
          margin: 0;
        }

        :deep(.bk-date-picker) {
          width: 100%;
        }
      }

      .text-form-item {
        width: 800px;

        .capacity-description-container {
          padding: 5px 10px;
          line-height: 18px;
          color: #63656e;
          background-color: #fafbfd;
          border: 1px solid #c4c6cc;
          border-radius: 2px;
          font-size: 12px;

          .content {
            margin-left: 24px;
          }

          .red {
            color: #ea3636;
          }

          .formula {
            display: flex;

            .column {
              display: flex;
              flex-flow: column;
              white-space: pre-wrap;
              text-align: center;
            }
          }
        }
      }
    }

    .button-container {
      padding: 0 60px 100px;

      .king-submit-button {
        min-width: 86px;
        margin-right: 10px;
      }
    }
  }

  .approval-detail-container {
    height: 100%;
    padding-top: 100px;
    font-size: 14px;

    .approval-text {
      display: flex;
      flex-flow: column;
      font-size: 16px;

      .button-text {
        margin-top: 16px;
      }
    }
  }
</style>
