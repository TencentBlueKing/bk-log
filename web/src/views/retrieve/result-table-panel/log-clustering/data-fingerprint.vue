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
      <p class="operate-message">
        <i18n v-if="selectList.length" path="当前已选择{0}条数据, 共有{1}条数据">
          <span>{{selectSize}}</span>
          <span>{{allFingerList.length}}</span>
        </i18n>
        <i18n v-else path="共有{0}条数据">
          <span>{{allFingerList.length}}</span>
        </i18n>
      </p>
      <span
        v-if="selectList.length"
        class="operate-click"
        @click="handleBatchUseAlarm(true)">{{$t('批量使用告警')}}</span>
      <span
        v-if="selectList.length"
        class="operate-click"
        @click="handleBatchUseAlarm(false)">{{$t('批量停用告警')}}</span>
    </div>
    <bk-table
      data-test-id="cluster_div_fingerTable"
      class="finger-cluster-table table-no-data"
      row-key="$index"
      ref="fingerTableRef"
      :data="fingerList"
      :outer-border="false"
      :reserve-selection="true"
      @row-mouse-enter="(index) => hoverLabelIndex = index"
      @row-mouse-leave="() => hoverLabelIndex = -1">

      <bk-table-column
        width="50"
        :render-header="renderHeader">
        <template slot-scope="{ row }">
          <bk-checkbox
            :checked="getCheckedStatus(row)"
            :disabled="isRequestAlarm"
            @change="handleRowCheckChange(row, $event)">
          </bk-checkbox>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('数据指纹')" :render-header="$renderHeader" width="150">
        <template slot-scope="{ row }">
          <div class="fl-ac signature-box">
            <span v-bk-overflow-tips>{{row.signature}}</span>
            <div v-show="row.is_new_class" class="new-finger">New</div>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        :label="$t('数量')"
        :render-header="$renderHeader"
        :width="getTableWidth.number"
        sortable
        prop="number">
        <template slot-scope="{ row }">
          <span
            class="link-color"
            @click="handleMenuClick('show original', row)">
            {{row.count}}</span>
        </template>
      </bk-table-column>

      <bk-table-column
        :label="$t('占比')"
        :render-header="$renderHeader"
        :width="getTableWidth.percentage"
        sortable
        prop="percentage">
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
          align="center"
          header-align="center"
          :width="getTableWidth.year_on_year_count"
          :label="$t('同比数量')"
          :render-header="$renderHeader"
          :sort-by="'year_on_year_count'">
          <template slot-scope="{ row }">
            <span>{{row.year_on_year_count}}</span>
          </template>
        </bk-table-column>

        <bk-table-column
          sortable
          align="center"
          header-align="center"
          :width="getTableWidth.year_on_year_percentage"
          :label="$t('同比变化')"
          :render-header="$renderHeader"
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
              <text-highlight
                style="word-break: break-all;"
                :queries="getHeightLightList(row.pattern)">
                {{getHeightLightStr(row.pattern)}}
              </text-highlight>
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

      <template v-if="requestData.group_by.length">
        <bk-table-column
          v-for="(item,index) of requestData.group_by"
          :key="index"
          :label="item"
          :render-header="$renderHeader"
          width="130"
          class-name="symbol-column">
          <template slot-scope="{ row }">
            <span>{{row.group[index]}}</span>
          </template>
        </bk-table-column>
      </template>

      <bk-table-column
        :label="$t('告警')"
        :render-header="$renderHeader"
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
            <bk-popover v-if="row.monitor.is_active" :content="$t('可去告警策略编辑')">
              <span
                class="bk-icon icon-edit2 link-color"
                @click="policyEditing(row.monitor.strategy_id)"></span>
            </bk-popover>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column
        :label="$t('标签')"
        :render-header="$renderHeader"
        width="160"
        align="center"
        header-align="center">
        <template slot-scope="{ row, $index }">
          <div class="lable-edit-box" v-if="editLabelIndex === $index">
            <bk-form
              ref="labelRef"
              style="width: 100%"
              :rules="rules"
              :label-width="0">
              <bk-form-item property="labelRuels">
                <bk-input
                  clearable
                  behavior="simplicity"
                  v-model="verifyData.editLabelStr"
                  @enter="handleChangeLabel(row)"></bk-input>
              </bk-form-item>
            </bk-form>
            <div class="operate-button">
              <span class="bk-icon icon-check-line" @click="handleChangeLabel(row)"></span>
              <span class="bk-icon icon-close-line-2" @click="handleCancelLable"></span>
            </div>
          </div>
          <div class="row-label" v-else>
            <div class="label-container">
              <span class="label-str title-overflow" v-bk-overflow-tips>
                {{row.label || '--'}}
              </span>
              <span
                v-show="hoverLabelIndex === $index"
                class="bk-icon icon-edit-line"
                @click="handleEditLabel(row.label, $index)">
              </span>
            </div>
          </div>
        </template>
      </bk-table-column>

      <!-- <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column> -->

      <template slot="append" v-if="fingerList.length && isPageOver">
        <clustering-loader :width-list="loaderWidthList" />
      </template>

      <template slot="append" v-if="isShowBottomTips">
        <div class="bottom-tips">
          <i18n path="已加载完全部数据，如需查看更多查询条件可以{0}">
            <span @click="handleReturnTop">{{$t('返回顶部')}}</span>
          </i18n>
        </div>
      </template>

      <div slot="empty">
        <empty-status empty-type="empty" :show-text="false">
          <div class="empty-text" v-if="!clusterSwitch || !configData.extra.signature_switch">
            <p>{{getLeaveText}}</p>
            <span class="empty-leave" @click="handleLeaveCurrent">{{$t('去设置')}}</span>
          </div>
          <p v-if="fingerList.length === 0 && configData.extra.signature_switch">{{$t('暂无数据')}}</p>
        </empty-status>
      </div>
    </bk-table>
  </div>
