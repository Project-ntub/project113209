import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import axios from './axios'; 

const app = createApp(App);

// 通用的配置
app.use(router);
app.use(store);

// 判斷前台還是後台
const isBackend = window.location.pathname.startsWith('/admin');

// 根據判斷加載不同的配置
if (isBackend) {
  // 後台特有的配置
  app.config.globalProperties.$axios = axios; 
} else {
  // 前台特有的配置
  import('@fortawesome/fontawesome-svg-core').then(({ library }) => {
    import('@fortawesome/vue-fontawesome').then(({ FontAwesomeIcon }) => {
      import('@fortawesome/free-solid-svg-icons').then(({ fas }) => {
        library.add(fas);
        app.component('font-awesome-icon', FontAwesomeIcon);
        app.mount('#app');
      });
    });
  });
}

if (isBackend) {
  app.mount('#app');
}
