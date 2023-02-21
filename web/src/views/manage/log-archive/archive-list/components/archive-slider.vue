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
  <div class="archive-slider-container">
    <bk-sideslider
      transfer
      :title="isEdit ? $t('编辑归档') : $t('新增归档')"
      :is-show="showSlider"
      :width="676"
      :quick-close="true"
      :before-close="handleCloseSideslider"
      @animation-end="$emit('hidden')"
      @update:isShow="updateIsShow">
      <div v-bkloading="{ isLoading: sliderLoading }" slot="content" class="archive-slider-content">
        <bk-form
          v-if="!sliderLoading"
          data-test-id="addNewArchive_div_formContainer"
          :model="formData"
          :label-width="160"
          :rules="basicRules"
          form-type="vertical"
          ref="validateForm"
          class="king-form">
          <bk-form-item
            :label="$t('选择采集项/采集插件')"
            required
            property="instance_id">
            <bk-select
              searchable
              v-model="formData.instance_id"
              data-test-id="formContainer_select_selectCollector"
              :clearable="false"
              :disabled="isEdit"
              @change="handleCollectorChange"
            >
              <bk-option-group
                show-collapse
                v-for="item in collectorList"
                :id="item.id"
                :name="item.name"
                :key="item.id"
              >
                <bk-option
                  v-for="option in item.list"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name"
                  :disabled="!option.permission[authorityMap.MANAGE_COLLECTION_AUTH]"
                >
                  {{ option.name }}
                </bk-option>
              </bk-option-group>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('归档仓库')"
            required
            property="target_snapshot_repository_name">
            <bk-select
              v-model="formData.target_snapshot_repository_name"
              data-test-id="formContainer_select_selectStorehouse"
              :disabled="isEdit || !formData.instance_id">
              <bk-option
                v-for="option in repositoryRenderList"
                :key="option.repository_name"
                :id="option.repository_name"
                :name="option.repository_name"
                :disabled="!option.permission[authorityMap.MANAGE_ES_SOURCE_AUTH]">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t('过期时间')"
            required
            property="snapshot_days">
            <bk-select
              style="width: 300px;"
              v-model="formData.snapshot_days"
              data-test-id="formContainer_select_selectExpireDate"
              :clearable="false">
              <div slot="trigger" class="bk-select-name">
                {{ getDaysStr }}
              </div>
              <template v-for="(option, index) in retentionDaysList">
                <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
              </template>
              <div slot="extension" style="padding: 8px 0;">
                <bk-input
                  v-model="customRetentionDay"
                  size="small"
                  type="number"
                  :placeholder="$t('输入自定义天数，按 Enter 确认')"
                  :show-controls="false"
                  @enter="enterCustomDay($event)"
                ></bk-input>
              </div>
            </bk-select>
          </bk-form-item>
          <bk-form-item style="margin-top: 40px;">
            <bk-button
              theme="primary"
              class="king-button mr10"
              data-test-id="formContainer_button_handleSubmit"
              :loading="confirmLoading"
              @click.stop.prevent="handleConfirm">
              {{ $t('提交') }}
            </bk-button>
            <bk-button
              data-test-id="formContainer_button_handleCancel"
              @click="handleCancel">{{ $t('取消') }}</bk-button>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import * as authorityMap from '../../../../../common/authority-map';

