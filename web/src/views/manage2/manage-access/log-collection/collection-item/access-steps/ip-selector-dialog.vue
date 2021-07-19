<template>
  <bk-dialog
    width="1100"
    header-position="left"
    ext-cls="king-dialog-ip-selector"
    :title="$t('retrieve.select_target')"
    :position="{ top: dialogTop }"
    :auto-close="false"
    :value="showDialog"
    @value-change="handleValueChange"
    @confirm="handleConfirm">
    <div class="ip-select-dialog-content">
      <TopoSelector
        v-if="showDialog"
        ref="topoSelector"
        height="100%"
        :preview-width="230"
        :target-node-type="targetNodeType"
        :target-object-type="targetObjectType"
        :checked-data="targetNodes"
        @check-change="handleChecked" />
    </div>
  </bk-dialog>
</template>

<script>
import TopoSelector from '@/components/ip-selector/business/topo-selector-new.vue';

export default {
  components: {
    TopoSelector,
  },
  props: {
    showDialog: {
      type: Boolean,
      default: false,
    },
    targetObjectType: {
      type: String,
      default: 'HOST',
    },
    targetNodeType: {
      type: String,
      default: 'TOPO',
    },
    targetNodes: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    const top = (window.innerHeight - 675) / 2;
    const dialogTop = top < 70 ? 70 : top;
    return {
      dialogTop,
    };
  },
  methods: {
    handleChecked() {
      // const { type, data = [] } = checkedData
      // console.log('handleChecked', type, data)
    },
    handleValueChange(val) {
      this.$emit('update:showDialog', val);
    },
    handleConfirm() {
      const params = this.getParams();
      this.$emit('target-change', params);
    },
    getParams() {
      const { type, data } = this.$refs.topoSelector.getCheckedData();
      return {
        target_node_type: type,
        target_nodes: data,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
    .ip-select-dialog-content {
      height: 560px;
    }
</style>

<style lang="scss">
  .king-dialog-ip-selector.bk-dialog-wrapper {
    .bk-dialog-header {
      padding-bottom: 10px;
    }

    .bk-dialog-body {
      padding-bottom: 0;
    }

    .bk-dialog-footer {
      border: none;
      background-color: #fff;
    }
  }
</style>
