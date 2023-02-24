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
  <div class="preview-file-content">
    <div class="flex-box">
      <bk-select
        v-model="previewIp"
        style="width: 190px; margin-right: 20px;background-color: #fff;"
        data-test-id="addNewExtraction_div_selectPreviewAddress"
        :clearable="false"
        multiple
        show-select-all>
        <bk-option
          v-for="option in ipList"
          :key="option.bk_cloud_id + ':' + option.ip"
          :id="option.bk_cloud_id + ':' + option.ip"
          :name="option.bk_cloud_id + ':' + option.ip"
        ></bk-option>
      </bk-select>
      <span>{{ $t('文件日期') }}：</span>
      <file-date-picker :time-range.sync="timeRange" :time-value.sync="timeValue" />
      <bk-checkbox
        v-model="isSearchChild"
        style="margin-right: 20px;"
        data-test-id="addNewExtraction_div_isSearchSubdirectory"
      >{{ $t('是否搜索子目录') }}</bk-checkbox>
      <bk-button
        theme="primary"
        :disabled="!ipList.length || !fileOrPath"
        :loading="isLoading"
        data-test-id="addNewExtraction_button_searchFilterCondition"
        @click="getExplorerList({})">{{ $t('搜索') }}
      </bk-button>
    </div>
    <span class="table-head-text">{{ $t('从下载目标中选择预览目标') }}</span>
    <div class="flex-box" v-bkloading="{ isLoading, opacity: .7, zIndex: 0 }">
      <bk-table
        ref="previewTable"
        class="preview-scroll-table"
        style="background-color: #fff;"
        :data="explorerList"
        :height="360"
        @selection-change="handleSelect">
        <bk-table-column type="selection" width="60" :selectable="row => row.size !== '0'"></bk-table-column>
        <bk-table-column prop="path" :label="$t('文件名')" min-width="80" sortable :sort-by="['path', 'mtime', 'size']">
          <div class="table-ceil-container" slot-scope="{ row }">
            <span
              v-if="row.size === '0'"
              v-bk-overflow-tips
              class="download-url-text"
              @click="getExplorerList(row)">
              {{ row.path }}
            </span>
            <span v-else v-bk-overflow-tips>{{ row.path }}</span>
          </div>
        </bk-table-column>
        <bk-table-column
          prop="mtime"
          :label="$t('最后修改时间')"
          min-width="50"
          sortable
          :sort-by="['mtime', 'path', 'size']">
        </bk-table-column>
        <bk-table-column
          prop="size"
          :label="'尺寸'"
          min-width="40"
          sortable
          :sort-by="['size', 'mtime', 'path']">
        </bk-table-column>
        <div slot="empty">
          <empty-status empty-type="empty" />
        </div>
      </bk-table>
    </div>
  </div>
</template>

<script>
import { formatDate } from '@/common/util';
import FileDatePicker from '@/views/extract/home/file-date-picker';
import EmptyStatus from '@/components/empty-status';

