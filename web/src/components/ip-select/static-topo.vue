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
  <div class="static-topo">
    <bk-big-tree
      ref="tree"
      class="static-topo-content"
      show-checkbox
      :filter-method="handlerSearch"
      :default-checked-nodes="checkedData"
      :default-expanded-nodes="[treeData[0] && treeData[0].id]"
      :data="treeData"
      @check-change="handleTreeCheck">
    </bk-big-tree>
  </div>
</template>
<script>
import { debounce } from 'throttle-debounce';
export default {
  name: 'static-topo',
  props: {
    treeData: {
      type: Array,
      required: true,
    },
    checkedData: {
      type: Array,
      default() {
        return [];
      },
    },
    disabledData: {
      type: Array,
      default() {
        return [];
      },
    },
    felterMethod: {
      type: Function,
      default: () => () => {},
    },
    keyword: {
      type: String,
      default: '',
    },
    isSearchNoData: Boolean,
  },
  data() {
    return {
      watchKeyword: null,
      defaultExpanded: [],
    };
  },
  watch: {
    treeData: {
      handler(v) {
        this.$refs.tree && this.$refs.tree.setData(v || []);
      },
    },
    checkedData: {
      handler(v, old) {
        const { difference } = this.handlerGetInterOrDiff(v, old);
        this.$refs.tree && this.$refs.tree.setChecked(v, {
          checked: true,
        });
        this.$refs.tree && this.$refs.tree.setChecked(difference, {
          checked: old.length === 0,
        });
      },
    },
    disabledData: {
      handler(v, old) {
        const { difference } = this.handlerGetInterOrDiff(v, old);
        this.$refs.tree && this.$refs.tree.setDisabled(v, {
          disabled: true,
        });
        this.$refs.tree && this.$refs.tree.setDisabled(difference, {
          disabled: old.length === 0,
        });
      },
    },
  },
  created() {
    this.watchKeyword = this.$watch('keyword', debounce(300, this.handleFilter));
    this.handleDefaultExpanded();
  },
  mounted() {
    if (this.keyword.length) {
      this.handleFilter(this.keyword);
    }
  },
  beforeDestroy() {
    this.watchKeyword && this.watchKeyword();
  },
  methods: {
    handleTreeCheck(checkedList, node) {
      this.$emit('node-check', 'static-topo', { checked: node.state.checked, data: node.data });
    },
    handleFilter(v) {
      const data = this.$refs.tree.filter(v);
      this.$emit('update:isSearchNoData', !data.length);
    },
    handlerSearch(keyword, node) {
      return (`${node.data.ip}`).indexOf(keyword) > -1 || (`${node.data.name}`).indexOf(keyword) > -1;
    },
    handlerGetInterOrDiff(v, old) {
      const intersection = v.filter(item => old.indexOf(item) > -1);
      let difference = v.filter(item => old.indexOf(item) === -1).concat(old.filter(item => v.indexOf(item) === -1));
      difference = difference.filter(set => !~v.indexOf(set));
      return { intersection, difference };
    },
    handleDefaultExpanded() {
      if (this.checkedData.length) {
        this.defaultExpanded = this.checkedData;
      } else {
        this.defaultExpanded.push(this.treeData[0].id);
      }
    },
  },
};
</script>
<style lang="scss" scoped>
  .static-topo {
    margin: 15px 0 0 0;

    /deep/ .bk-big-tree {
      .node-content {
        overflow: inherit;
        text-overflow: inherit;
        white-space: nowrap;
        font-size: 14px;
      }
    }
  }
</style>
