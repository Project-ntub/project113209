<template>
  <div>
    <SidebarPage /> <!-- 確保 SidebarPage 組件在這裡使用 -->
    <div class="history-page">
      <div class="container">
        <!-- 顯示未登入狀態的消息 -->
        <div v-if="!isLoggedIn" class="no-history centered-content">
          <p>未登入，無紀錄顯示。</p>
        </div>
        <!-- 顯示登入狀態下的歷史紀錄 -->
        <div v-else>
          <div class="search-container centered-content">
            <input type="text" id="searchInput" placeholder="搜尋紀錄..." v-model="searchQuery">
            <button @click="filterTimeline">搜尋</button>
          </div>
          <ul class="timeline centered-content" id="timeline">
            <li class="timeline-item" v-for="item in filteredItems" :key="item.id" @click="showDetail(item.id)">
              <div class="timeline-panel">
                <div class="timeline-heading">
                  <h4>{{ item.date }}</h4>
                </div>
                <div class="timeline-body">
                  <p>{{ item.action }}</p>
                  <div class="timeline-user">使用者: {{ item.user }}</div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SidebarPage from '@/components/frontend/SidebarPage.vue'; // 確保引入 SidebarPage 組件
import axios from 'axios';

export default {
  name: 'HistoryPage',
  components: {
    SidebarPage // 註冊 SidebarPage 組件
  },
  data() {
    return {
      searchQuery: '',
      items: [], // 初始化為空，後續通過 API 獲取數據
      isLoggedIn: false, // 初始化為未登入狀態
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(item => {
        const query = this.searchQuery.trim().toUpperCase();
        return item.action.toUpperCase().includes(query) || item.date.includes(query);
      });
    }
  },
  methods: {
    filterTimeline() {
      // 使用计算属性进行过滤，不需要额外的过滤逻辑
    },
    showDetail(id) {
      this.$router.push(`/detail/${id}`);
    },
    async checkLoginStatus() {
      try {
        const response = await axios.get('/api/frontend/check_login_status'); // 確保 API 路徑正確
        this.isLoggedIn = response.data.loggedIn;
        if (this.isLoggedIn) {
          this.fetchHistory(); // 如果已登入，則獲取歷史記錄
        }
      } catch (error) {
        console.error('無法檢查登入狀態:', error);
      }
    },
    async fetchHistory() {
      try {
        const response = await axios.get('/api/frontend/history'); // 調用後端 API 獲取數據
        this.items = response.data; // 將獲取到的數據賦值給 items
      } catch (error) {
        console.error('無法獲取歷史記錄:', error);
      }
    }
  },
  mounted() {
    this.checkLoginStatus(); // 組件掛載後先檢查登入狀態
  }
}
</script>

<style scoped>
.history-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* 使頁面高度充滿視窗 */
}

.container {
  width: 100%;
  max-width: 800px; /* 設定容器最大寬度 */
  margin: 0 auto;
  padding: 20px;
  text-align: center; /* 使內容置中 */
}

.centered-content {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.no-history {
  font-size: 18px;
  color: #555;
}

.search-container {
  margin-bottom: 20px;
}

.timeline {
  list-style: none;
  padding: 0;
}

.timeline-item {
  margin-bottom: 20px;
}

.timeline-panel {
  background: #f8f9fa;
  border-radius: 5px;
  padding: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: left; /* 保持左對齊 */
}
</style>
