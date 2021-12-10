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
  <div class="custom-item-container">
    <section class="operation">
      <div class="top-operation">
        <bk-button
          class="fl"
          theme="primary"
          @click="operateHandler({}, 'add')">
          {{ $t('新建自定义上报') }}
        </bk-button>
        <div class="collect-search fr">
          <bk-input
            :placeholder="$t('')"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="input"
            @enter="inputEnter">
          </bk-input>
        </div>
      </div>

      <div class="table-operation">
        <bk-table
          class="custom-table"
          :data="data"
          :pagination="pagination"
          :outer-border="false"
          @page-change="handlePageChange">
          <bk-table-column label="数据ID" prop="ip" width="208"></bk-table-column>
          <bk-table-column label="名称" prop="source" width="208"></bk-table-column>
          <bk-table-column label="监控对象" prop="status" width="208"></bk-table-column>
          <bk-table-column label="数据类型" prop="create_time" width="208"></bk-table-column>
          <bk-table-column label="创建记录" prop="create_time" width="239"></bk-table-column>
          <bk-table-column label="更新记录" prop="create_time" width="239"></bk-table-column>
          <bk-table-column label="操作" width="262" class-name="operate-column">
            <div class="collect-table-operate" slot-scope="">
              <bk-button class="king-button" theme="primary" text>{{ $t('nav.retrieve') }}</bk-button>
              <bk-button class="king-button" theme="primary" text>{{ $t('编辑') }}</bk-button>
              <bk-button class="king-button" theme="primary" text>{{ $t('logClean.goToClean') }}</bk-button>
              <bk-button class="king-button" theme="primary" text>{{ $t('logClean.storageSetting') }}</bk-button>
              <bk-dropdown-menu ref="dropdown" align="right">
                <i
                  class="bk-icon icon-more"
                  style="margin-left: 5px; font-size: 14px; font-weight: bold;"
                  slot="dropdown-trigger">
                </i>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <!-- 查看详情 -->
                  <li><a href="javascript:;">{{ $t('详情') }}</a></li>
                  <!-- <li><a href="javascript:;" class="text-disabled">{{$t('btn.block')}}</a></li> -->
                  <li><a href="javascript:;" class="text-disabled">{{$t('btn.start')}}</a></li>
                  <li><a href="javascript:;">{{$t('btn.delete')}}</a></li>
                </ul>
              </bk-dropdown-menu>
            </div>
          </bk-table-column>
        </bk-table>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'custom-report-list',
  data() {
    return {
      input: '',
      data: [
        {
          ip: '1',
          source: '2',
          status: '3',
          create_time: '4',
        },
        {
          ip: '1',
          source: '2',
          status: '3',
          create_time: '4',
        },
        {
          ip: '1',
          source: '2',
          status: '3',
          create_time: '4',
        },
      ],
      pagination: {
        current: 1,
        count: 100,
        limit: 10,
      },
    };
  },
  methods: {
    inputEnter() {},
    operateHandler(row, operateType) {
      const params = {};
      const query = {};
      const routeMap = {
        add: 'custom-report-create',
      };

      const targetRoute = routeMap[operateType];
      this.$router.push({
        name: targetRoute,
        params,
        query: {
          ...query,
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    handlePageChange(page) {
      this.pagination.current = page;
    },
    remove() {
    },
    reset() {
    },
  },
};
</script>

<style lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/conf";
@import "../../../../scss/devops-common.scss";

.custom-item-container {
  padding: 20px 24px;
  .operation {
    background-color: #fff;
    padding: 16px 20px;
    border-radius: 2px;
    box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, 0.05);
  }
  .top-operation {
    margin-bottom: 16px;
    @include clearfix;
    .bk-button {
      width: 150px;
    }
    .collect-search {
      width: 239px;
    }
  }
  .table-operation {
    .custom-table {
      overflow: visible;
      &:before {
        display: none;
      }
      .bk-table-pagination-wrapper {
        background-color: #fff;
      }
      .operate-column .cell {
        overflow: visible;
      }
      .bk-table-body-wrapper {
        overflow: visible;
      }
      .collect-table-operate {
        display: flex;
        .king-button {
          margin-right: 14px;
          &:last-child {
            margin-right: 0;
          }
        }
      }
      .bk-dropdown-list a.text-disabled:hover {
        color: #c4c6cc;
        cursor: not-allowed;
      }
    }
  }
}
</style>
