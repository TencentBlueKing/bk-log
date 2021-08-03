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
  <div class="advance-clean-land" v-bkloading="{ isLoading: loading }">
    <span class="bk-icon icon-clock"></span>
    <p class="title">{{ $t('logClean.cleaning') }}</p>
    <p class="remark">
      <span v-if="isInit">
        <span v-if="resultList.length">{{ `${resultList.join('、')}${$t('logClean.finishClean')}` }}</span>
        <span v-else>{{ $t('logClean.cleaningConfirmTips') }}</span>
      </span>
      <span v-else>{{ $t('logClean.cleaningTips') }}</span>
    </p>
    <div class="refresh-button">
      <span class="bk-icon icon-refresh-line"></span>
      <span @click="handleRefresh">{{ $t('刷新') }}</span>
    </div>
    <bk-button class="back-list">{{ $t('返回列表') }}</bk-button>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    dataId: {
      type: String,
      dafault: '',
    },
    collectorId: {
      type: String,
      dafault: '',
    },
  },
  data() {
    return {
      loading: false,
      isInit: false,
      resultList: [], // 清洗结果
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
  },
  methods: {
    handleRefresh() {
      this.isInit = true;
      this.loading = true;
      this.$http.request('clean/refreshClean', {
        params: {
          collector_config_id: this.collectorId,
        },
        query: {
          bk_biz_id: this.bkBizId,
          bk_data_id: this.dataId,
        },
      }).then((res) => {
        this.resultList = res.data;
      })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style lang="scss">
  .advance-clean-land {
    padding-top: 210px;
    text-align: center;
    .icon-clock {
      font-size: 64px;
      color: #c4c6cc;
    }
    .title {
      margin-top: 18px;
      font-size: 16px;
      color: #000;
    }
    .remark {
      margin-top: 10px;
      font-size: 12px;
      color: #63656e;
    }
    .refresh-button {
      margin: 18px 0 20px;
      color: #3a84ff;
      font-size: 12px;
      cursor: pointer;
    }
  }
</style>
