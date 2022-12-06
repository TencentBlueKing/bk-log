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
  <div class="log-extract-container" v-bkloading="{ isLoading }">
    <router-view></router-view>
  </div>
</template>

<script>

export default {
  name: 'Extract',
  data() {
    return {
      isRender: true,
      isLoading: false,
    };
  },
  computed: {
    bkBizId() {
      return this.$store.state.bkBizId;
    },
  },
  watch: {
    // 切换业务销毁实例
    bkBizId() {
      this.isLoading = true;
      this.isRender = false;
      setTimeout(() => {
        this.isRender = true;
        if (this.$route.query.create) {
          this.isLoading = false;
        }
      }, 400);
    },
  },
  methods: {
    backHome() {
      this.$router.push({
        name: 'extract',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    handleLoading(bool) {
      this.isLoading = bool;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../scss/mixins/scroller';

  .log-extract-container {
    padding: 0 24px 20px;
    color: #313238;
    font-size: 14px;

    .top-title-container {
      height: 60px;
      padding: 20px 0;
      margin: 0 60px;
      border-bottom: 1px solid #dde4eb;

      .top-title {
        display: flex;
        align-items: center;
        margin: 0;
        padding-left: 10px;
        border-left: 2px solid #a3c5fd;
        line-height: 20px;
        font-size: 14px;
        font-weight: bold;

        .icon-arrows-left-shape {
          color: #979ba5;
          cursor: pointer;
          padding: 2px 8px 2px 2px;
          transition: color .2s;

          &:hover {
            color: #3a84ff;
            transition: color .2s;
          }
        }
      }
    }

    ::v-deep .main-container {
      position: relative;
      padding-bottom: 60px;
      overflow: auto;

      @include scroller($backgroundColor: #c4c6cc, $width: 4px);
    }
  }
</style>
