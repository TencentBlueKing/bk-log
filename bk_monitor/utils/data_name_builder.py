# -*- coding: utf-8 -*-


class DataNameBuilder(object):
    """
    data_name等拼接工具
    """

    def __init__(self, data_name, bk_biz_id, data_name_prefix):
        self.data_name = data_name
        self.bk_biz_id = bk_biz_id
        self.data_name_prefix = data_name_prefix

    @property
    def name(self):
        return f"{self.data_name_prefix}_{self.data_name}"

    @property
    def time_series_group_name(self):
        return f"{self.data_name_prefix}_{self.data_name}"

    @property
    def table_id(self):
        return f"{self.bk_biz_id}_{self.data_name_prefix}_{self.data_name}.base".replace("-", "_")
