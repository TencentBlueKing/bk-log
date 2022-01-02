module.exports = {
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: 'babel-eslint',
  },
  extends: ['@blueking/eslint-config-bk/vue'],
  globals: {
    NODE_ENV: false,
    __webpack_public_path__: false,
  },
  parserOptions: {
    // 解析器
    parser: 'babel-eslint',
    ecmaFeatures: {
      // 支持装饰器
      legacyDecorators: true,
    },
  },
  rules: {
    'no-param-reassign': 'off',
    'prefer-destructuring': 'off',
    'no-underscore-dangle': 'off',
    'no-restricted-syntax': 'off',
    'array-callback-return': 'off',
    'no-nested-ternary': 'off',
    'arrow-body-style': 'off',
    'no-restricted-properties': 'off',
    'function-paren-newline': 'off',
    'vue/no-lone-template': 'off',
  },
};
