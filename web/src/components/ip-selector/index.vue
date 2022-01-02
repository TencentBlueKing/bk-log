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
  <section class="ip-selector" :style="{ height: typeof height === 'number' ? `${height}px` : height }">
    <selector-tab
      ref="tab"
      class="ip-selector-left"
      :panels="panels"
      :active="panelActive"
      :tab-visible="tabVisible"
      @tab-change="handleTabChange">
      <selector-content
        ref="content"
        :active="panelActive"
        :panels="panels"
        v-bind="$attrs"
        v-on="contentEvents">
      </selector-content>
    </selector-tab>
    <div class="preview-toggle" v-if="width === 0">
      <div 
        class="open-preview"
        v-bk-tooltips="{
          content: $t('点击展开'),
          showOnInit: true,
          placements: ['left'],
          delay: 300,
          boundary: 'window'
        }"
        @click.stop="handleResetWidth">
        <i class="bk-icon icon-angle-left"></i>
      </div>
    </div>
    <selector-preview
      v-else
      class="ip-selector-right"
      ref="preview"
      :width.sync="width"
      :range="previewRange"
      :data="previewData"
      :operate-list="previewOperateList"
      :default-active-name="defaultActiveName"
      @menu-click="handlePreviewMenuClick"
      @remove-node="handleRemoveNode">
    </selector-preview>
  </section>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref, Emit, Watch } from 'vue-property-decorator'
import SelectorTab from './selector/selector-tab.vue'
import SelectorContent from './selector/selector-content.vue'
import SelectorPreview from './selector/selector-preview.vue'
import { IEventsMap, IPanel, IMenu, IPerateFunc, IPreviewData } from './types/selector-type'

@Component({
  name: 'ip-selector',
  inheritAttrs: false,
  components: {
    SelectorTab,
    SelectorContent,
    SelectorPreview
  }
})
export default class IpSelector extends Vue {
  @Prop({ default: '', type: String }) private readonly active!: string
  @Prop({ default: () => [], type: Array, required: true }) private readonly panels!: IPanel[]
  @Prop({ default: true, type: Boolean }) private readonly tabVisible!: boolean

  @Prop({ default: 280, type: [Number, String] }) private readonly previewWidth!: number | string
  @Prop({ default: () => [150, 600], type: Array }) private readonly previewRange!: number[]
  @Prop({ default: () => [], type: Array }) private readonly previewData!: IPreviewData[]
  @Prop({ default: () => [], type: [Array, Function] }) private readonly previewOperateList!: IMenu[] | IPerateFunc
  @Prop({ default: '', type: [Number, String] }) private readonly height!: number |  string
  @Prop({ default: () => [], type: Array }) private readonly defaultActiveName!: string[]

  @Ref('tab') private readonly tabRef!: SelectorTab
  @Ref('preview') private readonly previewRef!: SelectorPreview

  private panelActive = this.active // 当前active的tab项
  private width = this.previewWidth // 预览区域宽度
  private excludeEvents = ['tab-change', 'menu-click', 'remove-node'] // 不能丢到layout组件的事件

  private get contentEvents() {
    return Object.keys(this.$listeners).reduce<IEventsMap>((pre, key) => {
      if (this.excludeEvents.includes(key)) return pre
      pre[key] = (...args: any[]) => {
        this.$emit(key, ...args)
      }
      return pre
    }, {})
  }

  @Watch('active')
  private handleActiveChange() {
    this.panelActive = this.active
  }

  private created() {
    if (!this.panelActive) {
      const [firstPanel] = this.panels
      this.panelActive = firstPanel?.name ? firstPanel.name : ''
      this.$emit('update:active', this.panelActive)
    }
  }

  // 展开预览面板
  private handleResetWidth() {
    this.width = this.previewWidth
  }
  // tab切换
  @Emit('tab-change')
  @Emit('update:active')
  private handleTabChange(active: string) {
    this.panelActive = active
    return active
  }
  // 预览面板操作(移除IP、复制IP等操作)
  @Emit('menu-click')
  private handlePreviewMenuClick({ menu, item }: { menu: IMenu, item: IPreviewData }) {
    return {
      menu,
      item
    }
  }
  // 移除预览面板节点
  @Emit('remove-node')
  private handleRemoveNode({ child, item }: { child: any, item: IPreviewData }) {
    return {
      child,
      item
    }
  }
  // eslint-disable-next-line @typescript-eslint/member-ordering
  public handleGetDefaultSelections() {
    try {
      (this.$refs.content as any).handleGetDefaultSelections()
    } catch (err) {
      console.log(err)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import './style/selector.css';

  .ip-selector {
    display: flex;
    height: 100%;
    width: 100%;

    &-left {
      flex: 1;
      width: 0;
    }

    &-right {
      margin-left: -1px;
      position: relative;
    }
  }

  .preview-toggle {
    margin-left: -1px;
    position: relative;
  }

  .open-preview {
    display: flex;
    justify-content: center;
    align-items: center;
    position: absolute;
    left: -10px;
    top: calc(50% - 50px);
    width: 10px;
    height: 100px;
    cursor: pointer;
    border: 1px solid #dcdee5;
    border-right: 0;
    border-radius: 4px 0px 0px 4px;
    background-color: #f0f1f5;
    z-index: 10;
    outline: 0;
  }

  .icon-angle-left {
    display: inline-block;
    width: 16px;
    height: 16px;
    font-size: 16px;
    color: #979ba5;
  }
</style>
