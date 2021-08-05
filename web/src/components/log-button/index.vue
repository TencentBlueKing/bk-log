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
  <section v-bk-tooltips="tipsConf">
    <bk-button
      :theme="theme"
      :text="text"
      class="mr10 king-button"
      :disabled="!props.row.bkdata_auth_url"
      v-cursor="{ active: !(props.row.permission && props.row.permission.manage_collection) }"
      @click.stop="operateHandler(props.row, 'delete')">
      {{ $t('btn.delete') }}
    </bk-button>
  </section>
</template>

<script>
export default {
  props: {
    theme: {
      type: String,
      default: 'dark',
    },
    text: {
      type: Boolean,
      default: false,
    },
    tipsConf: {
      // eslint-disable-next-line vue/require-prop-type-constructor
      type: Object | String,
      default: '',
    },
  },
};
</script>

