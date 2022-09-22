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
    style="background: #fff;"
    ext-popover-cls="retrieve-index-select-popover"
    data-test-id="dataQuery_div_indexSetSelect"
    :searchable="true"
    :clearable="false"
    :value="indexId"
    :popover-min-width="600"
    :popover-options="{ boundary: 'window' }"
    @selected="handleSelectIndex">
    <div
      slot="trigger"
      class="bk-select-name"
      v-bk-overflow-tips="{ placement: 'right' }">
      <span>{{ selectedItem.indexName }}</span>
      <span style="color: #979ba5;">{{ selectedItem.lightenName }}</span>
    </div>
    <!-- <bk-option v-for="item in indexSetList"
            class="custom-no-padding-option"
            :key="item.index_set_id"
            :id="item.index_set_id"
            :name="item.indexName + item.lightenName">
            <div
            v-if="!(item.permission && item.permission.search_log)"
             class="option-slot-container no-authority" @click.stop>
                <span class="text">{{ item.indexName + item.lightenName }}</span>
                <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
            </div>
            <div v-else v-bk-overflow-tips class="option-slot-container">
                <span class="bk-icon icon-star"></span>
                <span>{{ item.indexName }}</span>
                <span style="color: #979BA5;">{{ item.lightenName }}</span>
            </div>
        </bk-option> -->

    <bk-option-group
      v-for="(group, index) in renderOptionList"
      :id="group.id"
      :name="group.name"
      :key="index"
      :show-count="false">
      <bk-option
        v-for="item in group.children"
        class="custom-no-padding-option"
        :key="item.index_set_id"
        :id="item.index_set_id"
        :name="item.indexName + item.lightenName"
        :data-test-id="`ul_li_${item.indexName}`">
        <div
          v-if="!(item.permission && item.permission[authorityMap.SEARCH_LOG_AUTH])"
          class="option-slot-container no-authority" @click.stop>
          <span class="text">{{ item.indexName + item.lightenName }}</span>
          <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
        </div>
        <div v-else v-bk-overflow-tips class="option-slot-container authority">
          <div class="index-info">
            <span
              :class="[item.is_favorite ? 'log-icon icon-star-shape' : 'bk-icon icon-star']"
              style="color: #fe9c00;"
              @click.stop="handleCollection(item)">
            </span>
            <span>{{ item.indexName }}</span>
            <span style="color: #979ba5;" :title="item.lightenName">{{ item.lightenName }}</span>
          </div>
          <div class="index-tags">
            <span
              v-for="(tag, tIndex) in item.tags"
              :key="tag.tag_id">
              <span
                :class="['tag-card', `tag-card-${tag.color}`]"
                v-if="tIndex < 2"
                v-bk-tooltips.top="{
                  content: `${$t('上次检测时间')}: ${item.no_data_check_time}`,
                  disabled: tag.tag_id !== 4,
                  delay: [300, 0]
                }">{{ tag.name }}</span>
            </span>
          </div>
        </div>
      </bk-option>
    </bk-option-group>
  </bk-select>
</template>

<script>
import * as authorityMap from '../../../common/authority-map';

export default {
  props: {
    indexId: {
      type: String,
      required: true,
    },
    indexSetList: {
      type: Array,
      required: true,
    },
    basicLoading: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      isCollectionLoading: false,
    };
  },
  computed: {
    authorityMap() {
      return authorityMap;
    },
    selectedItem() {
      return this.indexSetList.find(item => item.index_set_id === this.indexId) || {};
    },
    renderOptionList() {
      let list = [
        { name: this.$t('收藏'), children: [] },
        { name: '', children: [] },
      ];
      this.indexSetList.forEach((item) => {
        if (item.is_favorite) list[0].children.push(item);
        else list[1].children.push(item);
      });

      if (!list[0].children.length) {
        list = list.slice(1);
      }

      return list;
    },
  },
  methods: {
    handleSelectIndex(val) {
      this.$emit('selected', val);
    },
    // 申请索引集的搜索权限
    async applySearchAccess(item) {
      this.$el.click(); // 手动关闭下拉
      try {
        this.$emit('update:basicLoading', true);
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: [authorityMap.SEARCH_LOG_AUTH],
          resources: [{
            type: 'indices',
            id: item.index_set_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.$emit('update:basicLoading', false);
      }
    },
    async handleCollection(item) {
      if (this.isCollectionLoading) return;

      try {
        this.isCollectionLoading = true;
        const url = `/indexSet/${item.is_favorite ? 'cancelMark' : 'mark'}`;

        await this.$http.request(url, {
          params: {
            index_set_id: item.index_set_id,
          },
        }).then(() => {
          this.$emit('updateIndexSetList');
        });
      } finally {
        this.isCollectionLoading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
  .authority {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-height: 32px;

    .tag-card {
      display: inline-block;
      font-size: 12px;
      padding: 0 10px;
      height: 22px;
      line-height: 22px;
      margin-left: 6px;
      cursor: default;
      border-width: 1px;
      border-style: solid;
      padding: 0 9px;
      line-height: 20px;

      &-gray {
        border-color: #dcdee5;
        color: #63656e;
        background-color: rgba(151,155,165,.1);
      }

      &-blue {
        border-color: #3a84ff;
        color: #3a84ff;
        background-color: rgba(58,132,255,.1);
      }

      &-yellow {
        background-color: rgba(254,156,0,.1);
        border-color: #fe9c00;
        color: #fe9c00;
      }

      &-green {
        background-color: #14a5681a;
        border-color: #14a568;
        color: #14a568;
      }

      &-red {
        background-color: rgba(234,53,54,.1);
        border-color: #ea3536;
        color: #ea3536;
      }
    }

    .index-info {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
</style>

<style lang="scss">
  .retrieve-index-select-popover {
    .bk-options {
      .bk-option-group {
        &:last-child {
          .bk-option-group-name {
            height: 0;
            border-top: 1px solid #f0f1f5;
          }
        }

        &:first-child {
          .bk-option-group-name {
            border-top: 0;
          }
        }

        .bk-option-group-name {
          margin: 0 10px;
          border: none;
        }
      }

      .bk-group-options .bk-option {
        padding: 0;

        .bk-option-content {
          .option-slot-container {
            padding: 9px 10px;
          }
        }
      }

    }
  }
</style>
