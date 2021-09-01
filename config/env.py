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
import importlib
import os

import yaml


# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if "BKPAAS_ENVIRONMENT" in os.environ:
    ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT", "dev")
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get("BK_ENV", "development")
    ENVIRONMENT = {
        "development": "dev",
        "testing": "stag",
        "production": "prod",
    }.get(PAAS_V2_ENVIRONMENT)


class FancyDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)


def _has_format(value: dict) -> bool:
    if isinstance(value, dict):
        return "value" in value
    return False


def _get_format(value: dict, context):
    for context_key in context.keys():
        if value.get(context_key):
            value[context_key] = FancyDict(value[context_key])
    try:
        return value["value"].format(**context)
    except AttributeError:
        return value["value"].format(**value)


def load_env():
    env = os.getenv("BKAPP_ENV_FILE", "")
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = os.path.join(project_path, f"{ENVIRONMENT}.env.yml" if not env else f"{env}.{ENVIRONMENT}.env.yml")
    assert os.path.exists(env), f"{env} not exists"
    with open(env, encoding="utf-8") as f:
        content = yaml.load(f, Loader=yaml.FullLoader)
    assert content, f"{env} must have content"
    return content


def load_settings():
    module = importlib.import_module("config.default")
    context = {"settings": module, "env": FancyDict(os.environ)}
    env = load_env()
    settings = env.get("settings", {})
    result_settings = {}
    for key, value in settings.items():
        if _has_format(value):
            result_settings[key] = _get_format(value, context)
            continue
        if key in ["FEATURE_TOGGLE"]:
            original_value = getattr(module, key, {})
            assert isinstance(original_value, dict), "FEATURE_TOGGLE need is a object"
            original_value.update(value)
            result_settings[key] = original_value
            continue
        result_settings[key] = value
    return result_settings


def load_domains(settings):
    context = {"settings": settings, "env": FancyDict(os.environ)}
    env = load_env()
    domains = env.get("domains", {})
    result_domains = {}
    for key, value in domains.items():
        result_domains[key] = value.format(**context)
    return result_domains
