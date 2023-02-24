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
    :value="value"
    :width="840"
    :title="title"
    :show-footer="false"
    header-position="left"
    @value-change="handleVisibilityChange">
    <div style="padding-bottom: 20px;min-height: 200px;">
      <bk-table v-if="value" :data="filterList" :max-height="320">
        <bk-table-column label="ID" prop="id"></bk-table-column>
        <bk-table-column label="Name" prop="name"></bk-table-column>
        <bk-table-column label="Host" prop="host"></bk-table-column>
      </bk-table>
    </div>
  </bk-dialog>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    list: {
      type: Array,
      default() {
        return [];
      },
    },
    type: {
      type: String,
      default: 'hot',
    },
    formData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      title: '',
    };
  },
  computed: {
    filterList() {
      return this.list.filter((item) => {
        if (this.type === 'hot') {
          return item.attr === this.formData.hot_attr_name && item.value === this.formData.hot_attr_value;
        }
        return item.attr === this.formData.warm_attr_name && item.value === this.formData.warm_attr_value;
      });
    },
  },
  watch: {
    value(val) {
      if (val) {
        const isHot = this.type === 'hot';
        const name = isHot ? this.formData.hot_attr_name : this.formData.warm_attr_name;
        const value = isHot ? this.formData.hot_attr_value : this.formData.warm_attr_value;
        this.title = this.$t('包含属性 {n} 的节点列表', { n: `${name}:${value}` });
      }
    },
  },
  methods: {
    handleVisibilityChange(val) {
      this.$emit('input', val);
    },
  },
};
</script>
