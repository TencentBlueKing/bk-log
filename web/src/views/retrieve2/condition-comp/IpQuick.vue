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
  <div class="ip-quick-container">
    <div v-if="hostScopes.modules.length" class="tag" @click="openDialog">
      <!-- <span class="bk-icon icon-close-circle-shape" @click="removeSelections"></span> -->
      {{ $t('已选择') + ' ' + hostScopes.modules.length + ' ' + $t('个模块') }}
      <span class="bk-icon icon-close-line" @click.stop="removeSelections"></span>
    </div>
    <div v-if="hostScopesIps.length" class="tag" @click="openDialog">
      <!-- <span class="bk-icon icon-close-circle-shape" @click="removeSelections"></span> -->
      {{ $t('已选择') + ' ' + hostScopesIps.length + ' ' + $t('个IP') }}
      <span class="bk-icon icon-close-line" @click.stop="removeSelections"></span>
    </div>
    <!-- <div class="tag add-tag" @click="openDialog">
            <span class="bk-icon icon-plus-line"></span>
            <span class="add-text" v-if="!hostScopes.modules.length && !hostScopesIps.length">{{ $t('添加IP') }}</span>
        </div> -->

    <bk-dialog
      v-model="showDialog"
      header-position="left"
      :title="$t('retrieve.ipSelect')"
      :ok-text="$t('btn.save')"
      :width="600"
      :mask-close="false"
      :esc-close="false"
      :draggable="false"
      @confirm="handleConfirm"
      @after-leave="handleLeave">
      <div class="ip-quick-dialog" v-bkloading="{ isLoading }">
        <div class="select-type">
          <div class="bk-button-group">
            <bk-button @click="activeTab = 'module'" :class="showModule && 'is-selected'">
              {{ $t('retrieve.topologySelection') }}
            </bk-button>
            <bk-button @click="activeTab = 'ip'" :class="!showModule && 'is-selected'">
              {{ $t('retrieve.manualInput') }}
            </bk-button>
          </div>
          <div v-show="showModule" class="selected-information">
            {{ $t('retrieve.selected') + modulesValue.length + $t('retrieve.modules') }}
          </div>
          <div v-show="!showModule" class="selected-information">
            {{ $t('retrieve.entered') + invalidIpList.length + $t('retrieve.ips') }}
          </div>
        </div>
        <!-- 拓扑模块选择 -->
        <div v-show="showModule" class="module-selector">
          <bk-input
            class="king0input" :placeholder="$t('btn.search') + '...'"
            v-model="moduleSearchKeyword"
            @enter="searchModule"></bk-input>
          <bk-tree
            ref="bizTopo"
            :data="moduleList"
            :node-key="'bk_inst_id'"
            :multiple="true"
            :has-border="true"
            :show-icon="false"
            @on-check="handleCheckModule">
          </bk-tree>
        </div>
        <!-- 手动输入IP -->
        <bk-input
          v-show="!showModule"
          v-model.trim="ipsValue"
          class="ip-selector"
          type="textarea"
          :placeholder="$t('retrieve.ipPlaceholder')"
          data-test-id="addIP_input_manualInputIP"
        ></bk-input>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
