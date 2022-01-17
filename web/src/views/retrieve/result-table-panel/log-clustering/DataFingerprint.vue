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
  <div class="finger-container">
    <div class="top-operate" v-if="allFingerList.length">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <p v-html="getTipsMessage" class="operate-message"></p>
      <span
        v-if="selectList.length"
        class="operate-click"
        @click="handleBatchUseAlarm">{{$t('批量使用告警')}}</span>
    </div>
    <bk-table
      data-test-id="cluster_div_fingerTable"
      class="finger-cluster-table table-no-data"
      row-key="$index"
      ref="fingerTableRef"
      :data="fingerList"
      :outer-border="false"
      :reserve-selection="true"
      @select="handleSelectAlarm"
      @select-all="handleSelectAllAlarm">

      <bk-table-column
        v-if="!requestData.group_by.length"
        type="selection"
        width="40">
      </bk-table-column>

      <bk-table-column :label="$t('数据指纹')" width="150">
        <template slot-scope="{ row }">
          <div class="fl-ac signature-box">
            <span>{{row.signature}}</span>
            <div v-show="row.is_new_class" class="new-finger">New</div>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        :label="$t('数量')"
        sortable
        width="91"
        prop="number">
        <template slot-scope="{ row }">
          <span
            class="link-color"
            @click="handleMenuClick('show original', row)">
            {{row.count}}</span>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('占比')" sortable width="96">
        <template slot-scope="{ row }">
          <span
            class="link-color"
            @click="handleMenuClick('show original', row)">
            {{`${toFixedNumber(row.percentage, 2)}%`}}
          </span>
        </template>
      </bk-table-column>

      <template v-if="requestData.year_on_year_hour >= 1 ">
        <bk-table-column
          sortable
          width="101"
          align="center"
          header-align="center"
          :label="$t('同比数量')"
          :sort-by="'year_on_year_count'">
          <template slot-scope="{ row }">
            <span>{{row.year_on_year_count}}</span>
          </template>
        </bk-table-column>

        <bk-table-column
          sortable
          width="101"
          align="center"
          header-align="center"
          :label="$t('同比变化')"
          :sort-by="'year_on_year_percentage'">
          <template slot-scope="{ row }">
            <div class="fl-ac compared-change">
              <span>{{`${toFixedNumber(row.year_on_year_percentage, 0)}%`}}</span>
              <span :class="['bk-icon', showArrowsClass(row)]"></span>
            </div>
          </template>
        </bk-table-column>
      </template>

      <bk-table-column label="Pattern" min-width="350" class-name="symbol-column">
        <!-- eslint-disable-next-line -->
        <template slot-scope="{ row, column, $index }">
          <div :class="['pattern-content', { 'is-limit': !cacheExpandStr.includes($index) }]">
            <cluster-event-popover
              :context="row.pattern"
              :tippy-options="{ offset: '0, 10', boundary: scrollContent }"
              @eventClick="(option) => handleMenuClick(option,row)">
              <span>{{row.pattern ? row.pattern : $t('未匹配')}}</span>
            </cluster-event-popover>
            <p
              v-if="!cacheExpandStr.includes($index)"
              class="show-whole-btn"
              @click.stop="handleShowWhole($index)">
              {{ $t('展开全部') }}
            </p>
            <p
              v-else
              class="hide-whole-btn"
              @click.stop="handleHideWhole($index)">
              {{ $t('收起') }}
            </p>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        v-if="requestData.group_by.length"
        :label="$t('分组')"
        class-name="symbol-column">
        <template slot-scope="{ row }">
          <div class="group-box">
            <span>{{row.group}}</span>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        v-if="!requestData.group_by.length"
        :label="$t('告警')"
        width="103"
        class-name="symbol-column">
        <template slot-scope="{ row }">
          <div class="fl-ac" style="margin-top: 2px;">
            <div @click.stop="handleClickAlarmSwitch(row)">
              <bk-switcher
                v-model="row.monitor.is_active"
                theme="primary"
                :disabled="isRequestAlarm"
                :pre-check="() => false">
              </bk-switcher>
            </div>
            <bk-popover v-if="row.monitor.is_active" content="可去告警策略编辑">
              <span class="bk-icon icon-edit2 link-color"></span>
            </bk-popover>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        :label="$t('标签')"
        min-width="105"
        align="center"
        header-align="center">
        <template slot-scope="{ row }">
          <div>
            <span v-if="!row.labels || !row.labels.length">--</span>
            <bk-tag v-else v-for="(item,index) of row.labels" :key="index">{{item}}</bk-tag>
          </div>
        </template>
      </bk-table-column>

      <!-- <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column> -->

      <template slot="append" v-if="fingerList.length && isPageOver">
        <clustering-loader :width-list="loaderWidthList" />
      </template>

      <div slot="empty">
        <div class="empty-text" v-if="clusterSwitch && !configData.extra.signature_switch">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('goFingerMessage')}}</p>
          <span class="empty-leave" @click="handleLeaveCurrent">{{$t('去设置')}}</span>
        </div>
        <div class="empty-text" v-if="fingerList.length === 0 && configData.extra.signature_switch">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('暂无数据')}}</p>
        </div>
      </div>
    </bk-table>
  </div>
