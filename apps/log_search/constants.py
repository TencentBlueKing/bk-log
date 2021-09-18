# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from enum import Enum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.utils import ChoicesEnum
from apps.log_databus.constants import ETL_DELIMITER_IGNORE, ETL_DELIMITER_DELETE, ETL_DELIMITER_END


class TagColor(ChoicesEnum):
    RED = "red"
    YELLOW = "yellow"
    BLUE = "blue"
    GREEN = "green"
    GRAY = "gray"

    _choices_labels = (
        (RED, _("red")),
        (YELLOW, _("yellow")),
        (BLUE, _("blue")),
        (GREEN, _("green")),
        (GRAY, _("gray")),
    )


DEFAULT_TAG_COLOR = TagColor.BLUE

SEARCH_SCOPE_VALUE = ["default", "search_context"]
MAX_RESULT_WINDOW = 10000
MAX_SEARCH_SIZE = 100000
SCROLL = "1m"
DEFAULT_TIME_FIELD = "dtEventTimeStamp"
BK_SUPPLIER_ACCOUNT = "0"
BK_BCS_APP_CODE = "bk_bcs"

# API请求异常编码
API_RESULT_ERROR_AUTH = "40000"

# cc api find_module_with_relation
MAX_LIST_BIZ_HOSTS_PARAMS_COUNT = 200

# 上下文gseIndex
CONTEXT_GSE_INDEX_SIZE = 10000

# 数据平台异步导出必需字段
BKDATA_ASYNC_FIELDS = ["dtEventTimeStamp", "ip", "gseindex", "_iteration_idx"]
# 数据平台容器类型异步导出必需字段
BKDATA_ASYNC_CONTAINER_FIELDS = ["dtEventTimeStamp", "container_id", "gseindex", "_iteration_idx"]
# 采集异步导出必需字段
LOG_ASYNC_FIELDS = ["dtEventTimeStamp", "serverIp", "gseIndex", "iterationIndex"]
# 异步导出默认排序
ASYNC_SORTED = "desc"
# 获取异步导出目标多少
ASYNC_COUNT_SIZE = 1
# 异步导出最大条数
MAX_ASYNC_COUNT = 2000000
# 异步导出时间
ASYNC_EXPORT_TIME_RANGE = "customized"
# 异步导出目录
ASYNC_APP_CODE = settings.APP_CODE.replace("-", "_")
ASYNC_DIR = f"/tmp/{ASYNC_APP_CODE}"
# 异步导出配置名称
FEATURE_ASYNC_EXPORT_COMMON = "feature_async_export"
# 异步导出通知方式
FEATURE_ASYNC_EXPORT_NOTIFY_TYPE = "notify_type"
# 异步导出存储方式
FEATURE_ASYNC_EXPORT_STORAGE_TYPE = "storage_type"
# 异步导出邮件模板名
ASYNC_EXPORT_EMAIL_TEMPLATE = "async_export_email_template"
# 异步导出邮件默认中文模板路径
ASYNC_EXPORT_EMAIL_TEMPLATE_PATH = "templates/email_template/email_template.html"
# 异步导出邮件默认英文模板路径
ASYNC_EXPORT_EMAIL_TEMPLATE_PATH_EN = "templates/email_template/email_template_en.html"
# 异步导出邮件模板名
ASYNC_EXPORT_EMAIL_ERR_TEMPLATE = "async_export_email_err_template"
# 异步导出邮件默认中文模板路径
ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH = "templates/email_template/email_template_err.html"
# 异步导出邮件默认英文模板路径
ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH_EN = "templates/email_template/email_template_err_en.html"
# 异步导出文件过期天数
ASYNC_EXPORT_FILE_EXPIRED_DAYS = 2
# 异步导出链接expired时间 24*60*60
ASYNC_EXPORT_EXPIRED = 86400
HAVE_DATA_ID = "have_data_id"
BKDATA_OPEN = "bkdata"

FIND_MODULE_WITH_RELATION_FIELDS = ["bk_module_id", "bk_module_name", "service_template_id"]

COMMON_LOG_INDEX_RE = r"^(v2_)?{}_(?P<datetime>\d+)_(?P<index>\d+)$"
BKDATA_INDEX_RE = r"^{}_\d+$"

MAX_EXPORT_REQUEST_RETRY = 3


# 消息模式
class MsgModel(object):
    NORMAL = "normal"
    ABNORMAL = "abnormal"


