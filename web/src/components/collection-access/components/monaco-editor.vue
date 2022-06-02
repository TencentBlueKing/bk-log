<template>
  <div class="editor-container">
    <template>
      <div class="editor-title">
        <div>{{$t('编辑器')}}</div>
        <div class="right-container">
          <slot name="right"></slot>
          <span v-if="!isFull" class="bk-icon icon-full-screen" @click="openFullScreen"></span>
        </div>
      </div>
    </template>
    <div ref="editorRefs"
         class="editor"
         :style="{ height: calcSize(renderHeight), width: calcSize(renderWidth), position: 'relative' }">
      <span
        v-if="isFull"
        @click="exitFullScreen"
        class="bk-icon icon-un-full-screen"
        style="right: 20px"
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
              <span class="problem-line">[{{item.lineNumber}}, {{item.column}}]</span>
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
      return process.env.NODE_ENV === 'production' ? `${window.static_url}log/yaml.worker.js` : './yaml.worker.js';
    }
    return process.env.NODE_ENV === 'production'
      ? `${window.static_url}log/editor.worker.js`
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
  },
  data() {
    return {
      editor: null,
      renderWidth: '100%',
      renderHeight: 500,
      problemList: [],
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
    // this.setWaringMarker();
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
          fontSize: 16,
          fontFamily: 'Microsoft YaHei',
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
      // this.editor.onDidChangeModel(event => this.$emit('model', event))
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
     */
    setWaringMarker() {
      const markers = [];
      markers.push({
        startLineNumber: 8,
        endLineNumber: 8,
        startColumn: 1,
        endColumn: 12,
        message: 'sdsadsad',
        severity: monaco.MarkerSeverity.Warning,
      });
      monaco.editor.setModelMarkers(this.editor.getModel(), 'owner', markers);
    },
    /**
     * @desc: 警告bottom点击鼠标事件
     */
    handelClickProblemBtn(lineNumber, column) {
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

  &:hover {
    color: #fff;
    background: #424242;
  }
}

.editor {
  overflow: hidden;
}

.problems-drag {
  position: absolute;
  width: 25px;
  height: 6px;
  display: flex;
  align-items: center;
  justify-items: center;
  border-radius: 3px;
  top: 6px;
  transform: translateY(-50%);
  left: 50%;
  z-index: 100;

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
