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
      <div class="form-title">基础信息</div>
      <bk-form :label-width="103" :model="formData">
        <bk-form-item label="数据ID" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item label="数据token" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item label="数据名称" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item label="数据类型" :required="true" :property="'name'">
          <div class="bk-button-group">
            <bk-button class="is-selected">日志</bk-button>
            <bk-button>trace</bk-button>
            <bk-button>ot日志</bk-button>
          </div>
          <p class="group-tip" slot="tip">自定义上报指标数据，可以通过HTTP等方式进行上报，自定义上报有一定的数据格式要求，具体可以查看使用说明</p>
        </bk-form-item>
        <bk-form-item label="英文名" :required="true" :property="'name'">
          <bk-input class="form-input" v-model="formData.name"></bk-input>
        </bk-form-item>
        <bk-form-item label="数据分类" :required="true" :property="'name'">
          <bk-select v-model="formData.class" style="width:250px;">
            <bk-option
              v-for="option in classList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
              <span>{{option.name}}</span>
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="说明">
          <bk-input
            style="width:529px"
            type="textarea"
            placeholder="未输入"
            v-model="formData.desc"
            :maxlength="100"></bk-input>
        </bk-form-item>
        <bk-form-item label="存储集群" :required="true" :property="'name'">
          <bk-select v-model="formData.class" style="width:250px;">
            <bk-option
              v-for="option in classList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
              <span>{{option.name}}</span>
            </bk-option>
          </bk-select>
          <bk-alert class="cluster-alert" :show-icon="false" type="info" title="消息的提示文字" slot="tip"></bk-alert>
        </bk-form-item>
        <bk-form-item label="存储索引名" :required="true" :property="'name'">
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
      <p class="window-top-title">帮助文档</p>
      <div class="content">
        <p class="content-title">使用方法</p>
        <div class="content-row" v-for="(item,index) of list" :key="index">
          <span>{{item.title}}</span>
          <pre class="content-example">{{item.test}}</pre>
        </div>
      </div>
    </div>
    <div class="submit-btn">
      <bk-button
        class="fl"
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
  },
};
</script>

<style lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/mixins/flex";
.custom-create-container {
  padding: 20px 24px;
  .create-form {
    background-color: #fff;
    padding: 24px 37px;
    border-radius: 2px;
    box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, 0.05);
    .form-title {
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 24px;
    }
    .form-input {
      width: 410px;
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
    position: absolute;
    right: 0;
    top: calc(48vh - 48px);
    transition:right .5s;
    &.button-active{
      right: 400px;
    }
    @include flex-center;
  }
  .right-window{
    width: 400px;
    height: calc(100% - 52px);
    background: #fff;
    border: 1px solid #dcdee5;
    position: absolute;
    right: -400px;
    top: 52px;
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
    width: 160px;
    margin: 20px 0 100px 0;
    @include clearfix;
  }
}
</style>
