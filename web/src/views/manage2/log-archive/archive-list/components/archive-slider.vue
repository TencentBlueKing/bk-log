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
  <div class="archive-slider-container">
    <bk-sideslider
      transfer
      :title="isEdit ? $t('logArchive.editArchive') : $t('logArchive.createArchive')"
      :is-show="showSlider"
      :width="676"
      :quick-close="false"
      @animation-end="$emit('hidden')"
      @update:isShow="updateIsShow">
      <div v-bkloading="{ isLoading: sliderLoading }" slot="content" class="archive-slider-content">
        <bk-form
          v-if="!sliderLoading"
          :model="formData"
          :label-width="150"
          :rules="basicRules"
          form-type="vertical"
          ref="validateForm"
          class="king-form">
          <bk-form-item :label="$t('logArchive.collectFormLabel')" required property="cluster_name">
            <bk-select></bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('logArchive.archiveRepository')" required property="cluster_name">
            <bk-select></bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('过期时间')" required property="cluster_name">
            <bk-select style="width: 300px;" v-model="formData.retention" :clearable="false">
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
          <bk-form-item style="margin-top:40px;">
            <bk-button
              theme="primary"
              class="king-button mr10"
              :loading="confirmLoading"
              @click.stop.prevent="handleConfirm">
              {{ $t('提交') }}
            </bk-button>
            <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    showSlider: {
      type: Boolean,
      default: false,
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
      customRetentionDay: '', // 自定义过期天数
      retentionDaysList: [], // 过期天数列表
      formData: {
        retention: '1',
      },
      basicRules: {

      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    isEdit() {
      return this.archiveId !== null;
    },
  },
  watch: {
    showSlider(val) {
      if (val) {
        if (this.isEdit) {
          this.editDataSource();
        } else {
          //
        }
      } else {
        // 清空表单数据
        this.formData = {

        };
      }
    },
  },
  methods: {
    updateIsShow(val) {
      this.$emit('update:showSlider', val);
    },
    handleCancel() {
      this.$emit('update:showSlider', false);
    },
    // 输入自定义过期天数、冷热集群存储期限
    enterCustomDay() {
      // const numberVal = parseInt(val.trim(), 10);
      // const stringVal = numberVal.toString();
      // const isRetention = type === 'retention'; // 过期时间 or 热数据存储时间
      // if (numberVal) {
      //   const maxDays = this.selectedStorageCluster.max_retention || 30;
      //   if (numberVal > maxDays) { // 超过最大天数
      //     isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
      //     this.messageError(this.$t('最大自定义天数为') + maxDays);
      //   } else {
      //     if (isRetention) {
      //       if (!this.retentionDaysList.some(item => item.id === stringVal)) {
      //         this.retentionDaysList.push({
      //           id: stringVal,
      //           name: stringVal + this.$t('天'),
      //         });
      //       }
      //       this.formData.retention = stringVal;
      //       this.customRetentionDay = '';
      //     } else {
      //       if (!this.hotDataDaysList.some(item => item.id === stringVal)) {
      //         this.hotDataDaysList.push({
      //           id: stringVal,
      //           name: stringVal + this.$t('天'),
      //         });
      //       }
      //       this.formData.allocation_min_days = stringVal;
      //       this.customHotDataDay = '';
      //     }
      //     document.body.click();
      //   }
      // } else {
      //   isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
      //   this.messageError(this.$t('请输入有效数值'));
      // }
    },
    handleConfirm() {},
  },
};
</script>

<style lang="scss" scoped>
  .archive-slider-content {
    min-height: 394px;
    .king-form {
      padding: 10px 0 36px 36px;
      .bk-form-item {
        margin-top: 18px;
      }
      .bk-select {
        width: 300px;
      }
    }
  }
</style>
