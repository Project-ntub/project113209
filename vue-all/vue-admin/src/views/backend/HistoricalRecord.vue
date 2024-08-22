<template>
  <div>
    <div class="container" >
      <!-- Search Box -->
      <div class="search-container">
        <input type="text" v-model="searchQuery" placeholder="查尋歷史紀錄..." />
        <button @click="searchHistory">查尋</button>
        <button @click="refreshPage">重整</button>
      </div>
  
      <!-- Modal for adding records -->
      <div v-if="isAddRecordModalVisible" class="modal" @click.self="closeModal('addRecordModal')">
        <div class="modal-content">
          <span class="close" @click="closeModal('addRecordModal')">&times;</span>
          <form @submit.prevent="addRecord">
            <label for="userName">用戶:</label>
            <input type="text" v-model="newRecord.userName" required /><br /><br />
            <label for="userAction">操作:</label>
            <input type="text" v-model="newRecord.userAction" required /><br /><br />
            <label for="userEmail">電子郵件:</label>
            <input type="email" v-model="newRecord.userEmail" required /><br /><br />
            <label for="timestamp">操作時間:</label>
            <input type="datetime-local" v-model="newRecord.timestamp" required /><br /><br />
            <button type="submit">新增紀錄</button>
          </form>
        </div>
      </div>
  
      <!-- History Records Section -->
      <div class="history-container">
        <h2>歷史紀錄</h2>
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
              <td>{{ record.user_id }}</td>
              <td>{{ record.action }}</td> <!-- 使用返回数据中的action字段 -->
              <td>{{ record.userEmail || 'N/A' }}</td> <!-- 如果没有userEmail，显示N/A -->
              <td>{{ formatDateTime(record.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'HistoricalRecord',
  data() {
    return {
      searchQuery: '',
      isAddRecordModalVisible: false,
      isLoading: false,
      newRecord: {
        userName: '',
        userAction: '',
        userEmail: '',
        timestamp: '',
      },
      records: [],
      isSidebarActive: false,
    };
  },
  computed: {
    filteredRecords() {
      return this.records.filter((record) =>
        ['user_id', 'userName', 'userAction', 'userEmail'].some((key) => {
          const value = record[key];
          return typeof value === 'string'
            ? value.toLowerCase().includes(this.searchQuery.toLowerCase())
            : String(value).includes(this.searchQuery); // 对非字符串类型，直接转换为字符串再进行匹配
        })
      );
    },
  },
  methods: {
    openModal(modalName) {
      if (modalName === 'addRecordModal') {
        this.isAddRecordModalVisible = true;
      }
    },
    closeModal(modalName) {
      if (modalName === 'addRecordModal') {
        this.isAddRecordModalVisible = false;
      }
    },
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
    async addRecord() {
      this.isLoading = true;
      try {
        await axios.post('/api/backend/user_history/', this.newRecord);
        this.records.push({ ...this.newRecord });
        this.newRecord = { userName: '', userAction: '', userEmail: '', timestamp: '' };
        this.closeModal('addRecordModal');
      } catch (error) {
        alert('Failed to add record: ' + error.response.data.message || 'Unknown error');
        console.error('Failed to add record:', error);
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
  },
  mounted() {
    this.fetchRecords();
  },
};
</script>

<style scoped src="@/assets/css/backend/HistoricalRecord.css"></style>
