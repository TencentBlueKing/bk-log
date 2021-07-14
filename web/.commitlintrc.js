module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always',
      [
        'feature',
        'bugfix',
        'minor',
        'optimization',
        'sprintfix',
        'refactor',
        'test',
        'docs',
        'merge'
      ]
    ]
  }
};
