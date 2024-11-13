<template>
  <div class="profile-container">
    <div class="profile-card">
      <div v-if="!isEditing" class="profile-info">
        <h3>個人資料</h3>
        <br>                 
        <br>
        <br>
        
        <div class="form-row">
          <div class="form-group">
            <label>用戶名稱：</label>
            <p>{{ userData.username || 'N/A' }}</p>
          </div>
          <div class="form-group">
            <label>部門：</label>
            <p>{{ userData.department_id || 'N/A' }}</p>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>職位：</label>
            <p>{{ userData.position_id || 'N/A' }}</p>
          </div>
          <div class="form-group">
            <label>電話：</label>
            <p>{{ userData.phone || 'N/A' }}</p>
          </div>
        </div>
        <div class="form-group full-width">
          <label>電子郵件：</label>
          <p>{{ userData.email || 'N/A' }}</p>
        </div>
        <button class="edit-button" @click="editProfile">編輯</button>
      </div>

      <div v-if="isEditing" class="edit-form">
        <h3>編輯個人資料</h3>
        <div class="form-row">
          <div class="form-group">
            <label for="username">用戶名稱：</label>
            <input type="text" v-model="editData.username" />
          </div>
          <div class="form-group">
            <label for="department">部門：</label>
            <input type="text" v-model="editData.department_id" disabled />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="position">職位：</label>
            <input type="text" v-model="editData.position_id" disabled />
          </div>
          <div class="form-group">
            <label for="phone">電話：</label>
            <input type="tel" v-model="editData.phone" @input="validatePhone" />
          </div>
        </div>
        <div class="form-group full-width">
          <label for="email">電子郵件：</label>
          <input type="email" v-model="editData.email" />
        </div>

        <!-- 密碼修改欄位 -->
        <div class="form-row">
          <div class="form-group">
            <label for="currentPassword">當前密碼：</label>
            <input type="password" v-model="editData.currentPassword" />
          </div>
          <div class="form-group">
            <label for="newPassword">新密碼：</label>
            <input type="password" v-model="editData.newPassword" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group half-width">
            <label for="confirmPassword">確認新密碼：</label>
            <input type="password" v-model="editData.confirmPassword" />
          </div>
          <div class="form-group small-button">
            <button type="button" class="submit-button" @click="handleSubmit">修改密碼</button>
          </div>
        </div>
        <p class="password-requirements">
          密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。
        </p>

        <div class="button-container">
          <button @click="saveProfile" class="save">保存</button>
          <button @click="cancelEdit" class="cancel">取消</button>
        </div>

        <!-- 錯誤提示 -->
        <p v-if="errorMessage" class="feedback">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';

export default {
  data() {
    return {
      userData: {
        username: '',
        email: '',
        phone: '',
        department_id: '',
        position_id: ''
      },
      editData: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      isEditing: false,
      errorMessage: ''
    };
  },
  methods: {
    // 獲取用戶資料
    async fetchUserProfile() {
      try {
        const token = localStorage.getItem('frontend_token');
        if (!token) {
          alert('無效的token，請重新登入');
          router.push('/frontend/login');
        }
        const response = await axios.get('/api/frontend/profile/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        this.userData = response.data;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },

    // 切換到編輯模式
    editProfile() {
      this.editData = { ...this.userData };
      this.isEditing = true;
    },

    // 取消編輯
    cancelEdit() {
      this.isEditing = false;
    },

    // 保存個人信息和密碼
    async saveProfile() {
      if (this.editData.newPassword || this.editData.confirmPassword) {
        if (this.editData.newPassword !== this.editData.confirmPassword) {
          this.errorMessage = '新密碼與確認密碼不匹配';
          return;
        }

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(this.editData.newPassword)) {
          this.errorMessage = '新密碼不符合要求。';
          return;
        }
      }

      try {
        const token = localStorage.getItem('frontend_token');
        const formData = new FormData();
        formData.append('username', this.editData.username);
        formData.append('email', this.editData.email);
        formData.append('phone', this.editData.phone);

        if (this.editData.newPassword) {
          formData.append('current_password', this.editData.currentPassword);
          formData.append('new_password', this.editData.newPassword);
          formData.append('confirm_password', this.editData.confirmPassword);
        }

        await axios.put('/api/frontend/profile/', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });

        if (this.editData.newPassword) {
          alert('密碼修改成功，請重新登入');
          router.push('/frontend/login');
        } else {
          this.userData = { ...this.editData };
          this.isEditing = false;
          alert('個人資訊已更新');
        }
      } catch (error) {
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message || '保存失敗';
        } else {
          this.errorMessage = '保存失敗';
        }
        console.error('Error saving profile:', error);
      }
    },

    // 密碼修改提交功能
    async handleSubmit() {
      if (this.editData.newPassword !== this.editData.confirmPassword) {
        this.errorMessage = '新密碼與確認密碼不匹配';
        return;
      }

      if (!this.validatePassword(this.editData.newPassword)) {
        this.errorMessage = '新密碼不符合要求。';
        return;
      }

      try {
        const response = await axios.post('/frontend/changepassword/', {
          current_password: this.editData.currentPassword,
          new_password: this.editData.newPassword
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
    },

    // 驗證電話欄位只接受數字
    validatePhone() {
      this.editData.phone = this.editData.phone.replace(/\D/g, '');
    },

    // 驗證密碼的正則表達式
    validatePassword(password) {
      const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      return re.test(password);
    }
  },
  mounted() {
    if (!this.isBackend) {
      this.fetchUserProfile();
    }
  }
};
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100vh;
  background-color: #f4f4f4;
  overflow-y: auto;
  padding: 20px;
  margin-top: 100px;
  padding-bottom: 50px;
}

.profile-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 800px;
  max-height: none;
  overflow: visible;
  margin-bottom: 75px;
}

.form-group {
  margin-bottom: 15px;
}

.half-width {
  width: 48%;
}

.small-button {
  width: 30%;
  text-align: center;
  padding: 8px;
  margin-top: 25px;
}

.profile-info h3, .edit-form h3 {
  margin-bottom: 20px;
  text-align: center;
}

.form-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.form-group {
  flex: 1;
  margin-right: 10px;
}

.form-group:last-child {
  margin-right: 0;
}

.full-width {
  width: 100%;
}

.button-container {
  display: flex;
  justify-content: space-between;
}

.save {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.submit-button {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 8px;
  cursor: pointer;
  border-radius: 5px;
  font-size: 14px;
}

.cancel {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.edit-button {
  display: block;
  margin: 0 auto;
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.password-requirements {
  font-size: 12px;
  color: gray;
  margin-top: -10px;
  text-align: left;
}

.feedback {
  color: red;
  text-align: center;
  margin-top: 15px;
}
</style>
