<!--
  - Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for BK-LOG 蓝鲸日志平台:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <section class="allocation" v-bkloading="{ isLoading: textLoading, opacity: 0.8 }">
    <auth-page v-if="authPageInfo" :info="authPageInfo"></auth-page>
    <div class="label-ground" v-else>
      <bk-tab :active.sync="active" @tab-change="handleTabChange">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
          <div v-if="index === 0" class="deploy">
            <div class="deploy-sub">
              <div><span>{{$t('configDetails.name')}}</span><span>{{ data.collector_config_name || '-'}}</span></div>
              <div>
                <span>{{$t('configDetails.logType')}}</span>
                <span>{{data.collector_scenario_name || '-'}}</span>
              </div>
              <div><span>{{$t('configDetails.dataClassify')}}</span><span>{{data.category_name || '-'}}</span></div>
              <div>
                <span>{{$t('configDetails.logPath')}}</span>
                <div class="deploy-path">
                  <p v-for="(val, key) in data.params.paths" :key="key">{{val}}</p>
                </div>
              </div>
              <div><span>{{$t('configDetails.logSet')}}</span><span>{{data.data_encoding || '-'}}</span></div>
              <div><span>{{$t('configDetails.target')}}</span><span>{{$t('configDetails.selected')}}
                <p class="num-color" @click="active = 'hisitory'">{{data.target_nodes.length || '-'}}</p>
                {{data.target_node_type !== 'INSTANCE' ? $t('configDetails.Been') : $t('configDetails.staticHosts')}}
              </span></div>
              <div>
                <span>{{$t('configDetails.storageIndexName')}}</span>
                <span v-if="data.table_id">
                  {{data.table_id_prefix}}{{data.table_id}}</span>
                <span v-else>-</span>
              </div>
              <div><span>{{$t('configDetails.remarkExplain')}}</span><span>{{data.description || '-'}}</span></div>
              <div
                class="content-style"
                v-if="data.params.conditions.type === 'match' && data.params.conditions.match_content !== ''">
                <span>{{$t('configDetails.filterContent')}}</span>
                <div>
                  <p>{{$t('configDetails.strMatching')}}</p>
                  <p v-if="data.params.conditions.match_content">{{data.params.conditions.match_content}}</p>
                  <p>
                    {{data.params.conditions.match_type}}/{{data.params.conditions.match_type === 'include' ?
                      $t('configDetails.keep') : $t('configDetails.Filter')}}
                  </p>
                </div>
              </div>
              <div
                class="content-style"
                v-else-if="data.params.conditions.type === 'separator' &&
                  data.params.conditions.separator_filters !== []">
                <span>{{$t('configDetails.filterContent')}}</span>
                <div>
                  <p>{{$t('configDetails.sepMatching')}}</p>
                  <p v-if="data.params.conditions.separator">{{data.params.conditions.separator}}</p>
                  <div class="condition-stylex">
                    <div>
                      <div class="the-column">
                        <div
                          v-for="(val, key) in data.params.conditions.separator_filters"
                          :key="key">
                          {{$t('configDetails.the')}} {{val.fieldindex}} {{$t('configDetails.column')}}
                        </div>
                      </div>
                      <div>
                        <div v-for="(val, key) in data.params.conditions.separator_filters" :key="key">
                          <p @mouseenter="handleEnter" @mouseleave="handleLeave">{{val.word}}</p>
                          <div
                            :class="key === 0 ? 'line-styy' : 'line-sty'"
                            v-if="data.params.conditions.separator_filters.length > 1">
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="con-text" v-if="data.params.conditions.separator_filters.length > 1">
                      <div class="line-styx"></div>
                      <p>
                        {{ data.params.conditions.separator_filters[0].logic_op === 'and' ?
                          $t('configDetails.and') : $t('configDetails.or')}}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="content-style" v-else>
                <span>{{$t('configDetails.filterContent')}}</span>
                <div>
                  --
                </div>
              </div>
              <div>
                <span>{{$t('configDetails.StorageCluster')}}</span>
                <span>{{data.storage_cluster_name || '-'}}</span>
              </div>
              <div>
                <span>{{$t('configDetails.storageIndexName')}}</span>
                <span>{{data.table_id_prefix + data.table_id || '-'}}</span>
              </div>
              <div>
                <span>{{$t('configDetails.expirationTime')}}</span>
                <span>{{data.retention || '-'}} {{$t('configDetails.day')}}</span>
              </div>
              <div v-if="accessUserManage">
                <span>{{$t('indexSetList.jurisdiction')}}</span>
                <span v-if="!textLoading">{{data.peo || '-'}}</span>
              </div>
              <p class="button-place">
                <bk-button :theme="'primary'" @click="handleClick" class="mr10">
                  {{$t('btn.edit')}}
                </bk-button>
              </p>
            </div>
            <div class="deploy-name">
              <div v-for="(key, x) in dataCreat" :key="x"><span>{{key.key}}</span><span>{{key.data}}</span></div>
            </div>
          </div>
          <div v-if="index === 1" class="collect">
            <div class="mb15 nav-section">
              <div class="button-group">
                <span
                  v-for="(val, x) in dataButton"
                  :class="clickSec.selected === val.key ? 'button-bul' : 'button-wit'"
                  @click="handleChangeGroup(val)"
                  :key="x">
                  {{val.content}}({{val.dataList.totalLenght}})
                </span>
              </div>
              <div>
                <span>{{$t('configDetails.text')}}</span>
                <bk-button
                  theme="default"
                  :title="$t('configDetails.retry')"
                  icon="refresh"
                  class="mr10"
                  :size="size"
                  @click="retryClick(dataFal, dataFir.contents.length)"
                  :disabled="!collectProject">
                  {{$t('configDetails.batchRetry')}}
                </bk-button>
                <bk-button
                  :theme="'primary'"
                  :title="$t('configDetails.dataSampling')"
                  class="mr10"
                  :size="size"
                  :disabled="!collectProject"
                  @click="jsonFormatClick">
                  {{$t('configDetails.dataSampling')}}
                </bk-button>
              </div>
            </div>
            <div
              v-for="(value, i) in renderTableList"
              :key="i"
              style="margin-bottom: 10px; overflow: hidden"
              ref="unfold">
              <div class="table-detail" @click="closeTable(i)">
                <div>
                  <i
                    class="bk-icon title-icon icon-down-shape"
                    :style="{ 'color': collapseColor }"
                    ref="icon"></i><!--:class="[showSetting ? 'icon-down-shape' : 'icon-right-shape']"-->
                  <span>{{value.node_path}}</span>
                  <span>{{dataSec[i] ? dataSec[i].length : ''}}</span>
                  <span>{{$t('configDetails.successful')}},</span>
                  <span>{{dataFal[i] ? dataFal[i].length : ''}}</span>
                  <span>{{$t('configDetails.failure')}}</span>
                </div>
              </div>
              <div class="table-calc">
                <bk-table
                  :empty-text="$t('btn.vacancy')"
                  :data="clickSec.data[i]"
                  :size="size"
                  v-bkloading="{ isLoading: reloadTable }">
                  <bk-table-column :label="$t('configDetails.goal')" prop="ip"></bk-table-column>
                  <bk-table-column :label="$t('alarmStrategy.active_name')">
                    <template slot-scope="props">
                      <span @click="reset(props.row)">
                        <i
                          class="bk-icon icon-refresh"
                          style="display: inline-block; animation: button-icon-loading 1s linear infinite;"
                          v-if="props.row.status !== 'SUCCESS' && props.row.status !== 'FAILED'"></i>
                        <span
                          v-if="props.row.status === 'SUCCESS'"
                          class="SUCCESS">
                          {{$t('configDetails.success')}}
                        </span>
                        <span
                          v-else-if="props.row.status === 'FAILED'"
                          class="FAILED">
                          {{$t('configDetails.failed')}}
                        </span>
                        <span v-else class="PENDING">{{$t('configDetails.Pending')}}</span>
                      </span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t('configDetails.updated_at')" prop="create_time"></bk-table-column>
                  <bk-table-column :label="$t('configDetails.plug_in')" prop="plugin_version"></bk-table-column>
                  <bk-table-column :label="$t('monitors.detail')">
                    <template slot-scope="props">
                      <span @click="reset(props.row)">
                        <div class="text-style">
                          <span></span>
                          <span @click.stop="viewDetail(props.row)">{{ $t('dataManage.more') }}</span>
                        </div>
                      </span>
                    </template>
                  </bk-table-column>
                  <bk-table-column label="" width="120">
                    <template slot-scope="props">
                      <bk-button
                        theme="primary"
                        text
                        @click="retryClick(props.row, 'odd')"
                        v-if="props.row.status === 'FAILED'">
                        {{$t('configDetails.retry')}}
                      </bk-button>
                    </template>
                  </bk-table-column>
                </bk-table>
              </div>
            </div>
            <template v-if="renderTableList.length">
              <div v-show="!isPageOver && !reloadTable" v-bkloading="{ isLoading: true }" style="height: 40px;"></div>
            </template>
          </div>
        </bk-tab-panel>
      </bk-tab>
    </div>
    <bk-sideslider
      :width="800"
      :quick-close="true"
      :ext-cls="'issued-detail'"
      :is-show.sync="detail.isShow"
      @animation-end="closeSlider">
      <div slot="header">{{ detail.title }}</div>
      <!-- eslint-disable vue/no-v-html -->
      <div
        class="p20 detail-content"
        slot="content"
        v-bkloading="{ isLoading: detail.loading }"
        v-html="detail.content">
      </div>
      <!--eslint-enable-->
    </bk-sideslider>
  </section>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import AuthPage from '@/components/common/auth-page';
