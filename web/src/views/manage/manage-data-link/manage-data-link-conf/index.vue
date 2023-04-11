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
  <div class="link-configuration-container" data-test-id="linkConfiguration_div_linkConfigBox">
    <div class="header">
      <bk-button
        theme="primary"
        style="width: 120px;"
        @click="createConfig"
        data-test-id="linkConfigBox_button_addNewLinkConfig"
      >{{ $t('新建') }}</bk-button>
    </div>
    <bk-table
      :data="tableData"
      :empty-text="$t('暂无内容')"
      v-bkloading="{ isLoading: tableLoading }"
      data-test-id="linkConfigBox_table_linkConfigTable">
      <bk-table-column
        :label="$t('链路名称')"
        :render-header="$renderHeader"
        prop="link_group_name"
        min-width="20"></bk-table-column>
      <bk-table-column
        :label="$t('允许的空间')"
        :render-header="$renderHeader"
        prop="bk_biz_id"
        min-width="20">
        <template slot-scope="{ row }">
          <div>{{ filterProjectName(row) || '--'}}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('链路信息')" :render-header="$renderHeader" min-width="60">
        <template slot-scope="{ row }">
          <div>{{ filterLinkInformation(row) || '' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('备注')" :render-header="$renderHeader" min-width="20">
        <div style="padding: 10px 0;" slot-scope="{ row }">
          {{ row.description || '--' }}
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('是否启用')" :render-header="$renderHeader" min-width="10">
        <template slot-scope="{ row }">
          <div>{{ row.is_active ? $t('是') : $t('否') }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" :render-header="$renderHeader" min-width="10">
        <template slot-scope="props">
          <bk-button
            theme="primary"
            text
            @click="editConfig(props.row)">
            {{ $t('编辑') }}
          </bk-button>
          <!--<bk-button theme="primary" text @click="deleteConfig(props.row)">{{ $t('删除') }}</bk-button>-->
        </template>
      </bk-table-column>
      <div slot="empty">
        <empty-status :empty-type="emptyType" @operation="handleOperation" />
      </div>
    </bk-table>
    <config-dialog
      :visible.sync="dialogSetting.visible"
      :type="dialogSetting.type"
      :project-list="projectList"
      :data-source="dialogSetting.dataSource"
      :select-data="selectData"
      @showUpdateList="getLinkData" />
  </div>
</template>

<script>
import ConfigDialog from './config-dialog';
import EmptyStatus from '@/components/empty-status';

export default {
  name: 'LinkConfiguration',
  components: {
    ConfigDialog,
    EmptyStatus,
  },
  data() {
    return {
      tableData: [],
      tableLoading: false,
      dialogSetting: {
        visible: false,
        type: 'create', // create edit
        dataSource: {},
      },
      selectData: {
        kafka: [],
        transfer: [],
        es: [],
      },
      emptyType: 'empty',
    };
  },
  computed: {
    projectList() {
      return [
        { bk_biz_id: '0', space_full_code_name: this.$t('全部空间') },
        ...this.$store.state.mySpaceList,
      ];
    },
  },
  created() {
    this.init();
  },
  methods: {
    async init() {
      try {
        this.tableLoading = true;
        const [listRes, kafkaRes, transferRes, esRes] = await Promise.all([
          this.$http.request('linkConfiguration/getLinkList'),
          this.$http.request('linkConfiguration/getClusterList', { query: { cluster_type: 'kafka' } }),
          this.$http.request('linkConfiguration/getClusterList', { query: { cluster_type: 'transfer' } }),
          this.$http.request('linkConfiguration/getClusterList', { query: { cluster_type: 'es' } }),
        ]);

        listRes.data.forEach((item) => {
          item.bk_biz_id += '';
        });
        this.tableData = listRes.data;
        Object.assign(this.selectData, {
          kafka: kafkaRes.data,
          transfer: transferRes.data,
          es: esRes.data,
        });
      } catch (e) {
        console.warn(e);
        this.emptyType = '500';
      } finally {
        this.tableLoading = false;
      }
    },
    async getLinkData() {
      try {
        this.tableLoading = true;
        const res = await this.$http.request('linkConfiguration/getLinkList');
        res.data.forEach((item) => {
          item.bk_biz_id += '';
        });
        this.tableData = res.data;
      } catch (e) {
        this.tableData.splice(0);
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    filterProjectName(row) {
      return this.projectList.find(item => item.bk_biz_id === row.bk_biz_id)?.space_name;
    },
    filterLinkInformation(row) {
      const kafkaName = this.selectData.kafka.find((item) => {
        return item.cluster_id === row.kafka_cluster_id;
      })?.cluster_name;
      if (!kafkaName) {
        return '';
      }
      const transferName = this.selectData.transfer.find((item) => {
        return item.cluster_id === row.transfer_cluster_id;
      })?.cluster_name;
      if (!transferName) {
        return '';
      }
      const esNameList = row.es_cluster_ids.map(id => this.selectData.es.find((item) => {
        return item.cluster_id === id;
      // eslint-disable-next-line camelcase
      })?.cluster_name);
      if (!esNameList.length || esNameList.includes(undefined)) {
        return '';
      }
      const esName = esNameList.join(', ');

      return `Kafka（${kafkaName}）—> Transfer（${transferName}）—> ES（${esName}）`;
    },
    createConfig() {
      this.dialogSetting = {
        visible: true,
        type: 'create',
        dataSource: {
          link_group_name: '',
          bk_biz_id: '0',
          kafka_cluster_id: '',
          transfer_cluster_id: '',
          es_cluster_ids: [],
          is_active: true,
          description: '',
        },
      };
    },
    editConfig(item) {
      this.dialogSetting = {
        visible: true,
        type: 'edit',
        dataSource: item,
      };
    },
    handleOperation(type) {
      if (type === 'refresh') {
        this.emptyType = 'empty';
        this.init();
        return;
      }
    },
    // async deleteConfig (item) {
    //     try {
    //         this.tableLoading = true
    //         await this.$http.request('linkConfiguration/deleteLink', {
    //             params: {
    //                 data_link_id: item.data_link_id
    //             }
    //         })
    //         this.messageSuccess(this.$t('删除成功'))
    //         this.getLinkData()
    //     } catch (e) {
    //         console.warn(e)
    //         this.tableLoading = false
    //     }
    // }
  },
};
</script>

<style lang="scss" scoped>
  .link-configuration-container {
    padding: 20px 24px;

    .header {
      margin-bottom: 20px;
    }
  }
</style>
