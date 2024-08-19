<template>
  <div class="container">
    <h2>重設密碼</h2>
    <form @submit.prevent="handleResetPassword">
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

<style scoped>
.container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.input-container {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

.password-container {
  position: relative;
}

.toggle-password {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  cursor: pointer;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.error {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}
</style>
