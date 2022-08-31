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
      <bk-form-item :label="$t('应用类型')">
        <bk-select
          v-model="formData.workload_type"
          searchable>
          <bk-option
            v-for="(option, index) in typeList"
            :key="index"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t('应用名称')">
        <bk-select
          ref="loadSelectRef"
          :class="{ 'application': formData.workload_name, 'no-click': nameCannotClick }"
          v-model="formData.workload_name"
          allow-create
          searchable
          @toggle="(status) => isOptionOpen = status">
          <bk-option
            v-for="(option, index) in nameList"
            :key="`${option.name}_${index}`"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
        <span :class="['bk-icon', 'icon-angle-down', isOptionOpen && 'angle-rotate']"></span>
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
      isOptionOpen: false, // 是否展开了应用的下拉列表
      nameCannotClick: false, // 应用列表是否正在请求中
      typeList: [],
      nameList: [],
    };
  },
  computed: {},
  watch: {
    isShowDialog(val) {
      if (val) {
        Object.assign(this.formData, this.container);
        !this.typeList.length && this.getWorkLoadTypeList();
      };
    },
    'formData.workload_type'(val) {
      !!val ? this.getWorkLoadNameList(val) : this.nameList = [];
    },
    nameCannotClick(val) {
      const inputDOM = this.$refs.loadSelectRef.$refs.createInput;
      // input禁用样式
      val ? inputDOM.setAttribute('disabled', 'disabled') : inputDOM.removeAttribute('disabled');
    },
  },
  mounted() {
    this.$refs.loadSelectRef.$refs.createInput.placeholder = `${this.$t('请输入应用名称')}, ${this.$t('支持正则匹配')}`;
  },
  methods: {
    handelCancelDialog() {
      this.$emit('update:is-show-dialog', false);
    },
    async handelConfirmContainer() {
      const { workload_type, workload_name, container_name } = this.formData;
      const containerObj = {
        container: {
          workload_type,
          workload_name,
          container_name,
        },
      };
      this.$emit('configContainerChange', containerObj);
      this.$emit('update:is-show-dialog', false);
    },
    getWorkLoadTypeList() {
      this.nameCannotClick = true;
      this.$http.request('container/getWorkLoadType').then((res) => {
        if (res.code === 0) {
          this.typeList = res.data.map(item => ({ id: item, name: item }));
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.nameCannotClick = false;
        });
    },
    getWorkLoadNameList(type) {
      this.nameCannotClick = true;
      const { bk_biz_id, namespace, bcs_cluster_id } = this.container;
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
          this.nameCannotClick = false;
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
}

.application:hover + .icon-angle-down {
    display: none;
}

.icon-angle-down {
  position: absolute;
  font-size: 21px;
  color: #979ba5;
  right: 4px;
  top: 6px;
  transition: transform .3s;
}

.angle-rotate {
  transform: rotateZ(-180deg);
}

.no-click {
  pointer-events: none;
}
</style>
