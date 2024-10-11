<template>
  <div class="content" id="content">
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
              <input :type="passwordVisible ? 'text' : 'password'" id="password" v-model="password" required />
              <i :class="passwordVisible ? 'fas fa-eye-slash' : 'fas fa-eye'" 
                 class="toggle-password"
                 @click="togglePasswordVisibility">
              </i>
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
          <div v-if="error" class="error">{{ error }}</div>
        </form>
        <p>還未擁有帳號？ <router-link to="/frontend/register">註冊</router-link></p>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      error: '',
      passwordVisible: false // 新增 passwordVisible 變數
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('/api/token/', {
          email: this.email,
          password: this.password,
          remember_me: this.rememberMe
        });

        if (response.data && response.data.access) {
          localStorage.setItem('frontend_token', response.data.access);
          this.$router.push('/frontend/home');
        } else {
          this.error = '登入失敗，無法取得 Token';
        }
      } catch (error) {
        this.error = error.response?.data?.detail || '登入失敗，請檢查您的使用者名稱和密碼';
      }
    },
    togglePasswordVisibility() {
      this.passwordVisible = !this.passwordVisible;
    }
  }
};
</script>


<style src="@/assets/css/frontend/LoginPage.css"></style>
