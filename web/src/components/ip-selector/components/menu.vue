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
  <ul class="menu">
    <li v-for="(item, index) in list"
        :key="index"
        class="menu-item"
        :style="{ 'text-align': align }"
        :disabled="item.disabled"
        v-show="!item.hidden"
        @click="!item.disabled && handleMenuClick(item)">
      {{ item.label }}
    </li>
  </ul>
</template>

<script lang="ts">
import { Vue, Component, Prop, Emit } from 'vue-property-decorator'
import { IMenu } from '../types/selector-type'

@Component({ name: 'menu-list' })
export default class Menu extends Vue {
  @Prop({ default: () => [], type: Array }) private readonly list!: IMenu[]
  @Prop({ default: 'left', type: String }) private readonly align!: string

  @Emit('click')
  private handleMenuClick(item: IMenu) {
    return item
  }
}
</script>

<style lang="scss" scoped>
  .menu {
    font-size: 12px;
    padding: 6px 0;
    min-width: 84px;
    background: #fff;

    &-item {
      height: 32px;
      line-height: 32px;
      padding: 0 10px;
      cursor: pointer;

      &:hover {
        background: #f5f6fa;
        color: #3a84ff;
      }
    }

    &-item[disabled] {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }
</style>
