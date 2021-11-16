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
  <div class="result-table-panel">
    <bk-tab :active.sync="active" type="unborder-card">
      <bk-tab-panel
        v-for="(panel, index) in panelList"
        v-bind="panel"
        :key="index">
      </bk-tab-panel>
    </bk-tab>
    <div class="panel-content-wrap">
      <original-log
        v-if="active === 'origin'"
        v-bind="$attrs"
        v-on="$listeners" />
      <log-clustering
        v-if="active === 'clustering'"
        v-bind="$attrs"
        v-on="$listeners"
        @showOriginLog="showOriginLog" />
    </div>
  </div>
</template>

<script>
import OriginalLog from './original-log/index.vue';
import LogClustering from './log-clustering/index.vue';

export default {
  components: { OriginalLog, LogClustering },
  props: {
  },
  data() {
    return {
      active: 'origin',
      panelList: [
        { name: 'origin', label: '原始日志' },
        { name: 'clustering', label: '日志聚类' },
      ],
    };
  },
  methods: {
    showOriginLog() {
      this.active = 'origin';
    },
  },
};
</script>

<style lang="scss">
  .result-table-panel {
    position: relative;
    margin: 0 0 16px;
    padding: 10px 24px 20px;
    background: #fff;
    .bk-tab {
      margin-bottom: 16px;
      .bk-tab-section {
        display: none;
      }
    }
  }
</style>
