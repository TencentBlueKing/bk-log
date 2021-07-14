#  1 . 背景

为了尽早发现代码问题，防止不符合规范的代码提交到仓库，强烈推荐每位开发者配置 `pre-commit` 代码提交前检查

# 2 . Git Hooks 本地配置

`pre-commit` 检查通过本地配置实现，因此每个开发者在开发之前都必须先配好本地的 Git Hooks。

推荐使用 [pre-conmmit](https://pre-commit.com/) 框架对 Git Hooks 进行配置及管理。**pre-commit**是由 python 实现的，用于管理和维护多个 pre-commit hooks 的实用框架。它提供了插件式的管理机制，并拥有大量的官方与第三方插件（需要时可自行开发），能够快速实现常见的代码检查任务，如 `eslint` 检查（支持跨语言），`flake8` 检查，`isort` 代码美化等。


## 配置方式

1. 将附录中的 `.pre-commit-config.yaml` 和 `.flake8` 文件复制到项目根目录下
2. 在项目根目录下执行该以下命令

```sh
# 安装 pre-commit
pip install pre-commit

# 初始化 hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

执行后，查看 `.git/hooks` 目录，若存在名为 `pre-commit` 和 `commit-msg` 新文件，则配置成功 。

## 触发 Git Hooks

- pre-commit 代码检查无需手动触发，只要执行 `git commit ` 命令，就会自动触发（无论是在终端还是IDE）。请注意，代码检查的范围只是本次提交所修改的文件，而非全局。

- 若代码检查不通过，提交会被中断。可以根据具体的错误信息去调整代码，只有所有的检查项全部通过方可 push。
	

- 配置 `pre-commit` 后，第一次执行 `git commit` 命令时会联网下载所需的插件依赖，大概需要一分钟的时间，请耐心等待。

# 3 . 常用插件说明

## pyupgrade

提升Python代码风格

https://github.com/asottile/pyupgrade

## python-modernize

**【Python2项目专用】** 将python2风格代码自动转换为2-3兼容风格

https://python-modernize.readthedocs.io/en/latest/fixers.html#

## check-merge-conflict

通过匹配conflict string，检查是否存在没有解决冲突的代码

## isort

自动调整 python 代码文件内的 import 顺序

若该项结果为 `failed`，通过 `git diff` 查看自动调整的地方，确认无误后，重新 `git add` 和 `git commit` 即可

## autopep8

根据 `.flake8` 给出的配置自动调整 python 代码风格。

若该项结果为 `failed`，通过 `git diff` 查看自动调整的地方，确认无误后，重新 `git add` 和 `git commit` 即可

## flake8

根据 `.flake8` 给出的配置检查代码风格。

若该项结果为 `failed`，需要根据给出的错误信息手动进行调整。（autopep8 会尽可能地把能自动修复的都修复了，剩下的只能手动修复）


关于 flake8 规则代码与具体示例，可查阅 https://lintlyci.github.io/Flake8Rules/

## check-commit-message

检查 git 提交信息是否符合蓝鲸 SaaS 开发规范，需要将附录中的 `check_commit_message.py` 拷贝到项目中


commit message 必须包含以下前缀之一:

`feature`     	- 新特性

`bugfix`      	- 线上功能bug

`minor`       	- 不重要的修改（换行，拼写错误等）

`optimization`	- 功能优化

`sprintfix`   	- 未上线代码修改 （功能模块未上线部分bug）

`refactor`    	- 功能重构

`test`        	- 增加测试代码

`docs`        	- 编写文档

`merge`       	- 分支合并及冲突解决


# 4. 附录

## .pre-commit-config.yaml

```yaml
default_stages: [commit]
repos:
  - repo: https://github.com/asottile/pyupgrade
    rev: v1.21.0
    hooks:
      - id: pyupgrade
  - repo: https://github.com/python-modernize/python-modernize
    rev: 5650894e684250b8dd7a7d552adeea98eb8663ba
    hooks:
      - id: python-modernize
        args: [--write, --fix=default, --nobackups, --future-unicode]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v2.1.0
    hooks:
    - id: check-merge-conflict
  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v4.3.17
    hooks:
    - id: isort
  - repo: https://github.com/pre-commit/mirrors-autopep8
    rev: v1.4.3
    hooks:
    - id: autopep8
      args: [-i, --global-config=.flake8, -v]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v2.1.0
    hooks:
    - id: flake8
  - repo: local
    hooks:
      - id: check-commit-message
        name: Check commit message
        entry: python check_commit_message.py
        language: system
        stages: [commit-msg]
```

## .flake8

```
[flake8]
exclude = .git,__pycache__,docs,old,build,dist,venv,webpack
max-line-length = 120
max-complexity = 25
ignore = E731,F401,F403,F841,F9,W503
```

## check_commit_message.py

```python
# -*- coding: utf-8 -*-
"""
校验提交信息是否包含规范的前缀
"""
from __future__ import absolute_import, print_function, unicode_literals

import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    # py3
    pass


ALLOWED_COMMIT_MSG_PREFIX = [
    ('feature', '新特性'),
    ('bugfix', '线上功能bug'),
    ('minor', '不重要的修改（换行，拼写错误等）'),
    ('optimization', '功能优化'),
    ('sprintfix', '未上线代码修改 （功能模块未上线部分bug）'),
    ('refactor', '功能重构'),
    ('test', '增加测试代码'),
    ('docs', '编写文档'),
    ('merge', '分支合并及冲突解决'),
]


def get_commit_message():
    args = sys.argv
    if len(args) <= 1:
        print("Warning: The path of file `COMMIT_EDITMSG` not given, skipped!")
        return 0
    commit_message_filepath = args[1]
    with open(commit_message_filepath, 'r') as fd:
        content = fd.read()
    return content.strip().lower()


def main():
    content = get_commit_message()
    for prefix in ALLOWED_COMMIT_MSG_PREFIX:
        if content.startswith(prefix[0]):
            return 0

    else:
        print("Commit Message 不符合规范！必须包含以下前缀之一：".encode('utf8'))
        [print("%-12s\t- %s" % prefix) for prefix in ALLOWED_COMMIT_MSG_PREFIX]

    return 1


if __name__ == '__main__':
    exit(main())

```