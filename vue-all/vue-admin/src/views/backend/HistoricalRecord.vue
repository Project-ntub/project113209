<template>
  <TopNavbar title="歷史紀錄" />
  <div>
    <div v-if="isLoading" class="loading-container">
      <div class="loading-animation"></div>
      <p class="loading-text">載入中，請稍等...</p>
    </div>
    <div v-else-if="hasPermission" class="container">
      <!-- Search and Sort Container -->
      <div class="search-sort-container">
        <!-- Search Box -->
        <div class="search-container">
          <input type="text" v-model="searchQuery" placeholder="查尋歷史紀錄..." />
          <button @click="searchHistory" class="search-btn">查尋</button>
          <button @click="refreshPage" class="refresh-btn">重整</button>
        </div>
        
        <!-- Sort Box -->
        <div class="sort-container">
          <label for="sortField">排序依據:</label>
          <select v-model="sortField" id="sortField">
            <option value="timestamp">操作時間</option>
            <option value="username">用戶</option>
            <option value="action">操作</option>
          </select>

          <button @click="toggleSortOrder" class="sort-order-btn">
            排序順序: {{ sortOrder === 'asc' ? '升序' : '降序' }}
          </button>
        </div>
      </div>
  
      <!-- History Records Section -->
      <div class="history-container">
        <div class="table-container">
          <table class="history-table" id="history-table">
            <thead>
              <tr>
                <th>編號</th>
                <th>用戶</th>
                <th>歷史操作</th>
                <th>電子郵件</th>
                <th>操作時間</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in filteredRecords" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ record.user ? record.user.username : '未知' }}</td>
                <td>{{ record.action }}</td>
                <td>{{ record.user ? record.user.email : 'N/A' }}</td>
                <td>{{ formatDateTime(record.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else>
      <p>您沒有權限觀看</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import TopNavbar from '@/components/frontend/TopNavbar.vue';

export default {
  name: 'HistoricalRecord',
  components: {
    TopNavbar,
  },
  data() {
    return {
      searchQuery: '',
      isLoading: false,
      records: [],
      sortField: 'timestamp', // Default sorting field
      sortOrder: 'asc', // Default sorting order
      hasPermission: true, // Indicates if the user has permission
    };
  },
  computed: {
    filteredRecords() {
      let records = this.records.filter((record) =>
        ['user_id', 'userName', 'userAction', 'userEmail'].some((key) => {
          const value = record[key];
          return typeof value === 'string'
            ? value.toLowerCase().includes(this.searchQuery.toLowerCase())
            : String(value).includes(this.searchQuery);
        })
      );

      // Sort the records
      records = records.sort((a, b) => {
        let fieldA = this.sortField === 'username' ? (a.user ? a.user.username : '') : a[this.sortField];
        let fieldB = this.sortField === 'username' ? (b.user ? b.user.username : '') : b[this.sortField];

        if (fieldA < fieldB) return this.sortOrder === 'asc' ? -1 : 1;
        if (fieldA > fieldB) return this.sortOrder === 'asc' ? 1 : -1;
        return 0;
      });

      return records;
    }
  },
  methods: {
    async fetchRecords() {
      this.isLoading = true; // Show loading animation
      try {
        const { data } = await axios.get('/api/backend/user_history/');
        console.log(data); // For debugging
        this.records = data;
      } catch (error) {
        if (error.response && error.response.status === 403) {
          // If the backend returns 403, it means no permission
          this.hasPermission = false;
        } else {
          console.error('Failed to fetch records:', error);
        }
      } finally {
        this.isLoading = false; // Hide loading animation after data is fetched
      }
    },
    searchHistory() {
      // Search logic is handled by computed: filteredRecords
    },
    refreshPage() {
      this.fetchRecords();
    },
    formatDateTime(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    }
  },
  mounted() {
    this.fetchRecords();
  }
};
</script>

<style scoped>
body, html {
  margin: 0;
  padding: 0;
  font-family: 'Poppins', sans-serif;
  background-color: #f0f8ff;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.loading-animation {
  border: 10px solid #f3f3f3;
  border-top: 10px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

.loading-text {
  font-size: 20px;
  color: #333;
  margin-top: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.container {
  margin: 0 auto;
  padding: 20px 30px;
  max-width: 1200px;
  width: 100%;
  box-sizing: border-box;
  background-color: #ffffff;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.search-sort-container {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-container input {
  width: 300px;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #3498db;
  border-radius: 5px;
  margin-right: 10px;
}

.search-btn, .refresh-btn, .sort-order-btn {
  padding: 10px 15px;
  font-size: 16px;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-btn {
  background-color: #3498db;
}

.search-btn:hover {
  background-color: #2c81b7;
}

.refresh-btn {
  background-color: #4a90e2;
}

.refresh-btn:hover {
  background-color: #357ab8;
}

.sort-container label {
  font-weight: bold;
  color: #333;
}

.sort-container select {
  width: 150px;
  padding: 10px;
  border: 2px solid #e67e22;
  background-color: #f39c12;
  color: #ffffff;
  border-radius: 5px;
  cursor: pointer;
}

.sort-order-btn {
  background-color: #e67e22;
}

.sort-order-btn:hover {
  background-color: #d35400;
}

.history-container {
  max-width: 100%;
  margin-top: 20px;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  background-color: #ffffff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th, .history-table td {
  border: 1px solid #ddd;
  padding: 15px;
  text-align: center;
  font-size: 16px;
}

.history-table th {
  background-color: #4a90e2;
  color: #ffffff;
}

.history-table tr:nth-child(even) {
  background-color: #e1f5fe;
}

.history-table tr:nth-child(odd) {
  background-color: #ffeaa7;
}

.history-table tr:hover {
  background-color: #ffeb3b;
}
</style>
