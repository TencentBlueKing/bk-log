# 采集器自检测工具

## 目的
 
  通过该工具能发现采集器的一些基础问题，减少人工排查成本
 
## 检测方式

- 给采集器内置一个指令（依赖采集器更新）
- 单独写一个脚本来检测
    - python(考虑2-3兼容问题，window系统兼容问题)
    - shell(windows系统兼容问题)
    
## 检测逻辑


- 自身状态检测
    - 采集器是否安装
    - 进程是否存在
    - 是否频繁重启，从/tmp/bkc.log中查看
    - 进程当前的资源占用
    - GSE procfile.json中配置的资源占用

- 配置检测
    - 主配置文件
        - gse相关路径是否配置正确
            - 上云gse_bkte
            - 上云预发布 gse_cloud
            - 运维 gse_opbk
            - 其他版本 gse
    
    - 子配置文件
        - 对应采集项的配置是否
