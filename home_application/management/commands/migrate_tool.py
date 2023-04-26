import os
import json
import sys
from typing import Any, List, Dict

import pymysql

from pymysql.cursors import SSDictCursor
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.serializers import FastCollectorCreateSerializer
from apps.utils.local import activate_request
from apps.utils.thread import generate_request
from bkm_space.utils import bk_biz_id_to_space_uid

from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_databus.handlers.collector import CollectorHandler

from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import Scenario


BASE_DIR = os.getcwd()

# CC映射表
ENV_OFFSET_TABLE = "cc_EnvIDOffset"
ENV_BIZ_MAP_TABLE = "cc_EnvBizMap"

# 日志映射表
BK_LOG_SEARCH_RESOURCE_MAPPING_TABLE = "bk_log_search_resource_mapping"


class MigrateStatus:
    """迁移状态"""

    INIT = "init"
    SUCCESS = "success"
    FAIL = "fail"
    UNKNOWN = "unknown"


class PromptColorEnum:
    """提示颜色枚举"""

    DEBUG = "cyan"
    INFO = "green"
    WARNING = "blue"
    ERROR = "red"
    PANIC = "red"


class Prompt:
    """提示"""

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
    }

    @classmethod
    def print(cls, msg: Any, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                msg = msg.replace(f"{{{key}}}", f"{value}")
        print(msg)

    @classmethod
    def fprint(cls, level: str, msg: Any, **kwargs):
        color = cls.COLORS[PromptColorEnum.__dict__[level.upper()]]
        msg = f"{color}[{level.upper()}]{cls.COLORS['reset']}\t" + msg
        if kwargs:
            for key, value in kwargs.items():
                msg = msg.replace(f"{{{key}}}", f"{color}{value}{cls.COLORS['reset']}")
        print(msg)

    @classmethod
    def debug(cls, msg: Any, **kwargs):
        if os.environ.get("DEBUG", "False"):
            cls.fprint("debug", msg, **kwargs)

    @classmethod
    def info(cls, msg: Any, **kwargs):
        cls.fprint("info", msg, **kwargs)

    @classmethod
    def warning(cls, msg: Any, **kwargs):
        cls.fprint("warning", msg, **kwargs)

    @classmethod
    def error(cls, msg: Any, **kwargs):
        cls.fprint("error", msg, **kwargs)

    @classmethod
    def panic(cls, msg: Any, **kwargs):
        cls.fprint("panic", msg, **kwargs)
        sys.exit(1)


class JsonFile(object):
    """json文件读写"""

    @classmethod
    def read(cls, filepath: str, encoding: str = "utf-8") -> Any:
        with open(filepath, "r", encoding=encoding) as f:
            return json.load(f)


def parse_str_int_list(str_list: str) -> List[int]:
    """解析字符串为int列表"""
    try:
        if not str_list:
            return []
        return [int(i) for i in str_list.split(",")]
    except Exception:
        raise Exception(f"解析失败: {str_list}, 请输入逗号分隔的数字")


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

    def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """插入数据"""
        fields = ",".join(data.keys())
        values = ",".join([f"'{i}'" for i in data.values()])
        sql = f"INSERT INTO {table_name} ({fields}) VALUES ({values})"
        try:
            self.execute_sql(sql)
            self.conn.commit()
        except Exception as e:
            Prompt.error(
                "表: {table_name}插入数据失败: {e}, 数据为: {data}", table_name=table_name, e=str(e), data=json.dumps(data)
            )
            self.conn.rollback()

    def close(self) -> None:
        self.conn.close()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-e", "--env", help="需要导入的环境", required=True)
        parser.add_argument("-b", "--bk_biz_id", help="需要导入的业务, 不传时导入所有的业务", type=int, default=0)
        parser.add_argument(
            "-c",
            "--collector_config_data",
            help="需要导入的采集项数据, 默认为: log_databus_collectorconfig.json",
            default=os.path.join(BASE_DIR, "log_databus_collectorconfig.json"),
        )
        parser.add_argument("--collector_config_id_list", help="需要导入的采集项ID, 不传时导入所有的采集项, 例如: 1,2", type=str, default="")
        parser.add_argument(
            "-i",
            "--index_set_data",
            help="需要导入的索引集数据, 默认为: log_search_logindexset.json",
            default=os.path.join(BASE_DIR, "log_search_logindexset.json"),
        )
        parser.add_argument("--index_set_id_list", help="需要导入的索引集ID, 不传时导入所有的索引集, 例如: 1,2,3", type=str, default="")
        parser.add_argument("--mysql_host", help="公共数据库地址")
        parser.add_argument("--mysql_port", help="公共数据库端口", default=3306)
        parser.add_argument("--mysql_user", help="公共数据库用户", default="root")
        parser.add_argument("--mysql_db", help="公共数据库链接库名称", default="sg_migration")
        parser.add_argument("--mysql_password", help="公共数据库密码")
        parser.add_argument("--env_offset_table", help="环境映射表", default=ENV_OFFSET_TABLE)
        parser.add_argument("--env_biz_map_table", help="业务映射表", default=ENV_BIZ_MAP_TABLE)
        parser.add_argument(
            "--bk_log_search_resource_mapping_table", help="日志平台映射表", default=BK_LOG_SEARCH_RESOURCE_MAPPING_TABLE
        )

    def handle(self, *args, **options):
        mysql_config = {
            "host": options["mysql_host"],
            "port": options["mysql_port"],
            "user": options["mysql_user"],
            "password": options["mysql_password"],
            "db": options["mysql_db"],
        }
        # 获取环境映射
        cc_env = CCEnv(
            env=options["env"],
            mysql_config=mysql_config,
            env_offset_table=options["env_offset_table"],
            env_biz_map_table=options["env_biz_map_table"],
        ).handle()
        # 导入采集项
        CollectorConfigMigrateTool(
            bk_biz_id=options["bk_biz_id"],
            filepath=options["collector_config_data"],
            mysql_config=mysql_config,
            cc_env=cc_env,
            bk_log_search_resource_mapping_table=options["bk_log_search_resource_mapping_table"],
            collector_config_id_list=options["collector_config_id_list"],
            index_set_id_list=options["index_set_id_list"],
        ).handle()
        # 导入索引集
        IndexSetMigrateTool(
            bk_biz_id=options["bk_biz_id"],
            filepath=options["index_set_data"],
            mysql_config=mysql_config,
            cc_env=cc_env,
            bk_log_search_resource_mapping_table=options["bk_log_search_resource_mapping_table"],
            collector_config_id_list=options["collector_config_id_list"],
            index_set_id_list=options["index_set_id_list"],
        ).handle()


class CCEnv:
    """
    环境映射
    包含两个映射
    1. 业务映射, bk_biz_map, 旧业务ID -> 新业务ID
    2. 偏移量, offset, 旧业务ID -> 偏移量
    """

    CC_ENV_BIZ_MAP_FIELDS = ["bk_old_biz_id", "bk_new_biz_id"]
    CC_ENV_ID_OFFSET_FIELDS = ["offset"]

    def __init__(self, env: str, mysql_config: dict, env_offset_table: str, env_biz_map_table: str) -> None:
        self.env = env
        self.env_offset_table = env_offset_table
        self.env_biz_map_table = env_biz_map_table
        self.mysql_config = mysql_config
        self.bk_biz_map = {}
        self.offset = 0
        self.database: Database = self.init_connection()

    def init_connection(self):
        connection = Database(**self.mysql_config)
        connection.connect()
        return connection

    def get_offset(self) -> None:
        """获取偏移量"""
        sql = f"SELECT * FROM {self.env_offset_table} WHERE env='{self.env}'"
        result = self.database.execute_sql(sql)
        if not result:
            Prompt.panic(msg="环境{env}未配置偏移量(表:{table}), 请检查环境是否存在", env=self.env, table=self.env_offset_table)
        self.offset = result[0]["offset"]

    def get_bk_biz_map(self) -> None:
        """获取业务映射关系"""
        sql = f"SELECT * FROM {self.env_biz_map_table} WHERE bk_env='{self.env}'"
        result = self.database.execute_sql(sql)
        if not result:
            Prompt.panic(msg="环境{env}未配置业务映射关系(表:{table}), 请检查环境是否存在", env=self.env, table=self.env_biz_map_table)
        self.bk_biz_map = {item["bk_old_biz_id"]: item["bk_new_biz_id"] for item in result}

    def handle(self):
        self.get_offset()
        self.get_bk_biz_map()
        self.database.close()
        return {"offset": self.offset, "bk_biz_map": self.bk_biz_map}


class MigrateToolBase:
    """迁移工具基类"""

    def __init__(
        self,
        bk_biz_id: int,
        filepath: str,
        mysql_config: Dict[str, Any],
        cc_env: Dict[str, Any],
        bk_log_search_resource_mapping_table: str,
        collector_config_id_list: str = "",
        index_set_id_list: str = "",
    ):
        self.bk_biz_id = bk_biz_id
        self.cc_env = cc_env
        self.bk_log_search_resource_mapping_table = bk_log_search_resource_mapping_table
        self.collector_config_id_list = parse_str_int_list(collector_config_id_list)
        self.index_set_id_list = parse_str_int_list(index_set_id_list)
        self.db = Database(**mysql_config)
        self.db.connect()
        if os.path.exists(filepath):
            self._datas = JsonFile.read(filepath)
        else:
            self._datas = []
            Prompt.warning(msg="文件不存在: {filepath}", filepath=filepath)

    def _migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        迁移数据, 各个子类实现
        各个类返回要求是一个字典, 且必须包含以下字段
        - index_set_id: 索引集ID
        """
        raise NotImplementedError

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供最基础的转换数据
        如果还有额外需要转换的, 先继承该方法, 然后继续转换
        """
        bk_biz_id = self.cc_env["bk_biz_map"][data["bk_biz_id"]]
        space_uid = bk_biz_id_to_space_uid(bk_biz_id)
        mapping = {
            "origin_index_set_id": data["index_set_id"],
            "origin_bk_biz_id": data["bk_biz_id"],
            "index_set_id": 0,
            "bk_biz_id": bk_biz_id,
            "space_uid": space_uid,
            "status": MigrateStatus.INIT,
            "details": "",
        }
        data["bk_biz_id"] = bk_biz_id
        return mapping

    @staticmethod
    def merge_success_mapping(mapping: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """合并成功mapping"""
        mapping.update(
            {
                "status": MigrateStatus.SUCCESS,
                "index_set_id": result["index_set_id"],
            }
        )
        return mapping

    @staticmethod
    def merge_fail_mapping(mapping: Dict[str, Any], exception: str) -> Dict[str, Any]:
        """合并失败mapping"""
        mapping.update({"status": MigrateStatus.FAIL, "details": exception})
        return mapping

    def check_record(self, mapping: Dict[str, Any]) -> bool:
        """检查记录是否已经存在"""
        sql = "SELECT * FROM {table} WHERE origin_index_set_id={origin_index_set_id}".format(
            table=self.bk_log_search_resource_mapping_table, origin_index_set_id=mapping["origin_index_set_id"]
        )
        result = self.db.execute_sql(sql)
        if result:
            # 如果已经存在, 则检查状态
            status = result[0]["status"]
            if status == MigrateStatus.SUCCESS:
                Prompt.info(msg="索引集{origin_index_set_id}已经迁移成功, 跳过", index_set_id=mapping["origin_index_set_id"])
            else:
                Prompt.warning(
                    msg="索引集{origin_index_set_id}已经迁移失败, 报错信息: {details}, 联系日志平台开发处理",
                    index_set_id=mapping["origin_index_set_id"],
                    details=result[0]["details"],
                )
            return True
        return False

    def record(self, mapping: Dict[str, Any]) -> None:
        """记录迁移结果"""
        self.db.insert(table_name=self.bk_log_search_resource_mapping_table, data=mapping)

    def success(self, data: Dict[str, Any], result: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        """控制台输出成功信息"""
        raise NotImplementedError

    def fail(self, data: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        """控制台输出失败信息"""
        raise NotImplementedError

    def handle(self):
        # 如果没有指定业务，则导入所有的业务
        for data in self._datas:
            if self.bk_biz_id and data["bk_biz_id"] != self.bk_biz_id:
                continue
            if (
                self.collector_config_id_list
                and data.get("collector_config_id", 0) not in self.collector_config_id_list
            ):
                continue
            if self.index_set_id_list and data["index_set_id"] not in self.index_set_id_list:
                continue
            mapping = self.transform(data)
            # 检查是否已经迁移过
            if self.check_record(mapping):
                continue
            try:
                result = self._migrate(data)
                mapping = self.merge_success_mapping(mapping, result)
                self.success(data=data, result=result, mapping=mapping)
            except Exception as e:
                mapping = self.merge_fail_mapping(mapping, str(e))
                self.fail(data=data, mapping=mapping)
            finally:
                self.record(mapping)


class CollectorConfigMigrateTool(MigrateToolBase):
    """采集项迁移工具"""

    @staticmethod
    def filter_collector_config_name_en(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        由于旧采集项不存在采集项英文名, 所以根据table_id来生成采集项英文名
        """
        table_id = data["table_id"]
        try:
            collector_config_name_en = table_id.split(".")[-1]
        except Exception:
            collector_config_name_en = table_id
        # 如果采集项英文名已存在, 则在后面加上随机字符串
        if (
            CollectorHandler()
            .pre_check({"collector_config_name_en": collector_config_name_en, "bk_biz_id": data["bk_biz_id"]})
            .get("allowed", False)
        ):
            random_suffix = get_random_string(length=2)
            collector_config_name_en = f"{collector_config_name_en}_{random_suffix}"

        data["collector_config_name_en"] = collector_config_name_en
        return data

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据"""
        data = self.filter_collector_config_name_en(data)
        mapping = super().transform(data)
        # 根据offset转换target_nodes
        target_nodes = []
        if data["target_node_type"] == TargetNodeTypeEnum.TOPO:
            for item in json.loads(data["target_nodes"]):
                item["bk_inst_id"] += self.cc_env["offset"]
                target_nodes.append(item)
        else:
            for item in json.loads(data["target_nodes"]):
                item["bk_cloud_id"] += self.cc_env["offset"]
                target_nodes.append(item)
        data["target_nodes"] = target_nodes
        data["scenario_id"] = Scenario.LOG
        return mapping

    def _migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        利用fast_create迁移数据
        """
        # 把创建人给带过来
        activate_request(generate_request(data["created_by"]))
        collector_scenario = CollectorScenario.get_instance(collector_scenario_id=data["collector_scenario_id"])
        params = {
            "bk_biz_id": data["bk_biz_id"],
            "collector_config_name": data["collector_config_name"],
            "collector_config_name_en": data["collector_config_name_en"],
            "collector_scenario_id": data["collector_scenario_id"],
            "description": data["description"],
            "category_id": data["category_id"],
            "target_object_type": data["target_object_type"],
            "target_node_type": data["target_node_type"],
            "target_nodes": data["target_nodes"],
            # 旧采集项缺少params, 从节点管理拉到的造了一个steps, [{"id": "bkunifylogbeat", "params": {}}]
            "params": collector_scenario.parse_steps(data["steps"]),
        }
        slz = FastCollectorCreateSerializer(data=params)
        slz.is_valid()
        return CollectorHandler().fast_create(params=slz.data)

    def success(self, data: Dict[str, Any], result: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        Prompt.info(
            msg=(
                "采集项[{c_old_id}] {collector_config_name}迁移成功, 新采集项ID: {c_new_id}"
                ", 索引集 {origin_index_set_id} -> {index_set_id}"
            ),
            c_old_id=data["collector_config_id"],
            collector_config_name=data["collector_config_name"],
            c_new_id=result["collector_config_id"],
            origin_index_set_id=mapping["origin_index_set_id"],
            index_set_id=mapping["index_set_id"],
        )

    def fail(self, data: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        Prompt.error(
            msg=("采集项[{c_old_id}] {collector_config_name}迁移失败, 错误信息: {error}"),
            c_old_id=data["collector_config_id"],
            collector_config_name=data["collector_config_name"],
            error=mapping["details"],
        )


class IndexSetMigrateTool(MigrateToolBase):
    """索引集迁移工具"""

    @staticmethod
    def _migrate_bkdata(data: Dict[str, Any]) -> Dict[str, Any]:
        params = {
            "space_uid": bk_biz_id_to_space_uid(data["bk_biz_id"]),
            "index_set_name": data["index_set_name"],
            "scenario_id": data["scenario_id"],
            "indexes": data["indexes"],
            "is_trace_log": True if data["is_trace_log"] else False,
            "time_field": data["time_field"],
            "time_field_type": data["time_field_type"],
            "time_filed_unit": data["time_filed_unit"],
            "bk_app_code": data["source_app_code"],
            "username": data["created_by"],
            # TODO: 缺少映射, 而且没找到怎么传
            "bkdata_project_id": data["bkdata_project_id"],
        }
        index_set = IndexSetHandler.create(**params)
        return {
            "index_set_id": index_set["index_set_id"],
        }

    def _migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data["scenario_id"] == Scenario.BKDATA.value:
            return self._migrate_bkdata(data)
        # TODO: 暂不迁移第三方ES索引集
        # if data["scenario_id"] == Scenario.ES.value:
        #     return self._migrate_es(data)

    # @staticmethod
    # def _migrate_es(data: Dict[str, Any]) -> Dict[str, Any]:
    #     params = {
    #         "space_uid": bk_biz_id_to_space_uid(data["bk_biz_id"]),
    #         "index_set_name": data["index_set_name"],
    #         # TODO: 该字段需要做映射
    #         "storage_cluster_id": data["storage_cluster_id"],
    #         "scenario_id": data["scenario_id"],
    #         "indexes": data["indexes"],
    #         "is_trace_log": True if data["is_trace_log"] else False,
    #         "time_field": data["time_field"],
    #         "time_field_type": data["time_field_type"],
    #         "time_filed_unit": data["time_filed_unit"],
    #         "bk_app_code": data["source_app_code"],
    #         "username": data["created_by"],
    #     }
    #     index_set = IndexSetHandler.create(**params)
    #     return {
    #         "index_set_id": index_set["index_set_id"],
    #     }

    def success(self, data: Dict[str, Any], result: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        Prompt.info(
            msg="索引集[{i_old_id}] {index_set_name}迁移成功, 新索引集ID: {i_new_id}",
            i_old_id=mapping["origin_index_set_id"],
            index_set_name=data["index_set_name"],
            i_new_id=mapping["index_set_id"],
        )

    def fail(self, data: Dict[str, Any], mapping: Dict[str, Any]) -> None:
        Prompt.error(
            msg="索引集[{i_old_id}] {index_set_name}迁移失败, 错误信息: {error}",
            i_old_id=mapping["origin_index_set_id"],
            index_set_name=data["index_set_name"],
            error=mapping["details"],
        )
