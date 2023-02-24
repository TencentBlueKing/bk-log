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
    width="1350"
    header-position="left"
    theme="primary"
    render-directive="if"
    :title="$t('指定标签')"
    :value="isShowDialog"
    :mask-close="false"
    @confirm="handelConfirmLabel"
    @cancel="handelCancelDialog">
    <div class="log-target-container" v-bkloading="{ isLoading: treeLoading, zIndex: 10 }">
      <div :class="['label-tree', activeStretchBtn === 'left' && 'right-border-light']"
           :style="`width : ${leftPreWidth}px`">
        <div class="child-title">
          <span>{{$t('获取标签')}}</span>
          <span>{{$t('选择Service以获取Label列表')}}</span>
        </div>
        <bk-input
          class="tree-search"
          right-icon="bk-icon icon-search"
          v-model="filterStr"
          @change="search"
        ></bk-input>
        <bk-big-tree
          class="big-tree"
          ref="labelTreeRef"
          selectable
          has-border
          :data="treeList"
          :default-expanded-nodes="defaultExpandList"
          :filter-method="filterMethod"
          @select-change="handleSelectTreeItem">
          <div slot-scope="{ data }">
            <div class="item-slot">
              <span class="item-name" :title="data.name">{{data.name}}</span>
              <span v-if="data.children" class="item-number">{{data.children.length}}</span>
            </div>
          </div>
        </bk-big-tree>
        <div class="left-drag bk-log-drag-simple" @mousedown="(e) => handleMouseDown(e, 'left')"></div>
      </div>
      <div class="label-operate">
        <div class="label-config"
             v-bkloading="{ isLoading: labelLoading, zIndex: 10 }"
             :style="`width : calc( 100% - ${rightPreWidth + 300}px )`">
          <div class="child-title">
            <span>{{$t('设置标签')}}</span>
            <span>{{$t('通过标签获取采集目标列表')}}</span>
          </div>

          <div class="match-box">
            <div class="express-container">
              <match-label
                match-type="express"
                ref="matchExpressRef"
                :match-label-option="expressOptionList"
                :match-selector="labelParams.match_expressions"
                :match-obj.sync="matchExpressObj">
              </match-label>
            </div>

            <div class="label-container">
              <match-label
                match-type="label"
                ref="matchLabelRef"
                :all-match-list.sync="expressOptionList"
                :match-selector="labelParams.match_labels"
                :match-obj.sync="matchLabelObj">
              </match-label>
            </div>
          </div>
        </div>

        <div class="result">
          <div
            v-bkloading="{ isLoading: resultLoading, zIndex: 10 }"
            :class="['result-container',
                     !rightPreWidth && 'is-sliding-close',
                     activeStretchBtn === 'right' && 'left-border-light']"
            :style="`width : ${rightPreWidth}px`">
            <div class="child-title">
              <span>{{$t('结果预览')}}</span>
              <span></span>
            </div>
            <div class="hit-title">
              <span>
                <i18n path="已命中 {0} 个内容">
                  <span class="hit-number">{{hitResultList.length}}</span>
                </i18n>
              </span>
              <span class="hit-number" @click="handleClearHit">{{$t('清空')}}</span>
            </div>
            <div class="hit-container">
              <div class="hit-item" v-for="item of hitResultList" :key="item.id">
                <span :title="item.name">{{item.name}}</span>
              </div>
            </div>
            <div class="right-drag bk-log-drag-simple" @mousedown="(e) => handleMouseDown(e, 'right')"></div>
          </div>
          <div
            v-if="!rightPreWidth"
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

