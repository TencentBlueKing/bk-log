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
  <div class="right-panel" :class="{ 'need-border': needBorder }">
    <div
      @click="handleTitleClick"
      class="right-panel-title"
      :class="{ 'is-collapse': isEndCollapse }"
      :style="{ 'backgroundColor': titleBgColor }">
      <slot name="panel">
        <slot name="pre-panel"></slot>
        <i
          class="bk-icon title-icon"
          :style="{ 'color': collapseColor }"
          :class="[collapse ? 'icon-down-shape' : 'icon-right-shape']">
        </i>
        <div class="title-desc">
          <slot name="title">
            <i18n path="已选择{0}个{1}">
              <span class="title-desc-num">{{title.num}}</span>
              <span>{{title.type || $t('主机')}}</span>
            </i18n>
          </slot>
        </div>
      </slot>
    </div>
    <transition
      :css="false"
      @before-enter="beforeEnter"
      @enter="enter"
      @after-enter="afterEnter"
      @before-leave="beforeLeave"
      @leave="leave"
      @after-leave="afterLeave"
      @leave-cancelled="afterLeave">
      <div class="right-panel-content" v-show="collapse">
        <slot>
        </slot>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'RightPanel',
  model: {
    prop: 'collapse',
    event: 'change',
  },
  props: {
    collapse: Boolean,
    title: {
      type: Object,
      default() {
        return {
          num: 0,
          type: this.$t('主机'),
        };
      },
    },
    collapseColor: {
      type: String,
      default: '#63656E',
    },
    titleBgColor: {
      type: String,
      default: '#FAFBFD',
    },
    type: String,
    needBorder: Boolean,
  },
  data() {
    return {
      isEndCollapse: this.collapse,
    };
  },
  methods: {
    beforeEnter(el) {
      el.classList.add('collapse-transition');
      el.style.height = '0';
    },
    enter(el) {
      el.dataset.oldOverflow = el.style.overflow;
      if (el.scrollHeight !== 0) {
        el.style.height = `${el.scrollHeight}px`;
      } else {
        el.style.height = '';
      }
      this.$nextTick().then(() => {
        this.isEndCollapse = this.collapse;
      });
      el.style.overflow = 'hidden';
      setTimeout(() => {
        el.style.height = '';
        el.style.overflow = el.dataset.oldOverflow;
      }, 300);
    },
    afterEnter(el) {
      el.classList.remove('collapse-transition');
    },
    beforeLeave(el) {
      el.dataset.oldOverflow = el.style.overflow;
      el.style.height = `${el.scrollHeight}px`;
      el.style.overflow = 'hidden';
    },
    leave(el) {
      if (el.scrollHeight !== 0) {
        el.classList.add('collapse-transition');
        el.style.height = 0;
      }
      setTimeout(() => {
        this.isEndCollapse = this.collapse;
      }, 300);
    },
    afterLeave(el) {
      el.classList.remove('collapse-transition');
      setTimeout(() => {
        el.style.height = '';
        el.style.overflow = el.dataset.oldOverflow;
      }, 300);
    },
    handleTitleClick() {
      this.$emit('change');
    },
  },
};
</script>

<style lang="scss" scoped>
  .right-panel {
    &.need-border {
      border: 1px solid #dcdee5;
      border-radius: 2px;
    }

    &-title {
      display: flex;
      height: 40px;
      background: #fafbfd;
      color: #63656e;
      font-weight: bold;
      align-items: center;
      padding: 0 16px;
      cursor: pointer;

      &.is-collapse {
        border-bottom: 1px solid #dcdee5;
        height: 41px;
      }

      .title-icon {
        font-size: 14px;
        margin-right: 5px;

        &:hover {
          cursor: pointer;
        }
      }

      .title-desc {
        color: #979ba5;

        &-num {
          color: #3a84ff;
          margin: 0 3px;
        }
      }
    }

    &-content {
      ::v-deep .bk-table {
        border: 0;

        .bk-table-header {
          th {
            background: #fff;
          }
        }

        &::after {
          width: 0;
        }
      }
    }

    .collapse-transition {
      transition: .3s height ease-in-out;
    }
  }
</style>
