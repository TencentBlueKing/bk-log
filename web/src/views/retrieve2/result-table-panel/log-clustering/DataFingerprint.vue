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
  <div>
    <bk-table
      class="log-cluster-table"
      :data="fingerList"
      @row-mouse-enter="showEditIcon"
      @row-mouse-leave="hiddenEditIcon">
      <bk-table-column :label="$t('数据指纹')" width="150">
        <template slot-scope="props">
          <div class="flac">
            <span class="signature">{{props.row.signature}}</span>
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
          {{`${props.row.percentage.toFixed(4)}%`}}
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
              <span :class="['bk-icon',showArrowsClass(props.row)]"></span>
            </div>
          </template>
        </bk-table-column>
      </template>

      <bk-table-column label="Pattern" min-width="400">
        <template slot-scope="props">
          <ClusterEventPopver
            :is-search="false"
            @eventClick="(option) => handleMenuClick(option,props.row)">
            {{props.row.pattern}}
          </ClusterEventPopver>
        </template>
      </bk-table-column>

      <!-- <bk-table-column :label="$t('告警')" width="103">
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

    <bk-table-column :label="$t('备注')" width="100" prop="remark"></bk-table-column> -->

      <div slot="empty" v-if="isPermission && !configData.extra.signature_switch">
        <div class="empty-text">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('goFingerMessage')}}</p>
          <span class="empty-leave" @click="handleLeaveCurrent">
            {{$t('去设置')}}
          </span>
        </div>
      </div>
      <div slot="empty" v-if="fingerList.length === 0 && configData.extra.signature_switch">
        <div class="empty-text">
          <span class="bk-table-empty-icon bk-icon icon-empty"></span>
          <p>{{$t('暂无数据')}}</p>
        </div>
      </div>
    </bk-table>
  </div>
</template>

<script>
import ClusterEventPopver from './ClusterEventPopver';
export default {
  components: {
    ClusterEventPopver,
  },
  props: {
    fingerList: {
      type: Array,
      require: true,
    },
    yearOnYearCycle: {
      type: Number,
      require: true,
    },
    isPermission: {
      type: Boolean,
      require: true,
    },
    partterLevel: {
      type: String,
      default: '09',
    },
    configData: {
      type: Object,
      require: true,
    },
  },
  data() {
    return {
      currentHover: '',
    };
  },
  inject: ['addFilterCondition'],
  mounted() {
  },
  methods: {
    handleMenuClick(option, row) {
      switch (option) {
        case 'show original':
          this.addFilterCondition(`dist_${this.partterLevel}`, 'is', row.signature.toString());
          this.$emit('showOriginLog');
          break;
        case 'copy':
          try {
            const input = document.createElement('input');
            input.setAttribute('value', row.pattern);
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            this.messageSuccess(this.$t('复制成功'));
          } catch (e) {
            console.warn(e);
          }
          break;
      }
    },
    showArrowsClass(row) {
      if (row.year_on_year_percentage === 0) return '';
      return row.year_on_year_percentage < 0 ? 'icon-arrows-down' : 'icon-arrows-up';
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

.compared-change {
  height: 24px;
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
  .signature{
    // display: inline-block;
    width: 95px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 20px;
    max-height: 16px;
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
  margin: 4px 0 0 3px;
  text-align: center;
  color: #ea3636;
  background: #ffdddd;
  border: 1px solid #fd9c9c;
  border-radius: 9px;
}

// .pattern-icons {
//   width: 60px;
//   position: relative;
//   .bk-icon {
//     margin-right: 6px;
//   }
//   .icon-eye{
//     font-size: 14px !important;
//     cursor: pointer;
//   }
//   .icon-chart{
//     font-size: 12px !important;
//     cursor: pointer;
//   }
//   .icon-copy {
//     font-size: 26px;
//     position: absolute;
//     right: -8px;
//     top: -4px;
//     cursor: pointer;
//   }
// }

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
