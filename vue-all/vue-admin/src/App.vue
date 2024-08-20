<template>
  <div id="app">
    <!-- 只有在不是後台並且需要顯示導航欄時才顯示 TopNavbar -->
    <TopNavbar v-if="!isBackend && showTopNavbar" />
    
    <!-- 根據 isBackend 和 hideSidebar 渲染不同的 Sidebar -->
    <SidebarPage v-if="!isBackend && !$route.meta.hideSidebar" />
    <SidebarBackend v-if="isBackend && !$route.meta.hideSidebar" :isSidebarActive="isSidebarActive" @toggleSidebar="toggleSidebar" />

    <!-- 渲染當前路由對應的組件 -->
    <router-view />
  </div>
</template>

<script>
// 引入前台和後台的 Sidebar 組件
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
    // 判斷當前路由是否屬於後台
    isBackend() {
      return this.$route.path.startsWith('/backend');
    },
    // 判斷是否顯示前台的 TopNavbar
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


<style >
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
