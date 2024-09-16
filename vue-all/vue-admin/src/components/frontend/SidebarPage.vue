<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]">
      <div class="sidebar-header">
        <!-- 替換圖標，這裡使用 "home" 圖標 -->
        <font-awesome-icon icon="home" class="icon" />
        <span v-if="isSidebarOpen">{{ username }}</span> <!-- 只在展開時顯示 -->
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
  name: "SidebarPage",
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
      const confirmed = confirm("確定要登出嗎？");
      if (confirmed) {
        this.logout();
      }
    },
    logout() {
      alert("已登出");
      this.$router.push('/frontend/login');
    },
    async fetchUserData() {
      try {
        const response = await axios.get('/api/frontend/profile/'); // 替换为您的用户信息 API 路径
        this.username = response.data.username;
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      }
    }
  },
  mounted() {
    this.fetchUserData(); // 获取用户信息
  }
};
</script>

<style scoped src="@/assets/css/frontend/SidebarPage.css"></style>
