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
    <cluster-event-popover
      v-if="isMountPatter"
      @eventClick="handleClickIcon">
      {{context}}
    </cluster-event-popover>
    <span v-else>
      {{context}}
    </span>
  </div>
</template>
<script>
import ClusterEventPopover from './ClusterEventPopover';
export default {
  components: { ClusterEventPopover },
  props: {
    context: {
      type: String,
      require: true,
    },
  },
  data() {
    return {
      isMountPatter: true,
    };
  },
  deactivated() {
    this.isMountPatter = false;
    this.unregisterOberver();
  },
  activated() {
    this.isMountPatter = true;
    setTimeout(this.registerObserver, 20);
  },
  mounted() {
    this.isMountPatter = true;
    setTimeout(this.registerObserver, 20);
  },
  methods: {
    handleClickIcon(id) {
      this.$emit('eventClick', id);
    },
    registerObserver() {
      if (this.intersectionObserver) {
        this.unregisterOberver();
      }
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (this.intersectionObserver) {
            if (entry.intersectionRatio > 0) {
              this.isMountPatter = true;
            } else {
              this.isMountPatter = false;
            }
          }
        });
      });
      this.intersectionObserver.observe(this.$el);
    },
    unregisterOberver() {
      if (this.intersectionObserver) {
        this.intersectionObserver.unobserve(this.$el);
        // console.info('unobserve : ', this.$el, this.intersectionObserver);
        this.intersectionObserver.disconnect();
        this.intersectionObserver = null;
      }
    },
  },
};
</script>

<style lang="scss">
</style>
