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
  <div class="auth-page">
    <div class="auth-page-container">
      <img src="../../images/lock-radius.svg" alt="lock" class="lock-icon" />
      <div class="flex-jsb">
        <div class="detail">{{ $t("您没有相应资源的访问权限") }}</div>
        <bk-button class="king-button" theme="primary" @click="confirmPageApply">
          {{ $t("去申请") }}
        </bk-button>
      </div>
      <div class="permission-container">
        <table class="permission-table table-header">
          <thead>
            <tr>
              <th width="30%">{{ $t('需要申请的权限') }}</th>
              <th width="50%">{{ $t('关联的资源实例') }}</th>
            </tr>
          </thead>
        </table>
        <div class="table-content">
          <table class="permission-table">
            <tbody>
              <template v-if="authorityDetail.actions && authorityDetail.actions.length > 0">
                <tr v-for="(action, index) in authorityDetail.actions" :key="index">
                  <td width="30%">{{ action.name }}</td>
                  <td width="50%">
                    <p class="resource-type-item"
                       v-for="(reItem, reIndex) in getResource(action.related_resource_types)"
                       :key="reIndex">
                      {{ reItem }}
                    </p>
                  </td>
                </tr>
              </template>
              <tr v-else>
                <td class="no-data" colspan="3">{{ $t('无数据') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    info: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      authNames: '',
    };
  },
  computed: {
    authorityDetail() {
      return this.info.apply_data || {};
    },
  },
  methods: {
    confirmPageApply() {
      window.open(this.info.apply_url);
    },
    getResource(related) {
      if (!Array.isArray(related)) return [];
      try {
        return related[0].instances[0].reduce((pre, cur) => (pre.push(`${cur.type_name}: [${cur.id}] ${cur.name}`), pre), []);
      } catch (error) {
        console.warn(error);
        return [];
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';

.flex-jsb {
  align-items: center;

  @include flex-justify(space-between);
}

.auth-page {
  height: 100%;
  min-height: 50%;

  @include flex-center();
}

.auth-page-container {
  width: 800px;
  display: flex;
  flex-flow: column;
  align-items: center;
  transform: translateY(-30%);

  .lock-icon {
    margin-top: 128px;
    width: 160px;
  }

  .title {
    margin-top: 26px;
    line-height: 28px;
    font-size: 20px;
    font-weight: 500;
    color: #313238;
  }

  .detail {
    margin: 30px 10px 0 0;
    line-height: 20px;
    font-size: 14px;
    color: #63656e;
  }

  .king-button {
    margin-top: 30px;
  }

  .permission-container {
    margin-top: 20px;
    border: 1px solid #e7e8ed;
    box-shadow: 1px -1px 2px #e7e8ed;
    border-bottom: 0;
  }

  .permission-table {
    width: 100%;
    color: #63656e;
    border-bottom: 1px solid #e7e8ed;
    border-collapse: collapse;
    table-layout: fixed;

    th,
    td {
      padding: 12px 18px;
      font-size: 12px;
      text-align: left;
      border-bottom: 1px solid #e7e8ed;
      word-break: break-all;
    }

    th {
      color: #313238;
      background: #f5f6fa;
    }
  }

  .table-content {
    max-height: 260px;
    border-bottom: 1px solid #e7e8ed;
    border-top: 0;
    overflow: auto;

    .permission-table {
      border-top: 0;
      border-bottom: 0;

      td:last-child {
        border-right: 0;
      }

      tr:last-child td {
        border-bottom: 0;
      }

      .resource-type-item {
        padding: 0;
        margin: 0;
      }
    }

    .no-data {
      padding: 30px;
      text-align: center;
      color: #999;
    }
  }
}
</style>
