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
  <div class="custom-create-container">
    <div class="create-form">
      <div class="form-title">{{$t('基础信息')}}</div>
      <bk-form :label-width="103" :model="formData">
        <bk-form-item :label="$t('customReport.dataID')" :required="true" :property="'name'">
          <bk-input class="form-input" :disabled="true" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.token')" :required="true" :property="'name'">
          <bk-input class="form-input" :disabled="true" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.dataName')" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.typeOfData')" :required="true" :property="'name'">
          <div style="margin-top: -4px">
            <div class="bk-button-group">
              <bk-button
                v-for=" (item,index) of dataTypeList"
                :key="index"
                :class="`${dataType === item.id ? 'is-selected' : ''}`"
                @click="handleChangeType(item.id)">
                {{item.name}}
              </bk-button>
            </div>
            <p class="group-tip" slot="tip">{{$t('customReport.typeTips')}}</p>
          </div>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.englishName')" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.dataClassification')" :required="true" :property="'name'">
          <bk-select v-model="formData.class" style="width: 320px;">
            <bk-option
              v-for="option in classList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
              <span>{{option.name}}</span>
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('customReport.instruction')">
          <bk-input
            style="width:529px"
            type="textarea"
            v-model="formData.desc"
            :placeholder="$t('customReport.notEntered')"
            :maxlength="100"></bk-input>
        </bk-form-item>
      </bk-form>
    </div>

    <div class="create-form">
      <div class="form-title">{{$t('customReport.storageSettings')}}</div>
      <bk-form :label-width="103" :model="formData">
        <bk-form-item required :label="$t('customReport.dataLink')">
          <bk-select
            style="width: 320px;"
            v-model="formData.data_link_id"
            :clearable="false"
            :disabled="false">
            <bk-option
              v-for="item in classList"
              :key="item.data_link_id"
              :id="item.data_link_id"
              :name="item.link_group_name">
            </bk-option>
          </bk-select>
        </bk-form-item>

        <bk-form-item :label="$t('dataSource.storage_cluster_name')" required :property="'name'">
          <bk-select v-model="formData.class" style="width: 320px;">
            <bk-option
              v-for="option in classList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
              <span>{{option.name}}</span>
            </bk-option>
          </bk-select>
          <bk-alert
            class="cluster-alert"
            type="info"
            slot="tip"
            :show-icon="false"
            :title="$t('dataSource.tips_formula')"></bk-alert>
        </bk-form-item>
        <bk-form-item :label="$t('configDetails.storageIndexName')" :required="true" :property="'name'">
          <div style="width: 320px;">
            <bk-input v-model="formData.name">
              <template slot="prepend">
                <div class="group-text">{{formData.name}}</div>
              </template>
            </bk-input>
          </div>
        </bk-form-item>
        <!-- 过期时间 -->
        <bk-form-item :label="$t('configDetails.expirationTime')">
          <bk-select
            style="width: 320px;"
            v-model="formData.retention"
            :clearable="false">
            <div slot="trigger" class="bk-select-name">
              {{ formData.retention + $t('天') }}
            </div>
            <template v-for="(option, index) in retentionDaysList">
              <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
            </template>
            <div slot="extension" style="padding: 8px 0;">
              <bk-input
                v-model="customRetentionDay"
                size="small"
                type="number"
                :placeholder="$t('输入自定义天数')"
                :show-controls="false"
                @enter="enterCustomDay($event, 'retention')"
              ></bk-input>
            </div>
          </bk-select>
        </bk-form-item>
        <!-- 副本数 -->
        <bk-form-item :label="$t('configDetails.copyNumber')">
          <bk-input
            v-model="formData.storage_replies"
            style="width:100px;"
            type="number"
            :max="3"
            :min="0"
            :precision="0"
            :clearable="false"
            :show-controls="true"
            @blur="changeCopyNumber"
          ></bk-input>
        </bk-form-item>
        <!-- 热数据\冷热集群存储期限 -->
        <bk-form-item :label="$t('热数据')" class="hot-data-form-item">
          <bk-select
            style="width: 320px;"
            v-model="formData.allocation_min_days"
            :clearable="false"
            :disabled="true">
            <template v-for="(option, index) in hotDataDaysList">
              <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
            </template>
            <div slot="extension" style="padding: 8px 0;">
              <bk-input
                v-model="customHotDataDay"
                size="small"
                type="number"
                :placeholder="$t('输入自定义天数')"
                :show-controls="false"
                @enter="enterCustomDay($event, 'hot')"
              ></bk-input>
            </div>
          </bk-select>
          <span v-if="false" class="disable-tips">
            {{$t('该集群未开启热数据设置')}}
            <a href="javascript:void(0);" @click="jumpToEsAccess">{{$t('前往ES源进行设置')}}</a>
          </span>
        </bk-form-item>
      </bk-form>
    </div>

    <div :class="`right-button ${isOpenWindow ? 'button-active' : ''}`"
         @click="isOpenWindow = !isOpenWindow">
      <i :class="`bk-icon icon-angle-double-${isOpenWindow ? 'right' : 'left'}`"></i>
    </div>
    <div :class="`right-window ${isOpenWindow ? 'window-active' : ''}`">
      <p class="window-top-title">{{$t('customReport.helpDocument')}}</p>
      <div class="content">
        <p class="content-title">{{$t('customReport.instructions')}}</p>
        <div class="content-row" v-for="(item,index) of list" :key="index">
          <span>{{item.title}}</span>
          <pre class="content-example">{{item.test}}</pre>
        </div>
      </div>
    </div>

    <div class="submit-btn">
      <bk-button
        class="fl"
        style="width:"
        theme="primary">
        {{$t('提交')}}
      </bk-button>
      <bk-button
        class="fr"
        theme="default">
        {{$t('取消')}}
      </bk-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'custom-report-create',
  data() {
    return {
      customRetentionDay: 0,
      customHotDataDay: 0,
      retentionDaysList: [],
      classList: [],
      hotDataDaysList: [],
      isOpenWindow: false,
      dataType: 'log',
      dataTypeList: [
        { id: 'log', name: '日志' },
        { id: 'trace', name: 'trace' },
        { id: 'otLog', name: 'ot日志' },
      ],
      formData: {
        name: 'test',
        scope: '',
        retention: 0,
        storage_replies: '',
        allocation_min_days: '',
      },
      list: [
        {
          title: '不同云区域Proxy信息',
          test: `云区域 0 0.0.0.0
云区域 1 1.1.1.1 
云区域 2 2.2.2.2`,
        },
        {
          title: '不同云区域Proxy信息',
          test: `云区域 0 0.0.0.0
云区域 1 1.1.1.1 
云区域 2 2.2.2.2`,
        },
        {
          title: '不同云区域Proxy信息',
          test: `云区域 0 0.0.0.0
云区域 1 1.1.1.1 
云区域 2 2.2.2.2`,
        },
      ],
    };
  },
  methods: {
    enterCustomDay() {},
    changeCopyNumber() {},
    jumpToEsAccess() {},
    handleChangeType(id) {
      this.dataType = id;
    },
  },
};
</script>

