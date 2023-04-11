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
  <div 
    class="selector-preview"
    :style="{ width: isNaN(preWidth) ? preWidth : `${preWidth}px` }"
    v-show="isNaN(preWidth) || preWidth > 0">
    <div class="selector-preview-title">
      <slot name="title">{{ $t('结果预览') }}</slot>
    </div>
    <div class="selector-preview-content">
      <bk-collapse v-model="activeName">
        <bk-collapse-item
          v-for="item in data"
          :key="item.id"
          :name="item.id"
          hide-arrow
          v-show="item.data && item.data.length">
          <template #default>
            <div class="collapse-title">
              <span class="collapse-title-left">
                <i :class="['bk-icon icon-angle-right', { expand: activeName.includes(item.id) }]"></i>
                <slot name="collapse-title" v-bind="{ item }">
                  <i18n path="已选 {0} 个">
                    <span class="num">{{ item.data.length }}</span>
                  </i18n>
                </slot>
              </span>
              <span class="collapse-title-right" @click.stop="handleShowMenu($event, item)">
                <i class="bk-icon icon-more"></i>
              </span>
            </div>
          </template>
          <template #content>
            <slot name="collapse-content" v-bind="{ item }">
              <ul class="collapse-content">
                <li v-for="(child, index) in item.data"
                    :key="index"
                    class="collapse-content-item"
                    @mouseenter="hoverChild = child"
                    @mouseleave="hoverChild = null">
                  <span class="left" :title="child[item.dataNameKey] || child.name || '--'">
                    {{ child[item.dataNameKey] || child.name || '--' }}
                  </span>
                  <span class="right"
                        v-show="hoverChild === child"
                        @click="removeNode(child, item)">
                    <i class="bk-icon icon-close-line"></i>
                  </span>
                </li>
              </ul>
            </slot>
          </template>
        </bk-collapse-item>
      </bk-collapse>
    </div>
    <div class="drag" @mousedown="handleMouseDown"></div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit, Watch } from 'vue-property-decorator'
import { IPreviewData, IMenu, IPerateFunc } from '../types/selector-type'
import { Debounce } from '../common/util'
import Menu from '../components/menu.vue'

// 预览区域
@Component({ name: 'selector-preview' })
export default class SelectorPreview extends Vue {
  @Prop({ default: 280, type: [Number, String] }) private readonly width!: number | string
  @Prop({ default: () => [100, 600], type: Array }) private readonly range!: number[]
  @Prop({ default: () => [], type: Array }) private readonly data!: any[]
  @Prop({ default: () => [], type: [Array, Function] }) private readonly operateList!: IMenu[] | IPerateFunc
  @Prop({ default: () => [], type: Array }) private readonly defaultActiveName!: string[]

  private preWidth: number | string = 280;
  private activeName: string[] = [];
  private hoverChild = null;
  private menuInstance = null;
  private popoverInstance: any = null;
  private previewItem: IPreviewData = null;

  created() {
    this.preWidth = this.width;
    this.activeName = this.defaultActiveName;
    this.menuInstance = new Menu().$mount();
  }

  @Watch('width')
  private handleChange(width: number) {
    this.preWidth = width
  }

  private beforeDestroy() {
    if (this.menuInstance) {
      this.menuInstance.$off('click', this.handleMenuClick)
      this.menuInstance.$destroy()
    }
  }

  @Debounce(300)
  @Emit('update:width')
  private handleWidthChange() {
    return this.preWidth
  }

  @Emit('menu-click')
  private handleMenuItemClick(menu: IMenu, item: IPreviewData) {
    return {
      menu,
      item
    }
  }

  @Emit('remove-node')
  private removeNode(child: any, item: IPreviewData) {
    const index = item.data.indexOf(child)
    this.hoverChild = index > -1 && item.data[index + 1] ? item.data[index + 1] : null
    return {
      child,
      item
    }
  }

  private handleMenuClick(menu: IMenu) {
    this.popoverInstance && this.popoverInstance.hide()
    this.handleMenuItemClick(menu, this.previewItem)
  }

