<template>
  <div class="login-container">
    <div class="login-form">
      <h2>用戶登入</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="email">電子郵件</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="input-group">
          <label for="password">密碼</label>
          <div class="input-container">
            <input type="password" id="password" v-model="password" required />
            <i class="fas fa-eye toggle-password" @click="togglePasswordVisibility('password')"></i>
          </div>
        </div>
        <div class="additional-options">
          <label>
            <input type="checkbox" id="rememberMe" v-model="rememberMe" />
            記住我
          </label>
          <router-link to="/frontend/forgot_password">忘記密碼?</router-link>
        </div>
        <input type="submit" value="登入" class="submit-button" />
        <div id="login-feedback" class="feedback">{{ loginFeedback }}</div>
      </form>
      <p>還未擁有帳號？ <router-link to="/frontend/register">註冊</router-link></p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'; // 直接从 axios 库中导入 axios

export default {
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      loginFeedback: ''
    };
  },
  methods: {
    async handleLogin() {
      try {
        // POST 請求到 Django 後端的 /api/token/ 端點
        const response = await axios.post('http://127.0.0.1:8000/api/token/', {
          email: this.email,
          password: this.password
        });
        
        if (response.status === 200) {
          // 保存 token 到 localStorage 或 sessionStorage
          localStorage.setItem('token', response.data.access);
          if (this.rememberMe) {
            localStorage.setItem('refreshToken', response.data.refresh);
          } else {
            sessionStorage.setItem('refreshToken', response.data.refresh);
          }
          this.loginFeedback = '登入成功';
          this.$router.push('/frontend/home'); // 成功登錄後重定向到首頁
        }
      } catch (error) {
        if (error.response && error.response.data) {
          this.loginFeedback = error.response.data.detail || '登入失敗，請檢查您的電子郵件和密碼';
        } else {
          this.loginFeedback = '登入失敗，請稍後再試';
        }
      }
    },
    togglePasswordVisibility(inputId) {
      const passwordInput = document.getElementById(inputId);
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
      } else {
        passwordInput.type = 'password';
      }
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/LoginPage.css"></style>
