<template>
  <div class="link-configuration-container">
    <div class="header">
      <bk-button theme="primary" style="width: 120px;" @click="createConfig">{{ $t('新建') }}</bk-button>
    </div>
    <bk-table
      :data="tableData"
      :empty-text="$t('btn.vacancy')"
      v-bkloading="{ isLoading: tableLoading }">
      <bk-table-column :label="$t('链路名称')" prop="link_group_name" min-width="20"></bk-table-column>
      <bk-table-column :label="$t('允许的业务')" prop="bk_biz_id" min-width="20">
        <template slot-scope="{ row }">
          <div>{{ filterProjectName(row) || '--'}}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('链路信息')" min-width="60">
        <template slot-scope="{ row }">
          <div>{{ filterLinkInformation(row) || '' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('备注')" min-width="20">
        <div style="padding: 10px 0;" slot-scope="{ row }">
          {{ row.description || '--' }}
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('是否启用')" min-width="10">
        <template slot-scope="{ row }">
          <div>{{ row.is_active ? $t('是') : $t('否') }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" min-width="10">
        <template slot-scope="props">
          <bk-button theme="primary" text @click="editConfig(props.row)">{{ $t('编辑') }}</bk-button>
          <!--<bk-button theme="primary" text @click="deleteConfig(props.row)">{{ $t('删除') }}</bk-button>-->
        </template>
      </bk-table-column>
    </bk-table>
    <ConfigDialog
      :visible.sync="dialogSetting.visible"
      :type="dialogSetting.type"
      :project-list="projectList"
      :data-source="dialogSetting.dataSource"
      :select-data="selectData"
      @showUpdateList="getLinkData" />
  </div>
</template>

<script>
import ConfigDialog from './ConfigDialog';

export default {
  name: 'LinkConfiguration',
  components: {
    ConfigDialog,
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
    };
  },
  computed: {
    projectList() {
      return [
        { bk_biz_id: '0', project_name: this.$t('全部业务') },
        ...this.$store.state.myProjectList,
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
      return this.projectList.find(item => item.bk_biz_id === row.bk_biz_id)?.project_name;
    },
    filterLinkInformation(row) {
      const kafkaName = this.selectData.kafka.find(item => item.cluster_id === row.kafka_cluster_id)?.cluster_name;
      if (!kafkaName) {
        return '';
      }

      const transferName = this.selectData.transfer.find((item) => {
        return item.cluster_id === row.transfer_cluster_id;
      })?.cluster_name;
      if (!transferName) {
        return '';
      }

      const esNameList = row.es_cluster_ids.map((id) => {
        return this.selectData.es.find(item => item.cluster_id === id)?.cluster_name;
      });
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
    padding: 20px 60px;

    .header {
      margin-bottom: 20px;
    }
  }
</style>
