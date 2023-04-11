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
  <div class="basic-info-container" v-bkloading="{ isLoading: basicLoading }">
    <div>
      <div class="deploy-sub" v-if="!isContainer">
        <!-- 数据ID -->
        <div>
          <span>{{ $t('数据ID') }}</span>
          <span>{{ collectorData.bk_data_id || '-' }}</span>
        </div>
        <!-- otlp_log Token -->
        <div v-if="collectorData.custom_type === 'otlp_log'">
          <span>Token</span>
          <section class="token-view">
            <span v-if="!tokenStr" :class="['mask-content', { 'btn-loading': tokenLoading }]">
              <span class="placeholder">●●●●●●●●●●</span>
              <span v-if="tokenLoading" class="loading"></span>
              <bk-button
                text
                class="view-btn"
                v-cursor="{ active: !tokenReviewAuth }"
                :loading="tokenLoading"
                @click="handleGetToken">{{ tokenLoading ? '' : $t('点击查看')}}</bk-button>
            </span>
            <span v-else class="password-content">
              <span :class="{ 'placeholder': true, 'password-value': !showPassword }">
                {{showPassword ? (tokenStr || '-') : '********'}}
              </span>
              <span class="operate-box">
                <span v-if="showPassword" class="icon log-icon icon-copy" @click="handleCopy(tokenStr)"></span>
                <span
                  :class="`bk-icon toggle-icon ${showPassword ? 'icon-eye-slash' : 'icon-eye'}`"
                  @click="showPassword = !showPassword">
                </span>
              </span>
            </span>
          </section>
        </div>
        <!-- 名称 -->
        <div>
          <span>{{ $t('名称') }}</span>
          <span>{{ collectorData.collector_config_name || '-' }}</span>
        </div>
        <template v-if="isCustomReport">
          <div>
            <span>{{ $t('数据类型') }}</span>
            <span>{{ collectorData.custom_name || '-' }}</span>
          </div>
          <div>
            <span>{{ $t('英文名') }}</span>
            <span>{{ collectorData.collector_config_name_en || '-' }}</span>
          </div>
          <div>
            <span>{{ $t('数据分类') }}</span>
            <span>{{ collectorData.category_name || '-' }}</span>
          </div>
          <div>
            <span>{{ $t('说明') }}</span>
            <span>{{ collectorData.description || '-' }}</span>
          </div>
        </template>
        <template v-else>
          <!-- 日志类型 -->
          <div>
            <span>{{ $t('日志类型') }}</span>
            <span>{{ collectorData.collector_scenario_name || '-' }}</span>
          </div>
          <!-- 数据分类 -->
          <div>
            <span>{{ $t('数据分类') }}</span>
            <span>{{ collectorData.category_name || '-' }}</span>
          </div>
          <!-- 日志路径 -->
          <div>
            <span>
              {{collectorData.collector_scenario_id === 'wineventlog' ?
                $t('日志种类') : $t('日志路径') }}
            </span>
            <div v-if="collectorData.params.paths" class="deploy-path">
              <p v-for="(val, key) in collectorData.params.paths" :key="key">{{ val }}</p>
            </div>
            <div v-else class="deploy-path">
              <p>{{getLogSpeciesStr}}</p>
            </div>
          </div>
          <!-- 日志字符集 -->
          <div>
            <span>{{ $t('字符集') }}</span>
            <span>{{ collectorData.data_encoding || '-' }}</span>
          </div>
          <!-- 采集目标 -->
          <div>
            <span>{{ $t('采集目标') }}</span>
            <span>
              <i18n path="已选择 {0} 个{1}">
                <p class="num-color" @click="handleClickTarget">{{ collectorData.target_nodes.length || '-' }}</p>
                {{ collectorData.target_node_type !== 'INSTANCE' ? $t('节点') : $t('静态主机') }}
              </i18n>
            </span>
          </div>
          <!-- 存储索引名 -->
          <div>
            <span>{{ $t('索引名') }}</span>
            <span v-if="collectorData.table_id">{{ collectorData.table_id_prefix }}{{ collectorData.table_id }}</span>
            <span v-else>-</span>
          </div>
          <!-- 备注说明 -->
          <div>
            <span>{{ $t('备注说明') }}</span>
            <span>{{ collectorData.description || '-' }}</span>
          </div>
          <!-- 过滤内容 -->
          <div
            class="content-style"
            v-if="collectorData.params.conditions &&
              collectorData.params.conditions.type === 'match' &&
              collectorData.params.conditions.match_content !== ''">
            <span>{{ $t('过滤内容') }}</span>
            <div>
              <p>{{ $t('字符串匹配') }}</p>
              <p
                v-if="collectorData.params.conditions.match_content">
                {{ collectorData.params.conditions.match_content }}
              </p>
              <p>
                {{ collectorData.params.conditions.match_type }}/{{
                  collectorData.params.conditions.match_type === 'include' ?
                    $t('保留匹配字符串') : $t('过滤匹配字符串') }}
              </p>
            </div>
          </div>
          <!-- 段日志 -->
          <template v-if="collectorData.collector_scenario_id === 'section'">
            <div class="content-style">
              <span>{{ $t('段日志参数') }}</span>
              <div class="section-box">
                <p>{{$t('行首正则')}}: <span>{{collectorData.params.multiline_pattern}}</span></p> <br>
                <p>
                  <i18n path="最多匹配{0}行，最大耗时{1}秒">
                    <span>{{collectorData.params.multiline_max_lines}}</span>
                    <span>{{collectorData.params.multiline_timeout}}</span>
                  </i18n>
                </p>
              </div>
            </div>
          </template>
          <div
            class="content-style"
            v-else-if="collectorData.params.conditions &&
              collectorData.params.conditions.type === 'separator' &&
              collectorData.params.conditions.separator_filters !== []">
            <span>{{ $t('过滤内容') }}</span>
            <div>
              <p>{{ $t('分隔符匹配') }}</p>
              <p v-if="collectorData.params.conditions.separator">{{ collectorData.params.conditions.separator }}</p>
              <div class="condition-stylex">
                <div>
                  <div class="the-column">
                    <div
                      v-for="(val, key) in collectorData.params.conditions.separator_filters"
                      :key="key">
                      {{ $t('第 {n} 列', { n: val.fieldindex })}}
                    </div>
                  </div>
                  <div>
                    <div v-for="(val, key) in collectorData.params.conditions.separator_filters" :key="key">
                      <p @mouseenter="handleEnter" @mouseleave="handleLeave">{{ val.word }}</p>
                      <div
                        :class="key === 0 ? 'line-styy' : 'line-sty'"
                        v-if="collectorData.params.conditions.separator_filters.length > 1">
                      </div>
                    </div>
                  </div>
                </div>
                <div class="con-text" v-if="collectorData.params.conditions.separator_filters.length > 1">
                  <div class="line-styx"></div>
                  <p>
                    {{ collectorData.params.conditions.separator_filters[0].logic_op === 'and' ?
                      $t('并') : $t('或') }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="content-style"
               v-else-if="collectorData.collector_scenario_id === 'wineventlog' && isHaveEventValue">
            <span>{{ $t('过滤内容') }}</span>
            <div class="win-log">
              <div>
                <p>{{$t('事件ID')}}:{{getEventIDStr}}</p>
              </div>
              <div>
                <p>{{$t('级别')}}:{{getLevelStr}}</p>
              </div>
            </div>
          </div>
          <div class="content-style" v-else>
            <span>{{ $t('过滤内容') }}</span>
            <div>
              --
            </div>
          </div>
        </template>
        <!-- 存储集群 -->
        <div>
          <span>{{ $t('存储集群') }}</span>
          <span>{{ collectorData.storage_cluster_name || '-' }}</span>
        </div>
        <!-- 存储索引名 -->
        <div>
          <span>{{ $t('索引名') }}</span>
          <span>{{ collectorData.table_id_prefix + collectorData.table_id || '-' }}</span>
        </div>
        <!-- 过期时间 -->
        <div>
          <span>{{ $t('过期时间') }}</span>
          <span>{{ collectorData.retention || '-' }} {{ $t('天') }}</span>
        </div>
      </div>
      <container-base v-else :collector-data="collectorData" :is-loading.sync="basicLoading"></container-base>
    </div>
    <div>
      <bk-button
        :theme="'default'"
        ext-cls=""
        style="min-width: 88px; color: #3a84ff;"
        v-cursor="{ active: !editAuth }"
        @click="handleClickEdit"
        class="mr10">
        {{ $t('编辑') }}
      </bk-button>
      <bk-popover placement="bottom-end">
        <bk-button class="log-icon icon-lishijilu"></bk-button>
        <div slot="content" class="create-name-and-time">
          <div v-for="item in createAndTimeData" :key="item.key">
            <span>{{ item.label }}</span>
            <span>{{ item.value }}</span>
          </div>
        </div>
      </bk-popover>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { formatDate, copyMessage } from '@/common/util';
import containerBase from './components/container-base';
import * as authorityMap from '../../../../../../common/authority-map';

export default {
  components: {
    containerBase,
  },
  props: {
    collectorData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // 右边展示的创建人、创建时间
      createAndTimeData: [],
      editAuth: false,
      authData: null,
      basicLoading: false,
      isShowToken: false, // 是否展示 oltp_log Token
      showPassword: true, // 是否展示Token值
      tokenReviewAuth: false, // 是否有查看token的权限
      tokenLoading: false,
      tokenStr: '', // token 的值
    };
  },
  computed: {
    ...mapState(['spaceUid']),
    getEventIDStr() {
      return this.collectorData.params.winlog_event_id?.join(',') || '';
    },
    getLevelStr() {
      return this.collectorData.params.winlog_level?.join(',') || '';
    },
    getLogSpeciesStr() {
      return this.collectorData.params.winlog_name?.join(',') || '';
    },
    isHaveEventValue() {
      return this.collectorData.params.winlog_event_id.length || this.collectorData.params.winlog_level.length;
    },
    isContainer() {
      return this.collectorData.environment === 'container';
    },
    // 自定义上报基本信息
    isCustomReport() {
      return this.$route.name === 'custom-report-detail';
    },
  },
  created() {
    this.getCollectDetail();
    this.getEditAuth();
  },
  methods: {
    getCollectDetail() {
      try {
        const collectorData = this.collectorData;
        const createAndTimeData = [{
          key: 'updated_by',
          label: this.$t('更新人'),
        }, {
          key: 'updated_at',
          label: this.$t('更新时间'),
        }, {
          key: 'created_by',
          label: this.$t('创建人'),
        }, {
          key: 'created_at',
          label: this.$t('创建时间'),
        }];
        this.createAndTimeData = createAndTimeData.map((item) => {
          if (item.key === 'created_at' || item.key === 'updated_at') {
            item.value = formatDate(collectorData[item.key]);
          } else {
            item.value = collectorData[item.key];
          }
          return item;
        });
      } catch (e) {
        console.warn(e);
      }
    },
    handleClickTarget() {
      this.$emit('update-active-panel', 'collectionStatus');
    },
    // 判断是否超出  超出提示
    handleEnter(e) {
      const cWidth = e.target.clientWidth;
      const sWidth = e.target.scrollWidth;
      if (sWidth > cWidth) {
        this.instance = this.$bkPopover(e.target, {
          content: e.path[0].childNodes[0].data,
          arrow: true,
          placement: 'right',
        });
        this.instance.show(1000);
      }
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    handleClickEdit() {
      if (!this.editAuth && this.authData) {
        this.$store.commit('updateAuthDialogData', this.authData);
        return;
      };
      const params = {};
      params.collectorId = this.$route.params.collectorId;
      const routeName = this.isCustomReport ? 'custom-report-edit' : 'collectEdit';
      this.$router.push({
        name: routeName,
        params,
        query: {
          spaceUid: this.$store.state.spaceUid,
        },
      });
    },
    async getEditAuth() {
      try {
        const paramData = {
          action_ids: [authorityMap.MANAGE_COLLECTION_AUTH],
          resources: [{
            type: 'collection',
            id: this.$route.params.collectorId,
          }],
        };
        const res = await this.$store.dispatch('checkAndGetData', paramData);
        if (!res.isAllowed) this.authData = res.data;
        this.editAuth = res.isAllowed;
        this.tokenReviewAuth = res.isAllowed;
      } catch (error) {
        this.editAuth = false;
        this.tokenReviewAuth = false;
      }
    },
    async handleGetToken() {
      if (!this.tokenReviewAuth && this.authData) {
        this.$store.commit('updateAuthDialogData', this.authData);
        return;
      };
      try {
        this.tokenLoading = true;
        const res = await this.$http.request('collect/reviewToken', {
          params: {
            collector_config_id: this.$route.params.collectorId,
          },
        });
        this.tokenStr = res.data?.bk_data_token || '-';
      } catch (error) {
        console.warn(error);
        this.tokenStr = '';
      } finally {
        this.tokenLoading = false;
      }
    },
    handleCopy(text) {
      copyMessage(text);
    },
  },
};
</script>

<style lang="scss" scoped>
@import '@/scss/basic.scss';
@import '@/scss/mixins/flex.scss';

.basic-info-container {
  display: flex;
  justify-content: space-between;

  .deploy-sub > div {
    display: flex;
    margin-bottom: 33px;

    > span:nth-child(1) {
      display: block;
      width: 98px;
      color: #979ba5;
      text-align: right;
      font-size: 14px;
    }

    > span:nth-child(2) {
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

    .num-color {
      display: inline-block;
      padding: 0;

      /* stylelint-disable-next-line declaration-no-important */
      color: #4e99ff !important;
      font-weight: bold;
      cursor: pointer;
    }
  }

  .content-style {
    display: flex;

    .win-log {
      height: 60px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .section-box {
      > :last-child {
        margin-top: 4px;
      }

      span {
        /* stylelint-disable-next-line declaration-no-important */
        display: inline !important;
      }
    }

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


  .create-name-and-time {
    border-top: 1px solid #dcdee5;
    border-radius: 2px;

    div {
      height: 40px;
      width: 260px;
      border-bottom: 1px solid #dcdee5;
      border-left: 1px solid #dcdee5;
      border-right: 1px solid #dcdee5;
      line-height: 40px;

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

  .token-view {
    margin: -2px 0 0 24px;
    color: #63656e;

    .mask-content {
      .view-btn {
        font-size: 12px;
        margin-left: 8px;
        color: #3a84ff;
        cursor: pointer;
      }

      &.btn-loading {
        color: #c4c6cc;
        cursor: not-allowed;

        .view-btn {
          color: #c4c6cc;
        }
      }
    }

    .password-content {
      height: 24px;
      font-size: 14px;

      @include flex-align;

      .toggle-icon {
        margin-left: 8px;
        cursor: pointer;
      }

      .operate-box {
        display: inline-block;
        position: relative;
        top: -2px;
      }

      .icon-copy {
        position: absolute;
        top: -2px;
        font-size: 26px;
        margin-left: 8px;
        cursor: pointer;

        &:hover {
          color: #3a84ff;
        }
      }

      .icon-eye-slash {
        margin-left: 36px;
      }

      .password-value {
        padding-top: 6px;
      }
    }
  }


}
</style>
