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
  <ul>
    <li
      v-for="item in spaceList"
      :key="item.id"
      :class="[
        'list-item',
        {
          'is-select': item.space_uid === spaceUid,
          'is-disable': !(item.permission && item.permission.view_business),
        },
      ]"
      @mousedown="handleProjectChange(item)"
    >
      <span class="text" :title="item.space_name">
        {{item.space_name}}
        <span :class="`${theme}-item-code`">(#{{item.space_code}})</span>
      </span>
      <span class="list-item-right">
        <span :class="['list-item-tag', `${theme}-theme`, eTagsType[item.space_type_id] || 'other-type']">
          {{item.space_type_name}}
        </span>
      </span>
      <span
        v-if="!(item.permission && item.permission.view_business)"
        class="apply-text"
        @mousedown.stop="applyProjectAccess(item)">
        {{ $t("申请权限") }}
      </span>
    </li>
  </ul>
</template>

<script>
import navMenuMixin from '@/mixins/nav-menu-mixin';

export default {
  mixins: [navMenuMixin],
  props: {
    spaceList: {
      type: Array,
      require: true,
    },
    theme: {
      type: String,
      default: 'dark',
    },
  },
  data() {
    return {
      eTagsType: {
        bkcc: 'bkcc', /** 蓝鲸配置平台 */
        bcs: 'bcs', /** 蓝鲸容器平台 */
        bkdevops: 'bkdevops', /** 蓝盾 */
        bksaas: 'bksaas', /** 蓝鲸应用 */
      },
    };
  },
  computed: {},
  watch: {},
  mounted() {},
  methods: {
    handleProjectChange(space) {
      if (!(space.permission && space.permission.view_business)) return;
      this.$emit('click-menu-item', space);
    },
    // 业务列表点击申请业务权限
    async applyProjectAccess(item) {
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['view_business'],
          resources: [{
            type: 'space',
            id: item.space_uid,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$bkLoading.hide();
      }
    },
  },
};
</script>

<style scoped lang="scss">
  .list-item-right {
    flex-shrink: 0;

    .list-item-tag {
      display: inline-block;
      height: 23px;
      line-height: 23px;
      padding: 0 10px;
      border-radius: 2px;

      &:not(:last-child) {
        margin-right: 8px;
      }
    }

    .light-theme {
      &.bkcc {
        color: #f85959;
        background-color: #feebea;
      }

      &.bkdevops {
        color: #3fc362;
        background-color: #e4faf0;
      }

      &.bcs {
        color: #fc943b;
        background-color: #fff1db;
      }

      &.bksaas {
        color: #478efc;
        background-color: #edf4ff;
      }

      &.other-type {
        color: #b3b3b3;
        background-color: #f0f1f5;
      }
    }

    .dark-theme {
      &.bkcc {
        color: #f85959;
        background-color: #3c151d;
      }

      &.bkdevops {
        color: #3fc362;
        background-color: #183a28;
      }

      &.bcs {
        color: #fc943b;
        background-color: #3a2f18;
      }

      &.bksaas {
        color: #478efc;
        background-color: #1d2c4e;
      }

      &.other-type {
        color: #b3b3b3;
        background-color: #3d3d3d;
      }
    }
  }

  .light-item-code {
    color: #c4c6cc;
  }

  .dark-item-code {
    color: #66768e;
  }
</style>
