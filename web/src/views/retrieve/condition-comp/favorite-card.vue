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
      <ul v-if="computedFavoriteList.length" class="favorite-list" ref="favList">
        <template v-for="item in computedFavoriteList">
          <li
            :class="{
              'favorite-item': true,
              'is-latest': item.isLatest
            }"
            :key="item.id"
            :title="item.detail">
            <div class="title" @click.stop="handleSearch(item)">{{ item.title }}</div>
            <span class="bk-icon icon-close-line-2" @click.stop="$emit('remove', item.id)"></span>
          </li>
        </template>
      </ul>
      <span class="arrow-down-wrap">
        <i class="bk-icon expand-icon icon-angle-down" :class="isExpand ? 'is-flip' : ''"></i>
      </span>
    </template>
  </div>
</template>

<script>
import { debounce } from 'throttle-debounce';

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
      handleOverflowDebounce: null,
      resizeObserver: null,
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
        this.$nextTick(() => {
          this.handleOverflow();
        });
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
  created() {
    this.handleOverflowDebounce = debounce(300, false, this.handleOverflow);
  },
  mounted() {
    this.handleOverflowDebounce();
    this.resizeObsever();
  },
  beforeDestroy() {
    this.resizeObserver?.unobserve(this.$refs.favList);
  },
  methods: {
    /**
     * @desc 控制超出省略提示
     */
    async handleOverflow() {
      this.removeOverflow();
      const list = this.$refs.favList;
      if (!list) return;
      const childs = list.children;
      const overflowTagWidth = 22;
      const listWidth = list.offsetWidth;
      let totalWidth = 0;
      await this.$nextTick();
      // eslint-disable-next-line no-restricted-syntax
      for (const i in childs) {
        const item = childs[i];
        if (!item.className || item.className.indexOf('favorite-item') === -1) continue;
        totalWidth += item.offsetWidth + 10;
        // 超出省略
        if (totalWidth + overflowTagWidth + 4 > listWidth) {
          const hideNum = this.computedFavoriteList.length - +i;
          this.insertOverflow(item, hideNum > 99 ? 99 : hideNum);
          break;
        }
      }
    },
    /**
     * @desc 移除超出提示
     */
    removeOverflow() {
      const overflowList = this.$refs.favList?.querySelectorAll('.fav-overflow-item');
      if (!overflowList?.length) return;
      overflowList.forEach((item) => {
        this.$refs.favList.removeChild(item);
      });
    },
    /**
     * @desc 监听容器宽度
     */
    resizeObsever() {
      if (!this.$refs.favList) return;

      this.resizeObserver = new ResizeObserver(() => {
        this.removeOverflow();
        this.handleOverflow();
      });
      this.resizeObserver.observe(this.$refs.favList);
    },
    /**
     * @desc 插入超出提示
     * @param { * } target
     * @param { Number } num
     */
    insertOverflow(target, num) {
      if (this.isExpand) return;
      const li = document.createElement('li');
      const div = document.createElement('div');
      li.className = 'fav-overflow-item';
      div.className = 'tag';
      div.innerText = `+${num}`;
      li.appendChild(div);
      this.$refs.favList.insertBefore(li, target);
    },
    toggleExpand() {
      this.isExpand = !this.isExpand;
    },
    handleClickoutside() {
      this.isExpand = false;
    },
    handleSearch(item) {
      const payload = item;
      // if (!item.params.host_scopes.target_node_type) {
      //   payload.params.host_scopes.target_node_type = '';
      //   payload.params.host_scopes.target_nodes = [];
      // }
      if (Object.keys(!item.params.ip_chooser).length) {
        payload.params.ip_chooser = {};
      }
      this.$emit('shouldRetrieve', payload);
    },
  },
};
</script>

<style lang="scss">
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
      margin: 0 10px;
      display: flex;
      flex-wrap: wrap;
      flex: 1;
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

    .fav-overflow-item {
      width: 22px;
      height: 22px;
      line-height: 18px;
      margin: 0 4px 10px 0;
      border: 1px solid rgba(151, 155, 165, .3);
      border-radius: 3px;
      background-color: #fafbfd;

      .tag {
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 0;
      }
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

    .arrow-down-wrap {
      padding-top: 16px;
    }

    .expand-icon {
      display: inline-block;
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
