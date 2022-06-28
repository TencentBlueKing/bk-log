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
        <div>
          <div v-for="( configItem, configIndex) in collectorConfigs"
               :key="configIndex"
               class="config-box">
            <div class="config-title">{{getFromCharCode(configIndex)}}</div>
            <div class="deploy-sub">
              <!-- Namespace -->
              <div>
                <span>Namespace</span>
                <span v-if="configItem.namespaces.length" class="span-warp">
                  <span
                    v-for="(spaceItem, spaceIndex) in configItem.namespaces"
                    :key="spaceIndex">
                    {{spaceItem}}
                  </span>
                </span>
                <span v-else>{{$t('所有')}}</span>
              </div>
              <!-- 指定容器 -->
              <div>
                <span>{{$t('指定容器')}}</span>
                <div class="specify-box" v-if="isSelectorHaveValue(configItem.container)">
                  <template
                    v-for="([speKey, speValue], speIndex) in Object.entries(configItem.container)">
                    <div class="specify-container" v-if="speValue" :key="speIndex">
                      <span>{{specifyName[speKey]}}</span> : <span>{{speValue}}</span>
                    </div>
                  </template>
                </div>
                <span v-else>
                  {{$t('所有')}}
                </span>
              </div>
              <!-- 关联标签 -->
              <div>
                <span>{{$t('关联标签')}}</span>
                <div v-if="isSelectorHaveValue(configItem.label_selector)">
                  <template v-for="(labItem, labKey) in configItem.label_selector">
                    <div class="specify-box"
                         v-for="(matchItem, matchKey) of labItem"
                         :key="`${labKey}_${matchKey}`">
                      <div class="specify-container justify-bt">
                        <span>{{matchItem.key}}</span>
                        <div class="operator">{{matchItem.operator}}</div>
                      </div>
                      <div class="specify-container">
                        <span>{{matchItem.value}}</span>
                      </div>
                    </div>
                  </template>
                </div>
                <span v-else>
                  {{$t('所有')}}
                </span>
              </div>
              <!-- 日志路径 -->
              <div>
                <span>
                  {{ $t('configDetails.logPath') }}
                </span>
                <div v-if=" configItem.params.paths.length" class="deploy-path">
                  <p v-for="(val, key) in configItem.params.paths" :key="key">{{ val }}</p>
                </div>
                <span v-else>
                  --
                </span>
              </div>
              <!-- 日志字符集 -->
              <div>
                <span>{{ $t('configDetails.logSet') }}</span>
                <span>{{ configItem.data_encoding || '-' }}</span>
              </div>
              <!-- 过滤内容 -->
              <div
                class="content-style"
                v-if="configItem.params.conditions &&
                  configItem.params.conditions.type === 'match' &&
                  configItem.params.conditions.match_content !== ''">
                <span>{{ $t('configDetails.filterContent') }}</span>
                <div>
                  <p>{{ $t('configDetails.strMatching') }}</p>
                  <p
                    v-if="configItem.params.conditions.match_content">
                    {{ configItem.params.conditions.match_content }}
                  </p>
                  <p>
                    {{ configItem.params.conditions.match_type }}/{{
                      configItem.params.conditions.match_type === 'include' ?
                        $t('configDetails.keep') : $t('configDetails.Filter') }}
                  </p>
                </div>
              </div>
              <div
                class="content-style"
                v-else-if="configItem.params.conditions &&
                  configItem.params.conditions.type === 'separator' &&
                  configItem.params.conditions.separator_filters !== []">
                <span>{{ $t('configDetails.filterContent') }}</span>
                <div>
                  <p>{{ $t('configDetails.sepMatching') }}</p>
                  <p v-if="configItem.params.conditions.separator">{{ configItem.params.conditions.separator }}</p>
                  <div class="condition-stylex">
                    <div>
                      <div class="the-column">
                        <div
                          v-for="(val, key) in configItem.params.conditions.separator_filters"
                          :key="key">
                          {{ $t('configDetails.the') }} {{ val.fieldindex }} {{ $t('configDetails.column') }}
                        </div>
                      </div>
                      <div>
                        <div v-for="(val, key) in configItem.params.conditions.separator_filters" :key="key">
                          <p @mouseenter="handleEnter" @mouseleave="handleLeave">{{ val.word }}</p>
                          <div
                            :class="key === 0 ? 'line-styy' : 'line-sty'"
                            v-if="configItem.params.conditions.separator_filters.length > 1">
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="con-text" v-if="configItem.params.conditions.separator_filters.length > 1">
                      <div class="line-styx"></div>
                      <p>
                        {{ configItem.params.conditions.separator_filters[0].logic_op === 'and' ?
                          $t('configDetails.and') : $t('configDetails.or') }}
                      </p>
                    </div>
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
      </div>
      <!-- 附加日志标签 -->
      <div>
        <span>{{$t('附加日志标签')}}</span>
        <template v-if="collectorData.extra_labels.length">
          <div v-for="(extraItem, extraIndex) in collectorData.extra_labels" :key="extraIndex">
            <div class="specify-box">
              <div class="specify-container justify-bt">
                <span>{{extraItem.key}}</span>
                <div class="operator">=</div>
              </div>
              <div class="specify-container">
                <span>{{extraItem.value}}</span>
              </div>
            </div>
          </div>
        </template>
        <span v-else>
          --
        </span>
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
      collectorConfigs: [],
      specifyName: { // 指定容器中文名
        workload_type: this.$t('应用类型'),
        workload_name: this.$t('应用名称'),
        container_name: this.$t('容器名称'),
      },
    };
  },
  computed: {
  },
  created() {
    this.initContainerConfigData(this.collectorData);
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
    /**
     * @desc: 初始化编辑的form表单值
     * @returns { Object } 返回初始化后的Form表单
     */
    initContainerConfigData(data) {
      this.collectorConfigs = data.configs.map((item, index) => {
        const {
          workload_name,
          workload_type,
          container_name,
          match_expressions,
          match_labels,
          data_encoding,
          params,
          namespaces: itemNamespace,
        } = item;
        let isAllContainer = false;
        const namespaces = item.any_namespace ? [] : itemNamespace;
        const container =  {
          workload_type,
          workload_name,
          container_name,
        };
        // eslint-disable-next-line camelcase
        const label_selector = {
          match_labels,
          match_expressions,
        };
        if (JSON.stringify(container) === JSON.stringify(this.allContainer)
        && JSON.stringify(label_selector) === JSON.stringify(this.allLabelSelector)) {
          isAllContainer = true;
        }
        return {
          letterIndex: index,
          isAllContainer,
          namespaces,
          data_encoding,
          container,
          label_selector,
          params,
        };
      });
    },
    getFromCharCode(index) {
      return String.fromCharCode(index + 65);
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    isSelectorHaveValue(labelSelector) {
      return Object.values(labelSelector)?.some(item => item.length) || false;
    },
    isContainerHaveValue(container) {
      return Object.values(container)?.some(item => !!item) || false;
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
    color: #63656e;

    > span:nth-child(1) {
      display: block;
      width: 98px;
      color: #979ba5;
      text-align: right;
      font-size: 14px;
    }

    > span:nth-child(2) {
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
    margin-bottom: 20px;

    .deploy-sub {
      padding: 12px 43px 0 0;

      > div {
        margin-bottom: 20px;
      }
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
    min-width: 700px;
    margin-left: 24px;
    display: flex;
    flex-flow: wrap;
    padding: 8px 16px;
    margin-bottom: 8px;
    background: #f5f7fa;
    border-radius: 2px;

    .specify-container {
      width: 50%;
      height: 30px;
      line-height: 30px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      span {
        font-size: 14px;
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

.span-warp {
  display: flex;
  flex-direction: column;
}

.justify-bt {
  align-items: center;

  @include flex-justify(space-between);
}
</style>
