<template>
  <div>
    <button class="hamburger-menu" @click="toggleMenu">
      <div></div>
      <div></div>
      <div></div>
    </button>

    <div class="content" id="content">
      <div class="container">
        <div class="preferences">
          <div class="header">偏好設定</div>
          <div class="form-group">
            <label for="font-size">字體大小</label>
            <select id="font-size" v-model="fontSize">
              <option value="large">大</option>
              <option value="medium">適中</option>
              <option value="small">小</option>
            </select>
          </div>
          <div class="form-group">
            <label for="notification">通知設定</label>
            <select id="notification" v-model="notification">
              <option value="true">開啟通知</option>
              <option value="false">關閉通知</option>
            </select>
          </div>
          <div class="form-group">
            <label for="auto-login">自動登入</label>
            <select id="auto-login" v-model="autoLogin">
              <option value="true">自動登入</option>
              <option value="false">取消自動登入</option>
            </select>
          </div>
          <div class="form-group">
            <label for="authentication">認證設定</label>
            <select id="authentication" v-model="authentication">
              <option value="true">開啟認證</option>
              <option value="false">關閉認證</option>
            </select>
          </div>
          <div class="buttons">
            <button class="cancel-button" @click="cancelChanges">取消變更</button>
            <button class="submit-button" @click="submitChanges">更改</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PreferenceSetting',
  data() {
    return {
      fontSize: 'medium',
      notification: 'false',
      autoLogin: 'false',
      authentication: 'false',
    };
  },
  methods: {
    async fetchPreferences() {
      try {
        const response = await axios.get('/frontend/preferences/');
        const preferences = response.data;
        this.fontSize = preferences.fontSize || 'medium';
        this.notification = preferences.notification ? 'true' : 'false';
        this.autoLogin = preferences.autoLogin ? 'true' : 'false';
        this.authentication = preferences.authentication ? 'true' : 'false';
      } catch (error) {
        console.error('無法獲取偏好設置:', error);
      }
    },
    async submitChanges() {
      try {
        const response = await axios.post('/frontend/preferences/', {
          fontSize: this.fontSize,
          notification: this.notification === 'true',
          autoLogin: this.autoLogin === 'true',
          authentication: this.authentication === 'true',
        });
        if (response.data.success) {
          alert('偏好設定已更改');
        }
      } catch (error) {
        console.error('無法更新偏好設置:', error);
      }
    },
    cancelChanges() {
      this.fetchPreferences(); // 重新從服務器加載當前偏好設定
    },
    toggleMenu() {
      const dropdownContent = document.querySelector('.dropdown-content');
      dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    },
  },
  mounted() {
    this.fetchPreferences(); // 在組件加載時獲取當前偏好設定
  },
};
</script>

<style scoped src="@/assets/css/frontend/PreferenceSetting.css"></style>
