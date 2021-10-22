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
  <!-- 检索-设置 -->
  <bk-dialog
    v-model="showDialog"
    width="100%"
    :position="logPosition"
    ext-cls="set-dialog"
    :show-mask="false"
    :close-icon="false"
    :show-footer="false"
    :draggable="false"
    :scrollable="true"
  >
    <div class="setting-container">
      <div class="setting-title">
        <span>设置</span>
        <span class="bk-icon icon-close" @click="closeSetting"></span>
      </div>
      <div class="setting-main">
        <div class="setting-left">
          <div v-for="(item,index) of currentList"
               :key="item.id"
               :class="['setting-option',currentChoice === index ? 'blue-color' : '']"
               @click.stop="handleChoice(index)">
            <span class="bk-icon icon-block-shape"></span>
            <span style="width: 110px">{{item.name}}</span>
            <bk-switcher v-model="item.switch" theme="primary" size="small"></bk-switcher>
          </div>
        </div>
        <div class="setting-right">
          <div class="more-details">
            <div class="details">
              <p><span>索引集：</span>某某日志</p>
              <p><span>索引：</span>123</p>
              <p><span>来源：</span>某某日志/某某</p>
            </div>
            <div style="color: #3A84FF;cursor: pointer;">
              更多详情
              <span class="log-icon icon-lianjie"></span>
            </div>
          </div>
          <div class="operation-container">
            <full-text-index v-if="currentChoice === 0" />
            <field-extraction v-if="currentChoice === 1" />
            <log-cluster v-if="currentChoice === 2" />
          </div>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import FullTextIndex from './FullTextIndex';
import LogCluster from './LogCluster';
import FieldExtraction from './FieldExtraction';

export default {
  components: {
    FullTextIndex,
    FieldExtraction,
    LogCluster,
  },
  props: {
    showDialog: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      demo1: true,
      logPosition: {
        top: 50,
        left: 0,
      },
      currentChoice: 0,
      currentList: [{
        id: 'full_text_index',
        name: this.$t('fullTextIndex'),
        switch: true,
      },
      {
        id: 'field_extraction',
        name: this.$t('fieldExtraction'),
        switch: true,
      },
      {
        id: 'log_cluster',
        name: this.$t('logCluster'),
        switch: true,
      }],
    };
  },
  methods: {
    closeSetting() {
      this.$emit('closeSetting');
    },
    handleChoice(number) {
      this.currentChoice = number;
    },
  },
};
</script>

<style lang="scss" scoped>
/deep/.bk-dialog-body{
  background-color: #F5F6FA;
  padding: 0;
}
/deep/.bk-dialog-tool{
  display: none;
}

@mixin container-shadow(){
  background: #FFFFFF;
  border-radius: 2px;
  box-shadow: 0px 2px 4px 0px rgba(25,25,41,0.05);
}

.setting-container{
  height: calc(100vh - 52px);
  overflow-y: scroll;

  .setting-title{
    width: 100%;
    height: 52px;
    min-width: 1400px;
    line-height: 52px;
    font-size: 16px;
    text-align: center;
    position: fixed;
    z-index: 99;
    background-color: #FFFFFF;
    border-bottom: 1px solid #DCDEE5;
    // box-shadow:0 3px 6px #DEE0E7 ;

    .bk-icon {
      font-size: 32px;
      cursor: pointer;
      position: absolute;
      top: 10px;
      right: 24px;
    }
  }

  .setting-main{
    padding: 72px 40px 0;
    height: 100%;
    display: flex;
    position: relative;
    z-index: 0;

    .setting-left{
      min-width: 240px;
      height: 365px;
      padding-top:4px;

      .setting-option{
        height: 40px;
        font-size: 15px;
        margin: 4px 0;
        display:flex;
        cursor: pointer;
        justify-content: space-evenly;
        align-items: center;
        transition: all .3s;
        &:hover{
          @extend .blue-color
        }
      }
      @include container-shadow
    }

    .setting-right{
      width: 62.5vw;
      min-width: 1000px;
      margin-left: 20px;

      .more-details{
        height: 48px;
        padding: 0 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .details{
          display: flex;
          p{
            margin-right: 40px;
            span{
              color: #979BA5;
            }
          }
        }
        @include container-shadow
      }

      .operation-container{
        margin-top: 20px;
        min-height: 770px;
        padding: 24px 40px 100px;
        @include container-shadow
      }
    }
  }

  .blue-color{
    color: #3A84FF;
    background-color: #E1ECFF;
  }
}

</style>
