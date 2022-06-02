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
      <!-- 数据ID -->
      <div>
        <span>{{ $t('dataSource.dataId') }}</span>
        <span>{{ collectorData.bk_data_id || '-' }}</span>
      </div>
      <!-- 名称 -->
      <div>
        <span>{{ $t('configDetails.name') }}</span>
        <span>{{ collectorData.collector_config_name || '-' }}</span>
      </div>
      <!-- 英文名 -->
      <div>
        <span>{{ $t('dataSource.source_en_name') }}</span>
        <span>{{ collectorData.collector_config_name_en || '-' }}</span>
      </div>
      <!-- 备注说明 -->
      <div>
        <span>{{ $t('configDetails.remarkExplain') }}</span>
        <span>{{ collectorData.description || '-' }}</span>
      </div>
      <!-- 数据分类 -->
      <div>
        <span>{{ $t('configDetails.dataClassify') }}</span>
        <span>{{ collectorData.category_name || '-' }}</span>
      </div>
      <!-- 存储集群 -->
      <div>
        <span>{{ $t('configDetails.StorageCluster') }}</span>
        <span>{{ collectorData.storage_cluster_name || '-' }}</span>
      </div>
      <!-- 日志类型 -->
      <div>
        <span>{{ $t('configDetails.logType') }}</span>
        <span>{{ collectorData.collector_scenario_name || '-' }}</span>
      </div>
      <!-- 配置项 -->
      <div>
        <span>{{$t('配置项')}}</span>
        <div class="config-box">
          <div class="config-title">A</div>
          <div class="deploy-sub">
            <!-- Namespace -->
            <div>
              <span>Namespace</span>
              <span>所有</span>
            </div>
            <!-- 指定容器 -->
            <div>
              <span>{{$t('指定容器')}}</span>
              <div class="specify-box">
                <div
                  class="specify-container"
                  v-for="(item,index) in specifyList"
                  :key="index">
                  <p>{{item.name}} :</p><p>{{item.value}}</p>
                </div>
              </div>
            </div>
            <!-- 关联标签 -->
            <div>
              <span>{{$t('关联标签')}}</span>
              <div class="specify-box">
                <div class="specify-container justify-bt">
                  <p>123</p>
                  <div class="operator">=</div>
                </div>
                <div class="specify-container">
                  <p>123</p>
                </div>
              </div>
            </div>
            <!-- 日志路径 -->
            <div>
              <span>
                {{collectorData.collector_scenario_id === 'wineventlog' ?
                  $t('configDetails.logSpecies') : $t('configDetails.logPath') }}
              </span>
              <div v-if="collectorData.params.paths" class="deploy-path">
                <p v-for="(val, key) in collectorData.params.paths" :key="key">{{ val }}</p>
              </div>
              <div v-else class="deploy-path">
                <p>{{getLogSpeciesStr}}</p>
              </div>
            </div>
            <!-- 日志字符集 -->
            <div>
              <span>{{ $t('configDetails.logSet') }}</span>
              <span>{{ collectorData.data_encoding || '-' }}</span>
            </div>
            <!-- 过滤内容 -->
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
          </div>
        </div>
      </div>
      <!-- 附加日志标签 -->
      <div>
        <span>{{$t('附加日志标签')}}</span>
        <div class="specify-box">
          <div class="specify-container justify-bt">
            <p>123</p>
            <div class="operator">=</div>
          </div>
          <div class="specify-container">
            <p>123</p>
          </div>
        </div>
      </div>
      <!-- 上报链路 -->
      <div>
        <span>{{$t('上报链路')}}</span>
        <span>{{ collectorData.bk_data_id || '-' }}</span>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  props: {
    collectorData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      specifyList: [
        { name: this.$t('应用类型'), value: '****' },
        { name: this.$t('应用名称'), value: '****' },
        { name: this.$t('容器名称'), value: '****' },
      ],
    };
  },
  computed: {
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
  },
  methods: {
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
  },
};
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';

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

  }

  .content-style {
    display: flex;

    .win-log {
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

  .config-box {
    margin-left: 24px;
    border: 1px solid #dcdee5;
    border-radius: 2px;

    .deploy-sub {
      padding: 12px 43px 0 0;
    }

    .config-title {
      width: 100%;
      height: 30px;
      line-height: 30px;
      padding-left: 11px;
      background: #f0f1f5;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
    }
  }

  .specify-box {
    min-width: 573px;
    margin-left: 24px;
    display: flex;
    flex-flow: wrap;
    padding: 8px 16px;
    margin-bottom: 8px;
    background: #f5f7fa;
    border-radius: 2px;

    .specify-container {
      min-width: 50%;
      height: 30px;
      line-height: 30px;

      p {
        font-size: 14px;
        display: inline;
        color: #63656e;
      }

      .operator {
        padding: 0 6px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        color: #ff9c01;
        background: #fff;
        border-radius: 2px;
      }

      :last-child {
        margin-left: 12px;
      }
    }
  }
}

.justify-bt {
  align-items: center;

  @include flex-justify(space-between);
}
</style>
