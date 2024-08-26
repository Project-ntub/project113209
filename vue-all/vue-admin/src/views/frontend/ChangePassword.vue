<template>
  <div class="change-password-container">
    <h2>修改密碼</h2>
    <p class="password-policy">提示：一個月內只能修改兩次密碼</p>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="currentPassword">當前密碼</label>
        <input type="password" v-model="currentPassword" required class="input-field"/>
      </div>
      <div class="input-group">
        <label for="newPassword">新密碼</label>
        <input type="password" v-model="newPassword" required class="input-field"/>
        <p class="password-requirements">
          密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。
        </p>
      </div>
      <div class="input-group">
        <label for="confirmPassword">確認新密碼</label>
        <input type="password" v-model="confirmPassword" required class="input-field"/>
      </div>
      <div class="button-group">
        <button type="submit" class="submit-button">修改密碼</button>
      </div>
    </form>
    <p v-if="errorMessage" class="feedback">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';

export default {
  data() {
    return {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
      errorMessage: ''
    };
  },
  methods: {
    validatePassword(password) {
      // 密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。
      const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      return re.test(password);
    },
    async handleSubmit() {
      if (this.newPassword !== this.confirmPassword) {
        this.errorMessage = '新密碼與確認密碼不匹配';
        return;
      }

      if (!this.validatePassword(this.newPassword)) {
        this.errorMessage = '新密碼不符合要求。';
        return;
      }

      try {
        const response = await axios.post('/frontend/changepassword/', {
          current_password: this.currentPassword,
          new_password: this.newPassword
        });

        alert(response.data.message);
        router.push('/frontend/login');
      } catch (error) {
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message || '密碼修改失敗，請稍後再試';
        } else {
          this.errorMessage = '密碼修改失敗，請稍後再試';
        }
      }
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/ChangePassword.css"></style>
