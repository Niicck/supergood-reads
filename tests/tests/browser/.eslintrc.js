module.exports = {
  root: true,
  parser: 'esprima',
  extends: ['eslint:recommended', 'eslint-config-prettier', 'prettier'],
  env: {
    browser: true,
    node: true,
    es6: true,
    jest: true,
  },
  globals: {
    page: true,
    browser: true,
    context: true,
    puppeteerConfig: true,
    jestPuppeteer: true,
  },
};
