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
  data() {
    return {
      disabledTips: {
        terminated: {
          operateType: ['clone', 'storage', 'search', 'clean'],
          tips: this.$t('未完成配置'),
        },
        delete: this.$t('删除前请先停用'),
      },
    };
  },
  methods: {
    async operateHandler(row, operateType) { // type: [view, status , search, edit, field, start, stop, delete]
      if (operateType === 'add') { // 新建权限控制
        if (!this.isAllowedCreate) {
          return this.getOptionApplyData({
            action_ids: [authorityMap.CREATE_COLLECTION_AUTH],
            resources: [{
              type: 'space',
              id: this.spaceUid,
            }],
          });
        }
      } else if (operateType === 'view') { // 查看权限
        if (!(row.permission?.[authorityMap.VIEW_COLLECTION_AUTH])) {
          return this.getOptionApplyData({
            action_ids: [authorityMap.VIEW_COLLECTION_AUTH],
            resources: [{
              type: 'collection',
              id: row.collector_config_id,
            }],
          });
        }
      } else if (operateType === 'search') { // 检索权限
        if (!(row.permission?.[authorityMap.SEARCH_LOG_AUTH])) {
          return this.getOptionApplyData({
            action_ids: [authorityMap.SEARCH_LOG_AUTH],
            resources: [{
              type: 'indices',
              id: row.index_set_id,
            }],
          });
        }
      } else if (!(row.permission?.[authorityMap.MANAGE_COLLECTION_AUTH])) { // 管理权限
        return this.getOptionApplyData({
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: row.collector_config_id,
          }],
        });
      }
      this.leaveCurrentPage(row, operateType);
    },
    // 删除
    requestDeleteCollect(row) {
      this.$http.request('collect/deleteCollect', {
        params: {
          collector_config_id: row.collector_config_id,
        },
      }).then((res) => {
        if (res.result) {
          const page = this.collectList.length <= 1
            ? (this.pagination.current > 1 ? this.pagination.current - 1 : 1)
            : this.pagination.current;
          if (page !== this.pagination.current) {
            this.handlePageChange(page);
          } else {
            this.requestData();
          }
        }
      })
        .catch(() => { });
    },
    /**
     * 分页变换
     * @param  {Number} page 当前页码
     * @return {[type]}      [description]
     */
    handlePageChange(page) {
      if (this.pagination.current !== page) {
        this.pagination.current = page;
        if (this.$route.name === 'collection-item') {
          this.stopStatusPolling();
        }
        this.requestData();
      }
    },
    /**
    * 分页限制
    * @param  {Number} page 当前页码
    * @return {[type]}      [description]
    */
    handleLimitChange(page) {
      // console.log('changelimit');
      if (this.pagination.limit !== page) {
        this.pagination.current = 1;
        this.pagination.limit = page;
        this.requestData();
      }
    },
    async getOptionApplyData(paramData) {
      try {
        this.isTableLoading = true;
        const res = await this.$store.dispatch('getApplyData', paramData);
        this.$store.commit('updateAuthDialogData', res.data);
      } catch (err) {
        console.warn(err);
      } finally {
        this.isTableLoading = false;
      }
    },
    async checkCreateAuth() {
      try {
        const res = await this.$store.dispatch('checkAllowed', {
          action_ids: [authorityMap.CREATE_COLLECTION_AUTH],
          resources: [{
            type: 'space',
            id: this.spaceUid,
          }],
        });
        this.isAllowedCreate = res.isAllowed;
      } catch (err) {
        console.warn(err);
        this.isAllowedCreate = false;
      }
    },
    getDisabledTipsMessage(item, operateType) {
      if (operateType === 'delete') return this.disabledTips.delete;
      if (!this.disabledTips[item.status]) return '--';
      if (this.disabledTips[item.status].operateType?.includes(operateType)) {
        return this.disabledTips[item.status].tips;
      };
      return '--';
    },
  },
};
