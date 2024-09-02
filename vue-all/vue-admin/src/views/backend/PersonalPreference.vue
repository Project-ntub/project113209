<template>
  <TopNavbar title="個人偏好管理" />
  <div class="app-container">
    <div class="app-content" :class="{ shifted: isSidebarActive }">
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
import TopNavbar from '@/components/frontend/TopNavbar.vue'; // 引入前台的TopNavbar组件
import axios from 'axios';

export default {
  name: 'PersonalPreference',
  components: {
    TopNavbar
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
      axios.get('/api/user_preferences/')
        .then(response => {
            this.preferences = response.data;
        })
        .catch(error => {
            console.error('Error loading preferences:', error);
        });
    },
    updatePreferences() {
      axios.post('/api/user_preferences/', this.preferences)
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
      axios.post('/api/user_preferences/', this.newPreference)
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
      axios.post('/api/user_preferences/', { user_id: this.preferences.user_id })
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

<style scoped src="@/assets/css/backend/PersonalPreference.css"></style>

