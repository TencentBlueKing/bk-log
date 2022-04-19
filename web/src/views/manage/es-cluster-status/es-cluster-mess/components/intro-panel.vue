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
  <div class="intro-panel">
    <div :class="`right-window ${isOpenWindow ? 'window-active' : ''}`">
      <!-- <span class="bk-icon icon-more"></span> -->
      <div class="create-btn details" @click="handleActiveDetails(null)">
        <span class="bk-icon icon-text-file" :style="`color:${isOpenWindow ? '#3A84FF;' : ''}`"></span>
      </div>
      <div class="top-title">
        <p> {{$t('说明文档')}}</p>
        <div class="create-btn close" @click="handleActiveDetails(false)">
          <span class="bk-icon icon-minus-line"></span>
        </div>
      </div>
      <div class="help-main">
        <div class="help-md-container" v-for="(item, index) of customTypeIntro" :key="index">
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-html="item.help_md"></div>
          <template v-if="item.button_list.length">
            <div v-for="(sItem, sIndex) of item.button_list" :key="sIndex">
              <a class="help-a-link"
                 v-if="sItem.type === 'blank'"
                 target="_blank"
                 :href="sItem.url">
                {{$t('跳转至')}}{{item.name}}
                <span class="log-icon icon-lianjie"></span>
              </a>
              <bk-button
                v-else
                class="wx-button"
                theme="primary"
                size="small"
                :outline="true"
                @click="handleCreateAGroup(sItem)">{{$t('一键拉群')}}</bk-button>
            </div>
          </template>
        </div>
      </div>
    </div>
    <bk-dialog
      v-model="isShowDialog"
      theme="primary"
      header-position="left"
      width="600"
      :mask-close="false"
      :title="$t('一键拉群')"
      @confirm="handleSubmitQWGroup"
      @cancel="handleCancelQWGroup">
      <div class="group-container">
        <div class="group-title-container">
          <div class="qw-icon">
            <span class="ag-doc-icon doc-qw"></span>
          </div>
          <div class="hint">
            <p>{{$t('一键拉群功能')}}</p>
            <p>{{$t('qwGroupTips')}}</p>
          </div>
        </div>
        <div class="group-body-container">
          <bk-user-selector
            :value="formDataAdmin"
            :api="userApi"
            :placeholder="$t('请选择群成员')"
            :tag-clearable="false"
            @change="handleChangePrincipal">
          </bk-user-selector>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import BkUserSelector from '@blueking/user-selector';

export default {
  components: {
    BkUserSelector,
  },
  props: {
    isOpenWindow: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      isShowDialog: false,
      formDataAdmin: [],
      baseAdmin: [], // 本人和列表里的人物，不能够进行删除操作
      chatName: '',
      userApi: window.BK_LOGIN_URL,
    };
  },
  computed: {
    ...mapState({
      userMeta: state => state.userMeta,
    }),
    ...mapGetters({
      globalsData: 'globals/globalsData',
    }),
    esSourceList() {
      const { es_source_type: esSourceList } = this.globalsData;
      return esSourceList || [];
    },
    customTypeIntro() {
      return this.filterSourceShow(this.esSourceList) || [];
    },
  },
  methods: {
    filterSourceShow(list) {
      const filterList = list.filter(item => (item.help_md || item.button_list.length));
      return filterList || [];
    },
    handleActiveDetails(state) {
      this.$emit('handleActiveDetails', state ? state : !this.isOpenWindow);
    },
    handleCreateAGroup(adminList) {
      this.isShowDialog = true;
      this.chatName = adminList.chat_name;
      this.formDataAdmin = adminList.users.concat([this.userMeta.username]);
      this.baseAdmin = JSON.parse(JSON.stringify(this.formDataAdmin)); // 赋值最基础的人员
    },
    handleSubmitQWGroup() {
      const data = {
        user_list: this.formDataAdmin,
        name: this.chatName,
      };
      this.$http.request('collect/createWeWork', {
        data,
      }).then((res) => {
        if (res.data) {
          this.$bkMessage({
            theme: 'success',
            message: this.$t('创建成功'),
          });
        }
      });
    },
    handleCancelQWGroup() {
      this.formDataAdmin = [];
      this.baseAdmin = [];
      this.chatName = '';
    },
    handleChangePrincipal(val) {
      const setList = new Set([...this.baseAdmin, ...val]);
      this.formDataAdmin = [...setList];
    },
  },
};
</script>

<style lang="scss">
  @import '@/scss/mixins/flex';
  @import '@/scss/mixins/scroller';

  .intro-panel {
    .right-window {
      width: 320px;
      height: 100vh;
      background: #fff;
      border: 1px solid #dcdee5;
      position: fixed;
      right: -400px;
      top: 103px;
      z-index: 99;
      color: #63656e;
      transition: right .5s;
      padding: 16px 24px 0;

      .top-title {
        height: 28px;
      }

      &.window-active {
        right: 0;
      }

      h1 {
        font-size: 12px;
        font-weight: 700;
        margin: 26px 0 10px;

        &:first-child {
          margin-top: 0;
        }
      }

      ul {
        margin-left: 10px;

        li {
          margin-top: 8px;
          list-style: inside;
          font-size: 12px;
        }
      }

      p {
        font-size: 12px;
      }

      pre {
        margin: 0;
        margin-top: 6px;
        padding: 10px 14px;
        background: #f4f4f7;
        overflow-x: auto;

        @include scroller;
      }

      code {
        color: #BF6F84;;
        background: #F4EAEE;
      }

      .help-main{
        height: 100%;
        overflow-y: auto;
      }

      .help-md-container{
        padding: 16px 0;
        border-bottom: 1px solid #EAEBF0;
        .help-a-link {
          display: inline-block;
          margin: 10px 0;
          font-size: 12px;
          color: #3a84ff;
          span {
            transform: translateY(-1px);
            display: inline-block;
          }
        }
        .wx-button{
          margin: 10px 0;
        }
      }
    }

    .create-btn {
      width: 24px;
      height: 24px;
      position: absolute;

      @include flex-center;

      &.details {
        top: 64px;
        right: 16px;
        position: fixed;
        transform: rotateZ(360deg) rotateX(180deg);

        @include flex-center;
      }

      &.close {
        top: 10px;
        right: 16px;
      }

      &:hover {
        cursor: pointer;
        background: #f0f1f5;
        color: #3a84ff;
        border-radius: 2px;
      }
    }
  }
  .group-container{
    .group-body-container{
      height: 100px;
      & .user-selector{
        width: 100%;
        height: 100% !important;
      }
      .user-selector-input{
        height: 100% !important;
      }
    }
  }
</style>