export default {
  props: {
    hostScopes: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showDialog: false,
      isLoading: true,
      activeTab: 'module', // module/ip
      moduleList: [],
      modulesValue: [],
      moduleSearchKeyword: '',
      ipsValue: '',
      invalidIpList: [],
    };
  },
  computed: {
    showModule() {
      return this.activeTab === 'module';
    },
    hostScopesIps() {
      return this.hostScopes.ips.split(',').map(ip => ip.trim())
        .filter(Boolean);
    },
  },
  watch: {
    ipsValue(val) {
      const reg = /((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)/;
      const inputList = new Set(val.split(/\s|,|;/));
      const invalidList = [];
      for (const item of [...inputList]) {
        const ip = item.trim();
        if (ip && reg.test(ip)) {
          invalidList.push(ip);
        }
      }
      this.invalidIpList = invalidList;
    },
  },
  methods: {
    openDialog() {
      this.showDialog = true;
      if (this.hostScopes.ips) {
        this.activeTab = 'ip';
      }
      // 请求模块列表，回填参数模块
      this.$http.request('retrieve/getIpTree', {
        params: {
          bk_biz_id: localStorage.getItem('bk_biz_id'),
        },
      }).then((res) => {
        const list = this.filterTopoData(res.data);
        this.initTopoData(list, true);
        this.moduleList = list;
        this.handleCheckModule();
      })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.isLoading = false;
        });
      // 回填参数IP
      this.ipsValue = this.hostScopes.ips.split(',').join(',\n');
    },
    // 把获取的topo数据转换为组件需要的结构
    filterTopoData(data) {
      const result = Array.isArray(data) ? [] : {};
      for (const key in data) {
        // eslint-disable-next-line no-prototype-builtins
        if (data.hasOwnProperty(key)) {
          const newKey = key === 'child' ? 'children' : (key === 'bk_inst_name' ? 'name' : key);
          if (typeof data[key] === 'object') {
            result[newKey] = this.filterTopoData(data[key]);
          } else {
            result[newKey] = data[key];
          }
        }
      }
      return result;
    },
    // 回填已选择的模块
    initTopoData(data, expanded = false) {
      data.forEach((item) => {
        item.expanded = expanded;
        if (this.hostScopes.modules.find(moduleItem => moduleItem.bk_inst_id === item.bk_inst_id)) {
          item.checked = true;
        }
        if (item.children?.length) {
          this.initTopoData(item.children);
        }
      });
    },
    handleCheckModule() {
      this.$nextTick(() => {
        this.modulesValue = this.$refs.bizTopo.getNode(['bk_inst_id', 'bk_obj_id']);
      });
    },
    searchModule() {
      this.$refs.bizTopo.searchNode(this.moduleSearchKeyword);
    },

    // 移除已选择的模块或IP
    removeSelections() {
      this.$emit('confirm', {
        modules: [],
        ips: '',
      });
    },

    handleConfirm() {
      const data = this.showModule ? {
        modules: this.modulesValue,
        ips: '',
      } : {
        modules: [],
        ips: this.invalidIpList.join(','),
      };
      this.$emit('confirm', data);
    },
    handleLeave() {
      this.isLoading = true;
      this.activeTab = 'module';
      this.moduleList = [];
      this.modulesValue = [];
      this.moduleSearchKeyword = '';
      this.ipsValue = '';
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../../../scss/mixins/scroller';

  .ip-quick-container {
    display: flex;
    flex-flow: wrap;
    max-height: 102px;
    overflow: auto;
    margin-right: 3px;

    @include scroller($backgroundColor: #c4c6cc, $width: 4px);

    .tag {
      position: relative;
      padding: 0 28px 0 10px;
      margin-right: 2px;
      margin-bottom: 2px;
      background: #eceef5;
      border-radius: 2px;
      font-size: 12px;
      color: #63656e;
      line-height: 32px;
      white-space: nowrap;
      cursor: pointer;
      // .icon-close-circle-shape {
      //     display: none;
      //     position: absolute;
      //     right: 0;
      //     top: 0;
      //     cursor: pointer;
      //     font-size: 16px;
      // }
      // &:hover {
      //     .icon-close-circle-shape {
      //         display: block;
      //         &:hover {
      //             color: #ea3636;
      //         }
      //     }
      // }
      &.add-tag {
        padding: 0 7px;
        cursor: pointer;

        .icon-plus-line {
          font-size: 14px;
        }

        .add-text {
          margin-right: 3px;
        }

        &:hover {
          color: #3a84ff;
        }
      }

      .icon-close-line {
        display: none;
        position: absolute;
        right: 8px;
        top: 10px;
        margin: 0 0 0 6px;
        font-size: 12px;
        color: #c4c6cc;
        cursor: pointer;
      }
    }

    .tag:hover {
      .icon-close-line {
        display: inline-block;
      }
    }
  }

  .ip-quick-dialog {
    .select-type {
      display: flex;
      align-items: center;
      margin-bottom: 20px;

      .selected-information {
        margin-left: 20px;
      }
    }

    .module-selector {
      padding: 16px;
      border: 1px solid #c4c6cc;
      height: 310px;
      overflow-y: auto;
    }

    .ip-selector /deep/ .bk-form-textarea {
      height: 308px;
    }
  }
</style>
