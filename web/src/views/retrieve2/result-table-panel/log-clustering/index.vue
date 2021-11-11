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
  <div class="log-cluster-table-container">
    <div class="cluster-nav">
      <div class="bk-button-group">
        <bk-button
          v-for="(item) of clusterNavList" :key="item.id" size="small"
          :class="selected === item.id ? 'is-selected' : ''"
          @click="handleClickNav(item.id)">{{item.name}}</bk-button>
      </div>

      <div v-if="selected === '2'" class="fingerprint fljb">
        <div class="fingerprint-setting fljb">
          <div class="fljb">
            <span>{{$t('同比')}}</span>
            <bk-select
              :disabled="false"
              v-model="comparedValue"
              ext-cls="compared-select"
              :clearable="false"
              behavior="simplicity">
              <bk-option v-for="option in comparedList"
                         :key="option.id"
                         :id="option.id"
                         :name="option.name">
              </bk-option>
            </bk-select>
          </div>

          <bk-checkbox
            :true-value="'yes'"
            :false-value="'no'"
            v-model="value">
            <span style="font-size: 12px">{{$t('近24H新增')}}</span>
          </bk-checkbox>

          <div class="partter fljb" style="width: 200px">
            <span>Partter</span>
            <div class="partter-slider-box fljb">
              <span>{{$t('少')}}</span>
              <bk-slider class="partter-slider" v-model="number"></bk-slider>
              <span>{{$t('多')}}</span>
            </div>
          </div>
        </div>

        <div class="download-icon">
          <span class="log-icon icon-xiazai"></span>
        </div>
      </div>
    </div>

    <bk-alert type="info" :title="$t('clusterAlert')" closable></bk-alert>

    <div>
      <ignore-table v-if="selected === '0' || selected === '1'" />
      <data-fingerprint :compared-value="comparedValue" v-if="selected === '2'" />
    </div>
  </div>
</template>

<script>
import DataFingerprint from './DataFingerprint';
import IgnoreTable from './IgnoreTable';

export default {
  components: { DataFingerprint, IgnoreTable },
  props: {
  },
  data() {
    return {
      selected: '0',
      value: '0',
      number: 100,
      clusterNavList: [{
        id: '0',
        name: this.$t('忽略数字'),
      }, {
        id: '1',
        name: this.$t('忽略符号'),
      }, {
        id: '2',
        name: this.$t('数据指纹'),
      }],
      comparedList: [{
        id: '0',
        name: '一小时前',
      }, {
        id: '1',
        name: '不对比',
      }],
      comparedValue: '0',
    };
  },
  methods: {
    handleClickNav(id) {
      this.selected = id;
    },
  },
};
</script>

<style lang="scss">
  @import "@/scss/mixins/flex.scss";

  .log-cluster-table-container {
    .cluster-nav {
      min-width: 760px;
      margin-bottom: 12px;
      color: #63656e;

      .fingerprint {
        width: 535px;
      }

      .fingerprint-setting {
        width: 485px;
        height: 24px;
        line-height: 24px;
        font-size: 12px;

        .partter {
          width: 200px;

          .partter-slider-box {
            width: 154px;
          }

          .partter-slider {
            width: 114px;
          }
        }
      }

      .download-icon {
        width: 26px;
        height: 26px;
        border: 1px solid #c1c4ca;
        position: relative;
        color: #979ba5;
        cursor: pointer;
        border-radius: 2px;
        @include flex-center;
      }
      @include flex-justify(space-between);
    }

    .bk-alert {
      margin-bottom: 16px;
    }
  }
  .compared-select {
    min-width: 87px;
    margin-left: 6px;
    position: relative;
    top: -3px;

    .bk-select-name {
      height: 24px;
    }
  }
  .fljb {
    align-items: center;
    @include flex-justify(space-between);
  }
</style>
