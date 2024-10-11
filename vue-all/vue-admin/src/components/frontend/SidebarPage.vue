<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen, smallScreen: isSmallScreen }]">
      <!-- 顯示一個圖示，點擊後展開側邊欄 -->
      <div class="sidebar-header">
        <font-awesome-icon
          icon="user"
          class="icon user-icon"
          v-if="!isSmallScreen || isSidebarOpen" 
        />
        <span v-if="isSidebarOpen">{{ username }}</span>
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>

      <!-- 大螢幕時顯示所有圖示，小螢幕時依賴 v-if 展開 -->
      <div v-if="isSidebarOpen || !isSmallScreen">
        <!-- 儀表板 -->
        <router-link to="/frontend/home" class="sidebar-link">
          <font-awesome-icon icon="chart-pie" class="icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">儀錶板管理</span>
        </router-link>

        <!-- 個人資訊 -->
        <router-link to="/frontend/profile" class="sidebar-link">
          <font-awesome-icon icon="user" class="icon second-icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">個人資訊</span>
        </router-link>

        <!-- 登出 -->
        <a href="#" class="sidebar-link logout-btn" @click.prevent="confirmLogout">
          <font-awesome-icon icon="sign-out-alt" class="icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">登出</span>
        </a>
      </div>
    </div>

    <div :class="['content', { shift: isSidebarOpen }]">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SidebarPage',
  data() {
    return {
      isSidebarOpen: false,
      isSmallScreen: false, // 判斷是否為小螢幕
      username: ''
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    confirmLogout() {
      const confirmed = confirm("確定要登出嗎？");
      if (confirmed) {
        this.logout();
      }
    },
    logout() {
      // 清除 localStorage
      window.localStorage.clear();

      // 清除 sessionStorage
      window.sessionStorage.clear();

      // 清除所有 Cookies
      document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.trim() + "; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      });

      // 導向登入頁面
      this.$router.push('/frontend/login');

      // 阻止返回上一頁
      history.pushState(null, null, location.href);
      window.onpopstate = function() {
        history.go(1); // 強制前進，阻止返回
      };

      // 強制刷新頁面，確保狀態重置
      location.reload();
    },
    async fetchUserData() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.username = response.data.username;
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      }
    },
    checkScreenSize() {
      this.isSmallScreen = window.innerWidth <= 768;
    }
  },
  mounted() {
    this.fetchUserData();
    this.checkScreenSize(); // 初始檢查螢幕大小
    window.addEventListener('resize', this.checkScreenSize); // 監聽螢幕大小變化
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
};
</script>

<!-- 引入外部的 CSS 文件 -->
<style scoped src="@/assets/css/frontend/SidebarPage.css"></style>
