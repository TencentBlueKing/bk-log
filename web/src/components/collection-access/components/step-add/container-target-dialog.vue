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
    width="480"
    theme="primary"
    header-position="left"
    :value="isShowDialog"
    :mask-close="false"
    :title="$t('指定容器')"
    :auto-close="false"
    :confirm-fn="handelConfirmContainer"
    @cancel="handelCancelDialog">
    <bk-form
      class="specify-container"
      form-type="vertical"
      ref="containerFormRef"
      :model="formData">
      <bk-form-item :label="$t('Workload类型')" required>
        <bk-select
          :class="`${typeError && 'type-error'}`"
          v-model="formData.workload_type">
          <bk-option
            v-for="(option, index) in typeList"
            :key="index"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t('Workload名称')" required>
        <bk-select
          :class="`${nameError && 'name-error'}`"
          v-model="formData.workload_name"
          :disabled="nameIsLoading"
          allow-create
          searchable>
          <bk-option
            v-for="(option, index) in nameList"
            :key="`${option}_${index}`"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t('容器名称')">
        <bk-input v-model="formData.container_name"></bk-input>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>
<script>
export default {
  props: {
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    container: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      formData: {
        workload_type: '',
        workload_name: '',
        container_name: '',
      },
      typeError: false,
      nameError: false,
      nameIsLoading: false,
      typeList: [],
      nameList: [],
    };
  },
  computed: {},
  watch: {
    isShowDialog(val) {
      if (val) {
        Object.assign(this.formData, this.container);
        this.getWorkLoadTypeList();
      } else {
        setTimeout(() => {
          Object.assign(this.formData, {
            workload_type: '',
            workload_name: '',
            container_name: '',
          });
          this.nameList = [];
          this.typeList = [];
        }, 300);
      }
    },
    'formData.workload_type'(val) {
      this.typeError = false;
      this.getWorkLoadNameList(val);
    },
    'formData.workload_name'() {
      this.nameError = false;
    },
  },
  methods: {
    handelCancelDialog() {
      this.$emit('update:is-show-dialog', false);
    },
    async handelConfirmContainer() {
      const { workload_type: type, workload_name: name, container_name } = this.formData;
      type === '' && (this.typeError = true);
      name === '' && (this.nameError = true);
      if (!name || !type) return;
      const containerObj = {
        container: {
          workload_type: type,
          workload_name: name,
          container_name,
        },
      };
      this.$emit('configContainerChange', containerObj);
      this.$emit('update:is-show-dialog', false);
    },
    getWorkLoadTypeList() {
      this.$http.request('container/getWorkLoadType').then((res) => {
        if (res.code === 0) {
          this.typeList = res.data.map(item => ({ id: item, name: item }));
        }
      })
        .catch((err) => {
          console.warn(err);
        });
    },
    getWorkLoadNameList(type) {
      this.nameIsLoading = true;
      const { bk_biz_id, namespace, bcs_cluster_id } =  this.container;
      const query = { type, bk_biz_id, namespace, bcs_cluster_id };
      if (!namespace) delete query.namespace;
      this.$http.request('container/getWorkLoadName', { query }).then((res) => {
        if (res.code === 0) {
          this.nameList = res.data.map(item => ({ id: item, name: item }));
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.nameIsLoading = false;
        });;
    },
  },
};
</script>
<style lang="scss" scoped>
.specify-container {
  .bk-form-control {
    width: 100%;
  }

  .type-error,
  .name-error {
    border-color: #ff5656;
  }
}
</style>
