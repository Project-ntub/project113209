import { createApp } from 'vue';
import App from '@/App.vue';
import router from '@/router';
import store from '@/store';
import axios from 'axios';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
import VueCookies from 'vue-cookies'; // 引入 vue-cookies 插件

// 初始化應用程序
const app = createApp(App);

// 通用的配置
app.use(router);
app.use(store);
app.component('font-awesome-icon', FontAwesomeIcon);
library.add(fas); // 將所有 Font Awesome 的圖標加入庫
app.use(VueCookies); // 註冊 vue-cookies 插件

store.dispatch('initializeStore');

// 設置 Axios 攔截器來攜帶 token 和 CSRF token
axios.interceptors.request.use(config => {
  // 判斷是前台還是後台，選擇對應的 token
  const token = window.location.pathname.startsWith('/backend') ? 
                localStorage.getItem('backend_token') : 
                localStorage.getItem('frontend_token');  
  const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

  // 添加 Authorization 和 CSRF Token 到請求頭中
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  return config;
}, error => {
  return Promise.reject(error);
});

// 設置 Axios 攔截器來處理 403 錯誤並刷新 token
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // 判斷是前台還是後台
    const isBackend = window.location.pathname.startsWith('/backend');
    const tokenKey = isBackend ? 'backend_token' : 'frontend_token';
    const refreshTokenKey = isBackend ? 'backend_refresh_token' : 'frontend_refresh_token';

    // 如果遇到 403 且沒有重試過，嘗試使用 refresh token
    if (error.response && error.response.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem(refreshTokenKey);
        if (refreshToken) {
          // 發送請求獲取新的 access token
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken
          });

          // 成功刷新 token
          const newAccessToken = response.data.access;
          localStorage.setItem(tokenKey, newAccessToken);

          // 更新 Authorization header 並重試原始請求
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);

        // 如果刷新失敗，清除 token 並重定向到登入頁面
        localStorage.removeItem(tokenKey);
        localStorage.removeItem(refreshTokenKey);
        const loginPage = isBackend ? '/backend/login' : '/login';
        window.location.href = loginPage;
        return Promise.reject(refreshError);
      }
    }
    
    // 處理其他錯誤
    return Promise.reject(error);
  }
);

// 判斷是否為後台
const isBackend = window.location.pathname.startsWith('/backend');

if (isBackend) {
  // 後台特有的配置
  app.config.globalProperties.$axios = axios;
}

// 啟動應用
app.mount('#app');
