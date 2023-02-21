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
  <div
    ref="tabTitleRef"
    class="retrieve-tab-item-title">
    <div>
      {{$t('查询语句')}}
      <span class="log-icon icon-help" v-bk-tooltips="tips"></span>
      <div id="retrieve-help-tips-content">
        <div>
          {{$t('可输入SQL语句进行快速查询')}}
          <a class="tips-link" @click="handleGotoLink('queryString')">
            {{$t('查看语法')}}<span class="log-icon icon-lianjie"></span>
          </a>
        </div>
        <div class="title">{{$t('精确匹配(支持AND、OR)：')}}</div>
        <div class="detail">author:"John Smith" AND age:20</div>
        <div class="title">{{$t('字段名匹配(*代表通配符)：')}}</div>
        <div class="detail">status:active</div>
        <div class="detail">title:(quick brown)</div>
        <div class="title">{{$t('字段名模糊匹配：')}}</div>
        <div class="detail">vers\*on:(quick brown)</div>
        <div class="title">{{$t('通配符匹配：')}}</div>
        <div class="detail">qu?ck bro*</div>
        <div class="title">{{$t('正则匹配：')}}</div>
        <div class="detail">name:/joh?n(ath[oa]n/</div>
        <div class="title">{{$t('范围匹配：')}}</div>
        <div class="detail">count:[1 TO 5]</div>
        <div class="detail">count:[1 TO 5}</div>
        <div class="detail">count:[10 TO *]</div>
      </div>
    </div>
    <div>
      <!-- 历史记录 -->
      <div class="history-button">
        <span class="log-icon icon-lishijilu"></span>
        <span @click="handleClickHistoryButton">{{$t('历史查询')}}</span>
      </div>
      <div v-show="false">
        <ul ref="historyUlRef" class="retrieve-history-list">
          <template v-if="historyRecords.length">
            <li
              class="list-item"
              v-for="item in historyRecords"
              :key="item.id"
              @click="handleClickHistory(item)">
              <div v-bk-overflow-tips="{ placement: 'right' }" class="item-text text-overflow-hidden">
                {{ item.query_string }}
              </div>
            </li>
          </template>
          <li v-else class="list-item not-history">{{$t('暂无历史记录')}}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  model: {
    event: 'change',
  },
  props: {
    value: {
      type: String,
      required: true,
    },
    historyRecords: {
      type: Array,
      default: () => ([]),
    },
  },
  data() {
    return {
      tips: {
        trigger: 'click',
        theme: 'light',
        allowHtml: true,
        content: '#retrieve-help-tips-content',
        placement: 'bottom-start',
        distance: 9,
      },
      docCenterUrl: window.BK_DOC_QUERY_URL,
    };
  },
  methods: {
    handleClickHistory(item) {
      this.$emit('change', item.params.keyword);
      this.$emit('updateSearchParam', item.params.addition, item.params.host_scopes);
      this.$nextTick(() => {
        this.showDropdown = false;
        this.isSearchRecord = true;
        this.$emit('retrieve');
        this.popoverInstance && this.popoverInstance.destroy();
      });
    },
    handleClickHistoryButton(e) {
      const popoverWidth = this.$refs.tabTitleRef?.clientWidth || 'auto';
      this.popoverInstance = this.$bkPopover(e.target, {
        content: this.$refs.historyUlRef,
        trigger: 'manual',
        arrow: true,
        width: popoverWidth,
        theme: 'light',
        sticky: true,
        duration: [275, 0],
        interactive: true,
        placement: 'bottom-end',
        extCls: 'retrieve-history-popover',
        onHidden: () => {
          this.popoverInstance && this.popoverInstance.destroy();
          this.popoverInstance = null;
        },
      });
      this.popoverInstance.show();
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/mixins/flex.scss';

.retrieve-tab-item-title {
  align-items: center;
  margin: 16px 0 6px;
  line-height: 20px;
  font-size: 12px;
  color: #63656e;

  @include flex-justify(space-between);

  .icon-help {
    color: #979ba5;
    font-size: 14px;
    cursor: pointer;
    margin-left: 7px;
  }

  .history-button {
    color: #3a84ff;
    cursor: pointer;

    @include flex-center;

    .icon-lishijilu {
      margin-right: 3px;
    }
  }
}

.retrieve-history-popover {
  .light-theme {
    padding: 6px 0;
  }
}

.retrieve-history-list {
  max-height: 300px;
  overflow-y: auto;

  .list-item {
    font-size: 12px;
    line-height: 32px;
    background-color: #fff;

    @include flex-align;

    .item-type-icon {
      width: 32px;
      height: 32px;

      @include flex-center;

      .log-icon {
        font-size: 16px;
      }
    }

    .item-text {
      flex: 1;
      min-width: 150px;
      padding: 0 16px;
      color: #63656e;
      font-family: 'Roboto Mono', Consolas, Menlo, Courier, monospace;
    }

    .item-description {
      flex: 2;
      color: #979ba5;
      margin-left: 24px;

      .item-callout {
        padding: 0 4px;
        color: #313238;
        background-color: #f4f6fa;
        font-family: 'Roboto Mono', Consolas, Menlo, Courier, monospace;
      }
    }

    &:hover,
    &.active {
      background-color: #f4f6fa;

      .item-text {
        color: #313238;
      }

      .item-callout {
        background-color: #fff;
      }
    }

    &:hover {
      cursor: pointer;
      background-color: #eaf3ff;
    }
  }

  .not-history {
    @include flex-center;
  }
}

#retrieve-help-tips-content {
  color: #63656e;
  max-width: 264px;
  word-break: normal;

  .tips-link {
    color: #3a84ff;
    margin-left: 5px;
    cursor: pointer;

    .icon-lianjie {
      margin-left: 3px;
    }
  }

  .title {
    font-weight: 600;
    margin: 10px 0 4px;
  }

  .detail {
    line-height: 18px;
  }
}
</style>
