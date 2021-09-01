![](docs/resource/img/logo.png)
---
[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](https://github.com/TencentBlueKing/bk-log/blob/master/LICENSE.txt)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/TencentBlueKing/bk-log)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bk-log/pulls)
[![codecov](https://codecov.io/gh/TencentBlueKing/bk-log/branch/master/graph/badge.svg?token=ATK33SUT2R)](https://codecov.io/gh/TencentBlueKing/bk-log)
[![Web](https://github.com/TencentBlueKing/bk-log/actions/workflows/web.yml/badge.svg?event=schedule)](https://github.com/TencentBlueKing/bk-log/actions/workflows/web.yml)
[![Test](https://github.com/TencentBlueKing/bk-log/actions/workflows/unittest.yml/badge.svg?event=schedule)](https://github.com/TencentBlueKing/bk-log/actions/workflows/unittest.yml)



[English](README_EN.md) | 简体中文

> **重要提示**: `master` 分支在开发过程中可能处于 *不稳定或者不可用状态* 。
请通过 [releases](https://github.com/TencentBlueKing/bk-log/releases) 而非 `master` 去获取稳定的二进制文件。

蓝鲸日志平台(BK-LOG)是为解决分布式架构下日志收集、查询困难的一款日志产品，基于业界主流的全文检索引擎，通过蓝鲸智云的专属 Agent 进行日志采集，提供多种场景化的采集、查询功能。

## Overview

* [设计理念](docs/overview/design.md)
* [架构设计](docs/overview/architecture.md)
* [代码目录](docs/overview/code_framework.md)

## Features

- 简单易用的日志采集
- 可视化的日志字段提取
- 功能强大的日志查询
- 实时日志和日志上下文
- 日志关键字/汇聚告警
- 支持第三方 ES 接入
- 分布式跟踪支持
- 仪表盘能力
- 在线日志文件提取


## Getting Started
- 安装好`MySQL 5.7`、`Python3.6`，若同时开发多个项目，请创建Python虚拟环境
- 创建数据库 `CREATE DATABASE bk_log DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;`
- 在项目config新建`local_settings.py`文件，文件内容为数据库配置，如
  
  ```python
     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'bk_log',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        },
    }
  ```

- 编译前端
   
  ```cmd
  cd web
  npm install
  npm run build
  ```
  
- 配置环境变量 
  
  ```bash
  APP_ID=${APP_ID}
  BK_IAM_V3_INNER_HOST=${BK_IAM_V3_INNER_HOST}
  BK_PAAS_HOST=${BK_PAAS_HOST}
  APP_TOKEN=${APP_TOKEN}
  # BKAPP_REDIS_PASSWORD=${BKAPP_REDIS_PASSWORD}  # 缓存和Celery会使用到redis，如果本地redis有密码需要增加这个环境变量
  ```

- 启动工程 `python manage.py runserver 8000`
- 启动celery `celery -A worker -l info -c 8`

## Support

- [产品文档](https://bk.tencent.com/docs/)
- [蓝鲸论坛](https://bk.tencent.com/s-mart/community)

## BlueKing Community

- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：蓝鲸配置平台（蓝鲸 CMDB）是一个面向资产及应用的企业级配置管理平台。
- [BK-CI](https://github.com/Tencent/bk-ci)：蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs)：蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas)：蓝鲸容器管理平台 SaaS 基于原生 Kubernetes 和 Mesos 自研的两种模式，提供给用户高度可扩展、灵活易用的容器产品服务。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：蓝鲸 PaaS 平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理 SaaS 应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops)：标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类 SaaS 产品。

## Contributing

如果你有好的意见或建议，欢迎给我们提 Issues 或 Pull Requests，为蓝鲸开源社区贡献力量。关于 bk-log 分支管理、Issue 以及 PR 规范，
请阅读 [Contributing Guide](CONTRIBUTING.md)。

[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。


## License

项目基于 MIT 协议， 详细请参考 [LICENSE](LICENSE.txt) 。

