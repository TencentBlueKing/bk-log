# [分组] 拓扑相关接口

**公共参数**

**scope**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| scope_type | String | Yes | 资源范围类型, 枚举, [biz|space] |
| scope_id | String | Yes | 资源范围 ID |
| bk_biz_id | Int | Yes | 业务 ID, 最后只会使用这个 |

<hr>

## [API] trees (批量获取含各节点主机数量的拓扑树)

用法: 动态拓扑/静态拓扑(fetchTopologyHostCount)

路径: /api/v1/ipchooser/topo/trees/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- |------| ---------------------------------------------- |
| all_scope  | Bool | No   | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes  | 要获取拓扑结构的资源范围数组                   |

### 请求参数示例

```json
{
  "scope_list": [{ "scope_type": "biz", "scope_id": "2" }]
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
            "instance_id": 2,
            "instance_name": "蓝鲸",
            "object_id": "biz",
            "object_name": "业务",
            "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
            "child": [
                {
                    "instance_id": 1,
                    "instance_name": "测试集群",
                    "object_id": "set",
                    "object_name": "集群",
                    "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
                    "child": [
                        {
                            "instance_id": 281,
                            "instance_name": "空闲机模块",
                            "object_id": "module",
                            "object_name": "模块",
                            "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
                            "child": [],
                            "count": 4,
                        }
                    ],
                    "count": 4,
                },
                {
                    "instance_id": 2,
                    "instance_name": "空闲机池",
                    "objectId": "set",
                    "object_name": "集群",
                    "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
                    "child": [
                        {
                            "instance_id": 3,
                            "instance_name": "空闲机",
                            "object_id": "module",
                            "object_name": "模块",
                            "child": [],
                            "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
                            "count": 92,
                        }
                    ],
                    "count": 92,
                },
            ],
            "count": 96,
        }
    ],
    "request_id": "226d141055aa98f724a03cdce843cae1",
}
```

<hr>

## [API] query_path (查询多个节点拓扑路径)

用法: 动态拓扑获取节点(fetchNodesQueryPath)

路径: /api/v1/ipchooser/topo/query_path/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- |------| ---------------------------------------------- |
| all_scope  | Bool | No   | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| scope_list | List | Yes  | 要获取拓扑结构的资源范围数组                   |
| node_list | List | No       | 节点列表 |

**node**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| object_id | String | No | 节点类型 ID |
| instance_id | String | No | 节点实例 ID |
| scope | | | 参考公共参数 scope |


### 请求参数示例

```json
{
  "node_list": [
    {
      "meta": { "scope_type": "biz", "scope_id": 2, "bk_biz_id": 2 },
      "object_id": "set",
      "instance_id": "144"
    }
  ],
  "start": 0,
  "page_size": 20
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
        [
            {"meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}, "instance_id": 2, "instance_name": "蓝鲸", "objectId": "biz", "object_name": "业务"},
            {"meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}, "instance_id": 3, "instance_name": "测试", "object_id": "set", "object_name": "集群"},
        ]
    ],
    "request_id": "c13b9418f45d3af0",
}
```

<hr>

## [API] query_hosts (根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息)

用法: 静态拓扑获取主机(fetchTopologyHostsNodes)

路径: /api/v1/ipchooser/topo/query_hosts/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段      | 类型 | 是否必选 | 描述     |
| --------- | ---- | -------- | -------- |
| node_list | List | No       | 节点列表 |

**node**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| object_id | String | No | 节点类型 ID |
| instance_id | String | No | 节点实例 ID |
| host_id | String | No | 主机 ID，优先取 `host_id`，否则取 `ip` + `cloud_id` |
| scope | | | 参考公共参数 scope |

### 请求参数示例

```json
{

  "node_list": [
    {
      "meta": { "scope_type": "biz", "scope_id": 2, "bk_biz_id": 2 },
      "object_id": "set",
      "instance_id": "144"
    }
  ],
  "start": 0,
  "page_size": 20
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": {
        "start": 0,
        "page_size": 10,
        "total": 1,
        "data": [
            {
                "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2},
                "host_id": 355675,
                "ip": "127.0.0.1",
                "ipv6": "",
                "host_name": "",
                "alive": 0,
                "cloud_area": {"id": 2, "name": "ababababa"},
                "biz": {"id": 2, "name": "蓝鲸"},
                "os_name": "",
            }
        ],
    },
    "request_id": "c17ae1b76dc47a86",
}
```

<hr>

## [API] query_host_id_infos (根据多个拓扑节点与搜索条件批量分页查询所包含的主机ID信息)

用法: 全选, 跨页查询(fetchTopologyHostIdsNodes)

路径: /api/v1/ipchooser/topo/query_host_id_infos/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段      | 类型 | 是否必选 | 描述     |
| --------- | ---- | -------- | -------- |
| node_list | List | No       | 节点列表 |

**node**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| object_id | String | No | 节点类型 ID |
| instance_id | String | No | 节点实例 ID |
| host_id | String | No | 主机 ID，优先取 `host_id`，否则取 `ip` + `cloud_id` |
| scope | | | 参考公共参数 scope |

### 请求参数示例

```json
{
  "node_list": [
    {
      "meta": { "scope_type": "biz", "scope_id": 2, "bk_biz_id": 2 },
      "object_id": "set",
      "instance_id": "144"
    }
  ],
  "start": 0,
  "page_size": 20
}
```

### 返回示例

```json
{
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": {
      "start": 0, "pageSize": -1, "total": 1, "data": [{"meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}, "host_id": 355675}]
    },
    "request_id": "b96a0c97063469d8ac8ddceef64e73bc",
}
```

## [API] agent_statistics (获取多个拓扑节点的主机Agent状态统计信息)

用法: 动态拓扑/静态拓扑/服务模板/集群模板 均可用, 获取节点Agent状态(fetchHostAgentStatisticsNodes)

路径: /api/v1/ipchooser/topo/agent_statistics/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段      | 类型 | 是否必选 | 描述     |
| --------- | ---- | -------- | -------- |
| node_list | List | No       | 节点列表 |

**node**
| 字段 | 类型 | 是否必选 | 描述 |
|-----------|------------|--------|-------------------------|
| object_id | String | No | 节点类型 ID |
| instance_id | String | No | 节点实例 ID |
| meta | Dict | No | 元数据meta |

### 请求参数示例

```json
{
  "node_list": [
    {
      "meta": { "scope_type": "biz", "scope_id": 2, "bk_biz_id": 2 },
      "object_id": "set",
      "instance_id": "144"
    }
  ],
  "start": 0,
  "page_size": 20
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
            "node": {"meta": { "scope_type": "biz", "scope_id": 2, "bk_biz_id": 2 }, "instance_id": 2, "object_id": "biz"},
            "agent_statistics": {"alive_count": 100, "not_alive_count": 200, "total_count": 300},
        }
    ],
    "request_id": "c17ae1b76dc47a86",
}
```
