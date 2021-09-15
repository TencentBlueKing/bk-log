#! /usr/bin/env python
# -*- coding: utf-8 -*-
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


class ScanPoFile(object):
    def __init__(self):
        pass

    def safe_encode(s):
        try:
            return s.decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            return s

    def scan(self, po_file):
        write_list = []
        with open(po_file, "rb") as f:
            ori_content = []
            for line in f.readlines():
                line = self.safe_encode(line)
                if line.startswith('msgid "'):
                    ori_content = [
                        "msgstr" + line[5:],
                    ]
                    write_list.append(line)
                elif line.startswith('msgstr ""') and ori_content:
                    write_list.extend(ori_content)
                    ori_content = []
                elif line.startswith('"') and ori_content:
                    ori_content.append(line)
                    write_list.append(line)
                else:
                    write_list.append(line)

        content = "".join(write_list)
        with open(po_file, "wb") as f:
            f.write(content.encode("utf-8"))
        pass


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="fill .po file with excel resource")
    parser.add_argument("-p", "--pofile", help=".po file to handle")
    args = parser.parse_args()

    scanner = ScanPoFile()
    scanner.scan(args.pofile)


if __name__ == "__main__":
    main()