# 数据平台mapping返回错误
class BkDataErrorCode(object):
    COULD_NOT_GET_METADATA_ERROR = 1532013
    STORAGE_TYPE_ERROR = 1532007


class EsHealthStatus(ChoicesEnum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"


class TraceMatchFieldType(ChoicesEnum):
    MUST = "MUST"
    SUGGEST = "SUGGEST"
    USER_DEFINE = "USER_DEFINE"

    _choices_labels = ((MUST, _("必须")), (SUGGEST, _("建议")), (USER_DEFINE, _("用户自定义")))


class TraceMatchResult(ChoicesEnum):
    SUCCESS = "SUCCESS"
    FIELD_MISS = "FIELD_MISS"
    TYPE_NOT_MATCH = "TYPE_NOT_MATCH"
    OTHER = "OTHER"

    _choices_labels = (
        (SUCCESS, _("正常")),
        (FIELD_MISS, _("字段缺失")),
        (TYPE_NOT_MATCH, _("数据类型不匹配")),
        (OTHER, _("其他")),
    )


class TimeEnum(Enum):
    """
    时间枚举
    """

    ONE_SECOND: int = 1
    ONE_MINUTE_SECOND: int = ONE_SECOND * 60
    FIVE_MINUTE_SECOND: int = ONE_MINUTE_SECOND * 5
    ONE_HOUR_SECOND: int = ONE_MINUTE_SECOND * 60
    ONE_DAY_SECOND: int = ONE_HOUR_SECOND * 24
    ONE_YEAR_SECOND: int = ONE_DAY_SECOND * 365


class CCInstanceType(ChoicesEnum):
    SET = "set"
    MODULE = "module"
    _choices_labels = (
        (SET, _("集群")),
        (MODULE, _("模块")),
    )


class TemplateType(ChoicesEnum):
    SERIVCE_TEMPLATE = "SERVICE_TEMPLATE"
    SET_TEMPLATE = "SET_TEMPLATE"

    _choices_labels = (
        (SERIVCE_TEMPLATE, _("服务模版")),
        (SET_TEMPLATE, _("集群模版")),
    )


class BKDataProjectEnum(Enum):
    """
    数据平台项目常量
    """

    TAGS = ["inland"]


class AgentStatusEnum(ChoicesEnum):
    """
    agent状态
    """

    UNKNOWN = -1
    ON = 0
    OFF = 1
    NOT_EXIST = 2
    NO_DATA = 3

    _choices_labels = (
        (UNKNOWN, _("异常（未知）")),
        (ON, _("正常")),
        (OFF, _("关闭")),
        (NOT_EXIST, _("Agent未安装")),
        (NO_DATA, _("无数据")),
    )


class AgentStatusTranslationEnum(ChoicesEnum):
    """
    agent 状态为前端所做的改变
    """

    ON = 0
    NOT_EXIST = 2

    _choices_labels = (
        (ON, "normal"),
        (NOT_EXIST, "not_exist"),
    )


class InstanceTypeEnum(ChoicesEnum):
    SERVICE = "service"
    HOST = "host"

    _choices_labels = ((SERVICE, _("服务")), (HOST, _("主机")))


class GlobalTypeEnum(ChoicesEnum):
    """
    meta全局类型枚举
    """

    CATEGORY = "category"
    COLLECTOR_SCENARIO = "collector_scenario"
    ETL_CONFIG = "etl_config"
    DATA_DELIMITER = "data_delimiter"
    DATA_ENCODING = "data_encoding"
    STORAGE_DURATION_TIME = "storage_duration_time"
    FIELD_DATA_TYPE = "field_data_type"
    Field_DATE_FORMAT = "field_date_format"
    FIELD_BUILT_IN = "field_built_in"
    TIME_ZONE = "time_zone"
    TIME_FIELD_TYPE = "time_field_type"
    TIME_FIELD_UNIT = "time_field_unit"

    _choices_labels = (
        (CATEGORY, _("数据分类")),
        (COLLECTOR_SCENARIO, _("采集场景")),
        (DATA_DELIMITER, _("分隔符列表")),
        (DATA_ENCODING, _("编码格式")),
        (STORAGE_DURATION_TIME, _("数据保留时间")),
        (ETL_CONFIG, _("字段提取方式")),
        (FIELD_DATA_TYPE, _("字段类型")),
        (Field_DATE_FORMAT, _("时间格式")),
        (FIELD_BUILT_IN, _("内置字段")),
        (TIME_FIELD_TYPE, _("时间字段类型")),
        (TIME_FIELD_UNIT, _("时间字段单位")),
    )


class CollectorScenarioEnum(ChoicesEnum):
    ROW = "row"
    SECTION = "section"
    WIN_EVENT = "win_event"

    _choices_labels = (
        (ROW, _("行日志文件")),
        (SECTION, _("段日志文件")),
        (WIN_EVENT, _("win event日志")),
    )

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取_choices_keys的某个key值的value
        :return: list[dict{id, name, is_active}]
        """
        return [
            {"id": key, "name": value, "is_active": True if key in settings.COLLECTOR_SCENARIOS else False}
            for key, value in cls.get_dict_choices().items()
        ]


class EtlConfigEnum(ChoicesEnum):
    BK_LOG_JSON = "bk_log_json"
    BK_LOG_DELIMITER = "bk_log_delimiter"
    BK_LOG_REGEXP = "bk_log_regexp"

    _choices_labels = (
        (BK_LOG_JSON, _("JSON")),
        (BK_LOG_DELIMITER, _("分隔符")),
        (BK_LOG_REGEXP, _("正则表达式")),
    )


class CollectorScenarioDescriptionEnum(ChoicesEnum):
    _choices_labels = (
        (CollectorScenarioEnum.ROW.value, _("行日志")),
        (CollectorScenarioEnum.SECTION.value, _("段日志")),
        (CollectorScenarioEnum.WIN_EVENT.value, _("win event")),
    )


# 日志编码
ENCODINGS = [
    "utf-8",
    "gbk",
    "gb18030",
    "big5",
    # 8bit char map encodings
    "iso8859-6e",
    "iso8859-6i",
    "iso8859-8e",
    "iso8859-8i",
    "iso8859-1",  # latin-1
    "iso8859-2",  # latin-2
    "iso8859-3",  # latin-3
    "iso8859-4",  # latin-4
    "iso8859-5",  # latin/cyrillic
    "iso8859-6",  # latin/arabic
    "iso8859-7",  # latin/greek
    "iso8859-8",  # latin/hebrew
    "iso8859-9",  # latin-5
    "iso8859-10",  # latin-6
    "iso8859-13",  # latin-7
    "iso8859-14",  # latin-8
    "iso8859-15",  # latin-9
    "iso8859-16",  # latin-10
    # ibm codepages
    "cp437",
    "cp850",
    "cp852",
    "cp855",
    "cp858",
    "cp860",
    "cp862",
    "cp863",
    "cp865",
    "cp866",
    "ebcdic-037",
    "ebcdic-1040",
    "ebcdic-1047",
    # cyrillic
    "koi8r",
    "koi8u",
    # macintosh
    "macintosh",
    "macintosh-cyrillic",
    # windows
    "windows1250",  # central and eastern european
    "windows1251",  # russian, serbian cyrillic
    "windows1252",  # legacy
    "windows1253",  # modern greek
    "windows1254",  # turkish
    "windows1255",  # hebrew
    "windows1256",  # arabic
    "windows1257",  # estonian, latvian, lithuanian
    "windows1258",  # vietnamese
    "windows874",
    # utf16 bom codecs (seekable data source required)
    "utf-16-bom",
    "utf-16be-bom",
    "utf-16le-bom",
]


class EncodingsEnum(ChoicesEnum):
    """
    字符编码枚举
    """

    UTF = "UTF-8"
    GBK = "GBK"

    @classmethod
    def get_choices(cls):
        return [key.upper() for key in ENCODINGS]

    @classmethod
    def get_choices_list_dict(cls):
        return [{"id": key.upper(), "name": key.upper()} for key in ENCODINGS if key]


class GlobalCategoriesEnum(ChoicesEnum):
    """
    数据分类枚举
    """

    HOSTS = {"id": "hosts", "name": _("主机"), "children": [{"id": "os", "name": _("操作系统"), "children": []}]}

    SERVICES = {
        "id": "services",
        "name": _("服务"),
        "children": [{"id": "service_module", "name": _("服务模块"), "children": []}],
    }

    APPLICATIONS = {
        "id": "applications",
        "name": "应用",
        "children": [{"id": "application_check", "name": _("业务应用"), "children": []}],
    }

    OTHER = {"id": "others", "name": "其他", "children": [{"id": "other_rt", "name": _("其他"), "children": []}]}

    @classmethod
    def get_init_categories(cls):
        """
        获取初始化的数据分类
        :return: list[{
            id
            name
            children
        }]
        """
        return [cls.HOSTS.value, cls.SERVICES.value, cls.APPLICATIONS.value, cls.OTHER.value]

    @classmethod
    def get_display(cls, key: str) -> str:
        """
        获取指定分类的显示名
        :param key: others
        :return: 其他
        """

        def _get_display(_key, categories):
            if isinstance(categories, dict):
                if categories.get("id") == _key:
                    return categories.get("name")
                for _category in categories.get("children", []):
                    _name = _get_display(_key, _category)
                    if _name:
                        return _name

            if isinstance(categories, list):
                for _category in categories:
                    if _category.get("id") == _key:
                        return _category.get("name")

        for category in cls.get_init_categories():
            name = _get_display(key, category)
            if name:
                return name
        return ""

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取_choices_keys的某个key值的value
        :return: list[dict{id, name, children}]
        """
        return [{"id": key, "name": value} for key, value in cls.get_dict_choices().items()]


class ConditionFilterTypeEnum(ChoicesEnum):
    """
    过滤方式枚举
    """

    INCLUDE = "include"
    EXCLUDE = "exclude"

    _choices_labels = (
        (INCLUDE, _("包含")),
        (EXCLUDE, _("不包含")),
    )


class ConditionTypeEnum(ChoicesEnum):
    """
    过滤方式类型枚举
    """

    STRING = "match"
    DELIMITER = "separator"

    _choices_labels = (
        (STRING, _("字符串")),
        (DELIMITER, _("分隔符")),
    )


class SeparatorEnum(ChoicesEnum):
    """
    分隔符枚举
    """

    BAR = "|"
    COMMA = ","
    BACK_QUOTE = "`"
    SPACE = " "
    SEMICOLON = ";"

    _choices_labels = (
        (BAR, _("竖线(|)")),
        (COMMA, _("逗号(,)")),
        (BACK_QUOTE, _("反引号(`)")),
        (SPACE, _("空格")),
        (SEMICOLON, _("分号(;)")),
    )


class StorageDurationTimeEnum(ChoicesEnum):
    """
    ES过期时间枚举
    """

    ONE_DAY = "1"
    THREE_DAY = "3"
    SEVEN_DAY = "7"
    FOURTEEN_DAY = "14"
    THIRTY_DAY = "30"

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取_choices_keys的某个key值的value
        :return: list[dict{id, name, is_active}]
        """
        return [
            {"id": key, "name": value, "default": True if key == str(settings.ES_STORAGE_DEFAULT_DURATION) else False}
            for key, value in cls.get_dict_choices().items()
        ]

    _choices_labels = (
        (ONE_DAY, _("1天")),
        (THREE_DAY, _("3天")),
        (SEVEN_DAY, _("7天")),
        (FOURTEEN_DAY, _("14天")),
        (THIRTY_DAY, _("30天")),
    )


class TimeFieldTypeEnum(ChoicesEnum):
    """
    时间字段类型
    """

    DATE = "date"
    LONG = "long"

    _choices_labels = (
        (DATE, _("date")),
        (LONG, _("long")),
    )


class TimeFieldUnitEnum(ChoicesEnum):
    """
    时间字段单位
    """

    SECOND = "second"
    MILLISECOND = "millisecond"
    MICROSECOND = "microsecond"

    _choices_labels = ((SECOND, _("second")), (MILLISECOND, _("millisecond")), (MICROSECOND, _("microsecond")))


class FieldDataTypeEnum(ChoicesEnum):
    """
    字段类型
    """

    STRING = "string"
    INT = "int"
    LONG = "long"
    DOUBLE = "double"
    OBJECT = "object"
    NESTED = "nested"

    choices_list = [(STRING, STRING), (INT, INT), (LONG, LONG), (DOUBLE, DOUBLE)]

    if settings.FEATURE_TOGGLE.get("es_type_object") == "on":
        choices_list.append((OBJECT, OBJECT))

    if settings.FEATURE_TOGGLE.get("es_type_nested") == "on":
        choices_list.append((NESTED, NESTED))

    _choices_labels = tuple(choices_list)

    @classmethod
    def get_meta_field_type(cls, es_field_type):
        return {
            "ip": "string",
            "keyword": "string",
            "integer": "float",
            "long": "float",
            "float": "float",
            "double": "float",
            "object": "object",
            "nested": "nested",
        }.get(es_field_type, "string")

    @classmethod
    def get_es_field_type(cls, field_type, is_analyzed=False, is_time=False):
        field_type = {
            "string": "keyword",
            "int": "integer",
            "long": "long",
            "double": "double",
            "object": "object",
            "nested": "nested",
        }.get(field_type, "keyword")
        if is_analyzed:
            field_type = "text"
        if is_time:
            field_type = "date"
        return field_type

    @classmethod
    def get_field_type(cls, es_field_type):
        return {
            "ip": "string",
            "keyword": "string",
            "integer": "int",
            "long": "long",
            "float": "float",
            "double": "double",
            "object": "object",
            "nested": "nested",
        }.get(es_field_type, "string")


class FieldDateFormatEnum(ChoicesEnum):
    """
    时间格式
    """

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取时间格式
        id: transfer格式
        name: web校验格式（python）
        description: DEMO
        :return: list[dict{id, name, description}]
        """
        return [
            {"id": "yyyy-MM-dd HH:mm:ss", "name": "YYYY-MM-DD HH:mm:ss", "description": "2006-01-02 15:04:05"},
            {
                "id": "yyyy-MM-dd HH:mm:ss.SSS",
                "name": "YYYY-MM-DD HH:mm:ss.SSS",
                "description": "2006-01-02 15:04:05.000",
            },
            {
                "id": "yyyy-MM-dd HH:mm:ss.SSSSSS",
                "name": "YYYY-MM-DD HH:mm:ss.SSSSSS",
                "description": "2006-01-02 15:04:05.000000",
            },
            {"id": "yyyy-MM-dd+HH:mm:ss", "name": "YYYY-MM-DD+HH:mm:ss", "description": "2006-01-02+15:04:05"},
            {"id": "MM/dd/yyyy HH:mm:ss", "name": "MM/DD/YYYY HH:mm:ss", "description": "01/02/2006 15:04:05"},
            {"id": "yyyyMMddHHmmss", "name": "YYYYMMDDHHmmss", "description": "20060102150405"},
            {"id": "yyyyMMdd HHmmss", "name": "YYYYMMDD HHmmss", "description": "20060102 150405"},
            {"id": "yyyyMMdd HHmmss.SSS", "name": "YYYYMMDD HHmmss.SSS", "description": "20060102 150405.000"},
            {"id": "dd/MMM/yyyy:HH:mm:ss", "name": "DD/MMM/YYYY:HH:mm:ss", "description": "02/Jan/2006:15:04:05"},
            {
                "id": "dd/MMM/yyyy:HH:mm:ssZ",
                "name": "DD/MMM/YYYY:HH:mm:ssZ",
                "description": "02/Jan/2006:15:04:05-0700",
            },
            {
                "id": "dd/MMM/yyyy:HH:mm:ss Z",
                "name": "DD/MMM/YYYY:HH:mm:ss Z",
                "description": "02/Jan/2006:15:04:05 -0700",
            },
            {
                "id": "dd/MMM/yyyy:HH:mm:ssZZ",
                "name": "DD/MMM/YYYY:HH:mm:ssZZ",
                "description": "02/Jan/2006:15:04:05-07:00",
            },
            {
                "id": "dd/MMM/yyyy:HH:mm:ss ZZ",
                "name": "DD/MMM/YYYY:HH:mm:ss ZZ",
                "description": "02/Jan/2006:15:04:05 -07:00",
            },
            {"id": "date_hour_minute_second", "name": "YYYY-MM-DDTHH:mm:ss", "description": "2006-01-02T15:04:05"},
            {
                "id": "date_hour_minute_second_millis",
                "name": "YYYY-MM-DDTHH:mm:ss.SSS",
                "description": "2006-01-02T15:04:05.000",
            },
            {"id": "basic_date_time_no_millis", "name": "YYYYMMDDTHHmmssZ", "description": "20060102T150405-0700"},
            {
                "id": "basic_date_time_micros",
                "name": "YYYYMMDDTHHmmss.SSSSSSZ",
                "description": "20060102T150405.000000-0700",
            },
            {
                "id": "strict_date_time",
                "name": "YYYY-MM-DDTHH:mm:ss.SSSZ",
                "description": "2006-01-02T15:04:05.000-07:00",
            },
            {
                "id": "strict_date_time_no_millis",
                "name": "YYYY-MM-DDTHH:mm:ssZ",
                "description": "2006-01-02T15:04:05-07:00",
            },
            {
                "id": "strict_date_time_micros",
                "name": "YYYY-MM-DDTHH:mm:ss.SSSSSSZ",
                "description": "2006-01-02T15:04:05.000000-07:00",
            },
            {"id": "epoch_micros", "name": "epoch_micros", "description": "1136185445000000"},
            {"id": "epoch_millis", "name": "epoch_millis", "description": "1136185445000"},
            {"id": "epoch_second", "name": "epoch_second", "description": "1136185445"},
        ]


# 监控保留字
RT_RESERVED_WORD_EXAC = [
    "SERVER",
    "REPO",
    "VIEW",
    "TAGKEY",
    "ILLEGAL",
    "EOF",
    "WS",
    "IDENT",
    "BOUNDPARAM",
    "NUMBER",
    "INTEGER",
    "DURATIONVAL",
    "STRING",
    "BADSTRING",
    "BADESCAPE",
    "TRUE",
    "FALSE",
    "REGEX",
    "BADREGEX",
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "AND",
    "OR",
    "EQ",
    "NEQ",
    "EQREGEX",
    "NEQREGEX",
    "LT",
    "LTE",
    "GT",
    "GTE",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "COLON",
    "DOUBLECOLON",
    "SEMICOLON",
    "DOT",
    "ALL",
    "ALTER",
    "ANY",
    "AS",
    "ASC",
    "BEGIN",
    "BY",
    "CREATE",
    "CONTINUOUS",
    "DATABASE",
    "DATABASES",
    "DEFAULT",
    "DELETE",
    "DESC",
    "DESTINATIONS",
    "DIAGNOSTICS",
    "DISTINCT",
    "DROP",
    "DURATION",
    "END",
    "EVERY",
    "EXISTS",
    "EXPLAIN",
    "FIELD",
    "FOR",
    "FROM",
    "GROUP",
    "GROUPS",
    "IF",
    "IN",
    "INF",
    "INSERT",
    "INTO",
    "KEY",
    "KEYS",
    "KILL",
    "LIMIT",
    "MEASUREMENT",
    "MEASUREMENTS",
    "NAME",
    "NOT",
    "OFFSET",
    "ON",
    "ORDER",
    "PASSWORD",
    "POLICY",
    "POLICIES",
    "PRIVILEGES",
    "QUERIES",
    "QUERY",
    "READ",
    "REPLICATION",
    "RESAMPLE",
    "RETENTION",
    "REVOKE",
    "SELECT",
    "SERIES",
    "SET",
    "SHOW",
    "SHARD",
    "SHARDS",
    "SLIMIT",
    "SOFFSET",
    "STATS",
    "SUBSCRIPTION",
    "SUBSCRIPTIONS",
    "TAG",
    "TO",
    "TIME",
    "VALUES",
    "WHERE",
    "WITH",
    "WRITE",
    "TIMESTAMP",
    "TIME",
    # 内置字段
    "BK_BIZ_ID",
    "IP",
    "PLAT_ID",
    "BK_CLOUD_ID",
    "CLOUD_ID",
    "COMPANY_ID",
    "BK_SUPPLIER_ID",
    # CMDB拆分字段
    "bk_cmdb_level_name",
    "bk_cmdb_level_id",
    # 日志平台内置字段
    "cloudId",
    "serverIp",
    "path",
    "gseIndex",
    "iterationIndex",
    "log",
    "dtEventTimeStamp",
    "datetime",
    "filename",
    "items",
    "utctime",
    # ignore、delete、end
    ETL_DELIMITER_IGNORE,
    ETL_DELIMITER_DELETE,
    ETL_DELIMITER_END,
]


class FieldBuiltInEnum(object):
    """
    系统内置字段
    """

    @classmethod
    def get_choices(cls):
        return [key.lower() for key in RT_RESERVED_WORD_EXAC]

    @classmethod
    def get_choices_list_dict(cls):
        return [{"id": key.lower(), "name": key.lower()} for key in RT_RESERVED_WORD_EXAC if key]


class TimeZoneEnum(ChoicesEnum):
    """
    时区
    """

    @classmethod
    def get_choices_list_dict(cls) -> list:
        result = []
        for i in range(-12, 13, 1):
            result.append(
                {"id": i, "name": "UTC" + ("+" if i >= 0 else "") + f"{i:02}:00", "default": True if i == 8 else False}
            )
        return result


# CMDB 查询字段
CMDB_HOST_SEARCH_FIELDS = [
    "bk_host_id",
    "bk_os_type",
    "bk_os_name",
    "bk_cloud_id",
    "bk_host_innerip",
    "bk_supplier_account",
]

CMDB_SET_INFO_FIELDS = ["bk_set_id", "bk_chn_name"]

GET_SET_INFO_FILEDS_MAX_IDS_LEN = 500
