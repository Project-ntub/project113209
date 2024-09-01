<template>
  <div>
    <div :class="['sidebar', { open: isSidebarActive }]">
      <div class="sidebar-header">
        <h2 v-if="isSidebarActive">管理介面</h2> <!-- 只在展開時顯示 -->
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
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
      <router-link to="/backend/preferences" class="sidebar-link">
        <span class="icon">⚙️</span>
        <span class="text">個人偏好</span>
      </router-link>
      <router-link to="/backend/profile" class="sidebar-link">
        <span class="icon">👤</span>
        <span class="text">個人資料</span>
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
export default {
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
    logout() {
      this.$router.push('/backend/login');
    }
  }
};
</script>

<style src="@/assets/css/backend/SideBar.css"></style>
