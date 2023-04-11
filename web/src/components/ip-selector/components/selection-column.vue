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
  <div class="selection-header">
    <bk-checkbox
      :value="value === 2"
      :indeterminate="value === 1"
      :class="{
        'all-check': checkType.active === 'all',
        'indeterminate': value === 1 && checkType.active === 'all'
      }"
      :disabled="disabled"
      @change="handleCheckChange">
    </bk-checkbox>
    <i :class="[
         'bk-icon selection-header-icon',
         { disabled: disabled },
         isDropDownShow ? 'icon-angle-up' : 'icon-angle-down']"
       @click="handleShowMenu"></i>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref, Emit, Watch, Model } from 'vue-property-decorator'
import Menu from './menu.vue'
import { CheckType, CheckValue, IMenu } from '../types/selector-type'

// 表格自定义check列
@Component({ name: 'selection-column' })
export default class SelectionColumn extends Vue {
  // 0 未选 1 半选 2 全选
  @Model('update-value', { default: 0, type: Number }) private readonly value!: CheckValue

  // @Prop({ default: 0, type: Number }) private readonly value!: CheckValue
  @Prop({ default: false, type: Boolean }) private readonly disabled!: boolean
  @Prop({ default: false, type: Boolean }) private readonly loading!: boolean
  @Prop({ default: 'current', type: String }) private readonly defaultActive!: CheckType

  @Ref('popover') private readonly popover: any

  private menuInstance = new Menu().$mount()
  private popoverInstance: any = null
  private checkType: {
    active: CheckType
    list: IMenu[]
  } = {
    active: this.defaultActive,
    list: []
  }
  private isDropDownShow = false

  // 取消勾选时重置checkType
  // @Watch('value')
  // private handleValueChange(v: CheckValue) {
  //   v === 0 && (this.checkType.active = 'current')
  // }

  @Watch('defaultActive')
  private handleDefaultActiveChange() {
    this.checkType.active = this.defaultActive
  }

  private created() {
    this.checkType.list = [
      {
        id: 'current',
        label: this.$t('本页全选')
      },
      {
        id: 'all',
        label: this.$t('跨页全选')
      }
    ]
  }

  private beforeDestroy() {
    if (this.menuInstance) {
      this.menuInstance.$off('click', this.handleMenuClick)
      this.menuInstance.$destroy()
    }
  }
  /**
   * 全选操作
   * @param {String} type 全选类型：1. 本页权限 2. 跨页全选
   */
  @Emit('change')
  private handleCheckAll(type: CheckType) {
    this.popover && this.popover.instance.hide()
    this.checkType.active = type
    this.handleUpdateValue(2)
    return {
      value: 2,
      type
    }
  }
  /**
   * 勾选事件
   */
  @Emit('change')
  private handleCheckChange(value: boolean) {
    // if (!value) {
    //   this.checkType.active = 'current'
    // }
    this.handleUpdateValue(value ? 2 : 0)
    return {
      value: value ? 2 : 0,
      type: this.checkType.active
    }
  }

  @Emit('update-value')
  private handleUpdateValue(v: CheckValue) {
    return v
  }

  private handleMenuClick(menu: IMenu) {
    this.handleCheckAll(menu.id as CheckType)
    this.popoverInstance && this.popoverInstance.hide()
  }

  private handleShowMenu(event: Event) {
    if (!event.target || this.disabled) return

    this.menuInstance.$props.list = this.checkType.list
    this.menuInstance.$props.align = 'center'

    this.menuInstance.$off('click', this.handleMenuClick)
    this.menuInstance.$on('click', this.handleMenuClick)
    if (!this.popoverInstance) {
      this.popoverInstance = this.$bkPopover(event.target, {
        content: this.menuInstance.$el,
        trigger: 'manual',
        arrow: false,
        theme: 'light ip-selector',
        maxWidth: 280,
        offset: '30, 0',
        sticky: true,
        duration: [275, 0],
        interactive: true,
        boundary: 'window',
        placement: 'bottom',
        onHidden: () => {
          this.isDropDownShow = false
        },
        onShow: () => {
          this.isDropDownShow = true
        }
      })
    }

    this.popoverInstance.show()
  }
}
</script>

<style lang="scss" scoped>
  .selection-header {
    .all-check {
      :deep(.bk-checkbox) {
        /* stylelint-disable-next-line declaration-no-important */
        background-color: #fff !important;

        &::after {
          /* stylelint-disable-next-line declaration-no-important */
          border-color: #3a84ff !important;
        }
      }
    }

    .indeterminate {
      :deep(.bk-checkbox) {
        &::after {
          /* stylelint-disable-next-line declaration-no-important */
          background: #3a84ff !important;
        }
      }
    }

    &-icon {
      position: relative;
      top: 3px;
      font-size: 20px;
      cursor: pointer;
      color: #63656e;
      outline: 0;

      &.disabled {
        color: #dcdee5;
      }
    }
  }
</style>
