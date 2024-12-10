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
        target: "https://api.openai.com", // 保持這裡指向 OpenAI API
        changeOrigin: true,                // 允許跨域
        secure: true,                      // 啟用 HTTPS
        pathRewrite: { "^/api/openai": "" }, // 將 /api/openai 替換為空，這樣請求就會轉發到正確的 API 端點
        onProxyReq: (proxyReq, req, res) => {
          // 在代理請求中添加 Authorization 標頭
          proxyReq.setHeader('Authorization', `Bearer ${process.env.VUE_APP_OPENAI_API_KEY}`);
        },
      },
    },
  },
});
