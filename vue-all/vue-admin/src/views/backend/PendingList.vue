<template>
  <TopNavbar title="待審核名單" />
  <div class="container">
    <div class="back-button-container">
      <a href="/backend/user-management" class="back-button">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        回到用戶管理
      </a>
    </div>
    <table class="pending-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>電子郵件</th>
          <th>電話號碼</th>
          <th>申請時間</th>
          <th>審核</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in pendingUsers" :key="user.id">
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.phone }}</td>
          <td>{{ user.date_joined ? user.date_joined : '未知' }}</td>
          <td>
            <form @submit.prevent="approveUser(user.id)">
              <button type="submit" class="approve-btn">開通</button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue'; // 引入前台的TopNavbar组件
import axios from '@/axios';

export default {
  name: 'PendingList',
  components: {
    TopNavbar
  },
  data() {
    return {
      pendingUsers: [],
      isLoading: false // 添加一個加載狀態
    };
  },
  methods: {
    async fetchPendingUsers() {
      try {
        const response = await axios.get('/api/backend/pending-users/');
        this.pendingUsers = response.data;
      } catch (error) {
        console.error('Error fetching pending users:', error);
      }
    },
    async approveUser(userId) {
      if (this.isLoading) return; // 防止重複點擊
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/backend/approve-user/${userId}/`);
        if (response.data.success) {
          alert('用戶已成功開通');
          this.fetchPendingUsers(); // 重新加載待審核用戶列表
        } else {
          alert('開通失敗，請稍後再試');
        }
      } catch (error) {
        console.error('審批用戶時出錯：', error);
        alert('開通失敗，請稍後再試');
      } finally {
        this.isLoading = false; // 操作完成後取消加載狀態
      }
    }
  },
  mounted() {
    this.fetchPendingUsers();
  }
};
</script>

<style scoped>
  body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

.container {
    width: 100%; /* 設置更大的寬度 */
    height: calc(100vh - 60px);
    max-width: 1200px; 
    margin: 20px auto;
    padding: 0;
    background-color: #ffffff;
    box-shadow: none;
    border-radius: 0;
    overflow-x: auto;
    /* box-sizing: border-box; */
    position: relative;
}

.back-button-container {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 1000;
}

.back-button {
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #007bff;
    text-decoration: none;
    font-size: 16px;
}
  
.pending-table {
    width: 50%;
    border-collapse: collapse;
    margin-top: 40px;
}

.pending-table th, .pending-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

.pending-table th {
    background-color: #4A90E2;
    color: #ffffff;
    font-weight: bold;
}

.pending-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.pending-table tr:hover {
    background-color: #ddd;
}

.approve-btn {
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    align-items: center;
}

.approve-btn:hover {
    background-color: #0056b3;
}

.back-button:hover {
    color: #0056b3;
}

.back-button svg {
    margin-right: 8px;
}

/* 響應式設計 */
@media (max-width: 1024px) {
    .container {
        width: 95%;
        padding: 15px;
    }

    .pending-table th, .pending-table td {
        padding: 6px;
    }
}

@media (max-width: 768px) {
    .container {
        width: 100%;
        padding: 10px;
    }

    .pending-table th, .pending-table td {
        padding: 4px;
    }

    .approve-btn {
        padding: 8px;
    }

    .back-button {
        margin-bottom: 10px;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 5px;
    }

    .pending-table {
        font-size: 14px;
    }

    .approve-btn {
        width: 100%;
        padding: 10px;
        text-align: center;
    }
}

</style>
