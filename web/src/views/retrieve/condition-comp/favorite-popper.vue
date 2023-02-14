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
    class="favorite-popper-content">
    <div class="title">{{ $t('是否替换当前收藏') }}({{activeFavorite.name}})？</div>
    <div class="content">
      <bk-button text size="small" @click="handleOperate('replace')">{{ $t('替换当前') }}</bk-button>
      <bk-button text size="small" @click="handleOperate('add')">{{ $t('新建') }}</bk-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    activeFavorite: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      value: '',
    };
  },
  computed: {
  },
  methods: {
    handleOperate(type) {
      if (type === 'add') {
        this.$emit('favoriteTipsOperate', 'add-new');
      } else {
        this.$emit('favoriteTipsOperate', 'replace');
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .favorite-popper-content {
    min-width: 200px;
    padding: 2px;
    // word-wrap: ;

    .title {
      margin-bottom: 10px;
      font-size: 12px;
      line-height: 20px;
      color: #63656e;
    }

    .content {
      text-align: right;

      .bk-button-text {
        padding: 0 6px;
      }
    }
  }
</style>
