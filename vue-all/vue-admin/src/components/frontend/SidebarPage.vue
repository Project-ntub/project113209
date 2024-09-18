<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]">
      <div class="sidebar-header">
        <font-awesome-icon icon="user" class="user-icon" />
        <span v-if="isSidebarOpen">{{ username }}</span>
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>

      <!-- 儀表板 -->
      <router-link to="/frontend/home" class="sidebar-link">
        <font-awesome-icon icon="chart-pie" class="icon" />
        <span class="text">儀錶板管理</span>
      </router-link>

      <!-- 個人資訊 -->
      <router-link to="/frontend/profile" class="sidebar-link">
        <font-awesome-icon icon="user" class="icon" />
        <span class="text">個人資訊</span>
      </router-link>

      <!-- 帳號設定 -->
      <router-link to="/frontend/accountsettings" class="sidebar-link">
        <font-awesome-icon icon="cogs" class="icon" />
        <span class="text">帳號設定</span>
      </router-link>

      <!-- 登出 -->
      <a href="#" class="sidebar-link logout-btn" @click.prevent="confirmLogout">
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
      alert("已登出");
      this.$router.push('/frontend/login');
    },
    async fetchUserData() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.username = response.data.username;
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      }
    }
  },
  mounted() {
    this.fetchUserData();
  }
};
</script>

<!-- 引入分離的 CSS 文件 -->
<style scoped src="@/assets/css/frontend/SidebarPage.css"></style>
