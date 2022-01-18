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
        v-model="requestData.year_on_year_hour"
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
              <span v-bk-tooltips="$t('customizeTips')" class="top-end">
                <i class="log-icon icon-help"></i>
              </span>
            </div>
          </div>
        </div>
      </bk-select>
    </div>

    <div class="is-near24">
      <bk-checkbox
        v-model="fingerOperateData.isNear24"
        data-test-id="fingerTable_checkBox_selectCustomSize"
        :true-value="true"
        :false-value="false"
        :disabled="!fingerOperateData.signatureSwitch"
        @change="handleShowNearPattern">
      </bk-checkbox>
      <span>{{$t('近24H新增')}}</span>
      <!-- <bk-popover
        :trigger="trigger"
        theme="light">
        <span style="border-bottom: 1px dashed #000">{{$t('近24H新增')}}</span>
        <div slot="content" class="alarm-content">
          <span>是否要告警</span>
          <bk-switcher
            theme="primary"
            size="small"
            v-model="alarmSwitch">
          </bk-switcher>
        </div>
      </bk-popover> -->
    </div>

    <div class="partter fl-sb" style="width: 200px">
      <span>Partter</span>
      <div class="partter-slider-box fl-sb">
        <span>{{$t('少')}}</span>
        <bk-slider
          class="partter-slider"
          v-model="fingerOperateData.partterSize"
          data-test-id="fingerTable_slider_patterSize"
          :show-tip="false"
          :disable="!fingerOperateData.signatureSwitch"
          :max-value="fingerOperateData.sliderMaxVal"
          @change="handleChangePartterSize"></bk-slider>
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
      trigger: 'click',
      alarmSwitch: true,
      group: [], // 当前选择分组的值
      isToggle: false, // 当前是否显示分组下拉框
    };
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
    this.group = this.requestData.group_by;
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
    handleChangePartterSize(val) {
      this.$emit('handleFingerOperate', 'partterSize', this.fingerOperateData.partterList[val]);
    },
    changeCustomizeState(val) {
      this.$emit('handleFingerOperate', 'customize', val);
    },
    handleSelectGroup(state) {
      this.isToggle = state;
      !state && this.$emit('handleFingerOperate', 'group', this.group);
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.fingerprint-setting {
  width: 700px;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
  .is-near24 {
    span {
      margin-left: 4px;
      cursor: pointer;
    }
    @include flex-center;
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
  .partter {
    width: 200px;
    .partter-slider-box {
      width: 154px;
    }
    .partter-slider {
      width: 114px;
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
    padding: 0 18px 0 10px !important;
  }
}
.alarm-content {
  span {
    margin: -2px 4px 0 0;
  }
  @include flex-center;
}
.fl-sb {
  align-items: center;
  @include flex-justify(space-between);
}
</style>
