<template>
  <div class="step-storage">
    <bk-form :label-width="115" :model="formData" ref="validateForm">
      <bk-form-item
        :label="$t('dataSource.storage_cluster_name')"
        required
        property="storage_cluster_id"
        :rules="rules.cluster_id">
        <bk-select
          style="width: 320px;"
          v-model="formData.storage_cluster_id"
          :disabled="isUnmodifiable"
          :clearable="false"
          @selected="handleSelectStorageCluster">
          <bk-option
            v-for="(item, index) in storageList"
            class="custom-no-padding-option"
            :id="item.storage_cluster_id"
            :name="item.storage_cluster_name"
            :disabled="isItsm && curCollect.can_use_independent_es_cluster && item.registered_system === '_default'"
            :key="index">
            <div
              v-if="!(item.permission && item.permission.manage_es_source)"
              class="option-slot-container no-authority"
              @click.stop>
              <span class="text">{{item.storage_cluster_name}}</span>
              <span class="apply-text" @click="applySearchAccess(item)">{{$t('申请权限')}}</span>
            </div>
            <div v-else class="option-slot-container">
              <span v-bk-tooltips="{
                content: $t('容量评估需要使用独立的ES集群'),
                placement: 'right',
                disabled: !(isItsm &&
                  curCollect.can_use_independent_es_cluster &&
                  item.registered_system === '_default')
              }">{{ item.storage_cluster_name }}</span>
            </div>
          </bk-option>
        </bk-select>
        <div class="tips_storage" v-if="formData.storage_cluster_id">
          <!-- eslint-disable-next-line vue/camelcase -->
          <div v-for="(tip, index) in tip_storage" :key="index">{{index + 1}}. {{tip}}</div>
          <!--eslint-enable-->
        </div>
      </bk-form-item>
      <div class="form-div mt">
        <bk-form-item
          :label="$t('configDetails.storageIndexName')"
          class="form-inline-div"
          :rules="rules.table_id"
          :property="'table_id'">
          <!-- <div class="prefix">{{formData.table_id_prefix}}</div> -->
          <bk-input
            style="width: 320px"
            :placeholder="$t('dataManage.input_number')"
            :disabled="isUnmodifiable"
            v-model="formData.table_id"
            maxlength="50" minlength="5">
            <template slot="prepend">
              <div class="group-text">{{formData.table_id_prefix}}</div>
            </template>
          </bk-input>
        </bk-form-item>
        <!-- <div class="tips">{{ $t('dataManage.start_bk') }}</div> -->
      </div>
      <!-- 过期时间 -->
      <bk-form-item :label="$t('configDetails.expirationTime')">
        <bk-select style="width: 320px;" v-model="formData.retention" :clearable="false">
          <div slot="trigger" class="bk-select-name">
            {{ formData.retention + $t('天') }}
          </div>
          <template v-for="(option, index) in retentionDaysList">
            <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
          </template>
          <div slot="extension" style="padding: 8px 0;">
            <bk-input
              v-model="customRetentionDay"
              size="small"
              type="number"
              :placeholder="$t('输入自定义天数')"
              :show-controls="false"
              @enter="enterCustomDay($event, 'retention')"
            ></bk-input>
          </div>
        </bk-select>
      </bk-form-item>
      <!-- 热数据\冷热集群存储期限 -->
      <bk-form-item :label="$t('热数据')" class="hot-data-form-item">
        <bk-select
          style="width: 320px;"
          v-model="formData.allocation_min_days"
          :clearable="false"
          :disabled="!selectedStorageCluster.enable_hot_warm">
          <template v-for="(option, index) in hotDataDaysList">
            <bk-option :key="index" :id="option.id" :name="option.name"></bk-option>
          </template>
          <div slot="extension" style="padding: 8px 0;">
            <bk-input
              v-model="customHotDataDay"
              size="small"
              type="number"
              :placeholder="$t('输入自定义天数')"
              :show-controls="false"
              @enter="enterCustomDay($event, 'hot')"
            ></bk-input>
          </div>
        </bk-select>
        <span v-if="!selectedStorageCluster.enable_hot_warm" class="disable-tips">
          {{$t('该集群未开启热数据设置')}}
          <a href="javascript:void(0);" @click="jumpToEsAccess">{{$t('前往ES源进行设置')}}</a>
        </span>
      </bk-form-item>
      <bk-form-item
        v-if="accessUserManage"
        :label="$t('indexSetList.jurisdiction')"
        required
        :property="'view_roles'"
        :rules="rules.view_roles"
        style="width: 435px;">
        <bk-select
          style="width: 320px;"
          v-model="formData.view_roles"
          searchable
          multiple
          :placeholder="$t('btn.select')"
          show-select-all>
          <bk-option
            v-for="(role, index) in roleList"
            :key="index"
            :id="role.group_id"
            :name="role.group_name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item>
        <bk-button
          theme="default"
          :title="$t('dataManage.last')"
          class="mr10"
          :disabled="isLoading"
          @click="prevHandler">
          {{$t('dataManage.last')}}
        </bk-button>
        <bk-button
          theme="primary"
          @click.stop.prevent="finish"
          :loading="isLoading"
          :disabled="!collectProject">
          {{$t('dataManage.perform')}}
        </bk-button>
        <!-- <bk-button
          theme="default"
          :title="$t('btn.cancel')"
          class="ml10"
          @click="handleBack"
          :disabled="isLoading">
          {{$t('dataManage.Return_list')}}
        </bk-button> -->
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { projectManages } from '@/common/util';

