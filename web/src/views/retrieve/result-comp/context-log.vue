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
    v-bkloading="{ isLoading: logLoading, opacity: .6 }"
    :class="{
      'log-full-dialog-wrapper': isScreenFull,
      'bk-form': true,
      'context-log-wrapper': true,
      'log-full-width': !isScreenFull
    }">
    <!-- IP 日志路径 -->
    <div class="dialog-label">
      <span style="margin-right: 10px;">IP: {{params.ip || params.serverIp}}</span>
      <span>{{ $t('日志路径') + ': ' + (params.path || params.logfile) }}</span>
    </div>

    <div class="dialog-bars">
      <log-filter :is-screen-full="isScreenFull" @handle-filter="handleFilter" />
      <!-- 暂停、复制、全屏 -->
      <div class="controls">
        <div class="control-icon" ref="fieldsConfigRef" v-bk-tooltips="fieldsConfigTooltip">
          <span class="icon log-icon icon-set-icon" style="font-size: 16px;"></span>
        </div>
        <fields-config
          :id="fieldsConfigId"
          :is-loading="isConfigLoading"
          :total="totalFieldNames"
          :display="displayFieldNames"
          @confirm="confirmConfig"
          @cancel="cancelConfig"
        ></fields-config>
        <div class="control-icon" @click="toggleScreenFull">
          <span class="icon log-icon icon-full-screen-log"></span>
        </div>
      </div>
    </div>
    <div class="dialog-log-markdown" ref="contextLog" tabindex="0">
      <log-view
        :log-list="logList"
        :reverse-log-list="reverseLogList"
        :filter-key="activeFilterKey"
        :filter-type="filterType"
        :ignore-case="ignoreCase"
        :interval="interval" />
    </div>

    <p class="handle-tips">{{ $t('快捷键  Esc:退出; PageUp: 向上翻页; PageDn: 向下翻页') }}</p>
    <!--        <div class="scroll-bar">-->
    <!--            <span class="icon log-icon icon-up" @click.stop="scrollPage('up')"></span>-->
    <!--            <span class="icon log-icon icon-down" @click.stop="scrollPage('down')"></span>-->
    <!--        </div>-->
  </section>
</template>

<script>
import logView from '@/components/log-view';
import FieldsConfig from '@/components/common/fields-config';
import LogFilter from '../condition-comp/Log-filter';

