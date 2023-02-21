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
  <!-- 检索-设置 -->
  <bk-dialog
    width="100%"
    v-model="isDialogVisiable"
    :show-mask="false"
    :close-icon="false"
    :show-footer="false"
    :draggable="false"
    :scrollable="true"
    :position="{
      top: 50,
      left: 0,
    }"
    @value-change="openPage"
    @after-leave="closePage">
    <div
      class="setting-container"
      v-if="isDialogVisiable"
      data-test-id="clusterSetting_div_settingContainer">
      <div class="setting-title">
        <span>{{$t('设置')}}</span>
        <span class="bk-icon icon-close" @click="closeSetting"></span>
      </div>

      <div class="setting-main">
        <div class="setting-left">
          <div
            v-for="item of showCurrentList"
            :key="item.id"
            :class="['setting-option',currentChoice === item.id ? 'current-color' : '']"
            :data-test-id="`settingContainer_div_select${item.id}`"
            @click="handleNavClick(item)">
            <span class="log-icon icon-block-shape"></span>
            <span style="width: 110px">{{item.name}}</span>
            <div @click.stop="stopChangeSwitch(item)">
              <bk-switcher
                theme="primary"
                v-model="item.isEditable"
                :pre-check="() => false"
                :disabled="item.isDisabled">
              </bk-switcher>
            </div>
          </div>
        </div>

        <div class="setting-right">
          <div class="more-details">
            <div class="details">
              <p><span>{{$t('索引集')}}：</span>{{indexSetItem.index_set_name}}</p>
              <p><span>{{$t('索引')}}：</span>{{showResultTableID}}</p>
              <p><span>{{$t('来源')}}：</span>{{indexSetItem.scenario_name}}</p>
            </div>
            <div
              style="color: #3a84ff; cursor: pointer;"
              v-if="isCollector"
              @click="handleClickDetail">
              {{$t('更多详情')}}
              <span class="log-icon icon-lianjie"></span>
            </div>
          </div>
          <div
            class="operation-container"
            :data-test-id="`settingContainer_div_${showComponent}`">
            <component
              v-if="isShowPage"
              :is="showComponent"
              :global-editable="!isDebugRequest && globalEditable"
              :index-set-item="indexSetItem"
              :total-fields="totalFields"
              :config-data="configData"
              :clean-config="cleanConfig"
              :statistical-fields-data="statisticalFieldsData"
              @resetPage="resetPage"
              @updateLogFields="updateLogFields"
              @debugRequestChange="debugRequestChange" />
          </div>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import FullTextIndex from './full-text-index';
import LogCluster from './log-cluster';
import FieldExtraction from './field-extraction';

