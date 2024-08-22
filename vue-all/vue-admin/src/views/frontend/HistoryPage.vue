<template>
  <div>
    <SidebarPage />
    <div class="history-page">
      <div class="container">
        <div v-if="!isLoggedIn" class="no-history centered-content">
          <p>未登入，無紀錄顯示。</p>
        </div>
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
                  <p v-if="item.changes">更改內容: {{ item.changes }}</p>
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
<<<<<<< HEAD
import SidebarPage from '@/components/frontend/SidebarPage.vue';
import axios from 'axios';
=======
import SidebarPage from '@/components/frontend/SidebarPage.vue'; // 確保引入 SidebarPage 組件
import axios from '@/axios';
>>>>>>> 9e8bcbe0d766bbd0cd6fc4dbfbb99fe547af9fec

export default {
  name: 'HistoryPage',
  components: {
    SidebarPage
  },
  data() {
    return {
      searchQuery: '',
      items: [],
      isLoggedIn: false,
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
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    async checkLoginStatus() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        const response = await axios.get('/frontend/check_login_status/', {
          headers: {
            'X-CSRFToken': csrfToken
          }
        });
        this.isLoggedIn = response.data.loggedIn;
        if (this.isLoggedIn) {
<<<<<<< HEAD
          this.fetchHistory();
=======
          this.fetchHistory(); // 如果已登入，則獲取歷史記錄
        } else {
          this.$router.pugh('/login');
>>>>>>> 9e8bcbe0d766bbd0cd6fc4dbfbb99fe547af9fec
        }
      } catch (error) {
        console.error('無法檢查登入狀態:', error);
      }
    },
    async fetchHistory() {
      try {
<<<<<<< HEAD
        const csrfToken = this.getCookie('csrftoken');
        const response = await axios.get('/frontend/history/', {
          headers: {
            'X-CSRFToken': csrfToken
          }
        });
        this.items = response.data.history;
=======
        const response = await axios.get('/api/frontend/history/'); // 調用後端 API 獲取數據
        this.items = response.data; // 將獲取到的數據賦值給 items
>>>>>>> 9e8bcbe0d766bbd0cd6fc4dbfbb99fe547af9fec
      } catch (error) {
        console.error('無法獲取歷史記錄:', error);
      }
    },
    showDetail(id) {
      this.$router.push(`/detail/${id}`);
    }
  },
  mounted() {
    this.checkLoginStatus();
  }
}
</script>

<style scoped>
.history-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
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
  text-align: left;
}
</style>
