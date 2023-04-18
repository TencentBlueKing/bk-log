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
    :class="['biz-menu-select', { 'light-theme': theme === 'light' }]"
    v-bk-clickoutside="handleClickOutSide"
  >
    <div :class="['menu-select']">
      <span class="menu-title" :style="`backgroundColor: ${spaceBgColor}`">{{ bizNameIcon }}</span>
      <span
        v-if="isExpand"
        tabindex="{0}"
        class="menu-select-name"
        @mousedown="handleClickBizSelect"
      >
        {{ bizName }}
        <i
          class="bk-select-angle bk-icon icon-angle-up-fill select-icon"
          :style="{ transform: `rotate(${!showBizList ? '0deg' : '-180deg'})` }"
        />
      </span>
    </div>
    <div
      v-if="isExpand"
      class="menu-select-list"
      :style="{ display: showBizList ? 'flex' : 'none' }"
    >
      <bk-input
        ref="menuSearchInput"
        class="menu-select-search"
        left-icon="bk-icon icon-search"
        :placeholder="$t('搜索')"
        :clearable="false"
        :value="keyword"
        @clear="handleBizSearch"
        @change="handleBizSearch"
      >
      </bk-input>
      <ul
        id="space-type-ul"
        class="space-type-list"
        v-if="spaceTypeIdList.length > 1">
        <li
          v-for="(item) in spaceTypeIdList"
          class="space-type-item"
          :key="item.id"
          :style="{
            ...item.styles,
            borderColor: item.id === searchTypeId ? item.styles.color : 'transparent'
          }"
          @click="handleSearchType(item.id)"
        >
          {{item.name}}
        </li>
      </ul>
      <div class="biz-list" :style="`width: ${bizBoxWidth}px`">
        <template v-if="allKeyWorldLength">
          <slot name="list-top"></slot>
          <template v-for="([gKey, gItem], gIndex) in Object.entries(groupList)">
            <div v-show="isShowGroup(gItem)" :key="gIndex">
              <span class="group-title">{{groupNameList[gKey]}}</span>
              <menu-list
                :key="gIndex"
                :theme="theme"
                :space-list="gItem.keywordList"
                @click-menu-item="(item) => handleClickMenuItem(item, gKey)"
              />
            </div>
          </template>
        </template>
        <li v-else class="list-empty">{{ $t('无匹配的数据') }}</li>
      </div>
      <div class="menu-select-extension">
        <!-- <div class="menu-select-extension-item">
          <span class="icon bk-icon icon-plus-circle"></span>
          {{ $t('申请业务权限') }}
        </div> -->
        <div
          class="menu-select-extension-item"
          v-if="demoUid"
          @mousedown.stop="experienceDemo"
        >
          <span class="icon log-icon icon-app-store"></span>
          {{ $t('体验DEMO') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import navMenuMixin from '@/mixins/nav-menu-mixin';
import menuList from './list';
import { deepClone } from '../monitor-echarts/utils';
import { Storage } from '@/common/util';
import * as authorityMap from '../../common/authority-map';
import { SPACE_TYPE_MAP } from '@/store/constant';

const SPACE_COLOR_LIST = ['#7250A9', '#3563BE', '#3799BA', '#4FB17F', '#86AF4A', '#E9AE1D', '#EB9258', '#D36C68', '#BC4FB3'];

export default {
  components: {
    menuList,
  },
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
    handlePropsClick: Function,
  },
  data() {
    return {
      bizId: '',
      keyword: '',
      showBizList: false,
      storage: null,
      commonMeta: null,
      userCommon: null,
      notTopAuthGroupList: [], // 非置顶非无权限的其余分组的值
      groupList: {
        top: {
          list: [],
          keywordList: [],
        },
        common: {
          list: [],
          keywordList: [],
        },
        haveAuth: {
          list: [],
          keywordList: [],
        },
        remain: {
          list: [],
          keywordList: [],
        },
      },
      groupNameList: {
        top: this.$t('置顶的'),
        common: this.$t('常用的'),
        haveAuth: this.$t('有权限的'),
        remain: this.$t('剩余的'),
      },
      BIZ_SELECTOR_COMMON_IDS: 'BIZ_SELECTOR_COMMON_IDS', // 常用的 的key
      BIZ_SELECTOR_COMMON_MAX: 5, // 常用的的最大长度
      spaceTypeIdList: [],
      searchTypeId: '',
      spaceBgColor: '#3799BA',
      bizBoxWidth: 418,
    };
  },
  computed: {
    ...mapGetters({
      demoUid: 'demoUid',
    }),
    bizName() {
      return this.mySpaceList.find(item => item.space_uid === this.spaceUid)?.space_name;
    },
    bizNameIcon() {
      return this.bizName[0].toLocaleUpperCase();
    },
    allKeyWorldLength() {
      return Object.values(this.groupList).reduce((pre, cur) => ((pre += cur.keywordList.length), pre), 0);
    },
  },
  watch: {
    keyword() {
      this.initGroupList();
    },
    async showBizList(val) {
      if (val) {
        await this.$nextTick();
        const el = document.querySelector('#space-type-ul');
        this.bizBoxWidth = Math.max(394, el.clientWidth ?? 394) + 24;
      }
    },
  },
  created() {
    // this.spaceBgColor = this.$store.getters.spaceBgColor || this.getRandomColor();
    this.initGroupList();
    const spaceTypeMap = {};
    this.mySpaceList.forEach((item) => {
      spaceTypeMap[item.space_type_id] = 1;
      if (item.space_type_id === 'bkci' && item.space_code) {
        spaceTypeMap.bcs = 1;
      }
    });
    this.spaceTypeIdList = Object.keys(spaceTypeMap).map(key => ({
      id: key,
      name: SPACE_TYPE_MAP[key]?.name || this.$t('未知'),
      styles: (this.theme === 'dark' ? SPACE_TYPE_MAP[key]?.dark : SPACE_TYPE_MAP[key]?.light) || {},
    }));
  },
  methods: {
    getRandomColor() {
      const color =  SPACE_COLOR_LIST[Math.floor(Math.random() * SPACE_COLOR_LIST.length)];
      this.$store.commit('setSpaceBgColor', color);
      return color;
    },
    initGroupList() {
      this.storage = new Storage();
      this.commonListIds = this.storage.get(this.BIZ_SELECTOR_COMMON_IDS) || [];
      // 分组 置顶的 置顶以外的
      const [correctList, failureList] = this.filterGroupList(
        this.mySpaceList, item => item.is_sticky,
      );
      this.groupDistributeList(correctList, 'top'); // 置顶赋值
      // 从置顶以外的挑出有权限的并赋值给notTopAuthGroupList
      const [perCorrectList, perFailureList] = this.filterGroupList(
        failureList, item => item.permission[authorityMap.VIEW_BUSINESS],
      );
      this.groupDistributeList(perFailureList, 'remain');
      this.notTopAuthGroupList = perCorrectList;
      this.commonAssignment();
    },
    isShowGroup(group) {
      return !!group.keywordList.length;
    },
    handleClickBizSelect() {
      this.showBizList = !this.showBizList;
      setTimeout(() => {
        this.$refs.menuSearchInput.focus();
      }, 100);
    },
    /**
     * @desc: 分配分类列表里的数组
     * @param {Array} distributeList 分配的数组
     * @param {String} type 分配哪个数组
     */
    groupDistributeList(distributeList = [], type = 'remain') {
      const typeList = ['top', 'common', 'haveAuth', 'remain'];
      if (!typeList.includes(type) || !Array.isArray(distributeList)) return;
      for (const itemKey in this.groupList[type]) {
        this.groupList[type][itemKey] = deepClone(distributeList);
      }
    },
    /**
     * @desc: 点击下拉框的空间选项
     * @param {Object} space 点击的空间
     * @param {String} type 点的是哪个分组的空间
     */
    handleClickMenuItem(space, type) {
      try {
        if (typeof this.handlePropsClick === 'function') return this.handlePropsClick(space); // 外部function调用
        if (type === 'haveAuth') this.commonAssignment(space.space_uid); // 点击有权限的业务时更新常用的ul列表
        this.checkSpaceChange(space.space_uid); // 检查是否有权限然后进行空间切换
      } catch (error) {
        console.warn(error);
      } finally {
        this.showBizList = false;
      }
    },
    /**
     * @desc: 常用的分配
     * @param {Number} id 点击的space_uid
     * @param {Array} filterList 基于哪个数组进行过滤
     */
    commonAssignment(id = null, filterList = this.notTopAuthGroupList) {
      const leng = this.commonListIds.length;
      if (!!id) {
        const isExist = this.commonListIds.includes(id);
        let newIds = [...this.commonListIds];
        if (isExist) newIds = newIds.filter(item => item !== id);
        newIds.unshift(id);
        this.commonListIds = newIds;
      }
      leng >= this.BIZ_SELECTOR_COMMON_MAX && (this.commonListIds.length = this.BIZ_SELECTOR_COMMON_MAX);
      const [correctList, failureList] = this.filterGroupList(
        filterList, item => this.commonListIds.includes(item.space_uid),
      );
      this.storage.set(this.BIZ_SELECTOR_COMMON_IDS, this.commonListIds);
      this.groupDistributeList(correctList, 'common');
      this.groupDistributeList(failureList, 'haveAuth');
    },
    /**
     * @desc: 过滤分组用的函数
     * @param {Array} groupList
     * @param {Function} callback
     * @returns {Array} 返回callback判断的布尔数组
     */
    filterGroupList(groupList, callback) {
      const correctList = [];
      const failureList = [];
      groupList.forEach((item) => {
        let show = false;
        const keyword = this.keyword.trim().toLocaleLowerCase();
        if (this.searchTypeId) {
          show = this.searchTypeId === 'bcs' ? item.space_type_id === 'bkci' && !!item.space_code : item.space_type_id === this.searchTypeId;
        }

        if ((show && keyword) || (!this.searchTypeId && !show)) {
          show = (item.space_name.toLocaleLowerCase().indexOf(keyword) > -1
        || item.py_text.toLocaleLowerCase().indexOf(keyword) > -1
        // || `${item.id}`.includes(keyword));
        || `${item.space_code}`.includes(keyword));
        }
        if (show) {
          const tags = [{ id: item.space_type_id, name: item.space_type_name, type: item.space_type_id }];
          if (item.space_type_id === 'bkci' && item.space_code) {
            tags.push({ id: 'bcs', name: this.$tc('容器项目'), type: 'bcs' });
          }
          const newItem = {
            ...item,
            name: item.space_name.replace(/\[.*?\]/, ''),
            tags,
          };
          callback(item) ? correctList.push(newItem) : failureList.push(newItem);
        }
      });
      return [correctList, failureList];
    },
    handleClickOutSide() {
      this.showBizList = false;
    },
    handleBizSearch(v) {
      this.keyword = v;
    },
    experienceDemo() {
      this.checkSpaceChange(this.demoUid);
    },
    handleSearchType(typeId) {
      this.searchTypeId = typeId === this.searchTypeId ? '' : typeId;
      this.initGroupList();
    },
  },
};
</script>

<style lang="scss">
  @import '../../scss/mixins/flex.scss';
  @import '../../scss/mixins/ellipsis.scss';

  .biz-menu-select {
    padding-left: 8px;

    .menu-select {
      padding: 0 4px 0 8px;
      flex: 1;
      display: flex;
      align-items: center;
      position: relative;
      height: 32px;
      border-radius: 2px;
      background-color: #2b354d;

      &-name {
        padding: 0 26px 0 8px;
        flex: 1;
        position: relative;
        color: #acb2c6;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 30px;
        cursor: pointer;

        .select-icon {
          position: absolute;
          top: 8px;
          right: 8px;
          color: #c4c6cc;
          transition: transform .3s cubic-bezier(.4,0,.2,1),-webkit-transform .3s cubic-bezier(.4,0,.2,1);
        }

        .icon-angle-up-fill {
          top: 8px;
          color: #96a2b9;
        }
      }

      &-list {
        display: flex;
        position: fixed;
        left: 0;
        top: 100px;
        flex-direction: column;
        z-index: 99;
        background-color: #38455f;
        overflow: auto;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,.20);
        z-index: 2000;

        .biz-list {
          display: flex;
          flex-direction: column;
          max-height: 240px;
          overflow: auto;
          padding: 6px 0;

          .group-title {
            font-size: 12px;
            color: #66768e;
            margin: 0 0 7px 12px;
            display: inline-block;
          }

          .list-empty,
          %list-empty {
            height: 32px;
            flex: 0 0 32px;
            padding: 0 9px 0 12px;
            color: #c3d0e7;
            font-size: 12px;

            @include flex-center;
          }

          .list-item {
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
              background-color: #323c53;

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

            .list-item-left {
              /* stylelint-disable-next-line declaration-no-important */
              display: inline-flex !important;
              flex: 1;
              flex-wrap: nowrap;
              margin-right: 8px;

              @include ellipsis();

              .list-item-name {
                @include ellipsis();
              }

              .list-item-id {
                margin-left: 8px;

                @include ellipsis();
              }
            }
          }

          &::-webkit-scrollbar {
            width: 4px;
            background: #38455f;
          }

          &::-webkit-scrollbar-thumb {
            border-radius: 20px;
            background: #ddd;
            box-shadow: inset 0 0 6px rgba(204, 204, 204, .3);
          }
        }
      }

      &-search {
        padding: 0 5px;
        flex: 1;
        width: inherit;

        .left-icon {
          color: #63656e;
          left: 0;
        }

        .bk-form-input {
          border: 0;
          border-bottom: 1px solid rgba(240,241,245,.16);
          border-radius: 0;
          background-color: #38455f;
          color: #acb5c6;;

          &::placeholder {
            /* stylelint-disable-next-line declaration-no-important */
            color: #66768e!important;
            background-color: #39455f;
          }

          &:focus {
            /* stylelint-disable-next-line declaration-no-important */
            background-color: #39455f !important;

            /* stylelint-disable-next-line declaration-no-important */
            border-bottom-color: #434e68 !important;
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
      border-radius: 2px;
      width: 20px;
      min-width: 20px;
      max-width: 20px;
      background: #a09e21;;
      color: #fff;
      font-weight: 700;
      font-size: 12px;

      @include flex-center;
    }
  }

  .light-theme {
    padding: 0;

    .menu-select {
      background: transparent;
      border: 0;

      .menu-select-name {
        color: #313238;
        font-size: 14px;
      }

      .select-icon {
        /* stylelint-disable-next-line declaration-no-important */
        right: 2px !important;
      }

      &-list {
        top: 106px;
        left: 16px;
        min-width: 418px;
        background-color: #fff;
        outline: 1px solid #dcdee5;

        .biz-list {
          min-width: 418px;
          padding: 6px 0;

          .group-title {
            font-size: 12px;
            color: #c4c6cc;
            margin: 0 0 7px 12px;
            display: inline-block;
          }

          .list-empty,
          %list-empty {
            color: #63656e;
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
          border-bottom: 1px solid #eaebf0;
          background-color: #fff;
          color: #63656e;

          &::placeholder {
            background-color: #fff;
          }

          &:focus {
            /* stylelint-disable-next-line declaration-no-important */
            background-color: #fff !important;

            /* stylelint-disable-next-line declaration-no-important */
            border-color: #eaebf0 !important;
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
            border-color: #dcdee5;
          }
        }
      }
    }

    .select-icon {
      color: #c4c6cc;
    }

    .space-type-list {
      border-color: #eaebf0;
    }
  }

  .space-type-list {
    display: flex;
    align-items: center;
    padding: 8px 0;
    margin: 0 12px;
    border-bottom: 1px solid #434e68;

    .space-type-item {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 10px;
      border-radius: 2px;
      margin-right: 4px;
      height: 22px;
      font-size: 12px;
      cursor: pointer;
      border: 1px solid transparent;
    }
  }
</style>
