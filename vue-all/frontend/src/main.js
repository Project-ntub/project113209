import { createApp } from 'vue';
import App from './App.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
import router from './router';
import axios from 'axios';  

library.add(fas);

const app = createApp(App);

app.component('font-awesome-icon', FontAwesomeIcon);

// 設置 Axios 攔截器，攜帶 token
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

// 設置 Axios 攔截器，處理 403 錯誤並自動刷新 token
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // 如果回應是 403 且 token 尚未刷新過
    if (error.response && error.response.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          // 發送刷新 token 的請求
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken
          });

          // 成功獲取新的 access token
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // 更新 Authorization header 並重試原始請求
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);

        // 如果刷新失敗，清除 token 並重定向到登入頁面
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // 其他錯誤處理
    return Promise.reject(error);
  }
);

app.use(router);
app.mount('#app');