export default {
  props: {
    operateType: String,
    curStep: {
      type: Number,
      default: 1,
    },
    collectorId: String,
  },
  data() {
    return {
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      refresh: false,
      // eslint-disable-next-line no-useless-escape
      isLoading: false,
      basicLoading: true,
      isUnmodifiable: false,
      // switcher: false,
      roleList: [],
      defaultRetention: '',
      fieldType: '',
      deletedVisible: true,
      copysText: {},
      jsonText: {},
      defaultSettings: {
        isShow: false,
      },
      logOriginal: '',
      params: { // 此处为可以变动的数据，如果调试成功，则将此条件保存至formData，保存时还需要对比此处与formData是否有差异
        etl_config: 'bk_log_text',
        etl_params: {
          separator_regexp: '',
          separator: '',
        },
      },
      formData: { // 最后一次正确的结果，保存以此数据为准
        table_id: '',
        etl_config: 'bk_log_text',
        etl_params: {
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
          // separator_field_list: ''
        },
        fields: [],
        view_roles: [],
        retention: '',
        allocation_min_days: '0',
        storage_cluster_id: '',
      },
      selectedStorageCluster: {}, // 选择的es集群
      retentionDaysList: [], // 过期天数列表
      customRetentionDay: '', // 自定义过期天数
      hotDataDaysList: [], // 冷热集群存储期限列表
      customHotDataDay: '', // 自定义冷热集群存储期限天数
      copyBuiltField: [],
      formatResult: true, // 验证结果是否通过
      rules: {
        table_id: [{
          required: true,
          trigger: 'blur',
        }, {
          max: 50,
          trigger: 'blur',
        }, {
          min: 5,
          trigger: 'blur',
        }, {
          regex: /^[A-Za-z0-9_]+$/,
          trigger: 'blur',
        }],
        cluster_id: [{
          validator(val) {
            return val !== '';
          },
          trigger: 'change',
        }],
        view_roles: [{
          validator(val) {
            return val.length >= 1;
          },
          trigger: 'change',
        }],
      },
      storage_capacity: '',
      tips_storage: [],
      tip_storage: [],
      storageList: [],
      isExtracting: false,
      dialogVisible: false,
      rowTemplate: {
        alias_name: '',
        description: '',
        field_type: '',
        is_analyzed: false,
        is_built_in: false,
        is_delete: false,
        is_dimension: false,
        is_time: false,
        value: '',
        option: {
          time_format: '',
          time_zone: '',
        },
      },
      activePanel: 'base',
      panels: [
        { name: 'base', label: this.$t('dataManage.Base') },
        { name: 'advance', label: this.$t('dataManage.Advance') },
      ],
      selectTemplate: '', // 应用模板
      saveTempName: '',
      templateList: [], // 模板列表
      templateDialogVisible: false,
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
      projectId: 'projectId',
      curCollect: 'collect/curCollect',
      globalsData: 'globals/globalsData',
      accessUserManage: 'accessUserManage',
    }),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    isJsonOrOperator() {
      return this.params.etl_config === 'bk_log_json' || this.params.etl_config === 'bk_log_delimiter';
    },
    hasFormat() { // 最后一次正确的fileds结果
      return this.formData.fields.length;
    },
    showDebugBtn() {
      const methods = this.params.etl_config;
      if (!methods || methods === 'bk_log_text' || methods === 'bk_log_regexp') return false;
      if (methods === 'bk_log_delimiter') {
        return this.params.etl_params.separator;
      }
      return true;
    },
    collectProject() {
      return projectManages(this.$store.state.topMenu, 'collection-item');
    },
  },
  watch: {
    'formData.storage_cluster_id'(val) {
      this.storageList.forEach((res) => {
        const arr = [];
        if (res.storage_cluster_id === val) {
          this.selectedStorageCluster = res; // 当前选择的存储集群
          this.updateDaysList();
          this.$nextTick(() => { // 如果开启了冷热集群天数不能为0
            if (res.enable_hot_warm && this.formData.allocation_min_days === '0') {
              this.formData.allocation_min_days = '7';
            }
          });

          this.storage_capacity = JSON.parse(JSON.stringify(res.storage_capacity));
          this.tips_storage = [
            `${this.$t('dataSource.tips_capacity')} ${this.storage_capacity} G，${this.$t('dataSource.tips_development')}`,
            this.$t('dataSource.tips_business'),
            this.$t('dataSource.tips_formula'),
          ];
          if (res.storage_capacity === 0) {
            arr.push(this.tips_storage[2]);
          } else {
            if (res.storage_used > res.storage_capacity) {
              arr.push(this.tips_storage[1]);
              arr.push(this.tips_storage[2]);
            } else {
              arr.push(this.tips_storage[0]);
              arr.push(this.tips_storage[2]);
            }
          }
          this.tip_storage = arr;
        }
      });
    },
    // 冷热数据天数需小于过期时间
    'formData.allocation_min_days'(val) {
      const max = this.formData.retention;
      if (Number(val) > Number(max)) {
        this.$nextTick(() => {
          this.formData.allocation_min_days = max;
        });
      }
    },
  },
  async mounted() {
    this.getStorage();
    this.defaultRetention = this.globalsData.storage_duration_time.filter(item => item.default === true)[0].id;
    this.getDataLog('init');
  },
  methods: {
    // 获取存储集群
    getStorage() {
      const queryData = { bk_biz_id: this.bkBizId };
      if (this.curCollect.data_link_id) {
        queryData.data_link_id = this.curCollect.data_link_id;
      }
      this.$http.request('collect/getStorage', {
        query: queryData,
      }).then((res) => {
        if (res.data) {
          // 根据权限排序
          const s1 = [];
          const s2 = [];
          for (const item of res.data) {
            if (item.permission?.manage_es_source) {
              s1.push(item);
            } else {
              s2.push(item);
            }
          }
          this.storageList = s1.concat(s2);
          if (this.isItsm && this.curCollect.can_use_independent_es_cluster) {
            // itsm 开启时，且可以使用独立集群的时候，默认集群 _default 被禁用选择
          } else {
            const defaultItem = this.storageList.find(item => item.registered_system === '_default');
            if (defaultItem && defaultItem?.permission?.manage_es_source) {
              this.formData.storage_cluster_id = defaultItem.storage_cluster_id;
            }
          }
          this.getDetail();
        }
      })
        .catch((res) => {
          this.$bkMessage({
            theme: 'error',
            message: res.message,
          });
        });
    },
    // 存储集群管理权限
    async applySearchAccess(item) {
      this.$el.click(); // 因为下拉在loading上面所以需要关闭下拉
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('getApplyData', {
          action_ids: ['manage_es_source'],
          resources: [{
            type: 'es_source',
            id: item.storage_cluster_id,
          }],
        });
        window.open(res.data.apply_url);
      } catch (err) {
        console.warn(err);
      } finally {
        this.basicLoading = false;
      }
    },
    // 选择存储集群
    handleSelectStorageCluster() {
      // 因为有最大天数限制，不同集群限制可能不同，所以切换集群时重置
      this.formData.retention = '7';
      this.formData.allocation_min_days = '0';
    },
    updateDaysList() {
      const retentionDaysList = [...this.globalsData.storage_duration_time].filter((item) => {
        return item.id <= (this.selectedStorageCluster.max_retention || 30);
      });
      this.retentionDaysList = retentionDaysList;
      this.hotDataDaysList = [...retentionDaysList];
    },
    // 字段提取
    fieldCollection() {
      const {
        etl_config,
        table_id,
        storage_cluster_id,
        retention,
        allocation_min_days,
        view_roles,
        fields,
        etl_params,
      } = this.formData;
      this.isLoading = true;
      const data = {
        etl_config,
        table_id,
        storage_cluster_id,
        retention: Number(retention),
        allocation_min_days: Number(allocation_min_days),
        view_roles,
        etl_params: {
          retain_original_text: etl_params.retain_original_text,
          separator_regexp: etl_params.separator_regexp,
          separator: etl_params.separator,
        },
        fields,
      };
      /* eslint-disable */
                if (etl_config !== 'bk_log_text') {
                    const etlParams = {
                        retain_original_text: etl_params.retain_original_text
                    }
                    if (etl_config === 'bk_log_delimiter') {
                        etlParams.separator = etl_params.separator
                    }
                    if (etl_config === 'bk_log_regexp') {
                        etlParams.separator_regexp = etl_params.separator_regexp
                    }
                    data.etl_params = etlParams
                    data.fields = this.$refs.fieldTable.getData()
                }
                /* eslint-enable */
      this.isLoading = true;
      this.$http.request('collect/fieldCollection', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
        data,
      }).then((res) => {
        if (res.code === 0) {
          // this.storageList = res.data
          // this.formData.storage_cluster_id = this.storageList[0].storage_cluster_id
          this.isLoading = false;
          if (res.data) {
            this.$store.commit('collect/updateCurCollect', Object.assign({}, this.formData, data, res.data));
            this.$emit('changeIndexSetId', res.data.index_set_id || '');
          }
          this.$emit('stepChange');
        }
      })
        .finally(() => {
          this.isLoading = false;
        });
    },
    // 输入自定义过期天数、冷热集群存储期限
    enterCustomDay(val, type) {
      const numberVal = parseInt(val.trim(), 10);
      const stringVal = numberVal.toString();
      const isRetention = type === 'retention'; // 过期时间 or 热数据存储时间
      if (numberVal) {
        const maxDays = this.selectedStorageCluster.max_retention || 30;
        if (numberVal > maxDays) { // 超过最大天数
          isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
          this.messageError(this.$t('最大自定义天数为') + maxDays);
        } else {
          if (isRetention) {
            if (!this.retentionDaysList.some(item => item.id === stringVal)) {
              this.retentionDaysList.push({
                id: stringVal,
                name: stringVal + this.$t('天'),
              });
            }
            this.formData.retention = stringVal;
            this.customRetentionDay = '';
          } else {
            if (!this.hotDataDaysList.some(item => item.id === stringVal)) {
              this.hotDataDaysList.push({
                id: stringVal,
                name: stringVal + this.$t('天'),
              });
            }
            this.formData.allocation_min_days = stringVal;
            this.customHotDataDay = '';
          }
          document.body.click();
        }
      } else {
        isRetention ? this.customRetentionDay = '' : this.customHotDataDay = '';
        this.messageError(this.$t('请输入有效数值'));
      }
    },
    // 跳转到 es 源
    jumpToEsAccess() {
      window.open(this.$router.resolve({
        name: 'es-collection',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      }).href, '_blank');
    },
    // 完成按钮
    finish() {
      if (!this.params.etl_config) {
        this.$bkMessage({
          theme: 'error',
          message: this.$t('dataManage.select_field'),
        });
      }
      const promises = [this.checkStore()];
      if (this.formData.etl_config !== 'bk_log_text') {
        promises.splice(1, 0, ...this.checkFieldsTable());
      }
      Promise.all(promises).then(() => {
        // 非bk_log_text类型需要有正确的结果
        if (this.formData.etl_config && this.formData.etl_config !== 'bk_log_text' && !this.hasFormat) return;
        let isConfigChange = false; // 提取方法或条件是否已变更
        const etlConfigParam = this.params.etl_config;
        if (etlConfigParam !== 'bk_log_text') {
          const etlConfigForm = this.formData.etl_config;
          if (etlConfigParam !== etlConfigForm) {
            isConfigChange = true;
          } else {
            const etlParams = this.params.etl_params;
            const etlParamsForm = this.formData.etl_params;
            if (etlConfigParam === 'bk_log_regexp') {
              isConfigChange = etlParams.separator_regexp !== etlParamsForm.separator_regexp;
            }
            if (etlConfigParam === 'bk_log_delimiter') {
              isConfigChange = etlParams.separator !== etlParamsForm.separator;
            }
          }
        }
        if (isConfigChange) {
          const h = this.$createElement;
          this.$bkInfo({
            type: 'warning',
            title: this.$t('dataManage.Submit'),
            subHeader: h('p', {
              style: {
                whiteSpace: 'normal',
              },
            }, this.$t('dataManage.Debug_set')),
            confirmFn: () => {
              this.fieldCollection();
            },
          });
          return;
        }
        this.fieldCollection();
      }, (validator) => {
        console.warn('保存失败', validator);
      });
    },
    // 字段表格校验
    checkFieldsTable() {
      return this.formData.etl_config !== 'bk_log_text' ? this.$refs.fieldTable.validateFieldTable() : [];
    },
    // 存储校验
    checkStore() {
      return new Promise((resolve, reject) => {
        if (!this.isUnmodifiable) {
          this.$refs.validateForm.validate().then((validator) => {
            resolve(validator);
          })
            .catch((err) => {
              console.warn('存储校验错误');
              reject(err);
            });
        } else {
          resolve();
        }
      });
    },
    // 返回列表
    handleBack() {
      this.$router.push({
        name: 'collection-item',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    prevHandler() {
      this.$emit('stepChange', 1);
    },
    // 获取详情
    getDetail() {
      const tsStorageId = this.formData.storage_cluster_id;
      const {
        table_id,
        storage_cluster_id,
        retention,
        allocation_min_days,
        table_id_prefix,
        view_roles,
        etl_config,
        etl_params,
        fields,
      } = this.curCollect;
      const option = { time_zone: '', time_format: '' };
      const copyFields = fields ? JSON.parse(JSON.stringify(fields)) : [];
      copyFields.forEach((row) => {
        row.value = '';
        if (row.is_delete) {
          const copyRow = Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), JSON.parse(JSON.stringify(row)));
          Object.assign(row, copyRow);
        }
        if (row.option) {
          row.option = Object.assign({}, option, row.option || {});
        } else {
          row.option = Object.assign({}, option);
        }
      });
      /* eslint-disable */
      this.params.etl_config = etl_config
      Object.assign(this.params.etl_params, {
          separator_regexp: etl_params.separator_regexp || '',
          separator: etl_params.separator || ''
      })
      this.isUnmodifiable = !!(table_id || storage_cluster_id)
      this.fieldType = etl_config || 'bk_log_text'
      // this.switcher = etl_config ? etl_config !== 'bk_log_text' : false
      /* eslint-enable */
      Object.assign(this.formData, {
        table_id,
        storage_cluster_id,
        table_id_prefix,
        etl_config: this.fieldType,
        etl_params: Object.assign({
          retain_original_text: true,
          separator_regexp: '',
          separator: '',
          // separator_field_list: ''
                    }, etl_params ? JSON.parse(JSON.stringify(etl_params)) : {}), // eslint-disable-line
        fields: copyFields.filter(item => !item.is_built_in),
        retention: retention ? `${retention}` : this.defaultRetention,
        // eslint-disable-next-line camelcase
        allocation_min_days: allocation_min_days ? `${allocation_min_days}` : '0',
        view_roles,
      });
      if (!this.copyBuiltField.length) {
        this.copyBuiltField = copyFields.filter(item => item.is_built_in);
      }
      if (this.curCollect.etl_config && this.curCollect.etl_config !== 'bk_log_text') {
        this.formatResult = true;
      }
      this.formData.storage_cluster_id = this.formData.storage_cluster_id === null
        ? tsStorageId : this.formData.storage_cluster_id;
    },
    chickFile() {
      this.defaultSettings.isShow = true;
    },
    switcherHandle(value) {
      if (value) {
        this.formData.etl_config = this.fieldType ? (this.fieldType === 'bk_log_text' ? '' : this.fieldType) : '';
        this.params.etl_config = this.formData.etl_config;
      } else {
        this.fieldType = this.formData.etl_config;
        this.formData.etl_config = 'bk_log_text';
        this.params.etl_config = 'bk_log_text';
      }
    },
    requestEtlPreview() {
    },
    //  获取采样状态
    getDataLog(isInit) {
      this.refresh = false;
      this.basicLoading = true;
      this.$http.request('source/dataList', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
      }).then((res) => {
        if (res.data && res.data.length) {
          this.copysText = res.data[0].etl || {};
          const data = res.data[0];
          this.jsonText = data.origin || {};
          this.logOriginal = data.etl.data || '';
          if (this.logOriginal) {
            this.requestEtlPreview(isInit);
          }
          this.copyBuiltField.forEach((item) => {
            const fieldName = item.field_name;
            if (fieldName) {
              // eslint-disable-next-line no-prototype-builtins
              if (item.hasOwnProperty('value')) {
                item.value = this.copysText[fieldName];
              } else {
                this.$set(item, 'value', this.copysText[fieldName]);
              }
            }
          });
        }
      })
        .catch(() => {
        })
        .finally(() => {
          this.basicLoading = false;
          this.refresh = true;
        });
    },
  },
};
</script>
<style lang="scss">
  @import '@/scss/mixins/clearfix';

  .step-storage {
    margin-top: 30px;
    position: relative;
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
    }

    .tips_storage {
      width: 540px;
      background-color: rgb(239, 248, 255);
      border: 1px solid deepskyblue;
      font-size: 12px;
      padding: 10px;
      margin-top: 15px;

      div {
        line-height: 24px;
        color: #63656e;
      }
    }

    .form-div {
      display: flex;
      margin: 20px 0;

      .form-inline-div {
        white-space: nowrap;

        .bk-form-content {
          display: flex;
          flex-wrap: nowrap;
        }
      }

      .prefix {
        font-size: 14px;
        line-height: 32px;
        color: #858790;
        margin-right: 8px;
        min-width: 80px;
        text-align: right;
      }
    }

    .hot-data-form-item {
      .bk-form-content {
        display: flex;
        align-items: center;

        .disable-tips {
          margin-left: 10px;
          font-size: 12px;
          color: #63656e;

          a {
            color: #3a84ff;
          }
        }
      }
    }
  }
</style>
