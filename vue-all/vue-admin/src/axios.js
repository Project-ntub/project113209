// axios.js

import axios from 'axios';

// 使用固定 IP 作為 baseURL
const baseURL = process.env.VUE_APP_API_URL || `http://${window.location.hostname}:8000`;

// 設置 Axios 的基本配置
axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

// 請求攔截器
axios.interceptors.request.use((config) => {
  if (config.url.startsWith('/api/backend/')) {
    const token = localStorage.getItem('backend_token'); // 後台 token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  } else if (config.url.startsWith('/api/frontend/')) {
    const token = localStorage.getItem('frontend_token'); // 前台 token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 從 Cookie 中取得 CSRF token 的函數
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default axios;
