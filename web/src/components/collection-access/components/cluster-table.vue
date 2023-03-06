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
  <div class="cluster-container">
    <div class="cluster-title">
      <div :class="['cluster-title-container' ,!isShowTable && 'is-active']"
           @click="isShowTable = !isShowTable">
        <span class="bk-icon icon-angle-up-fill"></span>
        <p>{{ tableShowType ? $t("共享集群") : $t('业务独享集群')}}</p>
      </div>
    </div>
    <div class="cluster-main" v-show="isShowTable">
      <template v-if="tableList.length">
        <bk-table
          class="cluster-table"
          :data="tableList"
          :max-height="254"
          @row-click="handleSelectCluster">
          <bk-table-column :label="$t('集群名')" min-width="240">
            <template slot-scope="{ row }">
              <bk-radio :checked="clusterSelect === row.storage_cluster_id">
                <div class="overflow-tips" v-bk-overflow-tips>
                  <span @click.stop>{{ row.storage_cluster_name }}</span>
                </div>
              </bk-radio>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('总量')" min-width="100">
            <template slot-scope="{ row }">
              <span>{{formatFileSize(row.storage_total)}}</span>
            </template>
          </bk-table-column>
          <bk-table-column min-width="110" :label="$t('空闲率')">
            <template slot-scope="{ row }">
              <div class="percent">
                <div class="percent-progress">
                  <bk-progress :theme="'success'" :show-text="false" :percent="getPercent(row)"></bk-progress>
                </div>
                <span>{{`${100 - row.storage_usage}%`}}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('索引数')" prop="index_count"></bk-table-column>
          <bk-table-column v-if="tableShowType" :label="$t('业务数')" prop="biz_count"></bk-table-column>
        </bk-table>
        <div class="cluster-illustrate" v-show="!!activeItem">
          <p class="illustrate-title">{{$t('集群说明')}}</p>
          <div class="illustrate-container">
            <div v-for="[key, value] of Object.entries(illustrateLabelData)" :key="key">
              <span class="illustrate-label">{{key}}：</span>
              <span class="illustrate-value">{{value}}</span>
            </div>
          </div>
          <div class="illustrate-list">
            <pre>{{description}}</pre>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="noData-container">
          <div slot="empty">
            <empty-status empty-type="empty" :show-text="false">
              <div class="noData-message">
                <p class="empty-message">{{ tableShowType ? $t('当前还没有共享集群，请联系平台管理员提供') : $t('当前还没有业务独享集群，快去创建吧')}}</p>
                <p v-if="!tableShowType" class="button-text" @click="handleCreateCluster">{{$t('创建集群')}}</p>
              </div>
            </empty-status>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
