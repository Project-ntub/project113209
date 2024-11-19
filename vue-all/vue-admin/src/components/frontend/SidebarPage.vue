<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen, smallScreen: isSmallScreen }]">
      <!-- 顯示一個圖示，點擊後展開側邊欄 -->
      <div class="sidebar-header">
        <font-awesome-icon
          icon="user"
          class="icon user-icon"
          v-if="!isSmallScreen || isSidebarOpen" 
        />
        <span v-if="isSidebarOpen">{{ username }}</span>
        <span class="toggle-btn" @click="toggleSidebar" style="color: #333 !important;">☰</span>
      </div>

      <!-- 大螢幕時顯示所有圖示，小螢幕時依賴 v-if 展開 -->
      <div v-if="isSidebarOpen || !isSmallScreen">
        <!-- 儀表板 -->
        <router-link to="/frontend/home" class="sidebar-link">
          <font-awesome-icon icon="chart-pie" class="icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">儀錶板管理</span>
        </router-link>

        <!-- 個人資訊 -->
        <router-link to="/frontend/profile" class="sidebar-link">
          <font-awesome-icon icon="user" class="icon second-icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">個人資訊</span>
        </router-link>

        <!-- 登出 -->
        <a href="#" class="sidebar-link logout-btn" @click.prevent="confirmLogout">
          <font-awesome-icon icon="sign-out-alt" class="icon" />
          <span class="text" v-if="isSidebarOpen || !isSmallScreen">登出</span>
        </a>
      </div>
    </div>

    <div :class="['content', { shift: isSidebarOpen }]">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

export default {
  name: 'SidebarPage',
  components: {
    FontAwesomeIcon
  },
  data() {
    return {
      isSidebarOpen: false,
      isSmallScreen: false, // 判斷是否為小螢幕
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
    async logout() {
      try {
        // 發送登出請求到後端
        await axios.post('/api/backend/logout/');
      } catch (error) {
        console.error('登出失敗', error);
      }

      // 清除 localStorage
      window.localStorage.clear();

      // 清除 sessionStorage
      window.sessionStorage.clear();

      // 清除所有 Cookies
      document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.trim() + "; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      });

      // 導向登入頁面
      this.$router.push('/frontend/login');

      // 阻止返回上一頁
      history.pushState(null, null, location.href);
      window.onpopstate = function() {
        history.go(1); // 強制前進，阻止返回
      };

      // 強制刷新頁面，確保狀態重置
      location.reload();
    },
    async fetchUserData() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.username = response.data.username;
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      }
    },
    checkScreenSize() {
      this.isSmallScreen = window.innerWidth <= 768;
    }
  },
  mounted() {
    this.fetchUserData();
    this.checkScreenSize(); // 初始檢查螢幕大小
    window.addEventListener('resize', this.checkScreenSize); // 監聽螢幕大小變化
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
};
</script>

<style scoped>
.sidebar {
  height: 100vh;
  width: 80px; /* 未展開時的寬度調整為更寬 */
  position: fixed;
  top: 0;
  left: 0;
  background-color: #b3e5fc; /* 改為淡藍色背景 */
  overflow-x: hidden;
  transition: width 0.3s ease;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  box-sizing: border-box;
}

.sidebar.open {
  width: 250px; /* 展開時的寬度調整為更寬 */
}

.sidebar-header {
  padding: 10px 15px;
  font-size: 25px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: start;
  gap: 10px;
  margin-top: 100px; /* 調整這裡的值來控制圖示向下的距離 */
  background-color: #636262; /* 保持側邊欄頂部背景為黑色 */
}

.sidebar-link {
  text-decoration: none;
  font-size: 18px;
  color: #333 !important; /* 改為深灰色字體顏色 */
  display: flex;
  align-items: center;
  padding: 15px 20px; /* 增加間距，讓元素更寬鬆 */
  position: relative;
  background-color: transparent; /* 圖示背景透明 */
  border-bottom: 1px solid #ccc; /* 為每個選項之間增加分隔線 */
  transition: background 0.3s ease;
}

.sidebar-link:hover {
  background-color: #e0e4e7; /* 懸停時背景顏色變化 */
}

.sidebar-link .icon {
  margin-right: 10px;
  display: inline-block;
  width: 25px;
  text-align: center;
  font-size: 33px;
  background-color: transparent; /* 去除背景陰影色 */
}

.sidebar.open .sidebar-link .icon {
  background-color: transparent; /* 展開時保持圖示背景透明 */
}

.sidebar.open .sidebar-link .text {
  display: inline-block;
}

.sidebar-link .text {
  display: none; /* 收起時隱藏文字 */
}

.sidebar.open ~ .content {
  margin-left: 250px; /* 展開時的內容偏移調整為更寬 */
}

.sidebar ~ .content {
  margin-left: 80px; /* 未展開時的內容偏移調整為更寬 */
}

.sidebar .toggle-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  font-size: 30px;
  cursor: pointer;
  color: white;
}

.logout {
  margin-top: auto;
  padding-bottom: 20px;
  background-color: transparent; /* 縮小時隱藏底部黑色背景 */
}

.sidebar.open .logout {
  background-color: #636262; /* 展開時顯示底部背景 */
}

.content {
  padding: 20px;
  transition: margin-left 0.3s;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .sidebar {
    width: 80px; /* 小螢幕時未展開寬度調整為更寬 */
  }

  .sidebar.open {
    width: 200px; /* 小螢幕展開時的寬度調整為更寬 */
    background-color: #636262; /* 強制展開時不透明背景 */
  }

  .sidebar-link {
    display: none; /* 小螢幕未展開時隱藏所有選單項目 */
  }

  .sidebar.open .sidebar-link {
    display: flex; /* 展開時顯示所有選單項目 */
  }

  .sidebar ~ .content {
    margin-left: 80px;
  }

  .sidebar.open ~ .content {
    margin-left: 200px;
  }

  /* 設置側邊欄的底部部分透明，並且保留頂部部分背景 */
  .sidebar {
    background: linear-gradient(to bottom, #636262 0%, transparent 0%);
  }

  /* 隱藏側邊欄頂部區塊背景 */
  .sidebar-header {
    background-color: transparent !important; /* 小螢幕時設置背景為透明 */
  }

  /* 隱藏圖示 */
  .sidebar-header .icon {
    display: none; /* 小螢幕時隱藏圖示 */
  }
}
</style>
