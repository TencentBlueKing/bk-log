<template>
  <div class="filter-bar">
    <span>{{ $t('configDetails.filterContent') }}</span>
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
      :placeholder="$t('retrieve.filterPlaceholder')"
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
    <span>{{ $t('retrieve.ignoreCase') }}</span>
    <div class="filter-bar" v-if="filterType === 'include'" style="margin-left: 20px">
      <span>{{ $t('retrieve.showPrev') }}</span>
      <bk-tag-input
        style="width: 74px;margin-right: 10px"
        v-model="interval.prev"
        placeholder="请输入"
        :list="lineList"
        :max-data="1"
        :allow-create="false">
      </bk-tag-input>
      <span style="margin-right: 20px">{{ $t('行') }}</span>
      <span>{{ $t('retrieve.showNext') }}</span>
      <bk-tag-input
        style="width: 74px;margin-right: 10px"
        v-model="interval.next"
        placeholder="请输入"
        :list="lineList"
        :max-data="1"
        :allow-create="false">
      </bk-tag-input>
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
        { id: 'include', name: this.$t('retrieve.include') },
        { id: 'uninclude', name: this.$t('retrieve.uninclude') },
      ],
      interval: {
        prev: [0],
        next: [0],
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
  created() {
    this.lineList = Array.from({ length: 101 }, (v, k) => ({
      id: k,
      name: k.toString(),
    }));
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
