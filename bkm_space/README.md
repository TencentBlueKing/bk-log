# BKM_SPACE - 蓝鲸监控项目空间工具集

## 1. 功能

### 生效范围
- 基于 Django MiddleWare 请求和响应参数注入
- 基于 DRF Serializer 校验参数注入

### 注入逻辑
针对参数结构进行深度优先遍历 (默认最大遍历深度为5)
- 如果存在 `bk_biz_id`，且不存在 `space_uid`，则注入 `space_uid`
- 如果存在 `space_uid`，且不存在 `bk_biz_id`，则注入 `bk_biz_id`

## 2. 使用方式

1. `settings.INSTALLED_APPS` 增加应用 `bkm_space` ，无顺序要求
2. `settings.MIDDLEWARE` 增加中间件 `bkm_space.middleware.ParamInjectMiddleware`，无顺序要求


## 3. Settings

| 字段                              | 说明                                                         | 默认值                           |
| --------------------------------- | ------------------------------------------------------------ | -------------------------------- |
| BKM_SPACE_INJECT_REQUEST_ENABLED  | 请求参数是否需要注入空间属性                                 | `True`                           |
| BKM_SPACE_INJECT_RESPONSE_ENABLED | 返回参数是否需要注入空间属性                                 | `False`                          |
| BKM_SPACE_API_CLASS               | 项目空间API类模块路径，使用方需要基于抽象类 `bkm_space.api.AbstractSpaceApi` 实现 | `bkm_space.api.AbstractSpaceApi` |



