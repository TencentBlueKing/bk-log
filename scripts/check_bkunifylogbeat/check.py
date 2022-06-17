#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import subprocess
import sys
from optparse import OptionParser
import datetime
import platform
import json

STEP_CHECK_BIN_FILE = "check_bin_file"
STEP_CHECK_PROCESS = "check_process"
STEP_CHECK_CONFIG = "check_config"
STEP_CHECK_COLLECTOR_HEALTHZ = "check_collector_healthz"

subscription_id = 0
collector_home_path = "/usr/local/gse/plugins/"
collector_bin_path = os.path.join(collector_home_path, "bin/bkunifylogbeat")
collector_etc_path = os.path.join(collector_home_path, "etc/bkunifylogbeat")
config_name_suffix = "bkunifylogbeat_sub_"


def convert_to_str(t):
    if platform.python_version()[0] == "3":
        if isinstance(t, bytes):
            return t.decode("utf-8")
    return t


def get_command(cmd):
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return convert_to_str(output).strip()


class Result(object):
    def __init__(self, item, status=False, data=None, message=""):
        self.item = item
        self.status = status
        self.data = data
        self.message = message

    def print_json(self):
        d = {"item": self.item, "status": self.status, "data": self.data, "message": self.message}
        print(json.dumps(d))


class BKUnifyBeatCheck(object):
    def __init__(self):
        self.subscription_id = subscription_id

    @staticmethod
    def check_bin_file():
        result = Result(STEP_CHECK_BIN_FILE)
        if not os.path.exists(collector_bin_path):
            result.message = "bkunifylogbeat is not exist"
            result.print_json()
            sys.exit(1)
        result.status = True
        result.print_json()

    @staticmethod
    def check_process():
        result = Result(STEP_CHECK_PROCESS)
        output = get_command("ps -ef | grep bkunifylogbeat | awk '{print $2}' | xargs pwdx")
        if collector_home_path not in str(output):
            result.message = "bkunifylogbeat is not running"
            result.print_json()
            sys.exit(1)

        pid_to_dir = [line.split(":") for line in output.split("\n") if line.strip()]
        pid = pid_to_dir[0][0]
        for pid_dir in pid_to_dir:
            pid, bin_dir = pid_dir
            if bin_dir.strip().startswith(collector_home_path):
                break

        # 是否频繁重启
        restart_times = 10
        restart_records_file = "/tmp/bkc.log"
        today = datetime.datetime.now().strftime("%Y%m%d")
        output = get_command("grep {} {} | wc -l".format(today, restart_records_file))
        if not output or int(output) > restart_times:
            result.message = "restart/reload times is over %d" % restart_times
            result.print_json()
            sys.exit(1)

        # 当前资源
        cpu_usage = get_command("ps aux | grep %s | awk '{print $3}' | head -n 1" % pid)
        mem_usage = get_command("ps aux | grep %s | awk '{print $4}' | head -n 1" % pid)
        result.data = {"cpu_usage": "%s%%" % (str(cpu_usage)), "mem_usage": "%s%%" % (str(mem_usage))}
        result.status = True
        result.print_json()

    @staticmethod
    def check_config():
        result = Result(STEP_CHECK_CONFIG)
        real_config_name = ""
        g = os.walk(collector_etc_path)
        for path, dir_list, file_list in g:
            for file_name in file_list:
                config_name_suffix_with_subscription_id = "%s%d" % (config_name_suffix, subscription_id)
                if config_name_suffix_with_subscription_id in file_name:
                    real_config_name = file_name
                    result.message = "real_config_name: %s" % real_config_name
                    break
        if not real_config_name:
            result.message = "config_file is not exist"
            result.print_json()
            sys.exit(1)

        result.status = True
        result.print_json()

    @staticmethod
    def check_collector_healthz():
        result = Result(STEP_CHECK_COLLECTOR_HEALTHZ)
        result.message = get_command("%s healthz" % collector_bin_path)
        result.status = True
        result.print_json()


def _get_opt_parser():
    """get option parser"""
    opt_parser = OptionParser()

    opt_parser.add_option(
        "-p", "--path", action="store", type="string", dest="path", help="""collector_home_path""", default=""
    )

    opt_parser.add_option(
        "-s",
        "--subscription_id",
        action="store",
        type="int",
        dest="subscription_id",
        help="""subscription_id""",
        default=0,
    )

    return opt_parser


def arg_parse():
    global collector_home_path
    global subscription_id

    parser = _get_opt_parser()
    (options, args) = parser.parse_args(sys.argv)

    if options.path:
        collector_home_path = options.path
    if options.subscription_id:
        subscription_id = options.subscription_id


def main():
    arg_parse()

    c = BKUnifyBeatCheck()
    c.check_bin_file()
    c.check_process()
    c.check_config()
    c.check_collector_healthz()


if __name__ == "__main__":
    main()
