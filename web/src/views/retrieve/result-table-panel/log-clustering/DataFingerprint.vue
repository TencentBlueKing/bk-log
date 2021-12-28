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
    <bk-table
      data-test-id="cluster_div_fingerTable"
      :class="['log-cluster-table',fingerList.length === 0 ? 'table-no-data' : '']"
      :data="fingerList"
      :outer-border="false"
      @row-mouse-enter="showEditIcon"
      @row-mouse-leave="hiddenEditIcon">
      <bk-table-column :label="$t('数据指纹')" width="150">
        <template slot-scope="props">
          <div class="flac">
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
            <div class="flac compared-change">
              <span>{{`${props.row.year_on_year_percentage.toFixed(0)}%`}}</span>
              <span :class="['bk-icon',showArrowsClass(props.row)]"></span>
            </div>
          </template>
        </bk-table-column>
      </template>

      <bk-table-column label="Pattern" min-width="500" class-name="symbol-column">
        <!-- eslint-disable-next-line -->
        <template slot-scope="{ row, column, $index }">
          <div :class="['pattern-content', { 'is-limit': !cacheExpandStr.includes($index) }]">
            <cluster-event-popover
              :context="row.pattern"
              :tippy-options="{ offset: '0, 10', boundary: scrollContent }"
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
        </template>
      </bk-table-column>

      <!-- <bk-table-column :label="$t('告警')" width="103">
      <template slot-scope="props">
        <div class="">
          <bk-switcher v-model="props.row.a" theme="primary"></bk-switcher>
          <bk-popover content="可去告警策略编辑" :delay="300">
            <span
              class="bk-icon icon-edit2 link-color"
              :style="`visibility:${props.$index === currentHover ? 'unset' : 'hidden'}`"></span>
          </bk-popover>
        </div>
      </template>
    </bk-table-column>

    <bk-table-column :label="$t('标签')" width="135" align="center" header-align="center">
      <template slot-scope="props">
        <bk-tag v-for="(item,index) of props.row.labels" :key="index">{{item}}</bk-tag>
      </template>
    </bk-table-column>

    <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column> -->

      <template slot="append" v-if="fingerList.length && isPageOver">
        <clustering-loader :width-list="loaderWidthList" />
      </template>

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
import ClusteringLoader from '@/skeleton/clustering-loader';
import { copyMessage } from '@/common/util';
export default {
  components: {
    ClusterEventPopover,
    ClusteringLoader,
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
    loaderWidthList: {
      type: Array,
      default: [''],
    },
    isPageOver: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      currentHover: '',
      cacheExpandStr: [],
    };
  },
  inject: ['addFilterCondition'],
  computed: {
    scrollContent() {
      return document.querySelector('.result-scroll-container');
    },
  },
  mounted() {
    this.scrollEvent('add');
  },
  beforeDestroy() {
    this.scrollEvent('close');
  },
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
    scrollEvent(state = 'add') {
      const scrollEl = document.querySelector('.result-scroll-container');
      if (!scrollEl) return;
      if (state === 'add') {
        scrollEl.addEventListener('scroll', this.handleScroll, { passive: true });
      }
      if (state === 'close') {
        scrollEl.removeEventListener('scroll', this.handleScroll, { passive: true });
      }
    },
    handleScroll() {
      if (this.throttle) {
        return;
      }

      const el = document.querySelector('.result-scroll-container');
      if (el.scrollHeight - el.offsetHeight - el.scrollTop < 5) {
        this.throttle = true;
        setTimeout(() => {
          el.scrollTop = el.scrollTop - 5;
          this.throttle = false;
          this.$emit('paginationOptions');
        }, 100);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/scss/mixins/flex.scss";
.compared-change {
  height: 24px;
  width: 100%;
  justify-content: center;
}
.log-cluster-table {
  /deep/ .bk-table-body-wrapper {
    min-height: calc(100vh - 550px);
    .bk-table-empty-block {
      min-height: calc(100vh - 550px);
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
  .signature{
    width: 95px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 24px;
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
    color: #3A84FF;
    font-size: 12px;
    background: #fff;
    cursor: pointer;
    transition: background-color .25s ease;
  }
  .hide-whole-btn {
    line-height: 14px;
    margin-top: 2px;
    color: #3A84FF;
    cursor: pointer;
  }
}
.table-no-data{
  /deep/.bk-table-header-wrapper{
    tr{
      >th{
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
  color: #EA3636;
  background: #FFEEEE;
  border: 1px solid #FD9C9C;
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
.flac {
  margin-top: -4px;
  @include flex-align;
}
.bk-icon {
  font-size: 24px;
}
</style>
