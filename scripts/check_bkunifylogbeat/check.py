#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import subprocess
import sys
import getopt
import datetime
import platform


def convert_to_str(t):
    if platform.python_version()[0] == "3":
        if isinstance(t, bytes):
            return t.decode("utf-8")
    return t


collector_home_path = "/usr/local/gse/plugins/"
collector_bin_path = "bin/bkunifylogbeat"
collector_etc_path = "etc/bkunifylogbeat"


def get_command(cmd):
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return convert_to_str(output).strip()


def status_check():
    """
    Collector running status detection
    """
    # 采集器是否安装
    bin_path = os.path.join(collector_home_path, collector_bin_path)
    if not os.path.exists(bin_path):
        print("[-] bin file not exists")
        sys.exit(1)
    else:
        print("[+] check bin file ok")

    # 检测进程是否存在
    output = get_command("ps -ef | grep bkunifylogbeat | awk '{print $2}' | xargs pwdx")
    if collector_home_path not in str(output):
        print("[-] not running")
        sys.exit(1)
    else:
        print("[+] running ok")

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
        print("[-] restart/reload times is over %d" % restart_times)
        sys.exit(1)
    else:
        print("[+] check %s is ok" % restart_records_file)

    # 当前资源
    cpu_usage = get_command("ps aux | grep %s | awk '{print $3}' | head -n 1" % pid)
    mem_usage = get_command("ps aux | grep %s | awk '{print $4}' | head -n 1" % pid)
    print("[+] current cpu usage %s%%" % str(cpu_usage))
    print("[+] current mem usage %s%%" % str(mem_usage))

    # GSE procfile.json资源占用


def config_check():
    """
    Collector config file detection
    """
    pass


def collect_processor_check():
    """
    Collection progress detection
    """
    bin_path = os.path.join(collector_home_path, collector_bin_path)
    print(get_command("%s healthz" % bin_path))


def arg_parse():
    global collector_home_path

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:", ["help", "path"])
    except getopt.GetoptError as e:
        print("parse args error: %s", e)
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("This is help message.")
            sys.exit()
        elif opt in ("-p", "--path"):
            collector_home_path = arg

    # print(opts)
    # print(args)


def main():
    arg_parse()

    status_check()
    config_check()
    collect_processor_check()


if __name__ == "__main__":
    main()
