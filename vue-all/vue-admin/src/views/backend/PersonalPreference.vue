<template>
  <TopNavbar title="個人偏好管理" />
  <div class="personal-preference-container">
    <table class="preferences-table">
      <thead>
        <tr>
          <th>編號</th>
          <th>用戶</th>
          <th>字體大小</th>
          <th>通知</th>
          <th>自動登入</th>
          <th>是否驗證</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="preference in preferences" :key="preference.id">
          <td>{{ preference.id }}</td>
          <td>{{ preference.user_id }}</td>  <!-- 顯示用戶 ID -->
          <td>{{ preference.fontsize }}</td>
          <td>{{ preference.notificationSettings ? '啟用' : '不啟用' }}</td>
          <td>{{ preference.autoLogin ? '啟用' : '不啟用' }}</td>
          <td>{{ preference.authentication ? '已驗證' : '未驗證' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import TopNavbar from '@/components/frontend/TopNavbar.vue'; 


export default {
  name: 'PersonalPreference',
  components: {
    TopNavbar,
  },
  data() {
    return {
      preferences: []
    };
  },
  created() {
    this.loadPreferences();
  },
  methods: {
    loadPreferences() {
      axios.get('/api/backend/user_preferences/')
        .then(response => {
          this.preferences = response.data;
        })
        .catch(error => {
          console.error('載入偏好設置時出錯:', error);
        });
    }
  }
};
</script>
