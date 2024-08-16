<template>
  <div class="container">
    <h2>重設密碼</h2>
    <form @submit.prevent="handleResetPassword">
      <label for="resetCode">重置代碼：</label>
      <input type="text" id="resetCode" v-model="resetCode" required />

      <label for="newPassword">新密碼：</label>
      <div class="password-container">
        <input type="password" id="newPassword" v-model="newPassword" required />
        <span class="toggle-password" @click="handleTogglePassword">👁️</span>
      </div>

      <label for="confirmPassword">確認新密碼：</label>
      <div class="password-container">
        <input type="password" id="confirmPassword" v-model="confirmPassword" required />
        <span class="toggle-password" @click="handleTogglePassword">👁️</span>
      </div>

      <button type="submit">重設密碼</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ResetPasswordPage',
  data() {
    return {
      resetCode: '',  // 添加重置代码的输入框
      newPassword: '',
      confirmPassword: '',
      csrfToken: '',
    };
  },
  methods: {
    setAxiosCsrfToken(token) {
      axios.defaults.headers.common['X-CSRFToken'] = token;
    },
    async fetchCsrfToken() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/frontend/reset-password/', {
          withCredentials: true  // 确保包含cookies
        });
        this.csrfToken = response.data.csrfToken;
        this.setAxiosCsrfToken(this.csrfToken);
      } catch (error) {
        console.error('Failed to fetch CSRF Token:', error);
      }
    },
    async handleResetPassword() {
      if (this.newPassword !== this.confirmPassword) {
        alert('新密碼和確認新密碼不匹配');
        return;
      }
   
      try {
        const response = await axios.post('http://127.0.0.1:8000/frontend/reset-password/', {
          resetCode: this.resetCode,  // 发送重置代码到后端
          newPassword: this.newPassword
        }, {
          headers: {
            'X-CSRFToken': this.csrfToken
          },
          withCredentials: true
        });

        if (response.data.success) {
          alert('密碼重置成功！');
          this.$router.push('/login');  // 密码重置成功后跳转到登录页面
        } else {
          alert(response.data.message || '重置失敗，請稍後再試。');
        }
      } catch (error) {
        alert('重置失敗，請稍後再試。');
      }
    },
    handleTogglePassword(event) {
      const passwordInput = event.target.previousElementSibling;
      passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    }
  },
  created() {
    this.fetchCsrfToken();  // 初始化时获取CSRF token
  }
};
</script>

<style scoped src="@/assets/css/frontend/ResetPasswordPage.css"></style>
