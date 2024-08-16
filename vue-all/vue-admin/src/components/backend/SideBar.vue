<template>
  <div>
    <!-- Hamburger Menu -->
    <div class="hamburger-menu" @click="toggleSidebar">
      <div class="hamburger-icon">☰</div>
    </div>
    <!-- Sidebar Content -->
    <div class="sidebar" :class="{ active: isSidebarActive }">
      <h2>管理介面</h2>
      <router-link to="/backend/dashboard">儀錶板管理</router-link>
      <router-link to="/backend/user-management">用戶管理</router-link>
      <router-link to="/backend/role-management">角色管理</router-link>
      <router-link to="/backend/history">歷史紀錄</router-link>
      <router-link to="/backend/preferences">個人偏好</router-link>
      <router-link to="/backend/profile">個人資料</router-link>
      <button class="logout-btn" @click="logout">登出</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isSidebarActive: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar'); // Emit an event to the parent component to handle the toggle
    },
    logout() {
      this.$router.push('/backend/login');
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/SideBar.css"></style>
