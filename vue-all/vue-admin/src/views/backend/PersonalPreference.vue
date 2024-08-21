<template>
  <div class="app-container">
    <h1>個人偏好管理</h1>
    <form @submit.prevent="updatePreferences">
      <div class="form-group">
        <label for="font-size">字體大小:</label>
        <select v-model="preferences.fontsize" id="font-size">
          <option value="small">小</option>
          <option value="medium">中</option>
          <option value="large">大</option>
        </select>
      </div>
      <div class="form-group">
        <label for="notification-settings">通知:</label>
        <select v-model="preferences.notificationSettings" id="notification-settings">
          <option value="on">啟用</option>
          <option value="off">不啟用</option>
        </select>
      </div>
      <div class="form-group">
        <label for="auto-login">自動登入:</label>
        <select v-model="preferences.autoLogin" id="auto-login">
          <option value="on">啟用</option>
          <option value="off">不啟用</option>
        </select>
      </div>
      <div class="btn-container">
        <button type="submit" class="btn">保存更改</button>
        <button type="button" class="btn" @click="showAddModal">新增</button>
        <button type="button" class="btn btn-delete" @click="deletePreference">刪除</button>
        <button type="button" class="btn btn-cancel" @click="resetPreferences">取消更改</button>
      </div>
    </form>
  
    <div v-if="successMessage" class="success-message">保存成功！</div>
  
      <!-- 新增彈出窗口 -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeAddModal">&times;</span>
        <h2>新增個人偏好</h2>
        <form @submit.prevent="addPreference">
          <div class="form-group">
            <label for="add-font-size">字體大小:</label>
            <select v-model="newPreference.fontsize" id="add-font-size">
              <option value="small">小</option>
              <option value="medium">中</option>
              <option value="large">大</option>
            </select>
          </div>
          <div class="form-group">
            <label for="add-notifications">通知:</label>
            <select v-model="newPreference.notificationSettings" id="add-notifications">
              <option value="on">啟用</option>
              <option value="off">不啟用</option>
            </select>
          </div>
          <div class="form-group">
            <label for="add-auto-login">自動登入:</label>
            <select v-model="newPreference.autoLogin" id="add-auto-login">
              <option value="on">啟用</option>
              <option value="off">不啟用</option>
            </select>
          </div>
          <div class="btn-container">
            <button type="submit" class="btn">保存</button>
            <button type="button" class="btn btn-cancel" @click="closeAddModal">取消</button>
          </div>
        </form>
      </div>
    </div>
  
      <!-- 查詢表單 -->
    <h2>查詢個人偏好</h2>
    <form @submit.prevent="queryPreferences">
      <div class="form-group">
        <label for="query-font-size">字體大小:</label>
        <select v-model="query.fontsize" id="query-font-size">
          <option value="">--選擇--</option>
          <option value="small">小</option>
          <option value="medium">中</option>
          <option value="large">大</option>
        </select>
      </div>
      <div class="form-group">
        <label for="query-notifications">通知:</label>
        <select v-model="query.notificationSettings" id="query-notifications">
          <option value="">--選擇--</option>
          <option value="on">啟用</option>
          <option value="off">不啟用</option>
        </select>
      </div>
      <div class="form-group">
        <label for="query-auto-login">自動登入:</label>
        <select v-model="query.autoLogin" id="query-auto-login">
          <option value="">--選擇--</option>
          <option value="on">啟用</option>
          <option value="off">不啟用</option>
        </select>
      </div>
      <div class="btn-container">
        <button type="submit" class="btn">查詢</button>
      </div>
    </form>
  
      <!-- 查詢結果 -->
    <div class="results" v-if="queryResults.length > 0">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>字體大小</th>
            <th>通知</th>
            <th>自動登入</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in queryResults" :key="result.user_id">
            <td>{{ result.user_id }}</td>
            <td>{{ result.fontsize }}</td>
            <td>{{ result.notificationSettings === 'on' ? '啟用' : '不啟用' }}</td>
            <td>{{ result.autoLogin === 'on' ? '啟用' : '不啟用' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="results">沒有符合條件的偏好設置</div>
  </div>
</template>

<script>
import axios from 'axios'; // 確保你已經安裝並配置了 axios

export default {
  name: 'PersonalPreference',
  data() {
    return {
      preferences: {
        user_id: null,  // 這是從後端獲取的 user_id
        fontsize: '',
        notificationSettings: 'off',
        autoLogin: 'off'
      },
      newPreference: {
        fontsize: 'medium',
        notificationSettings: 'off',
        autoLogin: 'off'
      },
      query: {
        fontsize: '',
        notificationSettings: '',
        autoLogin: ''
      },
      queryResults: [],
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
          console.error('無法取得偏好設置:', error);
        });
    },
    updatePreferences() {
      axios.post('/preferences/update_preference/', this.preferences)
        .then(response => {
          if (response.data.status === 'success') {
            this.showSuccessMessage();
          } else {
            alert('保存失敗');
          }
        })
        .catch(error => {
          console.error('保存偏好設置失敗:', error);
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
          if (response.data.status === 'success') {
            this.closeAddModal();
            this.showSuccessMessage();
          } else {
            alert('新增失敗');
          }
        })
        .catch(error => {
          console.error('新增偏好設置失敗:', error);
        });
    },
    deletePreference() {
      axios.post('/preferences/delete_preference/', { user_id: this.preferences.user_id })  // 傳遞 user_id 進行刪除
        .then(response => {
          if (response.data.status === 'success') {
            this.showSuccessMessage();
          } else {
            alert('刪除失敗');
          }
        })
        .catch(error => {
          console.error('刪除偏好設置失敗:', error);
        });
    },
    resetPreferences() {
      this.loadPreferences();
    },
    queryPreferences() {
      let query = `/preferences/query_preferences/?`;
      if (this.query.fontsize) query += `fontsize=${this.query.fontsize}&`;
      if (this.query.notificationSettings) query += `notificationSettings=${this.query.notificationSettings}&`;
      if (this.query.autoLogin) query += `autoLogin=${this.query.autoLogin}&`;

      axios.get(query)
        .then(response => {
          this.queryResults = response.data;
        })
        .catch(error => {
          console.error('查詢偏好設置失敗:', error);
        });
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
