#! /usr/bin/env python
# -*- coding: utf-8 -*-


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
