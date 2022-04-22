### Config

Django工程环境变量加载，settings初始化


### 目录

```
|_ __init__.py
|_ default.py 默认配置，不区分环境的配置
|_ dev.py  开发环境配置
|_ prod.py 正式环境配置
|_ stag.py 预发布环境配置
|_ env.py  一些用来加载环境的公共方法
|_ domains.py  环境相关的第三方平台URL, 独立的配置，不会加载到settings中
```

### settings加载顺序

Django首先会加载顶层目录settings文件，然后再根据环境变量加载不同的文件

- dev -> config/dev.py
- stag -> config/stag.py
- prod -> config/prod.py


### config目录加载顺序

1. __init__.py
2. dev/stag/prod.py
    2.1. blueapps框架settings
    2.2. 自身配置
    2.3. env.py(环境配置，第三方平台URL)
    2.4. local_settings(dev环境才会加载这个文件)

根据文件加载顺序，最后加载的文件会覆盖前面的变量


### env加载方式

1. 加载config/default.py
2. 加载顶层目录的xxx.env.yaml文件，并使用config/default.py中的变量渲染
3. 得到配置后再放到settings中

### TODO 加载方式待优化