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
 * 收藏详情
 */
const getFavorite = {
  url: '/search/favorite/:id/',
  method: 'get',
};
/**
 * 收藏列表
 */
const getFavoriteList = {
  url: '/search/favorite/',
  method: 'get',
};
/**
 * 分组收藏列表
 */
const getFavoriteByGroupList = {
  url: '/search/favorite/list_by_group/',
  method: 'get',
};
/**
 * 新建收藏
 */
const createFavorite = {
  url: '/search/favorite/',
  method: 'post',
};
/**
 * 更新收藏
 */
const updateFavorite = {
  url: '/search/favorite/:id/',
  method: 'put',
};
/**
 * 删除收藏
 */
const deleteFavorite = {
  url: '/search/favorite/:favorite_id/',
  method: 'delete',
};
/**
 * 组列表
 */
const getGroupList = {
  url: '/search/favorite_group/',
  method: 'get',
};
/**
 * 新建组
 */
const createGroup = {
  url: '/search/favorite_group/',
  method: 'post',
};
/**
 * 更新组名
 */
const updateGroupName = {
  url: '/search/favorite_group/:group_id/',
  method: 'put',
};
/**
 * 解散组
 */
const deleteGroup = {
  url: '/search/favorite_group/:group_id/',
  method: 'delete',
};
/**
 * 获取检索语句字段
 */
const getSearchFields = {
  url: '/search/favorite/get_search_fields/',
  method: 'post',
};
/**
 * 检索语句字段换成keyword
 */
const getGenerateQuery = {
  url: '/search/favorite/generate_query/',
  method: 'post',
};
/**
 * 批量修改收藏
 */
const batchFavoriteUpdate = {
  url: '/search/favorite/batch_update/',
  method: 'post',
};
/**
 * 批量删除收藏
 */
const batchFavoriteDelete = {
  url: '/search/favorite/batch_delete/',
  method: 'post',
};
/**
 * 组排序
 */
const groupUpdateOrder = {
  url: '/search/favorite_group/update_order/',
  method: 'post',
};
/**
 * 检索语句语法检测
 */
const checkKeywords = {
  url: '/search/favorite/inspect/',
  method: 'post',
};

export {
  getFavorite,
  getFavoriteList,
  getFavoriteByGroupList,
  createFavorite,
  updateFavorite,
  deleteFavorite,
  getGroupList,
  createGroup,
  updateGroupName,
  deleteGroup,
  getSearchFields,
  getGenerateQuery,
  batchFavoriteUpdate,
  batchFavoriteDelete,
  groupUpdateOrder,
  checkKeywords,
};
