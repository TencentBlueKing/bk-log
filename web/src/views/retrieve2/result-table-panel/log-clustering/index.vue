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
    <div class="log-cluster-table-container" v-if="!globalLoading">
      <div class="cluster-nav" v-if="exhibitAll">
        <div class="bk-button-group">
          <bk-button
            size="small"
            v-for="(item) of clusterNavList"
            :key="item.id"
            :class="active === item.id ? 'is-selected' : ''"
            @click="handleClickNav(item.id)">
            {{item.name}}
          </bk-button>
        </div>

        <div v-if="active === 'dataFingerprint'"
             class="fingerprint fljb">
          <div class="fingerprint-setting fljb">
            <div class="fljb">
              <span>{{$t('同比')}}</span>
              <bk-select
                behavior="simplicity"
                ext-cls="compared-select"
                ext-popover-cls="compared-select-option"
                v-model="yearOnYearCycle"
                :disabled="!signatureSwitch"
                :clearable="false"
                :popover-min-width="140"
                @change="requestFinger"
                @toggle="isShowCustomize = true">
                <bk-option
                  v-for="option in comparedList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
                <div slot="" class="compared-customize">
                  <div class="customize-option" v-if="isShowCustomize" @click="isShowCustomize = false">
                    <span>{{$t('自定义')}}</span>
                  </div>
                  <div v-else>
                    <bk-input @enter="handleEnterCompared"></bk-input>
                    <div class="compared-select-icon">
                      <span v-bk-tooltips="$t('customizeTips')" class="top-end">
                        <i class="log-icon icon-help"></i>
                      </span>
                    </div>
                  </div>
                </div>
              </bk-select>
            </div>

            <bk-checkbox
              v-model="showNewPattern"
              :true-value="true"
              :false-value="false"
              :disabled="!signatureSwitch">
              <span style="font-size: 12px">{{$t('近24H新增')}}</span>
            </bk-checkbox>

            <div class="partter fljb" style="width: 200px">
              <span>Partter</span>
              <div class="partter-slider-box fljb">
                <span>{{$t('少')}}</span>
                <bk-slider
                  class="partter-slider"
                  v-model="partterSize"
                  :show-tip="false"
                  :disable="!signatureSwitch"
                  :max-value="sliderMaxVal"
                  @change="blurPartterSize"></bk-slider>
                <span>{{$t('多')}}</span>
              </div>
            </div>
          </div>

          <export-log
            :retrieve-params="retrieveParams"
            :total-count="totalCount"
            :queue-status="queueStatus"
            :async-export-usable="asyncExportUsable"
            :async-export-usable-reason="asyncExportUsableReason">
          </export-log>

        </div>
      </div>

      <bk-alert
        v-if="active === 'dataFingerprint' && signatureSwitch && !exhibitAll"
        :title="$t('clusterAlert')" closable type="info">
      </bk-alert>

      <div v-if="exhibitAll">
        <clustering-loader
          is-loading
          v-if="tableLoading"
          :width-list="smallLoaderWidthList">
        </clustering-loader>
        <div v-else>
          <ignore-table
            v-if="active === 'ignoreNumbers' || active === 'ignoreSymbol'"
            v-bind="$attrs"
            v-on="$listeners"
            :total-fields="totalFields"
            :origin-table-list="originTableList"
            :clustering-field="clusteringField"
            :active="active" />
          <data-fingerprint
            v-if="active === 'dataFingerprint'"
            v-bind="$attrs"
            v-on="$listeners"
            :show-new-pattern="showNewPattern"
            :year-on-year-cycle="yearOnYearCycle"
            :cluster-switch="clusterSwitch"
            :partter-level="partterLevel"
            :config-data="configData"
            :finger-list="fingerList" />
        </div>
      </div>

      <bk-table
        v-else
        class="no-text-table"
        :data="[]">
        <div slot="empty">
          <div class="empty-text">
            <span class="bk-table-empty-icon bk-icon icon-empty"></span>
            <p>{{exhibitText}}</p>
            <span class="empty-leave" @click="handleLeaveCurrent">
              {{exhibitOperate}}
            </span>
          </div>
        </div>
      </bk-table>
    </div>
    <clustering-loader
      is-loading
      v-else
      :width-list="loadingWidthList.global">
    </clustering-loader>
  </div>
</template>

<script>
import DataFingerprint from './DataFingerprint';
import IgnoreTable from './IgnoreTable';
import ClusteringLoader from '@/skeleton/clustering-loader';
import { mapGetters } from 'vuex';
import ExportLog from '../../result-comp/ExportLog.vue';

