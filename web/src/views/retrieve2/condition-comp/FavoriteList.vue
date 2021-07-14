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
  <div class="retrieve-favorite-container" v-bkloading="{ isLoading }">
    <ul v-if="computedFavoriteList.length" class="favorite-list">
      <template v-for="item in computedFavoriteList">
        <li class="favorite-item" :key="item.id">
          <div class="title">
            <div class="left-title title-container" @click="expandItem(item)">
              <span :class="['bk-icon icon-angle-right', item.expanded && 'expanded']"></span>
              <span v-bk-overflow-tips class="text">{{ item.title }}</span>
            </div>
            <div class="right-title title-container">
              <div class="icon-container" @click="$emit('shouldRetrieve', item)">
                <span class="bk-icon icon-play"></span>
              </div>
              <div class="icon-container" @click="$emit('remove', item.id)">
                <span class="bk-icon icon-delete"></span>
              </div>
            </div>
          </div>
          <div :class="item.expanded && 'expanded'" class="detail">
            <div class="text">{{ item.detail }}</div>
          </div>
        </li>
      </template>
    </ul>
    <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
  </div>
</template>

<script>
export default {
  props: {
    isLoading: {
      type: Boolean,
      required: true,
    },
    favoriteList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
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
        }));
      },
      immediate: true,
    },
  },
  methods: {
    expandItem(item) {
      item.expanded = !item.expanded;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller.scss';

  .retrieve-favorite-container {
    height: 100%;

    .favorite-list {
      height: 100%;
      overflow-y: auto;

      @include scroller;

      .favorite-item {
        padding: 8px 14px;
        border-bottom: 1px solid #f0f1f5;
        font-size: 12px;

        .title {
          display: flex;
          align-items: center;
          justify-content: space-between;
          color: #63656e;

          .title-container {
            display: flex;
            align-items: center;

            &.left-title {
              width: calc(100% - 58px);
              cursor: pointer;

              .bk-icon {
                flex-shrink: 0;
                margin-right: 6px;
                font-size: 24px;
                transition: transform .3s;

                &.expanded {
                  transform: rotate(90deg);
                  transition: transform .3s;
                }
              }

              .text {
                line-height: 24px;
                color: #313238;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              &:hover {
                color: #3a84ff;

                .text {
                  color: #3a84ff;
                }
              }
            }

            &.right-title {
              flex-shrink: 0;
              margin-left: 10px;
              font-size: 14px;

              .icon-container {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 24px;
                height: 24px;
                border-radius: 12px;
                cursor: pointer;

                &:hover {
                  color: #3a84ff;
                  background: #e1ecff;
                }
              }
            }
          }
        }

        .detail {
          max-height: 0;
          overflow: hidden;
          transition: max-height .3s;

          .text {
            max-height: 100px;
            line-height: 20px;
            margin: 8px 30px 12px;
            color: #63656e;
            overflow: hidden;
            display: box;
            -webkit-line-clamp: 5;
            box-orient: vertical;
          }

          &.expanded {
            max-height: 120px;
            transition: max-height .3s;
          }
        }
      }
    }

    .exception-part {
      margin-top: 100px;
    }
  }
</style>
