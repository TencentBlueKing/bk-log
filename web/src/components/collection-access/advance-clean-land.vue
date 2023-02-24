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
    <span class="log-icon icon-shijian"></span>
    <p class="title">{{ $t('高级清洗中') }}</p>
    <p class="remark">
      <span v-if="isInit">
        <span v-if="resultList.length">{{ `${resultList.join('、')}${$t('清洗已完成')}` }}</span>
        <span v-else>{{ $t('高级清洗仍在进行中') }}</span>
      </span>
      <span v-else>{{ $t('当前流程已跳转至计算平台进行清洗，若清洗完成可及时刷新页面更新状态') }}</span>
    </p>
    <div class="refresh-button">
      <span class="bk-icon icon-refresh-line"></span>
      <span @click="handleRefresh">{{ $t('刷新') }}</span>
    </div>
    <bk-button class="back-list" @click="backToList">{{ $t('返回列表') }}</bk-button>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    collectorId: {
      type: String,
      dafault: '',
    },
    backRouter: {
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
      curCollect: 'collect/curCollect',
    }),
  },
  methods: {
    backToList() {
      this.$router.push({
        name: this.backRouter,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    handleRefresh() {
      const { collector_config_id, bkdata_data_id } = this.curCollect;
      this.loading = true;
      this.$http.request('clean/refreshClean', {
        params: {
          collector_config_id,
        },
        query: {
          bk_biz_id: this.bkBizId,
          bk_data_id: bkdata_data_id,
        },
      }).then((res) => {
        this.isInit = true;
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
    height: 100%;
    text-align: center;
    background: #fff;
    border: 1px solid #dcdee5;

    .icon-shijian {
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
