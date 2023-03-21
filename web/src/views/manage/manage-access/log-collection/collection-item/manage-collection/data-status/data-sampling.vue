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
  <section id="json-format">
    <bk-table
      v-bkloading="{ isLoading: loading }"
      :data="data"
      :empty-text="$t('暂无内容')"
      :size="size">
      <bk-table-column
        type="index"
        :label="$t('序号')"
        align="center"
        width="120"
        style="margin-top: 13px">
      </bk-table-column>
      <bk-table-column :label="$t('原始日志')">
        <template slot-scope="props">
          <div
            :class="{ 'text-style': true, 'expand-style': expandIndex === props.$index }"
            @click="showClick($event, props.$index)"
            @mouseenter="handleEnter($event, props.row.etl.batch)"
            @mouseleave="handleLeave">
            <span v-for="(val,index) in props.row.etl.batch" :key="index">{{ val }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('采集时间')" width="200">
        <template slot-scope="props">
          <div>{{ props.row.etl.datetime }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" width="200">
        <template slot-scope="props">
          <div>
            <span class="option-text" @click="copyText(props.row.etl.batch, 'log')">{{ $t('复制') }}</span>
            <span class="option-text" @click="chickFile(props.row)">{{ $t('查看上报日志') }}</span>
          </div>
        </template>
      </bk-table-column>
      <div slot="empty">
        <empty-status empty-type="empty" :show-text="false">
          <span>{{$t('暂无内容')}}</span>
        </empty-status>
      </div>
    </bk-table>
    <bk-sideslider
      transfer
      class="locker-style"
      :is-show.sync="defaultSettings.isShow"
      :quick-close="true"
      :modal="false"
      :width="596">
      <div slot="header">{{ customSettings.title }}
        <span @click="copyText(JSON.stringify(jsonText))">{{ $t('复制') }}</span></div>
      <div class="p20 json-text-style" slot="content">
        <VueJsonPretty :deep="5" :data="jsonText" />
      </div>
    </bk-sideslider>
  </section>
</template>

<script>
import EmptyStatus from '@/components/empty-status';
export default {
  components: {
    EmptyStatus,
  },
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
    data: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      instance: null,
      customSettings: {
        isShow: false,
        title: this.$t('上报日志详情'),
      },
      jsonText: '',
      defaultSettings: {
        isShow: false,
      },
      size: 'small',
      expandIndex: -1,
    };
  },
  methods: {
    showClick(e, rowIndex) {
      if (this.expandIndex === rowIndex) {
        this.expandIndex = -1;
        return;
      }
      this.expandIndex = rowIndex;
    },
    divClose() {
      const divHeight = document.getElementsByClassName('text-style');
      for (let i = 0; i < divHeight.length; i++) {
        if (divHeight[i].offsetHeight > 54) {
          divHeight[i].style.height = '54px';
        }
      }
    },
    handleEnter(e) {
      this.instance = this.$bkPopover(e.target, {
        content: this.$t('点击展示全部'),
        arrow: true,
        placement: 'top',
      });
      this.instance.show(1000);
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    chickFile(data) {
      this.defaultSettings.isShow = true;
      this.jsonText = data.origin;
    },
    copyText(data, val) {
      let sta = '';
      if (val === 'log') {
        data.forEach((item) => {
          sta = `${sta + item}\n`;
        });
      }
      const createInput = document.createElement('textarea');
      createInput.value = val === 'log' ? sta : data;
      document.body.appendChild(createInput);
      createInput.select(); // 选择对象
      document.execCommand('Copy'); // 执行浏览器复制命令
      createInput.style.display = 'none';
      const h = this.$createElement;
      this.$bkMessage({
        message: h('p', {
          style: {
            textAlign: 'center',
          },
        }, this.$t('复制成功')),
        offsetY: 80,
      });
    },
  },
};
</script>

<style scoped lang="scss">
  @import '../../../../../../../scss/mixins/clearfix';
  @import '../../../../../../../scss/conf';

  #json-format {
    .option-text {
      margin-right: 6px;
      color: #3a84ff;
      cursor: pointer;
    }
  }

  .nav-head {
    height: 20px;
    line-height: 20px;
    font-size: 14px;
    position: relative;

    i {
      cursor: pointer;
      font-size: 18px;
      color: #3a84ff;
      font-weight: 900;
      position: absolute;
      top: 1px;
    }

    span {
      margin-left: 30px;
      font-size: 14px;
    }
  }

  .json-view-wrapper {
    padding: 10px 0;
  }

  .text-style {
    max-height: 54px;
    line-height: 18px;
    overflow: hidden;
    display: flex;
    flex-flow: column;

    span {
      flex-shrink: 0;
      font-size: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .expand-style {
    max-height: fit-content;

    span {
      white-space: normal;
    }
  }

  .json-text-style {
    background-color: #313238;
    color: #c4c6cc;
  }

  .locker-style {
    :deep(section) {
      /* stylelint-disable-next-line declaration-no-important */
      background-color: #313238 !important;

      > div:nth-child(1) {
        height: 50px;

        > div:nth-child(1) {
          height: 50px;
          line-height: 50px;
        }

        > div:nth-child(2) {
          height: 50px;
          line-height: 50px;
          color: #737987;
          font-size: 14px;

          > div {
            display: flex;
            justify-content: space-between;
            align-items: center;

            span {
              margin-right: 20px;
              display: inline-block;
              width: 68px;
              height: 32px;
              border: 1px solid #c4c6cc;
              line-height: 32px;
              text-align: center;
              color: #737987;
              cursor: pointer;
            }
          }
        }
      }
    }
  }
</style>
