<template>
  <div class="container">
    <h2>新增權限</h2>
    <div class="form-group">
      <label for="permission-name">功能名稱</label>
      <input type="text" v-model="newPermission.permission_name" id="permission-name" required />
    </div>
    <div class="form-group">
      <h3>權限</h3>
      <div class="checkbox-container">
        <label><input type="checkbox" v-model="newPermission.can_add" /> 新增</label>
        <label><input type="checkbox" v-model="newPermission.can_query" /> 查詢</label>
        <label><input type="checkbox" v-model="newPermission.can_view" /> 檢視</label>
        <label><input type="checkbox" v-model="newPermission.can_edit" /> 修改</label>
        <label><input type="checkbox" v-model="newPermission.can_delete" /> 刪除</label>
        <label><input type="checkbox" v-model="newPermission.can_print" /> 列印</label>
        <label><input type="checkbox" v-model="newPermission.can_export" /> 匯出</label>
        <label><input type="checkbox" v-model="newPermission.can_maintain" /> 維護</label>
      </div>
    </div>
    <div class="btn-container">
      <button @click="savePermission" class="btn">新增</button>
      <button @click="cancelPermission" class="btn secondary">取消</button>
    </div>
  </div>
</template>

<script>
import axios from '@/axios'; 
import '@/assets/css/backend/RolePermissions.css';  // 引入CSS文件

export default {
  data() {
    return {
      newPermission: {
        permission_name: '',
        can_add: false,
        can_query: false,
        can_view: false,
        can_edit: false,
        can_delete: false,
        can_print: false,
        can_export: false,
        can_maintain: false
      }
    };
  },
  methods: {
    async savePermission() {
      try {
        const response = await axios.post('/api/backend/role_permissions/', {
          ...this.newPermission,
          role: this.$route.params.roleId
        });
        if (response.status >= 200 && response.status < 300) {
          alert('新增成功');
          this.$emit('permission-saved');  // 通知父組件權限已經保存
          this.$router.back();  // 返回到上一个页面
        } else {
          alert('新增失敗');
        }
      } catch (error) {
        console.error('Error saving permission:', error.response ? error.response.data : error.message);
        alert(`新增失敗: ${error.response ? error.response.data.detail : error.message}`);
      }
    },
    cancelPermission() {
      this.$emit('permission-cancelled');  // 通知父組件取消了新增權限
      this.$router.back();  // 返回到上一个页面
    }
  }
};
</script>
