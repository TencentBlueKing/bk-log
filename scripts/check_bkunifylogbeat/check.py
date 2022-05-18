#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import getopt


collector_home_path = "/usr/local/gse/plugins/"
collector_bin_path = "bin/bkunifylogbeat"
collector_etc_path = "etc/bkunifylogbeat"


def status_check():
    """
    Collector running status detection
    """

    pass


def config_check():
    """
    Collector config file detection
    """
    pass


def collect_processor_check():
    """
    Collection progress detection
    """
    pass


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

    print(opts)
    print(args)


def main():
    arg_parse()

    status_check()
    config_check()
    collect_processor_check()


if __name__ == "__main__":
    main()
