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
  <div class="basic-info-container">
    <div class="deploy-sub">
      <div>
        <span>{{ $t('dataSource.dataId') }}</span><span>{{ collectorData.bk_data_id || '-' }}</span>
      </div>
      <div>
        <span>{{ $t('configDetails.name') }}</span><span>{{ collectorData.collector_config_name || '-' }}</span>
      </div>
      <template v-if="isCustomReport">
        <div>
          <span>{{ $t('数据类型') }}</span><span>{{ collectorData.custom_name || '-' }}</span>
        </div>
        <div>
          <span>{{ $t('dataSource.source_en_name') }}</span>
          <span>{{ collectorData.collector_config_name_en || '-' }}</span>
        </div>
        <div>
          <span>{{ $t('数据分类') }}</span><span>{{ collectorData.category_name || '-' }}</span>
        </div>
        <div>
          <span>{{ $t('customReport.remark') }}</span><span>{{ collectorData.description || '-' }}</span>
        </div>
      </template>
      <template v-else>
        <div>
          <span>{{ $t('configDetails.logType') }}</span><span>{{ collectorData.collector_scenario_name || '-' }}</span>
        </div>
        <div>
          <span>{{ $t('configDetails.dataClassify') }}</span><span>{{ collectorData.category_name || '-' }}</span>
        </div>
        <div>
          <span>{{collectorData.collector_scenario_id === 'wineventlog' ?
            $t('configDetails.logSpecies') : $t('configDetails.logPath') }}</span>
          <div v-if="collectorData.params.paths" class="deploy-path">
            <p v-for="(val, key) in collectorData.params.paths" :key="key">{{ val }}</p>
          </div>
          <div v-else class="deploy-path">
            <p>{{getLogSpeciesStr}}</p>
          </div>
        </div>
        <div><span>{{ $t('configDetails.logSet') }}</span><span>{{ collectorData.data_encoding || '-' }}</span>
        </div>
        <div><span>{{ $t('configDetails.target') }}</span><span>{{ $t('configDetails.selected') }}
          <p class="num-color" @click="handleClickTarget">{{ collectorData.target_nodes.length || '-' }}</p>
          {{ collectorData.target_node_type !== 'INSTANCE' ?
            $t('configDetails.Been') : $t('configDetails.staticHosts') }}
        </span></div>
        <div>
          <span>{{ $t('configDetails.storageIndexName') }}</span>
          <span v-if="collectorData.table_id">{{ collectorData.table_id_prefix }}{{ collectorData.table_id }}</span>
          <span v-else>-</span>
        </div>
        <div><span>{{ $t('configDetails.remarkExplain') }}</span><span>{{ collectorData.description || '-' }}</span>
        </div>
        <div
          class="content-style"
          v-if="collectorData.params.conditions &&
            collectorData.params.conditions.type === 'match' &&
            collectorData.params.conditions.match_content !== ''">
          <span>{{ $t('configDetails.filterContent') }}</span>
          <div>
            <p>{{ $t('configDetails.strMatching') }}</p>
            <p
              v-if="collectorData.params.conditions.match_content">
              {{ collectorData.params.conditions.match_content }}
            </p>
            <p>
              {{ collectorData.params.conditions.match_type }}/{{
                collectorData.params.conditions.match_type === 'include' ?
                  $t('configDetails.keep') : $t('configDetails.Filter') }}
            </p>
          </div>
        </div>
        <div
          class="content-style"
          v-else-if="collectorData.params.conditions &&
            collectorData.params.conditions.type === 'separator' &&
            collectorData.params.conditions.separator_filters !== []">
          <span>{{ $t('configDetails.filterContent') }}</span>
          <div>
            <p>{{ $t('configDetails.sepMatching') }}</p>
            <p v-if="collectorData.params.conditions.separator">{{ collectorData.params.conditions.separator }}</p>
            <div class="condition-stylex">
              <div>
                <div class="the-column">
                  <div
                    v-for="(val, key) in collectorData.params.conditions.separator_filters"
                    :key="key">
                    {{ $t('configDetails.the') }} {{ val.fieldindex }} {{ $t('configDetails.column') }}
                  </div>
                </div>
                <div>
                  <div v-for="(val, key) in collectorData.params.conditions.separator_filters" :key="key">
                    <p @mouseenter="handleEnter" @mouseleave="handleLeave">{{ val.word }}</p>
                    <div
                      :class="key === 0 ? 'line-styy' : 'line-sty'"
                      v-if="collectorData.params.conditions.separator_filters.length > 1">
                    </div>
                  </div>
                </div>
              </div>
              <div class="con-text" v-if="collectorData.params.conditions.separator_filters.length > 1">
                <div class="line-styx"></div>
                <p>
                  {{ collectorData.params.conditions.separator_filters[0].logic_op === 'and' ?
                    $t('configDetails.and') : $t('configDetails.or') }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="content-style"
             v-else-if="collectorData.collector_scenario_id === 'wineventlog' && isThereValue">
          <span>{{ $t('configDetails.filterContent') }}</span>
          <div class="win-log">
            <div>
              <p>{{$t('事件ID')}}:{{getEventIDStr}}</p>
            </div>
            <div>
              <p>{{$t('级别')}}:{{getLevelStr}}</p>
            </div>
          </div>
        </div>
        <div class="content-style" v-else>
          <span>{{ $t('configDetails.filterContent') }}</span>
          <div>
            --
          </div>
        </div>
      </template>
      <div>
        <span>{{ $t('configDetails.StorageCluster') }}</span>
        <span>{{ collectorData.storage_cluster_name || '-' }}</span>
      </div>
      <div>
        <span>{{ $t('configDetails.storageIndexName') }}</span>
        <span>{{ collectorData.table_id_prefix + collectorData.table_id || '-' }}</span>
      </div>
      <div>
        <span>{{ $t('configDetails.expirationTime') }}</span>
        <span>{{ collectorData.retention || '-' }} {{ $t('configDetails.day') }}</span>
      </div>
      <p class="button-place">
        <bk-button :theme="'primary'" @click="handleClickEdit" class="mr10">
          {{ $t('编辑') }}
        </bk-button>
      </p>
    </div>
    <div class="create-name-and-time">
      <div v-for="item in createAndTimeData" :key="item.key">
        <span>{{ item.label }}</span>
        <span>{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { formatDate } from '@/common/util';

export default {
  props: {
    collectorData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // 右边展示的创建人、创建时间
      createAndTimeData: [],
    };
  },
  computed: {
    ...mapState(['projectId']),
    getEventIDStr() {
      return this.collectorData.params.winlog_event_id.join(',');
    },
    getLevelStr() {
      return this.collectorData.params.winlog_level.join(',');
    },
    getLogSpeciesStr() {
      return this.collectorData.params.winlog_name.join(',');
    },
    isThereValue() {
      return this.collectorData.params.winlog_event_id.length > 0 || this.collectorData.params.winlog_level.length > 0;
    },
    // 自定义上报基本信息
    isCustomReport() {
      return this.$route.name === 'custom-report-detail';
    },
  },
  created() {
    this.getCollectDetail();
  },
  methods: {
    getCollectDetail() {
      try {
        const collectorData = this.collectorData;
        const createAndTimeData = [{
          key: 'updated_by',
          label: this.$t('configDetails.updated_by'),
        }, {
          key: 'updated_at',
          label: this.$t('configDetails.updated_at'),
        }, {
          key: 'created_by',
          label: this.$t('configDetails.created_by'),
        }, {
          key: 'created_at',
          label: this.$t('configDetails.created_at'),
        }];
        this.createAndTimeData = createAndTimeData.map((item) => {
          if (item.key === 'created_at' || item.key === 'updated_at') {
            item.value = formatDate(collectorData[item.key]);
          } else {
            item.value = collectorData[item.key];
          }
          return item;
        });
      } catch (e) {
        console.warn(e);
      }
    },
    handleClickTarget() {
      this.$emit('update-active-panel', 'collectionStatus');
    },
    // 判断是否超出  超出提示
    handleEnter(e) {
      const cWidth = e.target.clientWidth;
      const sWidth = e.target.scrollWidth;
      if (sWidth > cWidth) {
        this.instance = this.$bkPopover(e.target, {
          content: e.path[0].childNodes[0].data,
          arrow: true,
          placement: 'right',
        });
        this.instance.show(1000);
      }
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    handleClickEdit() {
      const params = {};
      params.collectorId = this.$route.params.collectorId;
      const routeName = this.isCustomReport ? 'custom-report-edit' : 'collectEdit';
      this.$router.push({
        name: routeName,
        params,
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .basic-info-container {
    display: flex;
    justify-content: space-between;

    .deploy-sub > div {
      display: flex;
      margin-bottom: 33px;

      span:nth-child(1) {
        display: block;
        width: 98px;
        color: #979ba5;
        text-align: right;
        font-size: 14px;
      }

      span:nth-child(2) {
        margin-left: 24px;
        color: #63656e;
        font-size: 14px;
      }

      .deploy-path {
        margin-left: 24px;
        color: #63656e;
        font-size: 14px;
        line-height: 22px;
      }

      .num-color {
        display: inline-block;
        padding: 0;
        color: #4e99ff !important;
        font-weight: bold;
        cursor: pointer;
      }
    }

    .content-style {
      display: flex;

      .win-log{
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }

      > div {
        font-size: 14px;
        margin-left: 24px;

        p {
          display: inline-block;
          margin-right: 2px;
          background-color: #f0f1f5;
          padding: 0 5px;
          border-radius: 2px;
          color: #63656e;
          height: 20px;
          text-align: center;
          line-height: 20px;
        }
      }
    }

    .button-place {
      margin-left: 118px;
    }

    .create-name-and-time {
      border-top: 1px solid #dcdee5;
      border-radius: 2px;

      div {
        height: 40px;
        width: 260px;
        border-bottom: 1px solid #dcdee5;
        border-left: 1px solid #dcdee5;
        border-right: 1px solid #dcdee5;
        line-height: 40px;

        span:nth-child(1) {
          margin-left: 14px;
          font-size: 12px;
          color: #313238;
          display: inline-block;
          width: 48px;
        }

        span:nth-child(2) {
          margin-left: 22px;
          font-size: 12px;
          color: #63656e;
        }
      }
    }
  }
</style>
