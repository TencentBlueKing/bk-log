## 本地部署

1. 安装python 3.6.6，使用pip —version确认版本及路径是否正确

2. 安装virtualenv

   ```shell
   pip3 install virtualenv
   ```

3. 安装virtualenvwrapper

   ```shell
   pip3 install virtualenvwrapper
   ```
   
   ```
    如果找不到mkvirtualenv命令
    1. 创建目录用来存放虚拟环境
    mkdir $HOME/.virtualenvs
    
    2. 在 ~/.bashrc 中添加行:
    export WORKON_HOME=HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    
    3. 运行:
    source ~/.bashrc
   ```


4. 创建日志检索虚拟环境

   ```shell
   # 用于企业版
   $ mkvirtualenv log_open -p python3
   ```

5. 用git仓库clone代码

6. 初始化企业版

   ```sh
   $ workon log_open
   $ cd log_search_v4
   $ . ./scripts/env.sh open
   ```
   
7. 初始化社区版版

   ```shell
   $ workon log_open
   $ cd log_search_v4
   $ . ./scripts/env.sh open
   ```

8. 创建DB，并在根目录创建本地调试配置文件：local_settings.py

   ```python
   # -*- coding: utf-8 -*-
   
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'log_search_v4',
           'USER': 'root',
           'PASSWORD': '',
           'HOST': '127.0.0.1',
           'PORT': '3306',
       },
   }
   
   ```

9. 初始化DB

   ```shell
   export BKPAAS_ENGINE_REGION=open
   python manage.py migrate
   python manage.py createcachetable django_cache
   ```

10. 环境变量
 - 企业版：BKPAAS_ENGINE_REGION=open; BK_PAAS_HOST=http://your_bk_paas.com;
 
11. 国际化
```shell
# 标识语言
django-admin makemessages --ignore=blueapps/* --ignore=web/* --extension=py

# 翻译后编译
django-admin compilemessages
```

## 目录结构说明

```
 ./                                # 日志检索根目录
 |-- apps                          # 后台业务逻辑
     |-- api                       # 外部接口依赖，不同版本在sites实现
     |-- log_chart                 # 日志检索图表看板
     |-- log_search                # 日志检索基础功能
     |-- log_databus               # 日志检索独立数据链路
     |-- plugins                   # 版本特定插件      
         |-- smart_monitor         # 第三方插件
 |-- config                        # 应用配置      
     |-- domains.py                # 外部接口依赖域名配置      
 |-- scripts                       # 公共脚本：目前用于版本切换      
 |-- sites                         # 不同版本配置及部署内容      
     |-- open                      # 社区版
         |-- config                # 版本配置
         |-- deploy                # 版本部署：版本切换时会将此目录覆盖到SaaS根目录
 |-- static                        # 前端静态目录      
     |-- dist                      # 前端编译后部署目录
 |-- manage.py                     # jango 工程 manage  
 |-- settings.py                   # Django工程 settings      
 |-- urls.py                       # Django工程主路由 URL 配置
 |-- wsgi.py                       # WSG I配置
```

## 单元测试

```
代码覆盖
coverage run --source . manage.py test apps.log_databus --keepdb && coverage report 


生成报告
coverage report 

生成html报告
coverage html && open htmlcov/index.html
```
