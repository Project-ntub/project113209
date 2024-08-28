<template>
  <div class="app-container">
    <Sidebar :isSidebarActive="isSidebarActive" />
    <div class="app-content" :class="{ shifted: isSidebarActive }">
      <h1 class="title">個人偏好管理</h1>
      <form @submit.prevent="updatePreferences" class="preferences-form">
        <div class="form-group">
          <label for="font-size">字體大小:</label>
          <select v-model="preferences.fontsize" id="font-size" class="form-control">
            <option value="small">小</option>
            <option value="medium">中</option>
            <option value="large">大</option>
          </select>
        </div>
        <div class="form-group">
          <label for="notification-settings">通知:</label>
          <select v-model="preferences.notificationSettings" id="notification-settings" class="form-control">
            <option :value="1">啟用</option>
            <option :value="0">不啟用</option>
          </select>
        </div>
        <div class="form-group">
          <label for="auto-login">自動登入:</label>
          <select v-model="preferences.autoLogin" id="auto-login" class="form-control">
            <option :value="1">啟用</option>
            <option :value="0">不啟用</option>
          </select>
        </div>
        <div class="form-group">
          <label for="authentication">是否驗證:</label>
          <select v-model="preferences.authentication" id="authentication" class="form-control">
            <option :value="1">已驗證</option>
            <option :value="0">未驗證</option>
          </select>
        </div>
        <div class="btn-container">
          <button type="submit" class="btn btn-save">保存更改</button>
          <button type="button" class="btn btn-cancel" @click="resetPreferences">取消更改</button>
        </div>
      </form>
  
      <div v-if="successMessage" class="success-message">保存成功！</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Sidebar from './SideBar.vue';

export default {
  name: 'PersonalPreference',
  components: {
    Sidebar
  },
  data() {
    return {
      preferences: {
        user_id: null,
        fontsize: '',
        notificationSettings: 0,
        autoLogin: 0,
        authentication: 0
      },
      successMessage: false,
      isSidebarActive: false
    };
  },
  created() {
    this.loadPreferences();
  },
  methods: {
    loadPreferences() {
      axios.get('/preferences/get_preferences/')
        .then(response => {
          this.preferences = response.data;
        })
        .catch(error => {
          console.error('Error loading preferences:', error);
        });
    },
    updatePreferences() {
      axios.post('/preferences/update_preference/', this.preferences)
        .then(response => {
          if (response.status === 200) {
            this.showSuccessMessage();
          } else {
            alert('保存失敗');
          }
        })
        .catch(error => {
          console.error('Error updating preferences:', error);
        });
    },
    resetPreferences() {
      this.loadPreferences();
    },
    showSuccessMessage() {
      this.successMessage = true;
      setTimeout(() => {
        this.successMessage = false;
      }, 3000);
    }
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.app-content {
  width: 100%;
  max-width: 600px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  color: #333;
  font-size: 24px;
  margin-bottom: 20px;
}

.preferences-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  font-size: 16px;
  color: #555;
  margin-bottom: 5px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: #fff;
  color: #333;
}

.btn-container {
  display: flex;
  justify-content: center; /* 將按鈕在容器中水平居中 */
  gap: 10px; /* 按鈕之間的間距 */
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #fff;
}

.btn-save {
  background-color: #28a745;
}

.btn-cancel {
  background-color: #6c757d;
}

.btn:hover {
  opacity: 0.9;
}

.success-message {
  color: #28a745;
  text-align: center;
  font-size: 16px;
  margin-top: 20px;
}
</style>
