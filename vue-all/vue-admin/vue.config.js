const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack'); // 確保引入 webpack
const path = require('path'); // 確保引入 path 模塊

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),  // src 目錄的別名
        'shared': path.resolve(__dirname, 'src/shared')  // shared 目錄的別名
      }
    },
    plugins: [
      new webpack.DefinePlugin({
        '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(true),
      })
    ]
  }
});
