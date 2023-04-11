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
  <bk-dialog
    :value="visible"
    :mask-close="false"
    :close-icon="false"
    :width="800"
    :position="{ top: '120' }"
    :loading="confirmLoading"
    :title="dialogTitle"
    header-position="left"
    @confirm="handleConfirm"
    @cancel="closeDialog">
    <div class="link-config-form" data-test-id="addNewLinkConfig_div_linkConfigForm">
      <bk-form
        class="king-form"
        ref="form"
        :label-width="220"
        :model="formData"
        :rules="rules">
        <bk-form-item
          :label="$t('链路名称')"
          required
          property="link_group_name"
          error-display-type="normal">
          <bk-input
            data-test-id="linkConfigForm_div_linkName"
            v-model="formData.link_group_name"
            :clearable="true"
            style="width: 380px;"></bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('允许的空间')"
          required
          property="bk_biz_id"
          error-display-type="normal">
          <bk-select
            data-test-id="linkConfigForm_select_selectPermitted"
            v-model="formData.bk_biz_id"
            searchable
            :clearable="false"
            style="width: 380px;">
            <template v-for="item in projectList">
              <bk-option
                :key="item.bk_biz_id"
                :id="item.bk_biz_id"
                :name="item.space_full_code_name">
                <div class="space-code-option">
                  <span class="code-name" :title="item.space_full_code_name">{{item.space_full_code_name}}</span>
                  <div v-if="item.space_type_id" class="list-item-right">
                    <span :class="['list-item-tag', 'light-theme', item.space_type_id || 'other-type']">
                      {{item.space_type_name}}
                    </span>
                  </div>
                </div>
              </bk-option>
            </template>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          label="Kafka"
          required
          property="kafka_cluster_id"
          error-display-type="normal">
          <bk-select
            data-test-id="linkConfigForm_select_selectKafka"
            v-model="formData.kafka_cluster_id"
            :clearable="false"
            style="width: 380px;">
            <template v-for="item in selectData.kafka">
              <bk-option
                :key="item.cluster_id"
                :id="item.cluster_id"
                :name="item.cluster_name">
              </bk-option>
            </template>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          label="Transfer"
          required
          property="transfer_cluster_id"
          error-display-type="normal">
          <bk-select
            data-test-id="linkConfigForm_select_selectTransfer"
            v-model="formData.transfer_cluster_id"
            :clearable="false"
            style="width: 380px;">
            <template v-for="item in selectData.transfer">
              <bk-option
                :key="item.cluster_id"
                :id="item.cluster_id"
                :name="item.cluster_name">
              </bk-option>
            </template>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          :label="$t('ES集群')"
          required
          property="es_cluster_ids"
          error-display-type="normal">
          <bk-select
            data-test-id="linkConfigForm_select_selectEsClusterIds"
            v-model="formData.es_cluster_ids"
            :clearable="false"
            multiple
            style="width: 380px;">
            <template v-for="item in selectData.es">
              <bk-option
                :key="item.cluster_id"
                :id="item.cluster_id"
                :name="item.cluster_name">
              </bk-option>
            </template>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          :label="$t('是否启用')"
          property="is_active"
          error-display-type="normal">
          <bk-checkbox
            v-model="formData.is_active"
            data-test-id="linkConfigForm_checkbox_isEnable"
          ></bk-checkbox>
        </bk-form-item>
        <bk-form-item
          :label="$t('备注')"
          property="description"
          error-display-type="normal">
          <bk-input
            data-test-id="linkConfigForm_input_Remark"
            v-model="formData.description"
            type="textarea"
            :maxlength="64"
            :clearable="true"
            style="width: 380px;">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </div>
  </bk-dialog>
</template>

<script>
export default {
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    type: {
      type: String,
      default: 'create',
    },
    projectList: {
      type: Array,
      required: true,
    },
    dataSource: {
      type: Object,
      default() {
        return {};
      },
    },
    selectData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      dialogTitle: '',
      confirmLoading: false,
      formData: {},
      rules: {
        link_group_name: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        bk_biz_id: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        kafka_cluster_id: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        transfer_cluster_id: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
        es_cluster_ids: [{
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        }],
      },
    };
  },
  watch: {
    visible(val) {
      if (val) {
        this.dialogTitle = this.type === 'create' ? this.$t('新建链路配置') : this.$t('编辑链路配置');
        this.formData = JSON.parse(JSON.stringify(this.dataSource));
        this.$refs.form.clearError();
      }
    },
  },
  methods: {
    async handleConfirm() {
      try {
        this.confirmLoading = true;
        await this.$refs.form.validate();
        const formData = { ...this.formData };
        formData.bk_biz_id = Number(formData.bk_biz_id);
        if (this.type === 'create') { // 新建
          await this.$http.request('linkConfiguration/createLink', {
            data: formData,
          });
          this.messageSuccess(this.$t('创建成功'));
        } else { // 编辑
          await this.$http.request('linkConfiguration/updateLink', {
            data: formData,
            params: {
              data_link_id: this.formData.data_link_id,
            },
          });
          this.messageSuccess(this.$t('修改成功'));
        }
        this.$emit('showUpdateList');
        this.closeDialog();
      } catch (e) {
        console.warn(e);
        await this.$nextTick();
        this.$emit('update:visible', true);
      } finally {
        this.confirmLoading = false;
      }
    },
    closeDialog() {
      // 通过父组件关闭对话框
      this.$emit('update:visible', false);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '@/scss/space-tag-option';

  .link-config-form {
    :deep(.bk-form-content) {
      position: relative;

      .form-error-tip {
        position: absolute;
        top: 32px;
        margin: 0;
      }
    }
  }
</style>
