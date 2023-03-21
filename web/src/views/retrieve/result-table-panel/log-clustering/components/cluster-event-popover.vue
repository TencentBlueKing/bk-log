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
  <bk-popover
    ref="eventPopover"
    :class="['retrieve-event-popover', { 'is-inline': !isCluster }]"
    :ext-cls="`event-tippy${!isCluster ? ' is-cluster' : ''}`"
    :trigger="trigger"
    :placement="placement"
    :tippy-options="tippyOptions"
    :on-show="handlePopoverShow"
    :on-hide="handlePopoverHide"
    theme="light">
    <slot />
    <div slot="content" class="event-icons">
      <span
        v-if="isCluster"
        class="icon bk-icon icon-eye"
        v-bk-tooltips.top="{ content: $t('查询命中pattern的日志'), delay: 300 }"
        @click="handleClick('show original')">
      </span>
      <!-- <span
        v-if="isCluster"
        class="icon log-icon icon-chart"
        v-bk-tooltips.top="{ content: $t(''), delay: 300 }"
        @click="handleClick('a')">
      </span> -->
      <span
        v-if="isHavePattern"
        class="icon log-icon icon-copy"
        v-bk-tooltips.top="{ content: $t('复制'), delay: 300 }"
        @click="handleClick('copy')">
      </span>
    </div>
  </bk-popover>
</template>

<script>
export default {
  props: {
    placement: {
      type: String,
      default: 'bottom',
    },
    trigger: {
      type: String,
      default: 'click',
    },
    isCluster: {
      type: Boolean,
      default: true,
    },
    tippyOptions: {
      type: Object,
      default: () => {},
    },
    context: {
      type: String,
      require: true,
    },
  },
  computed: {
    isHavePattern() {
      return this.context !== '';
    },
  },
  methods: {
    handleClick(id) {
      this.$emit('eventClick', id);
    },
    unregisterOberver() {
      if (this.intersectionObserver) {
        this.intersectionObserver.unobserve(this.$el);
        this.intersectionObserver.disconnect();
        this.intersectionObserver = null;
      }
    },
    // 注册Intersection监听
    registerObserver() {
      if (this.intersectionObserver) {
        this.unregisterOberver();
      }
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (this.intersectionObserver) {
            if (entry.intersectionRatio <= 0) {
              this.$refs.eventPopover.instance.hide();
            }
          }
        });
      });
      this.intersectionObserver.observe(this.$el);
    },
    handlePopoverShow() {
      setTimeout(this.registerObserver, 20);
    },
    handlePopoverHide() {
      this.unregisterOberver();
    },
  },
};
</script>

<style lang="scss">
  .event-icons {
    position: relative;
  }

  .event-tippy {
    .event-icons {
      min-height: 24px;
      display: flex;
      align-items: center;
    }

    .tippy-tooltip {
      padding: 4px 0 2px 8px;
    }

    .icon {
      display: inline-block;
      margin-right: 8px;
      font-size: 14px;
      cursor: pointer;

      &:hover {
        color: #3a84ff;
      }
    }

    .log-icon {
      font-size: 12px;
    }

    .icon-chart {
      margin-right: 4px;
    }

    .icon-copy {
      margin-right: 3px;
      font-size: 24px;
    }

    &.is-cluster {
      .tippy-tooltip {
        padding-left: 4px;
      }
    }
  }

  .retrieve-event-popover {
    .bk-tooltip-ref {
      cursor: pointer;

      &:hover {
        color: #3a84ff;
      }
    }

    mark {
      color: #575961;
      background: #f0f1f5;
    }

    &.is-inline {
      display: inline;

      .bk-tooltip-ref {
        display: inline;
      }

      .tippy-tooltip {
        padding-left: 0;
      }
    }
  }
</style>
