<template>
  <div class="register-page-wrapper">
    <div class="register-container">
      <h2>註冊</h2>
      <form @submit.prevent="handleSubmit" class="register-form">
        <div class="input-group">
          <label for="username">用戶名</label>
          <input type="text" id="username" v-model="username" required />
        </div>

        <div class="input-group">
          <label for="email">電子郵件</label>
          <input type="email" id="email" v-model="email" required />
        </div>

        <button type="button" class="get-code-button" @click="getVerificationCode">獲取驗證碼</button>
        <div id="verification-feedback" :class="{'feedback': true, 'success': feedbackSuccess, 'error': !feedbackSuccess}">
          {{ verificationFeedback }}
        </div>

        <div class="input-group">
          <label for="verification_code">驗證碼</label>
          <input type="text" id="verification_code" v-model="verificationCode" required />
        </div>

        <div class="input-group">
          <label for="password">密碼</label>
          <div class="password-container">
            <input type="password" id="password" v-model="password" required />
            <span class="toggle-password" @click="handleTogglePassword">👁️</span>
          </div>
          <div class="password-example">密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。例如：Password@123</div>
        </div>

        <div class="input-group">
          <label for="confirm_password">確認密碼</label>
          <div class="password-container">
            <input type="password" id="confirm_password" v-model="confirmPassword" required />
            <span class="toggle-password" @click="handleTogglePassword">👁️</span>
          </div>
        </div>

        <div class="input-group">
          <label for="phone">電話號碼</label>
          <input type="text" id="phone" v-model="phone" required />
        </div>

        <input type="submit" value="註冊" class="submit-button"/>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import '@/assets/css/frontend/RegisterPage.css'; // 引入分離的CSS文件

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      phone: '',
      verificationCode: '',
      verificationFeedback: '',
      feedbackSuccess: false,
      csrfToken: ''  
    };
  },
  methods: {
    setAxiosCsrfToken(token) {
      axios.defaults.headers.common['X-CSRFToken'] = token;
    },
    async fetchCsrfToken() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/frontend/register/', {
          withCredentials: true  // 確保包含cookies
        });
        this.csrfToken = response.data.csrfToken;
        this.setAxiosCsrfToken(this.csrfToken);
      } catch (error) {
        console.error('Failed to fetch CSRF Token:', error);
      }
    },
    async getVerificationCode() {
      if (!this.validateEmail(this.email)) {
        alert('請輸入有效的電子郵件地址。');
        return;
      }

      try {
        const response = await axios.post('http://127.0.0.1:8000/frontend/send-verification-code/', {
          email: this.email
        }, {
          headers: {
            'X-CSRFToken': this.csrfToken
          },
          withCredentials: true  // 確保傳遞cookies
        });

        this.feedbackSuccess = response.data.success;
        this.verificationFeedback = response.data.success
          ? '驗證碼已發送到您的電子郵件，有效期限5分鐘。'
          : response.data.message || '無法發送驗證碼，請稍後再試。';
      } catch (error) {
        this.feedbackSuccess = false;
        this.verificationFeedback = '無法發送驗證碼，請稍後再試。';
      }
    },
    validateEmail(email) {
      const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      return re.test(String(email).toLowerCase());
    },
    validatePassword(password) {
      const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      return re.test(password);
    },
    handleTogglePassword(event) {
      const passwordInput = event.target.previousElementSibling;
      passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    },
    async handleSubmit() {
      if (this.password !== this.confirmPassword) {
        alert('密碼與確認密碼不匹配。');
        return;
      }

      if (!this.validatePassword(this.password)) {
        alert('密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。例如：Password@123');
        return;
      }

      try {
        const response = await axios.post('/frontend/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
          confirmPassword: this.confirmPassword,  
          phone: this.phone,
          verificationCode: this.verificationCode  
        }, {
          headers: {
            'X-CSRFToken': this.csrfToken
          },
          withCredentials: true  
        });

        if (response.data.success) {
          alert('註冊成功！請等待管理員審核您的帳號。');
          this.$router.push('/frontend/login');
        } else {
          alert(response.data.message || '註冊失敗，請重試。');
        }
      } catch (error) {
        alert('註冊失敗，請稍後再試。');
      }
    }
  },
  created() {
    this.fetchCsrfToken();  // 初始化時獲取CSRF token
  }
};
</script>
