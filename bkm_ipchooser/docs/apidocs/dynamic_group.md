# [分组] 动态相关接口

**公共参数**

**scope**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| scope_type | String | Yes | 资源范围类型, 枚举, [biz|space] |
| scope_id | String | Yes | 资源范围 ID |

<hr>

## [API] dynamic_groups (拉取动态分组列表)

用法: 获取动态分组列表

路径: /ipchooser/dynamic_group/groups/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
}
```

### 返回示例

```json
{
    "result": true,
    "data": {
        "count": 2,
        "groups": [
            {
                "id": "aaaaaaaaaaaa",
                "name": "test1",
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2",
                    "bk_biz_id": 2
                },
                "count": 27,
                "is_latest": false,
                "object_id": "host",
                "object_name": "主机"
            },
            {
                "id": "bbbbbbbbbbb",
                "name": "test2",
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2",
                    "bk_biz_id": 2
                },
                "count": 29,
                "is_latest": false,
                "object_id": "host",
                "object_name": "主机"
            }
        ]
    },
    "code": 0,
    "message": ""
}
```

<hr>

## [API] execute_dynamic_group (获取动态分组下节点)

用法: 执行动态分组, 获取对应主机

路径: /ipchooser/dynamic_group/execute/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| dynamic_group_id | String | Yes | 动态分组ID |
| start | Int | No | 分页参数, start |
| page_size | Int | No | 分页参数, page_size |

### 请求参数示例

```json
{
    "scope_list": [
        {
            "scope_type": "biz",
            "scope_id": "2"
        }
    ],
    "dynamic_group_id": "aaaaaaaaaaa",
    "start": 0,
    "page_size": 20
}
```

### 返回示例

```json
{
    "result": true,
    "data": {
        "start": 0,
        "page_size": 1,
        "count": 29,
        "child": [
            {
                "bk_cloud_id": 0,
                "bk_host_id": 1,
                "bk_host_innerip": "bk_host_innerip",
                "bk_host_name": "bk_host_name",
                "bk_os_name": "linux centos",
                "bk_os_type": "1",
                "status": 1
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
