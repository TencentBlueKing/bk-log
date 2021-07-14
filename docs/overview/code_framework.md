## 蓝鲸日志平台（BK-LOG）代码结构

蓝鲸日志平台（BK-LOG）是基于 blueapps + Django 开发的日志类SaaS服务，通过blueapps可快速开发基于蓝鲸体系的应用。

```
 ./                                # 日志平台根目录
 |-- apps                          # 后台业务逻辑
     |-- api                       # 蓝鲸平台接口适配
     |-- grafana                   # 仪表盘
     |-- iam                       # 权限中心集成
     |-- log_databus               # 日志采集模块
     |-- log_esquery               # 统一查询模块
     |-- log_extract               # 日志提取模块
     |-- log_measure               # 日志运营指标
     |-- log_search                # 日志检索模块
     |-- log_trace                 # 调用链UI
     |-- tests                     # 各模块测试用例
 |-- config                        # 应用配置      
 |-- static                        # 前端静态目录      
 |-- web                           # 前端源码      
 |-- manage.py                     # Django 工程 manage  
 |-- settings.py                   # Django工程 settings      
 |-- urls.py                       # Django工程主路由 URL 配置
 |-- wsgi.py                       # WSGI 配置
```