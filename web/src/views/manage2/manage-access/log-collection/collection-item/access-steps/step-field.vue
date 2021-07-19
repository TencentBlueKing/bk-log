<template>
  <div class="step-field" v-bkloading="{ isLoading: basicLoading }">
    <div class="step-field-title">{{$t('btn.Field')}}
      <bk-switcher size="small" theme="primary" class="ml10" v-model="switcher" @change="switcherHandle"></bk-switcher>
    </div>
    <div class="tips">{{$t('dataManage.field_hint')}}</div>
    <template v-if="switcher">
      <div class="text-nav">
        {{$t('configDetails.originalLog')}}
        <div>
          <span @click="refreshClick">{{$t('dataManage.Refresh')}}</span>
          <span @click="chickFile">{{$t('configDetails.report')}}</span>
        </div>
      </div>
      <div class="log-style">
        <bk-input
          placeholder=" "
          :type="'textarea'"
          :rows="3"
          :input-style="{
            'background-color': '#313238',
            height: '82px',
            'line-height': '24px',
            color: '#C4C6CC',
            borderRadius: '2px'
          }"
          v-model.trim="logOriginal">
        </bk-input>
      </div>
      <bk-sideslider
        class="locker-style"
        :is-show.sync="defaultSettings.isShow"
        :quick-close="true"
        :modal="false"
        :width="596">
        <div slot="header">
          {{$t('configDetails.logDetails')}}<span @click="copyText(JSON.stringify(jsonText))">{{$t('btn.copy')}}</span>
        </div>
        <div class="p20 json-text-style" slot="content">
          <VueJsonPretty :deep="5" :data="jsonText" />
        </div>
      </bk-sideslider>
    </template>

    <section class="field-method" v-if="switcher">
      <div class="field-method-head">
        <h4 class="field-method-title fl field-text">{{ $t('dataManage.Field_extraction') }}</h4>
        <div class="fr form-item-flex bk-form-item">
          <label class="bk-label has-desc" v-bk-tooltips="$t('dataManage.confirm_append')">
            <span>{{ $t('dataManage.keep_log') }}</span>
          </label>
          <div class="bk-form-content">
            <bk-switcher size="small" theme="primary" v-model="formData.etl_params.retain_original_text"></bk-switcher>
          </div>
        </div>
      </div>
      <div :class="['field-method-cause clearfix', { mb10: params.etl_config === 'bk_log_regexp' }]">
        <bk-select
          class="fl"
          style="width: 130px; margin-right: 10px;"
          v-model="params.etl_config"
          :disabled="isExtracting"
          :clearable="false">
          <!-- @selected="methodHandle"> -->
          <bk-option
            v-for="option in globalsData.etl_config"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
        <bk-select
          style="float: left; width: 320px; margin-right: 10px;"
          v-if="params.etl_config === 'bk_log_delimiter'"
          :disabled="isExtracting"
          :clearable="false"
          v-model="params.etl_params.separator">
          <!-- @selected="separatorHandler"> -->
          <bk-option
            v-for="option in globalsData.data_delimiter"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
        <bk-button
          v-if="showDebugBtn"
          class="fl debug-btn"
          theme="primary"
          :disabled="!logOriginal || isExtracting"
          @click="debugHandler">
          {{ $t('dataManage.Commissioning_setup') }}
        </bk-button>
        <p class="format-error ml10 fl" v-if="isJsonOrOperator && !formatResult">{{ $t('dataManage.try_methods') }}</p>
        <template v-if="params.etl_config === 'bk_log_regexp'">
          <span
            v-bk-tooltips="{ allowHtml: true, placement: 'right', content: '#reg-tip' }"
            style="margin-top: 8px; color: #979ba5; cursor: pointer;"
            class="log-icon icon-info-fill fl"></span>
          <div id="reg-tip">
            <p>{{$t('dataManage.regular_format1')}}</p>
            <p>{{$t('dataManage.regular_format2')}}</p>
            <p>{{$t('dataManage.regular_format3')}}</p>
          </div>
        </template>
      </div>
      <div class="field-method-regex" v-if="params.etl_config === 'bk_log_regexp'">
        <div class="textarea-wrapper">
          <pre class="mimic-textarea">
                        {{ params.etl_params.separator_regexp }}
                    </pre>
          <bk-input
            class="regex-textarea"
            :placeholder="defaultRegex"
            :type="'textarea'"
            v-model="params.etl_params.separator_regexp">
          </bk-input>
        </div>
        <bk-button
          theme="primary"
          class="debug-btn regex-btn"
          :disabled="!logOriginal || !params.etl_params.separator_regexp || isExtracting"
          @click="debugHandler">
          {{ $t('dataManage.Commissioning_setup') }}
        </bk-button>
        <p class="format-error" v-if="!formatResult">{{ $t('dataManage.try_methods') }}</p>
      </div>
      <template v-if="isJsonOrOperator && hasFormat && !isExtracting">
        <div class="field-method-head">
          <h4 class="field-method-title fl">{{ $t('dataManage.Settings_Preview') }}</h4>
        </div>
        <div class="field-method-result">
          <field-table
            ref="fieldTable"
            :is-edit-json="isUnmodifiable"
            :extract-method="formData.etl_config"
            :deleted-visible="deletedVisible"
            :fields="formData.fields"
            @deleteVisible="visibleHandle"
            @standard="dialogVisible = true"
            @reset="getDetail">
          </field-table>
        </div>
      </template>
      <template v-if="params.etl_config === 'bk_log_regexp' && hasFormat && !isExtracting">
        <div class="field-method-head">
          <h4 class="field-method-title fl">{{ $t('dataManage.Settings_Preview') }}</h4>
        </div>
        <div class="field-method-result">
          <field-table
            ref="fieldTable"
            :extract-method="formData.etl_config"
            :deleted-visible="deletedVisible"
            :fields="formData.fields"
            @standard="dialogVisible = true"
            @reset="getDetail">
          </field-table>
        </div>
      </template>

      <div class="loading-block" v-if="isExtracting">
        <div style="height: 100%;" v-bkloading="{ isLoading: isExtracting }"></div>
      </div>
    </section>
    <div class="step-field-title">{{ $t('dataManage.storage') }}</div>
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
          required
          class="form-inline-div"
          :rules="rules.table_id"
          :property="'table_id'">
          <div class="prefix">{{formData.table_id_prefix}}</div>
          <bk-input
            style="width: 232px"
            :placeholder="$t('dataManage.input_number')"
            :disabled="isUnmodifiable"
            v-model="formData.table_id"
            maxlength="50" minlength="5">
          </bk-input>
        </bk-form-item>
        <div class="tips">{{ $t('dataManage.start_bk') }}</div>
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
        <bk-button
          theme="default"
          :title="$t('btn.cancel')"
          class="ml10"
          @click="handleBack"
          :disabled="isLoading">
          {{$t('dataManage.Return_list')}}
        </bk-button>
      </bk-form-item>
    </bk-form>
    <bk-dialog
      v-model="dialogVisible"
      width="1012"
      :header-position="'left'"
      :mask-close="false"
      :draggable="false"
      :show-footer="false"
      :title="$t('dataManage.View_fields')">
      <div class="standard-field-table">
        <field-table
          v-if="dialogVisible"
          :table-type="'preview'"
          :extract-method="formData.etl_config"
          :fields="copyBuiltField"
          :json-text="copysText">
        </field-table>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
