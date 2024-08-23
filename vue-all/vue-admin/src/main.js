import { createApp } from 'vue';
<<<<<<< HEAD
import App from '@/App.vue';
import router from '@/router';
import store from '@/store';
import axios from '@/axios';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
=======
import App from './App.vue';
import router from './router';
import store from './store';
import axios from './axios';
import VueCookies from 'vue-cookies'; // 引入 vue-cookies 插件
>>>>>>> dda5c7e (change)

// 初始化應用程序
const app = createApp(App);

// 通用的配置
app.use(router);
app.use(store);
<<<<<<< HEAD
app.component('font-awesome-icon', FontAwesomeIcon);
library.add(fas);
=======
app.use(VueCookies); // 註冊 vue-cookies 插件
>>>>>>> dda5c7e (change)

// 判斷前台還是後台
const isBackend = window.location.pathname.startsWith('/admin');

if (isBackend) {
  // 後台特有的配置
  app.config.globalProperties.$axios = axios;
}

// 啟動應用
app.mount('#app');
