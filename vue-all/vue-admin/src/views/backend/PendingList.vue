<template>
  <TopNavbar title="待審核名單" />
  <div class="container">
    <a href="/backend/user-management" class="back-button">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      回到用戶管理
    </a>
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

<style scoped src="@/assets/css/backend/PendingList.css"></style>
