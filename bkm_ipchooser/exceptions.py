# -*- coding: utf-8 -*-
class IpChooserBaseException(Exception):
    pass


class SerValidationError(IpChooserBaseException):
    pass


class TopoNotExistsError(IpChooserBaseException):
    pass
