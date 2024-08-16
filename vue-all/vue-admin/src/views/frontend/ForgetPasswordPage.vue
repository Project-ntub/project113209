<template>
  <div class="container">
    <h2>忘記密碼</h2>
    <form @submit.prevent="sendPasswordReset">
      <label for="email">電子郵件：</label>
      <input type="email" id="email" v-model="email" required>
      <button type="submit">發送</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ForgetPasswordPage',
  data() {
    return {
      email: '',
      csrfToken: '',
    };
  },
  methods: {
    setAxiosCsrfToken(token) {
      axios.defaults.headers.common['X-CSRFToken'] = token;
    },
    async fetchCsrfToken() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/frontend/forgot-password/', {
          withCredentials: true  // 确保包含cookies
        });
        this.csrfToken = response.data.csrfToken;
        this.setAxiosCsrfToken(this.csrfToken);
      } catch (error) {
        console.error('Failed to fetch CSRF Token:', error);
      }
    },
    async sendPasswordReset() {
      if (!this.email) {
        alert('請輸入有效的電子郵件地址');
        return;
      }

      try {
        const response = await axios.post('http://127.0.0.1:8000/frontend/forgot-password/', {
          email: this.email
        }, {
          headers: {
            'X-CSRFToken': this.csrfToken
          },
          withCredentials: true
        });

        if (response.data.success) {
          alert('已發送密碼重設請求至您的電子郵件');
          this.$router.push('/frontend/reset_password');  // 发送成功后跳转到重置密码页面
        } else {
          alert(response.data.message || '操作失敗，請稍後再試。');
        }
      } catch (error) {
        alert('操作失敗，請稍後再試。');
      }
    },
  },
  created() {
    this.fetchCsrfToken();  // 初始化时获取CSRF token
  }
};
</script>

<style scoped src="@/assets/css/frontend/ForgetPasswordPage.css"></style>
