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
</style>
