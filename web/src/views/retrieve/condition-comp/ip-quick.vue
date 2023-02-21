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
  <div class="ip-quick-container">
    <div v-if="targetNode.length" class="tag" @click="openDialog">
      <i18n path="已选择 {0} 个{1}">
        <span>{{targetNode.length}}</span>
        <span>{{nodeUnit}}</span>
      </i18n>
      <span class="bk-icon icon-close-line" @click.stop="removeSelections"></span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    targetNode: {
      type: Array,
      required: true,
    },
    targetNodeType: {
      type: String,
      required: true,
    },
  },
  computed: {
    nodeUnit() {
      const nodeTypeTextMap = {
        TOPO: this.$t('节点'),
        INSTANCE: this.$t('IP'),
        SERVICE_TEMPLATE: this.$t('服务模板'),
        SET_TEMPLATE: this.$t('集群模板'),
        DYNAMIC_GROUP: this.$t('动态分组'),
      };
      return nodeTypeTextMap[this.targetNodeType] || '';
    },
  },
  methods: {
    openDialog() {
      this.$emit('openIpQuick');
    },
    // 移除已选择的模块或IP
    removeSelections() {
      this.$emit('confirm', {
        modules: [],
        ips: '',
        target_nodes: [],
        target_node_type: '',
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .ip-quick-container {
    display: flex;
    flex-flow: wrap;
    max-height: 102px;
    overflow: auto;
    margin-right: 3px;

    @include scroller($backgroundColor: #c4c6cc, $width: 4px);

    .tag {
      position: relative;
      padding: 0 28px 0 10px;
      margin-right: 2px;
      margin-bottom: 2px;
      background: #eceef5;
      border-radius: 2px;
      font-size: 12px;
      color: #63656e;
      line-height: 32px;
      white-space: nowrap;
      cursor: pointer;

      &.add-tag {
        padding: 0 7px;
        cursor: pointer;

        .icon-plus-line {
          font-size: 14px;
        }

        .add-text {
          margin-right: 3px;
        }

        &:hover {
          color: #3a84ff;
        }
      }

      .icon-close-line {
        display: none;
        position: absolute;
        right: 8px;
        top: 10px;
        margin: 0 0 0 6px;
        font-size: 12px;
        color: #c4c6cc;
        cursor: pointer;
      }
    }

    .tag:hover {
      .icon-close-line {
        display: inline-block;
      }
    }
  }
</style>
