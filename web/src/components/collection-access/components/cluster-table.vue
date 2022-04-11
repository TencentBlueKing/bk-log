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
  <div class="cluster-container">
    <div class="cluster-title">
      <span class="bk-icon icon-angle-up-fill"></span>
      <p>{{ $t("平台集群") }}</p>
    </div>
    <div class="cluster-main">
      <template v-if="tableList.length">
        <bk-table
          class="cluster-table"
          :data="tableList"
          :max-height="254"
          @row-click="handleSelectCluster">
          <bk-table-column :label="$t('集群名')">
            <template slot-scope="{ row }">
              <bk-radio-group v-model="clusterSelect">
                <bk-radio :value="row.ip">
                  {{ row.ip }}
                </bk-radio>
              </bk-radio-group>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('总量')" prop="source"></bk-table-column>
          <bk-table-column :label="$t('空闲率')" prop="status"></bk-table-column>
          <bk-table-column :label="$t('索引数')" prop="create_time"></bk-table-column>
          <bk-table-column :label="$t('业务数')" prop="create_time"></bk-table-column>
        </bk-table>
        <div class="cluster-illustrate">
          <p class="illustrate-title">{{$t('集群说明')}}</p>
          <div class="illustrate-container">
            <div v-for="[key,value] of Object.entries(illustrateLabelData)" :key="key">
              <span class="illustrate-label">{{key}}：</span>
              <span class="illustrate-value">{{value}}</span>
            </div>
          </div>
          <p class="illustrate-list" v-for="(item,index) of illustrateData" :key="index">
            {{item}}
          </p>
        </div>
      </template>
      <template v-else>
        <div class="noData-container">
          <div class="noData-message">
            <span class="bk-table-empty-icon bk-icon icon-empty"></span>
            <p class="empty-message">{{$t('createAClusterTips')}}</p>
            <p class="button-text">{{$t('创建集群')}}</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    tableList: {
      type: Array,
      default: () => [],
    },
    tableParams: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      clusterSelect: null,
      illustrateLabelData: {
        副本数: '最大2天',
        过期时间: '最大10天',
        热冷数据: '是',
        日志归档: '是',
      },
      illustrateData: [
        '11111',
        '22222',
        '22222',
      ],
    };
  },
  mounted() {
    this.clusterSelect = this.tableParams.clusterSelect;
  },
  methods: {
    handleSelectCluster($row) {
      this.clusterSelect = $row.ip;
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.cluster-container {
  margin-top: 20px;

  .cluster-title {
    width: 100%;
    height: 32px;
    font-size: 12px;
    color: #626369;
    background: #eff1f5;
    border: 1px solid #dcdee5;
    border-bottom: none;

    @include flex-align;

    .icon-angle-up-fill {
      margin: 0 10px;
      font-size: 16px;
    }
  }

  .cluster-main {
    display: flex;

    .cluster-table {
      width: 58%;
    }

    .cluster-illustrate {
      width: 42%;
      overflow-y: auto;
      max-height: 254px;
      padding: 16px;
      font-size: 12px;
      overflow-y: auto;
      border: 1px solid #dcdee5;
      border-left: none;

      .illustrate-title {
        font-weight: 700;
        color: #66676b;
      }

      .illustrate-container {
        padding: 12px 0;
        border-bottom: 1px solid #eee;

        @include flex-justify(space-between);
      }

      .illustrate-label {
        color: #66676b;
      }

      .illustrate-list {
        margin-top: 8px;
        color: #575961;
      }
    }

    .bk-radio-text {
      font-size: 12px;
    }

    .noData-container {
      width: 100%;
      border: 1px solid #dcdee5;

      @include flex-center;

      .noData-message {
        flex-direction: column;
        padding: 20px 0;
        font-size: 12px;

        @include flex-center;

        .empty-message {
          color: #63656e;
          margin-bottom: 6px;
        }
      }

      .icon-empty {
        font-size: 65px;
        color: #c3cdd7;
      }
    }
  }
}
</style>
