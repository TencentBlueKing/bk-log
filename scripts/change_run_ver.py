# -*- coding: utf-8 -*-
"""
此文件位于 PROJECT_ROOT/scripts/change_run_ver.py
"""
import os
import shutil
from argparse import ArgumentParser

# 忽略的目录，在do_copy中不进行拷贝
IGNORE_DIR = []
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_ROOT)
SITES_ROOT = os.sep.join([PROJECT_ROOT, "sites"])


class Command(object):
    def change_run_ver(self, run_ver):

        run_ver_dir = self.get_run_ver_dir(run_ver)
        self.do_copy(run_ver_dir)
        print("Changing RUN_VER to %s" % run_ver)

    @staticmethod
    def get_run_ver_dir(run_ver):
        """
        根据版本获取配置所在的根目录
        :param run_ver:
        :return:
        """
        run_ver_dir = os.sep.join([SITES_ROOT, run_ver])
        return run_ver_dir

    @staticmethod
    def do_copy(run_ver_dir):
        """
        执行拷贝命令
        :param run_ver_dir:
        :return:
        """
        # 拷贝通用配置
        # public_settings_path = os.sep.join([SITES_ROOT, 'common_settings.py'])
        # shutil.copy2(public_settings_path, PROJECT_ROOT)

        # 拷贝部署相关的目录至根目录
        deploy_dir = os.sep.join([run_ver_dir, "deploy"])

        for _path in os.listdir(deploy_dir):
            if _path in IGNORE_DIR:
                continue

            _abspath = os.sep.join([deploy_dir, _path])
            if os.path.isfile(_abspath):
                print("[Handling File]: %s" % _abspath)
                shutil.copy2(_abspath, PROJECT_ROOT)

            if os.path.isdir(_abspath):
                print("[Handling Directory]: %s" % _abspath)
                _dst_dir = os.sep.join([PROJECT_ROOT, _path])
                shutil.rmtree(_dst_dir, ignore_errors=True)
                shutil.copytree(_abspath, _dst_dir)


def main():
    parser = ArgumentParser(description="Change App Run Version")
    parser.add_argument("-V", "--run_ver", help="APP RUN VERSION: default | ieod | tencent")
    parser.add_argument("-i", "--ignore_dir", help="Ignore Dir, split with comma(,)", default="api")
    args = parser.parse_args()
    extend_ignore_dir = args.ignore_dir.split(",")
    IGNORE_DIR.extend(extend_ignore_dir)

    command = Command()
    command.change_run_ver(args.run_ver)


if __name__ == "__main__":
    main()
