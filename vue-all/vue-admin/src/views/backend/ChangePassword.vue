<template>
  <div>
    <h2>修改密碼</h2>
    <form @submit.prevent="changePassword">
      <div>
        <label for="currentPassword">當前密碼</label>
        <input type="password" v-model="currentPassword" required />
      </div>
      <div>
        <label for="newPassword">新密碼</label>
        <input type="password" v-model="newPassword" required />
      </div>
      <div>
        <label for="confirmPassword">確認新密碼</label>
        <input type="password" v-model="confirmPassword" required />
      </div>
      <button type="submit">修改密碼</button>
    </form>
    <p v-if="errorMessage">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';

export default {
  name: 'BackendChangePassword',
  data() {
    return {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
      errorMessage: ''
    };
  },
  methods: {
    async changePassword() {
      if (this.newPassword !== this.confirmPassword) {
        this.errorMessage = '新密碼與確認密碼不匹配';
        return;
      }
      try {
        const response = await axios.post('/api/frontend/changepassword/', {
          current_password: this.currentPassword,
          new_password: this.newPassword
        });
        alert(response.data.message);
        router.push('/backend/login'); // 密碼修改成功後跳轉到登入頁面
      } catch (error) {
        this.errorMessage = error.response?.data?.message || '密碼修改失敗，請稍後再試';
      }
    }
  }
};
</script>

<style scoped>
.change-password-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
}
.input-group {
  margin-bottom: 1em;
}
.submit-button, .cancel-button {
  display: inline-block;
  margin-right: 10px;
}
.feedback {
  margin-top: 1em;
  color: red;
  font-size: 16px;
}
</style>
