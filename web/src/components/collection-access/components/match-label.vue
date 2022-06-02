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
      <div class="flex-ac add-match" @click="isShowAdd = true">
        <span class="bk-icon icon-plus-circle"></span>
        <span>{{isLabel ? $t('添加标签') : $t('添加表达式')}}</span>
      </div>
    </div>
    <div v-show="isShowAdd" class="add-filling flex-ac">
      <div class="customize-box" v-if="isLabel">
        <bk-input :class="`label-input ${isKeyError && 'input-error'}`" v-model="matchKey"></bk-input>
        <span>=</span>
        <bk-input :class="`label-input ${isValueError && 'input-error'}`" v-model="matchValue"></bk-input>
      </div>
      <div class="customize-box" v-else>
        <bk-select :class="`fill-first ${isKeyError && 'select-error'}`" v-model="matchKey"></bk-select>
        <bk-select class="fill-second" :clearable="false" v-model="matchOperator"></bk-select>
        <bk-input :class="`fill-input ${isValueError && 'input-error'}`" v-model="matchValue"></bk-input>
      </div>
      <div class="add-operate flex-ac">
        <span class="bk-icon icon-check-line" @click="handleAddMatch"></span>
        <span class="bk-icon icon-close-line-2" @click="handleCancelMatch"></span>
      </div>
    </div>
    <div class="list-container" :style="`height: ${isShowAdd ? 140 : 172 }px`">
      <template v-if="matchList.length">
        <bk-checkbox-group v-model="matchSelectList">
          <bk-checkbox v-for="item of matchList" :key="item.id" :value="item.id">
            <div class="match-item justify-sb"
                 @mouseenter="activeItemID = item.id"
                 @mouseleave="activeItemID = -1">
              <div id="content-copy-html">
                <span class="icon log-icon icon-copy" @click="copyContent(item.name)"></span>
              </div>
              <div class="justify-sb">
                <span
                  v-bk-tooltips.light.click="{ allowHtml: true, content: '#content-copy-html' }"
                  @click.stop>
                  {{item.key}}
                </span>
                <span class="match-left">{{item.operator}}</span>
              </div>
              <div class="justify-sb">
                <span>{{item.value}}</span>
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
        <span class="bk-table-empty-icon bk-icon icon-empty"></span>
        <p>{{$t('暂无数据')}}</p>
      </div>
    </div>
  </div>
</template>
<script>
import { deepClone } from '../../monitor-echarts/utils';
import { copyMessage, random } from '@/common/util';

export default {
  props: {
    matchObj: {
      type: Object,
      default: () => ({}),
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
      isKeyError: false,
      isValueError: false,
      matchOperator: '=', // 自定义匹配操作
      activeItemID: -1, // 当前鼠标hover的列表元素ID
      initMatchList: [],
    };
  },
  computed: {
    isLabel() {
      return this.matchObj.matchType === 'label';
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
    matchSelectList(val) {
      const selectList = [];
      this.matchList.forEach((item) => {
        if (val.includes(item.id)) {
          selectList.push({ key: item.key, value: item.value, operator: item.operator });
        }
      });
      const emitObj = Object.assign(this.matchObj, { selectList });
      this.$emit('update:matchObj', emitObj);
    },
  },
  created() {
    this.initMatch();
  },
  methods: {
    handleDeleteMatch(id) {
      this.matchList.splice(this.matchList.findIndex(item => item.id === id), 1);
      this.matchCacheList.splice(this.matchCacheList.findIndex(item => item.id === id), 1);
      this.matchSelectList.splice(this.matchSelectList.findIndex(item => item === id), 1);
    },
    /**
     * @desc: 切换不同的树的值时过滤展示标签和表达式
     * @param treeList 树的值列表
     */
    handleSelectTreeItem(treeList) {
      // 当前列表为空时 直接赋值树列表
      if (!this.matchList.length) {
        this.matchList = deepClone(treeList || []);
      } else {
        this.matchCacheList = this.matchList.filter((item) => {
          return (item.customize === true || this.matchSelectList.includes(item.id));
        });
        const filterList = this.comparedListItem(treeList, this.matchCacheList);
        this.matchList = this.matchCacheList.concat(filterList);
      }
    },
    handleAddMatch() {
      if (!this.matchKey.trim() || !this.matchValue.trim()) {
        !this.matchKey.trim() && (this.isKeyError = true);
        !this.matchValue.trim() && (this.isValueError = true);
        return;
      }
      const isRepeat = this.matchList.some((item) => {
        return this.matchKey === item.key && this.matchValue === item.value && this.matchOperator === item.operator;
      });
      const id = new Date().getTime();
      if (!isRepeat) {
        this.matchList.unshift({
          key: this.matchKey, value: this.matchValue, operator: this.matchOperator, customize: true, id,
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
    copyContent(text) {
      copyMessage(text);
    },
    initMatch() {
      this.initMatchList = this.matchSelector.map(item => ({ ...item, id: random(10) }));
      this.matchList.push(...this.initMatchList);
      this.matchSelectList.push(...this.initMatchList.map(item => item.id));
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

.match-empty {
  min-height: 140px;
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
}

.select-error {
  border-color: #ff5656;
}

::v-deep .input-error .bk-form-input {
  border-color: #ff5656;
}

</style>
