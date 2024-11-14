const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack');
const path = require('path');

module.exports = defineConfig({
  transpileDependencies: true, // 允许依赖转换
  lintOnSave: false, // 禁用 ESLint 保存时的检查
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'), // 定义 src 的别名
        'shared': path.resolve(__dirname, 'src/shared'), // 定义 shared 的别名
      },
    },
    plugins: [
      new webpack.DefinePlugin({
        '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(true),
      }),
    ],
  },
});