<script>
import { formatFileSize } from '../../../common/util';
import { mapGetters } from 'vuex';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    EmptyStatus,
  },
  props: {
    tableList: {
      type: Array,
      default: () => [],
    },
    tableType: {
      type: String,
      default: 'shared',
    },
    storageClusterId: {
      type: [Number, String],
      require: true,
    },
    isChangeSelect: {
      type: Boolean,
      require: true,
    },
  },
  data() {
    return {
      isShowTable: true,
      clusterSelect: null,
      illustrateLabelData: {
        [this.$t('副本数')]: '',
        [this.$t('过期时间')]: '',
        [this.$t('热冷数据')]: '',
        [this.$t('日志归档')]: '',
      },
      description: '',
      activeItem: null,
      isShow: false,
      throttle: false,
    };
  },
  computed: {
    ...mapGetters({
      curCollect: 'collect/curCollect',
    }),
    tableShowType() {
      return this.tableType !== 'exclusive';
    },
  },
  watch: {
    storageClusterId(val) {
      if (val === undefined) return;
      this.clusterSelect = val;
      this.activeItem = this.tableList.find(item => item.storage_cluster_id === val);
      if (!!this.activeItem) {
        const { number_of_replicas_max: replicasMax, retention_days_max: daysMax } = this.activeItem.setup_config;
        const { enable_hot_warm: hotWarm, enable_archive: archive } =  this.activeItem;
        this.illustrateLabelData = {
          [this.$t('副本数')]: `${this.$t('最大')} ${replicasMax} ${this.$t('个')}`,
          [this.$t('过期时间')]: `${this.$t('最大')} ${daysMax} ${this.$t('天')}`,
          [this.$t('热冷数据')]: hotWarm ? this.$t('支持') : this.$t('不支持'),
          [this.$t('日志归档')]: archive ? this.$t('支持') : this.$t('不支持'),
        };
        this.description = this.activeItem.description;
      } else {
        this.illustrateLabelData = {
          [this.$t('副本数')]: '',
          [this.$t('过期时间')]: '',
          [this.$t('热冷数据')]: '',
          [this.$t('日志归档')]: '',
        };
        this.description = '';
      }
    },
  },
  mounted() {
    this.formatFileSize = formatFileSize;
  },
  methods: {
    handleSelectCluster($row) {
      if (this.throttle || this.storageClusterId === $row.storage_cluster_id) return;

      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;
      }, 300);
      if (this.isChangeSelect || this.storageClusterId === '') {
        this.$emit('update:isChangeSelect', true);
        this.$emit('update:storageClusterId', $row.storage_cluster_id);
        return;
      }
      this.$bkInfo({
        type: 'warning',
        title: this.$t('切换集群将导致历史数据无法查询'),
        confirmFn: () => {
          this.$emit('update:isChangeSelect', true);
          this.$emit('update:storageClusterId', $row.storage_cluster_id);
        },
      });
    },
    handleCreateCluster() {
      const newUrl = this.$router.resolve({
        name: 'es-cluster-manage',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
      window.open(newUrl.href, '_blank');
    },
    getPercent($row) {
      return (100 - $row.storage_usage) / 100;
    },
  },
};
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';
@import '@/scss/mixins/overflow-tips.scss';

.cluster-container {
  line-height: 14px;
  min-width: 900px;

  .overflow-tips {
    @include overflow-tips;
    display: inline-block;
    transform: translateY(2px);
  }

  .cluster-title {
    width: 100%;
    height: 32px;
    font-size: 12px;
    color: #626369;
    background: #eff1f5;
    border: 1px solid #dcdee5;
    border-bottom: none;

    .cluster-title-container {
      height: 100%;
      cursor: pointer;

      @include flex-align;

      &.is-active {
        border-bottom: 1px solid #dcdee5;

        .icon-angle-up-fill {
          transform: rotateZ(-90deg);
        }
      }
    }

    .icon-angle-up-fill {
      margin: 0 10px;
      font-size: 16px;
    }
  }

  .cluster-main {
    display: flex;
    min-height: 170px;

    .cluster-table {
      width: 58%;
      min-width: 420px;
    }

    .cluster-illustrate {
      width: 42%;
      min-width: 460px;
      max-height: 254px;
      padding: 16px;
      font-size: 12px;
      border: 1px solid #dcdee5;
      border-left: none;
      overflow: hidden;

      .illustrate-title {
        font-weight: 700;
        color: #63656e;
      }

      .illustrate-container {
        padding: 12px 0;
        border-bottom: 1px solid #eee;

        @include flex-justify(space-between);
      }

      .illustrate-label {
        color: #979ba5;
      }

      .illustrate-value {
        color: #313238;
      }

      .illustrate-list {
        height: calc(100% - 46px);
        overflow-y: auto;
        color: #63656e;
      }
    }

    .noData-container {
      width: 100%;
      border: 1px solid #dcdee5;

      @include flex-center;

      .noData-message {
        flex-direction: column;
        padding: 20px 0;
        font-size: 12px;

        @include flex-center;

        .empty-message {
          color: #63656e;
          margin-bottom: 6px;
        }
      }

      .icon-empty {
        font-size: 65px;
        color: #c3cdd7;
      }
    }

    .percent {
      display: flex;
      align-items: center;

      .percent-progress {
        width: 40px;
        margin-right: 4px;
      }
    }
  }
}

::v-deep .bk-form-radio {
  white-space: nowrap;
  display: flex;
  align-items: center;
  & > input[type = "radio"] {
    /* stylelint-disable-next-line declaration-no-important */
    display: block !important;
    min-width: 16px;
  }
}

::v-deep .bk-radio-text {
  font-size: 12px;
  display: inline;
  width: 100%;
}
</style>
