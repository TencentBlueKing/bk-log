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
  <bk-dialog
    :value="isShowDialog"
    :mask-close="false"
    width="1250"
    header-position="left"
    theme="primary"
    title="日志目标"
    render-directive="if"
    @confirm="handelConfirmLabel"
    @cancel="handelCancelDialog">
    <div class="log-target-container">
      <div class="label-tree">
        <div class="child-title">
          <span>{{$t('获取标签')}}</span>
          <span>{{$t('选择Service以获取Label列表')}}</span>
        </div>
        <bk-input
          class="tree-search"
          right-icon="bk-icon icon-search"
          v-model="filter"
          @change="search"
        ></bk-input>
        <bk-big-tree
          class="big-tree"
          ref="labelTreeRef"
          :selectable="true"
          :data="treeList"
          :node-key="'id'"
          :has-border="true"
          :expand-on-click="false"
          @select-change="handleSelectTreeItem">
          <div slot-scope="{ data }">
            <div class="item-slot">
              <span>{{data.key}}</span>
              <span class="item-number">{{data.id}}</span>
            </div>
          </div>
        </bk-big-tree>
      </div>
      <div class="label-operate">
        <div class="label-config" :style="`width : calc( 100% - ${preWidth}px )`">
          <div class="child-title">
            <span>{{$t('设置标签')}}</span>
            <span>{{$t('通过标签获取采集目标列表')}}</span>
          </div>
          <div class="name-space-container">
            <div class="match-title">
              <span>{{$t('匹配范围')}}</span>
            </div>
            <div class="express-box">
              <div class="name-space">
                <span>{{$t('NameSpace选择')}}</span>
                <bk-select></bk-select>
              </div>
            </div>
          </div>

          <div class="match-box">
            <div class="express-container">
              <match-label
                :match-selector="labelSelector.match_expressions"
                :match-obj.sync="matchExpressObj">
              </match-label>
            </div>

            <div class="label-container">
              <match-label
                :match-selector="labelSelector.match_labels"
                :match-obj.sync="matchLabelObj">
              </match-label>
            </div>
          </div>
        </div>

        <div class="result">
          <div :class="['result-container',!preWidth && 'is-sliding-close']" :style="`width : ${preWidth}px`">
            <div class="child-title">
              <span>{{$t('结果预览')}}</span>
              <span></span>
            </div>
            <span class="hit-title">
              {{$t('已命中')}}
              <span class="hit-number">4</span>
              {{$t('个内容')}}
            </span>
            <div class="hit-item" v-for="index of 4" :key="index">{{$t('集群')}}{{index}}</div>
            <div class="bk-log-drag-simple" @mousedown="handleMouseDown"></div>
          </div>
          <div
            v-if="!preWidth"
            class="open-preview"
            v-bk-tooltips="{
              content: $t('点击展开'),
              showOnInit: true,
              placements: ['left'],
              delay: 1000,
              boundary: 'window'
            }"
            @click.stop="handleResetWidth">
            <i class="bk-icon icon-angle-left"></i>
          </div>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
import matchLabel from './match-label';
import { deepClone } from '../../monitor-echarts/utils';

