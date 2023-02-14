# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from blueapps.conf.default_settings import APP_CODE, BASE_DIR

APP_CODE = os.environ.get("APP_ID", APP_CODE)


# copy from blueapps
def get_logging_config_dict(settings_module):
    log_class = "logging.handlers.RotatingFileHandler"
    log_level = settings_module.get("LOG_LEVEL", "INFO")

    if settings_module.get("IS_LOCAL", False):
        log_dir = os.path.join(os.path.dirname(BASE_DIR), "logs", APP_CODE)
        log_name_prefix = os.getenv("BKPAAS_LOG_NAME_PREFIX", APP_CODE)
        logging_format = {
            "format": (
                "%(levelname)s [%(asctime)s] %(pathname)s "
                "%(lineno)d %(funcName)s %(process)d %(thread)d "
                "\n \t %(message)s \n"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    else:
        log_dir = settings_module.get("LOG_DIR_PREFIX", "/app/v3logs/")
        # rand_str = "".join(random.sample(string.ascii_letters + string.digits, 4))
        rand_str = "with"  # 这里固定字符串，如果随机的话，会导致日志文件太多，在worker的场景下，会不停重启，另外长期运行的也会，日志轮转没办法管理
        log_name_prefix = "{}-{}".format(os.getenv("BKPAAS_PROCESS_TYPE"), rand_str)

        logging_format = {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": (
                "%(levelname)s %(asctime)s %(pathname)s %(lineno)d " "%(funcName)s %(process)d %(thread)d %(message)s"
            ),
        }
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": logging_format,
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "root": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-django.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "component": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-component.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "mysql": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-mysql.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "celery": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-celery.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
        },
        "loggers": {
            "django": {"handlers": ["null"], "level": "INFO", "propagate": True},
            "django.server": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "django.request": {
                "handlers": ["root"],
                "level": "ERROR",
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": ["mysql"],
                "level": log_level,
                "propagate": True,
            },
            "component": {
                "handlers": ["component"],
                "level": log_level,
                "propagate": True,
            },
            "celery": {"handlers": ["celery"], "level": log_level, "propagate": True},
            "blueapps": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            "root": {"handlers": ["root"], "level": log_level, "propagate": True},
            "iam": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            "app": {"handlers": ["root"], "level": log_level, "propagate": True},
            "bk_dataview": {"handlers": ["root"], "level": log_level, "propagate": True},
            "bk_monitor": {"handlers": ["root"], "level": log_level, "propagate": True},
        },
    }

    # 可选，开启UDP日志上报
    if os.getenv("BKAPP_UDP_LOG", "off") == "on":
        log_udp_server_host = os.getenv("BKAPP_UDP_LOG_SERVER_HOST", "")
        log_udp_server_port = int(os.getenv("BKAPP_UDP_LOG_SERVER_PORT", 0))
        logging_config["handlers"]["udp"] = {
            "formatter": "verbose",
            "class": "apps.utils.log.UdpHandler",
            "host": log_udp_server_host,
            "port": log_udp_server_port,
        }
        for _, v in logging_config["loggers"].items():
            v["handlers"].append("udp")

    # 可选，开启OT日志上报
    if os.getenv("BKAPP_OTLP_LOG", "off") == "on":
        logging_config["handlers"]["otlp"] = {
            "class": "apps.utils.log.OTLPLogHandler",
        }
        for _, v in logging_config["loggers"].items():
            v["handlers"].append("otlp")

    return logging_config
