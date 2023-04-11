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
  <div id="graph-wrapper"></div>
</template>
<script>
import BkFlow from '@blueking/bkflow.js';
import tableRowDeepViewMixin from '@/mixins/table-row-deep-view-mixin';

export default {
  mixins: [tableRowDeepViewMixin],
  props: {
    tree: {
      type: Object,
      required: true,
    },
    config: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    const centerPoint = document.querySelector('.chart-container').clientWidth / 2;
    const instance = new BkFlow('#graph-wrapper', {
      mode: 'readonly',
      background: '#fff',
      renderVisibleArea: true,
      nodeConfig: [{
        type: 'default',
        width: this.config.span_width,
        height: 30,
        radius: '2px',
      }],
      tree: {
        mode: 'vertical',
        node: { width: 120 },
        horizontalSpacing: this.config.span_width / 2,
        verticalSpacing: 50,
        chartArea: {
          left: centerPoint,
          top: 50,
        },
      },
      zoom: {
        scaleExtent: [0.2, 2],
        controlPanel: true,
        tools: [{
          text: this.$t('放大'),
          icon: 'bk-icon icon-plus-circle',
          type: 'zoomIn',
        }, {
          text: this.$t('缩小'),
          icon: 'bk-icon icon-minus-circle',
          type: 'zoomOut',
        }, {
          text: this.$t('还原'),
          icon: 'bk-icon icon-full-screen',
          type: 'resetPosition',
        }],
      },
      lineConfig: {
        canvasLine: true,
        color: '#DCDEE5',
        activeColor: '#3a84ff',
      },
      // 配置节点样式
      onNodeRender: (node) => {
        const isError = this.tableRowDeepView(node, this.config.error_field, '', false);
        const className = node.relationship === 1 ? 'subscript' : 'node-item';
        const nodeClass = isError === true ? `${className} is-error` : className;
        return `<div class="${nodeClass}">
                  <a
                    href="javascript:;"
                    title="${node[this.config.display_field]}">
                    ${node[this.config.display_field]}
                  </a>
                </div>`;
      },
    });
    instance.renderTree(this.tree, 'spanID', this.config.display_field);

    instance.on('nodeClick', (node) => {
      this.$emit('showSpanId', { spanID: node.spanID });
    });
  },
};
</script>

<style lang="scss">
  #graph-wrapper {
    width: 100%;
    height: 458px;

    .node-item,
    .subscript {
      padding: 0 10px;
      line-height: 30px;
      text-align: center;
      font-size: 12px;
      height: 30px;
      border-radius: 3px;
      background-color: #f0f9eb;
      border: 1px solid #defad0;
      color: #67c23a;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      transition: all .2s;

      a {
        color: inherit;
      }

      &:hover {
        background: #83f095;
        color: #fff;
        transition: all .2s;
      }

      &.is-error {
        background-color: #ffeded;
        border: 1px solid #fde2e2;
        color: #f56c6c;
        transition: all .2s;

        &:hover {
          background: #fbb8ac;
          color: #fff;
          transition: all .2s;
        }
      }
    }

    .subscript {
      position: relative;

      &::before {
        content: '';
        display: inline-block;
        width: 0;
        height: 0;
        border-top: 7px solid #44e35f;
        border-right: 7px solid transparent;
        border-bottom: 7px solid transparent;
        border-left: 7px solid #44e35f;
        position: absolute;
        top: 0;
        left: 0;
      }

      &.is-error {
        &::before {
          border-top: 7px solid #fe6673;
          border-left: 7px solid #fe6673;
        }
      }
    }
  }
</style>
