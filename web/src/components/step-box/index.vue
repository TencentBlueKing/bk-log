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
    class="step-box"
    :class="className"
    :style="style">
    <div class="step-title">
      <slot name="title"></slot>
    </div>
    <div class="step-content">
      <slot name="content"></slot>
    </div>
    <div class="step-action">
      <slot name="action"></slot>
    </div>
    <div class="target-arrow"></div>
  </div>
</template>

<script>
export default {
  props: {
    placement: {
      type: String,
      default: '',
    },
    tipStyles: {
      type: Object,
      default: {},
    },
    hasBorder: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    className() {
      return `${this.placement} ${this.hasBorder ? 'has-border' : ''}`;
      // return this.placement;
    },
    style() {
      return this.tipStyles;
    },
  },
};
</script>


<style lang='scss'>
.step-box {
  position: absolute;
  width: 270px;
  min-height: 110px;
  padding: 12px 10px 10px;
  font-size: 12px;
  color: #313238;
  border-radius: 2px;
  background: #fff;

  &.has-border {
    box-shadow: 0 0 6px 0 #dcdee5;
    background-color: #fff;
    border: 1px solid #dcdee5;
  }

  &.right {
    .target-arrow {
      top: 30px;
      left: -4px;
    }
  }

  &.left {
    .target-arrow {
      top: 30px;
      right: -4px;
    }
  }

  &.bottom {
    .target-arrow {
      top: -4px;
      left: 50%;
    }
  }

  &.top {
    .target-arrow {
      bottom: -4px;
      left: 50%;
    }
  }

  .step-title {
    font-weight: bold;
    line-height: 16px;
  }

  .step-content {
    margin-top: 7px;
  }

  .step-action {
    display: flex;
    justify-content: flex-end;
    margin-top: 14px;

    .action-text {
      color: #3a84ff;
      cursor: pointer;
    }

    .action-btn {
      height: 20px;
      padding: 0 8px;
      margin-left: 14px;
      line-height: 20px;
      color: #fff;
      border-radius: 10px;
      background: #3a84ff;
      cursor: pointer;
    }
  }

  .target-arrow {
    position: absolute;
    width: 8px;
    height: 8px;
    background: inherit;
    transform: rotateZ(45deg);
  }
}
</style>
