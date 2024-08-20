<template>
  <div class="account-settings-page">
    <div class="main-panel">
      <div class="container">
        <div class="account-settings">
          <!-- 用户头像 -->
          <img class="profile-pic" src="https://via.placeholder.com/100" alt="Profile Picture">
          <!-- 用户名 -->
          <h3>wang</h3>
          <!-- 修改密码链接 -->
          <router-link to="/frontend/changepassword" class="setting-option">
            <img src="https://img.icons8.com/ios-filled/50/000000/lock.png" alt="修改密碼">
            修改密碼
          </router-link>
          <!-- 偏好设置链接 -->
          <router-link to="/frontend/preferences" class="setting-option">
            <img src="https://img.icons8.com/ios-filled/50/000000/settings.png" alt="偏好設定">
            偏好設定
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AccountSettings',
};
</script>

<style scoped src="@/assets/css/frontend/AccountSettings.css"></style>