export default {
  props: {
    showSlider: {
      type: Boolean,
      default: false,
    },
    editArchive: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      confirmLoading: false,
      sliderLoading: false,
      customRetentionDay: '', // 自定义过期天数
      collectorList: [
        { id: 'collector_config', name: this.$t('采集项'), list: [] }, // 采集项
        { id: 'collector_plugin', name: this.$t('采集插件'), list: [] }, // 采集插件
      ], // 采集项列表
      repositoryOriginList: [], // 仓库列表
      // repositoryRenderList: [], // 根据采集项关联的仓库列表
      retentionDaysList: [], // 过期天数列表
      formData: {
        snapshot_days: '',
        instance_id: '',
        target_snapshot_repository_name: '',
      },
      collectorType: 'collector_config',
      basicRules: {},
      requiredRules: {
        required: true,
        trigger: 'blur',
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      globalsData: 'globals/globalsData',
    }),
    authorityMap() {
      return authorityMap;
    },
    isEdit() {
      return this.editArchive !== null;
    },
    repositoryRenderList() {
      let list = [];
      const collectorId = this.formData.instance_id;
      if (collectorId && this.collectorList.length && this.repositoryOriginList.length) {
        const targetList = this.collectorList.find(item => item.id === this.collectorType)?.list || [];
        const curCollector = targetList.find(collect => collect.id === collectorId);
        const clusterId = curCollector.storage_cluster_id;
        list = this.repositoryOriginList.filter(item => item.cluster_id === clusterId);
      }

      return list;
    },
    getDaysStr() {
      if (String(this.formData.snapshot_days) === '0') {
        return this.$t('永久');
      }
      return !!this.formData.snapshot_days ? this.formData.snapshot_days + this.$t('天') : '';
    },
  },
  watch: {
    async showSlider(val) {
      if (val) {
        this.sliderLoading = this.isEdit;
        await this.getCollectorList();
        await this.getRepoList();
        this.updateDaysList();

        if (this.isEdit) {
          const {
            instance_id: instanceId,
            target_snapshot_repository_name,
            snapshot_days,
            instance_type: instanceType,
          } = this.editArchive;
          Object.assign(this.formData, {
            instance_id: instanceId,
            target_snapshot_repository_name,
            snapshot_days,
          });
          this.collectorType = instanceType;
        }
      } else {
        // 清空表单数据
        this.formData = {
          snapshot_days: '',
          instance_id: '',
          target_snapshot_repository_name: '',
        };
      }
    },
  },
  created() {
    this.basicRules = {
      instance_id: [this.requiredRules],
      target_snapshot_repository_name: [this.requiredRules],
      snapshot_days: [this.requiredRules],
    };
  },
  methods: {
    // 获取采集项列表
    getCollectorList() {
      const query = {
        bk_biz_id: this.bkBizId,
        have_data_id: 1,
      };
      this.$http.request('collect/getAllCollectors', { query }).then((res) => {
        this.collectorList[0].list = res.data.map((item) => {
          return {
            id: item.collector_config_id,
            name: item.collector_config_name,
            ...item,
          };
        }) || [];
      });
      this.$http.request('collect/getCollectorPlugins', { query }).then((res) => {
        this.collectorList[1].list = res.data.map((item) => {
          return {
            id: item.collector_plugin_id,
            name: item.collector_plugin_name,
            ...item,
          };
        }) || [];
      });
    },
    // 获取归档仓库列表
    getRepoList() {
      this.$http.request('archive/getRepositoryList', {
        query: {
          bk_biz_id: this.bkBizId,
        },
      }).then((res) => {
        const { data } = res;
        this.repositoryOriginList = data || [];
      })
        .finally(() => {
          this.sliderLoading = false;
        });
    },
    handleCollectorChange(value) {
      this.collectorType = this.collectorList.find(item => item.list.some(val => val.id === value))?.id || '';
      this.formData.target_snapshot_repository_name = '';
    },
    updateIsShow(val) {
      this.$emit('update:showSlider', val);
    },
    handleCancel() {
      this.$emit('update:showSlider', false);
    },
    updateDaysList() {
      const retentionDaysList = [...this.globalsData.storage_duration_time].filter((item) => {
        return item.id;
      });
      retentionDaysList.push({
        default: false,
        id: '0',
        name: this.$t('永久'),
      });
      this.retentionDaysList = retentionDaysList;
    },
    // 输入自定义过期天数
    enterCustomDay(val) {
      const numberVal = parseInt(val.trim(), 10);
      const stringVal = numberVal.toString();
      if (numberVal) {
        if (!this.retentionDaysList.some(item => item.id === stringVal)) {
          this.retentionDaysList.push({
            id: stringVal,
            name: stringVal + this.$t('天'),
          });
        }
        this.formData.snapshot_days = stringVal;
        this.customRetentionDay = '';
        document.body.click();
      } else {
        this.customRetentionDay = '';
        this.messageError(this.$t('请输入有效数值'));
      }
    },
    // 采集项列表点击申请采集项目管理权限
    async applyProjectAccess(item) {
      this.$el.click(); // 手动关闭下拉
      try {
        this.$bkLoading();
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: item.collector_config_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$bkLoading.hide();
      }
    },
    async handleConfirm() {
      try {
        await this.$refs.validateForm.validate();
        let url = '/archive/createArchive';
        const params = {};
        let paramsData = {
          ...this.formData,
          instance_type: this.collectorType,
          bk_biz_id: this.bkBizId,
        };

        if (this.isEdit) {
          url = '/archive/editArchive';
          const { snapshot_days } = this.formData;
          const { archive_config_id } = this.editArchive;
          paramsData = {
            snapshot_days,
          };
          // eslint-disable-next-line camelcase
          params.archive_config_id = archive_config_id;
        }

        this.confirmLoading = true;
        await this.$http.request(url, {
          data: paramsData,
          params,
        });
        this.$bkMessage({
          theme: 'success',
          message: this.$t('保存成功'),
          delay: 1500,
        });
        this.$emit('updated');
      } catch (e) {
        console.warn(e);
      } finally {
        this.confirmLoading = false;
      }
    },
    async handleCloseSideslider() {
      return await this.showDeleteAlert();
    },
    /**
     * @desc: 如果提交可用则点击遮罩时进行二次确认弹窗
     */
    showDeleteAlert() {
      return new Promise((reject) => {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('是否放弃本次操作？'),
          confirmFn: () => {
            reject(true);
          },
          close: () => {
            reject(false);
          },
        });
      });
    },
  },
};
</script>

<style lang="scss" scoped>
  .archive-slider-content {
    height: calc(100vh - 60px);
    min-height: 394px;

    .king-form {
      padding: 10px 0 36px 36px;

      .bk-form-item {
        margin-top: 18px;
      }

      .bk-select {
        width: 300px;
      }
    }
  }
</style>