export default {
  components: { DataFingerprint, IgnoreTable, ClusteringLoader, ExportLog },
  props: {
    retrieveParams: {
      type: Object,
      required: true,
    },
    configData: {
      type: Object,
      require: true,
    },
    cleanConfig: {
      type: Object,
      require: true,
    },
    totalFields: {
      type: Array,
      require: true,
    },
    originTableList: {
      type: Array,
      required: true,
    },
    totalCount: {
      type: Number,
      default: 0,
    },
    queueStatus: {
      type: Boolean,
      default: true,
    },
    asyncExportUsable: {
      type: Boolean,
      default: true,
    },
    asyncExportUsableReason: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      active: 'ignoreNumbers',
      partterSize: 0, // slider当前值
      partterLevel: '', // partter等级
      sliderMaxVal: 0, // partter最大值
      clusterSwitch: false, // 日志聚类开关
      signatureSwitch: false, // 数据指纹开关
      partterList: [], // partter敏感度List
      showNewPattern: false, // 近24h
      yearOnYearCycle: 0, // 同比值
      configID: -1, // 采集项ID
      exhibitAll: false, // 是否显示nav
      alreadyClickNav: [], // 已加载过的nav
      globalLoading: false, // 日志聚类大loading
      tableLoading: false, // 详情loading
      isShowCustomize: true, // 是否显示自定义
      clusterNavList: [{
        id: 'ignoreNumbers',
        name: this.$t('忽略数字'),
      }, {
        id: 'ignoreSymbol',
        name: this.$t('忽略符号'),
      }, {
        id: 'dataFingerprint',
        name: this.$t('数据指纹'),
      }],
      comparedList: [], // 同比List
      fingerList: [
        // {
        //   pattern: 'xx [ip] [xxxxx] xxxxx]',
        //   signature: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        //   count: 123,
        //   year_on_year: -10,
        //   percentage: 12,
        //   is_new_class: true,
        //   year_on_year_count: 12,
        //   year_on_year_percentage: 0,
        //   labels: ['xxxx', 'xxxx'],
        //   remark: 'xxxx',
        // },
      ], // 数据指纹List
      loadingWidthList: { // loading表头宽度列表
        global: [''],
        ignore: [60, 90, 90, ''],
        notCompared: [150, 90, 90, ''],
        compared: [150, 90, 90, 100, 100, ''],
      },
    };
  },
  computed: {
    ...mapGetters({
      globalsData: 'globals/globalsData',
    }),
    smallLoaderWidthList() {
      if (this.active !== 'dataFingerprint') {
        return this.loadingWidthList.ignore;
      }
      return this.yearOnYearCycle > 0 ? this.loadingWidthList.compared : this.loadingWidthList.notCompared;
    },
    exhibitText() {
      return this.clusterSwitch ? (this.configID ? this.$t('goCleanMessage') : this.$t('noConfigIDMessage')) : this.$t('goSettingMessage');
    },
    exhibitOperate() {
      return this.clusterSwitch ? (this.configID ? this.$t('跳转到日志清洗') : '') : this.$t('去设置');
    },
    clusteringField() {
      return this.configData?.extra?.clustering_field || '';
    },
  },
  watch: {
    configData: {
      deep: true,
      immediate: true,
      handler(val) {
        this.clusterSwitch = val.is_active;
        this.signatureSwitch = val.extra.signature_switch;
        this.configID = this.cleanConfig.extra?.collector_config_id;
      },
    },
    originTableList: {
      handler() {
        if (this.active === 'dataFingerprint' && this.configData.extra.signature_switch) {
          this.requestFinger();
        }
      },
    },
    totalFields: {
      deep: true,
      immediate: true,
      handler(newList) {
        if (newList.length !== 0) {
          if (!this.configData.is_active) {
            this.exhibitAll = false;
            return;
          }
          this.partterLevel === '' && this.initTable();
          this.exhibitAll = newList.some(el => el.field_type === 'text');
        }
      },
    },
    '$route.params.indexId'() {
      this.alreadyClickNav = [];
      this.showTableLoading('global');
    },
  },
  methods: {
    handleClickNav(id) {
      this.active = id;
      const isClick = this.alreadyClickNav.some(el => el === id);
      if (!isClick) {
        this.alreadyClickNav.push(id);
        if (this.alreadyClickNav.includes('dataFingerprint') && this.configData.extra.signature_switch) {
          this.requestFinger();
          return;
        }
        this.showTableLoading('table');
      }
    },
    // 同比自定义输入
    handleEnterCompared(val) {
      const matchVal = val.match(/^(\d+)h$/);
      if (!matchVal) {
        this.$bkMessage({
          theme: 'warning',
          message: this.$t('请按照提示输入'),
        });
        return;
      }
      this.isShowCustomize = true;
      const isRepeat =  this.comparedList.some(el => el.id === Number(matchVal[1]));
      if (isRepeat) {
        this.yearOnYearCycle = Number(matchVal[1]);
        return;
      }
      this.comparedList.push({
        id: Number(matchVal[1]),
        name: `${matchVal[1]}小时前`,
      });
      this.yearOnYearCycle = Number(matchVal[1]);
    },
    // 请求数据指纹
    requestFinger() {
      delete this.retrieveParams.bk_biz_id;
      delete this.retrieveParams.begin;
      this.tableLoading = true;
      this.$http.request('/logClustering/clusterSearch', {
        params: {
          index_set_id: this.$route.params.indexId,
        },
        data: {
          ...this.retrieveParams,
          pattern_level: this.partterLevel,
          show_new_pattern: true,
          year_on_year_hour: this.yearOnYearCycle,
        },
      })
        .then((res) => {
          this.fingerList = res.data;
        })
        .finally(() => {
          this.tableLoading = false;
        });
    },
    // 初始化数据指纹配置
    initTable() {
      const {
        log_clustering_level_year_on_year: yearOnYearList,
        log_clustering_level: clusterLevel,
      } = this.globalsData;
      this.comparedList = yearOnYearList;
      this.partterSize = clusterLevel.length - 1;
      this.sliderMaxVal = clusterLevel.length - 1;
      this.partterLevel = clusterLevel[clusterLevel.length - 1];
      this.partterList = clusterLevel;
    },
    // 敏感度
    blurPartterSize(val) {
      this.partterLevel = this.partterList[val];
      this.requestFinger();
    },
    // 跳转
    handleLeaveCurrent() {
      if (!this.clusterSwitch) {
        this.$emit('showSettingLog');
        return;
      }
      if (this.configID && this.configID > 0) {
        this.$router.push({
          name: 'clean-edit',
          params: { collectorId: this.configID },
          query: { projectId: window.localStorage.getItem('project_id') },
        });
      }
    },
    // table loading动画
    showTableLoading(type = 'table') {
      type === 'table' ? this.tableLoading : this.globalLoading = true;
      setTimeout(() => {
        type === 'table' ? this.tableLoading : this.globalLoading = false;
      }, 500);
    },
  },
};
</script>

