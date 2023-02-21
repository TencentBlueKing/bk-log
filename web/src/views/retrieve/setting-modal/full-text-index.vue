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
  <!-- 设置-全文索引 -->
  <div>
    <bk-form :label-width="200">
      <!-- 大小写敏感 -->
      <bk-form-item :label="$t('大小写敏感')" :required="true">
        <bk-switcher
          class="ml200"
          theme="primary"
          size="large"
          v-model="formData.is_case_sensitive"
          :disabled="!globalEditable"></bk-switcher>
      </bk-form-item>
      <!-- 包含中文 -->
      <bk-form-item
        :label="$t('包含中文')"
        :required="true">
        <bk-switcher
          class="ml200"
          theme="primary"
          size="large"
          v-model="demo1"
          :disabled="!globalEditable">
        </bk-switcher>
      </bk-form-item>
      <!-- 分词符 -->
      <bk-form-item
        :label="$t('分词符')"
        :required="true"
        :property="''">
        <bk-input
          class="ml200 w240"
          v-model="formData.delimeter"
          :clearable="true"
          :disabled="!globalEditable">
        </bk-input>
      </bk-form-item>

      <bk-form-item class="ml200" style="margin-top: 40px;">
        <bk-button
          theme="primary"
          :title="$t('保存')"
          :disabled="!globalEditable"
          :loading="isHandle"
          @click.stop.prevent="handleSubmit">
          {{ $t('保存') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('重置')"
          :disabled="!globalEditable"
          @click="handleReset">
          {{ $t('重置') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('恢复默认')"
          :disabled="!globalEditable"
          @click="handleDefaultReset">
          {{ $t('恢复默认') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
export default {
  props: {
    globalEditable: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      demo1: true,
      rules: {},
      formData: {
        is_case_sensitive: 1, // 大小写敏感
        delimeter: '', // 分词符
      },
    };
  },
  mounted() {},
  methods: {
    handleSubmit() {},
    handleReset() {},
    handleDefaultReset() {},
  },
};
</script>

<style lang="scss" scoped>
  ::v-deep .bk-label {
    text-align: left;
  }

  .ml200 {
    margin-left: -200px;
  }

  .w240 {
    width: 240px;
  }
</style>
