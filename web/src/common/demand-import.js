/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

/**
 * @file 按需引入 bk-magic-vue 组件
 * @author <>
 */

/* eslint-disable import/no-duplicates */

import Vue from 'vue';

import {
  bkAlert,
  bkBadge,
  bkButton,
  bkBigTree,
  bkCheckbox,
  bkCheckboxGroup,
  bkCol,
  bkCollapse,
  bkCollapseItem,
  bkContainer,
  bkDatePicker,
  bkDialog,
  bkDropdownMenu,
  bkException,
  bkForm,
  bkFormItem,
  bkInfoBox,
  bkInput,
  bkLoading,
  bkMessage,
  bkNavigation,
  bkNavigationMenu,
  bkNavigationMenuGroup,
  bkNavigationMenuItem,
  bkNotify,
  bkOption,
  bkOptionGroup,
  bkPagination,
  bkPopover,
  bkProcess,
  bkProgress,
  bkRadio,
  bkRadioGroup,
  bkRoundProgress,
  bkRow,
  bkSearchSelect,
  bkSelect,
  bkSideslider,
  bkSlider,
  bkSteps,
  bkSwitcher,
  bkTag,
  bkTab,
  bkTabPanel,
  bkTable,
  bkTableColumn,
  bkTableSettingContent,
  bkTagInput,
  bkTimePicker,
  bkTimeline,
  bkTransfer,
  bkTree,
  bkUpload,
  bkClickoutside,
  bkTooltips,
  bkSwiper,
  bkRate,
  bkAnimateNumber,
  bkVirtualScroll,
  bkOverflowTips,
  bkDivider,
  bkSpin,
} from 'bk-magic-vue';

// bkDiff 组件体积较大且不是很常用，因此注释掉。如果需要，打开注释即可
// import { bkDiff } from 'bk-magic-vue'

// components use
Vue.use(bkAlert);
Vue.use(bkBadge);
Vue.use(bkButton);
Vue.use(bkBigTree);
Vue.use(bkCheckbox);
Vue.use(bkCheckboxGroup);
Vue.use(bkCol);
Vue.use(bkCollapse);
Vue.use(bkCollapseItem);
Vue.use(bkContainer);
Vue.use(bkDatePicker);
Vue.use(bkDialog);
Vue.use(bkDropdownMenu);
Vue.use(bkException);
Vue.use(bkForm);
Vue.use(bkFormItem);
Vue.use(bkInput);
Vue.use(bkNavigation);
Vue.use(bkNavigationMenu);
Vue.use(bkNavigationMenuGroup);
Vue.use(bkNavigationMenuItem);
Vue.use(bkOption);
Vue.use(bkOptionGroup);
Vue.use(bkPagination);
Vue.use(bkPopover);
Vue.use(bkProcess);
Vue.use(bkProgress);
Vue.use(bkRadio);
Vue.use(bkRadioGroup);
Vue.use(bkRoundProgress);
Vue.use(bkRow);
Vue.use(bkSearchSelect);
Vue.use(bkSelect);
Vue.use(bkSideslider);
Vue.use(bkSlider);
Vue.use(bkSteps);
Vue.use(bkSwitcher);
Vue.use(bkTab);
Vue.use(bkTabPanel);
Vue.use(bkTable);
Vue.use(bkTableColumn);
Vue.use(bkTableSettingContent);
Vue.use(bkTag);
Vue.use(bkTagInput);
Vue.use(bkTimePicker);
Vue.use(bkTimeline);
Vue.use(bkTransfer);
Vue.use(bkTree);
Vue.use(bkUpload);
Vue.use(bkSwiper);
Vue.use(bkRate);
Vue.use(bkAnimateNumber);
Vue.use(bkVirtualScroll);
Vue.use(bkSpin);
// bkDiff 组件体积较大且不是很常用，因此注释了。如果需要，打开注释即可
// Vue.use(bkDiff)

// directives use
Vue.use(bkClickoutside);
Vue.use(bkTooltips);
Vue.use(bkLoading);
Vue.use(bkDivider);
bkOverflowTips.setDefaultProps({
  delay: [400, 0],
});
Vue.use(bkOverflowTips);

// Vue prototype mount
Vue.prototype.$bkInfo = bkInfoBox;
Vue.prototype.$bkMessage = bkMessage;
Vue.prototype.$bkNotify = bkNotify;
