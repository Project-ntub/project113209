import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:8000'; // Django 伺服器的基礎 URL
axios.defaults.withCredentials = true; // 允許跨域請求時攜帶憑證

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

// 新增的響應攔截器
axios.interceptors.response.use((response) => {
  // 如果響應成功，直接返回響應
  return response;
}, (error) => {
  // 如果有錯誤，統一處理
  if (error.response) {
    // 例如，處理未授權（401）錯誤
    if (error.response.status === 401) {
      alert('未授權，請重新登入。');
      // 可以在這裡添加重定向到登入頁面或登出邏輯
    } else if (error.response.status === 403) {
      alert('權限不足，您沒有權限訪問此資源。');
    } else if (error.response.status === 404) {
      alert('資源未找到。');
    } else {
      alert(`伺服器回傳錯誤：${error.response.status}`);
    }
  } else if (error.request) {
    // 沒有收到伺服器回應，通常是網絡錯誤
    alert('伺服器無回應，請檢查您的網絡連線。');
  } else {
    // 設置請求時發生的其他錯誤
    alert(`請求設置錯誤：${error.message}`);
  }
  
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
