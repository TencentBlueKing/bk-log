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
  <div class="editor-container">
    <template>
      <div class="editor-title">
        <div>{{$t('编辑器')}}</div>
        <div class="right-container">
          <slot name="right"></slot>
          <span v-bk-tooltips="{ distance: 20, content: $t('全屏'), delay: 300 }">
            <span v-if="!isFull" class="bk-icon icon-full-screen" @click="openFullScreen"></span>
          </span>
        </div>
      </div>
    </template>
    <div ref="editorRefs"
         :style="{ height: calcSize(renderHeight), width: calcSize(renderWidth), position: 'relative' }">
      <span
        v-if="isFull"
        class="bk-icon icon-un-full-screen"
        style="right: 20px"
        @click="exitFullScreen"
      ></span>

      <div v-if="problemList.length"
           class="problems"
           ref="problemsRef"
           :style="`height: ${problemHeight}px;`">
        <div class="problems-drag" @mousedown="handleMouseDown"></div>
        <template v-for="(item, index) of problemList">
          <div
            class="problem"
            :key="index"
            @click="handelClickProblemBtn(item.lineNumber, item.column)">
            <div :class="`bk-icon ${item.codiconClass}`"></div>
            <div class="problem-text">
              <span>{{ item.problemMessage }}</span>
              <span class="problem-line" v-if="item.lineNumber && item.column">
                [{{item.lineNumber}}, {{item.column}}]
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
import * as monaco from 'monaco-editor';

self.MonacoEnvironment = {
  getWorkerUrl(moduleId, label) {
    if (label === 'yaml') {
      return process.env.NODE_ENV === 'production' ? `${window.BK_STATIC_URL}/yaml.worker.js` : './yaml.worker.js';
    }
    return process.env.NODE_ENV === 'production'
      ? `${window.BK_STATIC_URL}/editor.worker.js`
      : './editor.worker.js';
  },
};

