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
    width="1060"
    header-position="left"
    theme="primary"
    render-directive="if"
    :title="$t('选择标签')"
    :value="isShowDialog"
    :mask-close="false"
    @confirm="handelConfirmLabel"
    @cancel="handelCancelDialog">
    <div class="log-target-container" v-bkloading="{ isLoading: treeLoading, zIndex: 10 }">
      <div
        :class="['label-tree', activeStretchBtn === 'left' && 'right-border-light']"
        :style="`width : ${leftPreWidth}px`">
        <bk-input
          class="tree-search"
          right-icon="bk-icon icon-search"
          v-model="filterStr"
          @change="search"
        ></bk-input>
        <bk-big-tree
          class="big-tree"
          ref="labelTreeRef"
          size="small"
          selectable
          has-border
          show-link-line
          :data="treeList"
          :default-expanded-nodes="defaultExpandList"
          :filter-method="filterMethod"
          @select-change="handleSelectTreeItem">
          <div slot-scope="{ data }">
            <div class="item-slot">
              <span class="item-name" v-bk-overflow-tips>{{data.name}}</span>
              <span v-if="data.children" class="item-number">{{data.children.length}}</span>
            </div>
          </div>
        </bk-big-tree>
        <div class="left-drag bk-log-drag-simple" @mousedown="(e) => handleMouseDown(e, 'left')"></div>
      </div>
      <div class="label-operate" v-bkloading="{ isLoading: labelLoading, zIndex: 10 }">
        <div class="label-config" v-if="!isEmpty">
          <div class="select-container" v-if="matchCheckedItemList.length">
            <div class="select-title">{{$t('已选择')}}</div>
            <!-- 标签生成已选择里挑选的 -->
            <div class="select-list">
              <bk-checkbox-group v-model="matchCheckedList">
                <bk-checkbox
                  v-for="labItem in matchCheckedItemList"
                  ext-cls="select-item"
                  :key="labItem.id"
                  :value="labItem.id">
                  <match-label-item
                    :class="{ 'is-checked': isSelectItem('matchCheckedList', labItem.id) }"
                    :match-item="labItem" />
                </bk-checkbox>
              </bk-checkbox-group>
            </div>
          </div>
          <div
            class="no-choice-container select-list"
            :style="`max-height: ${getNoChoiceMaxHeight}px;`">
            <!-- 标签生成备选的 -->
            <bk-checkbox-group v-model="matchSelectList">
              <bk-checkbox
                v-for="labItem in matchSelectItemList"
                ext-cls="select-item"
                :key="labItem.id"
                :value="labItem.id">
                <match-label-item
                  :class="{ 'is-checked': isSelectItem('matchSelectList', labItem.id) }"
                  :match-item="labItem" />
              </bk-checkbox>
            </bk-checkbox-group>
            <!-- 主页已选中的 -->
            <div class="view-select-container">
              <match-label-item
                v-for="(labItem, labKey) in labelParams.labelSelector"
                class="select-item disabled"
                :key="labKey"
                :match-item="labItem" />
            </div>
          </div>
        </div>
        <div class="match-empty" v-else>
          <empty-status empty-type="empty" :show-text="false">
            <p>{{$t('暂无标签')}}</p>
            <span>{{$t('请先在左侧列表进行选择')}}</span>
          </empty-status>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
