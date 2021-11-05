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
    width="100%"
    ext-cls="set-dialog"
    v-model="isShowDialog"
    :show-mask="false"
    :close-icon="false"
    :show-footer="false"
    :draggable="false"
    :scrollable="true"
    :position="{
      top: 50,
      left: 0,
    }"
    @value-change="openPage"
    @after-leave="closePage"
  >
    <div class="setting-container">
      <div class="setting-title">
        <span>{{$t('retrieveSetting.setting')}}</span>
        <span class="bk-icon icon-close" @click="closeSetting"></span>
      </div>

      <div class="setting-main">
        <div class="setting-left">
          <div v-for="(item,index) of currentList" :key="item.id"
               :class="['setting-option',currentChoice === item.id ? 'current-color' : '']"
               @click="handleNavClick(item.id,index)">
            <span class="bk-icon icon-block-shape"></span>
            <span style="width: 110px">{{item.name}}</span>
            <div @click="handleStopProp">
              <bk-switcher theme="primary" v-model="item.isEditable"></bk-switcher>
            </div>
          </div>
        </div>

        <div class="setting-right">
          <div class="more-details">
            <div class="details">
              <p><span>{{$t('indexSetList.index_set')}}：</span>{{indexSetItem.index_set_name}}</p>
              <p><span>{{$t('索引')}}：</span>{{indexSetItem.indexName}}</p>
              <p><span>{{$t('来源')}}：</span>{{indexSetItem.scenario_name}}</p>
            </div>
            <div style="color: #3A84FF;cursor: pointer;">
              {{$t('retrieveSetting.moreDetails')}}
              <span class="log-icon icon-lianjie"></span>
            </div>
          </div>
          <div class="operation-container">
            <component :is="showComponent"
                       :global-editable="globalEditable"
                       :index-set-item="indexSetItem"
            ></component>
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
    isShowDialog: {
      type: Boolean,
      default: false,
    },
    selectChoice: {
      type: String,
      default: 'index',
    },
    indexSetItem: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      isOpenPage: true,
      currentChoice: '', // 当前nav选中
      showComponent: '', // 当前显示的组件
      currentList: [
        // {
        //   id: 'index',
        //   componentsName: 'FullTextIndex',
        //   name: this.$t('retrieveSetting.fullTextIndex'),
        //   isEditable: true,
        // },
        {
          id: 'extract',
          componentsName: 'FieldExtraction',
          name: this.$t('retrieveSetting.fieldExtraction'),
          isEditable: true,
        },
        {
          id: 'clustering',
          componentsName: 'LogCluster',
          name: this.$t('retrieveSetting.logCluster'),
          isEditable: true,
        }],
    };
  },
  computed: {
    globalEditable() {
      return  this.currentList.find(el => el.id === this.currentChoice)?.isEditable;
    },
  },
  methods: {
    handleSubmitFormData() {
    },
    handleNavClick(val, index) {
      this.currentChoice = val;
      this.showComponent = this.currentList[index].componentsName;
    },
    // 打开设置页面
    openPage() {
      if (this.isOpenPage) {
        this.currentChoice = this.selectChoice;
        this.showComponent = this.currentList.find(el => el.id === this.selectChoice)?.componentsName;
        this.isOpenPage = false;
      }
    },
    handleStopProp(e) {
      e.stopPropagation();
    },
    closeSetting() {
      this.$emit('closeSetting');
    },
    closePage() {
      this.isOpenPage = true;
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
  overflow-y: auto;
  min-width: 1460px;
  display: flex;
  justify-content: center;
  .setting-title{
    width: calc(100vw + 12px);
    height: 52px;
    min-width: 1460px;
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
    display: flex;
    position: relative;
    left: -100px;

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
          @extend .current-color
        }
      }
      @include container-shadow
    }

    .setting-right{
      width: 1000px;
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

  .current-color{
    color: #3A84FF;
    background-color: #E1ECFF;
  }
}

</style>
