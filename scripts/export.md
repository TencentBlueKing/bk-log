# 导出数据工具(采集项和索引集)

## 数据来源
可以直连数据库导出, 也可以联系运维导出数据之后, 在本地source数据之后导出
```bash
mysqldump -h [host] -P [port] -u [username] -p [password] --databases bk_nodeman --tables node_man_subscriptionstep > bk_nodeman.sql
mysqldump -h [host] -P [port] -u [username] -p [password] --databases bk_log_search --tables log_databus_collectorconfig log_search_projectinfo log_search_logindexset log_search_logindexsetdata > bk_log_search.sql
```

## 导出表

- [节点管理] `node_man_subscriptionstep`
- [日志平台] `log_databus_collectorconfig`
- [日志平台] `log_search_projectinfo`
- [日志平台] `log_search_logindexset`
- [日志平台] `log_search_logindexsetdata`

## 配置文件`config.yaml`
```yaml
bk_nodeman:
 db: bk_nodeman
 host: 127.0.0.1
 port: 3306
 user: root
 password: password
 charset: utf8

bk_log_search:
 db: bk_log_search
 host: 127.0.0.1
 port: 3306
 user: root
 password: password
 charset: utf8
```

## 依赖
```bash
pip install pymysql
```

## 执行脚本
```bash
python export.py --config config.yaml
```
