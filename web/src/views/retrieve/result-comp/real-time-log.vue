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
  <section
    :class="{
      'log-dialog-wrapper': true,
      'log-full-dialog-wrapper': isScreenFull,
      'log-full-width': !isScreenFull }">
    <div class="dialog-label">
      <!-- IP -->
      <span style="margin-right: 10px;">IP: {{params.ip || params.serverIp}}</span>
      <!-- 日志路径 -->
      <span>{{ $t('日志路径') + ': ' + (params.path || params.logfile) }}</span>
    </div>
    <div class="dialog-bars">
      <log-filter :is-screen-full="isScreenFull" @handle-filter="handleFilter" />
      <!-- 暂停、复制、全屏 -->
      <div class="dialog-bar controls">
        <div v-bk-tooltips.top="{ content: isPolling ? $t('暂停') : $t('启动'), delay: 300 }"
             class="control-icon"
             @click="togglePolling">
          <span class="icon log-icon icon-stop-log" v-if="isPolling"></span>
          <span class="icon log-icon icon-play-log" v-else></span>
        </div>
        <div v-bk-tooltips.top="{ content: $t('复制'), delay: 300 }" class="control-icon" @click="copyLogText">
          <span class="icon log-icon icon-copy"></span>
        </div>
        <div v-bk-tooltips.top="{ content: $t('全屏'), delay: 300 }" class="control-icon" @click="toggleScreenFull">
          <span class="icon log-icon icon-full-screen-log"></span>
        </div>
      </div>
    </div>
    <div class="dialog-log-markdown" tabindex="0">
      <log-view
        :log-list="logList"
        :filter-key="activeFilterKey"
        :filter-type="filterType"
        :is-real-time-log="true"
        :max-length="maxLength"
        :shift-length="shiftLength"
        :ignore-case="ignoreCase"
        :interval="interval" />
    </div>
    <p class="handle-tips">{{ $t('快捷键  Esc:退出; PageUp: 向上翻页; PageDn: 向下翻页') }}</p>
  </section>
</template>

<script>
import logView from '@/components/log-view';
import LogFilter from '../condition-comp/Log-filter';