import { random } from '@/common/util';
import matchLabelItem from './match-label-item';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    matchLabelItem,
    EmptyStatus,
  },
  props: {
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    labelParams: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      treeList: [],
      filterStr: '', // 搜索过滤字符串
      expressOptionList: [], // 表达式select数组
      resultStrList: [], // 结果展示拼接字符串数组
      defaultExpandList: [], // 默认展开数组
      leftRange: [300, 600],
      matchCheckedList: [], // 已选择的
      matchCheckedItemList: [], // 已选择的选择列表
      matchSelectList: [], // 备选的
      matchSelectItemList: [], // 备选的选择列表
      leftPreWidth: 300,
      treeLoading: false, // 树loading
      labelLoading: false, // 标签loading
      timer: null,
      activeStretchBtn: '',
      cacheRequestParams: { // 缓存树结构传参
        bk_biz_id: null,
        bcs_cluster_id: null,
        type: null,
        namespace: null,
      },
    };
  },
  computed: {
    // 根据已选择的列表来计算备选和主页已选择的公用最大高度
    getNoChoiceMaxHeight() {
      const selectLength = this.matchCheckedItemList.length ?? 0;
      if (!selectLength) return 544;
      return 544 - (78 + Math.min(this.matchCheckedItemList.length, 6) * 42);
    },
    isEmpty() {
      const labelSelectorList = this.labelParams.labelSelector ?? [];
      const allList = [...this.matchCheckedItemList, ...this.matchSelectItemList, ...labelSelectorList];
      return !allList.length;
    },
  },
  watch: {
    isShowDialog(val) {
      if (val) {
        const { bk_biz_id, bcs_cluster_id, type, namespaceStr } = this.labelParams;
        const requestParams = { bk_biz_id, bcs_cluster_id, type, namespace: namespaceStr };
        // 若传参参数有变则重新请求树结构列表
        if (JSON.stringify(requestParams) !== JSON.stringify(this.cacheRequestParams)) {
          this.treeList = [];
          this.defaultExpandList = [];
          this.resultStrList = [];
          this.cacheRequestParams = requestParams;
          this.getTreeList();
        }
      } else {
        this.resetSelect();
        this.filterStr = '';
      }
    },
  },
  methods: {
    handleSelectTreeItem(treeItem) {
      if (!['pod', 'node'].includes(treeItem.data.type)) return;

      const [nameSpaceStr, nameStr] = this.getNameStrAndNameSpace(treeItem); // 获取当前树节点标签请求name字符串
      const { bk_biz_id, bcs_cluster_id, type } = this.labelParams;
      const query = { namespace: nameSpaceStr, bcs_cluster_id, type, bk_biz_id, name: nameStr };
      if (type === 'node') delete query.namespace;
      this.labelLoading = true;
      this.catchCheckedItemList();
      this.$http.request('container/getNodeLabelList', { query }).then((res) => {
        if (res.code === 0) {
          this.matchSelectItemList = res.data.filter((item) => {
            // 先生成已选列表和主页已选列表 若为没有 则全返回
            const allCheckedItemList = [...this.matchCheckedItemList, ...this.labelParams.labelSelector];
            if (!allCheckedItemList.length) return true;
            // 判断当前备选是否在已选和主页已选有重复 若有重复则不返回
            return !allCheckedItemList.some(mItem => item.key === mItem.key
             && item.value === mItem.value
             && mItem.operator === '=');
          }).map(item => ({ ...item, operator: '=', id: random(10) }));
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.labelLoading = false;
        });
    },
    // 切换树选项时缓存备选列表里的值
    catchCheckedItemList() {
      if (!this.matchSelectList.length) return; // 备选没有选择
      const checkedItemList = this.matchSelectItemList.filter((item) => {
        if (this.matchSelectList.includes(item.id)) { // 包含了id 过滤已选择里有过的值
          return !this.matchCheckedItemList.some(mItem => item.key === mItem.key
           && item.value === mItem.value
           && item.operator === mItem.operator);
        };
        return false;
      });
      this.matchCheckedItemList = [...this.matchCheckedItemList, ...checkedItemList];
      this.matchCheckedList = [...this.matchSelectList, ...this.matchCheckedList];
      this.matchSelectList = [];
    },
    // 关闭弹窗 重置备选 已选数组
    resetSelect() {
      this.matchSelectList = [];
      this.matchSelectItemList = [];
      this.matchCheckedList = [];
      this.matchCheckedItemList = [];
    },
    handelConfirmLabel() {
      const allCheckedKey = [...this.matchSelectList, ...this.matchCheckedList];
      const allCheckedValue = [...this.matchSelectItemList, ...this.matchCheckedItemList].map(item => ({ ...item, type: 'match_labels' }));
      const matchLabels = allCheckedValue.filter(item => allCheckedKey.includes(item.id));
      const labelObj = {
        labelSelector: [...matchLabels, ...this.labelParams.labelSelector],
      };
      this.resetSelect();
      this.$emit('configLabelChange', labelObj);
      this.$emit('update:is-show-dialog', false);
    },
    /**
     * @desc: 根据请求类型获取树列表
     */
    getTreeList() {
      const { bk_biz_id, bcs_cluster_id, type, namespaceStr } = this.labelParams;
      const query = { namespace: namespaceStr, bcs_cluster_id, type, bk_biz_id };
      if (type === 'node') delete query.namespace;
      this.treeLoading = true;
      this.$http.request('container/getPodTree', { query }).then((res) => {
        if (res.code === 0) {
          // 树列表
          this.treeList = typeof res.data === 'object' ? [res.data] : res.data;
          const [strList, expandList] = this.getResultStrList(this.treeList);
          // 结果展示列表
          this.resultStrList = strList;
          // 默认展开列表
          this.defaultExpandList = expandList;
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.treeLoading = false;
        });
    },
    /**
     * @desc: 根据树节点的值获取结果回填数组
     * @param { Array } treeList 树数组
     * @returns { Array } strList 结果回填数组
     */
    getResultStrList(treeList) {
      const absoluteNameList = []; // 最后一级之前拼接的name值
      const strList = []; // 结果字符串数组
      const expandList = []; // 默认展示ID数组
      // 树结构是数组 进行for循环遍历
      treeList.forEach((item, index) => {
        (function recurse(currentItem, fatherItem) {
          if (currentItem.children) {
            // 还有子数组则先判断name列表里当前对象是否有缓存name
            if (absoluteNameList.find(aItem => aItem.index === index)) {
              absoluteNameList[index].name = `${fatherItem.name}/${currentItem.name}`;
            } else {
              absoluteNameList.push({
                index,
                name: currentItem.name,
              });
            }
            for (const child of currentItem.children) {
              recurse(child, item);
            }
            expandList.push(currentItem.id);
          } else {
            // 无子数组则表示最后一层 则赋值字符串数组
            strList.push({
              id: currentItem.id,
              name: `${absoluteNameList[index].name}/${currentItem.name}`,
            });
            return;
          }
        }(item)); // 自执行函数保存递归函数
      });
      return [strList, expandList];
    },
    /**
     * @desc: 根据选中的树节点获取请求用的name字符串
     * @param { Array } treeList
     * @returns { String } 'name1,name2,name3'
     */
    getNameStrAndNameSpace(treeList) {
      const namespaceSetList = new Set();
      const strList = []; // 结果字符串数组
      (function recurse(currentItem) {
        if (currentItem.data?.children) {
          for (const child of currentItem.children) {
            recurse(child);
          }
        } else {
          if (currentItem.parent.data.type === 'namespace') {
            namespaceSetList.add(currentItem.parent.data.id);
          }
          strList.push(currentItem.data.id);
          return;
        }
      }(treeList)); // 自执行函数保存递归函数
      const nameStr = strList.join(',');
      const nameSpaceStr = [...namespaceSetList].join(',');
      return [nameSpaceStr, nameStr];
    },
    handleMouseDown(e, direction = 'left') {
      const node = e.target;
      const parentNode = node.parentNode;

      if (!parentNode) return;

      const nodeRect = node.getBoundingClientRect();
      const rect = parentNode.getBoundingClientRect();
      this.activeStretchBtn = direction;
      const handleMouseMove = (event) => {
        const [min, max] = this.leftRange;
        const newWidth = event.clientX - rect.left - nodeRect.width;
        this.leftPreWidth = newWidth < min ? min : Math.min(newWidth, max);
      };
      const handleMouseUp = () => {
        this.activeStretchBtn = '';
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    },
    handelCancelDialog() {
      this.$emit('update:is-show-dialog', false);
    },
    isSelectItem(listName, key) {
      return this[listName].includes(key);
    },
    search() {
      this.$refs.labelTreeRef.filter(this.filterStr);
    },
    filterMethod(keyword, node) {
      return node.data.name.includes(keyword);
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
    position: relative;
    z-index: 99;
    background: #fff;
    border-right: 1px solid #dcdee5;

    .tree-search {
      width: 100%;
    }

    .big-tree {
      margin-top: 12px;
      overflow-y: auto;

      /* stylelint-disable-next-line declaration-no-important */
      height: 476px !important;
    }

    .item-slot {
      align-items: center;
      color: #63656e;

      @include flex-justify(space-between);

      .item-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item-number {
        display: inline-block;
        font-size: 12px;
        min-width: 20px;
        height: 16px;
        padding: 2px 0;
        margin: 0 6px;
        line-height: 12px;
        text-align: center;
        color: #979ba5;
        background: #f0f1f5;
        border-radius: 2px;
      }
    }

    :deep(.bk-big-tree-node) {
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
    width: calc( 100% - 300px );

    .label-config {
      height: 100%;
      width: 100%;
      min-width: 600px;
      padding: 14px 24px;
    }

    .select-title {
      font-size: 14px;
      color: #313238;
      margin-bottom: 12px;
    }

    .select-container {
      border-bottom: 1px solid #dcdee5;
      padding-bottom: 22px;
      & + .no-choice-container {
        margin-top: 22px;
      }
    }

    .select-list {
      max-height: 252px;
      overflow-y: auto;

      .is-checked {
        .specify-box {
          background: #E1ECFF;
        }
      }
    }

    .no-choice-container {
      overflow-y: auto;
    }

    .view-select-container {
      margin-left: 30px;
      .disabled {
        opacity: 0.6;
        cursor: no-drop;
        .operator {
          color: #979BA5;
        }
      }
    }

    .select-item {
      align-items: center;
      padding: 4px 0;

      .bk-checkbox-text {
        flex: 1;
        margin-left: 14px;
      }
      @include flex-justify(space-between);
    }
  }

  .left-drag {
    right: -5px
  }

  .bk-log-drag-simple {
    position: absolute;
    width: 10px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-items: center;
    border-radius: 3px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;

    &:hover {
      user-select: none;
      cursor: col-resize;
    }
  }

  .right-border-light {
    border-right-color: #3a84ff;
  }

  .match-empty {
    height: 585px;
    flex-direction: column;

    p {
      font-size: 14px;
      margin-bottom: 12px;
    }

    span {
      font-size: 12px;
      color: #979BA5;
    }

    @include flex-center();

    .icon-empty {
      color: #c3cdd7;
      font-size: 50px;
    }
  }

}
</style>
