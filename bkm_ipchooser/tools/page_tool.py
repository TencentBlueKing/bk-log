# -*- coding: utf-8 -*-
from bkm_ipchooser.constants import CommonEnum
from bkm_ipchooser.tools.batch_request import batch_request, QUERY_CMDB_LIMIT


def get_pagination_data(func, params: dict) -> dict:
    """
    前端透传分页参数, 获取分页数据/全量数据
    适配page_size为-1获取CC全量数据的情况
    return: {}
    """
    # 判断是否全部获取
    if params.get("page", {}).get("limit", QUERY_CMDB_LIMIT) == CommonEnum.PAGE_RETURN_ALL_FLAG.value:
        # 多线程补充no_request参数
        params["no_request"] = True
        sort = params.get("page", {}).get("sort")
        params.pop("page", None)
        info = batch_request(func=func, params=params, sort=sort)
        return {"count": len(info), "info": info}

    return func(params)
