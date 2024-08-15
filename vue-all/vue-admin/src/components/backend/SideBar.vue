<!-- Sidebar.vue -->
<template>
    <div class="sidebar" :class="{ active: isSidebarActive }">
      <h2>管理介面</h2>
      <router-link to="/management/dashboard">儀錶板管理</router-link>
      <router-link to="/management/user-management">用戶管理</router-link>
      <router-link to="/management/role-management">角色管理</router-link>
      <router-link to="/management/history">歷史紀錄</router-link>
      <router-link to="/management/preferences">個人偏好</router-link>
      <router-link to="/management/profile">個人資料</router-link>
      <button class="logout-btn" @click="logout">登出</button>
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
      logout() {
        this.$router.push('/login');
      }
    }
  };
  </script>
  
  <style scoped src="@/assets/css/backend/SideBar.css"></style>

  