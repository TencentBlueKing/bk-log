# 数据导入工具(采集项和索引集)

## PIP依赖(已在requirements.txt中)
pip install pymysql

## 日志resource映射表

DB: sg_migration

Table: bk_log_search_resource_mapping

Fields:

| 字段名 | 字段含义    | 字段类型 |
| --- |---------|------|
| id | 主键      | 整数   |
| bk_biz_id | 业务ID    | 整数   |
| origin_bk_biz_id | 原始业务ID  | 整数   |
| index_set_id | 索引集ID   | 整数   |
| origin_index_set_id | 原始索引集ID | 整数   |
| space_uid | 空间ID    | 字符串  |
| status | 状态      | 字符串  |
| details | 迁移详情    | text |

如果不存在该表, 请执行以下SQL创建表:

```sql
CREATE TABLE `bk_log_search_resource_mapping` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bk_biz_id` int NOT NULL,
  `origin_bk_biz_id` int NOT NULL,
  `index_set_id` int DEFAULT 0,
  `origin_index_set_id` int NOT NULL,
  `space_uid` varchar(255) NOT NULL,
  `status` varchar(32) NOT NULL,
  `details` text ,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
```

## 参数说明

| 参数名                                    | 参数含义                                              | 是否必填 | 参数类型 | 默认值                                |
|----------------------------------------|---------------------------------------------------| --- | --- |------------------------------------|
| -e, --env                              | 需要导入的环境                                           | 是 | 无 | 无                                  |
| -b, --bk_biz_id                        | 需要导入的业务, 不传时导入所有的业务                               | 否 | 整数 | 0                                  |
| -c, --collector_config_data            | 需要导入的采集项数据, 默认为: log_databus_collectorconfig.json | 否 | 字符串 | "log_databus_collectorconfig.json" |
| --collector_config_id_list             | 需要导入的采集项ID, 不传时导入所有的采集项, 例如: 1,2                  | 否 | 字符串 | ""                                 |
| -i, --index_set_data                   | 需要导入的索引集数据, 默认为: log_search_logindexset.json      | 否 | 字符串 | "log_search_logindexset.json"      |
| --index_set_id_list                    | 需要导入的索引集ID, 不传时导入所有的索引集, 例如: 1,2,3                | 否 | 字符串 | ""                                 |
| --mysql_host                           | 公共数据库地址                                           | 否 | 字符串 | 无                                  |
| --mysql_port                           | 公共数据库端口                                           | 否 | 整数 | 3306                               |
| --mysql_user                           | 公共数据库用户                                           | 否 | 字符串 | "root"                             |
| --mysql_db                             | 公共数据库链接库名称                                        | 否 | 字符串 | "sg_migration"                     |
| --mysql_password                       | 公共数据库密码                                           | 否 | 字符串 | 无                                  |
| --env_offset_table                     | 环境映射表                                             | 否 | 无 | "cc_EnvIDOffset"                   |
| --env_biz_map_table                    | 业务映射表                                             | 否 | 无 | "cc_EnvBizMap"                     |
| --bk_log_search_resource_mapping_table | 日志平台映射表                                           | 否 | 无 | "bk_log_search_resource_mapping"   |
| -s, --storage_cluster_id               | 存储集群ID, 不传则使用系统分配的公共集群                            | 否 | 整数 | 0                                  |

## 使用示例
```bash
python manage.py migrate_tool --env=env_name --collector_config_data=log_databus_collectorconfig.json --mysql_host=127.0.0.1 --mysql_password=mysql_password
```
