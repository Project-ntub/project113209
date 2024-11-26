import { createApp } from 'vue';
import App from '@/App.vue';
import router from '@/router';
import store from '@/store';
import axios from 'axios';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
import VueCookies from 'vue-cookies'; // 引入 vue-cookies 插件
import 'vue-multiselect/dist/vue-multiselect.min.css';


// 初始化應用程序
const app = createApp(App);

// 通用的配置
app.use(router);
app.use(store);
app.component('font-awesome-icon', FontAwesomeIcon);
library.add(fas); // 將所有 Font Awesome 的圖標加入庫
app.use(VueCookies); // 註冊 vue-cookies 插件

store.dispatch('initializeStore');

// 設置 Axios 攔截器，攜帶 token 和 CSRF token
axios.interceptors.request.use(
  config => {
    // 排除不需要攜帶 token 的請求，例如註冊、忘記密碼
    const isAuthRequest = config.url.includes('register') || config.url.includes('forgot-password') || config.url.includes('login');
    
    if (!isAuthRequest) {
      const token = localStorage.getItem('frontend_token');  // 前台的 token
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }

    // 設置 CSRF token，如果存在的話
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 設置 Axios 攔截器來處理 403 錯誤並自動刷新 token
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // 如果遇到 403 錯誤且尚未刷新 token
    if (error.response && error.response.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('frontend_refresh_token'); // 前台 refresh token
        if (refreshToken) {
          // 發送請求刷新 token
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken
          });

          // 更新 access token
          const newAccessToken = response.data.access;
          localStorage.setItem('frontend_token', newAccessToken);

          // 更新 Authorization header 並重試原始請求
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);

        // 如果刷新失敗，清除 token 並重定向到登入頁面
        localStorage.removeItem('frontend_token');
        localStorage.removeItem('frontend_refresh_token');
        window.location.href = '/frontend/login'; // 前台登入頁面
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// 啟動應用
app.mount('#app');
