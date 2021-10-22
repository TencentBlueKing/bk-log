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
  <!-- 设置-日志聚类 -->
  <div class="setting-log-cluster">
    <bk-form :label-width="100">
      <bk-form-item
        :label="$t('聚类字段')"
        :required="true"
        :property="''">
        <br>
        <div class="form-item">
          <bk-select v-model="value" class="ml100" style="width: 482px;">
            <bk-option v-for="option in clusterField"
                       :key="option.id"
                       :id="option.id"
                       :name="option.name">
            </bk-option>
          </bk-select>
          <span v-bk-tooltips="iconMessage.field" class="right">
            <span class="bk-icon icon-info"></span>
          </span>
        </div>
      </bk-form-item>
      <div class="form-item">
        <span class="left-word">忽略数字</span>
        <span style="color:#979BA5">说明文字说明文字说明文字说明文字说明文字</span>
      </div>
      <div class="form-item">
        <span class="left-word">忽略字符</span>
        <span style="color:#979BA5">说明文字说明文字说明文字说明文字说明文字</span>
      </div>
      <div class="form-item">
        <span class="left-word">数据指纹</span>
        <bk-switcher class="left-word" v-model="demo1" theme="primary" size="large"></bk-switcher>
        <bk-alert style="width:780px" type="info" title="消息的提示文字"></bk-alert>
      </div>
      <div class="rule-container">
        <bk-form-item
          :label="$t('字段长度')"
          :required="true"
          :property="''">
          <br>
          <div class="form-item">
            <bk-input class="ml100" style="width: 94px;overflow: hidden;" type="number" v-model="value"></bk-input>
            <span style="margin-left: 8px">字节</span>
            <span v-bk-tooltips="iconMessage.byte" class="right">
              <span class="bk-icon icon-info"></span>
            </span>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t('过滤规则')"
          :property="''"
          class="container-item">
          <br>
          <bk-input class="ml100 w240" :clearable="true" v-model="value"></bk-input>
        </bk-form-item>
        <div class="container-item">
          <p style="height: 32px">聚类规则</p>
          <!-- <transition-group name="drag">
            <p
              @dragenter="dragenter($event, index)"
              @dragover="dragover($event, index)"
              @dragstart="dragstart(index)"
              :key="props.row.index"
              draggable>
              <span class="log-icon icon-drag-dots mr10"></span>
              <span>{{props.row.index}}</span>
            </p>
          </transition-group> -->
          <bk-table
            class="cluster-table"
            header-align="left"
            :data="tableData"
            @row-click="handleClickTableItem"
            align="left">
            <bk-table-column prop="index" label="序号" width="120">
              <template slot-scope="props">
                <p>
                  <span class="log-icon icon-drag-dots mr10"></span>
                  <span>{{props.row.index}}</span>
                </p>
              </template>
            </bk-table-column>
            <bk-table-column prop="regular" label="正则表达式" min-width="400"></bk-table-column>
            <bk-table-column prop="placeholder" label="占位符" width="150"></bk-table-column>
            <bk-table-column prop="operate" label="操作" width="150">
              <template slot-scope="props">
                <bk-button class="mr10" theme="primary" text @click="clusterEdit(props.row)">编辑</bk-button>
                <bk-button theme="primary" text @click="clusterRemove(props.row)">删除</bk-button>
              </template>
            </bk-table-column>
          </bk-table>
        </div>
        <div class="container-item">
          <p style="height: 32px">原始日志</p>
          <div class="log-style">
            <bk-input
              placeholder=" "
              data-test-id=""
              :type="'textarea'"
              :rows="3"
              :input-style="{
                'background-color': '#313238',
                height: '82px',
                'line-height': '24px',
                color: '#C4C6CC',
                borderRadius: '2px'
              }"
              v-model.trim="logOriginal">
            </bk-input>
          </div>
        </div>
        <div class="container-item">
          <p style="height:32px">效果</p>
          <bk-input
            placeholder=" "
            data-test-id=""
            :disabled="true"
            :type="'textarea'"
            :rows="3"
            :input-style="{
              'background-color': '#FAFBFD',
              height: '82px',
              'line-height': '24px',
              color: '#000000',
              borderRadius: '2px'
            }"
            v-model.trim="logOriginal">
          </bk-input>
        </div>
      </div>
      <bk-form-item class="change-button">
        <bk-button
          theme="primary"
          :title="$t('保存')"
          @click.stop.prevent="handleSubmit"
          :loading="isHandle">
          {{ $t('保存') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('重置')"
          @click="cancel">
          {{ $t('重置') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      clusterField: [],
      tableData: [{
        index: 1,
        regular: 1,
        placeholder: 1,
        operate: 1,
      }],
      logOriginal: '',
      rules: {},
      demo1: true,
      value: '',
      isHandle: false,
      iconMessage: {
        field: {
          content: '提示信息1',
          placements: ['right'],
        },
        byte: {
          content: '提示信息2',
          placements: ['right'],
        },
      },
    };
  },
  methods: {
    handleSubmit() {},
    cancel() {},
    clusterEdit($row) {
      console.log($row);
    },
    clusterRemove($row) {
      console.log($row);
    },
    handleClickTableItem(row, event, column, rowIndex, columnIndex) {
      console.log(row, event, column, rowIndex, columnIndex);
    },
  },
};
</script>

<style lang="scss" scoped>
/deep/ .bk-label{
  text-align: left;
}
.setting-log-cluster{
  .form-item{
    display: flex;
    align-items: center;
    margin-bottom: 25px;

    .left-word{
      font-weight: 700;
      font-size: 15px;
      margin-right: 16px;
    }

    .bk-icon{
      margin-left: 8px;
      font-size: 18px;
      color: #979BA5;
    }

  }

  .rule-container{
    padding: 0 16px;

    .container-item{
      margin-bottom: 40px;
    }
  }

  .log-style {
    height: 82px;

    /*background-color: #313238;*/
    /deep/.bk-form-textarea:focus {
      background-color: #313238 !important;
      border-radius: 2px;
    }

    /deep/.bk-textarea-wrapper {
      border: none;
    }

  }

  .change-button{
    margin:40px 0 40px -100px;
  }
}

.ml100{
  margin-left: -100px;
}

.mr10{
  margin-right: 10px;
}

.w240{
  width: 240px;
}
</style>
