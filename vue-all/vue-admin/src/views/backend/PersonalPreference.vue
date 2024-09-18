<template>
  <div class="personal-preference-container">
    <h1>個人偏好管理</h1>
    <table class="preferences-table">
      <thead>
        <tr>
          <th>編號</th>
          <th>用戶</th>
          <th>字體大小</th>
          <th>通知</th>
          <th>自動登入</th>
          <th>是否驗證</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="preference in preferences" :key="preference.id">
          <td>{{ preference.id }}</td>
          <td>{{ preference.user_id }}</td>
          <td>
            <!-- 將字體大小改為下拉式選單 -->
            <select v-model="preference.fontsize">
              <option value="small">小</option>
              <option value="medium">中</option>
              <option value="large">大</option>
            </select>
          </td>
          <td>
            <select v-model="preference.notificationSettings">
              <option :value="true">啟用</option>
              <option :value="false">不啟用</option>
            </select>
          </td>
          <td>
            <select v-model="preference.autoLogin">
              <option :value="true">啟用</option>
              <option :value="false">不啟用</option>
            </select>
          </td>
          <td>{{ preference.authentication ? '已驗證' : '未驗證' }}</td>
          <td>
            <button @click="savePreference(preference)">保存</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PersonalPreference',
  data() {
    return {
      preferences: [] // 存儲用戶偏好數據
    };
  },
  created() {
    this.loadPreferences(); // 初始化時載入偏好設置
  },
  methods: {
    // 載入當前登入用戶的偏好設置
    loadPreferences() {
      axios.get('/api/backend/user_preferences/')  // 後端自動返回當前登入用戶的偏好設置
        .then(response => {
          this.preferences = response.data; // 將API返回的偏好設置保存到本地
        })
        .catch(error => {
          console.error('載入偏好設置時出錯:', error);
        });
    },
    // 保存偏好設置
    savePreference(preference) {
      axios.put(`/api/backend/user_preferences/update/${preference.id}/`, preference)
        .then(() => {
          alert('偏好設置已保存'); // 保存成功後提示用戶
        })
        .catch(error => {
          console.error('保存偏好設置時出錯:', error);
        });
    }
  }
};
</script>

<style scoped>
.personal-preference-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.preferences-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.preferences-table th, .preferences-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.preferences-table th {
  background-color: #f4f4f4;
}
</style>
