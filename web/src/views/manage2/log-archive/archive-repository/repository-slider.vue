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
  <div class="repository-slider-container">
    <bk-sideslider
      transfer
      :title="isEdit ? $t('logArchive.editRepository') : $t('logArchive.createRepository')"
      :is-show="showSlider"
      :width="676"
      :quick-close="false"
      @animation-end="$emit('hidden')"
      @update:isShow="updateIsShow">
      <div v-bkloading="{ isLoading: sliderLoading }" slot="content" class="repository-slider-content">
        <bk-form
          v-if="!sliderLoading"
          :model="formData"
          :label-width="150"
          :rules="basicRules"
          form-type="vertical"
          ref="validateForm"
          class="king-form">
          <h3 class="form-title">{{ $t('基础信息') }}</h3>
          <bk-form-item ext-cls="es-cluster-item" :label="$t('ES集群')" required>
            <bk-select></bk-select>
            <p class="es-source">
              <span>{{ $t('来源') }}：</span>
              <span>腾讯云</span>
            </p>
          </bk-form-item>
          <h3 class="form-title">{{ $t('logArchive.repositoryConfig') }}</h3>
          <bk-form-item :label="$t('logArchive.repositoryType')" ext-cls="repository-item" required>
            <div
              :class="{ 'repository-card': true, 'is-active': formData.repository === card.name }"
              v-for="card in repository"
              :key="card.name"
              @click="changeRepository(card)">
              <span class="repository-name">{{ card.name }}</span>
            </div>
          </bk-form-item>
          <bk-alert type="info">
            <div slot="title" class="repository-alert">
              <div v-if="formData.repository === 'HDFS'">
                <p>{{ $t('logArchive.repositoryAlert1') }}</p>
                <p>{{ $t('logArchive.repositoryAlert2') }}</p>
              </div>
              <div v-if="formData.repository === this.$t('logArchive.sharedDirectory')">
                <p>{{ $t('logArchive.repositoryAlert3') }}</p>
              </div>
              <div v-if="formData.repository === 'COS'">
                <p>{{ $t('logArchive.repositoryAlert4') }}</p>
              </div>
            </div>
          </bk-alert>
          <bk-form-item :label="$t('logArchive.repositoryName')" required>
            <bk-input></bk-input>
          </bk-form-item>
          <bk-form-item :label="$t('logArchive.archiveDirectory')" required>
            <bk-input></bk-input>
          </bk-form-item>
          <template v-if="formData.repository === 'HDFS'">
            <bk-form-item :label="$t('logArchive.HDFSAddr')" required>
              <bk-input></bk-input>
            </bk-form-item>
            <bk-form-item label="Principal" required>
              <div class="principal-item">
                <bk-switcher size="large" theme="primary"></bk-switcher>
                <bk-input></bk-input>
              </div>
            </bk-form-item>
          </template>
          <template v-if="formData.repository === 'COS'">
            <bk-form-item label="Secretld" required>
              <bk-input></bk-input>
            </bk-form-item>
            <bk-form-item label="SecretKey" required>
              <bk-input></bk-input>
            </bk-form-item>
            <bk-form-item label="APPID" required>
              <bk-input></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('logArchive.BlucketName')" required>
              <bk-input></bk-input>
            </bk-form-item>
          </template>
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
      repository: [
        { name: 'HDFS' },
        { name: this.$t('logArchive.sharedDirectory') },
        { name: 'COS' },
      ],
      formData: {
        retention: '1',
        repository: 'HDFS',
        notifiedUser: [],
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
        } else {
          //
        }
      } else {
        // 清空表单数据
        // this.formData = {

        // };
      }
    },
  },
  created() {
  },
  methods: {
    updateIsShow(val) {
      this.$emit('update:showSlider', val);
    },
    handleCancel() {
      this.$emit('update:showSlider', false);
    },
    changeRepository(card) {
      this.formData.repository = card.name;
    },
    handleConfirm() {

    },
  },
};
</script>

<style lang="scss">
  .repository-slider-content {
    min-height: 394px;
    .bk-form.bk-form-vertical {
      padding: 0 0 26px 36px;
      .bk-form-content {
        width: 500px;
      }
      .bk-form-item {
        margin-top: 12px;
        padding-left: 34px;
      }
      .bk-alert {
        width: 500px;
        margin: 10px 0 12px 34px;
      }
      .bk-select,
      .bk-date-picker {
        width: 300px;
      }
      .es-cluster-item {
        display: flex;
        margin-top: 16px;
        .bk-label {
          width: auto !important;
        }
        .bk-form-content {
          display: flex;
        }
        .bk-select {
          width: 240px;
        }
        .es-source {
          margin-left: 10px;
          font-size: 14px;
          color: #63656e;
        }
      }
      .repository-item {
        display: inline-block;
      }
      .repository-card {
        float: left;
        width: 158px;
        height: 76px;
        margin-right: 12px;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 2px;
        font-size: 14px;
        color: #63656e;
        border: 1px solid #f5f7fa;
        cursor: pointer;
        &:last-child {
          margin-right: 0;
        }
        &.is-active {
          color: #3a84ff;
          background: #e1ecff;
          border: 1px solid #a3c5fd;
        }
      }
    }
    .form-title {
      margin: 24px 0 0;
      padding: 0 0 8px 10px;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      line-height: 20px;
      border-bottom: 1px solid #dcdee5;
    }
    .repository-alert {
      padding-right: 10px;
    }
    .principal-item {
      display: flex;
      align-items: center;
      .bk-switcher {
        margin-right: 16px;
      }
      .bk-form-control {
        flex: 1;
      }
    }
  }
</style>
