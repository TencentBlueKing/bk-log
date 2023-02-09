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

MODULE_BKUNIFYLOGBEAT = "bkunifylogbeat"
MODULE_GSEAGENT = "gse_agent"

STEP_CHECK_BKUNIFYLOGBEAT_BIN_FILE = "bin_file"
STEP_CHECK_BKUNIFYLOGBEAT_PROCESS = "process"
STEP_CHECK_BKUNIFYLOGBEAT_MAIN_CONFIG = "main_config"
STEP_CHECK_BKUNIFYLOGBEAT_CONFIG = "config"
STEP_CHECK_BKUNIFYLOGBEAT_HOSTED = "hosted"
STEP_CHECK_BKUNIFYLOGBEAT_HEALTHZ = "healthz"

STEP_CHECK_GSEAGENT_PROCESS = "process"
STEP_CHECK_GSEAGENT_SOCKET = "socket"
STEP_CHECK_GSEAGENT_SOCKET_QUEUE_STATUS = "socket_queue_status"
STEP_CHECK_GSEAGENT_DATASERVER_PORT = "dataserver_port"

COLLECTOR_MAIN_CONFIG_FILE_NAME = "bkunifylogbeat.conf"

DATASERVER_PORT = "58625"

subscription_id = 0
socket_between_gse_agent_and_beat = "/var/run/ipc.state.report"
gse_path = "/usr/local/gse/"
collector_bin_path = os.path.join(gse_path, "plugins/bin", MODULE_BKUNIFYLOGBEAT)
collector_etc_main_config_path = os.path.join(gse_path, "plugins/etc", COLLECTOR_MAIN_CONFIG_FILE_NAME)
collector_etc_path = os.path.join(gse_path, "plugins/etc", MODULE_BKUNIFYLOGBEAT)
procinfo_file_path = os.path.join(gse_path, "agent/etc/procinfo.json")
config_name_suffix = "%s_sub_" % MODULE_BKUNIFYLOGBEAT

check_result = {"status": False, "data": []}


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
    def __init__(self, module, item, status=False, message=""):
        self.module = module
        self.item = item
        self.status = status
        self.message = message

    def add_to_result(self):
        d = {
            "module": self.module,
            "item": self.item,
            "status": self.status,
            "message": self.message,
        }
        global check_result
        check_result["data"].append(d)


class BKUnifyLogBeatCheck(object):
    def __init__(self):
        self.subscription_id = subscription_id

    @staticmethod
    def check_bin_file():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_BIN_FILE)
        if os.path.exists(collector_bin_path):
            result.status = True
        result.add_to_result()

    @staticmethod
    def check_process():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_PROCESS)
        output = get_command("ps -ef | grep bkunifylogbeat | awk '{print $2}' | xargs pwdx")
        if gse_path not in str(output):
            result.message = "bkunifylogbeat is not running"
            result.add_to_result()
            return

        pid_to_dir = [line.split(":") for line in output.split("\n") if line.strip()]
        pid = pid_to_dir[0][0]
        for pid_dir in pid_to_dir:
            pid, bin_dir = pid_dir
            if bin_dir.strip().startswith(gse_path):
                break

        # 是否频繁重启
        restart_times = 10
        restart_records_file = "/tmp/bkc.log"
        today = datetime.datetime.now().strftime("%Y%m%d")
        output = get_command(
            "cat {} | grep {} | grep {} | wc -l".format(restart_records_file, today, MODULE_BKUNIFYLOGBEAT)
        )
        if not output or int(output) > restart_times:
            result.message = "restart/reload times is over %d" % restart_times
            result.add_to_result()
            return

        # 当前资源
        cpu_usage = get_command("ps aux | grep %s | awk '{print $3}' | head -n 1" % pid)
        mem_usage = get_command("ps aux | grep %s | awk '{print $4}' | head -n 1" % pid)
        result.message = "cpu_usage: {}%, mem_usage: {}%".format(str(cpu_usage), str(mem_usage))
        result.status = True
        result.add_to_result()

    @staticmethod
    def check_main_config():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_MAIN_CONFIG)
        if not os.path.exists(collector_etc_main_config_path):
            result.message = "main config file is not exists"
            result.add_to_result()
            return

        output = get_command(
            "sed -n '/^bkunifylogbeat.multi_config/,/^$/p' %s | grep path | awk -F: '{print $2}'"
            % collector_etc_main_config_path
        )
        output = output.replace(" ", "")
        path_list = output.split("\n")
        if collector_etc_path not in path_list:
            result.message = "multi_config not have path [{}]".format(collector_etc_main_config_path)
            result.add_to_result()
            return

        result.status = True
        result.add_to_result()

    @staticmethod
    def check_config():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_CONFIG)
        real_config_name = ""
        g = os.walk(collector_etc_path)
        for path, dir_list, file_list in g:
            for file_name in file_list:
                config_name_suffix_with_subscription_id = "%s%d" % (config_name_suffix, subscription_id)
                if config_name_suffix_with_subscription_id in file_name:
                    real_config_name = file_name
                    result.message = "real_config_name: %s" % real_config_name
                    break
        if real_config_name:
            result.status = True
        result.add_to_result()

    @staticmethod
    def check_gseagent_hosted():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_HOSTED)
        output = get_command("cat {} | grep {}".format(procinfo_file_path, MODULE_BKUNIFYLOGBEAT))
        if MODULE_BKUNIFYLOGBEAT in str(output):
            result.status = True
        result.add_to_result()

    @staticmethod
    def check_collector_healthz():
        result = Result(MODULE_BKUNIFYLOGBEAT, STEP_CHECK_BKUNIFYLOGBEAT_HEALTHZ)
        result.message = get_command("%s healthz" % collector_bin_path)
        result.status = True
        result.add_to_result()


