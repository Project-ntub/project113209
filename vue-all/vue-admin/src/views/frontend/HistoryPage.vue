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
                    <h4>{{ item.action_time }}</h4>
                  </div>
                  <div class="timeline-body">
                    <p>{{ item.action_description }}</p>
                    <p v-if="item.additional_info">更多信息: {{ item.additional_info }}</p>
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
  import SidebarPage from '@/components/frontend/SidebarPage.vue';
  import axios from 'axios';
  
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
          return item.action_description.toUpperCase().includes(query) || item.action_time.includes(query);
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
          const response = await axios.get('/api/frontend/check_login_status/', {
            headers: {
              'X-CSRFToken': csrfToken
            }
          });
          this.isLoggedIn = response.data.loggedIn;
          if (this.isLoggedIn) {
            this.fetchHistory();
          }
        } catch (error) {
          console.error('Login status check failed:', error);
        }
      },
      async fetchHistory() {
        try {
          const csrfToken = this.getCookie('csrftoken');
          const response = await axios.get('/api/frontend/history/', {
            headers: {
              'X-CSRFToken': csrfToken
            }
          });
          this.items = response.data;
        } catch (error) {
          console.error('無法獲取歷史記錄:', error);
        }
      },
      showDetail(id) {
        this.$router.push(`/frontend/detail/${id}`);
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
  