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
        "last_time": "2021-09-07T04:51:51.51Z",
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
| template_id | Int | Yes | 模板ID |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "template_type": "SET_TEMPLATE",
  "template_id": 1
}
```

### 返回示例

```json
{
    "result": true,
    "data": {
        "count": 1,
        "nodes": [
            {
                "instance_id": 1,
                "instance_name": "AAA",
                "template_id": 1,
                "object_id": "set",
                "object_name": "集群",
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2",
                    "bk_biz_id": 2
                },
                "node_path": "A/B/C",
                "total_count": 1,
                "not_alive_count": 0,
                "alive_count": 1
            }
        ]
    },
    "code": 0,
    "message": ""
}
```

<hr>

## [API] hosts (获取模板下各个主机)

用法: 获取服务模板/集群模板 主机

路径: /api/v1/ipchooser/template/hosts/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| template_type | String | Yes | 模板类型, 服务模板(SET_TEMPLATE), 集群模板(SERVICE_TEMPLATE) |
| template_id | Int | Yes | 模板ID |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "template_type": "SET_TEMPLATE",
  "template_id": 1
}
```

### 返回示例

```json
{
    "result": true,
    "data": {
        "count": 1,
        "hosts": [
            {
                "bk_cloud_id": 0,
                "bk_host_id": 1,
                "bk_host_innerip": "bk_host_innerip",
                "bk_host_name": "bk_host_name",
                "node_id": 160,
                "node_name": "node_name",
                "status": 1
            }
        ]
    },
    "code": 0,
    "message": ""
}
```
