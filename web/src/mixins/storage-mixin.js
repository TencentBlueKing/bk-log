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


export default {
  watch: {
    'formData.storage_cluster_id': {
      immediate: true,
      handler(val) {
        this.storageList.forEach((res) => {
          const arr = [];
          if (res.storage_cluster_id === val) {
            this.selectedStorageCluster = res; // 当前选择的存储集群
            this.updateDaysList();
            this.$nextTick(() => { // 如果开启了冷热集群天数不能为0
              if (res.enable_hot_warm && this.formData.allocation_min_days === '0') {
                this.formData.allocation_min_days = '7';
              }
            });

            this.storage_capacity = JSON.parse(JSON.stringify(res.storage_capacity));
            this.tips_storage = [
              `${this.$t('dataSource.tips_capacity')} ${this.storage_capacity} G，${this.$t('dataSource.tips_development')}`,
              this.$t('dataSource.tips_business'),
              this.$t('dataSource.tips_formula'),
            ];
            if (res.storage_capacity === 0) {
              arr.push(this.tips_storage[2]);
            } else {
              if (res.storage_used > res.storage_capacity) {
                arr.push(this.tips_storage[1]);
                arr.push(this.tips_storage[2]);
              } else {
                arr.push(this.tips_storage[0]);
                arr.push(this.tips_storage[2]);
              }
            }
            this.tip_storage = arr;
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
    // 获取存储集群
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
            if (item.permission?.manage_es_source) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          this.storageList = s1.concat(s2);
          if (this.isItsm && this.curCollect?.can_use_independent_es_cluster) {
            // itsm 开启时，且可以使用独立集群的时候，默认集群 _default 被禁用选择
          } else {
            const defaultItem = this.storageList.find(item => item.registered_system === '_default');
            if (defaultItem?.permission?.manage_es_source) {
              this.formData.storage_cluster_id = defaultItem.storage_cluster_id;
            }
          }
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
    // 存储集群管理权限
    async applySearchAccess(item) {
      this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['manage_es_source'],
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
    // 输入自定义过期天数、冷热集群存储期限
    enterCustomDay(val, type) {
      const numberVal = parseInt(val.trim(), 10);
      const stringVal = numberVal.toString();
      const isRetention = type === 'retention'; // 过期时间 or 热数据存储时间
      if (numberVal) {
        const maxDays = this.selectedStorageCluster.max_retention || 30;
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
      val === '' && (this.formData.storage_replies = 1);
    },
    // 跳转到 es 源
    jumpToEsAccess() {
      window.open(this.$router.resolve({
        name: 'es-cluster-manage',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      }).href, '_blank');
    },
    // 存储集群管理权限
    async applySearchAccess(item) {
      this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['manage_es_source'],
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
    handleSelectStorageCluster() {
      // 因为有最大天数限制，不同集群限制可能不同，所以切换集群时重置
      this.formData.retention = '7';
      this.formData.allocation_min_days = '0';
    },
    updateDaysList() {
      const retentionDaysList = [...this.globalsData.storage_duration_time].filter((item) => {
        return item.id <= (this.selectedStorageCluster.max_retention || 30);
      });
      this.retentionDaysList = retentionDaysList;
      this.hotDataDaysList = [...retentionDaysList];
    },
  },
};
