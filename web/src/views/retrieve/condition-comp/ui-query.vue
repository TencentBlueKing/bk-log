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
import { deepClone } from '../../../components/monitor-echarts/utils';

export default {
  props: {
    activeFavorite: {
      type: Object,
      required: true,
    },
    isFavoriteSearch: {
      type: Boolean,
      required: true,
    },
    keyword: {
      type: String,
      required: true,
    },
    isClearCondition: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      searchFieldsList: [], // 表单展示字段
      cacheFieldsList: [], // 修改字段之前的缓存字段
      loading: false,
      isUpdateFavorite: false,
      favoriteKeyword: '',
      isSearchInit: false,
    };
  },
  watch: {
    activeFavorite: {
      immediate: true,
      deep: true,
      handler(value) {
        this.isUpdateFavorite = true;
        this.favoriteKeyword = value?.params?.keyword || '*';
        const keyword = this.isSearchInit ? this.favoriteKeyword : this.keyword;
        this.getSearchFieldsList(keyword, value?.params?.search_fields);
      },
    },
    isClearCondition() {
      this.searchFieldsList.forEach(item => item.value = '');
      this.handleChangeValue();
    },
  },
  methods: {
    async getSearchFieldsList(keyword, fieldsList = []) {
      if (!keyword) keyword = '*';
      this.loading = true;
      try {
        const res = await this.$http.request('favorite/getSearchFields', {
          data: { keyword },
        });
        this.searchFieldsList = res.data
          .filter(item => fieldsList.includes(item.name))
          .map(item => ({
            ...item,
            name: item.is_full_text_field ? `${this.$t('全文检索')}${!!item.repeat_count ? `(${item.repeat_count})` : ''}` : item.name,
            chName: item.name,
          }));
        this.cacheFieldsList = deepClone(this.searchFieldsList); // 赋值缓存的展示字段
      } finally {
        this.loading = false;
        this.isSearchInit = false;
      }
    },
    async handleChangeValue() {
      const cacheValueStr = this.cacheFieldsList.map(item => item.value).join(',');
      const searchValueStr = this.searchFieldsList.map(item => item.value).join(',');
      if (cacheValueStr === searchValueStr) return; // 鼠标失焦后判断每个值是否和缓存的一样 如果一样 则不请求
      this.cacheFieldsList = deepClone(this.searchFieldsList); // 重新赋值缓存的展示字段
      const params = this.searchFieldsList
        .filter(item => Boolean(item.value))
        .map(item => ({
          value: item.value,
          pos: item.pos,
        }));
      this.$http.request('favorite/getGenerateQuery', {
        data: {
          keyword: this.isUpdateFavorite ? this.favoriteKeyword : this.keyword,
          params,
        },
      }).then(async (res) => {
        try {
          const { data } = await this.$http.request('favorite/checkKeywords', {
            data: { keyword: res.data },
          });
          this.$emit('updateKeyWords', res.data);
          this.$emit('isCanSearch', data.is_legal);
        } catch (error) {
          this.$emit('isCanSearch', false);
        }
      })
        .catch(() => {
          this.$emit('isCanSearch', false);
        })
        .finally(() => {
          this.isUpdateFavorite = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.ui-query-container {
  margin-top: 16px;
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
