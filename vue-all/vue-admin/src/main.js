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
library.add(fas);
app.use(VueCookies); // 註冊 vue-cookies 插件

// 設置 Axios 攔截器來攜帶 token 和 CSRF token
axios.interceptors.request.use(config => {
  const token = window.location.pathname.startsWith('/backend') ? 
                localStorage.getItem('backend_token') : 
                localStorage.getItem('frontend_token');  
  const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`; // 將 token 加到 Authorization 頭中
  }
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  return config;
}, error => {
  return Promise.reject(error);
});


// 判斷前台還是後台
const isBackend = window.location.pathname.startsWith('/admin');

if (isBackend) {
  // 後台特有的配置
  app.config.globalProperties.$axios = axios;
}

// 啟動應用
app.mount('#app');
