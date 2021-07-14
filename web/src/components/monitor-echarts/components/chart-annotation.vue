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
  <div class="echart-annotation" v-show="annotation.show" :style="{ left: annotation.x + 'px', top: annotation.y + 'px' }">
    <div class="echart-annotation-title">{{ annotation.title}}</div>
    <div class="echart-annotation-name">
      <span class="name-mark" :style="{ backgroundColor: annotation.color }"></span>{{annotation.name}}
    </div>
    <ul class="echart-annotation-list">
      <template v-for="item in annotation.list">
        <li class="list-item" v-if="item.show" :key="item.id" @click="handleGotoDetail(item)">
          <span class="icon-monitor item-icon" :class="`icon-mc-${item.id}`"></span>
          <span> {{toolBarMap[item.id]}}
            <span v-if="item.id === 'ip'" style="color: #c4c6cc">{{`(${item.value.split('-').reverse().join(':')})`}}</span>
          </span>
          <i class="icon-monitor icon-mc-link list-item-link"></i>
        </li>
      </template>
    </ul>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'
import { IAnnotation, IAnnotationListItem } from '../options/type-interface'
@Component({ name: 'ChartAnnotation' })
export default class ChartAnnotation extends Vue {
  @Prop({ required: true })annotation: IAnnotation
  get toolBarMap() {
    return {
      ip: this.$t('相关主机详情'),
      process: this.$t('相关进程信息'),
      strategy: this.$t('相关策略')
    }
  }
  handleGotoDetail(item: IAnnotationListItem) {
    switch (item.id) {
      case 'ip':
        window.open(location.href.replace(location.hash, `#/performance/detail/${item.value}`))
        break
      case 'process':
        window.open(location.href.replace(
          location.hash,
          `#/performance/detail-new/${item.value.id}/${item.value.processId}`
        ))
        break
      case 'strategy':
        window.open(location.href.replace(location.hash, `#/strategy-config?metricId=${item.value}`))
        break
    }
  }
}
</script>
<style lang="scss" scoped>
  .echart-annotation {
    position: absolute;
    min-height: 84px;
    width: 220px;
    background: white;
    border-radius: 2px;
    box-shadow: 0px 4px 12px 0px rgba(0,0,0,.2);
    z-index: 99;
    font-size: 12px;
    color: #63656e;

    &-title {
      margin: 6px 0 0 16px;
      line-height: 20px;
    }

    &-name {
      margin-top: 2px;
      padding-left: 18px;
      height: 20px;
      display: flex;
      align-items: center;
      font-weight: 700;
      border-bottom: 1px solid #f0f1f5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 90%;

      .name-mark {
        flex: 0 0 12px;
        height: 4px;
        margin-right: 10px;
      }
    }

    &-list {
      display: flex;
      flex-direction: column;

      .list-item {
        flex: 0 0 30px;
        display: flex;
        align-items: center;
        padding-left: 16px;

        .item-icon {
          margin-right: 10px;
          font-size: 16px;
          margin-right: 10px;
          height: 16px;
          width: 16px;
        }

        &-link {
          font-size: 12px;
          margin-left: auto;
          margin-right: 6px;
        }

        &:hover {
          background-color: #e1ecff;
          cursor: pointer;
          color: #3a84ff;
        }
      }
    }
  }
</style>
