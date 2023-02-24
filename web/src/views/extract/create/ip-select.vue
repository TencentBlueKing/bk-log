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
    header-position="left"
    :mask-close="false"
    :close-icon="false"
    :width="880"
    @value-change="handleValueChange"
    :confirm-fn="handleConfirm">
    <div class="ip-select-container" v-bkloading="{ isLoading }">
      <div class="select-title">
        <div class="server-info">
          {{$t('共 {n} 台', { n: selectedIpNodes.length })}}：
        </div>
        <div class="server-options">
          <bk-button @click="copyIp">{{$t('复制IP')}}</bk-button>
          <bk-button theme="danger" @click="clearIp">{{$t('清空IP')}}</bk-button>
        </div>
      </div>
      <div class="select-content">
        <div class="tree-container">
          <input
            type="text"
            class="bk-form-input tree-filter-input"
            :placeholder="$t('搜索') + '...'"
            v-model="searchWord"
            @keyup.enter="search">
          <bk-big-tree
            ref="treeRef"
            :data="topoTemplate"
            :default-expanded-nodes="[topoTemplate[0] && topoTemplate[0].id]"
            display-matched-node-descendants
            show-checkbox
            @check-change="handleNodeCheck">
          </bk-big-tree>
        </div>
        <div class="selected-ip-list">
          <bk-table
            class="king-table scroll-table"
            :data="selectedIpNodes"
            :empty-text="$t('暂无数据')"
            :height="400">
            <bk-table-column prop="ip" label="IP"></bk-table-column>
            <bk-table-column prop="bk_cloud_name" :label="$t('云区域')"></bk-table-column>
            <bk-table-column :label="$t('操作')" align="center">
              <template slot-scope="scope">
                <bk-button text @click="handleRemoveIp(scope)">{{$t('移除')}}</bk-button>
              </template>
            </bk-table-column>
            <div slot="empty">
              <empty-status empty-type="empty"></empty-status>
            </div>
          </bk-table>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import { copyMessage } from '@/common/util';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    EmptyStatus,
  },
  props: {
    showSelectDialog: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: true,
      searchWord: '',
      topoTemplate: [],
      selectedIpNodes: [],
      topoCache: [], // 缓存已选择的树节点
    };
  },
  computed: {
    selectedIpList() {
      return this.selectedIpNodes.map(item => ({
        ip: item.ip,
        bk_cloud_id: item.bk_cloud_id,
      }));
    },
  },
  created() {
    this.initTopoTemplate();
  },
  methods: {
    async initTopoTemplate() {
      try {
        this.isLoading = true;
        const res = await this.$http.request('extract/getTopoIpList', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        this.topoTemplate = res.data;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    handleNodeCheck(checkedId, checkedNode) {
      this.handleTree(checkedNode.tree);
    },
    handleTree(tree) {
      const { nodes, checkedNodes } = tree;
      const ipSet = new Set();
      const ipObj = {};
      // 从 topo 中已勾选的节点找到带 ip 的节点，去重
      checkedNodes.forEach((node) => {
        const ip = node.data?.ip;
        if (ip && !ipSet.has(ip)) {
          ipSet.add(ip);
          ipObj[ip] = {
            ip,
            bk_cloud_id: node.data.bk_cloud_id,
          };
        }
      });
      // 并将所有带此 ip 的节点勾选上
      const ipList = [...ipSet];
      nodes.forEach((node) => {
        if (ipList.includes(node.data?.ip)) {
          node.checked = true;
        }
      });
      this.isLoading = true;
      this.$http.request('collect/getHostByIp', {
        params: {
          bk_biz_id: this.$store.state.bkBizId,
        },
        data: {
          bk_biz_id: this.$store.state.bkBizId,
          ip_list: Object.values(ipObj),
        },
      }).then((res) => {
        this.selectedIpNodes = res.data;
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    handleRemoveIp(scope) {
      this.selectedIpNodes.splice(scope.$index, 1);
      this.$refs.treeRef.nodes.forEach((node) => {
        if (node.data?.ip === scope.row.ip) {
          node.checked = false;
        }
      });
    },
    handleValueChange(val) {
      if (val === true && this.topoCache.length) { // 恢复数据到确定选择的数据
        this.$refs.treeRef.setChecked(this.topoCache);
        this.handleTree(this.$refs.treeRef);
      }
      this.$emit('update:showSelectDialog', val);
    },
    copyIp() {
      copyMessage(JSON.stringify(this.selectedIpList));
    },
    clearIp() {
      this.selectedIpNodes.splice(0);
      this.$refs.treeRef.nodes.forEach((node) => {
        node.checked = false;
      });
    },
    async handleConfirm() {
      if (!this.selectedIpList.length) {
        return;
      }

      try {
        this.isLoading = true;
        // 选择服务器后，获取可预览的路径
        const res = await this.$http.request('extract/getAvailableExplorerPath', {
          data: {
            bk_biz_id: this.$store.state.bkBizId,
            ip_list: this.selectedIpList,
          },
        });
        const availablePaths = res.data.map(item => item.file_path);
        this.$emit('confirm', this.selectedIpList, availablePaths);
        this.$emit('update:showSelectDialog', false);

        this.topoCache = JSON.parse(JSON.stringify(this.$refs.treeRef.checked));
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
    search() {
      this.$refs.treeRef.filter(this.searchWord);
    },
  },
};
</script>

<style lang="scss" scoped>
  .ip-select-container {
    .select-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 60px;
      margin-bottom: 4px;
      font-size: 14px;

      .server-options .bk-button {
        margin-left: 10px;
      }
    }

    .select-content {
      display: flex;
      height: 400px;

      .tree-container {
        padding: 12px;
        width: 340px;
        border: 1px solid #dfe0e5;
        border-right: none;
        overflow: auto;
      }

      .selected-ip-list {
        width: 492px;

        ::v-deep .king-table {
          border-radius: 0;
        }
      }
    }
  }

  .scroll-table {
    overflow-y: auto;
  }
</style>
