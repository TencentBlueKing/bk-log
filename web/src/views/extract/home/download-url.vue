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
  <div class="list-box-container">
    <div class="list-title">
      <span class="bk-icon icon-download"></span>
      <h2 class="text">
        {{ $t('下载链接') }}
      </h2>
      <bk-button ref="button" theme="primary" style="margin-left: 20px;" :loading="loading" @click="handleClick">
        {{ $t('点击获取') }}
      </bk-button>
    </div>
    <bk-alert type="info" :title="$t('链接可重复获取，每个链接只能下载一次。')" style="margin-top: 10px;"></bk-alert>
  </div>
</template>

<script>
import Tippy from 'bk-magic-vue/lib/utils/tippy';

export default {
  props: {
    taskId: {
      type: Number,
      default: undefined,
    },
  },
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    async handleClick() {
      try {
        this.loading = true;
        const res = await this.$http.request('extract/getDownloadUrl', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
            task_id: this.taskId,
            is_url: true,
          },
        });

        const input = document.createElement('input');
        input.setAttribute('value', res.data);
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);

        const el = this.$refs.button.$el;
        if (!el._tippy) {
          el._tippy = Tippy(el, {
            content: this.$t('已复制到剪切板'),
            placement: 'top',
            trigger: 'manual',
            arrow: true,
            size: 'small',
            extCls: 'copy-successfully-tippy',
          });
        }
        el._tippy.show();
      } catch (e) {
        console.warn(e);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
