<template>
  <div class="app-container">
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
          <label for="authentication">是否驗證:</label>
          <select v-model="preferences.authentication" id="authentication" class="form-control">
            <option :value="1">已驗證</option>
            <option :value="0">未驗證</option>
          </select>
        </div>
        <div class="btn-container">
          <button type="submit" class="btn btn-save">保存更改</button>
        </div>
      </form>

      <div v-if="successMessage" class="success-message">保存成功！</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PreferenceSetting',
  data() {
    return {
      preferences: {
        fontsize: 'medium',
        notificationSettings: false,
        authentication: false
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
      axios.get('/frontend/user_preferences/')
        .then(response => {
          this.preferences = { ...this.preferences, ...response.data };
        })
        .catch(error => {
          console.error('載入偏好時出錯:', error);
        });
    },
    updatePreferences() {
      axios.put('/frontend/user_preferences/', this.preferences)
        .then(response => {
          if (response.data) {
            this.showSuccessMessage();
          } else {
            alert('保存失敗');
          }
        })
        .catch(error => {
          console.error('更新偏好時出錯:', error);
        });
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
/* Add custom styles here */
</style>
