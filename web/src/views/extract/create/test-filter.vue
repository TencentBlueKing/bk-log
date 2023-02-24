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
  <div class="text-filter-container">
    <bk-select v-model="filterType" style="width: 174px;margin-right: 20px;background-color: #fff;">
      <bk-option
        v-for="option in filterList"
        :key="option.id"
        :id="option.id"
        :name="option.name">
      </bk-option>
    </bk-select>
    <!-- 关键字过滤 -->
    <div class="filter-content" v-show="filterType === 'match_word'">
      <bk-input
        style="width: 300px;"
        :maxlength="64"
        data-test-id="addNewExtraction_input_filterKeyword"
        :placeholder="$t('多个关键字用英文逗号')"
        v-model="filterContent.keyword">
      </bk-input>
      <bk-select
        v-model="filterContent.keyword_type"
        style="width: 60px;margin-right: 10px;background-color: #fff;"
        data-test-id="addNewExtraction_select_filterCondition"
        :clearable="false">
        <bk-option
          v-for="option in keywordTypeList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
      {{ $t('关键字匹配模式') }}
    </div>
    <!-- 关键字范围 -->
    <div class="filter-content" v-show="filterType === 'match_range'">
      <i18n path="从匹配{0}开始到匹配{1}之间的所有行">
        <bk-input
          style="width: 180px;margin: 0 6px;"
          :maxlength="64"
          v-model="filterContent.start">
        </bk-input>
        <bk-input
          style="width: 180px;margin: 0 6px;"
          :maxlength="64"
          v-model="filterContent.end">
        </bk-input>
      </i18n>
    </div>
    <!-- 最新行数 -->
    <div class="filter-content" v-show="filterType === 'tail_line'">
      <bk-input
        style="width: 120px;"
        type="number"
        :placeholder="$t('请输入整数')"
        :precision="0"
        :value="filterContent.line_num"
        @change="handleChangeNumber('line_num', $event)">
      </bk-input>
    </div>
    <!-- 按行过滤 -->
    <div class="filter-content" v-show="filterType === 'line_range'">
      <i18n path="从第{0}行到第{1}行">
        <bk-input
          style="width: 120px;margin: 0 6px;"
          type="number"
          :placeholder="$t('请输入整数')"
          :precision="0"
          :value="filterContent.start_line"
          @change="handleChangeNumber('start_line', $event)">
        </bk-input>
        <bk-input
          style="width: 120px;margin: 0 6px;"
          type="number"
          :placeholder="$t('请输入整数')"
          :precision="0"
          :value="filterContent.end_line"
          @change="handleChangeNumber('end_line', $event)"
        ></bk-input>
      </i18n>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      filterType: '',
      filterList: [{
        id: 'match_word',
        name: this.$t('关键字过滤'),
      }, {
        id: 'match_range',
        name: this.$t('关键字范围'),
      }, {
        id: 'tail_line',
        name: this.$t('最新行数'),
      }, {
        id: 'line_range',
        name: this.$t('按行过滤'),
      }],
      filterContent: {
        // 关键字过滤
        keyword: '',
        keyword_type: 'keyword_and',
        // 关键字范围
        start: '',
        end: '',
        // 最新行数
        line_num: 0,
        // 按行过滤
        start_line: 0,
        end_line: 0,
      },
      keywordTypeList: [{
        id: 'keyword_and',
        name: this.$t('与'),
      }, {
        id: 'keyword_or',
        name: this.$t('或'),
      }, {
        id: 'keyword_not',
        name: this.$t('非'),
      }],
    };
  },
  methods: {
    handleClone({ filter_type: filterType, filter_content: filterContent }) {
      this.filterType = filterType;
      Object.assign(this.filterContent, filterContent);
    },
    handleChangeNumber(key, val) {
      const num = Number(val);
      if (num <= 0 && val !== '') { // 保证大于0并触发响应式数据更新
        this.filterContent[key] = -1;
        this.$nextTick(() => {
          this.filterContent[key] = 0;
        });
      } else {
        this.filterContent[key] = num;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .text-filter-container {
    display: flex;
    align-items: center;

    .filter-content {
      display: flex;
      align-items: center;
    }
  }
</style>