export default {
  components: {
    matchLabel,
  },
  props: {
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    labelSelector: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      treeList: [
        {
          key: '集群[批量启动进程模块1]',
          expanded: true,
          id: 1,
          expressList: [
            { key: 'aaaa1111111111111111', value: 'xx1111111111xx', customize: false, operator: 'In', id: 1 },
            { key: 'aaaa2', value: 'xxxx', customize: false, operator: 'In', id: 2 },
            { key: 'aaaa3', value: 'xxxx', customize: false, operator: 'In', id: 3 },
          ],
          labelList: [
            { key: 'aaaa1', value: 'xxxx', customize: false, operator: 'In', id: 1 },
            { key: 'aaaa2', value: 'xxxx', customize: false, operator: 'In', id: 2 },
            { key: 'aaaa3', value: 'xxxx', customize: false, operator: 'In', id: 3 },
          ],
          children: [
            {
              key: 'testwa.fda.1.1',
              id: 2,
              expressList: [
                { key: 'aaaa4', value: 'xxxx', customize: false, operator: 'In', id: 4 },
                { key: 'aaaa5', value: 'xxxx', customize: false, operator: 'In', id: 5 },
                { key: 'aaaa6', value: 'xxxx', customize: false, operator: 'In', id: 6 },
              ],
              labelList: [
                { key: 'aaaa4', value: 'xxxx', customize: false, operator: 'In', id: 4 },
                { key: 'aaaa5', value: 'xxxx', customize: false, operator: 'In', id: 5 },
                { key: 'aaaa6', value: 'xxxx', customize: false, operator: 'In', id: 6 },
              ] },
            { key: 'testwa.fda.1.2', title: 'testwa.fda.1.2', id: 3 },
            {
              key: '集群[批量启动]',
              id: 5,
              expanded: true,
              children: [
                { key: 'testwa.fda.2.1', id: 6 },
                { key: 'testwa.fda.2.2', id: 7 },
                { key: 'testwa.fda.2.3', id: 8 },
              ],
            },
            { key: 'testwa.fda.1.3', id: 4 },
            { key: '集群[批量启动]', id: 9 },
          ],
        },
      ],
      filter: '',
      matchExpressObj: {
        matchType: 'express', // 匹配类型
        treeList: [], // 树的值列表
        selectList: [], // 选中的元素的列表ID
      },
      matchLabelObj: {
        matchType: 'label', // 匹配类型
        treeList: [], // 树的值列表
        selectList: [], // 选中的元素的列表ID
      },
      range: [200, 600],
      preWidth: 280,
    };
  },
  methods: {
    handleSelectTreeItem(treeItem) {
      this.matchExpressObj.treeList = deepClone(treeItem.data.expressList);
      this.matchLabelObj.treeList = deepClone(treeItem.data.labelList);
    },
    handelConfirmLabel() {
      const labelObj = {
        label_selector: {
          match_labels: this.matchLabelObj.selectList,
          match_expressions: this.matchExpressObj.selectList,
        },
      };
      this.$emit('configLabelChange', labelObj);
      this.$emit('update:isShowDialog', false);
    },
    handleMouseDown(e) {
      const node = e.target;
      const parentNode = node.parentNode;

      if (!parentNode) return;

      const nodeRect = node.getBoundingClientRect();
      const rect = parentNode.getBoundingClientRect();
      const handleMouseMove = (event) => {
        const [min, max] = this.range;
        const newWidth = rect.right - event.clientX + nodeRect.width;
        if (newWidth < min) {
          this.preWidth = 0;
        } else {
          this.preWidth = Math.min(newWidth, max);
        }
      };
      const handleMouseUp = () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    },
    handelCancelDialog() {
      this.$emit('update:isShowDialog', false);
    },
    search() {
      this.$refs.labelTreeRef.filter(this.filter);
    },
    handleResetWidth() {
      this.preWidth = 280;
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.log-target-container {
  width: 100%;
  height: 585px;
  background: #fff;
  border: 1px solid #dcdee5;
  border-radius: 2px;
  display: flex;
  overflow: hidden;

  .label-tree {
    min-width: 290px;
    padding: 14px 24px;
    border-right: 1px solid #dcdee5;

    .tree-search {
      width: 240px;
    }

    .big-tree {
      margin-top: 12px;
    }

    .item-slot {
      align-items: center;
      color: #63656e;

      @include flex-justify(space-between);

      .item-number {
        width: 20px;
        height: 16px;
        margin: 0 6px 0 12px;
        background: #f0f1f5;
        border-radius: 2px;
        color: #979ba5;

        @include flex-center;
      }
    }

    ::v-deep .bk-big-tree-node {
      &:hover {
        background: #f0f1f5;
      }

      &.is-selected {
        .item-number {
          background: #a3c5fd;
          color: #fff;
        }
      }
    }
  }

  .label-operate {
    width: 100%;
    display: flex;
    position: relative;

    .express-container {
      padding-bottom: 16px;
      border-bottom: 1px solid #dcdee5;;
    }

    .label-container {
      margin-top: 16px;
    }
  }

  .label-config {
    height: 100%;
    min-width: 600px;
    padding: 14px 24px;

    .match-box {
      height: 554px;
    }

    .match-title {
      margin-bottom: 12px;
      font-size: 12px;

      @include flex-justify(space-between);

      > span {
        font-weight: 700;
        color: #63656e;
      }
    }

    .add-match {
      color: #3a84ff;
      margin-right: 8px;
      cursor: pointer;

      .icon-plus-circle {
        margin-right: 4px;
      }
    }

    .add-filling {
      > span {
        color: #ff9c01;
        padding: 0 7px;
      }

      .fill-first {
        width: 38%;
      }

      .fill-second {
        width: 14%;
        margin: 0 8px;
      }

      .fill-input {
        width: 45%;
      }

      .label-input {
        width: 50%;
      }

      .add-operate {
        font-size: 18px;

        .bk-icon {
          cursor: pointer;
        }

        .icon-check-line {
          color: #2dcb56;
          margin: 0 8px;
        }

        .icon-close-line-2 {
          color: #c4c6cc;
          margin-right: 8px;
        }
      }
    }

    .bk-form-control {
      width: 100%;

      .bk-form-checkbox {
        width: 100%;

        &:hover {
          .match-item {
            background: #f0f1f5;
          }
        }

        &.is-checked {
          .match-item {
            background: #e1ecff;
          }
        }
      }
    }

    .bk-checkbox-text {
      width: calc(100% - 40px);
      margin-left: 16px;
    }

    .express-box {
      border-bottom: 1px solid #dcdee5;
      padding-bottom: 8px;
      margin-bottom: 16px;
    }

    .list-container {
      overflow-y: auto;
    }

    .name-space-container {
      .name-space {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 8px;
        font-size: 12px;

        .bk-select {
          width: calc( 100% - 120px )
        }
      }
    }

    .match-item {
      width: 100%;
      padding: 6px 12px;
      margin: 8px 0;
      border-radius: 2px;
      background: #f5f7fa;
      font-size: 12px;

      > div {
        width: 50%;
        align-items: center;
      }

      .match-left {
        color: #ff9c01;
        background: #fff;
        padding: 2px 6px;
        margin-right: 12px;
      }

      .match-right {
        color: #c4c6cc;
      }

      .icon-close3-shape {
        font-size: 16px;
        color: #ea3636;
      }
    }
  }

  .result {
    position: absolute;
    height: 100%;
    right: 0;
  }

  .result-container {
    height: 100%;
    position: relative;
    padding: 12px 24px;
    border-left: 1px solid #dcdee5;
    background: #f5f6fa;
    font-size: 12px;
    color: #63656e;

    &.is-sliding-close {
      display: none;
    }

    .hit-title {
      display: inline-block;
      margin-bottom: 8px;
    }

    .hit-number {
      color: #3a84ff;
    }

    .hit-item {
      padding: 8px 12px;
      margin-bottom: 4px;
      background: #fff;
      border-radius: 2px;
    }
  }

  .child-title {
    font-size: 12px;
    margin-bottom: 16px;

    :first-child {
      font-size: 14px;
      color: #313238;
      margin-right: 16px;
    }

    :last-child {
      color: #979ba5;
    }
  }

  .flex-ac {
    @include flex-align();
  }

  .justify-sb {
    @include flex-justify(space-between);
  }

  .bk-log-drag-simple {
    position: absolute;
    width: 6px;
    height: 25px;
    display: flex;
    align-items: center;
    justify-items: center;
    border-radius: 3px;
    top: 50%;
    transform: translateY(-50%);
    left: 4px;
    z-index: 100;

    &::after {
      content: ' ';
      height: 100%;
      width: 0;
      border-left: 3px dotted #63656e;
      position: absolute;
      left: 2px;
    }

    &:hover {
      user-select: none;
      cursor: col-resize;
    }
  }

  .open-preview {
    display: flex;
    justify-content: center;
    align-items: center;
    position: absolute;
    left: -10px;
    top: calc(50% - 50px);
    width: 10px;
    height: 100px;
    cursor: pointer;
    border: 1px solid #dcdee5;
    border-right: 0;
    border-radius: 4px 0px 0px 4px;
    background-color: #f0f1f5;
    z-index: 10;
    outline: 0;
  }

}
</style>
