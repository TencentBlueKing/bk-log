module.exports = {
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: 'babel-eslint',
  },
  extends: ['@bkui/eslint-config-bk/vue'],
  globals: {
    NODE_ENV: false,
    __webpack_public_path__: false,
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
  },
};
