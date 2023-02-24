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
    width="1100"
    header-position="left"
    ext-cls="king-dialog-ip-selector"
    :title="$t('选择目标')"
    :position="{ top: dialogTop }"
    :auto-close="false"
    :value="showDialog"
    @value-change="handleValueChange"
    @confirm="handleConfirm"
    data-test-id="addCollectionTarget_div_selectCollectionTargetBox">
    <div class="ip-select-dialog-content">
      <topo-selector
        v-if="showDialog"
        ref="topoSelector"
        height="100%"
        :preview-width="230"
        :target-node-type="targetNodeType"
        :target-object-type="targetObjectType"
        :checked-data="targetNodes"
        :show-dynamic-group="showDynamicGroup"
        @check-change="handleChecked" />
    </div>
  </bk-dialog>
</template>

<script>
import TopoSelector from '@/components/ip-selector/business/topo-selector-new.vue';

export default {
  components: {
    TopoSelector,
  },
  props: {
    showDialog: {
      type: Boolean,
      default: false,
    },
    targetObjectType: {
      type: String,
      default: 'HOST',
    },
    targetNodeType: {
      type: String,
      default: 'TOPO',
    },
    targetNodes: {
      type: Array,
      default() {
        return [];
      },
    },
    // 是否显示动态分组
    showDynamicGroup: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    const top = (window.innerHeight - 675) / 2;
    const dialogTop = top < 70 ? 70 : top;
    return {
      dialogTop,
    };
  },
  methods: {
    handleChecked() {
      // const { type, data = [] } = checkedData
      // console.log('handleChecked', type, data)
    },
    handleValueChange(val) {
      this.$emit('update:showDialog', val);
    },
    handleConfirm() {
      const params = this.getParams();
      this.$emit('target-change', params);
    },
    getParams() {
      const { type, data } = this.$refs.topoSelector.getCheckedData();
      return {
        target_node_type: type,
        target_nodes: data,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
  .ip-select-dialog-content {
    height: 560px;
  }
</style>

<style lang="scss">
  .king-dialog-ip-selector.bk-dialog-wrapper {
    .bk-dialog-header {
      padding-bottom: 10px;
    }

    .bk-dialog-body {
      padding-bottom: 0;
    }

    .bk-dialog-footer {
      border: none;
      background-color: #fff;
    }
  }
</style>