export default {
  components: {
    FileDatePicker,
    EmptyStatus,
  },
  model: {
    prop: 'downloadFiles',
    event: 'checked',
  },
  props: {
    ipList: {
      type: Array,
      required: true,
    },
    fileOrPath: {
      type: String,
      required: true,
    },
  },
  data() {
    // 默认范围一周
    const currentTime = Date.now();
    const startTime = new Date(currentTime - 1000 * 60 * 60 * 24 * 7);
    const endTime = new Date(currentTime);

    return {
      isLoading: false,
      previewIp: [],
      timeRange: '1w', // 时间跨度 ["1d", "1w", "1m", "all", "custom"]
      timeValue: [startTime, endTime],
      isSearchChild: false,
      explorerList: [],
      historyStack: [], // 预览地址历史
    };
  },
  computed: {
    timeStringValue() {
      return [formatDate(this.timeValue[0]), formatDate(this.timeValue[1])];
    },
  },
  watch: {
    ipList(val) {
      this.previewIp.splice(0);
      if (val.length) {
        this.previewIp.push(`${val[0].bk_cloud_id}:${val[0].ip}`);
      }
      this.explorerList.splice(0); // 选择服务器后清空表格
      this.historyStack.splice(0); // 选择服务器后清空历史堆栈
    },
  },
  methods: {
    getExplorerList(row) {
      const { path = this.fileOrPath, size } = row;
      const cacheList = {
        exploreList: this.explorerList.splice(0),
        fileOrPath: path,
      };
      this.$emit('checked', []);
      if (path === '../' && this.historyStack.length) { // 返回上一级
        const cache = this.historyStack.pop();
        this.explorerList = cache.exploreList;
        const { fileOrPath } = this.historyStack[this.historyStack.length - 1];
        this.$emit('update:fileOrPath', fileOrPath);
        return;
      }
      this.$emit('update:fileOrPath', path);
      const ipList = [];
      for (let i = 0; i < this.previewIp.length; i++) {
        const cloudId = this.previewIp[i].split(':')[0];
        const ip = this.previewIp[i].split(':')[1];
        const target = this.ipList.find(item => item.ip === ip && item.bk_cloud_id === Number(cloudId));
        ipList.push(target);
      }

      this.isLoading = true;
      this.$http.request('extract/getExplorerList', {
        data: {
          bk_biz_id: this.$store.state.bkBizId,
          ip_list: ipList,
          path: path || this.fileOrPath,
          time_range: this.timeRange,
          start_time: this.timeStringValue[0],
          end_time: this.timeStringValue[1],
          is_search_child: this.isSearchChild,
        },
      }).then((res) => {
        if (path) { // 指定目录搜索
          this.historyStack.push(cacheList);
          const temp = {
            ...row,
            path: '../',
          };

          if (size === '0') this.explorerList = [temp, ...res.data];
          else this.explorerList = [...res.data];
        } else { // 搜索按钮
          this.historyStack = [];
          this.explorerList = res.data;
        }
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    // 父组件克隆时调用
    handleClone({
      preview_ip: ip,
      preview_directory: path,
      preview_time_range: timeRange,
      preview_start_time: startTime,
      preview_end_time: endTime,
      preview_is_search_child: isSearchChild,
      file_path: downloadFiles,
    }) {
      this.previewIp = ip.split(',');
      this.timeRange = timeRange;
      this.timeValue = [new Date(startTime), new Date(endTime)];
      this.isSearchChild = isSearchChild;

      const ipList = [];
      for (let i = 0; i < this.previewIp.length; i++) {
        const cloudId = this.previewIp[i].split(':')[0];
        const ip = this.previewIp[i].split(':')[1];
        const target = this.ipList.find(item => item.ip === ip && item.bk_cloud_id === Number(cloudId));
        ipList.push(target);
      }

      this.isLoading = true;
      this.$http.request('extract/getExplorerList', {
        data: {
          bk_biz_id: this.$store.state.bkBizId,
          ip_list: ipList,
          path,
          time_range: timeRange,
          start_time: startTime,
          end_time: endTime,
          is_search_child: isSearchChild,
        },
      }).then((res) => {
        this.historyStack = [];
        this.explorerList = res.data;
        this.$nextTick(() => {
          downloadFiles.forEach((path) => {
            for (const item of this.explorerList) {
              if (item.path === path) {
                this.$refs.previewTable.toggleRowSelection(item, true);
                break;
              }
            }
          });
        });
      })
        .catch((e) => {
          console.warn(e);
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    handleSelect(selection) {
      this.$emit('checked', selection.map(item => item.path));
    },
  },
};
</script>

<style lang="scss">
  .preview-file-content {
    display: flex;
    flex-flow: column;
    justify-content: center;
    width: calc(100% - 140px);
    max-width: 1000px;
    min-height: 40px;

    .flex-box {
      display: flex;
      align-items: center;

      .download-url-text {
        color: #3a84ff;
        cursor: pointer;

        &:hover {
          color: #699df4;
        }

        &:active {
          color: #2761dd;
        }

        &.is-disabled {
          color: #c4c6cc;
          cursor: not-allowed;
        }
      }
    }

    .table-head-text {
      margin: 18px 0 8px;
      font-size: 12px;
    }
  }

  .preview-scroll-table {
    .bk-table-body-wrapper {
      overflow-y: auto;
    }

    .cell {
      /* stylelint-disable-next-line declaration-no-important */
      display: flex !important;
    }
  }
</style>
