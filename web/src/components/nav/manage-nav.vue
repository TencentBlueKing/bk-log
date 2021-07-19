<template>
  <div class="sub-nav-container">
    <div class="back-container" v-if="$route.meta.needBack" @click="$router.back()">
      <span class="bk-icon icon-arrows-left"></span>
    </div>
    <div class="main-title">{{ $route.meta.needBack ? getTitleName() : activeManageNav.name }}</div>
    <ul class="sub-nav-list" v-if="activeManageNav.children && !$route.meta.needBack">
      <template v-for="navItem in activeManageNav.children">
        <li :class="{ 'sub-nav-item': true, 'active': navItem.id === activeManageSubNav.id }"
            :key="navItem.id" @click="handleClickSubNav(navItem.id)">
          {{ navItem.name }}
        </li>
      </template>
    </ul>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  props: {
    name: {
      type: String,
      default: '',
    },
    subNavList: {
      type: Array,
      default: null,
    },
  },
  computed: {
    ...mapState(['activeManageNav', 'activeManageSubNav']),
  },
  methods: {
    handleClickSubNav(id) {
      if (this.activeManageSubNav.id !== id) {
        this.$router.push({
          name: id,
          query: {
            projectId: window.localStorage.getItem('project_id'),
          },
        });
      }
    },
    // 根据路由名获取菜单名称
    getTitleName() {
      const collectionName = this.$store.state.collect.curCollect?.collector_config_name;
      const map = {
        collectAdd: this.$t('新建采集项'),
        collectEdit: collectionName,
        collectField: collectionName,
        collectStart: collectionName,
        collectStop: collectionName,
        'manage-collection': collectionName,
        'log-index-set-create': this.$t('新建索引集'),
        'log-index-set-edit': this.$t('编辑索引集'),
        'log-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'bkdata-index-set-create': this.$t('新建索引集'),
        'bkdata-index-set-edit': this.$t('编辑索引集'),
        'bkdata-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'es-index-set-create': this.$t('新建索引集'),
        'es-index-set-edit': this.$t('编辑索引集'),
        'es-index-set-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'bkdata-track-create': this.$t('新建索引集'),
        'bkdata-track-edit': this.$t('编辑索引集'),
        'bkdata-track-manage': this.$store.state.collect.curIndexSet?.index_set_name,
        'extract-link-create': this.$t('新建') + this.$t('提取链路'),
        'extract-link-edit': this.$t('编辑') + this.$t('提取链路'),
      };
      return map[this.$route.name];
    },
  },
};
</script>

<style lang="scss" scoped>
  .sub-nav-container {
    display: flex;
    align-items: center;
    height: 52px;
    padding: 0 20px;
    line-height: 24px;
    background-color: #FFF;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.10);
    position: relative;
    z-index: 1;
    .main-title {
      font-size: 16px;
      color: #313238;
    }
    .back-container {
      .icon-arrows-left {
        font-size: 30px;
        color: #3A84FF;
        cursor: pointer;
        &:hover {
          color: #699df4;
        }
      }
    }
    .sub-nav-list {
      display: flex;
      font-size: 14px;
      color: #63656E;
      margin-left: 35px;
      .sub-nav-item {
        height: 52px;
        line-height: 52px;
        padding: 0 10px;
        margin: 0 25px;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: color, border-color .3s;
        &:hover, &.active {
          color: #3A84FF;
          border-bottom: 3px solid #3A84FF;
          transition: color, border-color .3s;
        }
      }
    }
  }
</style>
