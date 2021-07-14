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
  <div class="ip-select" :style="{ minWidth: minWidth + 'px',height: height + 'px' }" v-bind="$attrs">
    <div class="ip-select-left">
      <div class="left-tab">
        <span
          class="left-tab-item"
          :class="[active === 0 ? 'active' : 'tab-item', { 'tab-disabled': tabDisabled === 0 }]"
          :style="{ 'border-right': active === 1 ? '1px solid #DCDEE5' : 'none' }"
          @click="tabDisabled !== 0 && handleTabClick(0)"
          @mouseleave="handleStaticMouseLeave"
          @mouseenter="handleStaticMouseEnter">
          <span ref="staticTab"><slot name="left-tab">{{ $t('configDetails.static') }}</slot></span>
        </span>
        <span
          class="left-tab-item"
          :class="[active === 1 ? 'active' : 'tab-item', { 'tab-disabled': tabDisabled === 1 }]"
          :style="{ 'border-left': active === 0 ? '1px solid #DCDEE5' : 'none' }"
          @click="tabDisabled !== 1 && handleTabClick(1)"
          @mouseleave="handleDynamicMouseLeave"
          @mouseenter="handleDynamicMouseEnter">
          <span ref="dynamicTab"><slot name="left-tab">{{ $t('configDetails.dynamic') }}</slot></span>
        </span>
      </div>
      <div class="left-content">
        <bk-select
          v-if="active === 0 && !selectUnshow.includes(active)"
          v-model="select.staticActive" class="left-content-select"
          :popover-min-width="200"
          :clearable="false">
          <bk-option
            v-for="option in select.staticList"
            :disabled="activeDiabled.includes(option.id)"
            :key="option.id"
            :id="option.id"
            :name="option.name"
            v-show="!activeUnshow.includes(option.id)">
          </bk-option>
        </bk-select>
        <bk-select
          v-if="active === 1 && !selectUnshow.includes(active)"
          v-model="select.dynamicActive"
          class="left-content-select"
          :popover-min-width="200"
          :clearable="false">
          <bk-option
            v-for="option in select.dynamicList"
            :key="option.id"
            :disabled="activeDiabled.includes(option.id)"
            :id="option.id"
            :name="option.name"
            v-show="!activeUnshow.includes(option.id)">
          </bk-option>
        </bk-select>
        <div
          class="left-content-wrap"
          :style="{ '--height': height + 'px' }"
          v-bkloading="{ isLoading: isShowTreeLoading && leftLoading }">
          <keep-alive>
            <template>
              <slot
                v-if="curActive === 0"
                name="static-input"
                v-bind="{
                  defaultText: staticInput.defaultText,
                  checked: handleSelectChecked
                }">
                <template>
                  <static-input
                    :default-text="staticInput.defaultText"
                    @checked="handleSelectChecked"
                    @change-input="handleChangeInput">
                    <slot name="change-input"></slot>
                  </static-input>
                </template>
              </slot>
              <slot v-else-if="curActive === 1"
                    name="static-topo"
                    v-bind="{
                      treeData: staticTopo.treeData,
                      checkedData: staticChecked,
                      disabledData: staticTopo.disabledData,
                      filterMethod: filterMethod,
                      keyword: search.keyword,
                      nodeCheck: handleSelectChecked
                    }">
                <template>
                  <static-topo
                    v-if="staticTopo.treeData.length"
                    :tree-data="staticTopo.treeData"
                    :checked-data="staticChecked"
                    :disabled-data="staticTopo.disabledData"
                    :filter-method="filterMethod"
                    :keyword="search.keyword"
                    :is-search-no-data.sync="isSearchNoData"
                    @node-check="handleSelectChecked"></static-topo>
                </template>
              </slot>
              <slot
                v-else-if="curActive === 2"
                name="dynamic-topo"
                v-bind="{
                  treeData: dynamicTopo.treeData,
                  checkedData: dynamicTopo.checkedData,
                  disabledData: dynamicTopo.disabledData,
                  filterMethod: filterMethod,
                  keyword: search.keyword,
                  refs: $refs.dynamicTopo,
                  nodeCheck: handleSelectChecked
                }">
                <template>
                  <dynamic-topo
                    v-if="dynamicTopo.treeData.length"
                    :tree-data="dynamicTopo.treeData"
                    :checked-data="dynamicTopo.checkedData"
                    :disabled-data="dynamicTopo.disabledData"
                    :filter-method="filterMethod"
                    :keyword="search.keyword"
                    :is-search-no-data.sync="isSearchNoData"
                    ref="dynamicTopo"
                    @node-check="handleSelectChecked"></dynamic-topo>
                </template>
              </slot>
              <slot
                v-else-if="curActive === 3"
                name="dynamic-group"
                v-bind="{
                  treeData: dynamicGroup.treeData,
                  checkedData: dynamicGroup.checkedData,
                  disabledData: dynamicGroup.disabledData,
                  filterMethod: filterMethod,
                  keyword: search.keyword,
                  refs: $refs.dynamicGroup,
                  nodeCheck: handleSelectChecked
                }">
                <template>
                  <dynamic-group
                    v-if="dynamicGroup.treeData.length"
                    :tree-data="dynamicGroup.treeData"
                    :checked-data="dynamicGroup.checkedData"
                    :disabled-data="dynamicGroup.disabledData"
                    :filter-method="filterMethod"
                    :keyword="search.keyword"
                    ref="dynamicGroup"
                    @node-check="handleSelectChecked"></dynamic-group>
                </template>
              </slot>
            </template>
          </keep-alive>
          <div v-if="isSearchNoData" class="search-none">
            <slot name="search-noData"></slot>
          </div>
        </div>
      </div>
      <div class="left-footer" :class="{ 'input-focus': search.focus }" v-show="curActive === 1">
        <i class="bk-icon icon-search left-footer-icon"></i>
        <input
          class="left-footer-input"
          :placeholder="$t('retrieve.Multiple_carriage')"
          @focus="handleSearchFocus"
          @blur="search.focus = false"
          v-model="search.keyword" />
      </div>
    </div>
    <div class="ip-select-right">
      <div
        :key="staticIp.type" class="right-wrap"
        :class="{ 'is-expand': staticIp.expand }"
        v-if="staticTableData.length"
        v-bkloading="{ isLoading: isShowTableLoading && staticLoading }">
        <right-panel
          v-model="staticIp.expand"
          type="staticIp"
          @change="handleCollapseChange" :
          title="{ num: curComp.tableData.length }">
          <slot name="static-ip-panel"
                v-bind="{
                  data: staticTableData,
                  deleteClick: handleDeleteStaticIp
                }">
            <bk-table :data="staticTableData" :empty-text="$t('retrieve.no_data')">
              <bk-table-column prop="ip" label="IP" min-width="210">
              </bk-table-column>
              <bk-table-column prop="agent" :label="$t('retrieve.state')">
              </bk-table-column>
              <bk-table-column prop="cloud" :label="$t('retrieve.Cloud_area')">
              </bk-table-column>
              <bk-table-column :label="$t('indexSetList.operation')" align="center" width="80">
                <template slot-scope="scope">
                  <bk-button text @click="handleDeleteStaticIp(scope)">{{$t('retrieve.remove')}}</bk-button>
                </template>
              </bk-table-column>
            </bk-table>
          </slot>
        </right-panel>
      </div>
      <div :key="dynamicTopo.type" class="right-wrap"
           v-bkloading="{ isLoading: isShowTableLoading && dynamicTopo.loading }"
           :class="{ 'is-expand': dynamicTopo.expand }"
           v-if="dynamicTopo.tableData.length">
        <right-panel
          v-model="dynamicTopo.expand"
          @change="handleCollapseChange"
          type="dynamicTopo"
          :title="{ num: dynamicTopo.tableData.length, 'type': $t('retrieve.node') }">
          <slot name="dynamic-topo-panel" v-bind="{
            data: dynamicTopo.tableData,
            deleteClick: handleDelDynamicTopo
          }">
            <ul class="topo-list">
              <li class="topo-list-item" v-for="(item,index) in dynamicTopo.tableData" :key="index">
                <span class="item-name">{{item.name}}</span>
                <div class="item-desc">
                  {{$t('retrieve.Existing_host')}}
                  <span class="status-host">{{item.host}}</span>，
                  <span class="status-unusual">{{item.unusual}}</span>
                  {{$t('retrieve.host_abnormal')}}
                </div>
                <bk-button
                  text class="item-btn"
                  @click="handleDelDynamicTopo(index,item)">
                  {{$t('retrieve.remove')}}
                </bk-button>
              </li>
            </ul>
          </slot>
        </right-panel>
      </div>
      <div
        :key="dynamicGroup.type" class="right-wrap"
        v-bkloading="{ isLoading: isShowTableLoading && dynamicGroup.loading }"
        :class="{ 'is-expand': dynamicGroup.expand }"
        v-if="dynamicGroup.tableData.length">
        <right-panel v-model="curComp.expand" @change="handleCollapseChange" type="dynamicTopo">
          <slot name="dynamic-group-panel"
                v-bind="{
                  data: dynamicGroup.tableData
                }">
          </slot>
        </right-panel>
      </div>
      <div key="right-empty" class="right-empty" v-if="isNoData">
        <span class="icon-monitor icon-hint"></span>
        <div class="right-empty-title">{{$t('retrieve.Nothing_selected')}}</div>
        <div class="right-empty-desc">{{defaultEmptyDesc}}</div>
      </div>
    </div>
  </div>