export default {
  model: {
    prop: 'value',
    event: 'change',
  },
  props: {
    options: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: String,
      default: '',
    },
    theme: {
      type: String,
      default: 'vs-dark',
    },
    language: {
      type: String,
      require: true,
    },
    fullScreen: {
      type: Boolean,
      default: false,
    },
    width: {
      type: String,
      default: '100%',
    },
    height: {
      type: Number,
      default: 600,
    },
    isShowProblem: {
      type: Boolean,
      default: true,
    },
    fontFamily: {
      type: String,
      default: 'Microsoft YaHei',
    },
    warningList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      editor: null,
      renderWidth: '100%',
      renderHeight: 500,
      problemList: [],
      isHaveError: false,
      isFull: false,
      problemHeight: null,
      range: [20, 500],
    };
  },
  watch: {
    value(newValue) {
      if (this.editor) {
        if (newValue !== this.editor.getValue()) {
          this.editor.setValue(newValue);
        }
      }
    },
    options: {
      deep: true,
      handler(options) {
        if (this.editor) {
          this.editor.updateOptions(options);
          this.editor.layout();
        }
      },
    },
    language(newVal) {
      this.editor && monaco.editor.setModelLanguage(monaco.editor.getModels()[0], newVal);
    },
    theme(newVal) {
      this.editor && monaco.editor.setTheme(newVal);
    },
    width(newVal) {
      this.renderWidth = newVal;
      this.initWidth = this.width;
    },
    height(newVal) {
      this.renderHeight = newVal;
      this.initHeight = this.height;
    },
    warningList(newVal) {
      this.setWaringMarker(newVal);
    },
    'problemList.length'() {
      this.isHaveError = this.problemList.some(item => item.codiconClass === 'icon-close-circle-shape');
      this.$emit('get-problem-state', this.isHaveError);
    },
  },
  mounted() {
    this.initWidth = this.width;
    this.initHeight = this.height;
    this.renderWidth = this.width;
    this.renderHeight = this.height;
    this.initMonaco(monaco);
    this.$nextTick().then(() => {
      this.editor.layout();
    });
    window.addEventListener('resize', this.handleFullScreen);
  },
  beforeDestroy() {
    this.editor?.dispose();
    window.removeEventListener('resize', this.handleFullScreen);
  },
  methods: {
    calcSize(size) {
      const _size = size.toString();
      if (_size.match(/^\d*$/)) return `${size}px`;
      if (_size.match(/^[0-9]?%$/)) return _size;
      return '100%';
    },

    initMonaco(monaco) {
      const options = Object.assign(
        {
          value: this.value,
          theme: this.theme,
          language: this.language,
          fontFamily: this.fontFamily,
          fontSize: 16,
          cursorBlinking: 'solid',
          automaticLayout: true,
        },
        this.options,
      );
      this.editor = monaco.editor.create(this.$refs.editorRefs, options);
      this.$emit('editorDidMount', this.editor);
      this.editor.onContextMenu(event => this.$emit('contextMenu', event));
      this.editor.onDidBlurEditorWidget(() => this.$emit('blur'));
      this.editor.onDidBlurEditorText(() => this.$emit('blurText'));
      this.editor.onDidChangeConfiguration(event => this.$emit('configuration', event));
      this.editor.onDidChangeCursorPosition((event) => {
        this.$emit('position', event);
      });
      this.editor.onDidChangeCursorSelection((event) => {
        this.$emit('selection', event);
      });
      this.editor.onDidChangeModelContent((event) => {
        const value = this.editor.getValue();
        if (this.value !== value) {
          this.$emit('change', value, event);
        }
      });
      this.editor.onDidChangeModelDecorations(event => this.$emit('modelDecorations', event));
      this.editor.onDidChangeModelLanguage(event => this.$emit('modelLanguage', event));
      this.editor.onDidChangeModelOptions(event => this.$emit('modelOptions', event));
      this.editor.onDidDispose(event => this.$emit('afterDispose', event));
      this.editor.onDidFocusEditorWidget(() => this.$emit('focus'));
      this.editor.onDidFocusEditorText(() => this.$emit('focusText'));
      this.editor.onDidLayoutChange(event => this.$emit('layout', event));
      this.editor.onDidScrollChange(event => this.$emit('scroll', event));
      this.editor.onKeyDown(event => this.$emit('keydown', event));
      this.editor.onKeyUp(event => this.$emit('keyup', event));
      this.editor.onMouseDown(event => this.$emit('mouseDown', event));
      this.editor.onMouseLeave(event => this.$emit('mouseLeave', event));
      this.editor.onMouseMove(event => this.$emit('mouseMove', event));
      this.editor.onMouseUp(event => this.$emit('mouseUp', event));
      this.isShowProblem && (this.markerChange(monaco));
    },

    exitFullScreen() {
      const exitMethod = document.exitFullscreen; // W3C
      if (exitMethod) {
        exitMethod.call(document);
      }
    },

    openFullScreen() {
      const element = this.$refs.editorRefs;
      const fullScreenMethod =        element.requestFullScreen // W3C
        || element.webkitRequestFullScreen // FireFox
        || element.webkitExitFullscreen // Chrome等
        || element.msRequestFullscreen; // IE11
      if (fullScreenMethod) {
        fullScreenMethod.call(element);
        this.renderWidth = window.screen.width;
        this.renderHeight = window.screen.height;
        this.$nextTick().then(() => {
          this.editor.layout();
        });
      } else {
        this.$bkMessage({
          showClose: true,
          message: `${this.$t('此浏览器不支持全屏操作')}, ${this.$t('请使用chrome浏览器')}`,
          theme: 'warning',
        });
      }
    },

    handleFullScreen() {
      if (document.fullscreenElement) {
        this.isFull = true;
        return true;
      }
      if (this.isFull) {
        this.isFull = false;
        this.renderWidth = this.initWidth;
        this.renderHeight = this.initHeight;
        this.$nextTick().then(() => {
          this.editor.layout();
        });
      }
      return false;
    },

    /**
     * @desc: 报错提示与警告提示
     * @param { Object } resource
     * @param { Object } monaco
     */
    markerChange(monaco) {
      monaco.editor.onDidChangeMarkers(([resource]) => {
        const markers = monaco.editor.getModelMarkers({ resource });
        this.problemList = [];
        for (const marker of markers) {
          if (marker.severity === monaco.MarkerSeverity.Hint) {
            continue;
          }
          this.problemList.push({
            codiconClass: marker.severity === monaco.MarkerSeverity.Warning
              ? 'icon-exclamation-circle-shape'
              : 'icon-close-circle-shape',
            lineNumber: marker.startLineNumber,
            column: marker.startColumn,
            problemMessage: marker.message,
          });
        }
      });
    },

    /**
     * @desc: 设置警告提示
     * Tips: 传参参数为 [{startLineNumber:xxx, endLineNumber:xxx, startColumn:xxx, endColumn:xxx, message:xxx}]
     */
    setWaringMarker(markers = []) {
      if (this.isHaveError) return;
      const waringMarkers = markers.map(item => ({
        lineNumber: item.startLineNumber,
        column: item.startColumn,
        problemMessage: item.message,
        codiconClass: 'icon-exclamation-circle-shape',
      }));
      this.problemList = waringMarkers;
      // 这是monaco编辑器自带的告警方法 行和列为0的话默认1-1 暂时不显示行列标记
      // monaco.editor.setModelMarkers(this.editor.getModel(), 'owner', waringMarkers);
    },
    /**
     * @desc: 警告bottom点击鼠标事件
     */
    handelClickProblemBtn(lineNumber, column) {
      if (!lineNumber || !column) return;
      this.editor.setPosition({
        lineNumber,
        column,
      });
      this.editor.focus();
    },
    handleMouseDown(e) {
      const node = e.target;
      const parentNode = node.parentNode;
      this.problemHeight = parentNode.offsetHeight;

      if (!parentNode) return;

      const rect = parentNode.getBoundingClientRect();
      const handleMouseMove = (event) => {
        const [min, max] = this.range;
        const newHeight = rect.top - event.clientY + rect.height;
        if (newHeight < min) {
          this.problemHeight = 0;
        } else {
          this.problemHeight = Math.min(newHeight, max);
        }
      };
      const handleMouseUp = () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    },
  },
};
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/flex.scss';

