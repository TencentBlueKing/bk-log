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
  <div class="fingerprint-setting fl-sb">
    <div class="fl-sb">
      <span>{{$t('分组')}}</span>
      <bk-select
        multiple
        display-tag
        behavior="simplicity"
        ext-cls="compared-select"
        v-model="group"
        :popover-min-width="180"
        :disabled="!fingerOperateData.signatureSwitch"
        @toggle="handleSelectGroup">
        <bk-option
          v-for="item in fingerOperateData.groupList"
          :key="item.id"
          :id="item.id"
          :name="item.name">
        </bk-option>
      </bk-select>
    </div>

    <div class="fl-sb">
      <span>{{$t('同比')}}</span>
      <bk-select
        behavior="simplicity"
        ext-cls="compared-select"
        ext-popover-cls="compared-select-option"
        v-model="yearOnYearHour"
        data-test-id="fingerTable_select_selectCustomSize"
        :disabled="!fingerOperateData.signatureSwitch"
        :clearable="false"
        :popover-min-width="140"
        @change="handleSelectCompared"
        @toggle="changeCustomizeState(true)">
        <bk-option
          v-for="option in fingerOperateData.comparedList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
        <div slot="" class="compared-customize">
          <div class="customize-option"
               v-if="fingerOperateData.isShowCustomize"
               @click="changeCustomizeState(false)">
            <span>{{$t('自定义')}}</span>
          </div>
          <div v-else>
            <bk-input @enter="handleEnterCompared"></bk-input>
            <div class="compared-select-icon">
              <span v-bk-tooltips="$t('自定义输入格式: 如 1h 代表一小时 h小时')" class="top-end">
                <i class="log-icon icon-help"></i>
              </span>
            </div>
          </div>
        </div>
      </bk-select>
    </div>

    <div class="is-near24">
      <bk-checkbox
        v-model="isNear24"
        data-test-id="fingerTable_checkBox_selectCustomSize"
        :true-value="true"
        :false-value="false"
        :disabled="!fingerOperateData.signatureSwitch"
        @change="handleShowNearPattern">
      </bk-checkbox>
      <span
        @mouseenter="handleShowAlarmPopover"
        @click="handleChangeTrigger">{{$t('近24H新增')}}</span>
      <div v-show="false">
        <div
          ref="alarmPopover"
          slot="content"
          class="alarm-content">
          <span @click.stop="updateNewClsStrategy">{{!alarmSwitch ? $t('开启告警') : $t('关闭告警')}}</span>
          <span
            v-if="alarmSwitch"
            class="right-alarm"
            @click="handleEmitEditAlarm">
            {{$t('编辑告警')}}</span>
        </div>
      </div>
    </div>

    <div class="pattern fl-sb" style="width: 200px">
      <span>Pattern</span>
      <div class="pattern-slider-box fl-sb">
        <span>{{$t('少')}}</span>
        <bk-slider
          class="pattern-slider"
          v-model="patternSize"
          data-test-id="fingerTable_slider_patterSize"
          :show-tip="false"
          :disable="!fingerOperateData.signatureSwitch"
          :max-value="fingerOperateData.sliderMaxVal"
          @change="handleChangepatternSize"></bk-slider>
        <span>{{$t('多')}}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    fingerOperateData: {
      type: Object,
      require: true,
    },
    requestData: {
      type: Object,
      require: true,
    },
    totalFields: {
      type: Array,
      require: true,
    },
  },
  data() {
    return {
      interactType: false, // false 为hover true 为click
      alarmSwitch: false,
      group: [], // 当前选择分组的值
      isToggle: false, // 当前是否显示分组下拉框
      patternSize: 0,
      yearOnYearHour: 0,
      isNear24: false,
      isRequestAlarm: false,
      popoverInstance: null,
    };
  },
  computed: {
    bkBizId() {
      return this.$store.state.bkBizId;
    },
  },
  watch: {
    group: {
      deep: true,
      handler(list) {
        // 分组列表未展开时数组变化则发送请求
        if (!this.isToggle) {
          this.$emit('handleFingerOperate', 'group', list);
        }
      },
    },
  },
  mounted() {
    this.initCache();
    this.handlePopoverShow();
  },
  beforeDestroy() {
    this.popoverInstance = null;
  },
  methods: {
    handleSelectCompared(newVal) {
      this.$emit('handleFingerOperate', 'compared', newVal);
    },
    handleEnterCompared(val) {
      this.$emit('handleFingerOperate', 'enterCustomize', val);
    },
    handleShowNearPattern(state) {
      this.$emit('handleFingerOperate', 'isShowNear', state);
    },
    handleChangepatternSize(val) {
      this.$emit('handleFingerOperate', 'patternSize', this.fingerOperateData.patternList[val]);
    },
    changeCustomizeState(val) {
      this.$emit('handleFingerOperate', 'customize', val);
    },
    handleSelectGroup(state) {
      this.isToggle = state;
      !state && this.$emit('handleFingerOperate', 'group', this.group);
    },
    handleEmitEditAlarm() {
      this.$emit('handleFingerOperate', 'editAlarm');
    },
    handlePopoverShow() {
      if (JSON.stringify(this.fingerOperateData.alarmObj) === '{}') {
        this.initNewClsStrategy();
      }
    },
    /**
     * @desc: 改变近24H新增的交互类型
     */
    handleChangeTrigger() {
      if (!this.interactType) {
        this.popoverInstance?.set({
          trigger: 'click',
          hideOnClick: true,
        });
      }
      this.interactType = true;
    },
    handleShowAlarmPopover(e) {
      if (this.popoverInstance || !this.fingerOperateData.signatureSwitch) return;
      this.popoverInstance = this.$bkPopover(e.target, {
        content: this.$refs.alarmPopover,
        trigger: 'mouseenter',
        placement: 'top',
        arrow: true,
        theme: 'light',
        interactive: true,
        hideOnClick: false,
      });
      this.popoverInstance && this.popoverInstance.show();
    },
    initCache() {
      // 赋值缓存
      this.patternSize = this.fingerOperateData.patternSize;
      this.yearOnYearHour = this.requestData.year_on_year_hour;
      this.isNear24 = this.requestData.show_new_pattern;
      this.alarmSwitch = this.fingerOperateData.alarmObj?.is_active;
      if (this.requestData.group_by?.length) this.group = this.requestData.group_by;
    },
    /**
     * @desc: 查询新类告警
     */
    initNewClsStrategy() {
      this.$http.request('/logClustering/getNewClsStrategy', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
      }).then((res) => {
        this.$emit('handleFingerOperate', 'getNewStrategy', res.data);
        this.alarmSwitch = res.data.is_active;
      });
    },
    /**
     * @desc: 更新新类告警
     */
    updateNewClsStrategy() {
      const action = this.alarmSwitch ? 'delete' : 'create';
      const strategyID = this.fingerOperateData.alarmObj?.strategy_id;
      const queryObj = {
        bk_biz_id: this.bkBizId,
        strategy_id: strategyID,
        action,
      };
      // 开启新类告警时需删除strategy_id字段
      !this.alarmSwitch && delete queryObj.strategy_id;
      this.isRequestAlarm = true,
      this.$http.request('/logClustering/updateNewClsStrategy', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data: { ...queryObj },
      }).then((res) => {
        if (res.result) {
          this.popoverInstance.hide();
          this.$emit('handleFingerOperate', 'getNewStrategy', {
            strategy_id: res.data,
            is_active: !this.alarmSwitch,
          });
          this.$bkMessage({
            theme: 'success',
            message: this.$t('操作成功'),
            ellipsisLine: 0,
          });
          setTimeout(() => {
            this.alarmSwitch = !this.alarmSwitch;
          }, 200);
        }
      })
        .finally(() => {
          this.isRequestAlarm = false;
        });
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.fingerprint-setting {
  height: 24px;
  line-height: 24px;
  font-size: 12px;

  > div {
    margin-left: 20px;
  }

  .is-near24 {
    @include flex-center;

    > span {
      border-bottom: 1px dashed #979ba5;
      margin-left: 4px;
      line-height: 16px;
      cursor: pointer;
    }
  }

  .compared-select {
    min-width: 87px;
    margin-left: 6px;
    position: relative;
    top: -3px;

    .bk-select-name {
      height: 24px;
    }

    .bk-select-tag-container {
      height: 24px;
      min-height: 24px;
      max-width: 170px;
    }
  }

  .pattern {
    width: 200px;

    .pattern-slider-box {
      width: 154px;
    }

    .pattern-slider {
      width: 114px;
    }
  }
}

.compared-select-option {
  .compared-customize {
    position: relative;
    top: -3px;

    .bk-select-name {
      height: 24px;
    }
  }
}

.compared-select-option {
  .compared-customize {
    position: relative;
    margin-bottom: 6px;
  }

  .compared-select-icon {
    font-size: 14px;
    position: absolute;
    right: 18px;
    top: 2px;
  }

  .customize-option {
    padding: 0 18px;
    cursor: pointer;

    &:hover {
      color: #3a84ff;
      background: #eaf3ff;
    }
  }

  .bk-form-control {
    width: 80%;
    margin: 0 auto;
  }

  .bk-form-input {
    /* stylelint-disable-next-line declaration-no-important */
    padding: 0 18px 0 10px !important;
  }
}

.alarm-content {
  color: #3a84ff;
  font-size: 12px;
  cursor: pointer;

  .right-alarm {
    margin-left: 6px;

    &:before {
      content: '|';
      margin-right: 6px;
      color: #dcdee5;
    }
  }
}

.fl-sb {
  align-items: center;

  @include flex-justify(space-between);
}
</style>
