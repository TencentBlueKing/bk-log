# -*- coding: utf-8 -*-
import typing

Scope = typing.Dict[str, typing.Union[int, str]]

ScopeList = typing.List[Scope]

MetaData = Scope

TreeNode = typing.Dict[str, typing.Any]

ReadableTreeNode = typing.Dict[str, typing.Any]

HostInfo = typing.Dict[str, typing.Any]

FormatHostInfo = typing.Dict[str, typing.Any]

Condition = typing.Dict[str, typing.Union[int, str, typing.Iterable]]

Template = typing.Dict[str, typing.Any]

TemplateNode = typing.Dict[str, typing.Any]

DynamicGroup = typing.Dict[str, typing.Any]
