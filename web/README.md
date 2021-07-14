web
===

``` bash
# create `Dll bundle` with webpack DllPlugin
npm run dll

# dev
npm run dev

# build
npm run build

# build with analyzer
npm run build:analyzer

```

## 目录结构说明

```
 ./web                                  # 日志检索-前端工程目录
 |-- build                              # 前端工程配置目录 
 |-- mock/ajax                          # 忽略            
 |-- src                                # 开发任务 - 主要文件目录  
  |-- api                            # http相关的配置改动
  |-- common                         # 工具类
  |-- components                     # 主视图下需要用到的小组件放在此目录，包括导航、错误页面、权限登录
  |-- images                         
  |-- mock                           # mock数据来源  
  |-- router                         # 前端路由控制  
  |-- scss                           # scss 样式控制文件  
  |-- services                       # HTTP请求的URL、请求方式统一在此处配置  
  |-- store                          # store 状态管理仓库  

  |-- views                          # 主视图组件
    |-- manage                      # 管理模块
      index.vue                   # 模块入口
      dataSource.vue              # 数据源管理
      indexSet.vue                # 索引集管理
      permissionGroup.vue         # 权限组管理
    |-- monitors                    # 监控模块  
      index.vue                   # 模块入口
      alarmLog.vue                # 告警记录
      alarmStrategy.vue           # 告警策略
      shieldStrategy.vue          # 屏蔽策略
    |-- retrieve                    # 检索模块 
      index.vue                   # 模块入口 

  App.vue                            # 视图入口文件  里面有一个mock数据的示例，可以直接贴后端给的数据
  main.js                            # js入口文件  
  .editorconfig                      
  .eslintignore                       
  .eslintrc.js                           
  .gitignore                             
  package-lock.json                     
  package.json                          # 依赖配置     
