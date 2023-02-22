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
  <div v-if="statusData && statusData.length" class="list-box-container">
    <div class="list-title">
      <span class="bk-icon icon-exclamation-circle"></span>
      <h2 class="text">{{ $t('任务状态') }}</h2>
    </div>
    <bk-table :data="statusData">
      <bk-table-column :label="$t('步骤')" prop="name_display"></bk-table-column>
      <bk-table-column :label="$t('开始时间')" prop="start_time" width="150"></bk-table-column>
      <bk-table-column :label="$t('耗时(s)')" width="100">
        <template slot-scope="{ row }">
          <span>
            {{ row.finish_time ?
              ((new Date(row.finish_time).getTime() - new Date(row.start_time).getTime()) / 1000) : '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('执行情况')" prop="state_display">
        <template slot-scope="{ row }">
          <span
            :class="['bk-icon', successState.includes(row.state) ? 'icon-check-circle' : 'icon-close-circle']">
          </span>
          <span>{{ row.state_display }}</span>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
export default {
  props: {
    statusData: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      successState: ['CREATED', 'RUNNING', 'FINISHED'],
    };
  },
};
</script>

<style lang="scss" scoped>
  .list-box-container {
    .icon-check-circle {
      color: #2dcb56;
    }

    .icon-close-circle {
      color: #ea3636;
    }
  }
</style>
