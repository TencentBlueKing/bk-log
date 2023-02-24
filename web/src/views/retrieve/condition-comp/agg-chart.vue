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
  <div class="field-data">
    <div class="title">
      <i18n path="{0}/{1}条记录中数量排名前 5 的数据值">
        <span>{{statisticalFieldData.__validCount}}</span>
        <span>{{statisticalFieldData.__totalCount}}</span>
      </i18n>
    </div>
    <ul class="chart-list">
      <template v-for="(item, index) in topFiveList">
        <li class="chart-item" :key="index + Date.now()">
          <div class="chart-content">
            <div class="text-container">
              <div v-bk-overflow-tips class="text-value">{{ item[0] }}</div>
              <div class="percent-value">{{ computePercent(item[1]) }}</div>
            </div>
            <div class="percent-bar-container">
              <div class="percent-bar" :style="{ width: computePercent(item[1]) }"></div>
            </div>
          </div>
          <div class="operation-container">
            <span
              v-bk-tooltips="getIconPopover('is', item[0])"
              :class="['bk-icon icon-enlarge-line', filterIsExist('is', item[0]) ? 'disable' : '']"
              @click="addCondition('is', item[0])">
            </span>
            <span
              v-bk-tooltips="getIconPopover('is not', item[0])"
              :class="['bk-icon icon-narrow-line', filterIsExist('is not', item[0]) ? 'disable' : '']"
              @click="addCondition('is not', item[0])">
            </span>
          </div>
        </li>
      </template>
      <li class="more-item" v-if="!showAllList && shouldShowMore">
        <span @click="() => {
          showAllList = !showAllList
        }">{{$t('更多')}}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    statisticalFieldData: {
      type: Object,
      default() {
        return {};
      },
    },
    fieldName: {
      type: String,
      required: true,
    },
    fieldType: {
      type: String,
      required: true,
    },
    parentExpand: {
      type: Boolean,
      default: false,
    },
    retrieveParams: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      showAllList: false,
      shouldShowMore: false,
    };
  },
  computed: {
    topFiveList() {
      const totalList = Object.entries(this.statisticalFieldData);
      totalList.sort((a, b) => b[1] - a[1]);
      totalList.forEach((item) => {
        const markList = item[0].toString().match(/(<mark>).*?(<\/mark>)/g) || [];
        if (markList.length) {
          item[0] = markList.map(item => item.replace(/<mark>/g, '')
            .replace(/<\/mark>/g, '')).join(',');
        }
      });
      this.shouldShowMore = totalList.length > 5;
      return this.showAllList ? totalList : totalList.filter((item, index) => index < 5);
    },
  },
  watch: {
    parentExpand(val) {
      if (!val) this.showAllList = false;
    },
  },
  inject: ['addFilterCondition'],
  methods: {
    // 计算百分比
    computePercent(count) {
      return `${Math.round((count / this.statisticalFieldData.__validCount).toFixed(2) * 100)}%`;
    },
    addCondition(operator, value) {
      if (this.fieldType === '__virtual__') return;
      this.addFilterCondition(this.fieldName, operator, value);
    },
    getIconPopover(operator, value) {
      if (this.fieldType === '__virtual__') return this.$t('该字段为平台补充 不可检索');
      if (this.filterIsExist(operator, value)) return this.$t('已添加过滤条件');
      return operator;
    },
    filterIsExist(operator, value) {
      if (this.fieldType === '__virtual__') return true;
      if (this.retrieveParams?.addition.length) {
        if (operator === 'not') operator = 'is not';
        return this.retrieveParams.addition.some((addition) => {
          return addition.field === this.fieldName
        && addition.operator === operator
        && addition.value.toString() === value.toString();
        });
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
  .field-data {
    padding: 0 12px;
    // background-color: #FAFBFD;
    .title {
      padding: 8px 0 4px;
      color: #979ba5;
    }

    .disable {
      /* stylelint-disable-next-line declaration-no-important */
      color: #dcdee5 !important;
    }

    .chart-list {
      .chart-item {
        display: flex;
        align-items: center;

        .chart-content {
          width: calc(100% - 46px);

          .text-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            line-height: 20px;

            .text-value {
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .percent-value {
              flex-shrink: 0;
              color: #2dcb56;
              margin-left: 6px;
            }
          }

          .percent-bar-container {
            position: relative;
            height: 6px;
            margin-bottom: 9px;
            background-color: #dcdee5;

            .percent-bar {
              position: absolute;
              height: 6px;
              background-color: #2dcb56;
            }
          }
        }

        .operation-container {
          flex-shrink: 0;
          display: flex;
          justify-content: space-between;
          width: 36px;
          margin-left: 10px;
          transform: translateY(4px);

          .bk-icon {
            font-size: 18px;
            color: #3a84ff;
            // transform: rotate(45deg);
            cursor: pointer;

            &:active {
              color: #2761dd;
            }

            &:hover {
              color: #699df4;
            }
          }
        }
      }

      .more-item {
        margin: 4px 0 10px;

        span {
          color: #3a84ff;
          cursor: pointer;
        }
      }
    }
  }
</style>