class GseAgentCheck(object):
    @staticmethod
    def check_process():
        result = Result(MODULE_GSEAGENT, STEP_CHECK_GSEAGENT_PROCESS)
        output = get_command("netstat -antulp | grep %s | grep LISTEN | awk '{print $7}'" % MODULE_GSEAGENT)
        if MODULE_GSEAGENT in str(output):
            result.status = True
        result.add_to_result()

    @staticmethod
    def check_socket_between_gse_agent_and_beat():
        result = Result(MODULE_GSEAGENT, STEP_CHECK_GSEAGENT_SOCKET)
        if os.path.exists(socket_between_gse_agent_and_beat):
            result.status = True
        result.add_to_result()

    @staticmethod
    def check_socket():
        result = Result(MODULE_GSEAGENT, STEP_CHECK_GSEAGENT_SOCKET_QUEUE_STATUS)
        output = get_command("ss -x -p | grep -E 'REC|%s' |awk '{print $6}'" % socket_between_gse_agent_and_beat)
        if not output:
            result.message = "socket not used"
            result.add_to_result()
            return
        port = output.split("-")[-1]
        queue_status = get_command("ss -x -p | grep -E 'Rec|%s' |awk 'NR>1{print $3;print $4}'" % port)
        queue_status = list(map(int, queue_status.split("\n")))
        if any(queue_status):
            result.message = "socket queue blocking"
            result.add_to_result()
            return
        result.status = True
        result.add_to_result()

    @staticmethod
    def check_dataserver():
        result = Result(MODULE_GSEAGENT, STEP_CHECK_GSEAGENT_DATASERVER_PORT)
        output = get_command("netstat -anplut | grep %s" % DATASERVER_PORT)
        if not output:
            result.message = "dataserver not exist"
            result.add_to_result()
            return
        result.status = True
        result.add_to_result()


def _get_opt_parser():
    """get option parser"""
    opt_parser = OptionParser()

    opt_parser.add_option(
        "-p", "--gse_path", action="store", type="string", dest="path", help="""gse_path""", default=""
    )

    opt_parser.add_option(
        "-s",
        "--subscription_id",
        action="store",
        type="int",
        dest="subscription_id",
        help="""subscription_id""",
        default=subscription_id,
    )

    opt_parser.add_option(
        "-i",
        "--ipc_socket_file",
        action="store",
        type="string",
        dest="ipc_socket_file",
        help="""ipc_socket_file""",
        default=socket_between_gse_agent_and_beat,
    )

    return opt_parser


def arg_parse():
    global gse_path
    global subscription_id
    global socket_between_gse_agent_and_beat
    global collector_bin_path
    global collector_etc_main_config_path
    global collector_etc_path
    global procinfo_file_path

    parser = _get_opt_parser()
    (options, args) = parser.parse_args(sys.argv)

    if options.path:
        gse_path = options.path
        collector_bin_path = os.path.join(gse_path, "plugins/bin", MODULE_BKUNIFYLOGBEAT)
        collector_etc_main_config_path = os.path.join(gse_path, "plugins/etc", COLLECTOR_MAIN_CONFIG_FILE_NAME)
        collector_etc_path = os.path.join(gse_path, "plugins/etc", MODULE_BKUNIFYLOGBEAT)
        procinfo_file_path = os.path.join(gse_path, "agent/etc/procinfo.json")
    if options.subscription_id:
        subscription_id = options.subscription_id
    if options.ipc_socket_file:
        socket_between_gse_agent_and_beat = options.ipc_socket_file


def main():
    arg_parse()

    bkunifylogbeat_checker = BKUnifyLogBeatCheck()
    bkunifylogbeat_checker.check_bin_file()
    bkunifylogbeat_checker.check_process()
    bkunifylogbeat_checker.check_main_config()
    bkunifylogbeat_checker.check_config()
    bkunifylogbeat_checker.check_gseagent_hosted()
    bkunifylogbeat_checker.check_collector_healthz()

    gse_agent_checker = GseAgentCheck()
    gse_agent_checker.check_process()
    gse_agent_checker.check_socket_between_gse_agent_and_beat()
    gse_agent_checker.check_socket()
    gse_agent_checker.check_dataserver()

    global check_result
    if all([i["status"] for i in check_result["data"]]):
        check_result["status"] = True

    print(json.dumps(check_result))


if __name__ == "__main__":
    main()
