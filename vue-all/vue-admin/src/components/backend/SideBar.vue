<template>
  <div>
    <!-- 只有當前頁面不是重設密碼或註冊頁面時顯示 sidebar -->
    <div v-if="!hideSidebar" :class="['sidebar', { open: isSidebarActive }]">
      <div class="sidebar-header">
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
      <div class="user-section" @click="toggleUserLinks">
        <font-awesome-icon icon="user" class="icon user-icon" />
        <span v-if="isSidebarActive" class="username">{{ username }}</span>
      </div>
      <!-- User-related links, only visible when the user section is expanded -->
      <div v-if="showUserLinks" class="user-links">
        <router-link to="/backend/profile" class="sidebar-link">
          <span class="icon">👤</span>
          <span class="text">個人資料</span>
        </router-link>
        <router-link to="/backend/preferences" class="sidebar-link">
          <span class="icon">⚙️</span>
          <span class="text">個人偏好</span>
        </router-link>
      </div>
      <!-- General links -->
      <router-link to="/backend/dashboard" class="sidebar-link">
        <span class="icon">📈</span>
        <span class="text">儀錶板管理</span>
      </router-link>
      <router-link to="/backend/user-management" class="sidebar-link">
        <span class="icon">👥</span>
        <span class="text">用戶管理</span>
      </router-link>
      <router-link to="/backend/role-management" class="sidebar-link">
        <span class="icon">🔧</span>
        <span class="text">角色管理</span>
      </router-link>
      <router-link to="/backend/history" class="sidebar-link">
        <span class="icon">🕒</span>
        <span class="text">歷史紀錄</span>
      </router-link>
      <button class="sidebar-link logout-btn" @click="confirmLogout">
        <span class="icon">🚪</span>
        <span class="text">登出</span>
      </button>
    </div>
    
    <!-- content 部分 -->
    <div :class="['content', { shift: isSidebarActive }]">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      showUserLinks: false, // 控制用戶相關鏈接的顯示
    };
  },
  computed: {
    hideSidebar() {
      // 當路由名稱為 "BackendForgetPassword" 或 "BackendRegister" 時，隱藏 sidebar
      return this.$route.name === 'BackendForgetPassword' || this.$route.name === 'BackendRegister';
    },
  },
  props: {
    isSidebarActive: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar');
    },
    toggleUserLinks() {
      this.showUserLinks = !this.showUserLinks;
    },
    confirmLogout() {
      const confirmed = confirm('確定要登出嗎？');
      if (confirmed) {
        this.handleLogout();
      }
    },
    async handleLogout() {
      try {
        // 發送登出請求到後端
        await axios.get('/backend/logout/');

        // 清除前端的 localStorage 和 sessionStorage
        localStorage.removeItem('frontend_token');
        localStorage.removeItem('backend_token');

        // 防止使用返回按鈕回到已登入頁面
        history.replaceState(null, null, '/backend/login');
        window.addEventListener('popstate', () => {
          history.pushState(null, null, document.URL);
        });

        // 導向登入頁面
        this.$router.replace('/backend/login');

        // 強制刷新頁面，清除所有舊的狀態
        setTimeout(() => {
          location.reload();
        }, 100);
      } catch (error) {
        console.error('登出失敗', error);
      }
    },
    async fetchUserData() {
      try {
        const response = await axios.get('/api/backend/profile/');
        this.username = response.data.username;
      } catch (error) {
        console.error('無法獲取用戶資料:', error);
      }
    },
  },
  mounted() {
    this.fetchUserData(); // 進入頁面時加載用戶資料
  },
};
</script>

<style scoped src="@/assets/css/backend/SideBar.css"></style>
