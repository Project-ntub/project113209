<template>
  <div id="app" :class="{ shifted: isSidebarActive }">
    <TopNavbar v-if="!isBackend && showTopNavbar" />
    <SidebarPage v-if="!isBackend && !$route.meta.hideSidebar" />
    <SidebarBackend 
      v-if="isBackend && !$route.meta.hideSidebar" 
      :isSidebarActive="isSidebarActive" 
      @toggleSidebar="toggleSidebar" 
    />
    <div class="main-content" :class="{ shifted: isSidebarActive }">
      <router-view />
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import SidebarPage from '@/components/frontend/SidebarPage.vue';
import SidebarBackend from '@/components/backend/SideBar.vue';

export default {
  name: 'App',
  components: {
    TopNavbar,
    SidebarPage,
    SidebarBackend
  },
  data() {
    return {
      isSidebarActive: false,
    };
  },
  computed: {
    isBackend() {
      return this.$route.path.startsWith('/backend');
    },
    showTopNavbar() {
      return !this.isBackend && !this.$route.meta.hideNavbar;
    }
  },
  methods: {
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    }
  }
};
</script>

<!-- 引入全局樣式 -->
<style src="./assets/css/global.css"></style>

<style>
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
