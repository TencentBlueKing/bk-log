# -*- coding: utf-8 -*-


class BaseMonitorException(Exception):
    def __init__(self, status: str, message: str):
        super().__init__(status, message)
        self.status = status
        self.message = message

    def __str__(self):
        return f"status: {self.status} message: {self.message}"

    def __repr__(self):
        return f"status: {self.status} message: {self.message}"


class MonitorReportRequestException(BaseMonitorException):
    def __init__(self, status, message):
        super().__init__(status, message)


class MonitorReportResultException(BaseMonitorException):
    def __init__(self, status, message):
        super().__init__(status, message)


class GetTsDataException(BaseMonitorException):
    def __init__(self, status, message):
        super().__init__(status, message)