import { mapGetters, mapState } from 'vuex';
import fieldTable from './field-table';
import { projectManages } from '@/common/util';

export default {
  components: {
    fieldTable,
  },
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
      defaultRegex: '(?P<request_ip>[\d\.]+)[^[]+\[(?P<request_time>[^]]+)\]',
      isLoading: false,
      basicLoading: true,
      isUnmodifiable: false,
      switcher: false,
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
    switcher(val) {
      this.formData.fields = val ? this.formData.fields : [];
    },
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
    debugHandler() {
      this.requestEtlPreview();
    },
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
      if (this.switcher && !this.params.etl_config) {
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
        if (this.switcher) { // 只有当字段提取打开的时候才提醒
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
                this.switcher = etl_config ? etl_config !== 'bk_log_text' : false
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
    //  原始日志刷新
    refreshClick() {
      if (this.refresh) {
        this.getDataLog('init');
      }
    },
    copyText(data) {
      const createInput = document.createElement('input');
      createInput.value = data;
      document.body.appendChild(createInput);
      createInput.select(); // 选择对象
      document.execCommand('Copy'); // 执行浏览器复制命令
      createInput.style.display = 'none';
      const h = this.$createElement;
      this.$bkMessage({
        message: h('p', {
          style: {
            textAlign: 'center',
          },
        }, this.$t('retrieve.copySuccess')),
        offsetY: 80,
      });
    },
    requestEtlPreview(type) {
      const { etl_config, etl_params } = this.params;
      /* eslint-disable */
                if (!this.logOriginal || !etl_config || etl_config === 'bk_log_text') return
                if (etl_config === 'bk_log_regexp' && !etl_params.separator_regexp) return
                if (etl_config === 'bk_log_delimiter' && !etl_params.separator) return
                const newFields = this.$refs.fieldTable ? this.$refs.fieldTable.getData() : [] // 不能取原fileds，因字段修改后的信息保留在table组件里
                this.isExtracting = type === 'init' ? !type : true
                const etlParams = {}
                if (etl_config === 'bk_log_delimiter') {
                    etlParams.separator = etl_params.separator
                }
                if (etl_config === 'bk_log_regexp') {
                    etlParams.separator_regexp = etl_params.separator_regexp
                }
                /* eslint-enable */
      this.$http.request('collect/getEtlPreview', {
        params: {
          collector_config_id: this.curCollect.collector_config_id,
        },
        data: {
          etl_config,
          etl_params: etlParams,
          data: this.logOriginal,
        },
      }).then((res) => {
        // 以下为整个页面关键逻辑
        /**
                     * 只有点击调试按钮，并且成功了，才会改变原有的fields列表，否则只是结果失败，不做任何操作
                     */
        // value 用于展示右边的预览值 - 编辑进入时需要触发预览
        if (res.data && res.data.fields) {
          const dataFields = res.data.fields;
          dataFields.forEach((item) => {
            item.verdict = this.judgeNumber(item);
          });
          const fields = this.formData.fields;

          /* eslint-disable */
                        if (!type) { // 只有点击了调试按钮，才能修改fields列表  // 原始日志更新值改边预览值
                            if (!this.formData.etl_config || this.formData.etl_config !== etl_config || !newFields.length) { // 如果没有提取方式 || 提取方式发生变化 || 不存在任何字段
                                const list = dataFields.reduce((arr, item) => {
                                    const field = Object.assign({}, JSON.parse(JSON.stringify(this.rowTemplate)), item)
                                    arr.push(field)
                                    return arr
                                }, [])
                                this.formData.fields.splice(0, fields.length, ...list)
                            } else { // 否则 - 将对table已修改值-> newFields进行操作
                                if (etl_config === 'bk_log_json' || etl_config === 'bk_log_regexp') {
                                    const list = dataFields.reduce((arr, item) => {
                                        const child = newFields.find(field => {
                                            // return  !field.is_built_in && (field.field_name === item.field_name || field.alias_name === item.field_name)
                                            return !field.is_built_in && field.field_name === item.field_name
                                        })
                                        item = child ? Object.assign({}, child, item) : Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item)
                                        arr.push(item)
                                        return arr
                                    }, [])
                                    if (etl_config === 'bk_log_json') { // json方式下已删除操作的需要拿出来合并到新的field列表里
                                        const deletedFileds = newFields.reduce((arr, field) => {
                                            if (field.is_delete && !dataFields.find(item => item.field_name === field.field_name)) {
                                                arr.push(field)
                                            }
                                            return arr
                                        }, [])
                                        list.splice(list.length, 0, ...deletedFileds)
                                    }
                                    this.formData.fields.splice(0, fields.length, ...list)
                                }

                                if (etl_config === 'bk_log_delimiter') { // 分隔符逻辑较特殊，需要单独拎出来
                                    let index
                                    newFields.forEach((item, idx) => { // 找到最后一个field_name不为空的下标
                                        if (item.field_name && !item.is_delete) {
                                            index = idx + 1
                                        }
                                    })
                                    const list = []
                                    const deletedFileds = newFields.filter(item => item.is_delete)
                                    list.splice(list.length, 0, ...deletedFileds) // 将已删除的字段存进数组
                                    if (index) {
                                        newFields.forEach((item, idx) => { // 找到最后一个field_name不为空的下标
                                            const child = dataFields.find(data => data.field_index === item.field_index)
                                            item.value = child ? child.value : '' // 修改value值(预览值)
                                            if (index > idx && !item.is_delete) { // 将未删除的存进数组
                                                list.push(item)
                                            }
                                        })
                                        dataFields.forEach(item => { // 新增的字段需要存进数组
                                            const child = list.find(field => field.field_index === item.field_index)
                                            if (!child) {
                                                list.push(Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item))
                                            }
                                        })
                                    } else {
                                        dataFields.reduce((arr, item) => {
                                            const field = Object.assign(JSON.parse(JSON.stringify(this.rowTemplate)), item)
                                            arr.push(field)
                                            return arr
                                        }, list)
                                    }
                                    list.sort((a, b) => a.field_index - b.field_index) // 按 field_index 大小进行排序

                                    this.formData.fields.splice(0, fields.length, ...list)
                                }
                            }
                            this.formatResult = true // 此时才能将结果设置为成功
                            this.savaFormData()

                        } else { // 仅做预览赋值操作，不改变结果
                            newFields.forEach(field => {
                                const child = dataFields.find(item => {
                                    if (etl_config === 'bk_log_json') {
                                        return field.field_name === item.field_name
                                        // return  field.field_name === item.field_name || field.alias_name === item.field_name // 同上
                                    } else {
                                        return etl_config === 'bk_log_delimiter' ? (field.field_index === item.field_index) : field.field_name === item.field_name
                                    }
                                })
                                if (!field.is_built_in) {
                                    field.value = child ? child.value : ''
                                }
                            })
                            this.formData.fields.splice(0, fields.length, ...newFields)
                        }
                        /* eslint-enable */
        } else {
          this.formatResult = false;
        }
      })
        .catch(() => {
          if (!type) { // 原始日志内容修改不引发结果变更
            this.formatResult = false;
          }
        })
        .finally(() => {
          this.isExtracting = false;
        });
    },
    savaFormData() {
      this.formData.etl_config = this.params.etl_config;
      Object.assign(this.formData.etl_params, this.params.etl_params);
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
    visibleHandle(val) {
      this.deletedVisible = val;
    },
    judgeNumber(val) {
      const { value } = val;
      if (value === 0) return false;

      return (value && value !== ' ') ? isNaN(value) : true;
    },
  },
};
</script>
<style lang="scss">
  @import '../../../../../../scss/mixins/clearfix';

  .step-field {
    position: relative;
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .step-field-title {
      width: 100%;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
      padding-top: 50px;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }

    .bk-switcher-small {
      width: 36px;
      height: 20px;

      &::after {
        width: 16px;
        height: 16px;
      }

      &.is-checked:after {
        margin-left: -18px;
      }
    }

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

    .text-nav {
      margin: 20px 0 10px 0;
      display: flex;
      justify-content: space-between;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;

      div {
        display: inline-block;
        font-size: 12px;
        color: #3a84ff;
        font-weight: normal;

        span {
          margin-left: 10px;
          cursor: pointer;
        }
      }
    }

    .field-method {
      position: relative;
      margin: 20px 0 0 0;

      .preview-panel-left {
        width: 621px;
      }

      .loading-block {
        position: absolute;
        top: calc(100% + 20px);
        left: 0;
        width: 100%;
        height: 40px;
      }
    }

    .field-method-head {
      margin: 0 0 10px 0;

      @include clearfix;

      .field-method-link {
        margin-top: 1px;
      }
    }

    .field-method-title {
      margin: 0;
      line-height: 20px;
      font-size: 14px;
      font-weight: normal;
      color: #7a7c85;
    }

    .field-text {
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
    }

    .field-method-link {
      font-size: 12px;
      color: #3a84ff;
      cursor: pointer;
    }
    // .field-method-result {
    //     margin-top: 45px;
    //     // & > div{
    //     //     min-height: 257px;
    //     //     border: 1px solid #DCDEE5;
    //     // }
    // }
    .field-method-cause {
      margin-bottom: 20px;

      @include clearfix;
    }

    .debug-btn {
      min-width: 120px;
      background: #fff;
      color: #3a84ff;

      &:hover {
        color: #fff;
      }
    }

    .field-method-regex {
      position: relative;
      margin-bottom: 20px;
      padding-right: 130px;
      width: 100%;

      .regex-btn {
        position: absolute;
        top: 0;
        right: 0;
      }
    }

    .textarea-wrapper {
      width: 100%;
      position: relative;
    }

    .mimic-textarea {
      margin: 0;
      padding: 6px 10px;
      width: 100%;
      line-height: 1.5;
      min-height: 72px;
      font-size: 12px;
      color: transparent;
      outline: none;
      white-space: pre-wrap;
    }

    .regex-textarea {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;

      .bk-textarea-wrapper {
        height: 100%;
      }

      textarea {
        height: 100%;
        overflow: hidden;
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

    .form-item-flex {
      display: flex;

      .bk-label {
        line-height: 20px;
        width: auto;
        padding: 0;
        font-size: 12px;
        color: #63656e;

        &.has-desc > span {
          border-bottom: 1px dashed #d8d8d8;
          cursor: pointer;
        }
      }

      .bk-form-content {
        flex: 1;
        margin: 0 0 0 10px;
        font-size: 0;
      }
    }

    .visible-deleted-text {
      font-size: 12px;
      color: #63656e;
    }
    // .visible-deleted-btn {
    //     vertical-align: top;
    // }
    .format-error {
      margin-top: 8px;
      font-size: 12px;
      color: #ea3636;
    }

    .log-style {
      height: 82px;

      /*background-color: #313238;*/
      .bk-form-textarea:focus {
        background-color: #313238 !important;
        border-radius: 2px;
      }

      .bk-textarea-wrapper {
        border: none;
      }
    }
  }

  .standard-field-table {
    width: 965px;
    padding-bottom: 14px;
    max-height: 464px;
    overflow-x: hidden;
    overflow-y: auto;

    .preview-panel-left {
      width: 615px;
    }

    .preview-panel-right {
      width: 350px;
    }
  }

  .json-text-style {
    background-color: #313238;
    color: #c4c6cc;
  }
</style>