</template>

<script>
import ClusterEventPopover from './components/ClusterEventPopover';
import ClusteringLoader from '@/skeleton/clustering-loader';
import { copyMessage } from '@/common/util';
export default {
  components: {
    ClusterEventPopover,
    ClusteringLoader,
  },
  props: {
    fingerList: {
      type: Array,
      require: true,
    },
    clusterSwitch: {
      type: Boolean,
      require: true,
    },
    requestData: {
      type: Object,
      require: true,
    },
    configData: {
      type: Object,
      require: true,
    },
    loaderWidthList: {
      type: Array,
      default: [''],
    },
    isPageOver: {
      type: Boolean,
      default: false,
    },
    allFingerList: {
      type: Array,
      require: true,
    },
  },
  data() {
    return {
      cacheExpandStr: [], // 展示pattern按钮数组
      selectSize: 0, // 当前选择几条数据
      isSelectAll: false, // 当前是否点击全选
      selectList: [], // 当前选中的数组
      isRequestAlarm: false, // 是否正在请求告警接口
    };
  },
  inject: ['addFilterCondition'],
  computed: {
    scrollContent() {
      return document.querySelector('.result-scroll-container');
    },
    getTipsMessage() {
      return this.selectList.length
        ? `${this.$t('fingerChoose')}
        <span>${this.selectSize}</span>
        ${this.$t('fingerSizeData')} ,
        ${this.$t('fingerTotalData')}
        <span>${this.allFingerList.length}</span>
        ${this.$t('fingerSizeData')}`
        : `${this.$t('fingerTotalData')}
        <span>${this.allFingerList.length}</span>
        ${this.$t('fingerSizeData')}`;
    },
    bkBizId() {
      return this.$store.state.bkBizId;
    },
  },
  watch: {
    'fingerList.length': {
      handler(newLength, oldLength) {
        if (this.isSelectAll) {
          this.$nextTick(() => {
            this.fingerList.slice(oldLength, newLength).forEach((item) => {
              this.$refs.fingerTableRef.toggleRowSelection(item, true);
            });
          });
        }
      },
    },
  },
  mounted() {
    this.scrollEvent('add');
  },
  beforeDestroy() {
    this.scrollEvent('close');
  },
  methods: {
    handleMenuClick(option, row) {
      switch (option) {
        // pattern 下钻
        case 'show original':
          this.addFilterCondition(`__dist_${this.requestData.pattern_level}`, 'is', row.signature.toString());
          this.$emit('showOriginLog');
          break;
        case 'copy':
          copyMessage(row.pattern);
          break;
      }
    },
    showArrowsClass(row) {
      if (row.year_on_year_percentage === 0) return '';
      return row.year_on_year_percentage < 0 ? 'icon-arrows-down' : 'icon-arrows-up';
    },
    handleShowWhole(index) {
      this.cacheExpandStr.push(index);
    },
    handleHideWhole(index) {
      this.cacheExpandStr = this.cacheExpandStr.map(item => item !== index);
    },
    handleLeaveCurrent() {
      this.$emit('showSettingLog');
    },
    toFixedNumber(value, size) {
      if (typeof value === 'number' && !isNaN(value)) {
        return value.toFixed(size);
      }
      return value;
    },
    /**
     * @desc: 添加或删除监听分页事件
     * @param { String } state 新增或删除
     */
    scrollEvent(state = 'add') {
      const scrollEl = document.querySelector('.result-scroll-container');
      if (!scrollEl) return;
      if (state === 'add') {
        scrollEl.addEventListener('scroll', this.handleScroll, { passive: true });
      }
      if (state === 'close') {
        scrollEl.removeEventListener('scroll', this.handleScroll, { passive: true });
      }
    },
    handleSelectAlarm(selection) {
      if (this.isSelectAll) { // 全选与非全选时显示选择的数量
        this.selectSize = selection.length + this.allFingerList.length - this.fingerList.length;
      } else {
        this.selectSize = selection.length;
      }
      this.selectList = selection;
    },
    handleSelectAllAlarm(selection) {
      if (selection.length === 0) {
        this.isSelectAll = false;
        this.selectSize = 0;
        return;
      }
      this.isSelectAll = true;
      this.selectSize = this.allFingerList.length;
      this.selectList = selection;
    },
    handleBatchUseAlarm() {
      this.$bkInfo({
        title: this.$t('是否批量开启告警'),
        confirmFn: () => {
          const alarmList = this.selectList;
          if (this.isSelectAll) {
            // 全选时获取未显示的数据指纹
            alarmList.concat(this.allFingerList.slice(this.fingerList.length));
          }
          // 过滤告警开启状态的元素
          const notActiveList = alarmList.filter(el => !el.monitor.is_active);
          this.requestAlarm(notActiveList, true, () => {
            this.$emit('updateRequest');
          });
        },
      });
    },
    handleClickAlarmSwitch(row) {
      const { monitor: { is_active: isActive } } = row;
      const msg = isActive ?  this.$t('是否关闭该告警') : this.$t('是否开启该告警');
      this.$bkInfo({
        title: msg,
        confirmFn: () => {
          this.requestAlarm([row], !isActive, (result) => {
            result && (row.monitor.is_active = !isActive);
          });
        },
      });
    },
    /**
     * @desc: 数据指纹告警请求
     * @param { Array } alarmList 告警数组
     * @param { Boolean } state 启用或关闭
     * @param { Function } callback 回调函数
     */
    requestAlarm(alarmList = [], state, callback) {
      if (!alarmList.length) {
        this.$bkMessage({
          theme: 'primary',
          message: '已全部开启告警',
        });
        return;
      }

      const action = state ? 'create' : 'delete';
      const actions = alarmList.reduce((pre, cur) => {
        const { signature, pattern, monitor: { strategy_id } } = cur;
        const queryObj = {
          signature,
          pattern,
          strategy_id,
          action,
        };
        !queryObj.strategy_id && delete queryObj.strategy_id;
        pre.push(queryObj);
        return pre;
      }, []);
      this.isRequestAlarm = true;
      this.$http.request('/logClustering/updateStrategies', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data: {
          bk_biz_id: this.bkBizId,
          pattern_level: this.requestData.pattern_level,
          actions,
        },
      })
        .then(({ data: { operators, result } }) => {
          let theme;
          let message;
          if (result) {
            theme = 'success';
            message = this.$t('操作成功');
          } else {
            theme = this.isSelectAll ? 'warning' : 'error';
            message = this.isSelectAll ? this.$t('部分操作成功') : operators[0].operator_msg;
          }
          this.$bkMessage({
            theme,
            message,
            ellipsisLine: 0,
          });
          callback(result);
        })
        .finally(() => {
          this.isRequestAlarm = false;
        });
    },
    handleScroll() {
      if (this.throttle) {
        return;
      }
      const el = document.querySelector('.result-scroll-container');
      if (el.scrollHeight - el.offsetHeight - el.scrollTop < 5) {
        this.throttle = true;
        setTimeout(() => {
          el.scrollTop = el.scrollTop - 5;
          this.throttle = false;
          this.$emit('paginationOptions');
        }, 100);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/scss/mixins/flex.scss";

.finger-container {
  position: relative;
  .top-operate{
    position: absolute;
    top: 42px;
    z-index: 99;
    width: 100%;
    height: 32px;
    font-size: 12px;
    background: #F0F1F5;
    border-top: 1px solid #dfe0e5;
    border-bottom: 1px solid #dfe0e5;
    @include flex-center;
    .operate-message{
      margin: -2px 8px 0 0;
      color: #63656E;
      :first-child {
        font-size: 14px;
        font-weight: 700;
      }
    }
    .operate-click{
      color: #3a84ff;
      cursor: pointer;
    }
  }
  .finger-cluster-table {
    /deep/ .bk-table-body-wrapper {
      margin-top: 32px;
      min-height: calc(100vh - 570px);
      .bk-table-empty-block {
        min-height: calc(100vh - 570px);
        @include flex-center;
      }
    }
    &:before {
      display: none;
    }
    /deep/.bk-table-row-last {
      td {
        border: none;
      }
    }
    .signature-box {
      margin-top: 1px;
      span{
        width: 95px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 24px;
      }
    }
    .compared-change {
      margin-top: 1px;
      justify-content: center;
    }
    .empty-text {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      .bk-icon {
        font-size: 65px;
      }
      .empty-leave {
        color: #3a84ff;
        margin-top: 8px;
        cursor: pointer;
      }
    }
    .pattern-content {
      position: relative;
      padding: 10px 15px 0 0;
      margin: 4px 0 10px 0;
      overflow: hidden;
      display: inline-block;
      &.is-limit {
        max-height: 96px;
      }
    }
    .hover-row {
      .show-whole-btn{
        background-color: #F0F1F5;
      }
    }
    .group-box{
      min-height: 40px;
      padding: 8px 0;
      @include flex-align;
    }
    .show-whole-btn {
      position: absolute;
      top: 72px;
      width: 100%;
      height: 24px;
      color: #3a84ff;
      font-size: 12px;
      background: #fff;
      cursor: pointer;
      transition: background-color .25s ease;
    }
    .hide-whole-btn {
      line-height: 14px;
      margin-top: 2px;
      color: #3a84ff;
      cursor: pointer;
    }
  }
}
.table-no-data {
  /deep/.bk-table-header-wrapper {
    tr {
      > th {
        border-bottom: none !important;
      }
    }
  }
}
.new-finger {
  width: 40px;
  height: 16px;
  font-size: 12px;
  line-height: 14px;
  text-align: center;
  color: #ea3636;
  background: #ffeeee;
  border: 1px solid #fd9c9c;
  border-radius: 9px;
}
.link-color {
  color: #3a84ff;
  cursor: pointer;
}
.icon-arrows-down {
  color: #2dcb56;
}
.icon-arrows-up {
  color: #ff5656;
}
.fl-ac {
  margin-top: -4px;
  @include flex-align;
}
.bk-icon {
  font-size: 24px;
}
</style>
