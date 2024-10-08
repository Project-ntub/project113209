<template>
  <TopNavbar title="歷史紀錄" />
  <div>
    <div class="container">
      <!-- Search Box -->
      <div class="search-container">
        <input type="text" v-model="searchQuery" placeholder="查尋歷史紀錄..." />
        <button @click="searchHistory">查尋</button>
        <button @click="refreshPage">重整</button>
      </div>
      
      <!-- Sort Box -->
      <div class="sort-container">
        <label for="sortField">排序依據:</label>
        <select v-model="sortField" id="sortField">
          <option value="timestamp">操作時間</option>
          <option value="username">用戶</option>
          <option value="action">操作</option>
        </select>

        <button @click="toggleSortOrder">排序順序: {{ sortOrder === 'asc' ? '升序' : '降序' }}</button>
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
      sortField: 'timestamp', // 默認排序字段
      sortOrder: 'asc' // 默認排序順序
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
      this.isLoading = true;
      try {
        const { data } = await axios.get('/api/backend/user_history/');
        console.log(data); // 調試用
        this.records = data;
      } catch (error) {
        console.error('Failed to fetch records:', error);
      } finally {
        this.isLoading = false;
      }
    },
    searchHistory() {
      // 搜尋功能由 computed: filteredRecords 處理
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
<style scoped src="@/assets/css/backend/HistoricalRecord.css"></style>
