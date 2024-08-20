const { defineConfig } = require('@vue/cli-service');
const path = require('path');

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
  },
  // 保持一個入口點
  pages: {
    index: {
      entry: 'src/main.js', // 使用統一的入口文件
      template: 'public/index.html', // 使用統一的 HTML 模板
      filename: 'index.html', // 生成的文件名
      title: 'Admin Frontend', // HTML 中 <title> 的內容
    },
  },
});
