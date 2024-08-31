import axios from 'axios';

// 使用固定 IP 作為 baseURL
const baseURL = process.env.VUE_APP_API_URL || `http://${window.location.hostname}:8000`;

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;
axios.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken');

// 請求攔截器
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
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
