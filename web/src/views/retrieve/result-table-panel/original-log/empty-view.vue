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
  <div class="empty-container">
    <template v-if="isFirstSearch">
      <bk-exception
        class="exception-wrap-item exception-part"
        type="empty"
        scene="part"
      >
        <div class="empty-card">
          <div class="empty-message">{{$t('暂未进行检索')}}</div>
          <div class="empty-main">
            <div class="suggest-title">{{$t('您可以按照以下方式进行检索')}}</div>
            <div class="suggest-list">
              <span>
                1. {{$t('当前是否有数据源，如果没有请')}}
                <span class="blue-btn" @click="handleBtnClick('goToConfig')">{{$t('前往配置')}}</span>
              </span>
              <span> 2. {{$t('检查查询条件是否完整，是否有报错')}}</span>
              <span>
                3. {{$t('当前可能是手动查询，请')}}
                <span class="blue-btn" @click="handleBtnClick('clickToQuery')">{{$t('点击查询')}}</span>
              </span>
            </div>
          </div>
        </div>
      </bk-exception>
    </template>
    <template v-else>
      <bk-exception
        class="exception-wrap-item exception-part"
        type="search-empty"
        scene="part"
      >
        <div class="empty-card">
          <div class="empty-message">{{$t('当前检索为结果为空')}}</div>
          <div class="empty-main">
            <div class="suggest-title">{{$t('您可以按照以下方式优化检索结果')}}</div>
            <div class="suggest-list">
              <span>
                1. {{$t('检查')}}
                <span class="blue-btn" @click="handleBtnClick('indexConfig')">{{$t('索引配置')}}</span>，
                {{$t('索引配置是使用日志服务进行检索分析的必要条件')}}
              </span>
              <span>2. {{$t('修改检索时间范围')}}</span>
              <span>3. {{$t('优化查询语法')}}</span>
              <div class="grammar-list">
                <span v-for="(item, index) in grammarMap" :key="index">
                  <span>{{ item.key }}</span> : <span>{{ item.value }}</span>
                </span>
              </div>
            </div>
          </div>
          <div class="more-rule" @click="handleBtnClick('queryString')">
            {{$t('查看更多语法规则')}}
            <span class="log-icon icon-tiaozhuan"></span>
          </div>
        </div>
      </bk-exception>
    </template>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
  props: {
    retrieveSearchNumber: {
      type: Number,
      require: true,
    },
    retrieveConfigId: {
      type: Number,
      require: true,
    },
  },
  data() {
    return {
      grammarMap: [
        {
          key: this.$t('全文检索'),
          value: 'abc',
        },
        {
          key: this.$t('模糊检索'),
          value: `abc* ${this.$t('或')} ab?c`,
        },
        {
          key: this.$t('键值检索'),
          value: 'info : abc',
        },
        {
          key: this.$t('范围检索'),
          value: 'status :> 400',
        },
        {
          key: this.$t('组合检索'),
          value: 'info:abc AND status:>400',
        },
      ],
    };
  },
  computed: {
    ...mapGetters({
      indexId: 'indexId',
      spaceUid: 'spaceUid',
    }),
    isFirstSearch() {
      return this.retrieveSearchNumber <= 1;
    },
  },
  methods: {
    handleBtnClick(clickType) {
      switch (clickType) {
        case 'queryString': // 查询更多语法
          this.handleGotoLink('queryString');
          break;
        case 'indexConfig': { // 索引配置
          if (!this.retrieveConfigId) {
            this.$bkMessage({
              theme: 'error',
              message: this.$t('未找到对应的采集项'),
            });
            return;
          }
          const jumpUrl = `/#/manage/log-collection/collection-item/manage/${this.retrieveConfigId}?spaceUid=${this.spaceUid}`;
          window.open(jumpUrl, '_blank');
        }
          break;
        case 'goToConfig': { // 前往配置
          const jumpUrl = `/#/manage/log-collection/collection-item?spaceUid=${this.spaceUid}`;
          window.open(jumpUrl, '_blank');
        }
          break;
        case 'clickToQuery': // 点击查询
          this.$emit('shouldRetrieve');
          break;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.empty-container {
  margin: 20px 0;

  .empty-card {
    margin-top: 24px;
    color: #63656e;

    .empty-main {
      font-size: 12px;
      min-width: 230px;
      text-align: left;

      .suggest-title {
        color: #979ba5;
        padding: 8px 0;
      }

      .suggest-list {
        display: flex;
        flex-direction: column;
        line-height: 18px;

        .grammar-list {
          margin-left: 14px;
          display: flex;
          flex-direction: column;
        }
      }
    }

    .more-rule {
      font-size: 12px;
      margin-top: 8px;
      color: #3a84ff;
      cursor: pointer;

      .log-icon {
        display: inline-block;
        transform: scale(.8);
      }
    }
  }

  .blue-btn {
    color: #3a84ff;
    cursor: pointer;
  }

  ::v-deep .exception-image {
    height: 180px;
  }
}
</style>
