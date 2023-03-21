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
  <div class="match-container">
    <div class="match-title">
      <span>{{isLabel ? $t('匹配标签') : $t('匹配表达式')}}</span>
      <div class="flex-ac add-match" v-show="!isShowAdd" @click="isShowAdd = true">
        <span class="bk-icon icon-plus-circle"></span>
        <span>{{isLabel ? $t('添加标签') : $t('添加表达式')}}</span>
      </div>
    </div>
    <div v-show="isShowAdd" class="add-filling flex-ac">
      <div class="customize-box" v-if="isLabel">
        <bk-input :class="`label-input ${isKeyError && 'input-error'}`" v-model.trim="matchKey"></bk-input>
        <span>=</span>
        <bk-input :class="`label-input ${isValueError && 'input-error'}`" v-model.trim="matchValue"></bk-input>
      </div>
      <div class="customize-box" v-else>
        <bk-select
          :class="`fill-first ${isKeyError && 'select-error'}`"
          v-model.trim="matchKey"
          searchable>
          <bk-option
            v-for="item of matchExpressOption"
            :key="item.id"
            :name="item.key"
            :id="item.key">
          </bk-option>
        </bk-select>
        <bk-select
          class="fill-second"
          :clearable="false"
          v-model="matchOperator">
          <bk-option
            v-for="item of expressOperatorList"
            :key="item.id"
            :name="item.name"
            :id="item.id">
          </bk-option>
        </bk-select>
        <bk-input
          v-model.trim="matchValue"
          :class="`fill-input ${isValueError && 'input-error'}`"
          :disabled="expressInputIsDisabled"></bk-input>
      </div>
      <div class="add-operate flex-ac">
        <span class="bk-icon icon-check-line" @click="handleAddMatch"></span>
        <span class="bk-icon icon-close-line-2" @click="handleCancelMatch"></span>
      </div>
    </div>
    <div class="list-container" :style="`height: ${isShowAdd ? 170 : 202 }px`">
      <template v-if="matchList.length">
        <bk-checkbox-group v-model="matchSelectList">
          <bk-checkbox v-for="item of matchList" :key="item.id" :value="item.id">
            <div
              class="match-item justify-sb"
              @mouseenter="activeItemID = item.id"
              @mouseleave="activeItemID = -1">
              <div id="content-copy-html">
                <span class="icon log-icon icon-copy" @click="copyContent(item.key)"></span>
              </div>
              <div class="justify-sb">
                <span
                  v-bk-tooltips.light.click="{ allowHtml: true, content: '#content-copy-html' }"
                  @click.stop>
                  {{item.key}}
                </span>
                <span class="match-left">{{getOperateShow(item.operator)}}</span>
              </div>
              <div class="justify-sb">
                <span v-bk-overflow-tips>{{item.value}}</span>
                <span v-if="item.customize">
                  <span v-show="activeItemID === item.id"
                        class="bk-icon icon-close3-shape"
                        @click.stop="handleDeleteMatch(item.id)"></span>
                  <span v-show="activeItemID !== item.id" class="match-right">{{$t('自定义')}}</span>
                </span>
              </div>
            </div>
          </bk-checkbox>
        </bk-checkbox-group>
      </template>
      <div class="match-empty" v-else>
        <empty-status empty-type="empty" :show-text="false">
          <p>{{!isLabel ? $t('请添加表达式') : $t('请添加标签')}}</p>
        </empty-status>
      </div>
    </div>
  </div>
