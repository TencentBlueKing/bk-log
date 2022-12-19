# [分组] 配置相关接口

## [API] global (全局配置)

用法: 获取全局配置列表

路径: /api/v1/ipchooser/config/global/

HTTP 请求方式: `GET`

### 返回示例

```json
{
    "result": true,
    "data": {
        "CC_ROOT_URL": "http://cmdb.xxx.com"
    },
    "code": 0,
    "message": ""
}
```

<hr>

## [API] batch_get (拉取配置)

用法: 获取当前用户配置列表

路径: /api/v1/ipchooser/config/batch_get/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| module_list | List | No      | 要获取配置列表, 不传或传空表示获取所有配置列表                   |

### 请求参数示例

```json
{
    "module_list": []
}
```

### 返回示例

```json
{
    "result": true,
    "data": {
        "ipchooser": {
            "items": [
                "aa",
                "bb",
                "cc"
            ],
            "width": 1000,
            "height": 800
        }
    },
    "code": 0,
    "message": ""
}
```

<hr>

## [API] update_config (更新配置)

用法: 更新当前用户配置列表

路径: /api/v1/ipchooser/config/update_config/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| settingsMap | Dict | Yes      | 要更新的配置                   |

### 请求参数示例

```json
{
    "settingsMap": {
    	"ipchooser":{
            "width": 1000,
            "height": 800,
            "items": ["aa","bb","cc"]
        }
    }
}
```

### 返回示例

```json
{
    "result": true,
    "data": null,
    "code": 0,
    "message": ""
}
```

<hr>

## [API] batch_delete (删除配置)

用法: 删除当前用户配置列表

路径: /api/v1/ipchooser/config/batch_delete/

HTTP 请求方式: `POST`, `application/json`

### 请求参数

| 字段       | 类型 | 是否必选 | 描述                                           |
| ---------- | ---- | -------- | ---------------------------------------------- |
| module_list | List | No      | 要删除配置列表, 不传或传空表示删除所有配置列表                   |

### 请求参数示例

```json
{
    "module_list": []
}
```

### 返回示例

```json
{
    "result": true,
    "data": null,
    "code": 0,
    "message": ""
}
```

<hr>
