<template>
  <div class="filter-bar">
    <span>{{ $t('过滤内容') }}</span>
    <bk-select
      style="width: 100px;"
      v-model="filterType"
      :clearable="false"
      @change="handleFilterType">
      <bk-option
        v-for="(option, index) in filterTypeList"
        :key="index"
        :id="option.id"
        :name="option.name">
      </bk-option>
    </bk-select>
    <bk-input
      :style="{ width: isScreenFull ? '500px' : '260px', margin: '0 10px' }"
      :clearable="true"
      :right-icon="'bk-icon icon-search'"
      :placeholder="$t('输入关键字进行过滤')"
      v-model="filterKey"
      @enter="filterLog"
      @clear="filterLog"
      @blur="filterLog"
    ></bk-input>
    <bk-checkbox
      style="margin-right: 4px"
      :true-value="true"
      :false-value="false"
      v-model="ignoreCase">
    </bk-checkbox>
    <span>{{ $t('大小写敏感') }}</span>
    <div
      class="filter-bar"
      v-if="filterType === 'include'"
      style="margin-left: 20px">
      <span>{{ $t('显示前') }}</span>
      <bk-input
        style="width: 74px;margin-right: 10px"
        v-model="interval.prev"
        type="number"
        :show-controls="false"
        :max="100"
        :min="0"
        placeholder="请输入">
      </bk-input>
      <span style="margin-right: 20px">{{ $t('行') }}</span>
      <span>{{ $t('显示后') }}</span>
      <bk-input
        style="width: 74px;margin-right: 10px"
        v-model="interval.next"
        type="number"
        :show-controls="false"
        :max="100"
        :min="0"
        placeholder="请输入">
      </bk-input>
      <span>{{ $t('行') }}</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isScreenFull: Boolean,
  },
  data() {
    return {
      filterType: 'include',
      filterKey: '',
      ignoreCase: false,
      filterTypeList: [
        { id: 'include', name: this.$t('包含') },
        { id: 'uninclude', name: this.$t('不包含') },
      ],
      interval: {
        prev: 0,
        next: 0,
      },
    };
  },
  watch: {
    ignoreCase(val) {
      this.$emit('handle-filter', 'ignoreCase', val);
    },
    interval: {
      deep: true,
      handler(val) {
        this.$emit('handle-filter', 'interval', val);
      },
    },
  },
  methods: {
    filterLog() {
      this.$emit('handle-filter', 'filterKey', this.filterKey);
    },
    handleFilterType(val) {
      this.$emit('handle-filter', 'filterType', val);
    },
  },
};
</script>

<style lang="scss" scoped>
  .filter-bar {
    display: flex;
    align-items: center;

    span {
      margin-right: 10px;
      color: #2d3542;
    }

    .hot-key {
      color: #979ba5;
    }
  }
</style>
