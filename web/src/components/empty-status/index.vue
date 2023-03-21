<template>
  <div class="empty-status-container">
    <bk-exception :type="emptyType" :scene="scene">
      <div class="empty-text-content">
        <p v-if="showText" class="empty-text">{{ typeText }}</p>
        <template v-if="$slots.default">
          <slot />
        </template>
        <template v-else>
          <i18n class="operation-text" path="可以尝试{0}或{1}" v-if="emptyType === 'search-empty'">
            <span style="margin: 0 3px">{{ $t('调整关键词') }}</span>
            <span
              class="operation-btn"
              style="margin-left: 3px"
              @click="handleOperation('clear-filter')"
            >
              {{ $t('清空筛选条件') }}
            </span>
          </i18n>
          <span
            v-if="emptyType === '500'"
            class="operation-btn"
            @click="handleOperation('refresh')"
          >
            {{ $t('刷新') }}
          </span>
        </template>
      </div>
    </bk-exception>
  </div>
</template>

<script>
export default {
  props: {
    emptyType: {
      type: String,
      default: 'empty',
    },
    scene: {
      type: String,
      default: 'part',
    },
    showOperation: {
      type: Boolean,
      default: true,
    },
    showText: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      defaultTextMap: {
        empty: this.$t('暂无数据'),
        'search-empty': this.$t('搜索结果为空'),
        500: this.$t('数据获取异常'),
        403: this.$t('无业务权限'),
      },
    };
  },
  computed: {
    typeText() {
      return this.defaultTextMap[this.emptyType];
    },
  },
  methods: {
    handleOperation(type) {
      this.$emit('operation', type);
    },
  },
};
</script>

<style lang="scss">
.empty-status-container {
  padding: 20px 0;

  .exception-image {
    height: 180px;
    user-select: none;
    user-select: none;
    user-select: none;
    onselectstart: none
  }

  .empty-text-content {
    margin-top: 20px;
  }

  .empty-text {
    margin: 8px 0;
    font-size: 14px;
    color: #63656e;
    line-height: 22px;
  }

  .operation-text {
    font-size: 12px;
    color: #63656e;
    line-height: 20px;
  }

  .operation-btn {
    color: #3a84ff;
    cursor: pointer;
  }
}
</style>
