<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]">
      <div class="sidebar-header">
        <font-awesome-icon icon="user" class="icon" />
        <span v-if="isSidebarOpen">{{ username }}</span>
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
      <router-link to="/frontend/home" class="sidebar-link">
        <font-awesome-icon icon="tachometer-alt" class="icon" />
        <span class="text">儀錶板管理</span>
      </router-link>
      <router-link to="/frontend/profile" class="sidebar-link">
        <font-awesome-icon icon="user" class="icon" />
        <span class="text">個人資訊</span>
      </router-link>
      <router-link to="/frontend/accountsettings" class="sidebar-link">
        <font-awesome-icon icon="users" class="icon" />
        <span class="text">帳號設定</span>
      </router-link>
      <a href="#" class="sidebar-link" @click.prevent="confirmLogout">
        <font-awesome-icon icon="sign-out-alt" class="icon" />
        <span class="text">登出</span>
      </a>
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
      username: '' // 用來存儲用戶名
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    confirmLogout() {
      const confirmed = confirm('確定要登出嗎？');
      if (confirmed) {
        this.handleLogout(); // 調用 handleLogout 方法進行登出
      }
    },
    async handleLogout() {
      try {
        // 發送登出請求到後端，清除 session
        await axios.get('/frontend/logout/');

        // 清除前端的 localStorage 和 sessionStorage
        localStorage.removeItem('frontend_token');
        localStorage.removeItem('backend_token');

        // 防止使用返回按鈕回到已登入頁面
        history.replaceState(null, null, '/frontend/login');
        window.addEventListener('popstate', () => {
          history.pushState(null, null, document.URL);
        });

        // 導向登入頁面
        this.$router.replace('/frontend/login');

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
        const response = await axios.get('/api/frontend/profile/');
        this.username = response.data.username;
      } catch (error) {
        console.error('無法獲取用戶資料:', error);
      }
    }
  },
  mounted() {
    this.fetchUserData(); // 進入頁面時加載用戶資料
  }
};
</script>

<style scoped src="@/assets/css/frontend/SidebarPage.css"></style>
