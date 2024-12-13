<template>
  <div class="container">
    <h2>登入</h2>
    <form @submit.prevent="login">
      <input type="hidden" name="next" value="/backend/management" />
      <div class="form-group">
        <label for="email">帳號:</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">密碼:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div class="additional-options">
        <label class="switch">
          <input type="checkbox" id="rememberMe" v-model="rememberMe" />
          <span class="slider round"></span>
        </label>
        <span>記住我</span>
      </div>
      <button type="submit" class="btn-login">登入</button>
    </form>
    <p>
      還未擁有帳號? <router-link to="/backend/register">註冊</router-link>
    </p>
    <p>
      忘記密碼? <router-link to="/backend/forgetpassword">重置密碼</router-link>
    </p>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import axios from '@/axios';
import { mapActions } from 'vuex';

export default {
  name: 'AppLogin',
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      error: ''
    };
  },
  methods: {
    ...mapActions(['setBackendToken', 'fetchPermissions', 'fetchPreference']),
    async login() {
      try {
        const response = await axios.post('/api/token/', {
          email: this.email,
          password: this.password,
          remember_me: this.rememberMe,
          user_type: 'backend' // 明確指定 user_type 為 backend
        });

        // 確保 response 和 response.data 存在
        if (response?.data) {
          console.log('登入成功', response);

          // 儲存 backend_token
          localStorage.setItem('backend_token', response.data.access);
          if (this.rememberMe) {
            localStorage.setItem('refresh_token', response.data.refresh);
          } else {
            sessionStorage.setItem('refresh_token', response.data.refresh);
          }

          // 更新 Vuex store
          this.setBackendToken(response.data.access);
          await this.fetchPermissions();
          await this.fetchPreference();
          this.$router.push('/backend/management');
        } else {
          // 回應結構無效
          console.error('API 回應格式錯誤', response);
          this.error = '無法處理後端回應，請稍後再試';
        }
      } catch (error) {
        // 處理錯誤情況
        console.error('登入失敗', error);
        this.error =
          error?.response?.data?.detail ||
          '登入失敗，請檢查您的使用者名稱和密碼';
      }
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/login.css"></style>
