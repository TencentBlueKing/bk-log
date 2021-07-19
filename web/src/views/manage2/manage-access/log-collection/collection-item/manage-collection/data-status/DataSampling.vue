<template>
  <section id="json-format">
    <bk-table
      v-bkloading="{ isLoading: loading }"
      :data="data"
      :empty-text="$t('btn.vacancy')"
      :size="size">
      <bk-table-column
        type="index"
        :label="$t('configDetails.number')"
        align="center"
        width="120"
        style="margin-top: 13px">
      </bk-table-column>
      <bk-table-column :label="$t('configDetails.originalLog')">
        <template slot-scope="props">
          <div
            class="text-style"
            @click="showClick($event, props.row.etl.batch)"
            @mouseenter="handleEnter($event, props.row.etl.batch)"
            @mouseleave="handleLeave">
            <span v-for="(val,index) in props.row.etl.batch" :key="index">{{ val }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column label="" prop=" " width="200"></bk-table-column>
      <bk-table-column :label="$t('configDetails.gatherTime')" width="200">
        <template slot-scope="props">
          <div>{{ props.row.etl.datetime }}</div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('dataSource.operation')" width="200">
        <template slot-scope="props">
          <div>
            <span class="option-text" @click="copyText(props.row.etl.batch, 'log')">{{ $t('btn.copy') }}</span>
            <span class="option-text" @click="chickFile(props.row)">{{ $t('configDetails.report') }}</span>
          </div>
        </template>
      </bk-table-column>
    </bk-table>
    <bk-sideslider
      class="locker-style"
      :is-show.sync="defaultSettings.isShow"
      :quick-close="true"
      :modal="false"
      :width="596">
      <div slot="header">{{ customSettings.title }}
        <span @click="copyText(JSON.stringify(jsonText))">{{ $t('btn.copy') }}</span></div>
      <div class="p20 json-text-style" slot="content">
        <VueJsonPretty :deep="5" :data="jsonText" />
      </div>
    </bk-sideslider>
  </section>
</template>

<script>
export default {
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
        title: this.$t('configDetails.logDetails'),
      },
      jsonText: '',
      defaultSettings: {
        isShow: false,
      },
      size: 'small',
    };
  },
  methods: {
    //  当原始日志超出三行时判断  点击选中效果
    showClick(e, val) {
      const labTarget = e.currentTarget;
      if (val.length > 3 && labTarget.offsetHeight === 54) {
        this.divClose();
        labTarget.style.height = `${val.length * 18}px`;
      } else {
        labTarget.style.height = '54px';
      }
    },
    divClose() {
      const divHeight = document.getElementsByClassName('text-style');
      for (let i = 0; i < divHeight.length; i++) {
        if (divHeight[i].offsetHeight > 54) {
          divHeight[i].style.height = '54px';
        }
      }
    },
    //  当原始日志超出三行时判断  鼠标选中效果
    handleEnter(e) {
      const cWidth = e.target.clientHeight;
      const sWidth = e.target.scrollHeight;
      if (sWidth - cWidth > 15) {
        this.instance = this.$bkPopover(e.target, {
          content: this.$t('dataManage.Click_all'),
          arrow: true,
          placement: 'top',
        });
        this.instance.show(1000);
      }
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
        }, this.$t('retrieve.copySuccess')),
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
    height: 54px;
    line-height: 18px;
    overflow: hidden;
    display: flex;
    flex-flow: column;

    span {
      flex-shrink: 0;
      font-size: 12px;
      overflow: hidden;
      white-space: nowrap;
    }
  }

  .json-text-style {
    background-color: #313238;
    color: #c4c6cc;
  }

  .locker-style {
    /deep/ section {
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