</template>
<script>
import { copyMessage, random } from '@/common/util';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    EmptyStatus,
  },
  props: {
    matchLabelOption: {
      type: Array,
      default: () => [],
    },
    matchType: {
      type: String,
      require: true,
    },
    matchObj: {
      type: Object,
      default: () => ({}),
    },
    allMatchList: {
      type: Array,
      default: () => [],
    },
    matchSelector: {
      type: Array,
      require: true,
    },
  },
  data() {
    return {
      matchList: [], // 标签总选择列表
      isShowAdd: false, // 是否展示添加操作
      matchSelectList: [], // 组件的标签用户选择ID列表
      matchCacheList: [], // 存储的用户选择或自定义的标签值列表
      matchKey: '', // 自定义匹配键名
      matchValue: '', // 自定义匹配值
      matchOperator: 'In', // 自定义匹配操作
      activeItemID: -1, // 当前鼠标hover的列表元素ID
      expressOperatorList: [{ // 表达式操作选项
        id: 'In',
        name: 'In',
      }, {
        id: 'NotIn',
        name: 'NotIn',
      },
      {
        id: 'Exists',
        name: 'Exists',
      }, {
        id: 'DoesNotExist',
        name: 'DoesNotExist',
      }],
      isKeyError: false,
      isValueError: false,
      matchExpressOption: [],
    };
  },
  computed: {
    isLabel() {
      return this.matchType === 'label';
    },
    expressInputIsDisabled() {
      return ['Exists', 'DoesNotExist'].includes(this.matchOperator);
    },
  },
  watch: {
    'matchObj.treeList': {
      handler(val) {
        this.handleSelectTreeItem(val);
      },
    },
    matchKey() {
      return this.isKeyError = false;
    },
    matchValue() {
      return this.isValueError = false;
    },
    matchList: { // 获取label的key数组为表达式下拉框选项赋值
      deep: true,
      handler(val) {
        if (this.isLabel) {
          const setList = new Set();
          const filterList = val.filter(item => !setList.has(item.key) && setList.add(item.key));
          this.$emit('update:all-match-list',  filterList);
        }
      },
    },
    matchLabelOption: {
      deep: true,
      handler(val) {
        if (!this.isLabel) {
          const setList = new Set();
          const allMatchVal = this.matchList.concat(val);
          this.matchExpressOption = allMatchVal.filter(item => !setList.has(item.key) && setList.add(item.key));
        }
      },
    },
    matchSelectList(val) {
      const selectList = [];
      this.matchList.forEach((item) => {
        if (val.includes(item.id)) {
          selectList.push({ key: item.key, value: item.value, operator: item.operator });
        }
      });
      this.$emit('update:matchObj',  Object.assign(this.matchObj, { selectList }));
    },
  },
  created() {
    this.initMatch();
  },
  methods: {
    handleDeleteMatch(id) {
      // 删除自定义时  应该把列表，缓存列表，选择ID列表都删除对应元素
      this.spliceListElement(this.matchList, item => item.id === id);
      this.spliceListElement(this.matchCacheList, item => item.id === id);
      this.spliceListElement(this.matchSelectList, item => item === id);
    },
    /**
     * @desc: 删除操作删除对应的元素值
     * @param { Array } list 操作的列表
     * @param { Function } callback 找到下标的回调函数
     */
    spliceListElement(list, callback) {
      const index = list.findIndex(callback);
      if (index >= 0) list.splice(index, 1);
    },
    /**
     * @desc: 切换不同的树的值时过滤展示标签和表达式
     * @param treeList 树的值列表
     */
    handleSelectTreeItem(treeList) {
      const treeIdList = treeList.map(item => ({ ...item, id: random(10) })) || [];
      // 当前列表为空时 直接赋值树列表
      if (!this.matchList.length) {
        this.matchList = treeIdList;
      } else {
        const notCustomSelectList = []; // 非自定义选择的列表
        const customSelectList = []; // 选择的自定义列表
        const customList = []; // 没选择的自定义列表
        // 按照选择的标签  选择的自定义标签  未选择的自定义标签顺序排序
        this.matchList.forEach((item) => {
          const isSelect = this.matchSelectList.includes(item.id);
          if (!item.customize && isSelect) {
            notCustomSelectList.push(item);
          } else if (item.customize && isSelect) {
            customSelectList.push(item);
          } else if (item.customize && !isSelect) {
            customList.push(item);
          }
        });
        this.matchCacheList = notCustomSelectList.concat(customSelectList, customList);
        // 切换不同的列表时与当前自定义，选择的列表进行去重
        const filterList = this.comparedListItem(treeIdList, this.matchCacheList);
        this.matchList = this.matchCacheList.concat(filterList);
      }
    },
    handleAddMatch() {
      if (!this.expressInputIsDisabled) {
        // key value 不能为空
        if (!this.matchKey || !this.matchValue) {
          !this.matchKey && (this.isKeyError = true);
          !this.matchValue && (this.isValueError = true);
          return;
        }
      } else {
        // 输入框禁止的时候 value可以为空
        if (!this.matchKey) {
          !this.matchKey && (this.isKeyError = true);
          return;
        }
      }
      // 是否有重复
      const isRepeat = this.matchList.some((item) => {
        return this.matchKey === item.key
        && this.matchValue === item.value
        && (this.isLabel ? true : this.matchOperator === item.operator);
      });
      if (!isRepeat) {
        this.matchList.unshift({
          key: this.matchKey,
          // 输入框禁止 value为空字符串
          value: this.expressInputIsDisabled ? '' : this.matchValue,
          // 匹配标签 操作则永远是等号
          operator: this.isLabel ? '=' : this.matchOperator,
          customize: true,
          id: random(10),
        });
      }
      this.handleCancelMatch();
    },
    handleCancelMatch() {
      this.matchKey = '';
      this.matchValue = '';
      this.isKeyError = false;
      this.isValueError = false;
      this.isShowAdd = false;
      this.matchOperator = 'In';
    },
    /**
     * @desc: 判断两个list键 值 操作是否都相同
     * @param firstList 树的值列表
     * @param secondList 选中或自定义列表
     * @returns 返回有一种或多种不同的数组
     */
    comparedListItem(firstList = [], secondList = []) {
      return firstList.filter((fItem) => {
        return !secondList.find((sItem) => {
          const { key: fKey, value: fValue, operator: fOperator } = fItem;
          const { key: sKey, value: sValue, operator: sOperator } = sItem;
          return fKey === sKey && fValue === sValue && fOperator === sOperator;
        });
      });
    },
    getOperateShow(operate) {
      return this.expressOperatorList.find(item => item.id === operate)?.name || '=';
    },
    copyContent(text) {
      copyMessage(text);
    },
    initMatch() {
      let initMatchList;
      if (this.matchType === 'express') { // 表达式的所有值都赋值为自定义
        initMatchList = this.matchSelector.map(item => ({ ...item, id: random(10), customize: true }));
      } else {
        initMatchList = this.matchSelector.map(item => ({ ...item, id: random(10) }));
      }
      this.matchList.push(...initMatchList);
      this.matchSelectList.push(...initMatchList.map(item => item.id));
    },
  },
};
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';

.customize-box {
  width: 100%;
  display: flex;
  align-items: center;

  > span {
    color: #ff9c01;
    padding: 0 8px;
  }
}

.list-container {
  overflow-y: auto;
}

.match-empty {
  min-height: 202px;
  flex-direction: column;

  @include flex-center();

  .icon-empty {
    color: #c3cdd7;
    font-size: 50px;
  }
}

#content-copy-html {
  height: 20px;
  display: flex;
  align-items: center;
  font-size: 20px;
  cursor: pointer;

  .icon-copy {
    display: inline-block;
  }
}

.flex-ac {
  @include flex-align();
}

.justify-sb {
  @include flex-justify(space-between);

  > span:first-child {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding-right: 4px;
  }
}

.select-error {
  border-color: #ff5656;
}

:deep(.input-error .bk-form-input) {
  border-color: #ff5656;
}

</style>
