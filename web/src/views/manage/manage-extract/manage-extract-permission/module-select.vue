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
    :value="showSelectDialog"
    :mask-close="false"
    :close-icon="false"
    :width="680"
    @value-change="handleValueChange"
    :confirm-fn="handleConfirm">
    <div class="module-select-container" v-bkloading="{ isLoading }">
      <bk-radio-group v-model="selectedTypeData" style="margin-bottom: 20px;">
        <bk-radio value="topo" style="margin-right: 16px;">{{$t('按大区选择')}}</bk-radio>
        <bk-radio value="module">{{$t('按模块选择')}}</bk-radio>
      </bk-radio-group>
      <div class="tree-container" v-show="selectedTypeData === 'topo'">
        <bk-big-tree
          ref="topoTreeRef"
          show-checkbox
          :data="topoList"
          :check-strictly="false"
          :default-checked-nodes="topoCheckedNodes"
          :default-expanded-nodes="topoExpandNodes"
          @check-change="handleTopoNodeCheck">
        </bk-big-tree>
      </div>
      <div class="tree-container" v-show="selectedTypeData === 'module'">
        <div class="checkbox-container">
          <bk-checkbox
            :value="isSelectAllModule"
            :indeterminate="indeterminate"
            @change="handleSelectAllChange">
            {{$t('全选')}}
          </bk-checkbox>
        </div>
        <bk-big-tree
          ref="moduleTreeRef"
          show-checkbox
          :data="moduleList"
          :default-checked-nodes="moduleCheckedNodes"
          @check-change="handleModuleNodeCheck">
        </bk-big-tree>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
