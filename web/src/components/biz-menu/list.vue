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
          'is-disable': !(item.permission && item.permission[authorityMap.VIEW_BUSINESS]),
        },
      ]"
      @mousedown="handleProjectChange(item)"
    >
      <span class="list-item-left">
        <span class="list-item-name" v-bk-overflow-tips>{{ item.space_name }}</span>
        <span :class="`list-item-id ${theme}-item-code`" v-bk-overflow-tips>
          <!-- ({{ item.space_type_id === eTagsType.biz ? `#${item.id}` : (item.space_id || item.space_code)}}) -->
          ({{ `#${item.space_id || item.space_code}` }})
        </span>
      </span>
      <span class="list-item-right">
        <span
          v-for="(tag) in item.tags"
          class="list-item-tag"
          :key="tag.id"
          :style="{
            ...spaceTypeMap[tag.id][theme]
          }"
        >
          {{ tag.name }}
        </span>
      </span>
      <span
        v-if="!(item.permission && item.permission[authorityMap.VIEW_BUSINESS])"
        class="apply-text"
        @mousedown.stop="applyProjectAccess(item)">
        {{ $t("申请权限") }}
      </span>
    </li>
  </ul>
</template>

<script>
import navMenuMixin from '@/mixins/nav-menu-mixin';
import * as authorityMap from '../../common/authority-map';
import { SPACE_TYPE_MAP } from '@/store/constant';

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
        biz: 'bkcc', /** 业务 */
        paas: 'paas', /** PaaS应用 */
        container: 'bcs', /** 蓝鲸容器平台 */
        research: 'bkci', /** 研发项目 */
        monitor: 'monitor', /** 监控空间 */
      },
    };
  },
  computed: {
    authorityMap() {
      return authorityMap;
    },
    spaceTypeMap() {
      return SPACE_TYPE_MAP;
    },
  },
  watch: {},
  mounted() {},
  methods: {
    handleProjectChange(space) {
      if (!(space.permission && space.permission[authorityMap.VIEW_BUSINESS])) return;
      this.$emit('click-menu-item', space);
    },
    // 业务列表点击申请业务权限
    async applyProjectAccess(item) {
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.VIEW_BUSINESS],
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
  @import '@/scss/space-tag-option';

  .light-item-code {
    color: #c4c6cc;
  }

  .dark-item-code {
    color: #66768e;
  }
</style>
