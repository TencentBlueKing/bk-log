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
  <div class="container-status-container">
    <div class="nav-section">
      <div class="nav-btn-box">
        <div
          v-for="item in navBtnList"
          :key="item.id"
          :class="`nav-btn ${item.id === navActive ? 'active' : ''}`"
          @click="handleClickNav(item.id)">
          <span
            v-if="item.id !== 'all'"
            :class="[
              item.id !== 'running' && 'circle nav-icon',
              isHaveRunning(item) && 'rotate-icon',
              colorClass[item.id],
            ]"
            v-bkloading="{
              isLoading: isHaveRunning(item),
              opacity: 1,
              zIndex: 10,
              theme: 'primary',
              mode: 'spin',
              size: 'small'
            }"></span>
          <span v-if="isHaveRunning(item)" class="running-circle"></span>
          <span>{{statusNameList[item.id]}} {{item.listNum}}</span>
        </div>
      </div>
      <bk-button @click.stop="issuedRetry()">
        {{$t('失败批量重试')}}
      </bk-button>
    </div>
    <div class="table-section">
      <div v-for="(renderItem, renderIndex) in renderTitleList" :key="renderIndex" class="table-item">
        <div :class="`table-title ${renderItem.isShowTable ? '' : 'close-table'}`"
             @click="handleClickTitle(renderIndex, renderItem.isShowTable)">
          <span class="bk-icon icon-down-shape"></span>
          <span>{{renderItem.collector_config_name}}</span>
        </div>
        <div :class="['table-main', renderItem.isShowTable ? 'show' : 'hidden']">
          <bk-table :data="renderItem[navActive]" size="small">
            <bk-table-column label="id" width="80" prop="container_collector_config_id"></bk-table-column>
            <bk-table-column :label="$t('名称')" prop="name"></bk-table-column>
            <bk-table-column :label="$t('状态')">
              <template slot-scope="{ row }">
                <div :class="row.status === 'running' ? 'rotate-div' : ''">
                  <span
                    :class="['circle',
                             row.status === 'running' ? 'rotate-icon' : 'nav-icon',
                             colorClass[row.status]]"
                    v-bkloading="{
                      isLoading: row.status === 'running',
                      opacity: 1,
                      zIndex: 10,
                      theme: 'primary',
                      mode: 'spin',
                      size: 'small'
                    }"></span>
                  <span>{{statusNameList[row.status]}}</span>
                </div>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('详情')" prop="message"></bk-table-column>
            <bk-table-column width="80">
              <template slot-scope="{ row }">
                <a
                  href="javascript: ;" class="retry"
                  v-if="row.status === 'failed'"
                  @click.stop="issuedRetry('alone', renderItem, row)">
                  {{ $t('重试') }}
                </a>
              </template>
            </bk-table-column>
          </bk-table>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapGetters } from 'vuex';

