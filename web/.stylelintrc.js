module.exports = {
  defaultSeverity: 'error',
  extends: ['@bkui/stylelint-config-bk'],
  rules: {
    'selector-max-id': 2,
    'declaration-property-value-disallowed-list': {
      "/^border/": []
    }
  }
}
