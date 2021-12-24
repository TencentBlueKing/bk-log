/* eslint-disable no-nested-ternary */
const wepack = require('webpack');
const path = require('path');
const fs = require('fs');
const CopyPlugin = require('copy-webpack-plugin');
const MonitorWebpackPlugin = require('./webpack/monitor-webpack-plugin');
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
    window.SITE_URL = "\${SITE_URL}"
    window.AJAX_URL_PREFIX = "\${AJAX_URL_PREFIX}"
    window.BK_STATIC_URL = "\${BK_STATIC_URL}"
    window.LOGIN_SERVICE_URL = "\${LOGIN_SERVICE_URL}"
    window.MONITOR_URL = "\${MONITOR_URL}"
    window.BKDATA_URL = "\${BKDATA_URL}"
    window.COLLECTOR_GUIDE_URL = "\${COLLECTOR_GUIDE_URL}"
    window.FEATURE_TOGGLE = "\${FEATURE_TOGGLE | safa}"
    window.FEATURE_TOGGLE_WHITE_LIST = "\${FEATURE_TOGGLE_WHITE_LIST | safa}"
    window.REAL_TIME_LOG_MAX_LENGTH = "\${REAL_TIME_LOG_MAX_LENGTH}"
    window.REAL_TIME_LOG_SHIFT_LENGTH = "\${REAL_TIME_LOG_SHIFT_LENGTH}"
    window.runVersion = "\${RUN_VER}"
    window.TITLE_MENU = "\${TITLE_MENU}"
    window.MENU_LOGO_URL = "\${MENU_LOGO_URL}"
    window.APP_CODE = "\${APP_CODE}"
    window.BK_DOC_URL = "\${BK_DOC_URL}"
    window.BK_DOC_QUERY_URL = "\${BK_DOC_QUERY_URL}"
    window.BK_HOT_WARM_CONFIG_URL = "\${BK_HOT_WARM_CONFIG_URL}"
    window.BIZ_ACCESS_URL = "\${BIZ_ACCESS_URL}"
    window.DEMO_BIZ_ID = "\${DEMO_BIZ_ID}"
    window.ES_STORAGE_CAPACITY = "\${ES_STORAGE_CAPACITY}"
    window.TAM_AEGIS_KEY = "\${TAM_AEGIS_KEY}"
    window.BK_LOGIN_URL = "\${BK_LOGIN_URL}"
    window.BK_DOC_DATA_URL = "\${BK_DOC_DATA_URL}"
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
  const distUrl = mobile ? path.resolve('./weixin/') : fta ? path.resolve('./fta/') : path.resolve('./monitor/');
  const config = baseConfig;
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
    config.plugins.push(
      new CopyPlugin({
        patterns: [
          { from: path.resolve(`./public/${mobile ? 'mobile/' : fta ? 'fta/' : 'pc/'}`), to: distUrl },
          { from: path.resolve('./public/img'), to: path.resolve(distUrl, './img') },
        ],
      }),
    );
    config.plugins.push(new MonitorWebpackPlugin({ ...monitorPluginConfig, mobile, fta }));
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
        // vue$: path.resolve(appDir, 'node_modules/vue'),
        // vuex$: path.resolve(appDir, 'node_modules/vuex'),
        // 'async-validator': path.resolve(appDir, 'node_modules/async-validator'),
        // codemirror: path.resolve(appDir, 'node_modules/codemirror'),
        // 'resize-detector': path.resolve(appDir, 'node_modules/resize-detector'),
        // 'throttle-debounce': path.resolve(appDir, 'node_modules/throttle-debounce'),
        // 'vue-tsx-support': path.resolve(appDir, 'node_modules/vue-tsx-support'),
        // 'bk-magic-vue$': path.resolve(appDir, 'node_modules/bk-magic-vue'),
        // moment$: path.resolve(appDir, 'node_modules/moment'),
        // 'vue-property-decorator': path.resolve(appDir, 'node_modules/vue-property-decorator'),
        // 'vue-class-component': path.resolve(appDir, 'node_modules/vue-class-component'),
        // deepmerge$: path.resolve(appDir, 'node_modules/deepmerge'),
        // '@': appDir,
        // '@router': path.resolve('./src/router/'),
        // '@store': path.resolve('./src/store/'),
        // '@page': path.resolve('./src/pages/'),
        // '@api': path.resolve('./src/monitor-api/'),
        // '@static': path.resolve('./src/monitor-static/'),
        // '@common': path.resolve('./src/monitor-common/'),
      },
    },
    cache: typeof devConfig.cache === 'boolean' ? devConfig.cache : config.cache,
  };
};
