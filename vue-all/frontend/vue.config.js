const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack');
const path = require('path');

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'shared': path.resolve(__dirname, 'src/shared'),
      },
    },
    plugins: [
      new webpack.DefinePlugin({
        '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(true),
      }),
    ],
  },
  devServer: {
    proxy: {
      "/api/openai": {
        target: "http://localhost:8000",  // 改為本地後端服務
        changeOrigin: true,               // 允許跨域
        secure: false,                    // 如果是本地環境，禁用 https 檢查
        pathRewrite: { "^/api/openai": "" }, // 請求重寫，使請求正確導向本地後端
        onProxyReq: (proxyReq, req, res) => {
          // 設置 API 密鑰，如果需要通過代理發送 Authorization 標頭
          proxyReq.setHeader('Authorization', `Bearer ${process.env.VUE_APP_OPENAI_API_KEY}`);
        },
      },
    },
  },
});