import { projectManage } from '@/common/util';

export default {
  name: 'allocation',
  components: { AuthPage },
  data() {
    return {
      authPageInfo: null,
      currentPage: 0,
      isPageOver: false, // 前端分页加载是否结束
      dataListPaged: [], // 将列表数据按 pageSize 分页
      count: 0, // 数据总条数
      pageSize: 30, // 每页展示多少数据
      totalPage: 1,
      renderTableList: [
        {
          is_label: false,
          bk_obj_name: '-',
          node_path: '-',
          bk_obj_id: '-',
          label_name: '',
          child: [],
          bk_inst_id: 6,
          bk_inst_name: '-',
        },
      ],
      detail: {
        isShow: false,
        title: this.$t('monitors.detail'),
        loading: true,
        content: '',
        log: '',
      },
      textLoading: true,
      dataButton: [
        {
          key: 'all',
          content: this.$t('configDetails.all'),
          dataList: {},
        },
        {
          key: 'sec',
          content: this.$t('configDetails.succeed'),
          dataList: {},
        },
        {
          key: 'fal',
          content: this.$t('configDetails.failed'),
          dataList: {},
        },
        {
          key: 'pen',
          content: this.$t('configDetails.Pending'),
          dataList: {},
        },
      ],
      dataCreat: [
        {
          key: this.$t('configDetails.updated_by'),
          value: 'updated_by',
          data: '',
        },
        {
          key: this.$t('configDetails.updated_at'),
          value: 'updated_at',
          data: '',
        },
        {
          key: this.$t('configDetails.created_by'),
          value: 'created_by',
          data: '',
        },
        {
          key: this.$t('configDetails.created_at'),
          value: 'created_at',
          data: '',
        },
      ],
      collapseColor: {
        type: String,
        default: '#63656E',
      },
      showSetting: true,
      config_id: '',
      reloadTable: false,
      instance: null,
      clickSec: {
        selected: 'all',
        data: '',
      },
      retryData: {
        ip: '',
        bk_cloud_id: '',
        bk_supplier_id: '',
      },
      data: {
        collector_scenario_id: '-',
        collector_config_name: '-',
        category_id: '-',
        category_name: '-',
        target_nodes: [],
        data_encoding: '-',
        bk_data_name: '-',
        description: '-',
        params: {
          paths: [],
          conditions: {},
        },
        storage_cluster_id: '-',
        storage_expires: '-',
        created_at: '',
        created_by: '',
        updated_at: '',
        updated_by: '',
        subscription_info: {},
        peo: '',
      },
      panels: [
        { name: 'mission', label: this.$t('configDetails.message'), count: 10 },
        // { name: 'config', label: '日志清洗', count: 20 },
        { name: 'hisitory', label: this.$t('configDetails.gatherState'), count: 30 },
      ],
      active: 'mission',
      groupSetting2: {
        selected: 'all',
      },
      size: 'small',
      dataFir: {
        contents: [
          {
            is_label: false,
            bk_obj_name: '-',
            node_path: '-',
            bk_obj_id: '-',
            label_name: '',
            child: [],
            bk_inst_id: 6,
            bk_inst_name: '-',
          },
        ],
      },
      dataSec: {},
      dataFal: {},
      dataPen: {},
      dataAll: {},
      permissionGroupList: {},
      requestQuene: [], // tab对应内容请求队列
      tabRequestMap: {
        mission: 'getDetailsList', // 获取配置信息
        hisitory: 'getCollectList', // 获取采集状态
      },
    };
  },
  computed: {
    ...mapGetters('collect', ['curCollect']),
    ...mapGetters(['accessUserManage']),
    ...mapState({
      currentProject: state => state.projectId,
    }),
    ...mapState({
      menuProject: state => state.menuProject,
    }),
    collectProject() {
      return projectManage(this.menuProject, 'manage', 'manage');
    },
  },
  watch: {
    currentProject(val) {
      val && this.jumpToHome();
    },
  },
  created() {
    const { hash } = this.$route;
    if (hash && hash === '#hisitory') {
      this.active = 'hisitory';
    }
    this.config_id = this.$route.params.collectorId;
    this.initPage(this.active);
  },
  destroyed() {
    // 清除定时器
    clearInterval(this.timer);
  },
  mounted() {
    this.adadScrollEvent();
  },
  methods: {
    async initPage(active) {
      // 进入路由需要先判断权限
      try {
        const paramData = {
          action_ids: ['view_collection'],
          resources: [{
            type: 'collection',
            id: this.$route.params.collectorId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (res.isAllowed === false) {
          this.authPageInfo = res.data;
          this.textLoading = false;
          return;
        }
      } catch (err) {
        console.warn(err);
        this.textLoading = false;
        return;
      }

      this.requestQuene.push(active);
      this[this.tabRequestMap[active]]();
    },
    closeTable(val) {
      this.$refs.unfold[val].style.height = this.$refs.unfold[val].style.height === '' ? '43px' : '';
      this.$refs.icon[val].classList.value = this.$refs.unfold[val].style.height === '' ? 'bk-icon title-icon icon-down-shape' : 'bk-icon title-icon icon-right-shape';
    },
    handleClick() {
      this.$router.push({
        name: 'collectEdit',
        params: {
          collectorId: this.config_id,
        },
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    jsonFormatClick() {
      this.$router.push({
        name: 'jsonFormat',
        params: {
          collectorId: this.config_id,
        },
        query: {
          projectId: window.localStorage.getItem('project_id'),
        },
      });
    },
    // 判断是否超出  超出提示
    handleEnter(e) {
      const cWidth = e.target.clientWidth;
      const sWidth = e.target.scrollWidth;
      if (sWidth > cWidth) {
        this.instance = this.$bkPopover(e.target, { content: e.path[0].childNodes[0].data, arrow: true, placement: 'right' });
        this.instance.show(1000);
      }
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    // 获取配置信息
    getDetailsList() {
      this.textLoading = true;
      this.$http.request('source/detailsList', {
        params: {
          collector_config_id: this.config_id,
        },
        mock: false,
        manualSchema: true,
      }).then((res) => {
        if (res.data) {
          this.data = res.data;
          this.dataCreat.forEach((item) => {
            item.data = this.data[item.value];
          });
        }
      })
        .finally(() => {
          this.getPermissionGroupList();
        });
    },
    getPermissionGroupList() {
      this.data.peo = '';
      this.textLoading = false;
    },
    adadScrollEvent() {
      this.scrollontentEl = document.querySelector('.allocation');
      if (!this.scrollontentEl) return;

      this.scrollontentEl.addEventListener('scroll', this.handleScroll, { passive: true });
    },
    // 获取采集状态
    getCollectList() {
      this.reloadTable = true;
      this.dataAll = { totalLenght: 0 };
      this.dataSec = { totalLenght: 0 };
      this.dataFal = { totalLenght: 0 };
      this.dataPen = { totalLenght: 0 };
      this.$http.request('source/collectList', {
        params: {
          collector_config_id: this.config_id,
        },
        mock: false,
        manualSchema: true,
      }).then((res) => {
        this.dataFir = res.data;
        if (this.dataFir.contents.length !== 0) {
          // 过滤child为空的节点
          this.dataFir.contents = this.dataFir.contents.filter(data => data.child.length);

          for (let x = 0; x < this.dataFir.contents.length; x++) {
            let allSet = [];
            const secSet = [];
            const failSet = [];
            const penSet = [];
            allSet = this.dataFir.contents[x].child;
            for (let i = 0; i < allSet.length; i++) {
              if (allSet[i].status === 'SUCCESS') {
                secSet.push(allSet[i]);
              } else if (allSet[i].status === 'FAILED') {
                failSet.push(allSet[i]);
              } else {
                penSet.push(allSet[i]);
              }
            }
            this.dataAll[x] = allSet;
            this.dataSec[x] = secSet;
            this.dataFal[x] = failSet;
            this.dataPen[x] = penSet;
            this.dataAll.totalLenght += allSet.length;
            this.dataSec.totalLenght += secSet.length;
            this.dataFal.totalLenght += failSet.length;
            this.dataPen.totalLenght += penSet.length;
            this.reloadTable = false;
          }
          this.dataButton.forEach((item) => {
            item.dataList = item.key === 'pen' ? this.dataPen : item.key === 'sec' ? this.dataSec : item.key === 'fal' ? this.dataFal : this.dataAll;
          });
          const sel = this.clickSec.selected;
          this.clickSec.data = sel === 'pen' ? this.dataPen : sel === 'sec' ? this.dataSec : sel === 'fal' ? this.dataFal : this.dataAll;

          if (!this.timer) {
            this.dataListPaged = [];
            this.dataListShadow = [];
            this.renderTableList = [];
            this.initPageConf(this.dataFir.contents);
            this.loadPage();
          }

          //  如果存在执行中添加定时器
          if (this.dataPen.totalLenght === 0) {
            clearInterval(this.timer);
            this.timer = null;
          } else {
            if (this.timer) {
              return 1;
            }
            this.timer = setInterval(() => {
              this.getCollectList();
            }, 10000);
          }
        }
      })
        .catch(() => {
          this.reloadTable = false;
        })
        .finally(() => {
          this.textLoading = false;
        });
    },
    // 采集状态过滤
    handleChangeGroup(val) {
      this.clickSec.selected = val.key;
      this.clickSec.data = val.dataList;

      // TODO
      this.dataListPaged = [];
      this.dataListShadow = [];
      this.renderTableList = [];
      this.initPageConf(this.dataFir.contents || []);
      this.loadPage();
    },
    // 初始化前端分页
    initPageConf(list) {
      this.currentPage = 0;
      this.isPageOver = false;

      this.count = list.length;
      this.totalPage = Math.ceil(this.count / this.pageSize) || 1;
      this.dataListShadow = list;
      this.dataListPaged = [];
      for (let i = 0; i < this.count; i += this.pageSize) {
        this.dataListPaged.push(this.dataListShadow.slice(i, i + this.pageSize));
      }
    },
    loadPage() {
      this.currentPage += 1;
      this.isPageOver = this.currentPage === this.totalPage;

      if (this.dataListPaged[this.currentPage - 1]) {
        this.renderTableList.splice(this.renderTableList.length, 0, ...this.dataListPaged[this.currentPage - 1]);
        top && this.$nextTick(() => {
          // this.scrollontentEl.scrollTop = top
        });
      }
    },
    handleScroll() {
      if (this.throttle) {
        return;
      }

      this.throttle = true;
      setTimeout(() => {
        this.throttle = false;

        const el = this.scrollontentEl;

        if (this.isPageOver) {
          return;
        }
        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 60) {
          this.loadPage(el.scrollTop);
        }
      }, 200);
    },
    // 重试
    retryClick(val, key) {
      this.reloadTable = true;
      const retryList = [];
      if (key === 'odd') {
        const data = JSON.parse(JSON.stringify(this.retryData));
        data.ip = val.ip;
        data.bk_cloud_id = val.bk_cloud_id;
        data.bk_supplier_id = val.bk_supplier_id;
        retryList.push(data);
      } else {
        if (val.totalLenght === 0) { // 判断是否存在失败项
          this.reloadTable = false;
          return 1;
        }
        for (let y = 0; y < key; y++) {
          for (let i = 0; i < val[y].length; i++) {
            const data = JSON.parse(JSON.stringify(this.retryData));
            data.ip = val[y][i].ip;
            data.bk_cloud_id = val[y][i].bk_cloud_id;
            data.bk_supplier_id = val[y][i].bk_supplier_id;
            retryList.push(data);
          }
        }
      }
      this.$http.request('source/retryList', {
        params: {
          collector_config_id: this.config_id,
        },
        data: {
          node_type: 'INSTANCE',
          target_nodes: retryList,
        },
        mock: false,
        manualSchema: true,
      }).then(() => {
        this.getCollectList();
      })
        .catch(() => {
        });
    },
    viewDetail(row) {
      this.detail.isShow = true;
      this.detail.loading = true;
      this.requestDetail(row);
    },
    requestDetail(row) {
      this.$http.request('collect/executDetails', {
        params: {
          collector_id: this.config_id,
        },
        query: {
          instance_id: row.instance_id,
          task_id: row.task_id,
        },
      }).then((res) => {
        if (res.result) {
          this.detail.log = res.data.log_detail;
          this.detail.content = res.data.log_detail;
        }
      })
        .catch((err) => {
          this.$bkMessage({
            theme: 'error',
            message: err.message || err,
          });
        })
        .finally(() => {
          this.detail.loading = false;
        });
    },
    closeSlider() {
      this.detail.content = '';
      this.detail.loading = false;
    },
    jumpToHome() {
      this.$router.push({
        name: 'retrieve',
        query: {
          projectId: this.currentProject,
        },
      });
      setTimeout(() => {
        this.$emit('reloadRouter');
      });
    },
    handleTabChange(tab) {
      if (!this.requestQuene.includes(tab)) {
        this[this.tabRequestMap[tab]]();
        this.requestQuene.push(tab);
      }
    },
  },
};
</script>

<style scoped lang="scss">
  @import '../../../scss/mixins/clearfix';
  @import '../../../scss/conf';

  .allocation {
    padding: 20px 60px;
    height: 100%;
    width: 100%;
    min-width: 1280px;
    overflow: scroll;

    .icon-refresh {
      color: #3a84ff;
    }
  }

  .deploy {
    padding: 22px 26px;
    display: flex;
    justify-content: space-between;
  }

  .label-ground {
    background-color: #fff;
    padding: 0;
    margin-bottom: 50px;
  }

  .deploy-sub > div {
    display: flex;
    margin-bottom: 33px;

    span:nth-child(1) {
      display: block;
      width: 98px;
      color: #979ba5;
      text-align: right;
      font-size: 14px;
    }

    span:nth-child(2) {
      margin-left: 24px;
      color: #63656e;
      font-size: 14px;
    }

    .deploy-path {
      margin-left: 24px;
      color: #63656e;
      font-size: 14px;
      line-height: 22px;
    }
  }

  .num-color {
    display: inline-block;
    padding: 0;
    color: #4e99ff !important;
    font-weight: bold;
    cursor: pointer;
  }

  .deploy-name {
    border-top: 1px solid #dcdee5;
    border-radius: 2px;

    div {
      height: 40px;
      width: 280px;
      border-bottom: 1px solid #dcdee5;
      border-left: 1px solid #dcdee5;
      border-right: 1px solid #dcdee5;
      line-height: 40px;
      white-space: nowrap;

      span:nth-child(1) {
        margin-left: 14px;
        font-size: 12px;
        color: #313238;
        display: inline-block;
        width: 48px;
      }

      span:nth-child(2) {
        margin-left: 22px;
        font-size: 12px;
        color: #63656e;
      }
    }
  }

  .button-place {
    margin-left: 118px;
  }

  .collect {
    padding: 0 40px;
  }

  .nav-section {
    display: flex;
    justify-content: space-between;

    span {
      color: #bfc0c6;
      font-size: 12px;
      display: inline-block;
      margin-right: 10px;
    }

    .mr10 {
      height: 32px;
    }
  }

  .table-detail {
    width: 100%;

    div {
      width: 100%;
      height: 42px;
      line-height: 42px;
      border-radius: 2px 2px 0 0;
      background-color: #f0f1f5;
      border: 1px solid #dcdee5;
      border-bottom: none;
      user-select: none;
      user-select: none;

      :nth-child(2) {
        font-weight: Bold;
        font-size: 12px;
        color: #63656e;
      }

      span {
        font-size: 12px;
        color: #979ba5;
      }

      :nth-child(3) {
        color: #2dcb56;
        margin-left: 20px;
      }

      :nth-child(5) {
        color: #ea3636;
      }
    }
  }

  .text-style {
    display: flex;

    :nth-child(1) {
      display: inline-block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    :nth-child(2) {
      color: #3a84ff;
      cursor: pointer;
    }
  }

  .SUCCESS {
    color: #2dcb56;
  }

  .FAILED {
    color: #ea3636;
  }

  .PENDING {
    color: $primaryColor;
  }

  .button-group {
    font-size: 0;
    border-radius: 3px;

    span {
      cursor: pointer;
      font-size: 12px;
      display: inline-block;
      height: 32px;
      line-height: 30px;
      padding: 0 15px;
      margin: 0;
      border: 1px #c4c6cc solid;
      border-right: none;
    }

    :nth-child(1) {
      border-bottom-left-radius: 3px;
      border-top-left-radius: 3px;
    }

    :nth-child(4) {
      border-right: 1px #c4c6cc solid;
    }

    .button-wit {
      background-color: white;
      color: #63656e !important;
    }

    .button-bul {
      color: whitesmoke !important;
      background-color: #3a84ff;
    }
  }

  .content-style {
    display: flex;

    > div {
      font-size: 14px;
      margin-left: 24px;

      p {
        display: inline-block;
        margin-right: 2px;
        background-color: #f0f1f5;
        padding: 0 5px;
        border-radius: 2px;
        color: #63656e;
        height: 20px;
        text-align: center;
        line-height: 20px;
      }
    }
  }

  .condition-stylex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;

    > div:nth-child(1) {
      display: flex;

      .the-column {
        > div {
          margin-right: 2px;
          background-color: #f0f1f5;
          padding: 0 5px;
          border-radius: 2px;
          color: #63656e;
          text-align: center;
          margin-top: 16px;
          font-size: 14px;
          height: 20px;
          line-height: 20px;
        }

        :nth-child(1) {
          margin-top: 0 !important;
        }
      }

      :nth-child(2) {
        > div {
          width: 225px;
          position: relative;
          height: 20px;
          margin-top: 16px;

          :nth-child(1) {
            position: absolute;
            left: 5px;
            padding: 0 5px;
            z-index: 100;
            margin-right: 0 !important;
            text-align: center;
            max-width: 200px;
            min-width: 50px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 14px;
          }

          .line-sty {
            position: absolute;
            bottom: 10px;
            right: 0;
            height: 36px;
            width: 180px;
            border-bottom: 1px dashed #c4c6cc;
            border-right: 1px dashed #c4c6cc;
          }
        }

        :nth-child(1) {
          margin-top: 0 !important;
        }
      }
    }

    .line-styy {
      position: absolute;
      bottom: 10px;
      right: 0;
      height: 36px;
      width: 180px;
      border-bottom: 1px dashed #c4c6cc;
    }

    .line-styx {
      width: 20px;
      height: 0;
      border-bottom: 1px dashed #c4c6cc;
    }

    .con-text {
      display: flex;
      align-items: center;
      margin-bottom: 2px;
    }
  }

  .title-icon {
    font-size: 14px;
    margin-left: 23px;

    &:hover {
      cursor: pointer;
    }
  }

  .detail-content {
    min-height: calc(100vh - 60px);
    white-space: pre-wrap;
  }

  /deep/ .bk-sideslider-wrapper {
    padding-bottom: 0;

    .bk-sideslider-content {
      background-color: #313238;
      color: #c4c6cc;
    }
  }
</style>
