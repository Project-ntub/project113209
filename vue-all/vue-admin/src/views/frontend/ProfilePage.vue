<template>
  <div>
    <div class="profile-container">
      <div class="profile-card">
        <div class="profile-image">
          <!-- 圓形的圖片容器，如果沒有圖片則顯示佔位圖片 -->
          <img :src="imageSrc || 'https://via.placeholder.com/150'" alt="Profile Image" />
        </div>
        <div class="profile-info">
          <h2>{{ userData.username || 'N/A' }}</h2>
          <p>{{ userData.position_id || 'N/A' }}</p>
          <p>{{ userData.department_id || 'N/A' }}</p>
          <p>{{ userData.email || 'N/A' }}</p>
          <p>{{ userData.phone || 'N/A' }}</p>
          <button class="edit-button" @click="editProfile">編輯</button>
        </div>
      </div>

      <div v-if="isEditing" class="edit-modal">
        <div class="edit-form">
          <h3>編輯個人信息</h3>
          <p>用戶名：<input type="text" v-model="editData.username" /></p>
          <p>部門：<input type="text" v-model="editData.department_id" disabled /></p>
          <p>職位：<input type="text" v-model="editData.position_id" disabled /></p>
          <p>電話：<input type="text" v-model="editData.phone" /></p>
          <p>電子郵件：<input type="email" v-model="editData.email" /></p>
          <p>上傳新照片：<input type="file" @change="onFileChange" /></p>
          <div class="button-container">
            <button @click="saveProfile" class="save">保存</button>
            <button @click="cancelEdit" class="cancel">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      userData: {
        username: '',
        email: '',
        phone: '',
        department_id: '',
        position_id: '',
        profile_image: null  // 用戶的個人照片
      },
      editData: {},
      isEditing: false,
      imageSrc: null,  // 用於顯示的圖片源
    };
  },
  methods: {
    async fetchUserProfile() {
      try {
        const token = localStorage.getItem('frontend_token');  // 獲取 token
        const response = await axios.get('/api/frontend/profile/', {
          headers: {
            'Authorization': `Bearer ${token}`  // 添加 Authorization 標頭
          }
        });
        console.log(response.data);  // 檢查後端返回的數據
        this.userData = response.data;
        console.log('Profile Image URL:', this.userData.profile_image); 
        this.imageSrc = `${this.userData.profile_image}?${new Date().getTime()}` || 'https://via.placeholder.com/150';  // 確保圖片不使用快取
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },

    editProfile() {
      this.editData = { ...this.userData };
      this.isEditing = true;
    },
    // 上傳新圖片時，更新顯示的圖片
    onFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        this.editData.profile_image = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imageSrc = e.target.result;  // 即時顯示上傳的圖片
          console.log('Profile Image URL:', this.imageSrc);
        };
        reader.readAsDataURL(file);
      }
    },
    // 取消編輯
    cancelEdit() {
      this.isEditing = false;
      this.imageSrc = `${this.userData.profile_image}?${new Date().getTime()}` || 'https://via.placeholder.com/150';  // 還原圖片
    },
    // 保存用戶資料並上傳新照片
    async saveProfile() {
      try {
        const token = localStorage.getItem('frontend_token');  // 獲取 token

        const formData = new FormData();
        formData.append('username', this.editData.username);
        formData.append('email', this.editData.email);
        formData.append('phone', this.editData.phone);
        if (this.editData.profile_image) {
          formData.append('profile_image', this.editData.profile_image);  // 將照片附加到 FormData
        }

        // 更新個人資訊
        await axios.put('/api/frontend/profile/', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,  // 添加 Authorization 標頭
            'Content-Type': 'multipart/form-data'  // 設置適當的內容類型
          }
        });

        this.userData = { ...this.editData };
        this.isEditing = false;

        // 確保保存後的圖片正確顯示
        this.imageSrc = `${this.userData.profile_image}?${new Date().getTime()}` || 'https://via.placeholder.com/150';
        console.log('Saved Profile Image URL:', this.imageSrc);

        alert('個人資訊已更新');
      } catch (error) {
        console.error('Error saving profile:', error.response);
        alert('保存失敗');
      }
    }
  },
  mounted() {
    this.fetchUserProfile();
  }
};
</script>

<style scoped>
/* 這裡是你的樣式代碼 */
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 80vh;  
  padding-top: 0px;
}

.profile-card {
  background-color: white;
  border-radius: 10px;
  padding: 10px;
  width: 300px;
  height: 400px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-top: 0;
}

.profile-image img {
  border-radius: 50%;
  width: 150px;
  height: 150px;
}

.edit-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-height: 80vh;
  overflow-y: auto;
}

.button-container {
  display: flex;
  justify-content: space-between;
}

button.save {
  background-color: #4caf50;
  color: white;
}

button.cancel {
  background-color: #f44336;
  color: white;
}
</style>