export default {
  name: 'RealTimeLog',
  components: {
    logView,
    LogFilter,
  },
  props: {
    logParams: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      filterType: 'include',
      activeFilterKey: '',
      params: {},
      isScreenFull: true,
      loading: false, // 是否已经发出请求
      isPolling: false,
      timer: null,
      cloudAreaList: [],
      logList: [],
      // 日志最大长度
      maxLength: Number(window.REAL_TIME_LOG_MAX_LENGTH) || 20000,
      // 超过此长度删除部分日志
      shiftLength: Number(window.REAL_TIME_LOG_SHIFT_LENGTH) || 10000,
      isScrollBottom: true,
      logWrapperEl: null,
      zero: true,
      ignoreCase: false,
      flipScreen: '',
      flipScreenList: [],
      interval: {
        prev: 0,
        next: 0,
      },
    };
  },
  created() {
    this.deepClone(this.logParams);
  },
  mounted() {
    document.addEventListener('keyup', this.handleKeyup);
    this.requestRealTimeLog();
    this.togglePolling();
    this.registerScrollEvent();
  },
  destroyed() {
    document.removeEventListener('keyup', this.handleKeyup);

    this.timer && clearInterval(this.timer);
  },
  methods: {
    handleKeyup(event) {
      if (event.keyCode === 27) {
        this.$emit('close-dialog');
      }
    },
    deepClone(obj) {
      const string = JSON.stringify(obj).replace(/<mark>/g, '')
        .replace(/<\/mark>/g, '');
      this.params = JSON.parse(string);
    },
    requestRealTimeLog() {
      if (this.loading) {
        return false;
      }
      this.loading = true;
      this.$http.request('retrieve/getRealTimeLog', {
        params: { index_set_id: this.$route.params.indexId },
        data: Object.assign({ order: '-', size: 500, zero: this.zero }, this.params),
      }).then((res) => {
        // 通过gseindex 去掉出返回日志， 并加入现有日志
        const { list } = res.data;
        if (list && list.length) {
          // 超过最大长度时剔除部分日志
          if (this.logList.length > this.maxLength) {
            this.logList.splice(0, this.shiftLength);
            this.logWrapperEl.scrollTo({ top: 0 });
          }

          const logArr = [];
          list.forEach((item) => {
            const { log } = item;
            let logString = '';
            if (typeof log === 'object') {
              logString = Object.values(log).join(' ');
            } else {
              logString = log;
            }
            logArr.push(logString);
          });
          this.deepClone(list[list.length - 1]);
          this.logList.splice(this.logList.length, 0, ...logArr);
          if (this.isScrollBottom) {
            this.$nextTick(() => {
              if (this.zero) {
                // 首次不要滚动动画
                this.logWrapperEl.scrollTo({ top: this.logWrapperEl.scrollHeight });
                this.zero = false;
              } else {
                this.$easeScroll(
                  this.logWrapperEl.scrollHeight - this.logWrapperEl.offsetHeight,
                  300,
                  this.logWrapperEl,
                );
              }
            });
          }
        }
      })
        .finally(() => {
          setTimeout(() => {
            this.loading = false;
          }, 300);
        });
    },
    clearLogList() {
      if (this.isPolling) {
        this.timer && clearInterval(this.timer);
      }
      this.logList.splice(0, this.logList.length);
      if (this.isPolling) {
        this.isPolling = false;
        this.requestRealTimeLog();
        this.togglePolling();
      }
    },
    togglePolling() {
      this.isPolling = !this.isPolling;
      this.timer && clearInterval(this.timer);
      if (this.isPolling) {
        this.timer = setInterval(this.requestRealTimeLog, 5000);
      }
    },
    toggleScreenFull() {
      this.isScreenFull = !this.isScreenFull;
      this.$emit('toggleScreenFull', this.isScreenFull);
    },
    registerScrollEvent() {
      this.logWrapperEl = document.querySelector('.dialog-log-markdown');
      this.logWrapperEl.addEventListener('scroll', () => {
        const { scrollTop } = this.logWrapperEl;
        const contentHeight = this.logWrapperEl.scrollHeight;
        const { offsetHeight } = this.logWrapperEl;
        if (scrollTop + offsetHeight >= contentHeight) {
          this.isScrollBottom = true;
        } else {
          this.isScrollBottom = false;
        }
      });
    },
    copyLogText() {
      const el = document.createElement('textarea');
      el.value = this.logList.join('\n');
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      const selected = document.getSelection().rangeCount > 0 ? document.getSelection().getRangeAt(0) : false;
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      if (selected) {
        document.getSelection().removeAllRanges();
        document.getSelection().addRange(selected);
      }
      this.$bkMessage({
        theme: 'success',
        message: this.$t('复制成功'),
      });
    },
    filterLog(value) {
      this.activeFilterKey = value;
    },
    handleFilter(field, value) {
      if (field === 'filterKey') {
        this.filterLog(value);
      } else {
        this[field] = value;
      }
    },
  },
};
</script>

<style lang="scss">
  @import '../../../scss/mixins/clearfix.scss';
  @import '../../../scss/mixins/scroller';

  .log-dialog.bk-dialog-wrapper {
    .bk-dialog-header {
      padding-bottom: 12px;
      line-height: 30px;
    }

    .bk-dialog-body {
      padding-bottom: 10px;
    }
  }

  .log-dialog-wrapper {
    .dialog-label {
      position: absolute;
      top: 24px;
      left: 160px;
    }

    .dialog-bars {
      position: relative;
      display: flex;
      align-items: center;
      margin-bottom: 14px;

      .dialog-bar {
        display: flex;
        align-items: center;
        margin-right: 50px;

        .label-text {
          margin-right: 10px;
          color: #2d3542;
        }

        .hot-key {
          color: #979ba5;
        }

        &.controls {
          position: absolute;
          right: 0;
          margin: 0;

          .control-icon {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 32px;
            height: 32px;
            border: 1px solid #c4c6cc;
            font-size: 32px;
            cursor: pointer;
            transition: color .2s;

            &:not(:last-child) {
              margin-right: 10px;
            }

            &:hover {
              color: #3a84ff;
              transition: color .2s;
            }
          }
        }
      }
    }

    .dialog-log-markdown {
      height: 404px;
      background: #f5f7fa;
      overflow-y: auto;

      @include scroller($backgroundColor: #aaa, $width: 4px);

      &::-webkit-scrollbar {
        background-color: #dedede;
      }
    }

    .handle-tips {
      margin-top: 10px;
      color: #63656e;
    }

    &.log-full-dialog-wrapper {
      margin: 10px 0;
      height: calc(100% - 28px);

      .dialog-log-markdown {
        height: calc(100% - 60px);
      }

      .dialog-label {
        position: fixed;
      }
    }
  }

  .log-full-width {
    width: 1030px;
  }
</style>
