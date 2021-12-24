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
  <div class="fingerprint fl-sb">
    <div class="fingerprint-setting fl-sb">
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

      <bk-checkbox
        v-model="fingerOperateData.isNear24"
        data-test-id="fingerTable_checkBox_selectCustomSize"
        :true-value="true"
        :false-value="false"
        :disabled="!fingerOperateData.signatureSwitch"
        @change="handleShowNearPattern">
        <span style="font-size: 12px">{{$t('近24H新增')}}</span>
      </bk-checkbox>

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
  },
  data() {
    return {
    };
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
  },
};
</script>
<style lang="scss">
@import "@/scss/mixins/flex.scss";

.fingerprint-setting {
  width: 485px;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
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
.compared-select {
  min-width: 87px;
  margin-left: 6px;
  position: relative;
  top: -3px;
  .bk-select-name {
    height: 24px;
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
.fl-sb {
  align-items: center;
  @include flex-justify(space-between);
}
</style>
