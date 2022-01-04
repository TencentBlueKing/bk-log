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
  <bk-dialog
    width="1105"
    :value="show"
    :show-footer="false"
    @value-change="handleValueChange">
    <template>
      <div class="log-version" v-bkloading="{ isLoading: loading }">
        <div class="log-version-left">
          <ul class="left-list">
            <li class="left-list-item"
                :class="{ 'item-active': index === active }"
                v-for="(item,index) in logList"
                :key="index"
                @click="handleItemClick(index)">
              <span class="item-title">{{item.title}}</span>
              <span class="item-date">{{item.date}}</span>
              <span v-if="index === current" class="item-current">当前版本</span>
            </li>
          </ul>
        </div>
        <div class="log-version-right">
          <!-- eslint-disable vue/no-v-html -->
          <div class="detail-container" v-html="currentLog.detail"></div>
          <!--eslint-enable-->
        </div>
      </div>
    </template>
  </bk-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'log-version',
  props: {
    // 是否显示
    dialogShow: Boolean,
  },
  data() {
    return {
      show: false,
      current: 0,
      active: 0,
      logList: [],
      loading: false,
    };
  },
  computed: {
    currentLog() {
      return this.logList[this.active] || {};
    },
  },
  watch: {
    dialogShow: {
      async handler(v) {
        this.show = v;
        if (v) {
          this.loading = true;
          this.logList = await this.getVersionLogsList();
          if (this.logList.length) {
            await this.handleItemClick();
          }
          this.loading = false;
        }
      },
      immediate: true,
    },
  },
  beforeDestroy() {
    this.show = false;
    this.$emit('update:dialogShow', false);
  },
  methods: {
    //  dialog显示变更触发
    handleValueChange(v) {
      this.$emit('update:dialogShow', v);
    },
    // 点击左侧log查看详情
    async handleItemClick(v = 0) {
      this.active = v;
      if (!this.currentLog.detail) {
        this.loading = true;
        const detail = await this.getVersionLogsDetail();
        this.currentLog.detail = detail;
        this.loading = false;
      }
    },
    // 获取左侧版本日志列表
    async getVersionLogsList() {
      const { data } = await axios({
        method: 'get',
        url: `${window.SITE_URL}version_log/version_logs_list/`,
      }).catch((_) => {
        console.warn(_);
        return { data: { data: [] } };
      });
      return data.data.map(item => ({ title: item[0], date: item[1], detail: '' }));
    },
    // 获取右侧对应的版本详情
    async getVersionLogsDetail() {
      const { data } = await axios({
        method: 'get',
        url: `${window.SITE_URL}version_log/version_log_detail/`,
        params: {
          log_version: this.currentLog.title,
        },
      }).catch((_) => {
        console.warn(_);
        return { data: '' };
      });
      return data.data;
    },
  },
};
</script>

<style lang="scss" scoped>
  .log-version {
    display: flex;
    margin: -33px -24px -26px;

    &-left {
      flex: 0 0 180px;
      background-color: #fafbfd;
      border-right: 1px solid #dcdee5;
      padding: 40px 0;
      display: flex;
      font-size: 12px;

      .left-list {
        border-top: 1px solid #dcdee5;
        border-bottom: 1px solid #dcdee5;
        height: 520px;
        overflow: auto;
        display: flex;
        flex-direction: column;
        width: 100%;

        &-item {
          flex: 0 0 54px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding-left: 30px;
          position: relative;
          border-bottom: 1px solid #dcdee5;

          &:hover {
            cursor: pointer;
            background-color: #fff;
          }

          .item-title {
            color: #313238;
            font-size: 16px;
          }

          .item-date {
            color: #979ba5;
          }

          .item-current {
            position: absolute;
            right: 20px;
            top: 8px;
            background-color: #699df4;
            border-radius: 2px;
            width: 58px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
          }

          &.item-active {
            background-color: #fff;

            &::before {
              content: ' ';
              position: absolute;
              top: 0px;
              bottom: 0px;
              left: 0;
              width: 6px;
              background-color: #3a84ff;
            }
          }
        }
      }
    }

    &-right {
      flex: 1;
      padding: 25px 30px 50px 45px;

      .detail-container {
        max-height: 525px;
        overflow: auto;
      }
    }
  }
</style>
