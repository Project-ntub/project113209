<template>
  <div class="profile-container">
    <div class="profile-card">
      <h3 v-if="!isEditing">個人資料</h3>
      <h3 v-if="isEditing">編輯個人資料</h3>
      <div class="scrollable-content">
        <div v-if="!isEditing" class="profile-info">
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
          <div class="form-group">
            <label>電子郵件：</label>
            <p>{{ userData.email || 'N/A' }}</p>
          </div>
          <button class="edit-button" @click="editProfile">編輯</button>
        </div>

        <div v-if="isEditing" class="edit-form">
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
          <div class="form-group">
            <label for="email">電子郵件：</label>
            <input type="email" v-model="editData.email" />
          </div>

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
          <div class="form-group">
            <label for="confirmPassword">確認新密碼：</label>
            <input type="password" v-model="editData.confirmPassword" />
          </div>
          <p class="password-requirements">
            密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。
          </p>
          <div class="button-container">
            <button @click="saveProfile" class="save">保存</button>
            <button @click="cancelEdit" class="cancel">取消</button>
          </div>
          <p v-if="errorMessage" class="feedback">{{ errorMessage }}</p>
        </div>
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
        username: '',
        email: '',
        phone: '',
        department_id: '',
        position_id: '',
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
        this.errorMessage =
          (error.response && error.response.data.message) || '保存失敗';
        console.error('Error saving profile:', error);
      }
    },

    // 驗證電話欄位只接受數字
    validatePhone() {
      this.editData.phone = this.editData.phone.replace(/\D/g, '');
    }
  },
  mounted() {
    this.fetchUserProfile();
  }
};
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  padding: 40px;
  background-color: #f9fafc;
  min-height: calc(100vh - 80px);
}

.profile-card {
  background-color: #ffffff;
  width: 90%;
  max-width: 1200px;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-height: 90vh; /* 卡片最大高度為視窗高度 */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden; /* 防止超出卡片的部分顯示 */
}

.scrollable-content {
  overflow-y: auto; /* 垂直方向可滾動 */
  max-height: calc(90vh - 80px); /* 根據卡片最大高度調整內容最大高度 */
  padding-right: 10px; /* 防止滾動條遮擋文字 */
}

.profile-info,
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  flex: 1 1 calc(33.33% - 20px);
  min-width: 200px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333333;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #cccccc;
  border-radius: 5px;
  font-size: 14px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.edit-button {
  background-color: #007bff;
  color: white;
  align-self: flex-end;
}

.save {
  background-color: #28a745;
  color: white;
}

.cancel {
  background-color: #dc3545;
  color: white;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.password-requirements {
  font-size: 12px;
  color: #6c757d;
}

.feedback {
  color: #dc3545;
  text-align: center;
}
.profile-card p {
  font-size: 18px;
  color: #666;
}
</style>











