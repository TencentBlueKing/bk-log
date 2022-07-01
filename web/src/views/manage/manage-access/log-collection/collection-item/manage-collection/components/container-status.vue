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
  <div class="container-status-container">
    <div class="nav-section">
      <div class="nav-btn-box">
        <div v-for="item in navBtnList"
             :key="item.id"
             :class="`nav-btn ${item.id === navActive ? 'active' : ''}`">
          <span
            v-if="item.id !== 'all'"
            :class="['circle', item.id === 'execution' ? 'rotate-icon' : 'nav-icon', item.class]"
            v-bkloading="{
              isLoading: item.id === 'execution',
              opacity: 1,
              zIndex: 10,
              theme: 'primary',
              mode: 'spin',
              size: 'small'
            }"></span>
          <span>{{item.name}} {{item.dataList.length}}</span>
        </div>
      </div>
      <bk-button>
        {{$t('复制目标')}}
      </bk-button>
    </div>
    <div class="table-section">
      <div v-for="(renderItem, renderIndex) in renderTitleList" :key="renderIndex" class="table-item">
        <div :class="`table-title ${renderItem.isShowTable ? '' : 'close-table'}`"
             @click="handleClickTitle(renderIndex, renderItem.isShowTable)">
          <span class="bk-icon icon-down-shape"></span>
          <span>这是一个table</span>
        </div>
        <div class="table-main" v-show="renderItem.isShowTable">
          <bk-table :data="[]" size="small">
            <bk-table-column label=""></bk-table-column>
            <bk-table-column label=""></bk-table-column>
            <bk-table-column label=""></bk-table-column>
          </bk-table>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      navActive: 'all', // 当前活跃按钮
      navBtnList: [ // 按钮列表
        {
          id: 'all',
          name: this.$t('configDetails.all'),
          class: '',
          dataList: [],
        },
        {
          id: 'success',
          name: this.$t('configDetails.succeed'),
          class: 'circle-green',
          dataList: [],
        },
        {
          id: 'failed',
          name: this.$t('configDetails.failed'),
          class: 'circle-red',
          dataList: [],
        },
        {
          id: 'execution',
          name: this.$t('configDetails.Pending'),
          class: '',
          dataList: [],
        },
      ],
      renderTitleList: [], // 当前活跃的目标
      renderList: {},
    };
  },
  methods: {
    handleClickTitle(index, isClose) {
      this.renderTitleList[index].isShowTable = !isClose;
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.container-status-container {
  .nav-section {
    @include flex-justify(space-between);

    .nav-btn-box {
      min-width: 327px;
      height: 36px;
      padding: 5px 4px;
      background: #f0f1f5;
      border-radius: 4px;
      align-items: center;
      font-size: 14px;

      @include flex-justify(space-between);

      .nav-btn {
        position: relative;
        padding: 4px 15px;
        border-radius: 4px;
        color: #63656e;

        &:not(:last-child)::after {
          content: '|';
          position: absolute;
          color: #dcdee5;
          top: 3px;
          right: -8px;
        }

        &:not(:first-child) {
          margin-left: 12px;
        }

        &:last-child {
          padding-left: 27px;
        }

        &:hover {
          background: #fff;
          cursor: pointer;
        }

        &.active {
          color: #3a84ff;
          background: #fff;
        }
      }

      .nav-icon {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;

        &.circle {
          &::after {
            content: ' ';
            width: 16px;
            height: 16px;
            display: inline-block;
            position: absolute;
            border-radius: 50%;
            top: -3px;
            left: -3px;
          }
        }

        &.circle-green {
          background: #3fc06d;

          &::after {
            background: rgba(63,192,109,.16);
          }
        }

        &.circle-red {
          background: #ea3636;

          &::after {
            background: rgba(234,54,54,.16);
          }
        }
      }

      .rotate-icon {
        position: absolute;
        top: -4px;
        left: -4px;
        display: inline-block;
        transform: scale(.6);
      }
    }
  }

  .table-section {
    .table-item {
      margin-top: 20px;

      .table-title {
        padding: 10px 23px;
        font-size: 12px;
        background: #f0f1f5;
        border: 1px solid #dcdee5;
        border-bottom: none;
        cursor: pointer;

        > span {
          &:first-child {
            font-size: 14px;
          }

          &:nth-child(2) {
            color: #63656e;
            font-weight: 700;
          }
        }

        .icon-down-shape {
          display: inline-block;
          transform: translateY(-1px);
        }

        &.close-table {
          border-bottom: 1px solid #dcdee5;

          .icon-down-shape {
            transform: rotateZ(-90deg) translateX(1px);
          }
        }
      }
    }
  }
}
</style>
