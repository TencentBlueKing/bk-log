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
  <bk-table
    :data="fingerList"
    class="log-cluster-table"
    v-bkloading="{ isLoading: tableLoading }"
    @row-mouse-enter="showEditIcon"
    @row-mouse-leave="hiddenEditIcon">
    <bk-table-column :label="$t('数据指纹')" width="110">
      <template slot-scope="props">
        <div class="flac">
          <span>{{props.row.signature}}</span>
          <div v-if="props.row.is_new_class" class="new-finger">New</div>
        </div>
      </template>
    </bk-table-column>

    <bk-table-column :label="$t('数量')" :sortable="true" width="91" prop="number">
      <template slot-scope="props">
        <span class="link-color">{{props.row.count}}</span>
      </template>
    </bk-table-column>

    <bk-table-column :label="$t('占比')" :sortable="true" width="91" prop="source">
      <template slot-scope="props">
        {{`${props.row.percentage}%`}}
      </template>
    </bk-table-column>

    <template v-if="yearOnYearCycle >= 1 ">
      <bk-table-column
        width="101" align="center" header-align="center" prop="source"
        :label="$t('同比数量')"
        :sortable="true">
        <template slot-scope="props">
          <span class="link-color">{{props.row.year_on_year_count}}</span>
        </template>
      </bk-table-column>

      <bk-table-column
        width="101" align="center" header-align="center" prop="source"
        :label="$t('同比变化')"
        :sortable="true">
        <template slot-scope="props">
          <div class="flac compared-change">
            <span class="link-color">{{`${props.row.year_on_year_percentage}%`}}</span>
            <span :class="['bk-icon', props.row.source < 0 ? 'icon-arrows-down' : 'icon-arrows-up']"></span>
          </div>
        </template>
      </bk-table-column>
    </template>

    <bk-table-column label="Pattern" min-width="400">
      <template slot-scope="props">
        <bk-popover placement="bottom" ext-cls="pattern" theme="light" :delay="300">
          <span style="cursor: pointer;">{{props.row.pattern}}</span>
          <div slot="content" class="pattern-icons">
            <span class="bk-icon icon-eye"></span>
            <span class="log-icon icon-chart"></span>
            <span class="log-icon icon-copy" @click="handleCopyPatter(props.row.pattern)"></span>
          </div>
        </bk-popover>
      </template>
    </bk-table-column>

    <bk-table-column :label="$t('告警')" width="103">
      <template slot-scope="props">
        <div class="flac">
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

    <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column>

    <div slot="empty">
      <div class="empty-text">
        <span class="bk-table-empty-icon bk-icon icon-empty"></span>
        <p>{{$t('goCleanMessage')}}</p>
        <span class="empty-leave">{{$t('跳转到日志清洗')}}</span>
      </div>
    </div>
  </bk-table>
</template>

<script>
export default {
  props: {
    fingerList: {
      type: Array,
      require: true,
    },
    yearOnYearCycle: {
      type: Number,
      require: true,
    },
    tableLoading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      currentHover: '',
    };
  },
  methods: {
    handleCopyPatter(value) {
      try {
        const input = document.createElement('input');
        input.setAttribute('value', value);
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        this.messageSuccess(this.$t('复制成功'));
      } catch (e) {
        console.warn(e);
      }
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

.compared-change {
  margin-left: 12px;
}

.log-cluster-table {
  /deep/ .bk-table-body-wrapper {
    min-height: calc(100vh - 600px);

    .bk-table-empty-block {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: calc(100vh - 600px);
    }
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
}

.new-finger {
  width: 36px;
  height: 16px;
  font-size: 12px;
  line-height: 14px;
  margin-left: 3px;
  text-align: center;
  color: #ea3636;
  background: #ffdddd;
  border: 1px solid #fd9c9c;
  border-radius: 9px;
}

.pattern-icons {
  width: 60px;
  // display: flex;
  position: relative;
  .bk-icon {
    margin-right: 6px;
  }
  .icon-eye{
    font-size: 14px !important;
    cursor: pointer;
  }
  .icon-chart{
    font-size: 12px !important;
    cursor: pointer;
  }
  .icon-copy {
    font-size: 26px;
    position: absolute;
    right: -8px;
    top: -4px;
    cursor: pointer;
  }
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
  @include flex-align;
}

.bk-icon {
  font-size: 24px;
}

</style>