export default {
  components: {
    matchLabel,
  },
  props: {
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    labelParams: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      treeList: [],
      filterStr: '', // 搜索过滤字符串
      matchExpressObj: {
        matchType: 'express', // 匹配类型
        treeList: [], // 树的值列表
        selectList: [], // 选中的元素值列表
      },
      matchLabelObj: {
        matchType: 'label', // 匹配类型
        treeList: [], // 树的值列表
        selectList: [], // 选中的元素值列表
      },
      expressOptionList: [], // 表达式select数组
      resultStrList: [], // 结果展示拼接字符串数组
      hitResultList: [], // 命中的结果数组
      defaultExpandList: [], // 默认展开数组
      rightRange: [160, 700],
      leftRange: [300, 600],
      rightPreWidth: 280,
      leftPreWidth: 300,
      treeLoading: false, // 树loading
      labelLoading: false, // 标签loading
      resultLoading: false, // 结果loading
      timer: null,
      currentNameSpaceStr: '',
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
    getMatchLabel() {
      return {
        match_labels: this.matchLabelObj.selectList,
        match_expressions: this.matchExpressObj.selectList,
      };
    },
  },
  watch: {
    getMatchLabel: {
      deep: true,
      handler(val) {
        // 第一次请求
        if (this.treeLoading) return;
        this.getResultShow(val);
      },
    },
    isShowDialog(val) {
      if (val) {
        const { bk_biz_id, bcs_cluster_id, type, namespace } = this.labelParams;
        const requestParams = { bk_biz_id, bcs_cluster_id, type, namespace };
        // 若传参参数有变则重新请求树结构列表
        if (JSON.stringify(requestParams) !== JSON.stringify(this.cacheRequestParams)) {
          this.treeList = [];
          this.defaultExpandList = [];
          this.resultStrList = [];
          this.cacheRequestParams = requestParams;
          this.getTreeList();
        }
      } else {
        this.hitResultList = [];
        this.filterStr = '';
      }
    },
  },
  methods: {
    handleSelectTreeItem(treeItem) {
      if (!['pod', 'node'].includes(treeItem.data.type)) return;

      const [nameSpaceStr, nameStr] = this.getNameStrAndNameSpace(treeItem); // 获取当前树节点标签请求name字符串
      this.currentNameSpaceStr = nameSpaceStr;
      const { bk_biz_id, bcs_cluster_id, type } = this.labelParams;
      const query = { namespace: nameSpaceStr, bcs_cluster_id, type, bk_biz_id,  name: nameStr  };
      if (type === 'node') delete query.namespace;
      this.labelLoading = true;
      this.$http.request('container/getNodeLabelList', { query }).then((res) => {
        if (res.code === 0) {
          this.matchLabelObj.treeList = res.data.map(item => ({ ...item, operator: '=' }));
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.labelLoading = false;
          this.getResultShow(this.getMatchLabel);
        });
    },
    handelConfirmLabel() {
      const labelObj = {
        label_selector: {
          match_labels: this.matchLabelObj.selectList,
          match_expressions: this.matchExpressObj.selectList,
        },
      };
      this.$emit('configLabelChange', labelObj);
      this.$emit('update:is-show-dialog', false);
    },
    /**
     * @desc: 根据请求类型获取树列表
     */
    getTreeList() {
      const { bk_biz_id, bcs_cluster_id, type, namespace } = this.labelParams;
      const query = { namespace, bcs_cluster_id, type, bk_biz_id };
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

          this.getResultShow({
            match_labels: this.labelParams.match_labels,
            match_expressions: this.labelParams.match_expressions,
          });
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
    getResultShow(val) {
      clearTimeout(this.timer);
      this.timer = setTimeout(() => {
        this.resultLoading = true;
        // 表达式或标签是否有选中的值  获取结果请求
        if (Object.values(val).some(item => item.length)) {
          const selectorVal = JSON.parse(JSON.stringify(val));
          if (selectorVal.match_expressions.length) {
            const keyList = [];
            const handleFilterExpressions = selectorVal.match_expressions
              .reduce((pre, cur) => {
                const { key, operator, value } = cur;
                if (['Exists', 'DoesNotExist'].includes(operator)) {
                  cur.value = ''; // 清空value值
                  pre.push(cur);
                  return pre;
                }
                if (!keyList.includes(key)) { // 没有key属性则新增对象
                  keyList.push(key);
                  pre.push(cur);
                } else {
                  const filterIndex = pre.findIndex(preItem => preItem.key === key && preItem.operator === operator);
                  // 有key值判断操作是否重复, 若是新操作则生成新的对象
                  filterIndex < 0 ? pre.push(cur) : pre[filterIndex].value = `${pre[filterIndex].value}, ${value}`;
                }
                return pre;
              }, [])
              .map(item => ({ ...item, value: ['NotIn', 'In'].includes(item.operator) ? `(${item.value})` : item.value }));
            selectorVal.match_expressions = handleFilterExpressions;
          }
          const data = {
            bcs_cluster_id: this.labelParams.bcs_cluster_id,
            bk_biz_id: this.labelParams.bk_biz_id,
            type: this.labelParams.type,
            label_selector: selectorVal,
            namespace: this.currentNameSpaceStr,
          };
          this.$http.request('container/getHitResult', { data }).then((res) => {
            if (res.code === 0) {
              this.hitResultList = this.resultStrList.filter(item => res.data.includes(item.id));
            }
          })
            .catch((err) => {
              console.warn(err);
            })
            .finally(() => {
              this.resultLoading = false;
            });
        } else {
          this.hitResultList = [];
          this.resultLoading = false;
        }
      }, 1000);
    },
    handleMouseDown(e, direction = 'right') {
      const node = e.target;
      const parentNode = node.parentNode;

      if (!parentNode) return;

      const nodeRect = node.getBoundingClientRect();
      const rect = parentNode.getBoundingClientRect();
      this.activeStretchBtn = direction;
      const handleMouseMove = (event) => {
        if (direction === 'right') {
          const [min, max] = this.rightRange;
          const newWidth = rect.right - event.clientX + nodeRect.width;
          this.rightPreWidth = newWidth < min ? 0 : Math.min(newWidth, max);
        } else {
          const [min, max] = this.leftRange;
          const newWidth = event.clientX - rect.left - nodeRect.width;
          this.leftPreWidth = newWidth < min ? min : Math.min(newWidth, max);
        }
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
    search() {
      this.$refs.labelTreeRef.filter(this.filterStr);
    },
    handleResetWidth() {
      this.rightPreWidth = 280;
    },
    handleClearHit() {
      this.hitResultList = [];
      this.$refs.matchLabelRef.matchSelectList = [];
      this.$refs.matchExpressRef.matchSelectList = [];
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
        // width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item-number {
        display: inline-block;
        width: 34px;
        height: 16px;
        padding: 2px 0;
        margin: 0 12px;
        line-height: 12px;
        text-align: center;
        color: #979ba5;
        background: #f0f1f5;
        border-radius: 2px;
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
    height: 100%;
    display: flex;
    position: absolute;
    left: 300px;

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
      height: calc(100% - 39px);
      display: flex;
      flex-direction: column;

      > div {
        flex: 1;
      }
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

    .absoluteNameList-container {
      overflow-y: auto;
      height: 50%;
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
        min-width: 20px;
        color: #ff9c01;
        background: #fff;
        padding: 2px 6px;
        margin-right: 12px;
      }

      .match-right {
        display: inline-block;
        min-width: 36px;
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
    right: 300px;
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

    .hit-container {
      height: 500px;
      overflow-y: auto;
    }

    .hit-title {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }

    .hit-number {
      color: #3a84ff;
      cursor: pointer;
    }

    .hit-item {
      padding: 8px 12px;
      margin-bottom: 4px;
      background: #fff;
      border-radius: 2px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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

  .left-drag {
    right: 0px
  }

  .right-drag {
    left: -2px;
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

    &::after {
      content: ' ';
      height: 25px;
      width: 0;
      border-left: 3px dotted #63656e;
      position: absolute;
      left: 5px;
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

  .right-border-light {
    border-right-color: #3a84ff;
  }

  .left-border-light {
    border-left-color: #3a84ff;
  }

}
</style>
