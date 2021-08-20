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
  <div class="es-access-slider-container">
    <bk-sideslider
      transfer
      :title="isEdit ? $t('编辑数据源') : $t('新建数据源')"
      :is-show="showSlider"
      :width="640"
      :quick-close="false"
      @animation-end="$emit('hidden')"
      @update:isShow="updateIsShow">
      <div v-bkloading="{ isLoading: sliderLoading }" slot="content" class="king-slider-content">
        <bk-form
          v-if="!sliderLoading"
          :model="formData"
          :label-width="150"
          :rules="basicRules"
          form-type="vertical"
          ref="validateForm"
          class="king-form">
          <bk-form-item :label="$t('名称')" required property="cluster_name">
            <bk-input v-model="formData.cluster_name" maxlength="50" :readonly="isEdit"></bk-input>
          </bk-form-item>
          <bk-form-item :label="$t('来源')" required property="source">
            <div class="source-item">
              <bk-select style="width:154px;margin-right:10px;"></bk-select>
              <bk-input v-model="formData.cluster_name" maxlength="50" :readonly="isEdit"></bk-input>
            </div>
          </bk-form-item>
          <bk-form-item :label="$t('可见范围')" required property="visible_range">
            <div class="selected-tag">
              <bk-tag class="tag-icon is-active" closable>业务名称1</bk-tag>
              <bk-tag class="tag-icon is-normal" closable>业务名称2</bk-tag>
              <bk-tag
                class="tag-icon is-active"
                closable
                v-bk-tooltips="inUseProjectPopover">
                业务名称3
              </bk-tag>
            </div>
            <bk-select></bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('地址')" required property="domain_name">
            <bk-input v-model="formData.domain_name" :readonly="isEdit"></bk-input>
          </bk-form-item>
          <bk-form-item :label="$t('端口')" required property="port">
            <bk-input
              v-model="formData.port"
              :readonly="isEdit"
              type="number"
              :min="0"
              :max="65535"
              :show-controls="false">
            </bk-input>
          </bk-form-item>
          <bk-form-item :label="$t('协议')" required>
            <bk-select v-model="formData.schema" :clearable="false">
              <bk-option id="http" name="http"></bk-option>
              <bk-option id="https" name="https"></bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('用户名')">
            <bk-input v-model="formData.auth_info.username"></bk-input>
          </bk-form-item>
          <bk-form-item :label="$t('密码')">
            <bk-input type="password" v-model="formData.auth_info.password"></bk-input>
          </bk-form-item>
          <bk-form-item label="">
            <div class="test-container">
              <bk-button type="button" theme="primary" :loading="connectLoading" @click="handleTestConnect">
                {{ $t('连通性测试') }}
              </bk-button>
              <div v-if="connectResult === 'success'" class="success-text">
                <i class="bk-icon icon-check-circle-shape"></i>{{ $t('连通成功！') }}
              </div>
              <div v-else-if="connectResult === 'failed'" class="error-text">
                <i class="bk-icon icon-close-circle-shape"></i>{{ $t('连通失败！') }}
              </div>
            </div>
          </bk-form-item>
          <bk-form-item label="" v-if="connectResult === 'failed' && connectFailedMessage">
            <div class="connect-message">{{ connectFailedMessage }}</div>
          </bk-form-item>
          <template v-if="connectResult === 'success'">
            <bk-form-item :label="$t('冷热集群设置')">
              <div class="form-flex-container">
                <bk-switcher
                  v-model="formData.enable_hot_warm"
                  theme="primary"
                  size="large"
                  :disabled="isDisableHotSetting"></bk-switcher>
                <template v-if="isDisableHotSetting && !connectLoading">
                  <span class="bk-icon icon-info"></span>
                  <span style="font-size:12px;">{{ $t('没有获取到正确的标签，') }}</span>
                  <a :href="configDocUrl" target="_blank" class="button-text">{{ $t('查看具体的配置方法') }}</a>
                </template>
              </div>
            </bk-form-item>
            <bk-form-item v-if="formData.enable_hot_warm" :label="$t('热数据标签')">
              <div class="form-flex-container">
                <bk-select v-model="selectedHotId" style="width: 300px;" @change="handleHotSelected">
                  <template v-for="option in hotColdAttrSet">
                    <bk-option
                      :key="option.computedId"
                      :id="option.computedId"
                      :disabled="option.isSelected"
                      :name="`${option.computedName}(${option.computedCounts})`">
                    </bk-option>
                  </template>
                </bk-select>
                <div
                  v-if="formData.hot_attr_name && formData.hot_attr_value"
                  class="button-text"
                  @click="handleViewInstanceList('hot')">
                  <span class="bk-icon icon-eye"></span>{{ $t('查看实例列表') }}
                </div>
              </div>
            </bk-form-item>
            <bk-form-item v-if="formData.enable_hot_warm" :label="$t('冷数据标签')">
              <div class="form-flex-container">
                <bk-select v-model="selectedColdId" style="width: 300px;" @change="handleColdSelected">
                  <template v-for="option in hotColdAttrSet">
                    <bk-option
                      :key="option.computedId"
                      :id="option.computedId"
                      :disabled="option.isSelected"
                      :name="`${option.computedName}(${option.computedCounts})`">
                    </bk-option>
                  </template>
                </bk-select>
                <div
                  v-if="formData.warm_attr_name && formData.warm_attr_value"
                  class="button-text"
                  @click="handleViewInstanceList('cold')">
                  <span class="bk-icon icon-eye"></span>{{ $t('查看实例列表') }}
                </div>
              </div>
            </bk-form-item>
          </template>
          <bk-form-item style="margin-top:40px;">
            <bk-button
              theme="primary"
              class="king-button mr10"
              :loading="confirmLoading"
              :disabled="connectResult !== 'success' || invalidHotSetting"
              @click.stop.prevent="handleConfirm">
              {{ $t('提交') }}
            </bk-button>
            <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
          </bk-form-item>
        </bk-form>
      </div>
      <!-- <div slot="footer" class="king-slider-footer">
        <bk-button
          theme="primary" class="king-button mr20"
          :loading="confirmLoading"
          :disabled="connectResult !== 'success' || invalidHotSetting"
          @click.stop.prevent="handleConfirm">{{ $t('确认') }}
        </bk-button>
        <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
      </div> -->
    </bk-sideslider>
    <!-- 查看实例列表弹窗 -->
    <es-dialog
      v-model="showInstanceDialog"
      :list="hotColdOriginList"
      :type="viewInstanceType"
      :form-data="formData"
    ></es-dialog>
  </div>
