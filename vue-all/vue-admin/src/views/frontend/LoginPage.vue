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
      loginFeedback: '',
      error: '' // 新增 error 變量
    };
  },
  methods: {
    async handleLogin() {  // 確保使用與模板中相同的名稱
      try {
        const csrfToken = getCookie('csrftoken');
        const response = await axios.post('/api/token/', {
          email: this.email,
          password: this.password,
          remember_me: this.rememberMe
        }, {
          headers: {
            'X-CSRFToken': csrfToken
          }
        });
        console.log('登入成功', response);
        this.user = response.data.user; 
        localStorage.setItem('token', response.data.access); // 確保令牌被存儲
        this.$router.push('/frontend/home');
      } catch (error) {
        console.error('登入失败', error.response);
        if (error.response && error.response.data) {
          this.error = error.response.data.detail || '登入失敗，請檢查您的使用者名稱和密碼';
        } else {
          this.error = '登入失敗，請稍後再試';
        }
      }
    },
    togglePasswordVisibility(inputId) {
      const passwordInput = document.getElementById(inputId);
      passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    }
  }
};

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
</script>

<style scoped src="@/assets/css/frontend/LoginPage.css"></style>
