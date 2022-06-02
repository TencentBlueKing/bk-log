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
    @confirm="handelConfirmContainer"
    @cancel="handelCancelDialog">
    <bk-form class="specify-container" form-type="vertical">
      <bk-form-item :label="$t('Workload类型')" required>
        <bk-select v-model="formData.workload_type">
          <bk-option
            v-for="option in selectList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t('Workload名称')" required>
        <bk-select
          v-model="formData.workload_name"
          allow-create
          searchable>
          <bk-option
            v-for="option in selectList"
            :key="option.id"
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
      selectValue: '',
      formData: {
        workload_type: '',
        workload_name: '',
        container_name: '',
      },
      selectList: [{
        name: '123',
        id: '3',
      },
      {
        name: '456',
        id: '4',
      },
      {
        name: '123',
        id: '5',
      },
      {
        name: '456',
        id: '6',
      }],
    };
  },
  watch: {
    isShowDialog(val) {
      if (val) {
        Object.assign(this.formData, this.container);
      } else {
        Object.assign(this.formData, {
          workload_type: '',
          workload_name: '',
          container_name: '',
        });
      }
    },
  },
  methods: {
    handelCancelDialog() {
      this.$emit('update:isShowDialog', false);
    },
    handelConfirmContainer() {
      const containerObj = {
        container: JSON.parse(JSON.stringify(this.formData)),
      };
      this.$emit('configContainerChange', containerObj);
      this.$emit('update:isShowDialog', false);
    },
  },
};
</script>
<style lang="scss" scoped>
.specify-container {
  .bk-form-control {
    width: 100%;
  }
}
</style>
