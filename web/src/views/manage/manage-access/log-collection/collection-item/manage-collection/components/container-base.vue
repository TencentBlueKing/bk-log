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
        <span>{{ $t('数据ID') }}</span>
        <span>{{ collectorData.bk_data_id || '-' }}</span>
      </div>
      <!-- 名称 -->
      <div>
        <span>{{ $t('名称') }}</span>
        <span>{{ collectorData.collector_config_name || '-' }}</span>
      </div>
      <!-- 英文名 -->
      <div>
        <span>{{ $t('英文名') }}</span>
        <span>{{ collectorData.collector_config_name_en || '-' }}</span>
      </div>
      <!-- 备注说明 -->
      <div>
        <span>{{ $t('备注说明') }}</span>
        <span>{{ collectorData.description || '-' }}</span>
      </div>
      <!-- 数据分类 -->
      <div>
        <span>{{ $t('数据分类') }}</span>
        <span>{{ collectorData.category_name || '-' }}</span>
      </div>
      <!-- 存储集群 -->
      <div>
        <span>{{ $t('存储集群') }}</span>
        <span>{{ collectorData.storage_cluster_name || '-' }}</span>
      </div>
      <!-- 日志类型 -->
      <div>
        <span>{{ $t('日志类型') }}</span>
        <span>{{ collectorData.collector_scenario_name || '-' }}</span>
      </div>
      <!-- 容器集群 -->
      <div>
        <span>{{ $t('容器集群') }}</span>
        <span>{{ bcsClusterName }}</span>
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
              <!-- 容器环境 -->
              <div>
                <span>{{ $t('容器环境') }}</span>
                <span>{{ configItem.collectorName }}</span>
              </div>
              <!-- Namespace -->
              <div>
                <span>Namespace</span>
                <span v-if="configItem.namespaces.length" class="span-warp">
                  <span
                    v-for="(spaceItem, spaceIndex) in configItem.namespaces"
                    :key="spaceIndex">
                    <span>{{spaceItem}}{{(spaceIndex + 1) !== configItem.namespaces.length ? ',' : ''}}&nbsp;</span>
                  </span>
                </span>
                <span v-else>{{$t('所有')}}</span>
              </div>
              <!-- 关联标签 -->
              <div>
                <span :class="{ 'label-title': isSelectorHaveValue(configItem.label_selector) }">{{$t('关联标签')}}</span>
                <div v-if="isSelectorHaveValue(configItem.label_selector)">
                  <template v-for="(labItem, labKey) in configItem.label_selector">
                    <div class="specify-box"
                         v-for="(matchItem, matchKey) of labItem"
                         :key="`${labKey}_${matchKey}`">
                      <div class="specify-container justify-bt" v-bk-overflow-tips>
                        <span>{{matchItem.key}}</span>
                        <div class="operator">{{matchItem.operator}}</div>
                      </div>
                      <div class="specify-container" v-bk-overflow-tips>
                        <span>{{matchItem.value}}</span>
                      </div>
                    </div>
                  </template>
                </div>
                <span v-else>{{$t('所有')}}</span>
              </div>
              <!-- 工作负载 -->
              <div class="content-style">
                <span>{{$t('工作负载')}}</span>
                <div class="container justify-bt" v-if="isSelectorHaveValue(configItem.container)">
                  <template
                    v-for="([speKey, speValue], speIndex) in Object.entries(configItem.container)">
                    <div class="container-item" v-if="speValue" :key="speIndex">
                      {{specifyName[speKey]}} : {{speValue}}
                    </div>
                  </template>
                </div>
                <span v-else>--</span>
              </div>
              <!-- 容器名 -->
              <div class="content-style">
                <span>{{$t('容器名')}}</span>
                <div class="container justify-bt" v-if="isContainerHaveValue(configItem.containerName)">
                  <template
                    v-for="(conItem, conIndex) in configItem.containerName">
                    <div class="container-item" :key="conIndex">{{conItem}}</div>
                  </template>
                </div>
                <span v-else>--</span>
              </div>
              <!-- 日志路径 -->
              <div>
                <span>{{ $t('日志路径') }}</span>
                <div v-if=" configItem.params.paths.length" class="deploy-path">
                  <p v-for="(val, key) in configItem.params.paths" :key="key">{{ val }}</p>
                </div>
                <span v-else>--</span>
              </div>
              <!-- 日志字符集 -->
              <div>
                <span>{{ $t('字符集') }}</span>
                <span>{{ configItem.data_encoding || '-' }}</span>
              </div>
              <!-- 过滤内容 -->
              <div
                class="content-style"
                v-if="configItem.params.conditions &&
                  configItem.params.conditions.type === 'match' &&
                  configItem.params.conditions.match_content !== ''">
                <span>{{ $t('过滤内容') }}</span>
                <div>
                  <p>{{ $t('字符串匹配') }}</p>
                  <p v-if="configItem.params.conditions.match_content">
                    {{ configItem.params.conditions.match_content }}
                  </p>
                  <p>
                    {{ configItem.params.conditions.match_type }}/{{
                      configItem.params.conditions.match_type === 'include' ?
                        $t('保留匹配字符串') : $t('过滤匹配字符串') }}
                  </p>
                </div>
              </div>
              <div
                class="content-style"
                v-else-if="configItem.params.conditions &&
                  configItem.params.conditions.type === 'separator' &&
                  configItem.params.conditions.separator_filters !== []">
                <span>{{ $t('过滤内容') }}</span>
                <div>
                  <p>{{ $t('分隔符匹配') }}</p>
                  <p v-if="configItem.params.conditions.separator">{{ configItem.params.conditions.separator }}</p>
                  <div class="condition-stylex">
                    <div>
                      <div class="the-column">
                        <div
                          v-for="(val, key) in configItem.params.conditions.separator_filters"
                          :key="key">
                          {{ $t('第 {n} 列', { n: val.fieldindex })}}
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
                          $t('并') : $t('或') }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="content-style" v-else>
                <span>{{ $t('过滤内容') }}</span>
                <div>--</div>
              </div>
              <!-- 段日志 -->
              <template v-if="collectorData.collector_scenario_id === 'section'">
                <div class="content-style">
                  <span>{{ $t('段日志参数') }}</span>
                  <div class="section-box">
                    <p>{{$t('行首正则')}}: <span>{{configItem.params.multiline_pattern}}</span></p> <br>
                    <p>
                      <i18n path="最多匹配{0}行，最大耗时{1}秒">
                        <span>{{configItem.params.multiline_max_lines}}</span>
                        <span>{{configItem.params.multiline_timeout}}</span>
                      </i18n>
                    </p>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      <!-- 附加日志标签 -->
      <div>
        <span>{{$t('附加日志标签')}}</span>
        <template v-if="extraLabelList.length">
          <div>
            <div v-for="(extraItem, extraIndex) in extraLabelList" :key="extraIndex">
              <div class="specify-box">
                <div class="specify-container justify-bt" v-bk-overflow-tips>
                  <span>{{extraItem.key}}</span>
                  <div class="operator">=</div>
                </div>
                <div class="specify-container" v-bk-overflow-tips>
                  <span>{{extraItem.value}}</span>
                </div>
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
        <span>{{ dataLinkName || '-' }}</span>
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
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      collectorConfigs: [], // config
      extraLabelList: [], // 附加日志标签
      specifyName: { // 指定容器中文名
        workload_type: this.$t('应用类型'),
        workload_name: this.$t('应用名称'),
      },
      collectorNameMap: {
        container_log_config: 'Container',
        node_log_config: 'Node',
        std_log_config: this.$t('标准输出'),
      },
      dataLinkName: '--',
      bcsClusterName: '--', // 容器环境集群名
    };
  },
  computed: {
  },
  async created() {
    this.$emit('update:is-loading', true);
    try {
      await this.getLinkData(this.collectorData);
      await this.initContainerConfigData(this.collectorData);
    } catch (error) {
      console.warn(error);
    } finally {
      this.$emit('update:is-loading', false);
    }
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
    async initContainerConfigData(data) {
      // 分yaml模式和ui模式下的config展示
      try {
        this.bcsClusterName = await this.getBcsClusterName(data.bcs_cluster_id);
        const showData = data.yaml_config_enabled ? await this.getYamlConfigData(data.yaml_config) : data;
        this.extraLabelList = showData.extra_labels;
        this.collectorConfigs = showData.configs.map((item) => {
          const {
            workload_name,
            workload_type,
            container_name: baseContainerName,
            match_expressions,
            match_labels,
            data_encoding,
            params,
            container: yamlContainer,
            label_selector: yamlSelector,
            namespaces,
            collector_type,
          } = item;
          let container;
          let labelSelector;
          let containerName = this.getContainerNameList(baseContainerName);
          if (data.yaml_config_enabled) {
            const { workload_name, workload_type, container_name: yamlContainerName } = yamlContainer;
            container = { workload_name, workload_type };
            containerName = this.getContainerNameList(yamlContainerName);
            labelSelector = yamlSelector;
          } else {
            container =  {
              workload_type,
              workload_name,
            };
            labelSelector = {
              match_labels,
              match_expressions,
            };
          }
          const collectorName = this.collectorNameMap[collector_type] || '--';
          return {
            namespaces,
            data_encoding,
            container,
            collectorName,
            containerName,
            label_selector: labelSelector,
            params,
          };
        });
      } catch (error) {
        console.warn(error);
      }
    },
    getContainerNameList(containerName = '') {
      const splitList = containerName.split(',');
      if (splitList.length === 1 && splitList[0] === '') return [];
      return splitList;
    },
    async getLinkData(collectorData) {
      try {
        const res = await this.$http.request('linkConfiguration/getLinkList', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        this.dataLinkName = res.data.find(item => (item.data_link_id === collectorData.data_link_id))?.link_group_name || '--';
      } catch (e) {
        console.warn(e);
      }
    },
    getFromCharCode(index) {
      return String.fromCharCode(index + 65);
    },
    async getYamlConfigData(yamlConfig) {
      const defaultConfigData = {
        configs: [],
        extra_labels: [],
      };
      try {
        const res = await this.$http.request('container/yamlJudgement', {
          data: {
            bk_biz_id: this.$store.state.bkBizId,
            bcs_cluster_id: this.collectorData.bcs_cluster_id,
            yaml_config: yamlConfig,
          },
        });
        const { parse_result: parseResult, parse_status: parseStatus } = res.data;
        if (Array.isArray(parseResult) && !parseStatus) return defaultConfigData; // 返回值若是数组则表示yaml解析出错
        if (parseStatus) return {
          configs: parseResult.configs,
          extra_labels: parseResult.extra_labels,
        };
      } catch (error) {
        console.warn(error);
        return defaultConfigData;
      }
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
    /**
     * @desc: 获取bcs集群列表名
     */
    async getBcsClusterName(bcsID) {
      try {
        const query = { bk_biz_id: this.$store.state.bkBizId };
        const res = await this.$http.request('container/getBcsList', { query });
        return res.data.find(item => item.id === bcsID)?.name || '--';
      } catch (error) {
        return '--';
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';
@import '@/scss/basic.scss';

.basic-info-container {
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

  .label-title {
    margin-top: 7px;
  }

  .content-style {
    display: flex;
    align-items: center;

    .win-log {
      height: 60px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .section-box {
      > :last-child {
        margin-top: 4px;
      }
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

    .container {
      flex-wrap: wrap;

      .container-item {
        padding: 4px 10px;
        color: #63656e;
        background: #f0f1f5;
        margin-right: 8px;
        border-radius: 2px;
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
    padding: 2px 16px;
    margin-bottom: 8px;
    background: #f5f7fa;
    border-radius: 2px;

    .specify-container {
      width: 50%;
      height: 30px;
      line-height: 28px;
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
        font-size: 14px;
        font-weight: 700;
      }

      :last-child {
        margin-left: 12px;
      }
    }
  }
}

.span-warp {
  display: flex;
  flex-wrap: wrap;
}

.justify-bt {
  align-items: center;

  @include flex-justify(space-between);
}
</style>
