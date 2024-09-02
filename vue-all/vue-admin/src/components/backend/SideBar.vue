<template>
  <div>
    <div :class="['sidebar', { open: isSidebarActive }]">
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
      <button class="sidebar-link logout-btn" @click="logout">
        <span class="icon">🚪</span>
        <span class="text">登出</span>
      </button>
    </div>
    <div :class="['content', { shift: isSidebarActive }]">
      <slot></slot>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  data(){
    return{
      username: '',
      showUserLinks: false  // State to control the visibility of user-related links
    };
  },
  props: {
    isSidebarActive: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar');
    },
    toggleUserLinks() {
      this.showUserLinks = !this.showUserLinks;
    },
    logout() {
      this.$router.push('/backend/login');
    }, 
    async fetchUserData() {
      try {
        const response = await axios.get('/api/frontend/profile/'); // 替换为你的用户信息 API 路径
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

<style src="@/assets/css/backend/SideBar.css"></style>

