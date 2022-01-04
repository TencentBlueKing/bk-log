module.exports = {
  defaultSeverity: 'error',
  extends: ['@blueking/stylelint-config-bk'],
  rules: {
    'selector-max-id': 2,
    'declaration-property-value-disallowed-list': {
      "/^border/": []
    }
  }
}
