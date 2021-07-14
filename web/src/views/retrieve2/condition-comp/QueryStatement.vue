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
  <div class="tab-item-title">{{$t('查询语句')}}
    <span class="log-icon icon-help" v-bk-tooltips="tips"></span>
    <div id="retrieve-help-tips-content">
      <div>
        {{$t('可输入SQL语句进行快速查询')}}
        <a v-if="docCenterUrl" :href="docCenterUrl" target="_blank" class="tips-link">
          {{$t('查看语法')}}<span class="log-icon icon-lianjie"></span>
        </a>
      </div>
      <div class="title">{{$t('精确匹配')}}</div>
      <div class="detail">author:"John Smith" AND age:20</div>
      <div class="title">{{$t('字段名匹配')}}</div>
      <div class="detail">status:active</div>
      <div class="detail">title:(quick brown)</div>
      <div class="title">{{$t('字段名模糊匹配')}}</div>
      <div class="detail">vers\*on:(quick brown)</div>
      <div class="title">{{$t('通配符匹配')}}</div>
      <div class="detail">qu?ck bro*</div>
      <div class="title">{{$t('正则匹配')}}</div>
      <div class="detail">name:/joh?n(ath[oa]n/</div>
      <div class="title">{{$t('范围匹配')}}</div>
      <div class="detail">count:[1 TO 5]</div>
      <div class="detail">count:[1 TO 5}</div>
      <div class="detail">count:[10 TO *]</div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tips: {
        trigger: 'click',
        theme: 'light',
        allowHtml: true,
        content: '#retrieve-help-tips-content',
        placement: 'bottom-start',
        distance: 9,
      },
      docCenterUrl: window.BK_DOC_QUERY_URL,
    };
  },
};
</script>

<style lang="scss" scoped>
  .icon-help {
    color: #979ba5;
    font-size: 14px;
    cursor: pointer;
    margin-left: 7px;
  }

  .tips-link {
    color: #3a84ff;
    margin-left: 5px;

    .icon-lianjie {
      margin-left: 3px;
    }
  }

  #retrieve-help-tips-content {
    color: #63656e;
    max-width: 264px;
    word-break: normal;

    .title {
      font-weight: 600;
      margin: 10px 0 4px;
    }

    .detail {
      line-height: 18px;
    }
  }
</style>
