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
    :class="{ 'retrieve-favorite-card': true, 'is-expand': isExpand }"
    v-bk-clickoutside="handleClickoutside"
    @click="toggleExpand">
    <template v-if="favoriteList.length">
      <div class="card-title">
        <span>{{ $t('收藏') }}</span>
      </div>
      <ul v-if="computedFavoriteList.length" class="favorite-list">
        <template v-for="item in computedFavoriteList">
          <li :class="{ 'favorite-item': true, 'is-latest': item.isLatest }" :key="item.id" :title="item.detail">
            <div class="title" @click.stop="$emit('shouldRetrieve', item)">{{ item.title }}</div>
            <span class="bk-icon icon-close-line-2" @click.stop="$emit('remove', item.id)"></span>
          </li>
        </template>
      </ul>
      <span class="bk-icon expand-icon icon-angle-down" :class="isExpand ? 'is-flip' : ''"></span>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    favoriteList: {
      type: Array,
      required: true,
    },
    latestFavoriteId: {
      type: [Number, String],
      default: '',
    },
  },
  data() {
    return {
      isExpand: false,
      computedFavoriteList: [],
    };
  },
  watch: {
    favoriteList: {
      handler(val) {
        this.computedFavoriteList = val.map(item => ({
          id: item.favorite_search_id,
          title: item.favorite_description,
          detail: item.query_string,
          params: item.params,
          indexId: String(item.index_set_id),
          expanded: false,
          isLatest: this.latestFavoriteId === item.favorite_search_id,
        }));
      },
      immediate: true,
    },
    latestFavoriteId(val) {
      this.computedFavoriteList = this.computedFavoriteList.map(item => ({
        ...item,
        isLatest: val === item.id,
      }));
    },
  },
  methods: {
    toggleExpand() {
      this.isExpand = !this.isExpand;
    },
    handleClickoutside() {
      this.isExpand = false;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller.scss';

  .retrieve-favorite-card {
    position: relative;
    display: flex;
    padding: 0 14px 0 24px;
    height: 42px;
    flex: 1;
    overflow: hidden;
    cursor: pointer;

    .card-title {
      margin-right: 12px;
      line-height: 50px;
      color: #63656e;
      white-space: nowrap;

      .icon-star-shape {
        color: rgb(254, 156, 0);
      }
    }

    .favorite-list {
      padding: 14px 0;
    }

    .favorite-item {
      position: relative;
      display: flex;
      justify-content: space-between;
      align-items: center;
      float: left;
      margin-right: 10px;
      margin-bottom: 10px;
      padding: 0 4px 0 8px;
      height: 22px;
      background: #fafbfd;
      border: 1px solid #dcdee5;
      border-radius: 3px;
      cursor: pointer;
    }

    .is-latest {
      background: #edf4ff;
      border-color: #3a84ff;
      color: #3a84ff;
    }

    .title {
      margin-right: 16px;
    }

    .icon-close-line-2 {
      display: none;
      position: absolute;
      right: 4px;
      font-size: 12px;
      color: #63656e;
      cursor: pointer;
    }

    .favorite-item:hover {
      background-color: #f0f1f5;

      .icon-close-line-2 {
        display: inline-block;
      }
    }

    .expand-icon {
      position: absolute;
      top: 14px;
      right: 12px;
      color: #63656e;
      font-size: 22px;
      cursor: pointer;
      transition: transform .3s;

      &.is-flip {
        transform: rotate(180deg);
        transition: transform .3s;
      }
    }

    &.is-expand {
      height: fit-content;
      overflow: auto;
      background: #fff;
      border: 1px solid #dcdee5;
      border-radius: 4px;
      box-shadow: 0px 2px 6px 0px rgba(0,0,0,.10);
    }
  }
</style>