export default {
  props: {
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      navActive: 'all', // 当前活跃按钮
      navBtnList: [ // 按钮列表
        {
          id: 'all',
          listNum: 0,
        },
        {
          id: 'success',
          listNum: 0,
        },
        {
          id: 'failed',
          listNum: 0,
        },
        {
          id: 'running',
          listNum: 0,
        },
      ],
      colorClass: { // 成功失败类名
        success: 'circle-green',
        failed: 'circle-red',
      },
      statusNameList: { // 状态中文名
        all: this.$t('全部'),
        success: this.$t('正常'),
        failed: this.$t('失败'),
        running: this.$t('执行中'),
      },
      timer: null,
      renderTitleList: [], // 当前活跃的目标
      curTaskIdStr: '',
      allFailedIDList: [], // 所有状态为失败的config_id
    };
  },
  computed: {
    ...mapGetters('collect', ['curCollect']),
    hasRunning() { // 是否还有执行中的状态
      return this.navBtnList[3].listNum;
    },
  },
  created() {
    this.curTaskIdStr = [...new Set([...this.curCollect.task_id_list])].join(',');
  },
  mounted() {
    this.getContainerList();
    this.pollingStatus();
  },
  beforeDestroy() {
    clearInterval(this.timer);
  },
  methods: {
    handleClickTitle(index, isClose) {
      this.renderTitleList[index].isShowTable = !isClose;
    },
    handleClickNav(activeID) {
      this.navActive = activeID;
    },
    /**
     * @desc: 轮询状态
     */
    pollingStatus() {
      clearInterval(this.timer);
      this.timer = setInterval(() => {
        this.getContainerList('polling');
      }, 5000);
    },
    /**
     * @desc: 容器日志list，与轮询共用
     * @param { String } isPolling 是否是轮询状态
     */
    getContainerList(isPolling = '') {
      if (isPolling !== 'polling') this.$emit('update:is-loading', true);
      const params = { collector_config_id: this.curCollect.collector_config_id };
      this.$http.request('collect/getIssuedClusterList', {
        params,
        query: { task_id_list: this.curTaskIdStr },
      }).then((res) => {
        const data = JSON.parse(JSON.stringify(res.data.contents)) || [];
        this.allFailedIDList = [];
        this.navBtnList.forEach(item => item.listNum = 0);
        this.renderTitleList = data.reduce((pre, cur) => {
          cur.isShowTable = true;
          this.navBtnList.forEach(item => cur[item.id] = []);
          if (cur.child.length) {
            cur.all = cur.child;
            for (const childItem of cur.child) {
              childItem.status = childItem.status === 'PENDING' ? 'running' : childItem.status.toLowerCase();
              childItem.status === 'failed' && this.allFailedIDList.push(childItem.container_collector_config_id);
              cur[childItem.status].push(childItem);
            }
            delete cur.child;
          }
          this.navBtnList.forEach(item => item.listNum += cur[item.id].length);
          pre.push(cur);
          return pre;
        }, []);
      })
        .catch((err) => {
          console.warn(err);
        })
        .finally(() => {
          this.$emit('update:is-loading', false);
          if (isPolling === 'polling' && !this.hasRunning) clearInterval(this.timer);
        });
    },
    issuedRetry(alone = '', renderItem, row) {
      const retrySubmitList = alone ? [row.container_collector_config_id] : this.allFailedIDList;
      // ID列表为空或者全局失败数为0时不请求
      if (!retrySubmitList.length || !this.navBtnList[2].listNum) return;
      if (row) {
        row.status = 'running';// 单选 单独变成running状态
        // 失败-1 执行中+1
        renderItem.running.push(row);
        const renderIndex =  renderItem.failed.findIndex(item => item.name === row.name);
        renderItem.failed.splice(renderIndex, 1);
        this.navBtnList[3].listNum += 1;
        this.navBtnList[2].listNum -= 1;
      } else {
        // 批量重试 清空失败 将所有的失败添加到执行中
        this.renderTitleList.forEach((tableItem) => {
          tableItem.all.forEach(item => item.status === 'failed' && (item.status = 'running'));
          tableItem.failed.forEach(item => item.status = 'running');
          tableItem.running.push(...tableItem.failed);
          tableItem.failed = [];
        });
        this.navBtnList[3].listNum = this.navBtnList[3].listNum + this.navBtnList[2].listNum;
        this.navBtnList[2].listNum = 0;
      }
      this.$http.request('source/retryList', {
        params: {
          collector_config_id: this.$route.params.collectorId,
        },
        data: {
          instance_id_list: retrySubmitList,
        },
      }).then(() => {
        this.pollingStatus();
      })
        .catch((e) => {
          console.warn(e);
        });
    },
    /**
     * @desc: 是否有重试执行中的采集状态
     * @param {Object} item
     */
    isHaveRunning(item) {
      return item.id === 'running' && item.listNum !== 0;
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/mixins/flex.scss';

.container-status-container {
  .nav-section {
    @include flex-justify(space-between);

    .nav-btn-box {
      min-width: 327px;
      height: 36px;
      padding: 5px 4px;
      background: #f0f1f5;
      border-radius: 4px;
      align-items: center;
      font-size: 14px;

      @include flex-justify(space-between);

      .nav-btn {
        position: relative;
        padding: 4px 15px;
        border-radius: 4px;
        color: #63656e;

        &:not(:last-child)::after {
          content: '|';
          position: absolute;
          color: #dcdee5;
          top: 3px;
          right: -8px;
        }

        &:not(:first-child) {
          margin-left: 12px;
        }

        &:hover {
          background: #fff;
          cursor: pointer;
        }

        &.active {
          color: #3a84ff;
          background: #fff;
        }
      }
    }
  }

  .nav-icon {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;

    &.circle {
      &::after {
        content: ' ';
        width: 16px;
        height: 16px;
        display: inline-block;
        position: absolute;
        border-radius: 50%;
        top: -3px;
        left: -3px;
      }
    }

    &.circle-green {
      background: #3fc06d;

      &::after {
        background: rgba(63, 192, 109, .16);
      }
    }

    &.circle-red {
      background: #ea3636;

      &::after {
        background: rgba(234, 54, 54, .16);
      }
    }
  }

  .rotate-div {
    transform: translateX(12px);
  }

  .rotate-icon {
    position: absolute;
    top: -4px;
    left: 8px;
    display: inline-block;
    transform: scale(.6);
  }

  .running-circle {
    display: inline-block;
    width: 10px;
    height: 10px;
  }

  .table-section {
    .table-item {
      margin-top: 20px;

      .table-title {
        padding: 10px 23px;
        font-size: 12px;
        background: #f0f1f5;
        border: 1px solid #dcdee5;
        border-bottom: none;
        cursor: pointer;

        > span {
          &:first-child {
            font-size: 14px;
          }

          &:nth-child(2) {
            color: #63656e;
            font-weight: 700;
          }
        }

        .icon-down-shape {
          display: inline-block;
          transform: translateY(-1px);
        }

        &.close-table {
          border-bottom: 1px solid #dcdee5;

          .icon-down-shape {
            transform: rotateZ(-90deg) translateX(1px);
          }
        }
      }

      .retry {
        color: #3a84ff;
      }
    }

    .hidden {
      height: 0px;
    }

    .show {
      height: auto;
    }
  }
}
</style>
