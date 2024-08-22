<template>
  <div class="change-password-container">
    <h2>修改密碼</h2>
    <div v-if="username">歡迎, {{ username }}</div>
    <form @submit.prevent="handleChangePassword">
      <div class="input-group">
        <label for="currentPassword">原密碼</label>
        <input type="password" id="currentPassword" v-model="currentPassword" required />
      </div>
      <div class="input-group">
        <label for="newPassword">新密碼</label>
        <input type="password" id="newPassword" v-model="newPassword" required />
      </div>
      <div class="input-group">
        <label for="confirmNewPassword">確認新密碼</label>
        <input type="password" id="confirmNewPassword" v-model="confirmNewPassword" required />
      </div>
      <button type="submit" class="submit-button">更改密碼</button>
      <button type="button" class="cancel-button" @click="cancelChanges">取消變更</button>
      <div id="feedback" class="feedback" v-if="feedbackMessage">{{ feedbackMessage }}</div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
      feedbackMessage: '',  // 用於存儲反饋信息
      username: '',  // 用於顯示用戶名
    };
  },
  methods: {
    async handleChangePassword() {
      this.feedbackMessage = '';  // 重置反饋信息
      if (this.newPassword !== this.confirmNewPassword) {
        this.feedbackMessage = '新密碼與確認密碼不匹配';
        console.log('新密碼與確認密碼不匹配'); // 調試信息
        return;
      }

      try {
        console.log('正在發送請求...'); // 調試信息
        const response = await axios.post('/frontend/change_password/', {
          currentPassword: this.currentPassword,
          newPassword: this.newPassword
        }, {
          headers: {
            'X-CSRFToken': this.$cookies.get('csrftoken')  // 傳遞 CSRF Token
          }
        });

        console.log('請求成功，回應：', response.data); // 調試信息

        if (response.data.success) {
          this.feedbackMessage = '密碼已成功修改';
          console.log('密碼已成功修改'); // 調試信息
          this.username = response.data.username;  // 獲取和顯示用戶名
          // 清空表單
          this.currentPassword = '';
          this.newPassword = '';
          this.confirmNewPassword = '';
        } else {
          this.feedbackMessage = response.data.message || '發生未知錯誤';
          console.log('錯誤訊息：', response.data.message); // 調試信息
        }
      } catch (error) {
        console.log('請求失敗', error); // 調試信息
        if (error.response && error.response.data && error.response.data.message) {
          this.feedbackMessage = error.response.data.message;
        } else if (error.message) {
          this.feedbackMessage = error.message;
        } else {
          this.feedbackMessage = '密碼修改失敗，請稍後再試';
        }
      }
    },
    cancelChanges() {
      this.feedbackMessage = '您取消了變更密碼';
      console.log('取消了變更密碼'); // 調試信息
      // 可選：清空表單字段
      this.currentPassword = '';
      this.newPassword = '';
      this.confirmNewPassword = '';
    }
  },
  mounted() {
    // 在頁面加載後，您可能需要從後端取得用戶資訊並更新 `username`
    axios.get('/frontend/profile/')
      .then(response => {
        this.username = response.data.username;
      })
      .catch(error => {
        console.error('無法取得用戶資訊', error);
      });
  }
};
</script>

<style scoped>
.change-password-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
}
.input-group {
  margin-bottom: 1em;
}
.submit-button, .cancel-button {
  display: inline-block;
  margin-right: 10px;
}
.feedback {
  margin-top: 1em;
  color: red;
  font-size: 16px;
}
</style>
