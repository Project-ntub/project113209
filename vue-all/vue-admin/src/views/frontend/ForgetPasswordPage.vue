<template>
  <div class="container">
    <h2 v-if="step === 1">忘記密碼</h2>
    <h2 v-if="step === 2">重設密碼</h2>

    <form v-if="step === 1" @submit.prevent="sendPasswordReset">
      <label for="email">電子郵件：</label>
      <input type="email" id="email" v-model="email" required>
      <button type="submit">發送驗證碼</button>
    </form>

    <form v-if="step === 2" @submit.prevent="handleResetPassword">
      <div class="input-container">
        <label for="resetCode">重置代碼：</label>
        <input type="text" id="resetCode" v-model="resetCode" required />
      </div>

      <div class="input-container">
        <label for="newPassword">新密碼：</label>
        <div class="password-container">
          <input type="password" id="newPassword" v-model="newPassword" required />
          <span class="toggle-password" @click="handleTogglePassword">👁️</span>
        </div>
        <p v-if="passwordError" class="error">{{ passwordError }}</p>
      </div>

      <div class="input-container">
        <label for="confirmPassword">確認新密碼：</label>
        <div class="password-container">
          <input type="password" id="confirmPassword" v-model="confirmPassword" required />
          <span class="toggle-password" @click="handleTogglePassword">👁️</span>
        </div>
        <p v-if="confirmPasswordError" class="error">{{ confirmPasswordError }}</p>
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
      step: 1, // 1: 忘記密碼, 2: 重設密碼
      email: '',
      resetCode: '',
      newPassword: '',
      confirmPassword: '',
      csrfToken: '',
      passwordError: '',
      confirmPasswordError: ''
    };
  },
  methods: {
    setAxiosCsrfToken(token) {
      axios.defaults.headers.common['X-CSRFToken'] = token;
    },
    async fetchCsrfToken() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/frontend/reset-password/', {
          withCredentials: true
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
          alert('已發送驗證碼至您的電子郵件');
          this.step = 2; // 切換到重設密碼步驟
        } else {
          alert(response.data.message || '操作失敗，請稍後再試。');
        }
      } catch (error) {
        alert('操作失敗，請稍後再試。');
      }
    },
    validatePasswordStrength(password) {
      const minLength = 8;
      const hasUpperCase = /[A-Z]/.test(password);
      const hasLowerCase = /[a-z]/.test(password);
      const hasNumbers = /\d/.test(password);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

      return password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar;
    },
    async handleResetPassword() {
      this.passwordError = '';
      this.confirmPasswordError = '';

      if (!this.validatePasswordStrength(this.newPassword)) {
        this.passwordError = '密碼必須至少包含8個字符，且包括大小寫字母、數字和特殊字符';
        return;
      }

      if (this.newPassword !== this.confirmPassword) {
        this.confirmPasswordError = '新密碼和確認新密碼不匹配';
        return;
      }

      try {
        const response = await axios.post('http://127.0.0.1:8000/frontend/reset-password/', {
          resetCode: this.resetCode,
          newPassword: this.newPassword
        }, {
          headers: {
            'X-CSRFToken': this.csrfToken
          },
          withCredentials: true
        });

        if (response.data.success) {
          alert('密碼重置成功！');
          this.$router.push('/frontend/login');
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
    this.fetchCsrfToken();
  }
};
</script>
<style  src="@/assets/css/frontend/ForgetPasswordPage.css"></style>