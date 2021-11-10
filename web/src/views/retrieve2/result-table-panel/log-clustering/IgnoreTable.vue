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
  <bk-table
    :data="tableData"
    class="log-cluster-table">
    <bk-table-column type="expand" width="30">
      <template slot-scope="props">
        {{props.row.a}}
      </template>
    </bk-table-column>
    <bk-table-column type="index" :label="$t('序号')" width="60"></bk-table-column>
    <bk-table-column :label="$t('数量')" :sortable="true" width="91" prop="number"></bk-table-column>
    <bk-table-column :label="$t('占比')" :sortable="true" width="91" prop="source">
      <template slot-scope="props">
        {{`${props.row.source}%`}}
      </template>
    </bk-table-column>
    <bk-table-column :label="$t('取样内容')" prop="status"></bk-table-column>
    <div slot="empty">
      <div class="empty-text">
        <span class="bk-table-empty-icon bk-icon icon-empty"></span>
        <p>{{$t('goSettingMessage')}}</p>
        <span class="empty-leave">{{$t('去设置')}}</span>
      </div>
    </div>
  </bk-table>
</template>

<script>
export default {
  data() {
    return {
      tableData: [{
        a: 123,
        number: 123,
        source: 123,
        status: 123,
      }, {
        a: 123,
        number: 124,
        source: 122,
        status: 123,
      }],
    };
  },
};
</script>

<style lang="scss" scoped>
.log-cluster-table {
  /deep/ .bk-table-body-wrapper {
    min-height: calc(100vh - 601px);

    .bk-table-empty-block {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: calc(100vh - 600px);
    }
  }

  .empty-text {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;

    .empty-leave {
      color: #3a84ff;
      margin-top: 8px;
      cursor: pointer;
    }
  }
}
</style>
