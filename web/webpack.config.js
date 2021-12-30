/* eslint-disable no-nested-ternary */
const wepack = require('webpack');
const path = require('path');
const fs = require('fs');
const MonitorWebpackPlugin = require('./webpack/monitor-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const devProxyUrl = 'http://appdev.bktencent.com:9002';
const devHost = 'appdev.bktencent.com';
const loginHost = 'https://paas-dev.bktencent.com';
const devPort = 8001;

let devConfig = {
  port: devPort,
  host: devHost,
  devProxyUrl,
  loginHost,
  proxy: {},
  cache: null,
};
const monitorPluginConfig = {
  pcBuildVariates: `
    <script>
    window.SITE_URL = '{{SITE_URL}'
    window.AJAX_URL_PREFIX = '{{AJAX_URL_PREFIX}'
    window.BK_STATIC_URL = '{{BK_STATIC_URL}'
    window.LOGIN_SERVICE_URL = '{{LOGIN_SERVICE_URL}'
    window.MONITOR_URL = '{{MONITOR_URL}'
    window.BKDATA_URL = '{{BKDATA_URL}'
    window.COLLECTOR_GUIDE_URL = '{{COLLECTOR_GUIDE_URL}'
    window.FEATURE_TOGGLE = '{{FEATURE_TOGGLE | safa}'
    window.FEATURE_TOGGLE_WHITE_LIST = '{{FEATURE_TOGGLE_WHITE_LIST | safa}'
    window.REAL_TIME_LOG_MAX_LENGTH = '{{REAL_TIME_LOG_MAX_LENGTH}'
    window.REAL_TIME_LOG_SHIFT_LENGTH = '{{REAL_TIME_LOG_SHIFT_LENGTH}'
    window.RUN_VER = '{{RUN_VER}'
    window.TITLE_MENU = '{{TITLE_MENU}'
    window.MENU_LOGO_URL = '{{MENU_LOGO_URL}'
    window.APP_CODE = '{{APP_CODE}'
    window.BK_DOC_URL = '{{BK_DOC_URL}'
    window.BK_DOC_QUERY_URL = '{{BK_DOC_QUERY_URL}'
    window.BK_HOT_WARM_CONFIG_URL = '{{BK_HOT_WARM_CONFIG_URL}'
    window.BIZ_ACCESS_URL = '{{BIZ_ACCESS_URL}'
    window.DEMO_BIZ_ID = '{{DEMO_BIZ_ID}'
    window.ES_STORAGE_CAPACITY = '{{ES_STORAGE_CAPACITY}'
    window.TAM_AEGIS_KEY = '{{TAM_AEGIS_KEY}'
    window.BK_LOGIN_URL = '{{BK_LOGIN_URL}'
    window.BK_DOC_DATA_URL = '{{BK_DOC_DATA_URL}'
  </script>
  {% if TAM_AEGIS_KEY != "" %}
    <script src="https://cdn-go.cn/aegis/aegis-sdk/latest/aegis.min.js?_bid=3977"></script>
  {% endif %}`,
};
if (fs.existsSync(path.resolve(__dirname, './local.settings.js'))) {
  const localConfig = require('./local.settings');
  devConfig = Object.assign({}, devConfig, localConfig);
}
module.exports = (baseConfig, { mobile, production, fta, email = false }) => {
  const config = baseConfig;
  const distUrl = path.resolve('../static/dist');
  if (!production) {
    config.devServer = Object.assign({}, config.devServer || {}, {
      port: devConfig.port,
      host: devConfig.host,
      proxy: {
        ...['/api'].reduce(
          (pre, key) => ({
            ...pre,
            [key]: {
              target: devConfig.devProxyUrl,
              changeOrigin: true,
              secure: false,
              toProxy: true,
              headers: {
                referer: devConfig.devProxyUrl,
              },
            },
          }),
          {},
        ),
        ...devConfig.proxy,
      },
    });
    config.plugins.push(
      new wepack.DefinePlugin({
        process: {
          env: {
            proxyUrl: JSON.stringify(devConfig.devProxyUrl),
            devUrl: JSON.stringify(`${devConfig.host}:${devConfig.port}`),
            loginHost: JSON.stringify(devConfig.loginHost),
            loginUrl: JSON.stringify(`${devConfig.loginHost}/login/`),
          },
        },
      }),
    );
  } else if (!email) {
    config.plugins.push(new MonitorWebpackPlugin({ ...monitorPluginConfig, mobile, fta }));
    config.plugins.push(
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve(__dirname, './src/images/new-logo.svg'),
            to: path.resolve(distUrl, './img'),
          },
        ],
      }),
    );
  }

  return {
    ...config,
    output: {
      ...config.output,
      path: distUrl,
    },
    entry: {
      ...config.entry,
      main: './src/main.js',
    },
    resolve: {
      ...config.resolve,
      alias: {
        vue$: 'vue/dist/vue.esm.js',
        '@': path.resolve('src'),
      },
    },
    cache: typeof devConfig.cache === 'boolean' ? devConfig.cache : config.cache,
  };
};