  private async handleShowMenu(event: Event, item: IPreviewData) {
    if (!event.target) return

    const list = typeof this.operateList === 'function'
      ? await this.operateList(item)
      : this.operateList

    if (!list || !list.length) return

    this.menuInstance.$props.list = list

    this.previewItem = item
    this.menuInstance.$off('click', this.handleMenuClick)
    this.menuInstance.$on('click', this.handleMenuClick)

    this.popoverInstance = this.$bkPopover(event.target, {
      content: this.menuInstance.$el,
      trigger: 'manual',
      arrow: false,
      theme: 'light ip-selector',
      maxWidth: 280,
      offset: '0, 5',
      sticky: true,
      duration: [275, 0],
      interactive: true,
      boundary: 'window',
      placement: 'bottom',
      onHidden: () => {
        this.popoverInstance && this.popoverInstance.destroy()
        this.popoverInstance = null
      }
    })
    this.popoverInstance.show()
  }

  private handleMouseDown(e: MouseEvent) {
    const node = e.target as HTMLElement
    const parentNode = node.parentNode as HTMLElement

    if (!parentNode) return

    const nodeRect = node.getBoundingClientRect()
    const rect = parentNode.getBoundingClientRect()
    document.onselectstart = function () {
      return false
    }
    document.ondragstart = function () {
      return false
    }
    const handleMouseMove = (event: MouseEvent) => {
      const [min, max] = this.range
      const newWidth = rect.right - event.clientX + nodeRect.width
      if (newWidth < min) {
        this.preWidth = 0
      } else {
        this.preWidth = Math.min(newWidth, max)
      }
      this.handleWidthChange()
    }
    const handleMouseUp = () => {
      document.body.style.cursor = ''
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.onselectstart = null
      document.ondragstart = null
    }
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }
}
</script>

<style>
  .ip-selector-theme {
    /* stylelint-disable-next-line declaration-no-important */
    padding: 0 !important;
  }
  </style>
  <style lang="scss" scoped>
  :deep(.bk-collapse-item) {
    margin-bottom: 10px;

    .bk-collapse-item-header {
      padding: 0;
      height: 24px;
      line-height: 24px;

      &:hover {
        color: #63656e;
      }
    }
  }

  .selector-preview {
    border: 1px solid #dcdee5;
    background: #f5f6fa;
    position: relative;
    height: 100%;

    &-title {
      color: #313238;
      font-size: 14px;
      line-height: 22px;
      padding: 10px 24px;
    }

    &-content {
      height: calc(100% - 42px);
      overflow: auto;

      .collapse-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 24px 0 18px;

        &-left {
          display: flex;
          align-items: center;
          font-size: 12px;

          .num {
            color: #3a84ff;
            font-weight: 700;
            padding: 0 2px;
          }
        }

        &-right {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          border-radius: 2px;

          &:hover {
            background: #e1ecff;
            color: #3a84ff;
          }

          i {
            font-size: 18px;
            outline: 0;
          }
        }
      }

      .collapse-content {
        padding: 0 14px;
        margin-top: 6px;

        &-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          height: 32px;
          line-height: 32px;
          background: #fff;
          padding: 0 12px;
          border-radius: 2px;
          box-shadow: 0px 1px 2px 0px rgba(0,0,0,.06);
          margin-bottom: 2px;

          .left {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
          }

          .right {
            cursor: pointer;
            color: #3a84ff;

            i {
              font-weight: 700;
            }
          }
        }
      }

      .icon-angle-right {
        font-size: 24px;
        transition: transform .2s ease-in-out;

        &.expand {
          transform: rotate(90deg);
        }
      }
    }
  }

  .drag {
    position: absolute;
    left: 0px;
    top: calc(50% - 10px);
    width: 6px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-items: center;
    outline: 0;

    &::after {
      content: ' ';
      height: 18px;
      width: 0;
      border-left: 2px dotted #c4c6cc;
      position: absolute;
      left: 2px;
    }

    &:hover {
      cursor: col-resize;
    }
  }
</style>
