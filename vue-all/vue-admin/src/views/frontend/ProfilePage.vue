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
        position_id: '',
      },
      editData: {},
      isEditing: false
    };
  },
  methods: {
    async fetchUserProfile() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.userData = response.data;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },
    editProfile() {
      this.editData = { ...this.userData };
      this.isEditing = true;
    },
    cancelEdit() {
      this.isEditing = false;
    },
    async saveProfile() {
      try {
        await axios.put('/api/frontend/profile/', this.editData);
        this.userData = { ...this.editData };
        this.isEditing = false;
        alert('個人信息已更新');
        await this.recordHistory({
          action: '更新個人資訊',
          operation_result: 1  
        });
      } catch (error) {
        console.error('Error saving profile:', error);
        alert('保存失敗');
      }
    },
    async recordHistory(historyData) {
      try {
        await axios.post('/api/frontend/history/', historyData);
        console.log('歷史紀錄成功');
      } catch (error) {
        console.error('歷史紀錄失敗:', error);
      }
    }
  },
  mounted() {
    this.fetchUserProfile();
  }
};
</script>

<style src="@/assets/css/frontend/ProfilePage.css"></style>
