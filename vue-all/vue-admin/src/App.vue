<template>
  <div :class="['home-page', fontSizeClass, { shifted: isSidebarActive }]">
    <TopNavbar v-if="!isBackend && showTopNavbar" />
    <SidebarPage v-if="!isBackend && !$route.meta.hideSidebar" />
    <SidebarBackend 
      v-if="isBackend && !$route.meta.hideSidebar" 
      :isSidebarActive="isSidebarActive" 
      @toggleSidebar="toggleSidebar" 
    />
    <div class="main-content" :class="{ shifted: isSidebarActive }">
      <router-view @preference-updated="updateFontSize" />
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import SidebarPage from '@/components/frontend/SidebarPage.vue';
import SidebarBackend from '@/components/backend/SideBar.vue';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'App',
  components: {
    TopNavbar,
    SidebarPage,
    SidebarBackend
  },
  computed: {
    ...mapGetters(['isBackend', 'getFontSize']),
    isBackend() {
      return this.$route.path.startsWith('/backend');
    },
    showTopNavbar() {
      return !this.isBackend && !this.$route.meta.hideNavbar;
    },
    fontSizeClass() { // 根據 Vuex 的字體大小狀態返回相應的類
      return `font-size-${this.getFontSize}`;
    }
  },
  data() {
    return {
      isSidebarActive: false
    };
  },
  methods: {
    ...mapActions(['fetchPreferences', 'updateFontSize', 'fetchPermissions']),
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    handlePreferenceUpdate(preference) { // 接收偏好更新事件
      this.updateFontSize(preference.fontsize);
    }
  },
  created() {
    const accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (accessToken) {
      this.setToken(accessToken);
      this.fetchPermissions();
      this.fetchPreference();
    }
  }
};
</script>

<!-- 引入全局樣式 -->
<style src="./assets/css/global.css"></style>

<style>
:root {
  --font-size: 16px; /* 預設字體大小 */
}

.font-size-small {
  --font-size: 12px;
}

.font-size-medium {
  --font-size: 16px;
}

.font-size-large {
  --font-size: 20px;
}

/* 使用 CSS 變量設置字體大小 */
body {
  font-size: var(--font-size);
}

/* 確保所有其他元素使用相對字體大小 */
h1, h2, h3, h4, h5, h6 {
  font-size: 1.5em;
}

p, span, a, button, select, input {
  font-size: 1em;
}

/* 其他樣式保持不變 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  transition: margin-left 0.3s ease; /* 過渡效果 */
}

#app.shifted {
  margin-left: 250px; /* 當側邊欄打開時，主內容區域向右移動 */
}

.main-content {
  width: 100%;
  padding: 20px;
  box-sizing: border-box; /* 確保 padding 不影響寬度 */
}

/* 響應式設計的樣式 */
@media (max-width: 600px) {
  #app {
    margin-left: 0; /* 在小螢幕設備上側邊欄收起，主內容不移動 */
  }

  .main-content {
    padding: 10px; /* 在小螢幕上縮小內邊距 */
  }
}

@media (min-width: 601px) and (max-width: 1024px) {
  #app.shifted {
    margin-left: 200px; /* 在中等螢幕設備上側邊欄展開時主內容區域稍微移動 */
  }

  .main-content {
    padding: 20px; /* 中等螢幕設備上的內邊距 */
  }
}

@media (min-width: 1025px) {
  #app.shifted {
    margin-left: 250px; /* 大螢幕設備上側邊欄展開時主內容區域正常移動 */
  }

  .main-content {
    padding: 30px; /* 大螢幕設備上的內邊距 */
  }
}
</style>
