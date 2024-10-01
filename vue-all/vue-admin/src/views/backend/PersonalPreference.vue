<template>
  <div class="personal-preference-container" :style="{ fontSize: currentFontSize }">
    <h1>個人偏好管理</h1>
    <table class="preferences-table">
      <thead>
        <tr>
          <th>編號</th>
          <th>用戶</th>
          <th>字體大小</th>
          <th>通知</th>
          <th>是否驗證</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="preference in preferences" :key="preference.id">
          <td>{{ preference.id }}</td>
          <td>{{ preference.user_id }}</td>
          <td>
            <!-- 字體大小選擇 -->
            <select v-model="tempFontSize">
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
          <td>{{ preference.authentication ? '已驗證' : '未驗證' }}</td>
          <td>
            <button class="save-btn" @click="savePreference(preference)">保存</button>
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
      preferences: [], // 存儲用戶偏好數據
      currentFontSize: 'medium', // 預設字體大小
      tempFontSize: 'medium' // 暫存使用者選擇的字體大小
    };
  },
  created() {
    this.loadPreferences(); // 初始化時載入偏好設置
    this.getSavedFontSize(); // 初始化時載入儲存的字體大小
  },
  methods: {
    // 載入當前登入用戶的偏好設置
    loadPreferences() {
      axios.get('/api/backend/user_preferences/')
        .then(response => {
          this.preferences = response.data;
          this.tempFontSize = this.currentFontSize; // 初始化時將暫存字體大小設定為當前大小
        })
        .catch(error => {
          console.error('載入偏好設置時出錯:', error);
        });
    },
    // 從 localStorage 載入已保存的字體大小
    getSavedFontSize() {
      const savedFontSize = localStorage.getItem('user-fontsize');
      if (savedFontSize) {
        this.currentFontSize = savedFontSize;
        this.tempFontSize = savedFontSize;
      }
    },
    // 保存偏好設置
    savePreference(preference) {
      // 保存選擇的字體大小
      switch (this.tempFontSize) {
        case 'small':
          this.currentFontSize = '12px';
          break;
        case 'medium':
          this.currentFontSize = '16px';
          break;
        case 'large':
          this.currentFontSize = '20px';
          break;
        default:
          this.currentFontSize = '16px';
      }
      
      // 將字體大小保存到 localStorage
      localStorage.setItem('user-fontsize', this.currentFontSize);

      // 保存其他偏好設置
      axios.put(`/api/backend/user_preferences/update/${preference.id}/`, preference)
        .then(() => {
          alert('偏好設置已保存');
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
  max-width: 1000px; /* 增加最大寬度 */
  margin: 0 auto;
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #f0f8ff, #fae3d9);
  border-radius: 15px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #333;
  font-size: 36px; /* 增加字體大小 */
  font-weight: bold;
  margin-bottom: 30px; /* 增加 margin */
}

.preferences-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 30px;
}

.preferences-table th, .preferences-table td {
  padding: 20px; /* 增加內部邊距 */
  border: 1px solid #ddd;
  text-align: center;
  font-size: 16px; /* 增加字體大小 */
}

.preferences-table th {
  background-color: #ff8c00;
  color: white;
  font-weight: bold;
}

.preferences-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.preferences-table tr:hover {
  background-color: #ffe4b5;
}

select {
  padding: 10px; /* 增加 padding */
  border-radius: 5px;
  border: 1px solid #ccc;
  font-size: 14px; /* 增加字體大小 */
}

.save-btn {
  background-color: #ff4500;
  color: white;
  padding: 12px 24px; /* 增加 padding */
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.save-btn:hover {
  background-color: #ff6347;
}

.save-btn:active {
  transform: scale(0.98);
}
</style>
