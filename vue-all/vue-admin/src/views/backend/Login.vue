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
      <div class="form-group checkbox-group">
        <input type="checkbox" id="remember_me" v-model="rememberMe" />
        <label for="remember_me">記住我</label>
      </div>
      <button type="submit" class="btn-login">登入</button>
    </form>
    <p>
      還未擁有帳號? <router-link to="/frontend/register">註冊</router-link>
    </p>
    <p>
      忘記密碼? <router-link to="/backend/forgetpassword">重置密碼</router-link> <!-- 修改的地方 -->
    </p>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from '@/axios'; // 使用配置好的 axios 实例

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
    async login() {
      try {
        const response = await axios.post('/api/token/', {
          email: this.email,
          password: this.password,
          remember_me: this.rememberMe
        });
        console.log('登入成功', response);
        localStorage.setItem('backend_token', response.data.access); // 儲存後台 token
        
        // 登入成功後，記錄歷史紀錄
        await this.recordLoginHistory();

        this.$router.push('/backend/management'); // 跳轉至後台管理頁面
      } catch (error) {
        console.error('登入失敗', error.response);
        if (error.response && error.response.data) {
          this.error = error.response.data.detail || '登入失敗，請檢查您的使用者名稱和密碼';
        } else {
          this.error = '登入失敗，請稍後再試';
        }
      }
    },

    // 方法用於記錄登入的歷史紀錄
    async recordLoginHistory() {
      try {
        const response = await axios.post('/backend/record-login-history/', {
          action: '登入成功',
        });
        console.log('歷史紀錄已保存', response);
      } catch (error) {
        console.error('無法保存歷史紀錄', error.response);
      }
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/login.css"></style>
