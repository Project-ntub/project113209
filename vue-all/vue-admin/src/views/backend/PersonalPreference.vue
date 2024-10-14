<!-- src/components/PersonalPreference.vue -->
<template>
  <div class="personal-preference-container">
    <h1>個人偏好管理</h1>
    <table class="preferences-table">
      <thead>
        <tr>
          <th>字體大小</th>
          <th>通知</th>
          <th>自動登入</th>
          <th>是否驗證</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="preference in preferences" :key="preference.id">
          <td>
            <!-- 字體大小選擇 -->
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
          this.$emit('preference-updated', preference); // 發射事件
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
  padding: 60px; /* 增加內部填充 */
  background: linear-gradient(135deg, #f0f8ff, #fae3d9); /* 使用漸層背景 */
  border-radius: 15px;
  box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); /* 增加陰影效果 */
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
  background-color: #f9f9f9; /* 使用交錯顏色行 */
}

.preferences-table tr:hover {
  background-color: #ffe4b5; /* 滑鼠懸停時背景色變化 */
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
  font-size: 16px; /* 增加字體大小 */
  transition: background-color 0.3s ease; /* 添加平滑的背景顏色變化效果 */
}

.save-btn:hover {
  background-color: #ff6347; /* 懸停時的背景顏色 */
}

.save-btn:active {
  transform: scale(0.98); /* 點擊時按鈕縮小效果 */
}
</style>
