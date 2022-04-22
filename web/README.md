#### 日志前端构建使用说明

###### 安装和更新前端依赖（`nodejs`最小依赖版本为`V10.13.0`）

```bash
cd webpack
npm ci
#### mac
npm run install-build
```

如果您尚未安装过 `nodejs` [详细安装参见](https://nodejs.org/zh-cn/download/)

###### 本地开发模式

- 本地启动

  ```bash
  # pc端本地开发模式
  npm run dev
  ```

- 前端环境变量配置

  1. 新建文件 `local.settings.js`

  2. 配置自定义内容 参考如下 [更多配置参见](https://webpack.docschina.org/configuration/dev-server/)

     ```js
     const devProxyUrl = ''
     const devHost = ''
     const loginHost = ''
     const devPort = 
     module.exports = {
         port: devPort, // 启动端口
         host: devHost, // 启动host
         devProxyUrl, // 后端地址 用于代理转发api
         loginHost, // 登入地址
         proxy: { // api代理配置
             '/rest': {
                 target: devProxyUrl,
                 changeOrigin: true,
                 secure: false,
                 toProxy: true
             }
     }

     ```

###### 生产构建

- 构建

  ```bash
  npm run build
  ```

- 分析构建产物组成

  ```bash
  # 生产环境构建产物分析
  npm run analyze
  ```

###### 前端构建工具 `@blueking/bkmonitor-cli`

```bash
cd webpack
git submodule update packages/cli
```

#### help

- 前端构建最小依赖 node 版本 V14.13.0
- 编译过程中出现任何问题请联系 admin
