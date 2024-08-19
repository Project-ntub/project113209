<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]">
      <div class="sidebar-header">
        <font-awesome-icon icon="user" class="icon" />
        <span v-if="isSidebarOpen">王曉明</span> <!-- 只在展开时显示 -->
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
      <router-link to="/frontend/home" data-tooltip="儀錶板管理">
        <font-awesome-icon icon="tachometer-alt" class="icon" />
        <span class="text">儀錶板管理</span>
      </router-link>
      <router-link to="/frontend/profile" data-tooltip="個人資訊">
        <font-awesome-icon icon="user" class="icon" />
        <span class="text">個人資訊</span>
      </router-link>
      <router-link to="/frontend/accountsettings" data-tooltip="帳號設定">
        <font-awesome-icon icon="users" class="icon" />
        <span class="text">帳號設定</span>
      </router-link>
      <router-link to="/frontend/history" data-tooltip="歷史紀錄">
        <font-awesome-icon icon="history" class="icon" />
        <span class="text">歷史紀錄</span>
      </router-link>
      <a href="#" @click.prevent="confirmLogout" data-tooltip="登出">
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
export default {
  name: "SidebarPage",
  data() {
    return {
      isSidebarOpen: false
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
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/SidebarPage.css"></style>