<style lang="scss">
@import "@/scss/mixins/flex.scss";

.log-cluster-table-container {
  .cluster-nav {
    min-width: 760px;
    margin-bottom: 12px;
    color: #63656e;

    .fingerprint {
      width: 535px;
    }

    .fingerprint-setting {
      width: 485px;
      height: 24px;
      line-height: 24px;
      font-size: 12px;

      .partter {
        width: 200px;

        .partter-slider-box {
          width: 154px;
        }

        .partter-slider {
          width: 114px;
        }
      }
    }

    .download-icon {
      min-width: 26px;
      height: 26px;
      padding: 0;
      border: 1px solid #c1c4ca;
      position: relative;
      color: #979ba5;
      cursor: pointer;
      border-radius: 2px;
      @include flex-center;
    }
    @include flex-justify(space-between);
  }

  .bk-alert {
    margin-bottom: 16px;
  }
}

.compared-select {
  min-width: 87px;
  margin-left: 6px;
  position: relative;
  top: -3px;

  .bk-select-name {
    height: 24px;
  }
}

.compared-select-option{
  .compared-customize{
    position: relative;
    margin-bottom: 6px;
  }
  .compared-select-icon{
    font-size: 14px;
    position: absolute;
    right: 18px;
    top: 2px;
  }
  .customize-option{
    padding:0 18px;
    cursor: pointer;
    &:hover{
      color:#3A84FF;
      background: #EAF3FF;
    }
  }
  .bk-form-control{
    width: 80%;
    margin: 0 auto;
  }
  .bk-form-input{
    padding: 0 18px 0 10px !important;
  }
}

.no-text-table {
  .bk-table-empty-block {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 480px);
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

.fljb {
  align-items: center;
  @include flex-justify(space-between);
}
</style>
