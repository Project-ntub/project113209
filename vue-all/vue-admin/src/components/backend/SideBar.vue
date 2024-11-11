<template>
  <div>
    <!-- Sidebar only displayed if not on reset password or register page -->
    <div v-if="!hideSidebar" :class="['sidebar', { open: isSidebarActive }]">
      <div class="sidebar-header">
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
      <div class="user-section" @click="toggleUserLinks">
        <font-awesome-icon icon="user" class="icon user-icon" />
        <span v-if="isSidebarActive" class="username">{{ username }}</span>
        <!-- 向右移動的向下箭頭圖示，僅在側邊欄展開時顯示 -->
        <font-awesome-icon icon="angle-down" class="arrow-icon" v-if="isSidebarActive" />
      </div>
      <!-- User-related links, only visible when the user section is expanded -->
      <div v-if="showUserLinks" class="user-links">
        <router-link to="/backend/profile" class="sidebar-link">
          <span class="icon">👤</span>
          <span class="text">個人資料</span>
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
    
    <!-- content section -->
    <div :class="['content', { shift: isSidebarActive }]">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

export default {
  components: {
    FontAwesomeIcon
  },
  data() {
    return {
      username: '',
      showUserLinks: false, // Controls display of user-related links
    };
  },
  computed: {
    hideSidebar() {
      // Hide sidebar on specific pages
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
        await axios.post('/api/backend/logout/');
        localStorage.removeItem('token');
        history.replaceState(null, null, '/backend/login');
        window.addEventListener('popstate', () => {
          history.pushState(null, null, document.URL);
        });
        this.$router.replace('/backend/login');
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
    this.fetchUserData(); // Load user data on mount
  },
};
</script>

<style scoped src="@/assets/css/backend/SideBar.css"></style>
<style scoped>
.user-section {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.arrow-icon {
  margin-left: auto; /* 將箭頭推到最右邊 */
  padding-left: 4px;
}
</style>
