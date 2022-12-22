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
| dynamic_group_list | List | No | 指定动态分组列表, 不填返回所有 |

dynamic_group

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| id  | Int | Yes       | 动态分组ID |
| meta | Dict | No      | 元数据                   |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }],
  "dynamic_group_list": [
    {
        "meta": {
            "scope_type": "biz",
            "scope_id": "2"
        },
        "id": "aaaaaaaaaaaa"
      }
  ]
}
```

### 返回示例

```json
{
    "result": true,
    "data": [
        {
            "id": "aaaaaaaaaaaa",
            "name": "test1",
            "meta": {
                "scope_type": "biz",
                "scope_id": "2",
                "bk_biz_id": 2
            },
            "count": 27,
            "last_time": "2021-12-07T03:45:17.589Z",
            "object_id": "host",
            "object_name": "主机"
        }
    ]
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
        "total": 29,
        "data": [
            {
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2"
                },
                "cloud_id": 0,
                "host_id": 1,
                "ip": "bk_host_innerip",
                "host_name": "bk_host_name",
                "os_name": "linux centos",
                "alive": 1
            }
        ]
    },
    "code": 0,
    "message": ""
}
```

<hr>

## [API] agent_statistics (获取动态分组下所有主机的Agent状态)

用法: 执行动态分组, 获取对应主机Agent状态

路径: /ipchooser/dynamic_group/agent_statistics/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| all_scope  | Bool | NO       | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes      | 要获取拓扑结构的资源范围数组                   |
| dynamic_group_list | List | No | 指定动态分组列表, 不填返回所有 |

dynamic_group

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| id  | Int | Yes       | 动态分组ID |
| meta | Dict | No      | 元数据                   |

### 请求参数示例

```json
{
    "scope_list": [
        {
            "scope_type": "biz",
            "scope_id": "2"
        }
    ],
    "dynamic_group_list": [
        {
            "meta": {
                "scope_type": "biz",
                "scope_id": "2"
            },
            "id": "aaaaaaa"
        }
    ]
}
```

### 返回示例

```json
{
    "result": true,
    "data": [
        {
            "dynamic_group": {
                "id": "aaaaaaa",
                "name": "aaaaaaa",
                "meta": {
                    "scope_type": "biz",
                    "scope_id": "2",
                    "bk_biz_id": 2
                }
            },
            "agent_statistics": {
                "total_count": 29,
                "alive_count": 16,
                "not_alive_count": 13
            }
        }
    ],
    "code": 0,
    "message": ""
}
```

<hr>