</template>

<script>
import EsDialog from './EsDialog';
import { mapGetters } from 'vuex';

export default {
  components: {
    EsDialog,
  },
  props: {
    showSlider: {
      type: Boolean,
      default: false,
    },
    editClusterId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      configDocUrl: window.BK_HOT_WARM_CONFIG_URL,
      confirmLoading: false,
      sliderLoading: false,
      formData: {
        cluster_name: '', // 集群名
        domain_name: '', // 地址
        port: '', // 端口
        schema: 'http', // 协议
        auth_info: {
          username: '', // 用户名
          password: '', // 密码
        },
        enable_hot_warm: false, // 是否开启冷热数据
        hot_attr_name: '', // 热节点属性名称
        hot_attr_value: '', // 热节点属性值
        warm_attr_name: '', // 冷节点属性名称
        warm_attr_value: '', // 冷节点属性值
      },
      basicRules: {
        cluster_name: [{
          required: true,
          trigger: 'blur',
        }],
        domain_name: [{
          required: true,
          trigger: 'blur',
        }],
        port: [{
          required: true,
          trigger: 'blur',
        }],
      },

      connectLoading: false,
      connectResult: '', // success failed
      connectFailedMessage: '',

      hotColdOriginList: [], // 新增编辑时的冷热数据
      hotColdAttrSet: [], // 相同 attr value 的集合
      selectedHotId: '', // 热 attr:value
      selectedColdId: '', // 冷 attr:value
      showInstanceDialog: false, // 查看实例列表
      viewInstanceType: '', // hot、cold 查看热数据/冷数据实例列表
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    isEdit() {
      return this.editClusterId !== null;
    },
    // 冷热设置不对，禁用提交
    invalidHotSetting() {
      return this.formData.enable_hot_warm && !(this.formData.hot_attr_value && this.formData.warm_attr_value);
    },
    // 标签数量不足，禁止开启冷热设置
    isDisableHotSetting() {
      return this.hotColdAttrSet.length < 2;
    },
    inUseProjectPopover() {
      return {
        theme: 'light',
        content: this.$t('inUseProjectTip'),
      };
    },
  },
  watch: {
    showSlider(val) {
      if (val) {
        if (this.isEdit) {
          this.editDataSource();
        } else {
          //
        }
      } else {
        // 清空表单数据
        this.formData = {
          cluster_name: '', // 集群名
          domain_name: '', // 地址
          port: '', // 端口
          schema: 'http', // 协议
          auth_info: {
            username: '', // 用户名
            password: '', // 密码
          },
          enable_hot_warm: false, // 是否开启冷热数据
          hot_attr_name: '', // 热节点属性名称
          hot_attr_value: '', // 热节点属性值
          warm_attr_name: '', // 冷节点属性名称
          warm_attr_value: '', // 冷节点属性值
        };
        // 清空连通测试结果
        this.connectResult = '';
        this.connectFailedMessage = '';
      }
    },
  },
  methods: {
    updateIsShow(val) {
      this.$emit('update:showSlider', val);
    },
    // 编辑 es 源，回填数据
    async editDataSource() {
      try {
        this.sliderLoading = true;
        const res = await this.$http.request('/source/info', {
          params: {
            cluster_id: this.editClusterId,
            bk_biz_id: this.bkBizId,
          },
        });
        this.formData = {
          cluster_name: res.data.cluster_config.cluster_name, // 集群名
          domain_name: res.data.cluster_config.domain_name, // 地址
          port: res.data.cluster_config.port, // 端口
          schema: res.data.cluster_config.schema, // 协议
          auth_info: {
            username: res.data.auth_info.username, // 用户名
            password: res.data.auth_info.password || '******', // 密码
          },
          enable_hot_warm: res.data.cluster_config.enable_hot_warm, // 是否开启冷热数据
          hot_attr_name: res.data.cluster_config.custom_option?.hot_warm_config?.hot_attr_name || '', // 热节点属性名称
          hot_attr_value: res.data.cluster_config.custom_option?.hot_warm_config?.hot_attr_value || '', // 热节点属性值
          warm_attr_name: res.data.cluster_config.custom_option?.hot_warm_config?.warm_attr_name || '', // 冷节点属性名称
          warm_attr_value: res.data.cluster_config.custom_option?.hot_warm_config?.warm_attr_value || '', // 冷节点属性值
        };
      } catch (e) {
        console.warn(e);
      } finally {
        this.sliderLoading = false;
      }
    },

    // 连通性测试
    async handleTestConnect() {
      try {
        await this.$refs.validateForm.validate();
        const postData = {
          bk_biz_id: this.bkBizId,
          cluster_name: this.formData.cluster_name, // 集群名
          domain_name: this.formData.domain_name, // 地址
          port: this.formData.port, // 端口
          schema: this.formData.schema, // 协议
          es_auth_info: {
            username: this.formData.auth_info.username,
            password: this.formData.auth_info.password,
          },
        };
        if (this.isEdit) {
          postData.cluster_id = this.editClusterId;
        }
        if (postData.es_auth_info.password === '******') {
          postData.es_auth_info.password = '';
        }
        this.connectLoading = true;
        const res = await this.$http.request('/source/connectivityDetect', { data: postData });
        if (res.data) {
          this.connectResult = 'success';
          // 连通性测试通过之后获取冷热数据
          const attrsRes = await this.$http.request('/source/getNodeAttrs', { data: postData });
          this.hotColdOriginList = attrsRes.data;
        } else {
          this.connectResult = 'failed';
          this.connectFailedMessage = res.message;
          this.hotColdOriginList = [];
        }
      } catch (e) {
        console.warn(e);
        this.connectResult = 'failed';
        this.connectFailedMessage = e.message;
        this.hotColdOriginList = [];
      } finally {
        this.connectLoading = false;
        this.dealWithHotColdData();
      }
    },
    dealWithHotColdData() {
      const hotColdAttrSet = [];
      this.hotColdOriginList.forEach((item) => {
        const newItem = { ...item };
        newItem.computedId = `${item.attr}:${item.value}`;
        newItem.computedName = `${item.attr}:${item.value}`;
        newItem.computedCounts = 1;
        newItem.isSelected = false;
        const existItem = hotColdAttrSet.find(item => item.computedId === newItem.computedId);
        if (existItem) {
          existItem.computedCounts += 1;
        } else {
          hotColdAttrSet.push(newItem);
        }
      });
      this.hotColdAttrSet = hotColdAttrSet;
      this.selectedHotId = this.formData.hot_attr_name ? (`${this.formData.hot_attr_name}:${this.formData.hot_attr_value}`) : '';
      this.selectedColdId = this.formData.warm_attr_name ? (`${this.formData.warm_attr_name}:${this.formData.warm_attr_value}`) : '';
    },
    handleHotSelected(value) {
      const item = this.hotColdAttrSet.find(item => item.computedId === value);
      this.formData.hot_attr_name = item?.attr || '';
      this.formData.hot_attr_value = item?.value || '';
      this.computeIsSelected();
    },
    handleColdSelected(value) {
      const item = this.hotColdAttrSet.find(item => item.computedId === value);
      this.formData.warm_attr_name = item?.attr || '';
      this.formData.warm_attr_value = item?.value || '';
      this.computeIsSelected();
    },
    computeIsSelected() {
      for (const item of this.hotColdAttrSet) {
        item.isSelected = this.selectedColdId === item.computedId || this.selectedHotId === item.computedId;
      }
    },
    handleViewInstanceList(type) {
      this.viewInstanceType = type;
      this.showInstanceDialog = true;
    },

    // 确认提交新增或编辑
    async handleConfirm() {
      try {
        await this.$refs.validateForm.validate();
        let url = '/source/create';
        const paramsData = {
          bk_biz_id: this.bkBizId,
        };
        const postData = JSON.parse(JSON.stringify(this.formData));
        if (!postData.enable_hot_warm) {
          delete postData.hot_attr_name;
          delete postData.hot_attr_value;
          delete postData.warm_attr_name;
          delete postData.warm_attr_value;
        }
        if (this.isEdit) {
          url = '/source/update';
          paramsData.cluster_id = this.editClusterId;
          if (postData.auth_info.password === '******') {
            postData.auth_info.password = '';
          }
        }
        this.confirmLoading = true;
        await this.$http.request(url, {
          data: postData,
          params: paramsData,
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
    handleCancel() {
      this.$emit('update:showSlider', false);
    },
  },
};
</script>

<style lang="scss" scoped>
  .king-slider-content {
      min-height: 394px;

      .king-form {
        padding: 16px 140px 36px 36px;

        .form-flex-container {
          display: flex;
          align-items: center;
          // height: 32px;
          // font-size: 12px;
          color: #63656e;

          .icon-info {
            margin: 0 8px 0 24px;
            font-size: 14px;
            color: #3a84ff;
          }

          .button-text {
            font-size: 12px;
            .icon-eye {
              margin: 0 6px 0 16px;
            }
          }
        }
        .bk-form-item {
          margin-top: 18px;
        }
        .source-item {
          display: flex;
        }
        .selected-tag {
          .bk-tag {
            position: relative;
            margin: 0 10px 10px 0;
            padding-left: 18px;
          }
          .tag-icon::before {
            position: absolute;
            top: 9px;
            left: 8px;
            content: '';
            width: 4px;
            height: 4px;
            border-radius: 50%;
          }
          .is-active::before {
            background-color: #45e35f;
          }
          .is-normal::before {
            background-color: #699df4;
          }
        }
      }
    }

    .king-slider-footer {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      width: 100%;
      height: 100%;
      padding-right: 36px;
      background-color: #fff;
      border-top: 1px solid #dcdee5;

      .king-button {
        min-width: 86px;
      }
    }

    .test-container {
      margin-top: 10px;
      font-size: 14px;
      color: #63656e;
      display: flex;
      align-items: center;

      .success-text .bk-icon {
        color: rgb(45, 203, 86);
        margin: 0 6px 0 10px;
      }

      .error-text .bk-icon {
        color: rgb(234, 54, 54);
        margin: 0 6px 0 10px;
      }
    }

    .connect-message {
      font-size: 14px;
      line-height: 18px;
      color: #63656e;
    }
</style>
