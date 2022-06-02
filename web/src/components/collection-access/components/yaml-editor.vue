<template>
  <div class="yaml-container">
    <monaco-editor
      v-model="editorValue"
      :language="language">
      <div class="load" slot="right">
        <span class="bk-icon icon-upload-cloud"></span>
        <span class="bk-icon icon-download"></span>
      </div>
    </monaco-editor>
  </div>
</template>
<script>
import { setDiagnosticsOptions } from 'monaco-yaml';
import monacoEditor from './monaco-editor';

export default {
  components: {
    monacoEditor,
  },
  props: {},
  data() {
    return {
      language: 'yaml',
      editor: null,
      editorValue:
        'username: {{ username }}\n'
        + 'sad',
    };
  },
  watch: {

  },
  mounted() {
    setDiagnosticsOptions({
      validate: true,
      enableSchemaRequest: true,
      format: true,
      hover: true,
      completion: true,
    });
  },
  methods: {

  },
};
</script>
<style lang="scss" scoped>
  .yaml-container {
    width: 74%;
    min-width: 800px;
    margin-left: 115px;
  }

  .load {
    display: flex;
    align-items: center;
  }

  .icon-upload-cloud {
    font-size: 20px;
    margin-right: 20px;
  }

  .icon-download {
    margin-right: 20px;
  }
</style>
