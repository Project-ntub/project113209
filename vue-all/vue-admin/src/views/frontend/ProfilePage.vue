<template>
  <div>
    <div class="content" :class="{ shift: isSidebarOpen }" id="content">
      <div class="info-container">
        <h3>個人資訊</h3>
        <div v-if="!isEditing">
          <!-- <p>姓名：<span>{{ userData.username || 'N/A' }}</span></p> -->
          <p>帳號：<span>{{ userData.username || 'N/A' }}</span></p>
          <p>部門：<span>{{ userData.department_name || 'N/A' }}</span></p>
          <p>職位：<span>{{ userData.position_name || 'N/A' }}</span></p>
          <p>電話：<span>{{ userData.phone || 'N/A' }}</span></p>
          <p>電子郵件：<span>{{ userData.email || 'N/A'  }}</span></p>
          <div class="button-container">
            <button class="edit" @click="editProfile">編輯</button>
          </div>
        </div>
        <div v-else>
          <!-- <p>姓名：<input type="text" v-model="editData.username"></p> -->
          <p>帳號：<input type="text" v-model="editData.username"></p>
          <p>部門：<input type="text" v-model="editData.department_id"></p>
          <p>職位：<input type="text" v-model="editData.position_id"></p>
          <p>電話：<input type="text" v-model="editData.phone"></p>
          <p>電子郵件：<input type="email" v-model="editData.email"></p>
          <div class="button-container">
            <button class="save" @click="saveProfile">保存</button>
            <button class="cancel" @click="cancelEdit">取消</button>
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
        department_name: '',
        position_name: '',
      },
      editData: {},
      isSidebarOpen: false,
      isEditing: false
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
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
      } catch (error) {
        console.error('Error saving profile:', error);
        alert('保存失敗');
      }
    }
  },
  mounted() {
    this.fetchUserProfile(); // 在組件加載時獲取用戶信息
  }
};
</script>

<style scoped src="@/assets/css/frontend/ProfilePage.css"></style>
