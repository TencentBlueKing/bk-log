/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import * as authorityMap from '../common/authority-map';

export default {
  watch: {
    'formData.storage_cluster_id': {
      handler(newVal, oldVal) {
        this.storageList.forEach((res) => {
          if (res.storage_cluster_id === newVal) {
            this.selectedStorageCluster = res; // 当前选择的存储集群
            if (oldVal === '') {  // 当oldVal为空时则表示第一次进入
              this.replicasMax = res.setup_config?.number_of_replicas_max || 0;
              this.shardsMax = res.setup_config?.es_shards_max || 1;
              if (!this.editStorageClusterID) this.handleSelectStorageCluster(res);
            } else {
              this.handleSelectStorageCluster(res);
            }
            this.updateDaysList();
            this.$nextTick(() => { // 如果开启了冷热集群天数不能为0
              if (res.enable_hot_warm && this.formData.allocation_min_days === '0') {
                this.formData.allocation_min_days = String(res.setup_config.retention_days_default);
              }
            });
          }
        });
      },
    },
    // 冷热数据天数需小于过期时间
    'formData.allocation_min_days'(val) {
      const max = this.formData.retention;
      if (Number(val) > Number(max)) {
        this.$nextTick(() => {
          this.formData.allocation_min_days = max;
        });
      }
    },
  },
  methods: {
    /**
     * @desc: 获取存储集群
     * @param { String } environment ['storage','customize'] // 当前页
     */
    getStorage() {
      const queryData = { bk_biz_id: this.bkBizId };
      if (this.curCollect?.data_link_id) {
        queryData.data_link_id = this.curCollect.data_link_id;
      }
      this.$http.request('collect/getStorage', {
        query: queryData,
      }).then(async (res) => {
        if (res.data) {
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            if (item.permission?.[authorityMap.MANAGE_ES_SOURCE_AUTH]) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          this.storageList = s1.concat(s2);
          this.storageList.forEach(item => (item.is_platform
            ? this.clusterList.push(item)
            : this.exclusiveList.push(item)));
          const notPerformList = ['custom-report-create', 'custom-report-edit'];
          if (!notPerformList.includes(this.$route.name)) {
            this.getCleanStash();
          }
        }
      })
        .catch((res) => {
          this.$bkMessage({
            theme: 'error',
            message: res.message,
          });
        });
    },
    // 输入自定义过期天数、冷热集群存储期限
    enterCustomDay(val, type) {
      const numberVal = parseInt(val.trim(), 10);
      const stringVal = numberVal.toString();
      const isRetention = type === 'retention'; // 过期时间 or 热数据存储时间
      if (numberVal) {
        const maxDays = this.selectedStorageCluster.setup_config.retention_days_max || 30;
        if (numberVal > maxDays) { // 超过最大天数
          isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
          this.messageError(this.$t('最大自定义天数为') + maxDays);
        } else {
          if (isRetention) {
            if (!this.retentionDaysList.some(item => item.id === stringVal)) {
              this.retentionDaysList.push({
                id: stringVal,
                name: stringVal + this.$t('天'),
              });
            }
            this.formData.retention = stringVal;
            this.customRetentionDay = '';
          } else {
            if (!this.hotDataDaysList.some(item => item.id === stringVal)) {
              this.hotDataDaysList.push({
                id: stringVal,
                name: stringVal + this.$t('天'),
              });
            }
            this.formData.allocation_min_days = stringVal;
            this.customHotDataDay = '';
          }
          document.body.click();
        }
      } else {
        isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
        this.messageError(this.$t('请输入有效数值'));
      }
    },
    // 输入自定义副本数
    changeCopyNumber(val) {
      val === '' && (this.formData.storage_replies = this.selectedStorageCluster.setup_config.number_of_replicas_default);
    },
    // 输入自定义分片数
    changeShardsNumber(val) {
      val === '' && (this.formData.es_shards = this.selectedStorageCluster.setup_config.es_shards_default);
    },
    // 跳转到 es 源
    jumpToEsAccess() {
      window.open(this.$router.resolve({
        name: 'es-cluster-manage',
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      }).href, '_blank');
    },
    // 存储集群管理权限
    async applySearchAccess(item) {
      this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.MANAGE_ES_SOURCE_AUTH],
          resources: [{
            type: 'es_source',
            id: item.storage_cluster_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    // 选择存储集群
    handleSelectStorageCluster(res) {
      // 因为有最大天数限制，不同集群限制可能不同，所以切换集群时展示默认
      const { setup_config } = res;
      this.formData.retention = setup_config?.retention_days_default || '7';
      this.formData.storage_replies = setup_config?.number_of_replicas_default || 0;
      this.formData.es_shards = setup_config?.es_shards_default || 0;
      this.replicasMax = setup_config?.number_of_replicas_max || 0;
      this.shardsMax = setup_config?.es_shards_max || 1;
      this.formData.allocation_min_days = '0';
    },
    updateDaysList() {
      const retentionDaysList = [...this.globalsData.storage_duration_time].filter((item) => {
        return item.id <= (this.selectedStorageCluster.setup_config.retention_days_max || 30);
      });
      this.retentionDaysList = retentionDaysList;
      this.hotDataDaysList = [...retentionDaysList];
    },
  },
};
