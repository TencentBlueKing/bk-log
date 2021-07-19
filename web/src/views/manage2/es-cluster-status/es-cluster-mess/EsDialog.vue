<template>
  <bk-dialog
    :value="value"
    :width="840"
    :title="title"
    :show-footer="false"
    header-position="left"
    @value-change="handleVisibilityChange">
    <div style="padding-bottom: 20px;min-height: 200px;">
      <bk-table v-if="value" :data="filterList" :max-height="320">
        <bk-table-column label="ID" prop="id"></bk-table-column>
        <bk-table-column label="Name" prop="name"></bk-table-column>
        <bk-table-column label="Host" prop="host"></bk-table-column>
      </bk-table>
    </div>
  </bk-dialog>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    list: {
      type: Array,
      default() {
        return [];
      },
    },
    type: {
      type: String,
      default: 'hot',
    },
    formData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      title: '',
    };
  },
  computed: {
    filterList() {
      return this.list.filter((item) => {
        if (this.type === 'hot') {
          return item.attr === this.formData.hot_attr_name && item.value === this.formData.hot_attr_value;
        }
        return item.attr === this.formData.warm_attr_name && item.value === this.formData.warm_attr_value;
      });
    },
  },
  watch: {
    value(val) {
      if (val) {
        const isHot = this.type === 'hot';
        const name = isHot ? this.formData.hot_attr_name : this.formData.warm_attr_name;
        const value = isHot ? this.formData.hot_attr_value : this.formData.warm_attr_value;
        this.title = `${this.$t('包含属性')} ${name}:${value} ${this.$t('的节点列表')}`;
      }
    },
  },
  methods: {
    handleVisibilityChange(val) {
      this.$emit('input', val);
    },
  },
};
</script>
