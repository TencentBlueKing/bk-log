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
  <div class="finger-container">
    <div class="top-operate">
      <p class="operate-message">当前已选择 <span>3</span> 条数据，共有134条数据</p>
      <span class="operate-click">批量使用告警</span>
    </div>
    <bk-table
      data-test-id="cluster_div_fingerTable"
      type="selection"
      :class="['finger-cluster-table','table-no-data']"
      :data="fingerList"
      :outer-border="false"
      @row-mouse-enter="showEditIcon"
      @row-mouse-leave="hiddenEditIcon">
      <bk-table-column type="selection" width="40"></bk-table-column>
      <bk-table-column :label="$t('数据指纹')" width="150">
        <template slot-scope="props">
          <div class="fl-ac">
            <span class="signature">{{props.row.signature}}</span>
            <div v-show="props.row.is_new_class" class="new-finger">New</div>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('数量')" sortable width="91" prop="number">
        <template slot-scope="props">
          <span
            class="link-color"
            @click="handleMenuClick('show original',props.row)">
            {{props.row.count}}</span>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('占比')" sortable width="96" prop="source">
        <template slot-scope="props">
          <span class="link-color" @click="handleMenuClick('show original',props.row)">
            {{`${props.row.percentage.toFixed(2)}%`}}
          </span>
        </template>
      </bk-table-column>

      <template v-if="requestData.year_on_year_hour >= 1 ">
        <bk-table-column
          width="101" align="center" header-align="center" prop="source"
          :label="$t('同比数量')"
          sortable
          :sort-by="'year_on_year_count'">
          <template slot-scope="props">
            <span>{{props.row.year_on_year_count}}</span>
          </template>
        </bk-table-column>

        <bk-table-column
          width="101" align="center" header-align="center" prop="source"
          :label="$t('同比变化')"
          sortable
          :sort-by="'year_on_year_percentage'">
          <template slot-scope="props">
            <div class="fl-ac compared-change">
              <span>{{`${props.row.year_on_year_percentage.toFixed(0)}%`}}</span>
              <span :class="['bk-icon',showArrowsClass(props.row)]"></span>
            </div>
          </template>
        </bk-table-column>
      </template>

      <bk-table-column label="Pattern" min-width="350" class-name="symbol-column">
        <!-- eslint-disable-next-line -->
        <template slot-scope="{ row, column, $index }">
          <register-column :context="row.pattern">
            <div :class="['pattern-content', { 'is-limit': !cacheExpandStr.includes($index) }]">
              <cluster-event-popover
                :context="row.pattern"
                @eventClick="(option) => handleMenuClick(option,row)">
                <span>{{row.pattern ? row.pattern : $t('未匹配')}}</span>
              </cluster-event-popover>
              <p
                v-if="!cacheExpandStr.includes($index)"
                class="show-whole-btn"
                @click.stop="handleShowWhole($index)">
                {{ $t('展开全部') }}
              </p>
              <p
                v-else
                class="hide-whole-btn"
                @click.stop="handleHideWhole($index)">
                {{ $t('收起') }}
              </p>
            </div>
          </register-column>
        </template>
      </bk-table-column>

      <bk-table-column label="分组" width="100" prop="remark"></bk-table-column> -->

      <bk-table-column :label="$t('告警')" width="103" class-name="symbol-column">
        <template slot-scope="props">
          <div class="fl-ac" style="margin-top: 2px;">
            <bk-switcher v-model="props.row.a" theme="primary"></bk-switcher>
            <bk-popover content="可去告警策略编辑" :delay="300">
              <span
                class="bk-icon icon-edit2 link-color"
                :style="`visibility:${props.$index === currentHover ? 'unset' : 'hidden'}`"></span>
            </bk-popover>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('标签')" min-width="105" align="center" header-align="center">
        <template slot-scope="props">
          <div class="fl-ac">
            <bk-tag v-for="(item,index) of props.row.labels" :key="index">{{item}}</bk-tag>
          </div>
        </template>
      </bk-table-column>

      <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column>

      <div slot="empty">
        <div class="empty-text" v-if="clusterSwitch && !configData.extra.signature_switch">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('goFingerMessage')}}</p>
          <span class="empty-leave" @click="handleLeaveCurrent">{{$t('去设置')}}</span>
        </div>
        <div class="empty-text" v-if="fingerList.length === 0 && configData.extra.signature_switch">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('暂无数据')}}</p>
        </div>
      </div>
    </bk-table>
  </div>
