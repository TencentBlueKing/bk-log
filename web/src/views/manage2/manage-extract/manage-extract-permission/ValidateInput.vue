<template>
  <div class="validate-input">
    <bk-input
      :value="value"
      :class="isError && 'is-error'"
      @change="handleChange"
      @blur="handleBlur"
      :placeholder="placeholder"
    ></bk-input>
  </div>
</template>

<script>
export default {
  model: {
    event: 'change',
  },
  props: {
    value: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    validator: {
      type: Function,
      default: val => Boolean(val),
    },
  },
  data() {
    return {
      isError: false,
    };
  },
  created() {
    this.handleBlur(this.value);
  },
  methods: {
    handleChange(val) {
      this.$emit('change', val);
    },
    handleBlur(val) {
      this.isError = !this.validator(val);
    },
  },
};
</script>
