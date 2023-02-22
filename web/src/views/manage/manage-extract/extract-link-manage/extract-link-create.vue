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
    class="extract-link-create-container"
    v-bkloading="{ isLoading: basicLoading }"
    data-test-id="extractLinkCreate_div_extractLinkCreateBox">
    <article
      class="article"
      data-test-id="extractLinkCreateBox_article_basicInformation">
      <h3 class="title">{{ $t('基础信息') }}</h3>
      <bk-form
        class="king-form"
        ref="formRef"
        :label-width="160"
        :model="formData"
        :rules="formRules">
        <bk-form-item
          :label="$t('链路名称')"
          required
          property="name">
          <bk-input
            v-model="formData.name"
            data-test-id="basicInformation_input_linkName">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('链路类型')"
          required
          property="link_type">
          <bk-select
            data-test-id="basicInformation_select_selectLinkType"
            v-model="formData.link_type"
            :clearable="false">
            <bk-option id="common" :name="$t('内网链路')"></bk-option>
            <bk-option id="qcloud_cos" :name="$t('腾讯云链路')"></bk-option>
            <bk-option id="bk_repo" :name="$t('bk_repo链路')"></bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          :label="$t('执行人')"
          required
          property="operator">
          <bk-user-selector
            data-test-id="basicInformation_input_executive"
            :class="isAdminError && 'is-error'"
            :value="formData.operator"
            :api="userApi"
            @focus="handleClearOperator"
            @change="handleUserChange"
            @blur="handleBlur">
          </bk-user-selector>
        </bk-form-item>
        <bk-form-item
          :label="$t('执行bk_biz_id')"
          required
          property="op_bk_biz_id">
          <bk-input
            v-model="formData.op_bk_biz_id"
            data-test-id="basicInformation_input_executivebk_biz_id"
          ></bk-input>
        </bk-form-item>
        <template v-if="formData.link_type === 'qcloud_cos'">
          <bk-form-item
            :label="$t('腾讯云SecretId')"
            required
            property="qcloud_secret_id">
            <bk-input
              v-model="formData.qcloud_secret_id"
              data-test-id="basicInformation_input_SecretId">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t('腾讯云SecretKey')"
            required
            property="qcloud_secret_key">
            <bk-input
              v-model="formData.qcloud_secret_key"
              data-test-id="basicInformation_input_SecretKey"
            ></bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t('腾讯云Cos桶名称')"
            required
            property="qcloud_cos_bucket">
            <bk-input
              v-model="formData.qcloud_cos_bucket"
              data-test-id="basicInformation_input_cosBucket"
            ></bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t('腾讯云Cos区域')"
            required
            property="qcloud_cos_region">
            <bk-input
              v-model="formData.qcloud_cos_region"
              data-test-id="basicInformation_input_cosRegion"
            ></bk-input>
          </bk-form-item>
        </template>
        <bk-form-item
          :label="$t('是否启用')"
          required
          property="is_enable">
          <bk-radio-group
            v-model="formData.is_enable"
            data-test-id="basicInformation_radio_whetherToEnable">
            <bk-radio :value="true" style="margin-right: 16px;">{{ $t('是') }}</bk-radio>
            <bk-radio :value="false">{{ $t('否') }}</bk-radio>
          </bk-radio-group>
        </bk-form-item>
      </bk-form>
    </article>
    <article class="article" data-test-id="extractLinkCreateBox_article_linkTransfer">
      <h3 class="title">{{ $t('链路中转机') }}</h3>
      <div class="custom-form">
        <div class="custom-label">{{ $t('中转机') }}</div>
        <div class="custom-content">
          <ul class="host-list" ref="hostListRef">
            <li class="host-item header">
              <div class="min-box dir-container">{{ $t('挂载目录') }}</div>
              <div class="min-box id-container">{{ $t('主机云区域ID') }}</div>
              <div class="min-box ip-container">{{ $t('主机IP') }}</div>
              <div class="min-box operation-container">{{ $t('操作') }}</div>
            </li>
            <li
              class="host-item"
              v-for="(item, index) in formData.hosts"
              :key="item.keyId">
              <div class="min-box dir-container">
                <bk-input
                  class="king-input"
                  v-model="item.target_dir"
                  @blur="handleInputBlur">
                </bk-input>
              </div>
              <div class="min-box id-container">
                <bk-input
                  class="king-input"
                  v-model="item.bk_cloud_id"
                  @blur="handleInputBlur">
                </bk-input>
              </div>
              <div class="min-box ip-container">
                <bk-input
                  class="king-input"
                  v-model="item.ip"
                  @blur="handleInputBlur">
                </bk-input>
              </div>
              <div class="min-box operation-container">
                <bk-button
                  text size="small"
                  style="padding: 0;"
                  :disabled="formData.hosts.length === 1"
                  @click="deleteHost(index)">{{ $t('删除') }}
                </bk-button>
              </div>
            </li>
          </ul>
          <bk-button class="king-button" @click="addHost">{{ $t('添加链路中转机') }}</bk-button>
        </div>
      </div>
    </article>
    <bk-button
      theme="primary"
      style="width: 86px;"
      :loading="submitLoading"
      data-test-id="basicInformation_button_submitFrom"
      @click="submitForm">
      {{ $t('提交') }}
    </bk-button>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import BkUserSelector from '@blueking/user-selector';

