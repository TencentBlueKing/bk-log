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
    <bk-form :label-width="100">
      <bk-form-item
        :label="$t('大小写敏感')"
        :required="true"
        :property="''">
        <br>
        <bk-switcher class="ml100" v-model="demo1" theme="primary" size="large"></bk-switcher>
      </bk-form-item>
      <bk-form-item
        :label="$t('包含中文')"
        :required="true"
        :property="''">
        <br>
        <bk-switcher class="ml100" v-model="demo1" theme="primary" size="large"></bk-switcher>
      </bk-form-item>
      <bk-form-item
        :label="$t('分词符')"
        :required="true"
        :property="''">
        <br>
        <bk-input class="ml100 w240" :clearable="true" v-model="value"></bk-input>
      </bk-form-item>
      <bk-form-item class="ml100" style="margin-top: 40px">
        <bk-button
          theme="primary"
          :title="$t('保存')"
          @click.stop.prevent="handleSubmit"
          :loading="isHandle">
          {{ $t('保存') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('重置')"
          @click="cancel">
          {{ $t('重置') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('恢复默认')"
          @click="handleReset">
          {{ $t('恢复默认') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      demo1: true,
      rules: {},
      value: '',
      isHandle: false,
    };
  },
  methods: {
    handleSubmit() {},
    cancel() {},
    handleReset() {},
  },
};
</script>

<style lang="scss" scoped>
  /deep/ .bk-label{
    text-align: left;
  }
  .ml100{
    margin-left: -100px;
  }
  .w240{
    width: 240px;
  }
</style>
