# [分组] 模板相关接口

**公共参数**

**scope**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| scope_type | String | Yes | 资源范围类型, 枚举, [biz|space] |
| scope_id | String | Yes | 资源范围 ID |
| bk_biz_id | Int | Yes | 业务 ID, 最后只会使用这个 |

<hr>

## [API] templates (拉取模板列表)

用法: 获取服务模板/集群模板列表

路径: /api/v1/ipchooser/template/templates/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| template_type | String | Yes | 模板类型, 服务模板(SET_TEMPLATE), 集群模板(SERVICE_TEMPLATE) |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "template_type": "SET_TEMPLATE"
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
      {
        "id": 41,
        "name": "TEMPLATE_1",
        "template_type": "SET_TEMPLATE",
        "meta": {
            "scope_type": "biz",
            "scope_id": "2",
            "bk_biz_id": 2
        }
      },
    ],
    "request_id": "226d141055aa98f724a03cdce843cae1",
}
```

<hr>

## [API] nodes (获取模板下各个节点)

用法: 获取服务模板/集群模板 节点信息

路径: /api/v1/ipchooser/template/nodes/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| template_type | String | Yes | 模板类型, 服务模板(SET_TEMPLATE), 集群模板(SERVICE_TEMPLATE) |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "template_type": "SET_TEMPLATE"
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
      {
        "instance_id": 41,
        "instance_name": "set_name_1",
        "template_id": 1,
        "object_id": "set",
        "object_name": "集群",
        "meta": {
            "scope_type": "biz",
            "scope_id": "2",
            "bk_biz_id": 2
        }
      },
    ],
    "request_id": "226d141055aa98f724a03cdce843cae1",
}
```

<hr>

## [API] agent (获取模板下各个节点的Agent状态)

用法: 获取服务模板/集群模板 节点Ggent状态信息

路径: /api/v1/ipchooser/template/agent/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| template_type | String | Yes | 模板类型, 服务模板(SET_TEMPLATE), 集群模板(SERVICE_TEMPLATE) |
| template_ids | List | No | 模板ID列表 |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "template_type": "SET_TEMPLATE",
  "template_ids": [1, 2]
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
      {
        "template_id": 1,
        "template_name": "TEMPLATE_NAME_1",
        "meta": {
            "scope_type": "biz",
            "scope_id": "2",
            "bk_biz_id": 2
        },
        "child": [
            {
                "instance_id": 1,
                "instance_name": "SET_NAME_1",
                "template_id": 1,
                "object_id": "set",
                "object_name": "集群",
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2",
                    "bk_biz_id": 2
                },
                "count": 0,
                "agent_error_count": 0
            }
        ]
      }
    ],
    "request_id": "226d141055aa98f724a03cdce843cae1",
}
```
