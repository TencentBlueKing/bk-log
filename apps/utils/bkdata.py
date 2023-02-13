from abc import ABC

from django.conf import settings
from apps.api import BkDataQueryApi


class Sql(ABC):
    def to_sql(self) -> str:
        pass


class Where(Sql):
    def __init__(self, key: any, op: str, value: any):
        self._key = key
        self._op = op
        self._value = value

    def to_sql(self) -> str:
        value = self._value
        if isinstance(self._value, str):
            value = f"'{self._value}'"

        return f"{self._key} {self._op} {value}"


class OrderBy(Sql):
    DESC = "DESC"
    ASC = "ASC"

    def __init__(self, field: str, asc: bool = True):
        self._field = field
        self._asc = asc

    def to_sql(self) -> str:
        sql_value = self.DESC
        if self._asc:
            sql_value = self.ASC

        return f"{self._field} {sql_value}"


class BkData(Sql):
    """
    BkData query
    """

    TIME_RANGE_FIELD = "dtEventTimeStamp"
    TIMESTAMP_S_TO_MS = 1000
    DEFAULT_LIMIT = 10000

    def __init__(self, rt: str = ""):
        self._rt = rt
        self._where = []
        self._fields = []
        self._order_by = []
        self._limit = self.DEFAULT_LIMIT

    def set_result_table(self, rt: str) -> "BkData":
        self._rt = rt
        return self

    def where(self, key: any, op: str, value: any) -> "BkData":
        self._where.append(Where(key, op, value))
        return self

    def select(self, *fields: str):
        self._fields.extend(list(fields))
        return self

    def time_range(self, start_time, end_time) -> "BkData":
        """

        :param start_time: 时间戳 秒
        :param end_time: 时间戳秒
        :return:
        """
        self.where(self.TIME_RANGE_FIELD, ">=", start_time * self.TIMESTAMP_S_TO_MS).where(
            self.TIME_RANGE_FIELD, "<=", end_time * self.TIMESTAMP_S_TO_MS
        )
        self.order_by(self.TIME_RANGE_FIELD)
        return self

    def order_by(self, field: str, asc: bool = False) -> "BkData":
        self._order_by.append(OrderBy(field, asc))
        return self

    def to_sql(self) -> str:
        fields = ",".join(self._fields)
        order_by = ""
        if self._order_by:
            order_by = f"ORDER BY {','.join([r.to_sql() for r in self._order_by])}"
        where_conditions = " AND ".join([where.to_sql() for where in self._where])
        return "SELECT {} FROM {} WHERE {} {} LIMIT {}".format(
            fields, self._rt, where_conditions, order_by, self._limit
        )

    def query(self) -> list:
        params = {"sql": self.to_sql()}
        if settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
            params.update({"bkdata_authentication_method": "token", "bkdata_data_token": settings.BKDATA_DATA_TOKEN})
        else:
            params.update({"bkdata_authentication_method": "user", "bk_username": "admin", "operator": "admin"})
        return BkDataQueryApi.query(params)["list"]
