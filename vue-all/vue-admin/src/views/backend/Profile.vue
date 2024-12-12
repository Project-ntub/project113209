<template>
  <TopNavbar title="個人資料" />
  <div>
    <div class="profile-container">
      <div class="profile-row">
        <!-- <div v-if="!showModal">
          <label for="name">姓名：</label>
          <input type="text" id="name" v-model="profile.name" disabled>
        </div> -->
        <!-- <div v-else>
          <label for="modal-name">姓名：</label>
          <input type="text" id="modal-name" v-model="editProfile.name">
        </div> -->

        <div v-if="!showModal">
          <label for="username">帳號：</label>
          <input type="text" id="username" v-model="profile.username" disabled>
        </div>
        <div v-else>
          <label for="modal-username">帳號：</label>
          <input type="text" id="modal-username" v-model="editProfile.username" disabled>
        </div>

        <div v-if="!showModal">
          <label for="department">部門：</label>
          <input type="text" id="department" v-model="profile.department" disabled>
        </div>
        <div v-else>
          <label for="modal-department">部門：</label>
          <input type="text" id="modal-department" v-model="editProfile.department">
        </div>

        <div v-if="!showModal">
          <label for="position">職位：</label>
          <input type="text" id="position" v-model="profile.position" disabled>
        </div>
        <div v-else>
          <label for="modal-position">職位：</label>
          <input type="text" id="modal-position" v-model="editProfile.position">
        </div>

        <div v-if="!showModal">
          <label for="phone">電話：</label>
          <input type="text" id="phone" v-model="profile.phone" disabled>
        </div>
        <div v-else>
          <label for="modal-phone">電話：</label>
          <input type="text" id="modal-phone" v-model="editProfile.phone">
        </div>

        <div v-if="!showModal">
          <label for="email">電子郵件：</label>
          <input type="text" id="email" v-model="profile.email" disabled>
        </div>
        <div v-else>
          <label for="modal-email">電子郵件：</label>
          <input type="text" id="modal-email" v-model="editProfile.email">
        </div>

        <div v-if="!showModal">
          <label for="created">建立時間：</label>
          <input type="text" id="created" v-model="profile.created" disabled>
        </div>
      </div>
      <div class="profile-buttons">
        <button v-if="!showModal" @click="openModal">編輯</button>
        <button v-else @click="saveProfile">保存</button>
        <button v-if="showModal" class="cancel-btn" @click="cancelEdit">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue'; // 引入前台的TopNavbar组件
import axios from 'axios';

export default {
  name: 'PersonalProfile',
  components: {
    TopNavbar
  },
  data() {
    return {
      profile: {
        // name: '',
        username: '',
        department: '',
        position: '',
        phone: '',
        email: '',
        created: ''
      },
      editProfile: {
        // name: '',
        username: '',
        department: '',
        position: '',
        phone: '',
        email: ''
      },
      showModal: false
    };
  },
  created() {
    this.getProfile();
  },
  methods: {
    getProfile() {
      axios.get('/api/backend/profile/')
        .then(response => {
          this.profile = response.data;
          this.profile.department = response.data.department_id;
          this.profile.position = response.data.position_id;
          this.profile.created = response.data.date_joined;
        })
        .catch(error => {
          console.error('無法取得個人資料:', error);
        });
    },
    openModal() {
      this.editProfile = { ...this.profile }; // 保存当前的profile状态
      this.showModal = true;
    },
    cancelEdit() {
      this.showModal = false;
    },
    saveProfile() {
      axios.post('/api/backend/profile/', this.editProfile)
        .then(() => {  
          this.profile = { ...this.editProfile };
          this.showModal = false;
          alert('個人資料已更新');
        })
        .catch(error => {
          console.error('無法更新個人資料:', error);
        });
    },
    logout() {
      axios.post('/api/backend/logout/')
        .then(() => {
          window.location.href = '/backend/login/';
        })
        .catch(error => {
          console.error('無法登出:', error);
        });
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Profile.css"></style>
