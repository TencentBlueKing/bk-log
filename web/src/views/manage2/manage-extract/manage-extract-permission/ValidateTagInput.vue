<template>
  <div class="validate-tag-input">
    <bk-tag-input
      :value="value"
      :class="isError && 'is-error'"
      :list="list"
      :placeholder="placeholder"
      :allow-create="allowCreate"
      :has-delete-icon="true"
      :save-key="'username'"
      :search-key="'username'"
      :display-key="'displayname'"
      :paste-fn="pasteFn"
      @change="handleChange"
      @blur="handleBlur"
    ></bk-tag-input>
  </div>
</template>

<script>
export default {
  model: {
    event: 'change',
  },
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    list: {
      type: Array,
      default: () => [],
    },
    allowCreate: {
      type: Boolean,
      required: true,
    },
    placeholder: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isError: false,
    };
  },
  created() {
    this.validateInitValue();
  },
  methods: {
    validateInitValue() {
      if (this.value.length) {
        if (this.allowCreate) {
          // 可以自定义用户情况下有用户就正确
          this.isError = false;
        } else {
          // 有用户存在于人员列表中，才算是通过校验
          for (const user of this.value) {
            if (this.list.find(item => item.username === user)) {
              this.isError = false;
              return;
            }
          }
          // 虽然有用户，但是用户不存在人员列表中，用户无效
          this.isError = true;
          this.$emit('change', []);
        }
      } else {
        this.isError = true;
      }
    },
    handleChange(val) {
      this.isError = !val.length;
      this.$emit('change', val);
    },
    handleBlur(input, tags) {
      this.isError = !tags.length;
    },
    pasteFn(val) {
      const users = [...this.value];
      val.split(';').forEach((item) => {
        item = item.trim();
        if (item) {
          if (this.allowCreate) {
            if (item.match(/^[0-9]*$/) && !users.includes(item)) {
              users.push(item);
            }
          } else {
            this.list.forEach((user) => {
              if ((user.displayname === item || user.username === item) && !users.includes(user.username)) {
                users.push(user.username);
              }
            });
          }
        }
      });
      this.$emit('change', users);
      return [];
    },
  },
};
</script>

<style lang="scss" scoped>
  .validate-tag-input /deep/ .is-error .bk-tag-input {
    border-color: #ff5656;
  }
</style>