</template>
<script>
import RightPanel from './right-panel';
import StaticInput from './static-input';
import StaticTopo from './static-topo';
import DynamicTopo from './dynamic-topo';
import DynamicGroup from './dynamic-group';

export default {
  name: 'ip-select',
  components: {
    RightPanel,
    StaticInput,
    StaticTopo,
    DynamicTopo,
    DynamicGroup,
  },
  props: {
    minWidth: {
      type: [Number, String],
      default: 850,
    },
    height: {
      type: [Number, String],
      default: 460,
    },
    idKey: {
      type: String,
      default: 'id',
    },
    nameKey: {
      type: String,
      default: 'name',
    },
    childrenKey: {
      type: String,
      default: 'children',
    },
    tabDisabled: {
      type: Number,
      default: -1,
    },
    activeDiabled: {
      type: Array,
      default() {
        return [3];
      },
    },
    activeUnshow: {
      type: Array,
      default() {
        return [];
      },
    },
    selectUnshow: {
      type: Array,
      default() {
        return [];
      },
    },
    defaultActive: {
      type: Number,
      required: true,
    },
    defaultEmptyDesc: {
      type: String,
      default: global.mainComponent.$t('retrieve.Please_left'),
    },
    inputIpSplit: {
      type: String,
      default: '|',
    },
    getDefaultData: {
      type: Function,
      required: true,
    },
    getFetchData: {
      type: Function,
      required: true,
    },
    filterMethod: {
      type: Function,
      default: () => () => {},
    },
    isShowTreeLoading: {
      type: Boolean,
      default: true,
    },
    isShowTableLoading: {
      type: Boolean,
      default: true,
    },
    isInstance: Boolean,
  },
  data() {
    return {
      active: 0,
      changeInput: false,
      select: {
        staticList: [
          {
            id: 0,
            name: this.$t('retrieve.IP_input'),
            type: 'staticInput',
          },
          {
            id: 1,
            name: this.$t('retrieve.Business'),
            type: 'staticTopo',
          },
        ],
        dynamicList: [
          {
            id: 2,
            name: this.$t('retrieve.Business'),
            type: 'dynamicTopo',
          },
          {
            id: 3,
            name: this.$t('retrieve.Dynamic_grouping'),
            type: 'dynamicGroup',
          },
        ],
        staticActive: 0,
        dynamicActive: 2,
      },
      staticInput: {
        name: 'staticIp',
        defaultText: '',
        expand: false,
        checkedData: [],
        tableData: [],
        type: 'static-ip',
        mark: false,
        loading: false,
      },
      staticTopo: {
        name: 'staticIp',
        treeData: [],
        checkedData: [],
        disabledData: [],
        expand: false,
        tableData: [],
        type: 'static-topo',
        loading: false,
      },
      dynamicTopo: {
        name: 'dynamicTopo',
        treeData: [],
        checkedData: [],
        disabledData: [],
        expand: false,
        tableData: [],
        type: 'dynamic-topo',
        loading: false,
      },
      dynamicGroup: {
        name: 'dynamicGroup',
        treeData: [],
        checkedData: [],
        disabledData: [],
        expand: false,
        tableData: [],
        type: 'dynamic-group',
        loading: false,
      },
      search: {
        keyword: '',
        focus: false,
      },
      leftLoading: false,
      isSearchNoData: false,
      staticIp: {
        expand: false,
      },
      instance: {
        dynamic: null,
        static: null,
      },
    };
  },
  computed: {
    curComp() {
      return this[this.curItem.type];
    },
    curActive() {
      return this.active === 0 ? this.select.staticActive : this.select.dynamicActive;
    },
    curItem() {
      return this.active === 0
        ? this.select.staticList.find(item => item.id === this.select.staticActive)
        : this.select.dynamicList.find(item => item.id === this.select.dynamicActive);
    },
    staticTableData() {
      let arr = this.handleStaticTableData(this.staticInput.tableData, this.staticTopo.tableData);
      const hash = {};
      arr = arr.reduce((item, next) => {
        if (!hash[next.name]) {
          hash[next.name] = true;
          item.push(next);
        }
        return item;
      }, []);
      return arr;
    },
    staticChecked() {
      const ids = this.handleStaticTableData(this.staticInput.checkedData, this.staticTopo.checkedData, false);
      ids.concat(this.staticTopo.checkedData);
      return Array.from(new Set(ids));
    },
    staticLoading() {
      return this.staticInput.loading || this.staticTopo.loading;
    },
    isNoData() {
      return !this.staticTableData.length && !this.dynamicTopo.tableData.length && !this.dynamicGroup.tableData.length;
    },
  },
  watch: {
    curActive: {
      handler: 'handlerCurActiveChange',
      // immediate: true
    },
    defaultActive: {
      handler(v) {
        if (v === 0 || v === 1) {
          this.active = 0;
          this.select.staticActive = v;
          this.curComp.expand = true;
          this.staticIp.expand = true;
        } else if (v === 2 || v === 3) {
          this.active = 1;
          this.select.dynamicActive = v;
          this.curComp.expand = true;
        }
      },
      immediate: true,
    },
  },
  methods: {
    async handleSelectChecked(type, payload) {
      const { curComp } = this;
      try {
        curComp.loading = true;
        const { checkedData, tableData, disabledData } = await this.getFetchData(type, payload);
        this.setCurActivedCheckedData(checkedData);
        this.setCurActivedDisabledData(disabledData);
        this.setCurActivedTableData(tableData);
        this.handleCollapseChange(true, curComp.name);
      } catch (e) {
        throw e;
      } finally {
        curComp.loading = false;
      }
    },
    async handlerCurActiveChange(v) {
      try {
        if (typeof this.getDefaultData === 'function') {
          this.leftLoading = true;
          if ((v > 0 && this.curComp.treeData.length === 0) || (v === 0 && !this.curComp.mark)) {
            const data = await this.getDefaultData(this.curComp.type);
            this.leftLoading = false;
            if (data) {
              if (v > 0) {
                this.curComp.treeData = data.treeData || [];
                this.curComp.checkedData = data.checkedData || [];
                this.curComp.disabledData = data.disabledData || [];
                this.curComp.tableData = data.tableData || [];
              } else {
                this.curComp.tableData = data.tableData || [];
                this.curComp.mark = true;
                this.curComp.defaultText = (data.defaultText || '').replace(new RegExp(`\\${this.inputIpSplit}`, 'gm'), '\n');
              }
            }
          }
        }
      } catch (e) {
        throw e;
      } finally {
        this.leftLoading = false;
      }
    },
    handleStaticTableData(data1, data2, value = true) {
      const data = new Map();
      let len = Math.max(data1.length, data2.length);
      while (len) {
        const item1 = data1[len - 1];
        const item2 = data2[len - 1];
        if (item1) {
          if (item1[this.idKey]) {
            data.set(item1[this.idKey], item1);
          } else {
            data.set(item1, item1);
          }
        }
        if (item2) {
          if (item2[this.idKey]) {
            data.set(item2[this.idKey], item2);
          } else {
            data.set(item2, item2);
          }
        }
        len = len - 1;
      }
      return value ? Array.from(data.values()) : Array.from(data.keys());
    },
    handleSearchFocus() {
      this.search.focus = true;
    },
    handleCollapseChange(v, set) {
      if (v) {
        ['staticIp', 'dynamicTopo'].forEach((key) => {
          this[key].expand = set === key;
        });
      } else {
        this[set].expand = v;
      }
    },
    handleDeleteStaticIp(scope) {
      this.staticInput.tableData = this.staticInput.tableData.filter((item) => {
        return item[this.idKey] !== scope.row[this.idKey];
      });
      this.staticTopo.tableData = this.staticTopo.tableData.filter(item => item[this.idKey] !== scope.row[this.idKey]);
    },
    handleDelDynamicTopo(index, item) {
      const setIndex = this.dynamicTopo.checkedData.findIndex(setId => setId === item[this.idKey]);
      if (setIndex > -1) {
        this.$refs.dynamicTopo.handleSetChecked([this.dynamicTopo.checkedData[setIndex]], false);
        this.dynamicTopo.checkedData.splice(setIndex, 1);
      }
      this.dynamicTopo.tableData.splice(index, 1);
    },
    handleTabClick(active) {
      this.active = active;
      this.$emit('change-tab', this.active);
    },
    getValues() {
      return {
        staticIp: this.staticTableData,
        dynamicTopo: this.dynamicTopo.tableData,
      };
    },
    setCurActivedCheckedData(checkedData) {
      if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
        this.staticInput.checkedData = Array.isArray(checkedData) ? checkedData.slice() : [];
        this.staticTopo.checkedData = this.staticInput.checkedData;
      } else {
        this.curComp.checkedData = Array.isArray(checkedData) ? checkedData.slice() : [];
      }
    },
    setCurActivedDisabledData(disabledData) {
      if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
        this.staticInput.disabledData = Array.isArray(disabledData) ? disabledData.slice() : [];
        this.staticTopo.disabledData = this.staticInput.disabledData;
      } else {
        this.curComp.disabledData = Array.isArray(disabledData) ? disabledData.slice() : [];
      }
    },
    setCurActivedTableData(tableData) {
      if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
        this.staticInput.tableData = Array.isArray(tableData) ? tableData.slice() : [];
        this.staticTopo.tableData = this.staticInput.tableData;
      } else {
        this.curComp.tableData = Array.isArray(tableData) ? tableData.slice() : [];
      }
    },
    handleStaticMouseEnter() {
      if (this.tabDisabled === 1 || this.tabDisabled === -1) {
        if (this.instance.static) {
          this.instance.static.destroy(true);
          this.instance.static = null;
        }
        return false;
      }
      const staticRef = this.$refs.staticTab;
      let content = '支持静态IP的选择方式';
      if (this.tabDisabled === 0 && this.isInstance) {
        content = '监控对象为服务，只能选择动态方式';
      } else if (this.tabDisabled === 0) {
        content = '动态和静态不能混用';
      }
      if (!this.instance.static) {
        this.instance.static = this.$bkPopover(staticRef, {
          content,
          arrow: true,
          maxWidth: 250,
          showOnInit: true,
          distance: 14,
          placement: 'right',
        });
      }
      this.instance.static.set({ content });
      this.instance.static && this.instance.static.show(100);
    },
    handleStaticMouseLeave() {
      this.instance.static && this.instance.static.hide(0);
    },
    handleDynamicMouseEnter() {
      if (this.tabDisabled === 0 || this.tabDisabled === -1) {
        if (this.instance.dynamic) {
          this.instance.dynamic.destroy(true);
          this.instance.dynamic = null;
        }
        return false;
      }
      let content = '支持按拓扑节点动态变化进行采集';
      if (this.tabDisabled === 1) {
        content = '动态和静态不能混用';
      }
      const dynamicRef = this.$refs.dynamicTab;
      if (!this.instance.dynamic) {
        this.instance.dynamic = this.$bkPopover(dynamicRef, {
          content,
          arrow: true,
          maxWidth: 250,
          showOnInit: true,
          distance: 14,
          placement: 'right',
        });
      }
      this.instance.dynamic.set({ content });
      this.instance.dynamic && this.instance.dynamic.show(100);
    },
    handleDynamicMouseLeave() {
      this.instance.dynamic && this.instance.dynamic.hide(0);
    },
    handleChangeInput(v) {
      this.$emit('change-input', v);
    },
  },
};
</script>
<style lang="scss" scoped>
  .ip-select {
    display: flex;
    background-color: #fff;
    border-radius: 2px;
    color: #63656e;
    font-size: 12px;

    .ip-select-left {
      flex: 0 0 240px;
      background-image: linear-gradient(180deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%),
        linear-gradient(90deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%),
        linear-gradient(-90deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%),
        linear-gradient(0deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%);
      background-size: 100% 100%;
      position: relative;

      .left-tab {
        display: flex;
        height: 42px;
        font-size: 14px;

        .left-tab-item {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 1px solid #dcdee5;
          background: #fafbfd;

          &:first-child {
            border-right: none
          }

          &.active {
            background: #fff;
            border-bottom: none;
            height: 41px;
          }

          &.tab-item:hover {
            border-color: #3a84ff !important;
            cursor: pointer;
            color: #3a84ff;
          }

          &.tab-disabled {
            color: #c4c6cc;

            &:hover {
              cursor: not-allowed;
              border-color: #dcdee5 !important;
              color: #c4c6cc;
            }
          }
        }
      }

      .left-content {
        padding: 20px;

        .left-content-select {
          width: 200px;
        }

        .left-content-wrap {
          height: calc(var(--height) - 142px);
          max-width: 200px;
          overflow: auto;

          &::-webkit-scrollbar {
            width: 4px;
            background-color: #dcdee5;
          }

          &::-webkit-scrollbar-thumb {
            height: 5px;
            border-radius: 2px;
            background-color: #dcdee5;
          }
        }

        .search-none {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 250px;
        }
      }

      .left-footer {
        height: 33px;
        display: flex;
        align-items: center;
        border: 1px solid #dcdee5;
        color: #c4c6cc;
        position: absolute;
        left: 0;
        bottom: 0;
        right: 0;

        ::placeholder {
          color: #979ba5;
        }

        &.input-focus {
          border-color: #3a84ff;

          .icon-search {
            color: #3a84ff
          }
        }

        .left-footer-icon {
          font-size: 14px;
          flex: 0 0 34px;
          text-align: center;
        }

        .left-footer-input {
          color: #63656e;
          height: 30px;
          width: 100%;
          border: none;
          outline: none;
        }
      }
    }

    .ip-select-right {
      flex: 1;
      background-image: linear-gradient(180deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%),
        linear-gradient(-90deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%),
        linear-gradient(0deg, #dcdee5 1px, rgba(0, 0, 0, 0) 1px, rgba(0, 0, 0, 0) 100%);
      background-size: 100% 100%;
      border-left: none;
      overflow: auto;

      .right-wrap {
        border: 1px solid #dcdee5;
        border-left: 0;

        &.is-expand {
          border-bottom: 0;
        }

        & + .right-wrap {
          border-top: 0
        }

        .topo-list {
          color: #63656e;
          font-size: 12px;

          .topo-list-item {
            height: 40px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #dfe0e5;
            padding-left: 32px;

            &:hover {
              background-color: #f0f1f5;
            }

            .item-desc {
              flex: 1;
              margin-left: 94px;
              color: #979ba5;

              .status-host {
                color: #3a84ff;
                font-weight: bold;
              }

              .status-unusual {
                color: #ea3636;
                font-weight: bold;
              }
            }

            .item-btn {
              margin-right: 21px;
              font-size: 12px;
            }
          }
        }
      }

      .right-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        margin-top: 164px;

        .icon-monitor {
          font-size: 28px;
          color: #dcdee5;
          margin-bottom: 8px;
        }

        .right-empty-title {
          font-size: 14px;
          margin-bottom: 3px;
        }

        .right-empty-desc {
          color: #c4c6cc;
        }
      }
    }
  }
</style>
