# -*- coding: utf-8 -*-

# 调用监控api必备常量 如果需要做成可配置建议迁移到constans文件
TIME_SERIES_ETL_CONFIG = "bk_standard_v2_time_series"
EVENT_ETL_CONFIG = "bk_standard_v2_event"

TIME_SERIES_TYPE = "time_series"
EVENT_TYPE = "event"
SOURCE_LABEL = "custom"
OPTION = {"inject_local_time": True}

LABEL = "application_check"

# todo 这里目前是根据监控返回msg做的判断
NOT_EXIST_MSG = "query does not exist"

LOGGER_NAME = "bk_monitor"

# custom_report 限制上报大小
BATCH_SIZE = 100


class ErrorEnum:
    """错误对象枚举"""

    # 参数验证错误
    PARAMS_VERIFY_ERROR = "001"
    # 请求初始化错误
    REQUEST_ERROR = "002"
    # 请求返回status_code异常错误
    REQUEST_STATUS_ERROR = "003"
    # 请求返回中code不为0
    REQUEST_RESPONSE_CODE_ERROR = "004"
    # 目前不支持该method
    REQUEST_METHOD_NOT_ALLOWED = "005"
    # monitor中获取
    CALL_GET_DATA_ID_RESPONSE_ERROR = "006"
    # 获取table_id不存在
    TABLE_ID_NOT_EXIST = "007"


class TimeFilterEnum:
    """
    支持的time filter 枚举 按照分钟进行分类
    """

    MINUTE1 = 1
    MINUTE2 = 2
    MINUTE5 = 5
    MINUTE10 = 10
    MINUTE30 = 30
    MINUTE60 = 60
    MINUTE120 = 180
    MINUTE360 = 360
    MINUTE720 = 720
    MINUTE1440 = 1440
