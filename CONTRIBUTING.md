# Contributing to 蓝鲸日志平台

蓝鲸团队秉持开放的态度，欢迎志同道合的开发者一起贡献项目。在开始之前，请认真阅读以下指引。

## 代码协议

[MIT LICENSE](LICENSE.txt) 为 BK-LOG 的开源协议，任何人贡献的代码也会受此协议保护，贡献代码前也请明确是否可以接受该协议。

## 如何开始

想要贡献代码，建议请先参照已有的特性文档和开发环境构建文档。

## Issues

蓝鲸团队使用 [issues](https://github.com/TencentBlueKing/bk-log/issues) 进行 bugs 追踪、特性追踪等。

当提交相关的 bug 时，请查找已存在或者相类似的 issue，从而保证不存在冗余。

如果确认该 bug 是一个新的 bug，提交时请包含以下的信息：

* 你所使用的操作系统信息
* 当前你使用的版本信息，例如 version，commitid
* 出现问题时，相关模块的日志输出
* 重现该问题的准确步骤，例如提交相关重现脚本/工具会比大量描述更有用一些

## Pull Request

Pull Request (简称 PR）是我们使用的主流工作方式，请参考 [Github 文档](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)了解 PR 的功能。我们采用 ["fork and pull"](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/getting-started/about-collaborative-development-models#fork-and-pull-model) 的开发模式，即开发者首先向自己的 fork 仓库提交变更，然后向上游仓库发起 PR。

除非有特殊约定，所有 PR 提交的目标分支应始终选择`master`分支。注意提交 PR 时带着 Issus 的编号。

此仓库遵循  *no merge-commit* 原则，当遇到代码冲突时，应使用 rebase （而非 merge）来进行处理。例如，当需要将 master 分支代码合并到特性分支代码进行测试时，始终使用 rebase 进行操作。请在将个人仓库（分支）下产生的零碎 commit 尽量压缩到与之相关的 commit 中，并填写有意义的 commit message，请参考[相关资料](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)。

提交建议的步骤：

	1. fork 代码仓库（第一次操作）；
	2. 填写 issue；
	3. 在个人仓库下切分支开发，建议按照"<分类>/<issue id>"来设定，比如: feature/#1；
	4. 进行开发，此阶段可以根据开发进度自行设置commit；
	5. 完成自测，请确保完成相关 issue 功能；
	6. 使用 `git rebase` 功能准备好发起 PR 的 commit，严格按照 commit message 的规范来填写提交信息；
	7. 向主仓库发起 PR（title 仓库默认使用 commit message），并指定好 code review 的负责人；
	8. 按照 CR 的意见修改代码。为了避免 CR 负责人在本地反复清理 CR 分支此阶段允许 PR 发起人提交修复类的小 commit，一般使用`fixup:`作为 commit 前缀
	9. CR 通过；
	10. PR 提交者需要将个人仓库下的 fixup commit 进行 `git rebase`，确保只有一个 commit；
	11. 仓库 master 角色完成 merge（仓库仅开放 rebase merging 选项）；
	12. 关闭 issue

## GIT message 规范

因不同团队不同的项目管理下会有不同的代码提交注释，规范化开源下对不同团队提交信息，做了不同的提交标记以规范化区分提交内容：

```
git commit -m '标记: 提交的概要注释 issue #123'
```

示例:

```shell
git commit -m 'bugfix: 修复提交问题 #29'
```

### 标记说明

| 标记 | 说明 |
| :--- | :---: |
| feature | 新特性 |
| bugfix | 不重要的修改（换行，拼写错误等） |
| optimization | 功能优化 |
| sprintfix | 未上线代码修改 （功能模块未上线部分bug） |
| refactor | 功能重构 |
| test | 增加测试代码 |
| docs | 编写文档 |
| merge | 分支合并及冲突解决 |