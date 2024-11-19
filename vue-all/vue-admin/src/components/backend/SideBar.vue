<template>
  <div>
    <!-- Sidebar only displayed if not on reset password or register page -->
    <div v-if="!hideSidebar" :class="['sidebar', { open: isSidebarActive }]">
      <div class="sidebar-header">
        <span class="toggle-btn" @click="toggleSidebar" style="color: #333 !important;">☰</span>
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
.sidebar {
  width: 250px; /* 調整側邊欄寬度 */
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: #b3e5fc; /* 改為淡藍色背景 */
  padding-top: 20px; /* 增加頂部間距 */
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); /* 輕微陰影 */
  transition: all 0.3s ease; /* 增加動畫效果 */
}

.sidebar.open {
  width: 250px; /* 側邊欄展開的寬度 */
}

.sidebar:not(.open) {
  width: 120px; /* 側邊欄收起的寬度，調整為更寬 */
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: 15px 20px; /* 增加間距，讓元素更寬鬆 */
  margin: 10px 15px; /* 增加項目之間的間距 */
  text-decoration: none;
  color: #333 !important; /* 字體顏色加上 !important */
  font-weight: bold; /* 加粗文字 */
  font-size: 1.1rem; /* 增大字體 */
  border-radius: 10px; /* 圓角背景 */
  border-bottom: 1px solid #000; /* 添加分隔線 */
  transition: background 0.3s ease, box-shadow 0.3s ease; /* 過渡效果 */
}

.sidebar-link .icon {
  font-size: 1.6rem; /* 增大圖標大小 */
  margin-right: 20px; /* 增加圖標和文字之間的間距 */
  color: #333 !important; /* 圖標的顏色也設為黑色 */
}

.sidebar-link:hover {
  background: #e0e4e7; /* 懸停時背景顏色變化 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* 輕微陰影增強懸停效果 */
}

.sidebar-link.active {
  background: #4285f4; /* 被選中項目藍色背景 */
  color: #ffffff !important; /* 被選中項目文字變為白色 */
}

.sidebar-link.active .icon {
  color: #ffffff !important; /* 被選中項目的圖標顏色變為白色 */
}

.user-section {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  background: #34495e; /* 比較深的背景色，和側邊欄形成區分 */
  color: #333 !important; /* 使用黑色字體增強對比 */
  font-weight: bold; /* 加粗文字 */
  transition: background 0.3s ease;
}

.user-section:hover {
  background: #3b5773; /* 懸停效果 */
}

.user-icon {
  font-size: 1.8rem; /* 增大圖標大小 */
  margin-right: 10px;
  color: #333 !important; /* 圖標顏色設為黑色 */
}

.username {
  margin-left: 10px;
  font-size: 1.2rem; /* 增大字體，增強可讀性 */
  color: #333 !important; /* 確保字體顏色是黑色 */
}

.logout-btn {
  background: #c0392b; /* 強調登出按鈕的危險性 */
  color: #ecf0f1;
  border: none;
  width: calc(100% - 30px);
  padding: 15px 20px;
  text-align: left;
  cursor: pointer;
  margin: 10px 15px;
  border-radius: 10px;
  transition: background 0.3s ease, box-shadow 0.3s ease;
  font-weight: bold; /* 加粗文字 */
  font-size: 1.1rem; /* 增大字體 */
}

.logout-btn:hover {
  background: #e74c3c; /* 懸停時更亮的紅色 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* 懸停效果的陰影 */
}

.content.shift {
  margin-left: 250px; /* 根據側邊欄的新寬度進行偏移 */
  transition: margin-left 0.3s ease;
}
</style>