</template>

<script>
import ClusterEventPopover from './components/ClusterEventPopover';
import RegisterColumn from '../../result-comp/RegisterColumn';
import { copyMessage } from '@/common/util';
export default {
  components: {
    ClusterEventPopover,
    RegisterColumn,
  },
  props: {
    fingerList: {
      type: Array,
      require: true,
    },
    clusterSwitch: {
      type: Boolean,
      require: true,
    },
    requestData: {
      type: Object,
      require: true,
    },
    configData: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      currentHover: '',
      cacheExpandStr: [],
    };
  },
  inject: ['addFilterCondition'],
  methods: {
    handleMenuClick(option, row) {
      switch (option) {
        case 'show original':
          this.addFilterCondition(`__dist_${this.requestData.pattern_level}`, 'is', row.signature.toString());
          this.$emit('showOriginLog');
          break;
        case 'copy':
          copyMessage(row.pattern);
          break;
      }
    },
    showArrowsClass(row) {
      if (row.year_on_year_percentage === 0) return '';
      return row.year_on_year_percentage < 0 ? 'icon-arrows-down' : 'icon-arrows-up';
    },
    handleShowWhole(index) {
      this.cacheExpandStr.push(index);
    },
    handleHideWhole(index) {
      this.cacheExpandStr = this.cacheExpandStr.map(item => item !== index);
    },
    handleLeaveCurrent() {
      this.$emit('showSettingLog');
    },
    showEditIcon(index) {
      this.currentHover = index;
    },
    hiddenEditIcon() {
      this.currentHover = '';
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/scss/mixins/flex.scss";

.finger-container {
  position: relative;
  .top-operate{
    position: absolute;
    top: 42px;
    z-index: 99;
    width: 100%;
    height: 32px;
    font-size: 12px;
    background: #F0F1F5;
    border-top: 1px solid #dfe0e5;
    border-bottom: 1px solid #dfe0e5;
    @include flex-center;
    .operate-message{
      margin: -2px 8px 0 0;
      color: #63656E;
      span {
        font-size: 14px;
        font-weight: 700;
      }
    }
    .operate-click{
      color: #3a84ff;
      cursor: pointer;
    }
  }
  .finger-cluster-table {
    /deep/ .bk-table-body-wrapper {
      margin-top: 32px;
      min-height: calc(100vh - 570px);
      .bk-table-empty-block {
        min-height: calc(100vh - 570px);
        @include flex-center;
      }
    }
    &:before {
      display: none;
    }
    /deep/.bk-table-row-last {
      td {
        border: none;
      }
    }
    .signature {
      width: 95px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      line-height: 24px;
    }
    .compared-change {
      height: 24px;
      width: 100%;
      justify-content: center;
    }
    .empty-text {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      .bk-icon {
        font-size: 65px;
      }
      .empty-leave {
        color: #3a84ff;
        margin-top: 8px;
        cursor: pointer;
      }
    }
    .pattern-content {
      display: inline-block;
      padding-right: 15px;
      position: relative;
      padding-top: 4px;
      overflow: hidden;
      &.is-limit {
        max-height: 96px;
      }
    }
    .show-whole-btn {
      position: absolute;
      top: 80px;
      width: 100%;
      height: 24px;
      color: #3a84ff;
      font-size: 12px;
      cursor: pointer;
    }
    .hide-whole-btn {
      line-height: 14px;
      margin-top: 2px;
      color: #3a84ff;
      cursor: pointer;
    }
  }
}
.table-no-data {
  /deep/.bk-table-header-wrapper {
    tr {
      > th {
        border-bottom: none !important;
      }
    }
  }
}
.new-finger {
  width: 40px;
  height: 16px;
  font-size: 12px;
  line-height: 14px;
  text-align: center;
  color: #ea3636;
  background: #ffeeee;
  border: 1px solid #fd9c9c;
  border-radius: 9px;
}
.link-color {
  color: #3a84ff;
  cursor: pointer;
}
.icon-arrows-down {
  color: #2dcb56;
}
.icon-arrows-up {
  color: #ff5656;
}
.fl-ac {
  margin-top: -4px;
  @include flex-align;
}
.bk-icon {
  font-size: 24px;
}
</style>
