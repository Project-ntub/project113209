<template>
  <div>
    <div class="profile-container">
      <div class="profile-card">
        <div class="profile-info">
          <h2>{{ userData.username || 'N/A' }}</h2>
          <p>{{ userData.position_id || 'N/A' }}</p>
          <p>{{ userData.department_id || 'N/A' }}</p>
          <p>{{ userData.email || 'N/A' }}</p>
          <p>{{ userData.phone || 'N/A' }}</p>
          <button class="edit-button" @click="editProfile">編輯</button>
        </div>
      </div>

      <div v-if="isEditing" class="edit-modal">
        <div class="edit-form">
          <h3>編輯個人信息</h3>
          <p>用戶名：<input type="text" v-model="editData.username" /></p>
          <p>部門：<input type="text" v-model="editData.department_id" disabled /></p>
          <p>職位：<input type="text" v-model="editData.position_id" disabled /></p>
          <p>電話：<input type="text" v-model="editData.phone" /></p>
          <p>電子郵件：<input type="email" v-model="editData.email" /></p>
          <div class="button-container">
            <button @click="saveProfile" class="save">保存</button>
            <button @click="cancelEdit" class="cancel">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      userData: {
        username: '',
        email: '',
        phone: '',
        department_id: '',
        position_id: ''
      },
      editData: {},
      isEditing: false,
    };
  },
  methods: {
    async fetchUserProfile() {
      try {
        const token = localStorage.getItem('frontend_token');  // 獲取 token
        const response = await axios.get('/api/frontend/profile/', {
          headers: {
            'Authorization': `Bearer ${token}`  // 添加 Authorization 標頭
          }
        });
        this.userData = response.data;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },

    editProfile() {
      this.editData = { ...this.userData };
      this.isEditing = true;
    },

    // 取消編輯
    cancelEdit() {
      this.isEditing = false;
    },

    // 保存用戶資料
    async saveProfile() {
      try {
        const token = localStorage.getItem('frontend_token');  // 獲取 token

        const formData = new FormData();
        formData.append('username', this.editData.username);
        formData.append('email', this.editData.email);
        formData.append('phone', this.editData.phone);

        // 更新個人資訊
        await axios.put('/api/frontend/profile/', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,  // 添加 Authorization 標頭
            'Content-Type': 'multipart/form-data'  // 設置適當的內容類型
          }
        });

        this.userData = { ...this.editData };
        this.isEditing = false;
        alert('個人資訊已更新');
      } catch (error) {
        console.error('Error saving profile:', error.response);
        alert('保存失敗');
      }
    }
  },
  mounted() {
    this.fetchUserProfile();
  }
};
</script>

<style scoped>
/* 這裡是你的樣式代碼 */
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 80vh;  
  padding-top: 0px;
  z-index: 1;  /* 保證容器不被其他元素擋住 */
}

.profile-card {
  background-color: white;
  border-radius: 10px;
  padding: 10px;
  width: 300px;
  height: 300px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-top: 50px;  /* 調整 margin，避免被頂部的 navbar 遮擋 */
}

.edit-modal {
  position: fixed;
  top: 60%; /* 確保模態框在頁面中間顯示，不被navbar擋住 */
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-height: 80vh;
  overflow-y: auto;
  z-index: 1000; /* 增加 z-index 確保模態框在最前面顯示 */
}

.button-container {
  display: flex;
  justify-content: space-between;
}

button.save {
  background-color: #4caf50;
  color: white;
}

button.cancel {
  background-color: #f44336;
  color: white;
}
</style>