</template>

<script>
import ClusterEventPopover from './components/cluster-event-popover';
import ClusteringLoader from '@/skeleton/clustering-loader';
import fingerSelectColumn from './components/finger-select-column';
import { copyMessage } from '@/common/util';
import TextHighlight from 'vue-text-highlight';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    ClusterEventPopover,
    ClusteringLoader,
    TextHighlight,
    EmptyStatus,
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
      checkValue: 0, // 0为不选 1为半选 2为全选
      editLabelIndex: -1,
      // editLabelStr: '',
      hoverLabelIndex: -1,
      verifyData: {
        editLabelStr: '',
      },
      rules: {
        labelRuels: [
          {
            validator: this.checkName,
            message: this.$t('{n}不规范, 包含特殊符号.', { n: this.$t('标签') }),
            trigger: 'blur',
          },
          {
            max: 50,
            message: this.$t('不能多于50个字符'),
            trigger: 'blur',
          },
        ],
      },
      enTableWidth: {
        number: '110',
        percentage: '116',
        year_on_year_count: '171',
        year_on_year_percentage: '171',
      },
      cnTableWidth: {
        number: '91',
        percentage: '96',
        year_on_year_count: '101',
        year_on_year_percentage: '101',
      },
    };
  },
  inject: ['addFilterCondition'],
  computed: {
    scrollContent() {
      return document.querySelector('.result-scroll-container');
    },
    bkBizId() {
      return this.$store.state.bkBizId;
    },
    isShowBottomTips() {
      return this.fingerList.length >= 50 && this.fingerList.length === this.allFingerList.length;
    },
    getLeaveText() {
      return !this.clusterSwitch ? this.$t('当前日志聚类未启用，请前往设置') : this.$t('当前数据指纹未启用，请前往设置');
    },
    getTableWidth() {
      return this.$store.getters.isEnLanguage ? this.enTableWidth : this.cnTableWidth;
    },
  },
  watch: {
    'fingerList.length': {
      handler(newLength, oldLength) {
        // 全选时 分页下拉新增页默认选中
        if (this.isSelectAll) {
          this.$nextTick(() => {
            this.selectList.push(...this.fingerList.slice(oldLength, newLength));
          });
        }
      },
    },
    'selectList.length'(newLength) {
      // 选择列表数据大小计算
      if (this.isSelectAll) {
        this.selectSize = newLength + this.allFingerList.length - this.fingerList.length;
      } else {
        this.selectSize = newLength;
      }
      // 根据手动选择列表长度来判断全选框显示 全选 半选 不选
      if (!newLength) {
        this.checkValue = 0;
        return;
      }
      if (newLength && newLength !== this.fingerList.length) {
        this.checkValue = 1;
      } else {
        this.checkValue = 2;
      };
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
    /**
     * @desc: 批量开启或者关闭告警
     * @param { Boolean } option 开启或关闭
     */
    handleBatchUseAlarm(option = true) {
      if (this.isRequestAlarm) {
        return;
      };
      const title = option ? this.$t('是否批量开启告警') : this.$t('是否批量关闭告警');
      this.$bkInfo({
        title,
        confirmFn: () => {
          let alarmList = this.selectList;
          if (this.isSelectAll) {
            // 全选时获取未显示的数据指纹
            alarmList = alarmList.concat(this.allFingerList.slice(alarmList.length));
          }
          // 过滤告警开启或者关闭状态的元素
          let filterList;
          if (option) {
            filterList = alarmList.filter(el => !el.monitor.is_active);
          } else {
            filterList = alarmList.filter(el => !!el.monitor.is_active);
          }
          // 分组情况下过滤重复的列表元素
          if (this.requestData.group_by.length) {
            filterList = this.getSetList(filterList);
          }
          this.requestAlarm(filterList, option, () => {
            // 批量成功后刷新数据指纹请求
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
          this.requestAlarm([row], !isActive, (result, strategyID) => {
            if (this.requestData.group_by.length) {
              this.$emit('updateRequest');
              return;
            }
            // 单次成功后告警状态取反
            if (result) {
              row.monitor.is_active = !isActive;
              row.monitor.strategy_id = strategyID;
            }
          });
        },
      });
    },
    getSetList(list = []) {
      const setIDList = new Set();
      const returnList = list.filter((el) => {
        if (!setIDList.has(el.signature)) {
          setIDList.add(el.signature);
          return true;
        }
      });
      return returnList;
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
          theme: 'success',
          message: state ? this.$t('已全部开启告警') : this.$t('已全部关闭告警'),
        });
        return;
      }

      const action = state ? 'create' : 'delete';
      // 组合告警请求数组
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
          /**
           * 当操作成功时 统一提示操作成功
           * 当操作失败时 分批量和单次
           * 单次显示返回值的提示 批量则显示部分操作成功
           */
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
          callback(result, operators[0].strategy_id);
        })
        .finally(() => {
          this.isRequestAlarm = false;
        });
    },
    policyEditing(strategyID) {
      // 监控编辑策略跳转
      window.open(`${window.MONITOR_URL}/?bizId=${this.bkBizId}#/strategy-config/edit/${strategyID}`, '_blank');
    },
    handleScroll() {
      if (this.throttle) return;
      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;
        // scroll变化时判断是否展示返回顶部的Icon
        this.$emit('handleScrollIsShow');
        if (this.fingerList.length >= this.allFingerList.length) return;
        const el = document.querySelector('.result-scroll-container');
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 5) {
          el.scrollTop = el.scrollTop - 5;
          this.throttle = false;
          this.$emit('paginationOptions');
        }
      }, 200);
    },
    renderHeader(h) {
      return h(fingerSelectColumn, {
        props: {
          value: this.checkValue,
          disabled: !this.fingerList.length,
        },
        on: {
          change: this.handleSelectionChange,
        },
      });
    },
    /**
     * @desc: 单选操作
     * @param { Object } row 操作元素
     * @param { Boolean } state 单选状态
     */
    handleRowCheckChange(row, state) {
      if (state) {
        this.selectList.push(row);
      } else {
        const index = this.selectList.indexOf(row);
        this.selectList.splice(index, 1);
      }
    },
    getCheckedStatus(row) {
      return this.selectList.includes(row);
    },
    /**
     * @desc: 全选和全不选操作
     * @param { Boolean } state 是否全选
     */
    handleSelectionChange(state) {
      this.isSelectAll = state;
      this.selectSize = state ? this.allFingerList.length : 0;
      // 先清空数组，如果是全选状态再添加当前已显示的元素
      this.selectList.splice(0, this.selectList.length);
      state && this.selectList.push(...this.fingerList);
    },
    handleReturnTop() {
      const el = document.querySelector('.result-scroll-container');
      this.$easeScroll(0, 300, el);
    },
    getHeightLightStr(str) {
      return !!str ? str : this.$t('未匹配');
    },
    getHeightLightList(str) {
      return str.match(/#.*?#/g) || [];
    },
    handleEditLabel(labelStr, index) {
      this.editLabelIndex = index;
      this.verifyData.editLabelStr = labelStr;
    },
    async handleChangeLabel(row) {
      this.$refs.labelRef.validate().then(() => {
        this.$http.request('/logClustering/editLabel', {
          params: {
            index_set_id: this.$route.params.indexId,
          },
          data: {
            signature: row.signature,
            label: this.verifyData.editLabelStr.trim(),
          },
        }).then((res) => {
          if (res.result) {
            row.label = this.verifyData.editLabelStr.trim();
            this.editLabelIndex = -1;
            this.$bkMessage({
              theme: 'success',
              message: this.$t('修改成功'),
            });
          }
        })
          .finally(() => {
            this.verifyData.editLabelStr = '';
          });
      });
    },
    checkName() {
      if (this.verifyData.editLabelStr.trim() === '') return true;
      // eslint-disable-next-line no-useless-escape
      return /^[\u4e00-\u9fa5_a-zA-Z0-9`~!\s@#$%^&*()_\-+=<>?:"{}|,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]+$/im.test(this.verifyData.editLabelStr.trim());
    },
    handleCancelLable() {
      this.editLabelIndex = -1;
      this.verifyData.editLabelStr = '';
    },
  },
};
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';

.finger-container {
  position: relative;

  .top-operate {
    position: absolute;
    top: 42px;
    z-index: 99;
    width: 100%;
    height: 32px;
    font-size: 12px;
    background: #f0f1f5;
    border-top: 1px solid #dfe0e5;
    border-bottom: 1px solid #dfe0e5;

    @include flex-center;

    .operate-message {
      padding-right: 6px;
      color: #63656e;
    }

    .operate-click {
      color: #3a84ff;
      cursor: pointer;
      padding-right: 6px;
    }
  }

  .finger-cluster-table {
    :deep(.bk-table-body-wrapper) {
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

    :deep(.bk-table-row-last) {
      td {
        border: none;
      }
    }

    .signature-box {
      margin-top: 1px;

      span {
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
      .show-whole-btn {
        background-color: #f0f1f5;
      }
    }

    .row-label {
      display: flex;
      justify-content: center;

      .label-container {
        max-width: 90%;
        position: relative;
        display: flex;
        align-items: center;
      }

      .icon-edit-line {
        position: absolute;
        right: -16px;
        color: #3a84ff;
        font-size: 14px;
        cursor: pointer;
      }
    }

    .lable-edit-box {
      display: flex;
      align-items: center;

      .operate-button {
        display: flex;
        margin-left: 6px;
        justify-content: space-between;
        color: #979ba5;

        span {
          font-size: 16px;
          display: inline-block;
          cursor: pointer;
        }

        > :first-child {
          color: #33d05c;
          margin-right: 12px;
        }

        > :last-child {
          color: #979ba5;
        }
      }
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
  :deep(.bk-table-header-wrapper) {
    tr {
      > th {
        /* stylelint-disable-next-line declaration-no-important */
        border-bottom: none !important;
      }
    }
  }
}

.bottom-tips {
  height: 43px;
  line-height: 43px;
  text-align: center;
  color: #979ba5;

  span {
    color: #3a84ff;
    cursor: pointer;
  }
}

.new-finger {
  width: 40px;
  height: 16px;
  font-size: 12px;
  line-height: 14px;
  text-align: center;
  color: #ea3636;
  background: #fee;
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
