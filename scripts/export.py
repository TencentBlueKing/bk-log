import os
import argparse
import json
import yaml

from typing import List, Dict, Union, Any
from collections import defaultdict

import pymysql

from pymysql.cursors import SSDictCursor

BASE_DIR = os.getcwd()

# CC映射表
ENV_OFFSET_TABLE = "cc_EnvIDOffset"
ENV_BIZ_MAP_TABLE = "cc_EnvBizMap"

# 节点管理表名
NODEMAN_SUBSCRIPTION_STEP_TABLE = "node_man_subscriptionstep"
# 日志平台表名
LOG_DATABUS_COLLECTOR_CONFIG_TABLE = "log_databus_collectorconfig"
LOG_SEARCH_PROJECT_TABLE = "log_search_projectinfo"
LOG_SEARCH_INDEX_SET_TABLE = "log_search_logindexset"
LOG_SEARCH_INDEX_SET_DATA_TABLE = "log_search_logindexsetdata"


class Scenario(object):
    """
    接入场景
    """

    LOG = "log"
    BKDATA = "bkdata"
    ES = "es"


class Config:
    """配置文件"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path=config_path)

    @staticmethod
    def _load_config(config_path: str):
        with open(config_path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def __getitem__(self, item):
        return self.config[item]


def export(data: Union[List[Any], Dict[str, Any]] = None, filepath: str = None):
    """导出数据"""
    filepath = os.path.join(BASE_DIR, filepath)
    with open(filepath, "w") as _f:
        json.dump(data, _f, ensure_ascii=False, indent=4)
        _f.close()
    print(f"导出数据成功，文件路径：{filepath}")


class Database:
    def __init__(
        self, db: str, host: str, port: int = 3306, user: str = "root", password: str = "", charset: str = "utf8"
    ) -> None:
        self.conn = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset

    def connect(self) -> None:
        """连接数据库"""
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset,
            cursorclass=SSDictCursor,
        )

    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """执行SQL"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def get_tables(self) -> List[str]:
        """获取所有表名"""
        sql = "SHOW TABLES"
        return [i[f"Tables_in_{self.db}"] for i in self.execute_sql(sql)]

    def query_table(self, table_name: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """查询表数据"""
        if fields:
            fields = ",".join(fields)
        else:
            fields = "*"
        sql = f"SELECT {fields} FROM {table_name}"
        return [i for i in self.execute_sql(sql)]

    def desc_table(self, table_name: str) -> List[Dict[str, Any]]:
        """查询表结构"""
        sql = f"DESC {table_name}"
        return [i for i in self.execute_sql(sql)]

    def close(self) -> None:
        self.conn.close()


class Table:
    """表"""

    FIELDS = []

    def __init__(self, table_name: str = "", mysql_config: Dict[str, Any] = None) -> None:
        self.table_name = table_name
        self.db = self.init_database(mysql_config=mysql_config)
        self._datas: List[Dict[str, Any]] = []

    @staticmethod
    def init_database(mysql_config: Dict[str, Any]) -> Database:
        """初始化日志数据库连接"""
        db = Database(**mysql_config)
        db.connect()
        return db

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据"""
        raise NotImplementedError

    def query_data(self) -> None:
        """查询数据"""
        raise NotImplementedError

    def append_data(self, data: Dict[str, Any] = None):
        """添加数据"""
        if not data:
            return
        self._datas.append(data)

    def extend_datas(self, datas: List[Dict[str, Any]] = None):
        """添加多行数据"""
        self._datas.extend(datas)

    def export(self, filepath: str = None):
        """导出数据"""
        if not self._datas:
            self.query_data()
        if not filepath:
            filepath = f"{self.table_name}.json"
        export(data=self._datas, filepath=filepath)


class NodemanSubscriptionInfo(Table):
    """节点管理订阅信息表"""

    FIELDS = ["subscription_id", "step_id", "params"]

    def __init__(self, mysql_config: Dict[str, Any] = None) -> None:
        super().__init__(table_name=NODEMAN_SUBSCRIPTION_STEP_TABLE, mysql_config=mysql_config)

    def query_data(self) -> None:
        """查询数据"""
        sql = f"SELECT {','.join(self.FIELDS)} FROM {self.table_name} WHERE step_id='bkunifylogbeat'"
        for data in self.db.execute_sql(sql):
            self.append_data(data)

    @property
    def mapping(self):
        if not self._datas:
            self.query_data()
        return {i["subscription_id"]: {"id": i["step_id"], "params": json.loads(i["params"])} for i in self._datas}


class LogDatabusCollectorConfig(Table):
    """日志采集配置表"""

    FIELDS = [
        "created_by",
        "collector_config_id",
        "collector_config_name",
        "collector_scenario_id",
        "bk_biz_id",
        "description",
        "category_id",
        "subscription_id",
        "target_object_type",
        "target_node_type",
        "target_nodes",
        "description",
        "index_set_id",
        "etl_config",
        "table_id",
    ]

    def __init__(self, subscription_info: Dict[str, Any] = None, mysql_config: Dict[str, Any] = None) -> None:
        super().__init__(table_name=LOG_DATABUS_COLLECTOR_CONFIG_TABLE, mysql_config=mysql_config)
        self.subscription_info = subscription_info if subscription_info else {}

    def query_data(self) -> None:
        """查询数据"""
        sql = f"SELECT {','.join(self.FIELDS)} FROM {self.table_name} WHERE is_deleted=0"
        for data in self.db.execute_sql(sql):
            data["steps"] = [self.subscription_info.get(data["subscription_id"], {})]
            self.append_data(data)


class LogSearchLogIndexSetData(Table):

    FIELDS = [
        "bk_biz_id",
        "index_set_id",
        "result_table_id",
    ]

    def __init__(self, mysql_config: Dict[str, Any] = None) -> None:
        super().__init__(table_name=LOG_SEARCH_INDEX_SET_DATA_TABLE, mysql_config=mysql_config)

    def query_data(self) -> None:
        """查询数据"""
        sql = "SELECT {fields} FROM {table_name} WHERE is_deleted=0".format(
            fields=",".join(self.FIELDS),
            table_name=self.table_name,
        )
        for data in self.db.execute_sql(sql):
            self.append_data(data)

    @property
    def mapping(self):
        result = defaultdict(list)
        if not self._datas:
            self.query_data()
        for i in self._datas:
            result[i["index_set_id"]].append(i)
        return result


class LogSearchLogIndexSet(Table):
    """索引集表"""

    FIELDS = [
        "created_by",
        "index_set_id",
        "index_set_name",
        "project_id",
        "bkdata_project_id",
        "scenario_id",
        "category_id",
        "source_id",
        "orders",
        "is_trace_log",
        "time_field",
        "source_app_code",
        "time_field_type",
        "time_field_unit",
        "view_roles",
    ]

    def __init__(self, index_set_data: Dict[str, Any] = None, mysql_config: Dict[str, Any] = None) -> None:
        super().__init__(table_name=LOG_SEARCH_INDEX_SET_TABLE, mysql_config=mysql_config)
        self.index_set_data = index_set_data if index_set_data else {}
        self.project_map: Dict[str, Any] = self.init_project_map()

    def init_project_map(self) -> Dict[str, Any]:
        """老数据索引用project_id, 新数据索引用bk_biz_id, 需要做映射"""
        sql = f"SELECT * FROM {LOG_SEARCH_PROJECT_TABLE}"
        result = self.db.execute_sql(sql)
        return {item["project_id"]: item for item in result}

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据"""
        data["bk_biz_id"] = self.project_map[data["project_id"]]["bk_biz_id"]
        data["indexes"] = self.index_set_data.get(data["index_set_id"], [])
        return data

    def query_data(self) -> None:
        """查询数据"""
        # 因为索引集和采集项一一对应, 所以仅导出计算平台和第三方ES的索引集
        scenario = f"('{Scenario.BKDATA}', '{Scenario.ES}')"
        sql = "SELECT {fields} FROM {table_name} WHERE is_deleted=0 AND scenario_id IN {scenario}".format(
            fields=",".join(self.FIELDS), table_name=self.table_name, scenario=scenario
        )
        for data in self.db.execute_sql(sql):
            self.append_data(data=self.transform_data(data=data))


class ExportHandler:
    """导出主逻辑, 程序入口"""

    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def handle(self):
        """入口函数"""
        # 获取订阅信息
        subscription_info = NodemanSubscriptionInfo(mysql_config=self.config["bk_nodeman"]).mapping
        index_set_data = LogSearchLogIndexSetData(mysql_config=self.config["bk_log_search"]).mapping

        # 导出数据
        LogDatabusCollectorConfig(
            subscription_info=subscription_info, mysql_config=self.config["bk_log_search"]
        ).export()
        LogSearchLogIndexSet(index_set_data=index_set_data, mysql_config=self.config["bk_log_search"]).export()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_path", type=str, help="配置文件路径, 默认值: config.yaml")
    args = parser.parse_args()
    handler = ExportHandler(config=Config(args.config_path))
    handler.handle()
