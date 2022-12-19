# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from multiprocessing.pool import ThreadPool

from django.utils.translation import get_language

from bkm_ipchooser.tools import translation
from apps.constants import DEFAULT_MAX_WORKERS

QUERY_CMDB_LIMIT = 500
WRITE_CMDB_LIMIT = 500
QUERY_CMDB_MODULE_LIMIT = 500
QUERY_CLOUD_LIMIT = 200
CONCURRENT_NUMBER = 10


def format_params(params, get_count, func):
    # 拆分params适配bk_module_id大于500情况
    request_params = []

    bk_module_ids = params.pop("bk_module_ids", [])

    # 请求第一次获取总数
    if not bk_module_ids:
        request_params.append({"count": get_count(func(page={"start": 0, "limit": 1}, **params)), "params": params})

    for s_index in range(0, len(bk_module_ids), QUERY_CMDB_MODULE_LIMIT):
        single_params = deepcopy(params)

        single_params.update({"bk_module_ids": bk_module_ids[s_index : s_index + QUERY_CMDB_MODULE_LIMIT]})
        request_params.append(
            {"count": get_count(func(page={"start": 0, "limit": 1}, **single_params)), "params": single_params}
        )

    return request_params


def batch_request(
    func,
    params,
    get_data=lambda x: x["info"],
    get_count=lambda x: x["count"],
    limit=QUERY_CMDB_LIMIT,
    sort=None,
    split_params=False,
):
    """
    异步并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :param sort: 排序
    :param split_params: 是否拆分参数
    :return: 请求结果
    """

    # 如果该接口没有返回count参数，只能同步请求
    if not get_count:
        return sync_batch_request(func, params, get_data, limit)

    if not split_params:
        final_request_params = [
            {"count": get_count(func(dict(page={"start": 0, "limit": 1}, **params))), "params": params}
        ]
    else:
        final_request_params = format_params(params, get_count, func)

    data = []

    # 根据请求总数并发请求
    pool = ThreadPool(20)
    futures = []

    for req in final_request_params:
        start = 0
        while start < req["count"]:
            request_params = {"page": {"limit": limit, "start": start}}
            if sort:
                request_params["page"]["sort"] = sort
            request_params.update(req["params"])
            futures.append(pool.apply_async(func, args=(request_params,)))

            start += limit

    pool.close()
    pool.join()

    # 取值
    for future in futures:
        data.extend(get_data(future.get()))

    return data


def sync_batch_request(func, params, get_data=lambda x: x["info"], limit=500):
    """
    同步请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param limit: 一次请求数量
    :return: 请求结果
    """
    # 如果该接口没有返回count参数，只能同步请求
    data = []
    start = 0

    # 根据请求总数并发请求
    while True:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        result = get_data(func(request_params))
        data.extend(result)
        if len(result) < limit:
            break
        else:
            start += limit

    return data


def request_multi_thread(func, params_list, get_data=lambda x: []):
    """
    并发请求接口，每次按不同参数请求最后叠加请求结果
    :param func: 请求方法
    :param params_list: 参数列表
    :param get_data: 获取数据函数，通常CMDB的批量接口应该设置为 get_data=lambda x: x["info"]，其它场景视情况而定
    :return: 请求结果累计
    """
    result = []
    with ThreadPoolExecutor(max_workers=DEFAULT_MAX_WORKERS) as ex:
        tasks = [
            ex.submit(translation.RespectsLanguage(language=get_language())(func), **params) for params in params_list
        ]
    for future in as_completed(tasks):
        _result = get_data(future.result())
        if isinstance(_result, list):
            result.extend(_result)
        else:
            result.append(_result)
    return result
