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
  <div class="biz-menu-select">
    <template v-if="isExpand">
      <div :class="['menu-select', { 'light-theme': theme === 'light' }]">
        <span tabindex="{0}" class="menu-select-name" @mousedown="handleClickBizSelect">
          {{ bizName }}
          <i
            class="bk-select-angle bk-icon icon-angle-down select-icon"
            :style="{ transform: `rotate(${!showBizList ? '0deg' : '-180deg'})` }"
          />
        </span>
      </div>
      <div class="menu-select-list" :style="{ display: showBizList ? 'flex' : 'none' }">
        <bk-input
          ref="menuSearchInput"
          class="menu-select-search"
          right-icon="bk-icon icon-search"
          :placeholder="$t('搜索')"
          :clearable="false"
          :value="keyword"
          @clear="handleBizSearch"
          @change="handleBizSearch"
          @blur="() => (showBizList = false)">
        </bk-input>
        <ul class="biz-list">
          <template v-if="bizList.length">
            <li
              v-for="(item) in bizList"
              :key="item.id"
              :class="['list-item', { 'is-select': item.project_id === projectId }]"
              @mousedown="() => projectChange(item.project_id)">
              {{ item.project_name }}
            </li>
          </template>
          <li v-else class="list-empty">{{ $t('无匹配的数据') }}</li>
        </ul>
      </div>
    </template>
    <span v-else class="menu-title">{{ bizNameIcon }}</span>

  </div>
</template>

<script>
import { mapState } from 'vuex';
// import { menuArr } from './nav/complete-menu';
import navMenuMixin from '@/mixins/navMenuMixin';

export default {
  mixins: [navMenuMixin],
  props: {
    isExpand: {
      type: Boolean,
      default: true,
    },
    theme: {
      type: String,
      default: 'dark',
    },
  },
  data() {
    return {
      bizId: '',
      keyword: '',
      demoProjectUrl: '', // demo 业务链接
      showBizList: false,
      isSelectLoading: false,
    };
  },
  computed: {
    ...mapState({
    }),
    bizName() {
      return this.myProjectList.find(item => item.project_id === this.projectId)?.project_name;
    },
    // 业务列表
    bizList() {
      return this.myProjectList.filter(item => item.project_name.includes(this.keyword));
    },
    bizNameIcon() {
      return this.bizName.split(']')[1][1].toLocaleUpperCase();
    },
  },
  methods: {
    // 选择的业务是否有权限
    checkProjectAuth(project) {
      // eslint-disable-next-line camelcase
      if (project?.permission?.view_business) {
        return true;
      }
      this.$store.commit('updateProject', project.project_id);
      this.$store.dispatch('getApplyData', {
        action_ids: ['view_business'],
        resources: [{
          type: 'biz',
          id: project.bk_biz_id,
        }],
      }).then((res) => {
        this.$emit('auth', res.data);
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.$store.commit('setPageLoading', false);
        });
    },
    // // 业务列表点击申请业务权限
    // async applyProjectAccess(item) {
    //   this.$el.click(); // 手动关闭下拉
    //   try {
    //     this.$bkLoading();
    //     const res = await this.$store.dispatch('getApplyData', {
    //       action_ids: ['view_business'],
    //       resources: [{
    //         type: 'biz',
    //         id: item.bk_biz_id,
    //       }],
    //     });
    //     window.open(res.data.apply_url);
    //   } catch (err) {
    //     console.warn(err);
    //   } finally {
    //     this.$bkLoading.hide();
    //   }
    // },
    // async applyBusinessAccess() {
    //   try {
    //     this.isSelectLoading = true;
    //     const res = await this.$store.dispatch('getApplyData', {
    //       action_ids: ['view_business'],
    //       resources: [],
    //     });
    //     window.open(res.data.apply_url);
    //   } catch (e) {
    //     console.warn(e);
    //   } finally {
    //     this.isSelectLoading = false;
    //   }
    // },
    handleClickBizSelect() {
      this.showBizList = !this.showBizList;
      setTimeout(() => {
        this.$refs.menuSearchInput.focus();
      }, 100);
    },
    handleBizSearch(v) {
      this.keyword = v;
    },
  },
};
</script>

<style lang="scss">
  @import '../scss/mixins/flex.scss';
  @import '../scss/mixins/ellipsis.scss';

  .biz-menu-select {
    padding: 0 16px;
    .menu-select {
      flex: 1;
      display: flex;
      position: relative;
      height: 32px;
      border: 1px solid #2c354d;
      border-radius: 2px;
      background-color: rgba(255,255,255,.05);
      &-name {
        padding: 0 36px 0 10px;
        flex: 1;
        min-width: 227px;
        position: relative;
        color: #acb2c6;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 30px;
        // @include flex-align(center);
        .select-icon {
          position: absolute;
          top: 4px;
          right: 10px;
          font-size: 18px;
          transition: transform .3s cubic-bezier(.4,0,.2,1),-webkit-transform .3s cubic-bezier(.4,0,.2,1);
        }
      }
      &-list {
        display: flex;
        position: fixed;
        left: 16px;
        top: 102px;
        flex-direction: column;
        z-index: 99;
        background-color: #363f56;
        overflow: auto;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,.20);
        .biz-list {
          display: flex;
          flex-direction: column;
          max-height: 240px;
          overflow: auto;
          min-width: 270px;
          padding: 6px 0;
          .list-empty,
          %list-empty {
            height: 32px;
            flex: 0 0 32px;
            padding: 0 16px;
            color: #acb5c6;
            font-size: 12px;
            @include flex-center;
          }
          .list-item {
            justify-content: flex-start;
            @extend %list-empty;
            @include ellipsis;
            @include flex-align(left);
            &.is-select,
            &%is-select {
              color: #fff;
              background-color: #2c354d;
            }
            &:hover {
              cursor: pointer;
              @extend %is-select;
            }
          }
          &::-webkit-scrollbar {
            width: 4px;
            height: 4px;
          }
          &::-webkit-scrollbar-thumb {
            border-radius: 20px;
            background: #363f56;
            box-shadow: inset 0 0 6px rgba(204, 204, 204, .3);
          }
        }
      }
      &-search {
        margin: 0 5px;
        flex: 1;
        width: inherit;
        .bk-form-input {
          border: 0;
          border-bottom: 1px solid rgba(240,241,245,.16);
          border-radius: 0;
          background-color: #363f56;
          color: #acb5c6;
          &:focus {
            background-color: #363f56 !important;
            border-color: rgba(240,241,245,.16) !important;
          }
        }
      }
    }
    .menu-title {
      height: 32px;
      flex: 1;
      border-radius: 4px;
      width: 32px;
      min-width: 32px;
      max-width: 32px;
      background: #a09e21;
      color: #f4f7fa;
      font-weight: bold;
      @include flex-center;
    }
    .menu-title {
      height: 32px;
      flex: 1;
      border-radius: 4px;
      width: 32px;
      min-width: 32px;
      max-width: 32px;
      background: #a09e21;
      color: #f4f7fa;
      font-weight: bold;

      @include flex-center;
    }
    .light-theme {
      background: #f0f1f5;
      border: 0;
      .menu-select-name {
        color: #63656e;
      }
      .select-icon {
        color: #c4c6cc;
      }
    }
  }
</style>
