// 支持的完整的菜单
export default [{
  name: '检索',
  id: 'retrieve',
}, {
  name: '仪表盘',
  id: 'dashboard',
  children: [{
    id: 'create-dashboard',
    name: '新建仪表盘',
  }, {
    id: 'create-folder',
    name: '新建目录',
  }, {
    id: 'import-dashboard',
    name: '导入仪表盘',
  }],
}, {
  name: '日志提取',
  id: 'extract',
}, {
  name: '调用链',
  id: 'trace',
}, {
  name: '监控策略',
  id: 'monitor',
}, {
  name: '管理',
  id: 'manage',
  children: [{
    id: 'manage-access',
    name: '日志接入',
    children: [{
      id: 'log-collection',
      name: '日志采集',
    }, {
      id: 'bk-data-collection',
      name: '数据平台',
    }, {
      id: 'es-collection',
      name: '第三方ES接入',
    }, {
      id: 'custom-collection',
      name: '自定义接入',
    }],
  }, {
    id: 'trace-track',
    name: '全链路追踪',
    children: [{
      id: 'collection-track',
      name: '采集接入',
    }, {
      id: 'bk-data-track',
      name: '数据平台接入',
    }, {
      id: 'sdk-track',
      name: 'SDK接入',
    }],
  }, {
    id: 'manage-extract',
    name: '日志提取',
    children: [{
      id: 'manage-extract-permission',
      name: '权限管理',
    }, {
      id: 'extract-link-manage',
      name: '链路管理',
    }],
  }, {
    id: 'log-archive',
    name: '日志归档',
    children: [{
      id: 'log-archive-conf',
      name: '日志归档',
    }],
  }, {
    id: 'es-cluster-status',
    name: 'ES集群',
    children: [{
      id: 'es-cluster-mess',
      name: '集群列表',
    }],
  }, {
    id: 'manage-data-link',
    name: '管理',
    children: [{
      id: 'manage-data-link-conf',
      name: '采集链路管理',
    }],
  }],
}];