export default {
  props: {
    showSelectDialog: {
      type: Boolean,
      default: false,
    },
    selectedType: {
      type: String,
      default: 'topo',
    },
    selectedModules: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      isLoading: true,
      topoList: [],
      topoCheckedNodes: [],
      topoExpandNodes: [],
      moduleList: [],
      moduleCheckedNodes: [],
      selectedTypeData: this.selectedType,
      selectedTopoList: this.selectedModules,
      selectedModuleList: [], // selectedType === topo 时需要通过遍历对比列表数据得到
      isSelectAllModule: false,
      indeterminate: false, // 是否半选
    };
  },
  created() {
    // 下载目标选择服务器：1803接口。从选择的节点中过滤出ip节点获取主机
    // 权限管理策略配置选择目标：0202接口。
    // 按大区选择：勾选单个节点；
    // 按模块选择：根据bk_obj_id==='module'过滤，根据'bk_inst_name'去重后的节点。
    this.initTopoList();
  },
  methods: {
    async initTopoList() {
      try {
        this.isLoading = true;
        const res = await this.$http.request('collect/getExtractBizTopo', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        this.topoList = res.data;
        this.moduleList = this.filterList(res.data);
        // 数据回填
        const {
          topoExpandNodes,
          topoCheckedNodes,
          moduleCheckedItems,
        } = this.recursiveFindDefault(res.data, null, this.selectedModules);
        // 回填已选择的模块
        this.selectedModuleList = moduleCheckedItems.map(item => ({
          bk_inst_id: item.bk_inst_id,
          bk_inst_name: item.bk_inst_name,
          bk_obj_id: item.bk_obj_id,
          bk_biz_id: item.bk_biz_id,
        }));
        this.moduleCheckedNodes = moduleCheckedItems.map(item => item.id);
        if (this.moduleCheckedNodes.length === this.moduleList.length) {
          this.isSelectAllModule = true;
        } else if (this.moduleCheckedNodes.length !== 0) {
          this.indeterminate = true;
        }
        // 保证根节点默认展开
        const rootId = res.data[0]?.id;
        if (rootId && !topoExpandNodes.includes(rootId)) {
          topoExpandNodes.push(rootId);
        }
        // 回填已选择的大区
        this.topoExpandNodes = topoExpandNodes;
        this.topoCheckedNodes = topoCheckedNodes;
        if (topoCheckedNodes.length) { // 父亲勾选后子孙禁用勾选
          this.$nextTick(() => {
            const rootNode = this.$refs.topoTreeRef?.nodes[0];
            if (rootNode?.children?.length) {
              this.recursiveDealCheckedNode(rootNode.children, rootNode.checked);
            }
          });
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    // 初始化处理默认勾选节点，父亲勾选后子孙禁用勾选
    recursiveDealCheckedNode(nodes, bool) {
      if (bool) {
        this.inheritCheckNode(nodes, bool);
      } else {
        nodes.forEach((node) => {
          if (node?.children?.length) {
            this.recursiveDealCheckedNode(node.children, node.checked);
          }
        });
      }
    },
    // 找到模板节点并打平去重
    filterList(list, dict = {}) {
      list.forEach((item) => {
        if (item.bk_obj_id === 'module' && !dict[item.bk_inst_name]) {
          dict[item.bk_inst_name] = item;
        }
        if (item.children?.length) {
          this.filterList(item.children, dict);
        }
      });

      return Object.values(dict);
    },
    recursiveFindDefault(
      treeNodes,
      parentNode,
      selectedNodes,
      topoCheckedNodes = [],
      topoExpandNodes = [],
      moduleCheckedMap = {},
    ) {
      treeNodes.forEach((treeNode) => {
        treeNode.parentNode = parentNode || null;

        for (const selectedNode of selectedNodes) {
          if (selectedNode.bk_obj_id === treeNode.bk_obj_id && selectedNode.bk_inst_id === treeNode.bk_inst_id) {
            topoCheckedNodes.push(treeNode.id);
            if (treeNode.bk_obj_id === 'module' && !moduleCheckedMap[treeNode.bk_inst_name]) {
              moduleCheckedMap[treeNode.bk_inst_name] = treeNode;
            }
            if (parentNode) {
              topoExpandNodes.push(parentNode.id);
            }
            break;
          }
        }

        if (treeNode.children?.length) {
          this.recursiveFindDefault(
            treeNode.children,
            treeNode,
            selectedNodes,
            topoCheckedNodes,
            topoExpandNodes,
            moduleCheckedMap,
          );
        }
      });

      return {
        topoCheckedNodes,
        topoExpandNodes: [...new Set(topoExpandNodes)],
        moduleCheckedItems: Object.values(moduleCheckedMap),
      };
    },
    // 按大区选择
    handleTopoNodeCheck(checkedId, checkedNode) {
      checkedNode?.children?.length && this.inheritCheckNode(checkedNode.children, checkedNode.state.checked);
      this.selectedTopoList = this.recursiveFindTopoNodes(this.$refs.topoTreeRef.nodes[0]);
    },
    // 父亲勾选或取消勾选后，子孙跟随状态变化，且父亲勾选后子孙禁用勾选
    inheritCheckNode(nodes, bool) {
      nodes.forEach((node) => {
        node.checked = bool;
        node.disabled = bool;
        node.children?.length && this.inheritCheckNode(node.children, bool);
      });
    },
    // 遍历树找到勾选的节点，如果父节点已勾选，子孙节点不算在列表内
    recursiveFindTopoNodes(node, selectedTopoList = []) {
      if (node.checked) {
        const { data } = node;
        selectedTopoList.push({
          bk_inst_id: data.bk_inst_id,
          bk_inst_name: data.bk_inst_name,
          bk_obj_id: data.bk_obj_id,
          bk_biz_id: data.bk_biz_id,
        });
      } else if (node.children?.length) {
        node.children.forEach((child) => {
          this.recursiveFindTopoNodes(child, selectedTopoList);
        });
      }

      return selectedTopoList;
    },
    // 按模板选择
    handleModuleNodeCheck(checkedId, checkedNode) {
      const { nodes, checkedNodes } = checkedNode.tree;
      if (checkedId.length) {
        if (checkedId.length === nodes.length) {
          this.isSelectAllModule = true;
          this.indeterminate = false;
        } else {
          this.isSelectAllModule = false;
          this.indeterminate = true;
        }
      } else {
        this.isSelectAllModule = false;
        this.indeterminate = false;
      }
      this.selectedModuleList = checkedNodes.map((node) => {
        const { data } = node;
        return {
          bk_inst_id: data.bk_inst_id,
          bk_inst_name: data.bk_inst_name,
          bk_obj_id: data.bk_obj_id,
          bk_biz_id: data.bk_biz_id,
        };
      });
    },
    // 全选模板节点或者取消全选
    handleSelectAllChange(val) {
      const { nodes } = this.$refs.moduleTreeRef;
      if (val) {
        this.indeterminate = false;
        this.isSelectAllModule = true;
        nodes.forEach((node) => {
          node.checked = true;
        });
        this.selectedModuleList = nodes.map((node) => {
          const { data } = node;
          return {
            bk_inst_id: data.bk_inst_id,
            bk_inst_name: data.bk_inst_name,
            bk_obj_id: data.bk_obj_id,
            bk_biz_id: data.bk_biz_id,
          };
        });
      } else {
        this.indeterminate = false;
        this.isSelectAllModule = false;
        nodes.forEach((node) => {
          node.checked = false;
        });
        this.selectedModuleList = [];
      }
    },
    handleValueChange(val) {
      this.$emit('update:showSelectDialog', val);
    },
    handleConfirm() {
      const selectedList = this.selectedTypeData === 'topo' ? this.selectedTopoList : this.selectedModuleList;
      this.$emit('confirm', this.selectedTypeData, selectedList);
      this.$emit('update:showSelectDialog', false);
    },
  },
};
</script>

<style lang="scss" scoped>
  .module-select-container {
    .tree-container {
      height: 440px;
      overflow: auto;

      .checkbox-container {
        line-height: 22px;
        padding: 0 0 7px 20px;
        border-bottom: 1px solid #dfdfdf;
      }
    }
  }
</style>
