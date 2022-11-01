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
  <div class="ui-query-container" v-bkloading="{ isLoading: loading }">
    <div class="query-item-box" v-for="(item, index) in searchFieldsList" :key="index">
      <div class="query-title">
        <span>{{item.name}}</span>
        <span>{{item.operator}}</span>
      </div>
      <bk-input v-model="item.value" @blur="handleChangeValue"></bk-input>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    activeFavorite: {
      type: Object,
      required: true,
    },
    keyword: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      searchFieldsList: [],
      loading: false,
    };
  },
  computed: {},
  watch: {
    activeFavorite: {
      immediate: true,
      deep: true,
      handler() {
        this.getSearchFieldsList(this.keyword);
      },
    },
  },
  methods: {
    async getSearchFieldsList(keyword) {
      this.loading = true;
      try {
        const res = await this.$http.request('favorite/getSearchFields', {
          data: { keyword },
        });
        this.searchFieldsList = res.data;
      } catch (error) {} finally {
        this.loading = false;
      }
    },
    async handleChangeValue() {
      const keyword = this.activeFavorite.params.keyword;
      const params = this.searchFieldsList
        .filter(item => Boolean(item.value))
        .map(item => ({
          value: item.value,
          pos: item.pos,
        }));
      try {
        const res = await this.$http.request('favorite/getGenerateQuery', {
          data: {
            keyword,
            params,
          },
        });
        this.$emit('updateKeyWords', res.data);
      } catch (error) {}
    },
  },
};
</script>

<style lang="scss" scoped>
.ui-query-container {
  min-height: 100px;

  &:not(:last-child) .query-item-box {
    margin-bottom: 16px;
  }

  .query-title {
    font-size: 12px;
    margin-bottom: 8px;

    :first-child {
      color: #63656e;
      margin-right: 9px;
    }

    :last-child {
      font-size: 14px;
      font-weight: 700;
      color: #ff9c01;
    }
  }
}
</style>