export default {
  name: 'ExtractLinkCreate',
  components: {
    BkUserSelector,
  },
  data() {
    return {
      basicLoading: false,
      submitLoading: false,
      isSubmit: false,
      userApi: window.BK_LOGIN_URL,
      formData: {
        name: '',
        link_type: 'common',
        operator: [],
        op_bk_biz_id: '',
        qcloud_secret_id: '', // 腾讯云SecretId
        qcloud_secret_key: '', // 腾讯云SecretKey
        qcloud_cos_bucket: '', // 腾讯云Cos桶名称
        qcloud_cos_region: '', // 腾讯云Cos区域
        is_enable: true, // 是否启用
        hosts: [{
          keyId: Date.now(),
          target_dir: '', // 挂载目录
          bk_cloud_id: '', // 主机云区域id
          ip: '', // 主机ip
        }], // 中转机列表
      },
      formRules: {
        name: [{
          required: true,
          trigger: 'blur',
        }],
        op_bk_biz_id: [{
          required: true,
          trigger: 'blur',
        }],
        qcloud_secret_key: [{
          required: true,
          trigger: 'blur',
        }],
        qcloud_cos_bucket: [{
          required: true,
          trigger: 'blur',
        }],
        qcloud_secret_id: [{
          required: true,
          trigger: 'blur',
        }],
        qcloud_cos_region: [{
          required: true,
          trigger: 'blur',
        }],
      },
      isAdminError: false, // 人员是否为空
      cacheOperator: [], // 缓存的人员
    };
  },
  computed: {
    ...mapState({
      showRouterLeaveTip: state => state.showRouterLeaveTip,
    }),
  },
  created() {
    this.init();
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit && !this.showRouterLeaveTip) {
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
  methods: {
    async init() {
      const linkId = this.$route.params.linkId;
      if (linkId) {
        try {
          this.basicLoading = true;
          const res = await this.$http.request('extractManage/getLogExtractLinkDetail', {
            params: {
              link_id: linkId,
            },
          });
          const formData = res.data;
          delete formData.link_id;
          formData.hosts.forEach((item, index) => {
            item.keyId = index;
          });
          // 字符串转成数组展示
          formData.operator = [formData.operator];
          this.formData = Object.assign({}, this.formData, formData);
          this.basicLoading = false;
        } catch (e) {
          console.warn(e);
          this.$router.push({
            name: 'extract-link-list',
            query: {
              spaceUid: this.$store.state.spaceUid,
            },
          });
        }
      }
    },
    addHost() {
      this.formData.hosts.push({
        keyId: Date.now(),
        target_dir: '', // 挂载目录
        bk_cloud_id: '', // 主机云区域id
        ip: '', // 主机ip
      });
    },
    deleteHost(index) {
      this.formData.hosts.splice(index, 1);
    },
    handleInputBlur(value, event) {
      if (value) {
        event.target.classList.remove('error');
      } else {
        event.target.classList.add('error');
      }
    },
    async submitForm() {
      try {
        let isError = false;
        const inputList = this.$refs.hostListRef.getElementsByClassName('bk-form-input');
        for (const inputEl of inputList) {
          if (!inputEl.value) {
            isError = true;
            inputEl.classList.add('error');
          } else {
            inputEl.classList.remove('error');
          }
        }
        await this.$refs.formRef.validate();
        if (isError || this.isAdminError) return;
        this.submitLoading = true;
        const requestData = { ...this.formData };
        if (requestData.link_type === 'common') {
          delete requestData.qcloud_cos_bucket;
          delete requestData.qcloud_cos_region;
          delete requestData.qcloud_secret_id;
          delete requestData.qcloud_secret_key;
        }
        requestData.hosts.forEach((host) => {
          delete host.keyId;
        });
        // 数组修改为字符串传参
        requestData.operator = requestData.operator[0];
        const linkId = this.$route.params.linkId;
        if (linkId) {
          await this.$http.request('extractManage/updateLogExtractLink', {
            params: {
              link_id: linkId,
            },
            data: requestData,
          });
          this.messageSuccess(this.$t('保存成功'));
        } else {
          await this.$http.request('extractManage/createLogExtractLink', {
            data: requestData,
          });
          this.messageSuccess(this.$t('创建成功'));
        }
        this.isSubmit = true;
        this.$router.push({
          name: 'extract-link-list',
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
      } catch (e) {
        console.warn(e);
        this.submitLoading = false;
      }
    },
    handleUserChange(val) {
      const realVal = val.filter(item => item !== undefined);
      this.isAdminError = !realVal.length;
      this.formData.operator = realVal;
      this.cacheOperator = realVal;
    },
    handleClearOperator() {
      if (this.formData.operator.length) {
        this.cacheOperator = this.formData.operator;
        this.formData.operator = [];
      }
    },
    handleBlur() {
      if (this.cacheOperator.length) {
        this.formData.operator = this.cacheOperator;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../../scss/mixins/scroller';

  .extract-link-create-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;

    @include scroller($backgroundColor: #ADADAD, $width: 4px);

    .article {
      padding: 22px 24px;
      margin-bottom: 20px;
      border: 1px solid #dcdee5;
      border-radius: 3px;
      background-color: #fff;

      .title {
        margin: 0 0 10px;
        font-size: 14px;
        font-weight: bold;
        color: #63656e;
        line-height: 20px;
      }

      .king-form {
        width: 680px;

        ::v-deep .bk-form-item {
          padding: 10px 0;
          margin: 0;
        }
      }

      .custom-form {
        display: flex;
        font-size: 14px;
        color: #63656e;

        .custom-label {
          position: relative;
          width: 160px;
          padding: 10px 24px 10px 0;
          line-height: 32px;
          text-align: right;

          &:after {
            content: '*';
            color: #ea3636;
            font-size: 12px;
            display: inline-block;
            position: absolute;
            top: 12px;
            right: 16px;
          }
        }

        .custom-content {
          width: calc(100% - 160px);
          max-width: 1000px;
          padding: 5px 24px 5px 0;

          .king-button {
            margin-top: 10px;
          }
        }

        .host-list {
          border: 1px solid #dcdee5;
          border-bottom: none;
          font-size: 12px;

          .host-item {
            display: flex;
            align-content: center;
            width: 100%;
            line-height: 32px;
            padding: 5px 0;
            border-bottom: 1px solid #dcdee5;
            background-color: #fff;

            &.header {
              background-color: #fafbfd;
            }

            .min-box {
              padding: 0 10px;

              .king-input {
                width: 86%;

                ::v-deep .bk-form-input.error {
                  border-color: #ea3636;
                }
              }

              &.dir-container {
                width: 40%;
              }

              &.id-container,
              &.ip-container {
                width: 25%;
              }

              &.operation-container {
                width: 10%;
              }
            }
          }
        }
      }
    }

  }

  ::v-deep .user-selector {
    width: 100%;
  }

  ::v-deep .is-error .user-selector-container {
    border-color: #ff5656;
  }
</style>
