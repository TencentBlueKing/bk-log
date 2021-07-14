# Contributing to BK-LOG

The BlueKing team upholds an open attitude and welcomes like-minded developers to contribute to the project. Before you start, please read the following instructions carefully.

## Code License

[MIT LICENSE](LICENSE.txt) is the open source license of BK-LOG. Code contributed by anyone is protected by this license. Please make sure that you can accept the license before contributing your code.

## How to Get Started

If you want to contribute your code, it is recommended to refer to existing documentation about features and development environment setup.

## Issues

The BlueKing team uses [issues](https://github.com/TencentBlueKing/bk-log/issues) to track bugs, feature, etc.

When submitting a relevant bug, please search for existing or similar issues to ensure that there is no redundancy.

If you confirm that this is a new bug, please include the following information when submitting.

* Information about the operating system you use.
* Information about the current version you use, such as version, commitid.
* Log outputs of relevant modules when the problem occurs.
* Exact steps to reproduce the bug. For example, submitting relevant reproduction scripts/tools is more useful than long description.

## Pull Request

Pull Request (PR for short) is the mainstream work method we use, please refer to [Github Documentation](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) understand the function of PR. We use ["fork and pull"](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/getting-started/about-collaborative-development-models#fork-and-pull-model) development model, that is, developers first submit changes to their fork warehouse, and then initiate a PR to the upstream warehouse.

Unless there is a special agreement, the target branch of all PR submissions should always choose the `master` branch. Pay attention to the Issus number when submitting the PR.

This repository follows the *no merge-commit* principle. When encountering code conflicts, rebase (not merge) should be used for processing. For example, when you need to merge the master branch code into the feature branch code for testing, always use rebase to perform the operation. Please compress the fragmented commits generated under the personal warehouse (branch) into related commits as much as possible, and fill in a meaningful commit message, please refer to [Related Information](https://www.atlassian.com/git/tutorials/merging-vs-rebasing).

Steps to submit suggestions:

1. Fork the code warehouse (first operation);
2. Fill in the issue;
3. Branch development under the personal warehouse, it is recommended to set according to "<category>/<issue id>", such as: feature/#1;
4. During development, you can set commit according to the development progress at this stage;
5. Complete the self-test, please make sure to complete the related issue function;
6. Use the `git rebase` function to prepare to initiate a PR commit, and fill in the submission information in strict accordance with the commit message specification;
7. Initiate a PR to the main warehouse (the title warehouse uses commit message by default), and designate the person in charge of the code review;
8. Modify the code according to CR's comments. In order to prevent the head of CR from repeatedly cleaning up the CR branch locally, at this stage, the PR initiator is allowed to submit repaired small commits, generally using `fixup:` as the commit prefix
9. CR passed;
10. The PR submitter needs to perform `git rebase` the fixup commit under the personal warehouse to ensure that there is only one commit;
11. The warehouse master role completes the merge (the warehouse only opens the rebase merging option);
12. Close the issue

## GIT message specification

Because different teams and different project management will have different code submission comments, different teams submit information under standardized open source, and different submission marks have been made to standardize and distinguish the submitted content:

```
git commit -m 'mark: summary comment for submission issue #123'
```

Example:

```shell
git commit -m 'bugfix: fix commit problem #29'
```

### Mark description

| Mark | Description |
| :--- | :---: |
| feature | New feature development |
| bugfix | Bug fixes released |
| optimization | Functional optimization |
| sprintfix | Code modification not online (bug of function module not online) |
| refactor | Refactor code/optimize configuration &amp; parameters/optimize logic and functions |
| test | test case related |
| docs | Documentation |
| merge | Branch merge and conflict resolution |