<style lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/mixins/flex";
.custom-create-container {
  padding:0 24px;
  .create-form {
    background-color: #fff;
    padding: 24px 37px;
    margin-top: 20px;
    border-radius: 2px;
    .form-title {
      font-size: 14px;
      color: #63656e;
      font-weight: 700;
      margin-bottom: 24px;
    }
    .form-input {
      width: 320px;
    }
    .group-tip {
      font-size: 12px;
      color: #979ba5;
    }
    .select-container {
      width: 280px;
      .icon-info-circle {
        color: #979ba5;
      }
      @include clearfix;
    }
    .cluster-alert {
      margin-top: 20px;
      padding-top: 8px;
      width: 529px;
      height: 50px;
    }
  }
  .right-button{
    width: 24px;
    height: 96px;
    border-radius: 8px 0 0 8px;
    border: 1px solid #dcdee5;
    border-right: none;
    background-color: #fafbfd;
    cursor: pointer;
    position: fixed;
    right: 0;
    top: calc(50vh - 48px);
    transition:right .5s;
    &.button-active{
      right: 400px;
    }
    @include flex-center;
  }
  .right-window{
    width: 400px;
    height: 100vh;
    background: #fff;
    border: 1px solid #dcdee5;
    position: fixed;
    right: -400px;
    top: 102px;
    z-index: 99;
    color: #63656e;
    transition:right .5s;
    &.window-active{
      right: 0;
    }
    .window-top-title{
      font-size: 12px;
      padding: 14px 16px 0;
    }
    .content{
      padding: 22px 20px 0;
      font-size: 12px;
      font-weight: 700;
      .content-title{
        margin-bottom: 8px;
      }
      .content-row{
        font-weight: 500;
        .content-example{
          margin-top: 6px;
          padding: 10px 14px;
          background: #f4f4f7;
          overflow-x: auto;
        }
      }
    }
  }
  .submit-btn {
    width: 140px;
    margin: 20px 20px 100px ;
    @include clearfix;
  }
}
</style>
