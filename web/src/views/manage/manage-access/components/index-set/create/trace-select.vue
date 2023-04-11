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
  <bk-select
    style="width: 520px;"
    searchable
    :clearable="false"
    :value="selectedId"
    @selected="handleSelected"
    data-test-id="newlogIndexSetBox_select_selectIndex">
    <template v-for="item in collectionList">
      <bk-option
        :key="item.result_table_id"
        :id="item.result_table_id"
        :name="item.result_table_name_alias">
      </bk-option>
    </template>
  </bk-select>
</template>

<script>
import { mapState } from 'vuex';

export default {
  props: {
    value: {
      type: Array,
      required: true,
    },
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      selectedId: '',
      collectionList: [],
    };
  },
  computed: {
    ...mapState(['spaceUid', 'bkBizId']),
  },
  watch: {
    value: {
      handler(val) {
        const item = val[0];
        if (item && (item.result_table_id !== this.selectedId)) {
          this.selectedId = item.result_table_id;
        }
      },
      immediate: true,
    },
  },
  created() {
    this.fetchCollectionList();
  },
  methods: {
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
          item.bk_biz_id = this.bkBizId;
          return item;
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    handleSelected(id) {
      this.selectedId = id;
      this.$emit('update:value', [this.collectionList.find(item => item.result_table_id === id)]);
    },
  },
};
</script>
