<template>
  <div class="add-collection-container">
    <bk-alert v-if="guideUrl" class="king-alert" type="info" closable>
      <div slot="title" class="slot-title-container">
        {{ $t('接入前请查看') }}
        <a class="link" target="_blank" :href="guideUrl"> {{ $t('接入指引') }}</a>
        {{ $t('，尤其是在日志量大的情况下请务必提前沟通。') }}
      </div>
    </bk-alert>
    <bk-form :label-width="115" :model="formData" ref="validateForm">
      <!-- 基础信息 -->
      <div class="add-collection-title">{{ $t('dataSource.basic_information') }}</div>
      <bk-form-item
        :label="$t('dataSource.source_name')"
        :required="true"
        :rules="rules.collector_config_name"
        :property="'collector_config_name'">
        <bk-input v-model="formData.collector_config_name" maxlength="50"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('configDetails.remarkExplain')">
        <bk-input type="textarea" style="width: 320px;" v-model="formData.description" maxlength="100"></bk-input>
      </bk-form-item>

      <!-- 源日志信息 -->
      <div class="add-collection-title">{{ $t('dataSource.Source_log_information') }}</div>
      <!-- 日志类型 -->
      <bk-form-item :label="$t('configDetails.logType')" required>
        <div class="bk-button-group log-type">
          <bk-button
            v-for="(item, index) in globalsData.collector_scenario"
            :key="index"
            :disabled="isUpdate"
            :class="{
              'disable': !item.is_active,
              'is-selected': item.id === formData.collector_scenario_id,
              'is-updated': isUpdate && item.id === formData.collector_scenario_id
            }"
            @click="chooseLogType(item)"
          >{{ item.name }}
          </bk-button>
        </div>
      </bk-form-item>
      <!-- 数据分类 -->
      <bk-form-item
        :label="$t('configDetails.dataClassify')"
        required
        :rules="rules.category_id"
        :property="'category_id'">
        <bk-select
          style="width: 320px;"
          v-model="formData.category_id"
          :disabled="isUpdate"
          @selected="chooseDataClass">
          <template v-for="(item, index) in globalsData.category">
            <bk-option-group :id="item.id" :name="item.name" :key="index">
              <bk-option
                v-for="(option, key) in item.children"
                :key="key"
                :id="option.id"
                :name="`${item.name}-${option.name}`"> {{ option.name }}
              </bk-option>
            </bk-option-group>
          </template>
        </bk-select>
      </bk-form-item>
      <!-- 采集目标 -->
      <div class="form-div mt">
        <bk-form-item
          :label="$t('configDetails.target')"
          class="item-target"
          required
          :rules="rules.nodes"
          :property="'target_nodes'" ref="formItemTarget">
          <bk-button
            theme="default"
            :title="$t('configDetails.newly_increased')"
            icon="plus"
            style="font-size: 12px"
            :class="colorRules ? 'rulesColor' : ''"
            :disabled="!formData.category_id"
            @click="showIpSelectorDialog = true">
            {{ $t('retrieve.select_target') }}
          </bk-button>
          <input type="text" :value="formData.target_nodes" style="display: none">
        </bk-form-item>
        <div class="count" v-if="formData.target_nodes.length">
          <span>{{ collectTargetTarget[formData.target_node_type + '1'] }}</span>
          <span class="font-blue">{{ formData.target_nodes.length }}</span>
          <span>{{ collectTargetTarget[formData.target_node_type + '2'] }}</span>
        </div>
        <ip-selector-dialog
          :show-dialog.sync="showIpSelectorDialog"
          :target-object-type="formData.target_object_type"
          :target-node-type="formData.target_node_type"
          :target-nodes="formData.target_nodes"
          @target-change="targetChange">
        </ip-selector-dialog>
      </div>
      <!-- 日志路径 -->
      <div class="form-div mt" v-for="(log, index) in logPaths" :key="index">
        <bk-form-item
          :label="index === 0 ? $t('retrieve.logPath') : ''" required
          :rules="rules.paths"
          :property="'params.paths.' + index + '.value'">
          <bk-input v-model="log.value"></bk-input>
        </bk-form-item>
        <div class="ml9">
          <i class="bk-icon icon-plus-circle icons" @click="addLog"></i>
          <i
            :class="['bk-icon icon-minus-circle icons ml9', { disable: logPaths.length === 1 }] "
            @click="delLog(index)"></i>
        </div>
        <div class="tips" v-if="index === 0">
          {{ $t('retrieve.log_available') }}<span class="font-gray">{{ $t('retrieve.log_wildcard_character') }}</span>
        </div>
      </div>
      <!-- 日志字符集 -->
      <bk-form-item :label="$t('configDetails.logSet')" required>
        <bk-select style="width: 320px;" searchable v-model="formData.data_encoding" :clearable="false">
          <bk-option
            v-for="(option, ind) in globalsData.data_encoding"
            :key="ind"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <!-- 段日志正则调试 -->
      <div v-if="hasMultilineReg" class="multiline-log-container">
        <div class="row-container">
          <bk-form-item :label="$t('行首正则')" :rules="rules.notEmptyForm" required property="params.multiline_pattern">
            <bk-input v-model.trim="formData.params.multiline_pattern"></bk-input>
          </bk-form-item>
          <bk-button text size="small" class="king-button" @click="showRegDialog = true">{{ $t('调试') }}</bk-button>
        </div>
        <div class="row-container second">
          {{ $t('最多匹配') }}
          <bk-form-item :rules="rules.maxLine" property="params.multiline_max_lines">
            <bk-input
              v-model="formData.params.multiline_max_lines"
              type="number"
              :precision="0"
              :show-controls="false">
            </bk-input>
          </bk-form-item>
          {{ $t('行，最大耗时') }}
          <bk-form-item :rules="rules.maxTimeout" property="params.multiline_timeout">
            <bk-input
              v-model="formData.params.multiline_timeout"
              type="number"
              :precision="0"
              :show-controls="false">
            </bk-input>
          </bk-form-item>
          {{ $t('秒') }}
        </div>
        <multiline-reg-dialog
          :old-pattern.sync="formData.params.multiline_pattern"
          :show-dialog.sync="showRegDialog">
        </multiline-reg-dialog>
      </div>

      <!-- 日志内容过滤 -->
      <div class="add-collection-title">{{ $t('retrieve.Log_content_filtering') }}</div>
      <div class="hight-setting">
        <div class="tips ml115">{{ $t('retrieve.suggest_clean') }}</div>
        <div class="form-div">
          <bk-form-item :label="$t('configDetails.filterContent')">
            <bk-select
              style="width: 129px; margin-right: 8px;"
              :clearable="false"
              v-model="formData.params.conditions.type"
              @change="chooseType">
              <bk-option id="match" :name="$t('retrieve.String_filtering')"></bk-option>
              <bk-option id="separator" :name="$t('retrieve.Separator_filtering')"></bk-option>
            </bk-select>
          </bk-form-item>
          <bk-input v-show="isString" v-model="formData.params.conditions.match_content"></bk-input>
          <bk-select
            style="width: 254px; margin-left: 8px; height: 32px"
            :clearable="false"
            v-if="isString" v-model="formData.params.conditions.match_type">
            <bk-option id="include" :name="$t('retrieve.Keep_string')"></bk-option>
            <bk-option id="exclude" :name="$t('retrieve.Keep_filtering')" disabled>
              <span v-bk-tooltips.right="$t('正在开发中')">{{ $t('retrieve.Keep_filtering') }}</span>
            </bk-option>
          </bk-select>
          <bk-select
            style="width: 320px; margin-right: 8px; height: 32px"
            v-if="!isString"
            v-model="formData.params.conditions.separator">
            <bk-option
              v-for="(option, index) in globalsData.data_delimiter"
              :key="index"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </div>
        <div class="tips ml115" v-show="!isString">{{ $t('retrieve.Complex_filtering') }}</div>
        <div class="form-div" v-if="!isString">
          <div class="choose-table">
            <div class="choose-table-item choose-table-item-head">
              <div class="left">{{ $t('retrieve.How_columns') }}</div>
              <div class="main">{{ $t('retrieve.equal_to') }}</div>
              <div class="right">{{ $t('retrieve.To_add_delete') }}</div>
            </div>
            <div class="choose-table-item-body">
              <div class="choose-table-item" v-for="(item, index) in separatorFilters" :key="index">
                <div class="left">
                  <bk-form-item
                    label="" :rules="rules.separator_filters" style="width: 100px;"
                    :property="'params.conditions.separator_filters.' + index + '.fieldindex'">
                    <bk-input style="width: 100px;" v-model="item.fieldindex"></bk-input>
                  </bk-form-item>
                </div>
                <div :class="['main', { line: separatorFilters.length > 1 }] ">
                  <bk-form-item
                    label="" :rules="rules.separator_filters"
                    :property="'params.conditions.separator_filters.' + index + '.word'">
                    <bk-input v-model="item.word"></bk-input>
                  </bk-form-item>
                </div>
                <div class="right">
                  <i class="bk-icon icon-plus-circle icons" @click="addItem"></i>
                  <i
                    :class="['bk-icon icon-minus-circle icons ml9', { disable: separatorFilters.length === 1 }] "
                    @click="delItem(index)">
                  </i>
                </div>
              </div>
              <div class="choose-select" v-if="separatorFilters && separatorFilters.length > 1">
                <bk-select class="select-div" v-model="type" @selected="changeType">
                  <bk-option id="and" :name="$t('configDetails.and')"></bk-option>
                  <bk-option id="or" :name="$t('configDetails.or')"></bk-option>
                </bk-select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 上报链路配置 -->
      <template v-if="!isCloseDataLink">
        <div class="add-collection-title">{{ $t('上报链路配置') }}</div>
        <bk-form-item required property="data_link_id" :label="$t('上报链路')" :rules="rules.linkConfig">
          <bk-select style="width: 320px;" v-model="formData.data_link_id" :clearable="false" :disabled="isUpdate">
            <bk-option
              v-for="item in linkConfigurationList"
              :key="item.data_link_id"
              :id="item.data_link_id"
              :name="item.link_group_name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </template>

      <bk-form-item>
        <bk-button
          theme="primary"
          :title="$t('retrieve.Start_collecting')"
          @click.stop.prevent="startCollect"
          :loading="isHandle"
          :disabled="!collectProject">
          {{ $t('retrieve.next') }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t('indexSetList.cancel')"
          class="ml10"
          @click="cancel">
          {{ $t('indexSetList.cancel') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>
<script>
import MultilineRegDialog from './multiline-reg-dialog';
import ipSelectorDialog from './ip-selector-dialog';
import { mapGetters, mapState } from 'vuex';
import { projectManage } from '@/common/util';

export default {
  components: {
    MultilineRegDialog,
    ipSelectorDialog,
  },
  data() {
    return {
      guideUrl: window.COLLECTOR_GUIDE_URL,
      colorRules: false,
      isItsm: window.FEATURE_TOGGLE.collect_itsm === 'on',
      showRegDialog: false, // 显示段日志调试弹窗
      linkConfigurationList: [], // 链路配置列表
      formData: {
        collector_config_name: '', // 采集项名称
        category_id: '', // 数据分类
        collector_scenario_id: 'row',
        data_encoding: 'UTF-8', // 日志字符集
        data_link_id: '', // 链路配置
        description: '', // 备注
        target_object_type: 'HOST', // 目前固定为 HOST
        target_node_type: 'TOPO', // 动态 TOPO 静态 INSTANCE 服务模版 SERVICE_TEMPLATE 集群模板 SET_TEMPLATE
        target_nodes: [], // 采集目标
        params: {
          multiline_pattern: '', // 行首正则, char
          multiline_max_lines: '50', // 最多匹配行数, int
          multiline_timeout: '2', // 最大耗时, int
          paths: [ // 日志路径
            { value: '' },
          ],
          conditions: {
            type: 'match', // 过滤方式类型
            match_type: 'include', // 过滤方式 可选字段 include, exclude
            match_content: '',
            separator: '',
            separator_filters: [ // 分隔符过滤条件
              { fieldindex: '', word: '', op: '=', logic_op: 'and' },
            ],
          },
        },
      },
      rules: {
        notEmptyForm: [ // 不能为空的表单
          {
            required: true,
            trigger: 'blur',
          },
        ],
        maxLine: [ // 最多匹配行数
          {
            validator: (val) => {
              if (val > 1000) {
                this.formData.params.multiline_max_lines = '1000';
              } else if (val < 1) {
                this.formData.params.multiline_max_lines = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
        maxTimeout: [ // 最大耗时
          {
            validator: (val) => {
              if (val > 10) {
                this.formData.params.multiline_timeout = '10';
              } else if (val < 1) {
                this.formData.params.multiline_timeout = '1';
              }
              return true;
            },
            trigger: 'blur',
          },
        ],
        collector_config_name: [ // 采集名称
          {
            required: true,
            trigger: 'blur',
          },
          {
            max: 50,
            trigger: 'blur',
          },
        ],
        category_id: [ // 数据分类
          {
            required: true,
            trigger: 'blur',
          },
        ],
        paths: [ // 日志路径
          {
            required: true,
            trigger: 'change',
          },
        ],
        separator_filters: [ // 分隔符过滤条件
          {
            required: true,
            trigger: 'blur',
          },
        ],
        // 上报链路配置
        linkConfig: [
          {
            required: true,
            trigger: 'blur',
          },
        ],
        nodes: [
          {
            validator: this.checkNodes,
            trigger: 'change',
          },
        ],
      },
      logUrl: [
        { value: '' },
      ],
      chooseList: [
        { fieldindex: '', word: '', op: '=', logic_op: 'and' },
      ],
      type: 'and',
      isUpdate: false,
      isHandle: false,
      globals: {},
      showIpSelectorDialog: false,
      collectTargetTarget: { // 已(动态)选择 静态主机 节点 服务模板 集群模板
        INSTANCE1: this.$t('configDetails.selected'),
        INSTANCE2: this.$t('configDetails.staticHosts'),
        TOPO1: this.$t('configDetails.Dynamic_selection'),
        TOPO2: this.$t('configDetails.Been'),
        SERVICE_TEMPLATE1: this.$t('configDetails.selected'),
        SERVICE_TEMPLATE2: this.$t('configDetails.serviceTemplates'),
        SET_TEMPLATE1: this.$t('configDetails.selected'),
        SET_TEMPLATE2: this.$t('configDetails.setTemplates'),
      },
    };
  },
  computed: {
    ...mapGetters({
      bkBizId: 'bkBizId',
    }),
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters('globals', ['globalsData']),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    // 分隔符字段过滤条件
    separatorFilters() {
      const { params } = this.formData;
      return params.conditions.separator_filters || [{
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      }];
    },
    // 日志路径
    logPaths() {
      const { params } = this.formData;
      return params.paths || [];
    },
    // 是否为字符串过滤
    isString() {
      return this.formData.params.conditions.type === 'match';
    },
    // 是否打开行首正则功能
    hasMultilineReg() {
      return this.formData.collector_scenario_id === 'section';
    },
    collectProject() {
      return projectManage(this.$store.state.topMenu, 'collection-item');
    },
    isCloseDataLink() {
      // 没有可上报的链路时，编辑采集配置链路ID为0或null时，隐藏链路配置框，并且不做空值校验。
      return !this.linkConfigurationList.length || (this.isUpdate && !this.curCollect.data_link_id);
    },
  },
  created() {
    this.getLinkData();
    this.isUpdate = this.$route.name !== 'collectAdd';
    if (this.isUpdate) {
      this.formData = JSON.parse(JSON.stringify(this.curCollect));
      if (this.formData.target?.length) { // IP 选择器预览结果回填
        this.formData.target_nodes = this.formData.target;
      }
      const { params } = this.formData;
      if (params.paths.length > 0) {
        params.paths = typeof params.paths[0] === 'string' ? params.paths.map(item => ({ value: item })) : params.paths;
      } else { // 兼容原日志路径为空列表
        params.paths = [{ value: '' }];
      }
    }
  },
  mounted() {
  },
  methods: {
    async getLinkData() {
      try {
        this.tableLoading = true;
        const res = await this.$http.request('linkConfiguration/getLinkList', {
          query: {
            bk_biz_id: this.$store.state.bkBizId,
          },
        });
        this.linkConfigurationList = res.data.filter(item => item.is_active);
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    // 开始采集
    startCollect() {
      this.$refs.validateForm.validate().then(() => {
        const params = this.handleParams();
        if (this.isCloseDataLink) {
          delete params.data_link_id;
        }
        this.isHandle = true;
        this.setCollection(params);
      }, () => {});
    },
    // 新增/修改采集
    setCollection(params) {
      this.isHandle = true;
      const urlParams = {};
      let requestUrl;
      if (this.isUpdate) {
        urlParams.collector_config_id = Number(this.$route.params.collectorId);
        requestUrl = this.isItsm ? 'collect/onlyUpdateCollection' : 'collect/updateCollection';
      } else {
        requestUrl = this.isItsm ? 'collect/onlyCreateCollection' : 'collect/addCollection';
      }
      const updateData = { params: urlParams, data: params };
      this.$http.request(requestUrl, updateData).then((res) => {
        if (res.code === 0) {
          if (this.isUpdate && this.isItsm) {
            sessionStorage.setItem('collectionUpdateData', JSON.stringify(updateData));
          }
          params.params.paths = params.params.paths.map(item => ({ value: item }));
          this.$store.commit(`collect/${this.isUpdate ? 'updateCurCollect' : 'setCurCollect'}`, Object.assign({}, this.formData, params, res.data));
          this.$emit('stepChange');
          this.setDetail(res.data.collector_config_id);
          this.isHandle = false;
        }
      })
        .finally(() => {
          this.isHandle = false;
        });
    },
    // 处理提交参数
    handleParams() {
      const formData = JSON.parse(JSON.stringify(this.formData));
      const {
        collector_config_name,
        target_object_type,
        target_node_type,
        target_nodes,
        data_encoding,
        data_link_id,
        description,
        params,
      } = formData;
      if (!this.hasMultilineReg) { // 行首正则未开启
        delete params.multiline_pattern;
        delete params.multiline_max_lines;
        delete params.multiline_timeout;
      }
      const { match_type, match_content, separator, separator_filters, type } = params.conditions;
      params.conditions = type === 'match' ? { type, match_type, match_content } : {
        type,
        separator,
        separator_filters,
      };
      params.paths = params.paths.map(item => item.value);
      if (this.isUpdate) { // 编辑
        return {
          collector_config_id: Number(this.$route.params.collectorId),
          collector_config_name,
          target_node_type,
          target_object_type,
          target_nodes,
          data_encoding,
          data_link_id,
          description,
          params,
        };
      }  // 新增
      return Object.assign(formData, {
        data_link_id,
        bk_biz_id: this.bkBizId,
      });
    },
    // 选择日志类型
    chooseLogType(item) {
      if (item.is_active) {
        this.formData.collector_scenario_id = item.id;
      }
    },
    // 选择数据分类
    chooseDataClass() {
      // console.log(val)
      /**
                 * 以下为预留逻辑
                 */
      // 当父类为services时，仅能选取动态类型目标；其他父类型目标为静态类型时，切换为serveices时需要做清空判断操作
      // if (['services', 'module'].includes(val)) {
      //     if (this.formData.target_object_type === 'SERVICE') {
      //         this.formData.target_nodes = []
      //     }
      //     this.formData.target_object_type = 'SERVICE'
      // } else {
      //     this.formData.target_object_type = 'HOST'
      // }
    },
    // 切换选择过滤内容
    chooseType(value) {
      this.isString = value === 'match';
      const conditions = this.formData.params.conditions || {};
      if (!this.isString && conditions.separator_filters.length < 1) {
        Object.assign(conditions, {
          separator_filters: [ // 分隔符过滤条件
            { fieldindex: '', word: '', op: '=', logic_op: this.type },
          ],
        });
      }
    },
    // 修改分隔符过滤的并&或
    changeType(value) {
      this.type = value;
      this.formData.params.conditions.separator_filters.map((item) => {
        item.logic_op = value;
      });
    },
    addLog() {
      this.formData.params.paths.push({ value: '' });
    },
    delLog(index) {
      if (this.formData.params.paths.length > 1) {
        this.formData.params.paths.splice(this.formData.params.paths.findIndex((item, ind) => ind === index), 1);
      }
    },
    addItem() {
      this.formData.params.conditions.separator_filters.push({
        fieldindex: '',
        word: '',
        op: '=',
        logic_op: this.type,
      });
    },
    delItem(index) {
      const { separator_filters } = this.formData.params.conditions;
      if (separator_filters.length > 1) {
        separator_filters.splice(separator_filters.findIndex((item, ind) => index === ind), 1);
      }
    },
    // 取消操作
    cancel() {
      this.$router.push({
        name: 'collection-item',
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    // 采集目标选择内容变更
    targetChange(params) { // bk_biz_id, target_object_type, target_node_type, target_nodes
      // this.formData.target_object_type = params.target_object_type
      this.formData.target_node_type = params.target_node_type;
      this.formData.target_nodes = params.target_nodes;
      this.showIpSelectorDialog = false;
      // 触发 bk-form 的表单验证
      this.$refs.formItemTarget.validate('change');
    },
    checkNodes() {
      this.colorRules = !(this.formData.target_nodes && this.formData.target_nodes.length);
      return this.formData.target_nodes.length;
    },
    // 新增的时候更新详情
    setDetail(id) {
      this.$http.request('collect/details', {
        params: { collector_config_id: id },
      }).then((res) => {
        if (res.data) {
          this.$store.commit('collect/setCurCollect', res.data);
        }
      });
    },
  },
};
</script>
<style lang="scss" scoped>
  .add-collection-container {
    min-width: 950px;
    max-height: 100%;
    padding: 0 42px 42px;
    overflow: auto;

    .king-alert {
      margin: 24px 0 -18px;

      .link {
        color: #3a84ff;
      }
    }

    .add-collection-title {
      width: 100%;
      font-size: 14px;
      font-weight: 600;
      color: #63656e;
      border-bottom: 1px solid #dcdee5;
      padding-top: 38px;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }

    .tips {
      font-size: 12px;
      color: #aeb0b7;
      margin-left: 8px;
      line-height: 32px;
    }

    .hight-setting {
      width: 100%;
      min-height: 60px;
      margin: 20px 0;

      .icons-downs {
        display: inline-block;
        width: 9px;
        height: 5px;
        background: url('../../../../../../images/icons/triangle.png');
        background-size: 100% 100%;
        margin-right: 6px;
        vertical-align: middle;
        margin-top: -3px;
      }

      .icon-left {
        transform: rotate(-90deg);
      }
    }

    .bk-label {
      color: #90929a;
    }

    .bk-form-control {
      width: 320px;
    }

    .multiline-log-container {
      margin: 20px 0;

      .row-container {
        display: flex;
        align-items: center;

        &.second {
          padding-left: 115px;
          margin-top: 10px;
          font-size: 12px;
          color: #63656e;

          /deep/ .bk-form-item {
            margin: 0 !important;

            .bk-form-content {
              margin: 0 !important;

              .bk-form-control {
                width: 64px;
                margin: 0 6px;
              }
            }
          }
        }
      }
    }

    .form-div {
      display: flex;
      margin-bottom: 20px;

      .form-inline-div {
        .bk-form-content {
          display: flex;
        }
      }

      .prefix {
        font-size: 14px;
        line-height: 32px;
        color: #858790;
        margin-right: 8px;
      }

      .count {
        font-size: 12px;
        line-height: 32px;
        color: #7a7c85;
        margin-left: 8px;
      }

      .font-blue {
        color: #4e99ff;
        font-weight: bold;
      }

      .font-gray {
        color: #858790;
      }

      .icons {
        font-size: 21px;
        vertical-align: middle;
        cursor: pointer;
        color: #979ba5;
        line-height: 32px;
      }

      .disable {
        color: #dcdee5;
        cursor: not-allowed;
      }

      .item-target {
        &.is-error .bk-form-content {
          padding-right: 30px;
        }
      }
    }

    .choose-table {
      background: #fff;
      width: 60%;
      height: 100%;
      border: 1px solid #dcdee5;
      margin-left: 115px;
      padding-bottom: 14px;

      .bk-form-content {
        margin-left: 0 !important;
      }

      label {
        width: 0 !important;
      }

      .choose-table-item {
        display: flex;
        height: 32px;
        line-height: 32px;
        padding: 0 20px;
        font-size: 13px;
        color: #858790;
        margin-top: 13px;
        position: relative;

        .left {
          width: 110px;
        }

        .main {
          flex: 1;
          padding-right: 130px;
          position: relative;

          .bk-form-control {
            width: 88%;
          }
        }

        .line {
          .bk-form-control {
            &::before {
              content: '';
              width: 25px;
              height: 1px;
              border-top: 1px dashed #c4c6cc;
              position: absolute;
              left: 100%;
              top: 16px;
            }
          }
        }

        .right {
          width: 60px;
        }
      }

      .choose-table-item-head {
        height: 42px;
        line-height: 42px;
        background: #fafbfd;
        border-bottom: 1px solid #dcdee5;
        margin-top: 0;
      }

      .choose-table-item-body {
        position: relative;
        height: 100%;

        .choose-select {
          height: 100%;
          position: absolute;
          top: 0;
          left: calc(88% - 120px);
          display: flex;
          align-items: center;

          .select-div {
            width: 80px;
          }

          &::before {
            content: '';
            width: 20px;
            height: 1px;
            border-top: 1px dashed #c4c6cc;
            position: absolute;
            right: 80px;
            top: 50%;
          }

          &::after {
            content: '';
            width: 1px;
            height: calc(100% - 32px);
            border-left: 1px dashed #c4c6cc;
            position: absolute;
            right: 100px;
            top: 17px;
          }
        }
      }
    }

    .log-type {
      height: 32px;
      border-radius: 2px;

      .bk-button {
        min-width: 106px;
        font-size: 12px;

        span {
          padding: 0 1px;
        }
      }

      .disable {
        color: #dcdee5;
        cursor: not-allowed;
        border-color: #dcdee5;
      }

      .is-updated {
        background: #fafbfd;
        border-color: #dcdee5;
        color: #63656e;
      }
    }

    .ml {
      margin-left: -115px;
    }

    .mt {
      margin-top: 20px;
    }

    .ml9 {
      margin-left: 8px;
    }

    .ml10 {
      margin-left: 10px;
    }

    .ml115 {
      margin-left: 115px;
    }

    .is-selected {
      z-index: 2 !important;
    }

    .bk-form .bk-form-content .tooltips-icon {
      left: 330px;
    }

    .rulesColor {
      border-color: #ff5656 !important;
    }
  }
</style>
