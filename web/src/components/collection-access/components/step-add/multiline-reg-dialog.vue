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
  <bk-dialog
    :value="showDialog"
    :title="$t('行首正则调试')"
    :ok-text="$t('保存')"
    :mask-close="false"
    :position="{ top: dialogTop }"
    width="680"
    header-position="left"
    @confirm="handleSave"
    @value-change="handleValueChange">
    <div class="multiline-reg-dialog-content">
      <bk-form :label-width="124" :model="formData" ref="formRef">
        <bk-form-item
          :label="$t('日志样例')"
          :required="true"
          :rules="notEmptyRule"
          property="log_sample"
          style="margin-bottom: 20px;">
          <bk-input v-model.trim="formData.log_sample" type="textarea" :rows="6"></bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t('行首正则表达式')"
          :required="true"
          :rules="notEmptyRule"
          property="multiline_pattern"
          style="margin-bottom: 20px;">
          <bk-input v-model.trim="formData.multiline_pattern"></bk-input>
        </bk-form-item>
      </bk-form>
      <div class="test-container">
        <bk-button
          theme="primary"
          class="mr15"
          :loading="isMatchLoading"
          @click="handleMatch">
          {{ $t('匹配验证') }}
        </bk-button>
        <div v-if="matchLines !== null" class="test-result">
          <span :class="matchLines ? 'bk-icon icon-check-circle-shape' : 'bk-icon icon-close-circle-shape'"></span>
          <template v-if="matchLines">
            <i18n path="成功匹配 {0} 条日志">
              <span class="match-counts">{{ matchLines }}</span>
            </i18n>
          </template>
          <template v-else>{{ $t('未成功匹配') }}</template>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false,
    },
    oldPattern: { // 父组件输入的行首正则内容
      type: String,
      default: '',
    },
  },
  data() {
    const top = (window.innerHeight - 380) / 2;
    const dialogTop = top < 70 ? 70 : top;
    return {
      dialogTop,
      isMatchLoading: false, // 匹配验证
      formData: {
        log_sample: '', // 日志样例
        multiline_pattern: '', // 行首正则表达式
      },
      notEmptyRule: [{
        required: true,
        trigger: 'blur',
      }],
      matchLines: null, // 匹配条数
    };
  },
  methods: {
    handleValueChange(val) {
      this.$emit('update:showDialog', val);
      if (val) { // 打开时填入采集页行首正则内容
        this.formData.multiline_pattern = this.oldPattern;
      } else { // 关闭时重置数据
        this.formData.log_sample = '';
        this.formData.multiline_pattern = '';
        this.matchLines = null;
      }
    },
    // 匹配验证
    async handleMatch() {
      try {
        await this.$refs.formRef.validate();
        this.isMatchLoading = true;
        const res = await this.$http.request('collect/regexDebug', {
          params: {
            collector_id: Number(this.$route.params.collectorId),
          },
          data: this.formData,
        });
        this.matchLines = res.data.match_lines;
      } catch (e) {
        console.warn(e);
        this.matchLines = 0;
      } finally {
        this.isMatchLoading = false;
      }
    },
    handleSave() {
      this.$emit('update:oldPattern', this.formData.multiline_pattern);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '@/scss/mixins/scroller';

  .multiline-reg-dialog-content {
    .test-container {
      display: flex;
      align-items: center;
      padding-left: 124px;

      .test-result {
        display: flex;
        align-items: center;
        line-height: 20px;

        .bk-icon {
          font-size: 12px;
          margin-right: 6px;
        }

        .icon-check-circle-shape {
          color: #2dcb56;
        }

        .icon-close-circle-shape {
          color: #ea3636;
        }

        .match-counts {
          margin: 0 4px;
          color: #3a84ff;
          font-weight: bold;
        }
      }
    }

    :deep(.bk-label-text) {
      color: #313238;
    }

    :deep(.bk-form-textarea) {
      @include scroller($backgroundColor: #C4C6CC, $width:4px);
    }
  }
</style>
