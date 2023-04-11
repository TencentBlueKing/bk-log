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

import { Component as tsc } from 'vue-tsx-support';
import { Component, Ref, Emit, Prop, Watch } from 'vue-property-decorator';
import { Input } from 'bk-magic-vue';
import { IFavoriteItem } from '../collect-index';
import './manage-input.scss';

interface IProps {
  favoriteData?: IFavoriteItem;
}
@Component
export default class ManageInput extends tsc<IProps> {
  @Prop({ type: Object, default: () => ({}) }) favoriteData: IFavoriteItem;
  @Ref() inputRef: any;

  inputStr = '';

  @Watch('favoriteData.name', { immediate: true })
  handleWatchFavoriteName(str) {
    this.inputStr = str;
  }

  @Emit('change')
  handleChangeFavoriteName() {
    return this.inputStr;
  }
  isClick = false;
  handleClickInput() {
    this.isClick = true;
    this.$nextTick(() => {
      this.inputRef.focus();
    });
  }
  blurInput() {
    this.isClick = false;
    this.handleChangeFavoriteName();
  }
  render() {
    return (
      <div class="manage-input" onClick={this.handleClickInput}>
        {this.isClick ? (
          <Input
            vModel={this.inputStr}
            ref="inputRef"
            onBlur={this.blurInput}
            maxlength={30}
          ></Input>
        ) : (
          <div class="collect-box">
            <span class="collect-name" v-bk-overflow-tips>{this.inputStr}</span>
            {!this.favoriteData.is_active ? (
              <span v-bk-tooltips={{ content: this.$t('数据源不存在'), placement: 'right' }}>
                <span class="bk-icon log-icon icon-shixiao"></span>
              </span>
            ) : undefined}
          </div>
        )}
      </div>
    );
  }
}
