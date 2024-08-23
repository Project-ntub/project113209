<template>
  <div class="app-container">
    <Sidebar :isSidebarActive="isSidebarActive" />
    <div class="app-content" :class="{ shifted: isSidebarActive }">
      <h1 class="title">個人偏好管理</h1>
      <form @submit.prevent="updatePreferences" class="preferences-form">
        <div class="form-group">
          <label for="font-size">字體大小:</label>
          <select v-model="preferences.fontsize" id="font-size" class="form-control">
            <option value="small">小</option>
            <option value="medium">中</option>
            <option value="large">大</option>
          </select>
        </div>
        <div class="form-group">
          <label for="notification-settings">通知:</label>
          <select v-model="preferences.notificationSettings" id="notification-settings" class="form-control">
            <option :value="1">啟用</option>
            <option :value="0">不啟用</option>
          </select>
        </div>
        <div class="form-group">
          <label for="auto-login">自動登入:</label>
          <select v-model="preferences.autoLogin" id="auto-login" class="form-control">
            <option :value="1">啟用</option>
            <option :value="0">不啟用</option>
          </select>
        </div>
        <div class="form-group">
          <label for="authentication">是否驗證:</label>
          <select v-model="preferences.authentication" id="authentication" class="form-control">
            <option :value="1">已驗證</option>
            <option :value="0">未驗證</option>
          </select>
        </div>
        <div class="btn-container">
          <button type="submit" class="btn btn-save">保存更改</button>
          <button type="button" class="btn btn-add" @click="showAddModal">新增</button>
          <button type="button" class="btn btn-delete" @click="deletePreference">刪除</button>
          <button type="button" class="btn btn-cancel" @click="resetPreferences">取消更改</button>
        </div>
      </form>
  
      <div v-if="successMessage" class="success-message">保存成功！</div>
  
      <!-- 新增彈出窗口 -->
      <div v-if="showModal" class="modal">
        <div class="modal-content">
          <span class="close" @click="closeAddModal">&times;</span>
          <h2 class="title">新增個人偏好</h2>
          <form @submit.prevent="addPreference" class="preferences-form">
            <div class="form-group">
              <label for="add-font-size">字體大小:</label>
              <select v-model="newPreference.fontsize" id="add-font-size" class="form-control">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
              </select>
            </div>
            <div class="form-group">
              <label for="add-notifications">通知:</label>
              <select v-model="newPreference.notificationSettings" id="add-notifications" class="form-control">
                <option :value="1">啟用</option>
                <option :value="0">不啟用</option>
              </select>
            </div>
            <div class="form-group">
              <label for="add-auto-login">自動登入:</label>
              <select v-model="newPreference.autoLogin" id="add-auto-login" class="form-control">
                <option :value="1">啟用</option>
                <option :value="0">不啟用</option>
              </select>
            </div>
            <div class="form-group">
              <label for="add-authentication">是否驗證:</label>
              <select v-model="newPreference.authentication" id="add-authentication" class="form-control">
                <option :value="1">已驗證</option>
                <option :value="0">未驗證</option>
              </select>
            </div>
            <div class="btn-container">
              <button type="submit" class="btn btn-save">保存</button>
              <button type="button" class="btn btn-cancel" @click="closeAddModal">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Sidebar from './SideBar.vue';

export default {
  name: 'PersonalPreference',
  components: {
    Sidebar
  },
  data() {
    return {
      preferences: {
        user_id: null,
        fontsize: '',
        notificationSettings: 0,
        autoLogin: 0,
        authentication: 0
      },
      newPreference: {
        fontsize: 'medium',
        notificationSettings: 0,
        autoLogin: 0,
        authentication: 0
      },
      successMessage: false,
      showModal: false,
      isSidebarActive: false
    };
  },
  created() {
    this.loadPreferences();
  },
  methods: {
    loadPreferences() {
      axios.get('/preferences/get_preferences/')
        .then(response => {
          this.preferences = response.data;
        })
        .catch(error => {
          console.error('Error loading preferences:', error);
        });
    },
    updatePreferences() {
      axios.post('/preferences/update_preference/', this.preferences)
        .then(response => {
          if (response.status === 200) {
            this.showSuccessMessage();
          } else {
            alert('保存失敗');
          }
        })
        .catch(error => {
          console.error('Error updating preferences:', error);
        });
    },
    showAddModal() {
      this.showModal = true;
    },
    closeAddModal() {
      this.showModal = false;
    },
    addPreference() {
      axios.post('/preferences/add_preference/', this.newPreference)
        .then(response => {
          if (response.status === 200) {
            this.closeAddModal();
            this.showSuccessMessage();
          } else {
            alert('新增失敗');
          }
        })
        .catch(error => {
          console.error('Error adding preference:', error);
        });
    },
    deletePreference() {
      axios.post('/preferences/delete_preference/', { user_id: this.preferences.user_id })
        .then(response => {
          if (response.status === 200) {
            this.showSuccessMessage();
          } else {
            alert('刪除失敗');
          }
        })
        .catch(error => {
          console.error('Error deleting preference:', error);
        });
    },
    resetPreferences() {
      this.loadPreferences();
    },
    showSuccessMessage() {
      this.successMessage = true;
      setTimeout(() => {
        this.successMessage = false;
      }, 3000);
    }
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.app-content {
  width: 100%;
  max-width: 600px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  color: #333;
  font-size: 24px;
  margin-bottom: 20px;
}

.preferences-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  font-size: 16px;
  color: #555;
  margin-bottom: 5px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: #fff;
  color: #333;
}

.btn-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #fff;
}

.btn-save {
  background-color: #28a745;
}

.btn-add {
  background-color: #007bff;
}

.btn-delete {
  background-color: #dc3545;
}

.btn-cancel {
  background-color: #6c757d;
}

.btn:hover {
  opacity: 0.9;
}

.success-message {
  color: #28a745;
  text-align: center;
  font-size: 16px;
  margin-top: 20px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.close {
  font-size: 24px;
  color: #333;
  position: absolute;
  top: 10px;
  right: 20px;
  cursor: pointer;
}
</style>
