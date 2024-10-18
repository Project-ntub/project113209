<template> 
  <div class="personal-preference-container">
    <h1>個人偏好管理</h1>
    <div v-if="loading">載入中...</div>
    <div v-else>
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
          <tr v-if="preference">
            <td>{{ preference.id }}</td>
            <td>{{ preference.user_id }}</td>
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
            <td>{{ preference.authentication ? '已驗證' : '未驗證' }}</td>
            <td>
              <button class="save-btn" @click="savePreference(preference)" :disabled="loading">
                {{ loading ? '保存中...' : '保存' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'PersonalPreference',
  computed: {
    ...mapGetters(['preference']), // 獲取單一偏好
  },
  data() {
    return {
      loading: true, // 新增 loading 狀態
      fontSizeMapping: { // 字體大小對應表
        small: '12px',
        medium: '16px',
        large: '20px'
      },
    };
  },
  created() {
    this.loadPreference(); // 初始化時載入偏好設置
  },
  methods: {
    ...mapActions(['fetchPreference', 'updateFontSize']), // 映射 Vuex actions
    // 載入當前登入用戶的偏好設置
    loadPreference() {
      this.fetchPreference()
        .then(() => {
          this.loading = false;
          // 更新字體大小
          this.updateFontSize(this.preference.fontsize);
        })
        .catch(() => {
          this.loading = false;
        });
    },
    // 保存偏好設置
    savePreference(preference) {
      this.loading = true;
      
      // 將字體大小保存到 localStorage
      if (this.fontSizeMapping[preference.fontsize]) {
        localStorage.setItem('user-fontsize', preference.fontsize);
      }

      // 保存其他偏好設置
      axios.put(`/api/backend/user_preferences/${preference.id}/`, preference)
        .then(() => {
          alert('偏好設置已保存');
          this.updateFontSize(preference.fontsize); // 更新 Vuex 中的字體大小
          this.loading = false;
        })
        .catch(error => {
          console.error('保存偏好設置時出錯:', error);
          alert('保存偏好設置時出錯，請稍後再試。');
          this.loading = false;
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
  transition: background-color 0.3s ease; /* 添加平滑的背景顏色變化效果 */
}

.save-btn:hover {
  background-color: #ff6347; /* 懸停時的背景顏色 */
}

.save-btn:active {
  transform: scale(0.98); /* 點擊時按鈕縮小效果 */
}
</style>
