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
  <div :class="['biz-menu-select', { 'light-theme': theme === 'light' }]">
    <div :class="['menu-select']">
      <span class="menu-title">{{ bizNameIcon }}</span>
      <span
        v-if="isExpand" tabindex="{0}" class="menu-select-name" @mousedown="handleClickBizSelect">
        {{ bizName }}
        <i
          :class="`bk-select-angle bk-icon ${theme === 'light' ? 'icon-angle-down' : 'icon-down-shape'} select-icon`"
          :style="{ transform: `rotate(${!showBizList ? '0deg' : '-180deg'})` }"
        />
      </span>
    </div>
    <div v-if="isExpand" class="menu-select-list" :style="{ display: showBizList ? 'flex' : 'none' }">
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
            :class="[
              'list-item',
              {
                'is-select': item.project_id === projectId,
                'is-disable': !(item.permission && item.permission.view_business)
              }
            ]"
            @mousedown="handleProjectChange(item)">
            <span class="text" :title="item.project_name">{{ item.project_name }}</span>
            <span
              v-if="!(item.permission && item.permission.view_business)"
              class="apply-text"
              @mousedown.stop="applyProjectAccess(item)">
              {{ $t('申请权限') }}
            </span>
          </li>
        </template>
        <li v-else class="list-empty">{{ $t('无匹配的数据') }}</li>
      </ul>
      <div class="menu-select-extension">
        <div class="menu-select-extension-item" @mousedown.stop="applyBusinessAccess">
          <span class="icon bk-icon icon-plus-circle"></span>
          {{ $t('申请业务权限') }}
        </div>
        <div class="menu-select-extension-item" v-if="demoProjectUrl" @mousedown.stop="experienceDemo">
          <span class="icon log-icon icon-app-store"></span>
          {{ $t('体验DEMO') }}
        </div>
      </div>
    </div>
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
    handleProjectChange(project) {
      if (!(project.permission && project.permission.view_business)) return;

      this.checkProjectChange(project.project_id);
    },
    // 业务列表点击申请业务权限
    async applyProjectAccess(item) {
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['view_business'],
          resources: [{
            type: 'biz',
            id: item.bk_biz_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$bkLoading.hide();
      }
    },
    async applyBusinessAccess() {
      if (this.isSelectLoading) return;

      try {
        this.isSelectLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['view_business'],
          resources: [],
        });
        window.open(res.data.apply_url);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isSelectLoading = false;
      }
    },
    handleClickBizSelect() {
      this.showBizList = !this.showBizList;
      setTimeout(() => {
        this.$refs.menuSearchInput.focus();
      }, 100);
    },
    handleBizSearch(v) {
      this.keyword = v;
    },
    experienceDemo() {
      window.open(this.demoProjectUrl);
    },
  },
};
</script>

<style lang="scss">
@import '../scss/mixins/flex.scss';
@import '../scss/mixins/ellipsis.scss';

.biz-menu-select {
  .menu-select {
    padding: 0 4px 0 16px;
    flex: 1;
    display: flex;
    align-items: center;
    position: relative;
    height: 40px;
    border: 1px solid #2c354d;
    border-radius: 2px;
    background: rgba(44,53,77,0.00);;
    &-name {
      padding: 0 26px 0 10px;
      flex: 1;
      position: relative;
      color: #eaebf0;
      font-size: 14px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      line-height: 30px;
      cursor: pointer;
      .select-icon {
        position: absolute;
        top: 8px;
        right: 10px;
        color: #96a2b9;
        transition: transform .3s cubic-bezier(.4,0,.2,1),-webkit-transform .3s cubic-bezier(.4,0,.2,1);
      }
      .icon-angle-down {
        top: 5px;
        font-size: 20px;
      }
    }
    &-list {
      display: flex;
      position: fixed;
      left: 0;
      top: 112px;
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
        min-width: 280px;
        padding: 6px 0;
        .list-empty,
        %list-empty {
          height: 32px;
          flex: 0 0 32px;
          padding: 0 16px;
          color: #c3d0e7;
          font-size: 12px;
          @include flex-center;
        }
        .list-item {
          max-width: 364px;
          justify-content: space-between;
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
          &.is-disable {
            color: #66768e;
            cursor: not-allowed;
          }
          .text {
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .apply-text {
            display: none;
            color: #3a84ff;
            cursor: pointer;
          }
          &:hover .apply-text {
            display: flex;
          }
        }
        &::-webkit-scrollbar {
          width: 4px;
          background: #363f56;
        }
        &::-webkit-scrollbar-thumb {
          border-radius: 20px;
          background: #363f56;
          box-shadow: inset 0 0 6px rgba(204, 204, 204, .3);
        }
      }
    }
    &-search {
      padding: 0 5px;
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
    &-extension {
      display: flex;
      padding: 10px 0;
      border-top: 1px solid #434e68;
      font-size: 12px;
      color: #c3d0e7;
      background-color: #323c53;
      cursor: pointer;
      &-item {
        width: 50%;
        text-align: center;
        flex-grow: 1;
        &:hover {
          color: #fff;
        }
        &:first-child {
          border-right: 1px solid #434e68;
        }
        &:last-child {
          border: 0;
        }
        .icon {
          font-size: 14px;
        }
      }
    }
  }
  .menu-title {
    height: 20px;
    flex: 1;
    border-radius: 4px;
    width: 20px;
    min-width: 20px;
    max-width: 20px;
    background: #FFD695;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    @include flex-center;
  }
}
.light-theme {
  .menu-select {
    background: #f0f1f5;
    border: 0;
    &-list {
      left: 16px;
      width: 418px;
      background-color: #FFF;
      outline: 1px solid #dcdee5;
      .biz-list {
        min-width: 418px;
        padding: 6px 0;
        .list-empty,
        %list-empty {
          color: #63656E;
        }
        .list-item {
          max-width: 100%;
          @extend %list-empty;
          &.is-select,
          &%is-select {
            color: #3a84ff;
            background-color: #f5f7fa;
          }
          &:hover {
            @extend %is-select;
          }
          &.is-disable {
            color: #c4c6cc;
          }
        }
        &::-webkit-scrollbar {
          background: #fff;
        }
        &::-webkit-scrollbar-thumb {
          background: #dcdee5;
        }
      }
    }
    &-name {
      color: #63656e;
      font-size: 12px;
    }
    &-search {
      .bk-form-input {
        border-bottom: 1px solid #EAEBF0;
        background-color: #FFF;
        color: #63656E;
        &:focus {
          background-color: #FFF !important;
          border-color: #EAEBF0 !important;
        }
      }
    }
    &-extension {
      border-top: 1px solid #dcdee5;
      color: #63656e;
      background-color: #fafbfd;
      &-item {
        &:hover {
          color: #3a84ff;
        }
        &:first-child {
          border-color:#dcdee5;
        }
      }
    }
  }
  .select-icon {
    color: #c4c6cc;
  }
}
</style>
