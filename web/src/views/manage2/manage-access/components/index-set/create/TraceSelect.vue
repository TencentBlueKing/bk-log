<template>
  <bk-select style="width: 520px;" searchable :clearable="false" :value="selectedId" @selected="handleSelected">
    <template v-for="item in collectionList">
      <bk-option
        :key="item.result_table_id"
        :id="item.result_table_id"
        :name="item.result_table_name_alias">
      </bk-option>
    </template>
  </bk-select>
</template>

<script>
import { mapState } from 'vuex';

export default {
  props: {
    value: {
      type: Array,
      required: true,
    },
  },
  data() {
    const scenarioId = this.$route.name.split('-')[0];
    return {
      scenarioId,
      selectedId: '',
      collectionList: [],
    };
  },
  computed: {
    ...mapState(['projectId', 'bkBizId']),
  },
  watch: {
    value: {
      handler(val) {
        const item = val[0];
        if (item && (item.result_table_id !== this.selectedId)) {
          this.selectedId = item.result_table_id;
        }
      },
      immediate: true,
    },
  },
  created() {
    this.fetchCollectionList();
  },
  methods: {
    // 获取下拉列表
    async fetchCollectionList() {
      try {
        this.basicLoading = true;
        const res = await this.$http.request('/resultTables/list', {
          query: {
            scenario_id: this.scenarioId,
            bk_biz_id: this.bkBizId,
          },
        });
        this.collectionList = res.data.map((item) => {
          item.bk_biz_id = this.bkBizId;
          return item;
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    handleSelected(id) {
      this.selectedId = id;
      this.$emit('update:value', [this.collectionList.find(item => item.result_table_id === id)]);
    },
  },
};
</script>
