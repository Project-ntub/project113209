<template>
  <div class="app-container">
    <Sidebar :isSidebarActive="isSidebarActive" />
    <div class="profile-content" :class="{ shifted: isSidebarActive }">
      <div class="profile-container">
        <h2>個人資料</h2>
        <label for="name">姓名：</label>
        <input type="text" id="name" v-model="profile.name">
        
        <label for="username">帳號：</label>
        <input type="text" id="username" v-model="profile.username" disabled>
        
        <label for="department">部門：</label>
        <input type="text" id="department" v-model="profile.department">
        
        <label for="position">職位：</label>
        <input type="text" id="position" v-model="profile.position">
        
        <label for="phone">電話：</label>
        <input type="text" id="phone" v-model="profile.phone">
        
        <label for="email">電子郵件：</label>
        <input type="text" id="email" v-model="profile.email">
        
        <label for="created">建立時間：</label>
        <input type="text" id="created" v-model="profile.created" disabled>
    
        <button @click="openModal">編輯</button>
        <button class="logout-btn" @click="logout">登出</button>
      </div>
    
      <div id="editModal" class="modal" v-if="showModal">
        <div class="modal-content">
          <span class="close" @click="closeModal">&times;</span>
          <h2>編輯個人資料</h2>
          <label for="modal-name">姓名：</label>
          <input type="text" id="modal-name" v-model="editProfile.name">
          
          <label for="modal-username">帳號：</label>
          <input type="text" id="modal-username" v-model="editProfile.username" disabled>
          
          <label for="modal-department">部門：</label>
          <input type="text" id="modal-department" v-model="editProfile.department">
          
          <label for="modal-position">職位：</label>
          <input type="text" id="modal-position" v-model="editProfile.position">
          
          <label for="modal-phone">電話：</label>
          <input type="text" id="modal-phone" v-model="editProfile.phone">
          
          <label for="modal-email">電子郵件：</label>
          <input type="text" id="modal-email" v-model="editProfile.email">
    
          <button @click="saveProfile">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Sidebar from './SideBar.vue';

export default {
  name: 'PensonalProfile',
  components: {
    Sidebar
  },
  data() {
    return {
      profile: {
        name: '',
        username: '',
        department: '',
        position: '',
        phone: '',
        email: '',
        created: ''
      },
      editProfile: {
        name: '',
        username: '',
        department: '',
        position: '',
        phone: '',
        email: ''
      },
      showModal: false,
      isSidebarActive: false
    };
  },
  created() {
    this.getProfile();
  },
  methods: {
    getProfile() {
      axios.get('/backend/api/profile/')
        .then(response => {
          this.profile = response.data;
        })
        .catch(error => {
          console.error('無法取得個人資料:', error);
        });
    },
    openModal() {
      this.editProfile = { ...this.profile };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    saveProfile() {
      axios.post('/backend/api/profile/', this.editProfile)
        .then(() => {  // 移除未使用的 response 變數
          this.profile = { ...this.editProfile };
          this.closeModal();
          alert('個人資料已更新');
        })
        .catch(error => {
          console.error('無法更新個人資料:', error);
        });
    },
    logout() {
      axios.post('/backend/api/logout/')
        .then(() => {
          window.location.href = '/frontend/login/';
        })
        .catch(error => {
          console.error('無法登出:', error);
        });
    }
  }
};
</script>

<style scoped src="../assets/css/Profile.css"></style>
