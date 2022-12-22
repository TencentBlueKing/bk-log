# [分组] 主机相关接口

**公共参数**

**scope**
| 字段 | 类型 | 是否必选 | 描述  |
|-----------|------------|--------|-------------------------|
| scope_type | String | Yes | 资源范围类型, 枚举, [biz|space] |
| scope_id | String | Yes | 资源范围ID |
| bk_biz_id | Int | No | 业务ID, 最后只会使用这个 |

<hr>

## [API] check (检查节点)

用法: 用于全局根据host_id获取主机信息(fetchHostCheck)

路径: /api/v1/ipchooser/host/check/

HTTP请求方式: `POST`, `application/json`

### 请求参数

| 字段 | 类型 | 是否必选 | 描述  |
|-----------|------------|------|-------------------------|
| scope_list | List | Yes  | 要获取拓扑结构的资源范围数组 |
| all_scope | Bool | No   | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| ip_list | List | No   | IPv4，支持的输入格式：`cloud_id:ip` / `ip` |
| ipv6_list | List | No   | IPv6，支持的输入格式：`cloud_id:ipv6` / `ipv6` |
| key_list | List | No   | 关键字，解析出的`主机名`、`host_id` 等关键字信息 |


### 请求参数示例

```json
{
  "scope_list": [{"scope_type": "biz", "scope_id": "2"}],
  "ip_list": ["0:127.0.0.1"],
  "ipv6_list": ["0:A:A:A:A:A:A"],
  "key_list": ["11111", "hahaha"],
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

## [API] details (根据主机关键信息获取机器详情信息)

用法: 获取静态拓扑根据主机host_id获取主机详情(fetchHostsDetails)

路径: /api/v1/ipchooser/host/details/

HTTP请求方式: `POST`, `application/json`

### 请求参数

| 字段 | 类型 | 是否必选 | 描述  |
|-----------|------------|------|-------------------------|
| scope_list | List | Yes  | 要获取拓扑结构的资源范围数组 |
| all_scope | Bool | No   | 是否获取所有资源范围的拓扑结构，默认为 `false` |
| host_list | List | No   | 主机列表 |

**host**
| 字段 | 类型 | 是否必选 | 描述  |
|-----------|------------|--------|-------------------------|
| cloud_id | Int | No | 云区域ID |
| ip | String | No | IPv4 协议下的主机IP |
| host_id | String | No | 主机 ID，优先取 `host_id`，否则取 `ip` + `cloud_id` |
| meta | Dict | No | Meta元数据 |


### 请求参数示例

```json
{
  "scope_list": [{"scope_type": "biz", "scope_id": "2"}],
  "host_list": [
    {
      "host_id": 1, "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}
    },
    {
      "ip": "127.0.0.1", "cloud_id": 0, "meta": {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}
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
            "meta": {
                "scope_type": "biz",
                "scope_id": "2",
                "bk_biz_id": 2
            },
            "host_id": 1,
            "ip": "10.0.1.7",
            "ipv6": "",
            "cloud_id": 0,
            "cloud_vendor": "",
            "agent_id": "",
            "host_name": "host_name",
            "os_name": "1",
            "alive": 1,
            "cloud_area": {
                "id": 0,
                "name": "default area"
            },
            "biz": {
                "id": 2,
                "name": "蓝鲸"
            },
            "bk_mem": 32011,
            "bk_disk": 245,
            "bk_cpu": 8
        }
    ],
    "code": 0,
    "message": ""
}
```