export default {
  components: {
    FullTextIndex,
    FieldExtraction,
    LogCluster,
  },
  props: {
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    selectChoice: {
      type: String,
      default: 'index',
    },
    indexSetItem: {
      type: Object,
      require: true,
    },
    totalFields: {
      type: Array,
      default: () => ([]),
    },
    configData: {
      type: Object,
      require: true,
    },
    cleanConfig: {
      type: Object,
      require: true,
    },
    statisticalFieldsData: { // 过滤条件字段可选值关系表
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isOpenPage: true,
      isShowPage: true,
      currentChoice: '', // 当前nav选中
      showComponent: '', // 当前显示的组件
      isSubmit: false, // 在当前设置页是否保存成功
      isDebugRequest: false,
      currentList: [
        // {
        //   id: 'index',
        //   componentsName: 'FullTextIndex',
        //   name: this.$t('全文索引'),
        //   isEditable: true,
        // },
        {
          id: 'extract',
          componentsName: 'FieldExtraction',
          name: this.$t('字段提取'),
          isEditable: false,
          isDisabled: false,
        },
        {
          id: 'clustering',
          componentsName: 'LogCluster',
          name: this.$t('日志聚类'),
          isEditable: false,
          isDisabled: false,
        }],
      showCurrentList: [],
    };
  },
  computed: {
    isDialogVisiable() {
      return this.isShowDialog;
    },
    globalEditable() {
      return this.showCurrentList.find(el => el.id === this.currentChoice)?.isEditable;
    },
    isCollector() { // 字段提取的索引集来源是否为采集项
      return this.cleanConfig?.extra?.collector_config_id !== null;
    },
    isExtractActive() { // 字段提取是否开启
      return this.cleanConfig?.is_active;
    },
    isClusteringActive() { // 日志聚类是否开启
      return this.configData?.is_active;
    },
    isSignatureActive() { // 日志聚类的数据指纹是否开启
      return this.configData?.extra?.signature_switch;
    },
    showResultTableID() {
      return this.indexSetItem?.indices[0]?.result_table_id || '';
    },
  },
  watch: {
    isDialogVisiable(val) {
      val && this.handleMenuStatus();
    },
    'indexSetItem.scenario_id': {
      immediate: true,
      handler(val) {
        this.setIsShowExtract(val === 'log');
      },
    },
  },
  methods: {
    handleMenuStatus() {
      const { isExtractActive, isClusteringActive, isCollector } = this;
      this.showCurrentList = this.showCurrentList.map((list) => {
        return {
          ...list,
          isEditable: list.id === 'extract' ? isExtractActive : isClusteringActive,
          isDisabled: list.id === 'extract' ? !isCollector : isClusteringActive,
        };
      });
    },
    /**
     * @desc: 离开当前页面无点击nav开关
     * @param { Object } item
     */
    handleNavClick(item) {
      if (item.id === this.currentChoice) return;

      if (this.isSubmit) {
        this.currentChoice = item.id;
        this.showComponent = item.componentsName;
        this.isSubmit = false;
        return;
      }
      this.$bkInfo({
        title: this.$t('是否放弃本次操作？'),
        confirmFn: () => {
          this.jumpCloseSwitch();
          this.currentChoice = item.id;
          this.showComponent = item.componentsName;
        },
      });
    },
    openPage() {
      if (this.isOpenPage) {
        this.currentChoice = this.selectChoice;
        this.showComponent = this.showCurrentList.find(el => el.id === this.selectChoice)?.componentsName;
        this.isOpenPage = false;
      }
    },
    /**
     * @desc: 离开当前页并点击nav开关
     * @param { Object } item
     */
    stopChangeSwitch(item) {
      if (item.isDisable) return;

      if (!item.isEditable) {
        // 当前tab不在操作的开关菜单 则跳转到对应菜单
        if (this.currentChoice !== item.id) {
          this.jumpCloseSwitch();
          this.currentChoice = item.id;
          this.showComponent = item.componentsName;
        }
        item.isEditable = true;
        return;
      }
      const msg = item.id === 'extract'
        ? this.$t('是否关闭字段提取？')
        : this.$t('是否关闭日志聚类？');

      if (item.id === 'extract') {
        this.$bkInfo({
          title: msg,
          confirmLoading: true,
          confirmFn: async () => {
            const isFinish = item.id === 'extract'
              ? await this.requestCloseClean()
              : await this.requestCloseCluster();
            isFinish && (item.isEditable = false);
          },
        });
      } else {
        item.isEditable = false;
      }
    },
    async requestCloseClean() {
      const { extra: { collector_config_id } } = this.cleanConfig;
      const res = await this.$http.request('/logClustering/closeClean', {
        params: {
          collector_config_id,
        },
        data: {
          collector_config_id,
        },
      });
      return res.result;
    },
    requestCloseCluster() {
      return true;
    },
    closeSetting() {
      this.$emit('closeSetting');
    },
    closePage() {
      this.isOpenPage = true;
      this.currentChoice = '';
      this.showComponent = '';
    },
    /**
     * @desc: 若nav的switch为关闭状态离开当前页面时判断是否发送保存请求，没有则关闭可编辑状态
     */
    jumpCloseSwitch() {
      if (!this.isClusteringActive && this.currentChoice === 'clustering') {
        this.showCurrentList[1].isEditable = false;
      }
      if (!this.isSubmit && this.currentChoice === 'extract'
       && this.showCurrentList[0].isDisabled !== true
       && !this.isExtractActive) {
        this.showCurrentList[0].isEditable = false;
      }
    },
    debugRequestChange(val) {
      this.isDebugRequest = val;
    },
    updateLogFields() {
      this.isSubmit = true;
      this.$emit('updateLogFields');
    },
    handleClickDetail() {
      const { extra: { collector_config_id: collectorID, collector_scenario_id: scenarioID } } = this.cleanConfig;
      if (!collectorID) return;
      const spaceUid = this.$store.state.spaceUid;
      const jumpUrl = scenarioID === 'custom'
        ? `/#/manage/custom-report/detail/${collectorID}?spaceUid=${spaceUid}`
        : `/#/manage/log-collection/collection-item/manage/${collectorID}?spaceUid=${spaceUid}`;
      window.open(jumpUrl, '_blank');
    },
    setIsShowExtract(state) {
      this.showCurrentList = this.currentList.filter(item => (state ? true : item.id !== 'extract'));
    },
    resetPage() {
      this.isShowPage = false;
      this.$nextTick(() => {
        this.isShowPage = true;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  ::v-deep .bk-dialog-body {
    background-color: #f5f6fa;
    overflow: hidden;
    padding: 0;
  }

  ::v-deep .bk-dialog-tool {
    display: none;
  }

  @mixin container-shadow() {
    background: #fff;
    border-radius: 2px;
    box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, .05);
  }

  .setting-container {
    height: calc(100vh - 52px);
    overflow-y: auto;
    min-width: 1460px;
    display: flex;
    justify-content: center;

    .setting-title {
      width: calc(100vw + 12px);
      height: 52px;
      min-width: 1460px;
      line-height: 52px;
      font-size: 16px;
      text-align: center;
      position: fixed;
      z-index: 999;
      background-color: #fff;
      border-bottom: 1px solid #dcdee5;
      // box-shadow:0 3px 6px #DEE0E7 ;
      .bk-icon {
        font-size: 32px;
        cursor: pointer;
        position: absolute;
        top: 10px;
        right: 24px;
      }
    }

    .setting-main {
      padding: 72px 40px 0;
      display: flex;
      position: relative;

      .setting-left {
        min-width: 240px;
        height: 365px;
        padding-top: 4px;

        @include container-shadow;

        .setting-option {
          height: 40px;
          font-size: 15px;
          margin: 4px 0;
          display: flex;
          cursor: pointer;
          justify-content: space-evenly;
          align-items: center;
          transition: all .3s;

          &:hover {
            @extend %current-color;
          }
        }
      }

      .setting-right {
        margin-left: 20px;
        max-width: 1000px;

        .more-details {
          height: 48px;
          padding: 0 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;

          @include container-shadow;

          .details {
            display: flex;

            p {
              margin-right: 40px;

              span {
                color: #979ba5;
              }
            }
          }
        }

        .operation-container {
          margin-top: 20px;
          min-height: 770px;
          padding: 24px 20px 100px;

          @include container-shadow;
        }
      }
    }

    %current-color,
    .current-color {
      color: #3a84ff;
      background-color: #e1ecff;
    }
  }
</style>
