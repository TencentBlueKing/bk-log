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
  <ul class="agent-status">
    <li v-for="(item, index) in data" :key="index">
      <div v-if="type === 0">
        <span :class="['status-font', `status-${String(item.status).toLocaleLowerCase()}`]">
          {{ item.count }}
        </span>
        <span>{{ item.display || '--' }}</span>
        <span class="separator" v-if="index !== (data.length - 1)">, </span>
      </div>
      <div v-else-if="type === 1">
        <span :class="['status-mark', `status-${String(item.status).toLocaleLowerCase()}`]">
        </span>
        <span>{{ item.display || '--' }}</span>
      </div>
      <div v-else>
        <span v-if="item.isFlag">
          <span :class="['status-count', !!item.errorCount ? 'status-terminated' : 'status-2']">
            {{ item.errorCount || 0 }}
          </span>
          <span>{{ item.count || 0 }}</span>
        </span>
        <span v-else
          class="bk-icon icon-refresh"
          style="display: inline-block; animation: button-icon-loading 1s linear infinite;"
        ></span>
      </div>
    </li>
  </ul>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { IAgentStatusData } from '../types/selector-type'

@Component({ name: 'agent-status' })
export default class AgentStatus extends Vue {
  @Prop({ default: 0, type: Number }) private readonly type!: 0 | 1 | 2
  @Prop({ default: () => [], type: Array }) private readonly data!: IAgentStatusData[]
}
</script>

<style lang="scss" scoped>

  @mixin normal {
    border-color: #3fc06d;
    background: #86e7a9;
    color: #3fc06d;
  }

  @mixin error {
    border-color: #ea3636;
    background: #fd9c9c;
    color: #ea3636;
  }

  @mixin unknown {
    border-color: #c4c6cc;
    background: #f0f1f5;
    color: #c4c6cc;
  }

  .separator {
    padding: 0 2px;
  }

  .agent-status {
    display: flex;
    align-items: center;
  }

  .status-mark {
    margin-right: 8px;
    width: 8px;
    height: 8px;
    border-radius: 4px;
    border: 1px solid;
    display: inline-block;
  }

  .status-font {
    font-weight: 700;

    /* stylelint-disable-next-line declaration-no-important */
    background: unset !important;
  }

  .status-count {
    /* stylelint-disable-next-line declaration-no-important */
    background: unset !important;

    &::after {
      content: '/';
      color: #63656e;
    }
  }

  .status-running,
  .status-1 {
    @include normal;
  }

  .status-terminated,
  .status-3 {
    @include error;
  }

  .status-unknown,
  .status-2 {
    @include unknown;
  }
</style>
