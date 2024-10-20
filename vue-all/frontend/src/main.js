import { createApp } from 'vue';
import App from './App.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
import router from './router';
import axios from 'axios';  // 引入 Axios

// 将所有图标添加到库中
library.add(fas);

// 创建 Vue 应用
const app = createApp(App);

// 注册 FontAwesomeIcon 组件
app.component('font-awesome-icon', FontAwesomeIcon);

// 设置 Axios 攔截器，用來自動攜帶 token 並處理 refresh token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // 如果返回 403，且 token 尚未刷新過
    if (error.response.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
          refresh: refreshToken
        });

        // 成功获取新的 access token
        const newAccessToken = response.data.access;
        localStorage.setItem('access_token', newAccessToken);

        // 更新 Authorization header 並重試請求
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// 使用 router
app.use(router);

// 挂载应用
app.mount('#app');