.editor-container {
  width: 100%;
}

.problems {
  width: 100%;
  padding: 6px 20px;
  position: absolute;
  overflow-y: auto;
  max-height: 500px;
  z-index: 999;
  background: #212121;
  bottom: 0;
}

.problem {
  display: flex;
  margin: 6px 0;
  align-items: center;
  color: #dcdee5;
  cursor: pointer;

  .problem-text {
    margin-left: 10px;
  }

  &:hover {
    color: #fff;
    background: #424242;
  }
}

.problems-drag {
  position: sticky;
  width: 26px;
  height: 6px;
  border-radius: 3px;
  transform: translateY(-50%);
  left: calc(50% - 13px);
  z-index: 100;

  @include flex-center();

  &::after {
    content: ' ';
    height: 0;
    width: 100%;
    border-bottom: 3px dotted #63656e;
    position: absolute;
    left: 2px;
  }

  &:hover {
    user-select: none;
    cursor: s-resize;
  }
}

.editor-title {
  width: 100%;
  padding: 14px 18px;
  display: flex;
  color: #979ba5;
  justify-content: space-between;
  background: #2e2e2e;

  .right-container {
    @include flex-center();
  }
}

.icon-un-full-screen {
  position: absolute;
  top: 10px;
  z-index: 1;
  color: #fff;
}

.bk-icon {
  margin-right: 8px;
  cursor: pointer;
}

.icon-close-circle-shape {
  color: #b34747;
}

.icon-exclamation-circle-shape {
  color: #ff9c01;
}

.problem-line {
  color: #979ba5;
}
</style>
