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
  <div>
    <slot v-if="isMountContent"></slot>
    <span v-else>{{context}}</span>
  </div>
</template>
<script>
export default {
  props: {
    context: {
      type: String,
      require: true,
    },
    rootMargin: {
      type: String,
      default: '0px 0px 0px 0px',
    },
  },
  data() {
    return {
      isMountContent: true,
    };
  },
  deactivated() {
    this.isMountContent = false;
    this.unregisterObserver();
  },
  activated() {
    this.isMountContent = true;
    setTimeout(this.registerObserver, 20);
  },
  mounted() {
    this.isMountContent = true;
    setTimeout(this.registerObserver, 20);
  },
  methods: {
    registerObserver() {
      if (this.intersectionObserver) {
        this.unregisterObserver();
      }
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (this.intersectionObserver) {
            if (entry.intersectionRatio > 0) {
              this.isMountContent = true;
            } else {
              this.isMountContent = false;
            }
          }
        });
      }, {
        rootMargin: this.rootMargin, // '-180px 0px 0px 0px',
      });
      this.intersectionObserver.observe(this.$el);
    },
    unregisterObserver() {
      if (this.intersectionObserver) {
        this.intersectionObserver.unobserve(this.$el);
        this.intersectionObserver.disconnect();
        this.intersectionObserver = null;
      }
    },
  },
};
</script>
