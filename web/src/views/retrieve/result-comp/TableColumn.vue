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
  <div :class="['td-log-container', { 'is-wrap': isWrap }]" @click.stop>
    <!-- eslint-disable vue/no-v-html -->
    <span
      :class="[
        'field-container',
        'add-to',
        { 'active': hasClickEvent },
        { 'mark': markList.includes(formatterStr(content)) }
      ]"
      @click.stop="handleClickContent"
      v-bk-tooltips="{ content: $t('查看调用链'), disabled: !hasClickEvent, delay: 500 }">
      <text-segmentation
        v-if="isInViewPort"
        :content="content"
        :field-type="fieldType"
        :menu-click="handleMenuClick">
      </text-segmentation>
      <!-- <span v-else>{{ formatterStr(content) }}</span> -->
      <text-highlight
        v-else
        style="word-break: break-all;"
        :queries="markList">
        {{formatterStr(content)}}
      </text-highlight>
    </span>
  </div>
</template>

<script>
import TextSegmentation from './TextSegmentation';
import TextHighlight from 'vue-text-highlight';

export default {
  components: {
    TextSegmentation,
    TextHighlight,
  },
  props: {
    isWrap: {
      type: Boolean,
      default: false,
    },
    content: {
      type: [String, Number, Boolean],
      required: true,
    },
    hasClickEvent: {
      type: Boolean,
      default: false,
    },
    fieldType: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isInViewPort: false,
    };
  },
  computed: {
    // isInViewPort() {
    //   const {
    //     top,
    //     bottom,
    //   } = this.$el.getBoundingClientRect();
    //   return (top > 0 && top <= innerHeight) || (bottom >= 0 && bottom < innerHeight);;
    // },
    // 高亮
    markList() {
      const markVal = this.content.toString().match(/(?<=<mark>).*?(?=<\/mark>)/g) || [];
      return markVal;
    },
  },
  mounted() {
    setTimeout(this.registerObserver, 20);
  },
  beforeDestroy() {
    this.unregisterOberver();
  },
  methods: {
    formatterStr(content) {
      // 匹配高亮标签
      let value = content;
      const markVal = content.toString().match(/(?<=<mark>).*?(?=<\/mark>)/g) || [];
      if (markVal) {
        value = String(value).replace(/<mark>/g, '')
          .replace(/<\/mark>/g, '');
      }

      return value;
    },
    handleClickContent() {
      if (this.hasClickEvent) this.$emit('contentClick');
    },
    handleMenuClick(option, content) {
      const operator = option === 'not' ? 'is not' : option;
      this.$emit('iconClick', operator, content);
    },
    unregisterOberver() {
      if (this.intersectionObserver) {
        this.intersectionObserver.unobserve(this.$el);
        // console.info('unobserve : ', this.$el, this.intersectionObserver);
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
            if (entry.boundingClientRect.height > 72) {
              this.$emit('computedHeight');
            }
            if (entry.intersectionRatio > 0) {
              this.isInViewPort = true;
            } else {
              this.isInViewPort = false;
            }
          }
        });
      });
      this.intersectionObserver.observe(this.$el);
    },
  },
};
</script>

<style lang="scss" scoped>
.td-log-container {
  position: relative;
  line-height: 14px;
  &.is-wrap {
    padding-bottom: 4px;
  }
  .field-container {
    &.active:hover {
      color: #3a84ff;
      cursor: pointer;
    }
    &.mark {
      background-color: #f3e186;
      color: black;
    }
  }
  .icon-search-container {
    display: none;
    justify-content: center;
    align-items: center;
    vertical-align: bottom;
    width: 14px;
    height: 14px;
    margin-left: 5px;
    cursor: pointer;
    background: #3a84ff;
    .icon {
      font-size: 12px;
      font-weight: bold;
      color: #fff;
      background: #3a84ff;
      transform: scale(.6);
      &.icon-copy {
        font-size: 14px;
        transform: scale(1);
      }
    }
  }
  &:hover {
    .icon-search-container {
      display: inline-flex;
    }
  }
}
</style>
