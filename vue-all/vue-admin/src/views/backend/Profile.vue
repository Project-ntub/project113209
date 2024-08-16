<template>
  <div class="profile-content" :class="{ shifted: isSidebarActive }">
    <div class="profile-container">
      <h2>個人資料</h2>
      <label for="name">姓名：</label>
      <input type="text" id="name" v-model="profile.name">
      
      <label for="username">帳號：</label>
      <input type="text" id="username" v-model="profile.username">
      
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
        <input type="text" id="modal-username" v-model="editProfile.username">
        
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
</template>

<script>
export default {
  name: 'PensonalProfile',
  data() {
    return {
      profile: {
        name: 'John Doe',
        username: 'johndoe123',
        department: '技術部',
        position: '系統管理員',
        phone: '0912345678',
        email: 'johndoe@example.com',
        created: '2023-01-01'
      },
      editProfile: {
        name: 'John Doe',
        username: 'johndoe123',
        department: '技術部',
        position: '系統管理員',
        phone: '0912345678',
        email: 'johndoe@example.com'
      },
      showModal: false,
      isSidebarActive: false
    };
  },
  methods: {
    openModal() {
      this.editProfile = { ...this.profile };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    saveProfile() {
      this.profile = { ...this.editProfile };
      this.closeModal();
      alert('個人資料已更新');
    },
    logout() {
      window.location.href = '登出成功.html';
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Profile.css"></style>
