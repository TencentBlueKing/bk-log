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
  <bk-dialog
    v-model="showDialog"
    header-position="left"
    :title="$t('新增索引')"
    :width="680"
    :mask-close="false"
    :show-footer="false">
    <div class="slot-container" v-bkloading="{ isLoading: basicLoading }">
      <bk-form :model="formData" :label-width="100" :rules="formRules" ref="formRef">
        <bk-form-item :label="$t('索引')" required property="resultTableId">
          <bk-select
            searchable
            :clearable="false"
            v-model="formData.resultTableId"
            data-test-id="addIndex_select_selectIndex"
            @selected="handleCollectionSelected">
            <bk-option
              v-for="item in getShowCollectionList"
              class="custom-no-padding-option"
              :disabled="parentData.indexes.some(selectedItem => item.result_table_id === selectedItem.result_table_id)"
              :key="item.result_table_id"
              :id="item.result_table_id"
              :name="`${item.result_table_name_alias}(${item.result_table_id})`">
              <div
                v-if="scenarioId === 'log'
                  && !(item.permission && item.permission[authorityMap.MANAGE_COLLECTION_AUTH])"
                class="option-slot-container no-authority" @click.stop>
                <span class="text">{{ item.result_table_name_alias }}</span>
                <span class="apply-text" @click="applyCollectorAccess(item)">{{ $t('申请权限') }}</span>
              </div>
              <div v-else class="option-slot-container">{{ item.result_table_name_alias }}</div>
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="">
          <bk-table
            v-bkloading="{ isLoading: tableLoading }"
            :data="tableData"
            max-height="400">
            <bk-table-column :label="$t('字段')" prop="field_name" min-width="240"></bk-table-column>
            <bk-table-column :label="$t('类型')" prop="field_type" min-width="250"></bk-table-column>
            <div slot="empty">
              <empty-status empty-type="empty" />
            </div>
          </bk-table>
        </bk-form-item>
      </bk-form>
      <div slot="footer" class="button-footer">
        <bk-button
          class="king-button"
          theme="primary"
          data-test-id="addIndex_button_confirm"
          :loading="confirmLoading"
          @click="handleConfirm">
          {{ $t('添加') }}
        </bk-button>
        <bk-button class="king-button" @click="handleCancel">{{ $t('取消') }}</bk-button>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import { mapState } from 'vuex';
import * as authorityMap from '../../../../../../common/authority-map';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    EmptyStatus,
  },
  props: {
    parentData: {
      type: Object,
      required: true,
    },
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      showDialog: false,
      basicLoading: false,
      tableLoading: false,
      confirmLoading: false,
      collectionList: [], // log bkdata 下拉列表
      tableData: [], // log bkdata 表格
      formData: {
        resultTableId: '',
      },
      formRules: {
        resultTableId: [{
          required: true,
          trigger: 'blur',
        }],
      },
    };
  },
  computed: {
    ...mapState(['spaceUid', 'bkBizId']),
    authorityMap() {
      return authorityMap;
    },
    getShowCollectionList() {
      if (this.parentData.storage_cluster_id) {
        return this.collectionList.filter(item => item.storage_cluster_id === this.parentData.storage_cluster_id);
      }
      return this.collectionList;
    },
  },
  mounted() {
    this.fetchCollectionList();
  },
  methods: {
    openDialog() {
      this.showDialog = true;
      Object.assign(this, {
        basicLoading: false,
        tableLoading: false,
        confirmLoading: false,
        tableData: [], // log bkdata 表格
        formData: {
          resultTableId: '',
        },
      });
    },
    // 获取下拉列表
    async fetchCollectionList() {
      try {
        this.basicLoading = true;
        const res = await this.$http.request('/resultTables/list', {
          query: {
            scenario_id: this.scenarioId,
            bk_biz_id: this.bkBizId,
          },
        });
        this.collectionList = res.data.map((item) => {
          // 后端要传这个值，虽然不太合理
          item.bk_biz_id = this.bkBizId;
          return item;
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    // 选择采集项
    async handleCollectionSelected(id) {
      try {
        this.tableLoading = true;
        const res = await this.$http.request('/resultTables/info', {
          params: {
            result_table_id: id,
          },
          query: {
            scenario_id: this.scenarioId,
            bk_biz_id: this.bkBizId,
          },
        });
        this.tableData = res.data.fields;
        this.tableLoading = false;
      } catch (e) {
        console.warn(e);
      }
    },
    // 采集项-申请权限
    async applyCollectorAccess(option) {
      try {
        this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: option.collector_config_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    // 确认添加
    async handleConfirm() {
      try {
        await this.$refs.formRef.validate();
        this.confirmLoading = true;
        const data = {
          scenario_id: this.scenarioId,
          basic_indices: this.parentData.indexes.map(item => ({
            index: item.result_table_id,
          })),
          append_index: {
            index: this.formData.resultTableId,
          },
        };
        await this.$http.request('/resultTables/adapt', { data });
        this.$emit('selected', this.collectionList.find(item => item.result_table_id === this.formData.resultTableId));
        this.showDialog = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.confirmLoading = false;
      }
    },
    handleCancel() {
      this.showDialog = false;
    },
  },
};
</script>

<style scoped lang="scss">
  .slot-container {
    min-height: 363px;
    padding-right: 40px;

    ::v-deep .bk-form {
      .bk-label {
        text-align: left;
      }
    }

    .button-footer {
      text-align: right;
      margin-top: 20px;

      .king-button {
        width: 86px;

        &:first-child {
          margin-right: 8px;
        }
      }
    }
  }
</style>
