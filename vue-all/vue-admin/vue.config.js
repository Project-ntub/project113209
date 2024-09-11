const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack'); // 確保引入 webpack

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(true),
        // 根據需求添加更多 feature flags
      })
    ]
  }
});
