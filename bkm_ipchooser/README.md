# BKM_IPCHOOSER - 蓝鲸监控IP选择器SDK

## 1. 功能

bkm_ipchooser 是一个 Django App，用于提供IP(V6)选择器统一API

## 2. 使用方式

1. `settings.INSTALLED_APPS` 增加应用 `bkm_ipchooser` ，无顺序要求
2. 在项目根目录的 `urls.py` 添加相应路由配置，如 `url(r"^api/v1/ipchooser/", include("bkm_ipchooser.urls"))`

## 3. Settings

| 字段                              | 说明                                                         | 默认值 |
| --------------------------------- | ------------------------------------------------------------ |-----|
| BKM_IPCHOOSER_BKAPI_CLASS               | 项目空间API类模块路径，使用方需要基于抽象类 `bkm_ipchooser.api.AbstractBkApi` 实现 | 不可用 |

## 4. AbstractBkApi 实现说明

```python
class AbstractBkApi(metaclass=abc.ABCMeta):

    @staticmethod
    def search_cloud_area(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def search_business(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def search_biz_inst_topo(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def get_biz_internal_module(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def find_host_topo_relation(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def list_biz_hosts(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def list_host_total_mainline_topo(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def get_agent_status(params: dict = None):
        raise NotImplementedError
```

`BKM_IPCHOOSER_BKAPI_CLASS` 需要继承以上基类实现这些静态方法，需要用到CMDB和GSE的API。实现时，请求参数和返回参数直接透传即可