export default {
  name: 'ContextLog',
  components: {
    logView,
    FieldsConfig,
    LogFilter,
  },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    logParams: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    const id = 'fields-config-tippy';
    return {
      logLoading: true,
      totalFields: [], // 所有字段信息
      totalFieldNames: [], // 所有的字段名
      displayFields: [], // 按顺序展示的字段信息
      displayFieldNames: [], // 展示的字段名
      isConfigLoading: false,
      fieldsConfigId: id,
      fieldsConfigTooltip: {
        allowHtml: true,
        width: 380,
        trigger: 'click',
        placement: 'bottom-end',
        theme: 'light',
        extCls: 'fields-config-tippy',
        content: `#${id}`,
        onShow: this.requestFields,
      },
      rawList: [],
      logList: [], // 过滤成字符串的列表
      reverseRawList: [],
      reverseLogList: [], // 过滤成字符串的列表
      isScreenFull: true,
      params: {},
      zero: true,
      prevBegin: 0,
      nextBegin: 0,
      firstLogEl: null,
      filterType: 'include',
      activeFilterKey: '',
      throttle: false,
      ignoreCase: false,
      flipScreen: '',
      flipScreenList: [],
      interval: {
        prev: 0,
        next: 0,
      },
    };
  },
  computed: {
    filedSettingConfigID() { // 当前索引集的显示字段ID
      return this.$store.state.retrieve.filedSettingConfigID;
    },
  },
  created() {
    this.deepClone(this.logParams);
  },
  async mounted() {
    document.addEventListener('keyup', this.handleKeyup);

    await this.requestFields();
    await this.requestContentLog();

    this.$nextTick(() => {
      document.querySelector('.dialog-log-markdown').focus();
    });
  },
  destroyed() {
    document.removeEventListener('keyup', this.handleKeyup);
  },
  methods: {
    handleKeyup(event) {
      if (event.keyCode === 27) {
        this.$emit('close-dialog');
      }
    },
    deepClone(obj) {
      for (const key in obj) {
        if (typeof obj[key] === 'object') {
          this.deepClone(obj[key]);
        } else {
          this.params[key] = String(obj[key]).replace(/<mark>/g, '')
            .replace(/<\/mark>/g, '');
        }
      }
    },
    toggleScreenFull() {
      this.isScreenFull = !this.isScreenFull;
      this.$emit('toggleScreenFull', this.isScreenFull);
    },
    async requestFields() {
      try {
        this.isConfigLoading = true;
        const res = await this.$http.request('retrieve/getLogTableHead', {
          params: { index_set_id: this.$route.params.indexId },
          query: {
            scope: 'search_context',
            start_time: this.retrieveParams.start_time,
            end_time: this.retrieveParams.end_time,
            is_realtime: 'True',
          },
        });
        this.totalFields = res.data.fields;
        this.displayFieldNames = res.data.display_fields;
        this.totalFieldNames = res.data.fields.map(fieldInfo => fieldInfo.field_name);
        this.displayFields = res.data.display_fields.map((fieldName) => {
          return res.data.fields.find(fieldInfo => fieldInfo.field_name === fieldName);
        });
        return true;
      } catch (err) {
        console.warn(err);
      } finally {
        this.isConfigLoading = false;
      }
    },
    async requestContentLog(direction) {
      const data = Object.assign({
        size: 500,
        zero: this.zero,
      }, this.params);
      if (direction === 'down') {
        data.begin = this.nextBegin;
      } else if (direction === 'top') {
        data.begin = this.prevBegin;
      } else {
        data.begin = 0;
      }

      try {
        this.logLoading = true;
        const res = await this.$http.request('retrieve/getContentLog', {
          params: { index_set_id: this.$route.params.indexId },
          data,
        });

        const { list } = res.data;
        if (list && list.length) {
          const stringList = this.formatStringList(
            list,
            this.displayFieldNames.length ? this.displayFieldNames : ['log'],
          );
          if (direction) {
            if (direction === 'down') {
              this.logList.push(...stringList);
              this.rawList.push(...list);
              this.nextBegin += stringList.length;
            } else {
              this.reverseLogList.unshift(...stringList);
              this.reverseRawList.unshift(...list);
              this.prevBegin -= stringList.length;
            }
          } else {
            const zeroIndex = res.data.zero_index;
            if ((!zeroIndex && zeroIndex !== 0) || zeroIndex === -1) {
              this.logList.splice(this.logList.length, 0, this.$t('无法定位上下文'));
            } else {
              this.logList.push(...stringList.slice(zeroIndex, stringList.length));
              this.rawList.push(...list.slice(zeroIndex, list.length));

              this.reverseLogList.unshift(...stringList.slice(0, zeroIndex));
              this.reverseRawList.unshift(...list.slice(0, zeroIndex));

              const value = zeroIndex - res.data.count_start;
              this.nextBegin = value + this.logList.length;
              this.prevBegin = value - this.reverseLogList.length;
            }
          }
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.logLoading = false;
        if (this.zero) {
          this.$nextTick(() => {
            this.initLogScrollPosition();
          });
        }
      }
    },
    /**
     * 将列表根据字段组合成字符串数组
     * @param {Array} list 当前页码
     * @param {Array} displayFieldNames 当前页码
     * @return {Array<string>}
     **/
    formatStringList(list, displayFieldNames) {
      const stringList = [];
      list.forEach((listItem) => {
        let logString = '';
        displayFieldNames.forEach((field) => {
          const listValue = listItem[field];
          if (listValue && typeof listValue === 'object') {
            // logString += (Object.values(listValue).join(' ') + '    ')
            logString += (`${Object.values(listValue).join(' ')} `);
          } else {
            // logString += (listValue + '    ')
            logString += (`${listValue} `);
          }
        });
        stringList.push(logString);
      });

      return stringList;
    },
    // 确定设置显示字段
    async confirmConfig(list) {
      this.isConfigLoading = true;
      try {
        await this.$http.request('retrieve/postFieldsConfig', {
          params: { index_set_id: this.$route.params.indexId },
          query: { scope: 'search_context' },
          data: { display_fields: list, sort_list: [], config_id: this.filedSettingConfigID },
        });
        const res = await this.requestFields();
        if (res) {
          this.logList = this.formatStringList(this.rawList, this.displayFieldNames);
          this.reverseLogList = this.formatStringList(this.reverseRawList, this.displayFieldNames);
          this.$refs.fieldsConfigRef._tippy.hide();
          this.messageSuccess(this.$t('设置成功'));
        }
      } catch (err) {
        console.warn(err);
        this.isConfigLoading = false;
      }
    },
    // 取消设置显示字段
    cancelConfig() {
      this.$refs.fieldsConfigRef._tippy.hide();
    },
    initLogScrollPosition() {
      // 确定第0条的位置
      this.firstLogEl = document.querySelector('.dialog-log-markdown .log-init');
      // 没有数据
      if (!this.firstLogEl) return;
      const logContentHeight = this.firstLogEl.scrollHeight;
      const logOffsetTop = this.firstLogEl.offsetTop;

      const wrapperOffsetHeight = this.$refs.contextLog.offsetHeight;

      if (wrapperOffsetHeight <= logContentHeight) {
        this.$refs.contextLog.scrollTop = logOffsetTop;
      } else {
        this.$refs.contextLog.scrollTop = logOffsetTop - Math.ceil((wrapperOffsetHeight - logContentHeight) / 2);
      }
      this.zero = false;
      // 避免重复请求
      setTimeout(() => {
        this.$refs.contextLog.addEventListener('scroll', this.handleScroll, { passive: true });
      }, 64);
    },
    handleScroll() {
      // if (this.filterKey.length) return

      if (!this.throttle) {
        this.throttle = true;
        setTimeout(() => {
          if (this.logLoading) {
            this.throttle = false;
            return;
          }
          const { scrollTop } = this.$refs.contextLog;
          const { scrollHeight } = this.$refs.contextLog;
          const { offsetHeight } = this.$refs.contextLog;
          if (scrollTop === 0) {
            // 滚动到顶部
            this.requestContentLog('top').then(() => {
              // 记录刷新前滚动位置
              const newScrollHeight = this.$refs.contextLog.scrollHeight;
              this.$refs.contextLog.scrollTo({ top: newScrollHeight - scrollHeight });
            });
          } else if (scrollHeight - scrollTop - offsetHeight === 0) {
            // 滚动到底部
            this.requestContentLog('down');
          }
          this.throttle = false;
        }, 200);
      }
    },
    scrollPage(direction) {
      const { scrollTop } = this.$refs.contextLog;
      const { offsetHeight } = this.$refs.contextLog;
      const { scrollHeight } = this.$refs.contextLog;
      if (direction === 'up' && scrollTop === 0) {
        // 顶部边界滚动需要请求
        this.requestContentLog('top');
      } else if (direction === 'down' && scrollHeight - scrollTop - offsetHeight === 0) {
        // 底部边界滚动需要请求
        this.requestContentLog('down');
      } else {
        // 滚动动画
        let top = direction === 'up' ? scrollTop - offsetHeight : scrollTop + offsetHeight;
        if (top < 0) {
          top = 0;
        }
        this.$easeScroll(top, 200, this.$refs.contextLog);
      }
    },
    handleFilter(field, value) {
      if (field === 'filterKey') {
        this.filterLog(value);
      } else {
        this[field] = value;
      }
    },
    filterLog(value) {
      this.throttle = true;
      this.activeFilterKey = value;
      setTimeout(() => {
        this.throttle = false;
      }, 300);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/clearfix';
  @import '../../../scss/mixins/scroller';

  .context-log-wrapper {
    position: relative;

    @include clearfix;

    .dialog-label {
      position: absolute;
      top: -60px;
      left: 84px;
    }

    .dialog-bars {
      display: flex;
      justify-content: space-between;
      margin-bottom: 14px;

      .controls {
        display: flex;
        align-items: center;

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

    .dialog-log-markdown {
      height: 404px;
      background: #f5f7fa;
      overflow-y: auto;

      @include scroller($backgroundColor: #aaa, $width: 4px);

      &::-webkit-scrollbar {
        background-color: #dedede;
      }
    }

    .scroll-bar {
      position: absolute;
      right: 24px;
      top: 68px;
      display: flex;
      flex-flow: column;
      justify-content: space-between;
      height: 56px;

      .icon {
        font-size: 24px;
        cursor: pointer;
        color: #d9d9d9;
      }
    }

    .handle-tips {
      margin-top: 10px;
      color: #63656e;
    }
  }

  .log-full-dialog-wrapper {
    margin-top: 10px;
    height: calc(100% - 40px);

    .dialog-log-markdown {
      height: calc(100% - 46px);
    }

    .dialog-label {
      position: fixed;
      top: 24px;
      left: 110px;
    }
  }

  .log-full-width {
    width: 1030px;
  }
</style>
