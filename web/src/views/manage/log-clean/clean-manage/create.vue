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
  <div class="log-clean-create-container" v-bkloading="{ isLoading: loading }">
    <article class="article" v-if="!isCleaning">
      <step-field
        v-if="curStep === 1"
        :cur-step="curStep"
        :is-clean-field="true"
        @stepChange="stepChange"
        @changeClean="isCleaning = true"
        @change-submit="changeSubmit" />
      <step-storage
        v-if="curStep === 2"
        :cur-step="curStep"
        :is-clean-field="true"
        @stepChange="stepChange"
        @change-submit="changeSubmit" />
    </article>

    <article class="article clean-landing" v-else>
      <advance-clean-land back-router="log-clean-list" />
    </article>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import stepField from '@/components/collection-access/step-field';
import stepStorage from '@/components/collection-access/step-storage';
import advanceCleanLand from '@/components/collection-access/advance-clean-land';

export default {
  name: 'LogCleanCreate',
  components: {
    stepField,
    stepStorage,
    advanceCleanLand,
  },
  data() {
    return {
      curStep: 1,
      isCleaning: false,
      loading: false,
      isSubmit: false,
      collectItem: '',
    };
  },
  computed: {
    ...mapState({
      showRouterLeaveTip: state => state.showRouterLeaveTip,
    }),
  },
  // eslint-disable-next-line no-unused-vars
  beforeRouteLeave(to, from, next) {
    if (!this.isSubmit && !this.showRouterLeaveTip) {
      this.$bkInfo({
        title: this.$t('pageLeaveTips'),
        confirmFn: () => {
          next();
        },
      });
      return;
    }
    next();
  },
  methods: {
    changeSubmit(isSubmit) {
      this.isSubmit = isSubmit;
    },
    stepChange(num) {
      if (num === 'back') {
        this.$router.push({
          name: 'log-clean-list',
          query: {
            spaceUid: this.$store.state.spaceUid,
          },
        });
        return;
      }

      this.curStep = num;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '@/scss/mixins/scroller';

  .log-clean-create-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;

    @include scroller($backgroundColor: #ADADAD, $width: 4px);

    .article {
      margin-bottom: 20px;
      border: 1px solid #dcdee5;
      border-radius: 3px;
      background-color: #fff;
    }

    .clean-landing {
      border: 0;
      height: calc(100% - 24px);
    }
  }
</style>
