<template>
  <div>
    <!-- 側邊欄 -->
    <div :class="['sidebar', { open: isSidebarOpen }]">
      <div class="sidebar-header">
        <span v-if="isSidebarOpen" class="username">{{ username }}</span>
        <span class="toggle-btn" @click="toggleSidebar">☰</span>
      </div>
      <div class="user-section" @click="toggleUserLinks">
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

    <!-- 內容區域 -->
    <div :class="['content', { shift: isSidebarOpen }]">
      <slot></slot>
    </div>
  </div>
</template>
<script>
import axios from "axios";

export default {
  name: "BackendSidebar",
  data() {
    return {
      isSidebarOpen: false, // 側邊欄開關狀態
      username: "", // 使用者名稱
    };
  },
  methods: {
    toggleSidebar() {
      // 切換側邊欄開關狀態
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    confirmLogout() {
      // 確認是否登出
      const confirmed = confirm("確定要登出嗎？");
      if (confirmed) {
        this.logout();
      }
    },
    async logout() {
      try {
        await axios.post("/api/backend/logout/");
      } catch (error) {
        console.error("登出失敗", error);
      }

      // 清除本地數據並跳轉到登入頁面
      window.localStorage.clear();
      window.sessionStorage.clear();
      document.cookie.split(";").forEach((c) => {
        document.cookie = c.trim() + "; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      });
      this.$router.push("/backend/login");
      location.reload();
    },
    async fetchUserData() {
      try {
        const response = await axios.get("/api/backend/profile/");
        this.username = response.data.username;
      } catch (error) {
        console.error("無法獲取用戶資料:", error);
      }
    },
  },
  mounted() {
    this.fetchUserData();
  },
};
</script>
<style scoped>
/* 側邊欄樣式 */
.sidebar {
  height: 100vh;
  width: 80px;
  position: fixed;
  top: 0;
  left: 0;
  background-color: #1e1e2f;
  transition: width 0.3s ease;
  z-index: 1050;
  display: flex;
  flex-direction: column;
}

.sidebar.open {
  width: 180px;
}

.sidebar-header {
  padding: 15px;
  font-size: 30px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #13131e;
}

.username {
  margin-left: 10px;
  font-size: 1.2rem; /* 增大字體，增強可讀性 */
  color: #ffffff !important; /* 確保字體顏色是白色 */
}

.toggle-btn {
  font-size: 24px;
  cursor: pointer;
  color: #fff;
}

/* 側邊欄選單樣式 */
.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-link {
  text-decoration: none;
  font-size: 16px;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 15px 20px;
  transition: background-color 0.3s ease, padding-left 0.2s ease;
}

.sidebar-link:hover {
  background-color: #3a3a4f;
  padding-left: 30px;
}

.sidebar-link .icon {
  margin-right: 10px;
  font-size: 20px;
}

.sidebar-link .text {
  display: none;
}

.sidebar.open .sidebar-link .text {
  display: inline-block;
}

/* 內容區域樣式 */
.content {
  margin-left: 80px;
  padding: 20px;
  transition: margin-left 0.3s ease;
}

.sidebar.open ~ .content {
  margin-left: 250px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }

  .sidebar.open {
    width: 200px;
  }

  .content {
    margin-left: 80px;
  }

  .sidebar.open ~ .content {
    margin-left: 200px;
  }
}
</style>
