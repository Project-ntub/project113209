<template>
  <div class="role-form-container">
    <form @submit.prevent="saveRole">
      <div class="form-group">
        <label for="role-name">角色名稱</label>
        <input type="text" v-model="localRole.name" id="role-name" required />
      </div>
      <div class="form-group">
        <label for="role-users">角色成員</label>
        <div class="member-container">
          <div v-for="(userId, index) in localRole.users" :key="index" class="member-item">
            <select v-model="localRole.users[index]">
              <option value="">-- 選擇成員 --</option>
              <option v-for="user in availableUsers" :key="user.id" :value="user.id">{{ user.username }}</option>
            </select>
            <button type="button" @click="removeMember(index)">-</button>
          </div>
          <button type="button" @click="addMember">+</button>
        </div>
      </div>
      <div class="form-group">
        <label for="role-is-active">角色狀態</label>
        <input type="checkbox" v-model="localRole.is_active" id="role-is-active" />
      </div>
      <div class="form-group">
        <label for="role-module">模組</label>
        <select v-model="localRole.module" id="role-module" required>
          <option value="">-- 選擇模組 --</option>
          <option v-for="module in availableModules" :key="module.id" :value="module.id">{{ module.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>角色權限</label>
        <table>
          <thead>
            <tr>
              <th>功能</th>
              <th>新增</th>
              <th>查詢</th>
              <th>檢視</th>
              <th>修改</th>
              <th>刪除</th>
              <th>列印</th>
              <th>匯出</th>
              <th>維護</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="permission in rolePermissions" :key="permission.id">
              <td>{{ permission.permission_name }}</td>
              <td><input type="checkbox" v-model="permission.can_add" /></td>
              <td><input type="checkbox" v-model="permission.can_query" /></td>
              <td><input type="checkbox" v-model="permission.can_view" /></td>
              <td><input type="checkbox" v-model="permission.can_edit" /></td>
              <td><input type="checkbox" v-model="permission.can_delete" /></td>
              <td><input type="checkbox" v-model="permission.can_print" /></td>
              <td><input type="checkbox" v-model="permission.can_export" /></td>
              <td><input type="checkbox" v-model="permission.can_maintain" /></td>
              <td>
                <button type="button" @click="deletePermission(permission.id)">刪除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <button type="button" @click="navigateToAddPermission" :disabled="!localRole.id">
          新增權限
        </button>
        <span v-if="!localRole.id" class="help-text">請先保存角色以獲取角色 ID</span>
      </div>
      <button type="submit" class="btn">{{ isEdit ? "保存變更" : "新增" }}</button>
      <button type="button" class="btn secondary" @click="cancel">取消</button>
    </form>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'RoleForm',
  props: {
    roleId: {
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      localRole: {
        name: '',
        module: '',
        users: [],
        is_active: false
      },
      availableUsers: [],
      availableModules: [],
      rolePermissions: [],
      isEdit: false
    };
  },
  methods: {
    async loadRole(roleId) {
      try {
        const response = await axios.get(`/api/backend/roles/${roleId}/`);
        const role = response.data;

        // 將響應的數據填充到 localRole
        this.localRole = {
          id: role.id,
          name: role.name,
          module: role.module ? role.module : '',
          users: role.users.map(user => user.id),
          is_active: role.is_active
        };

        // 加載權限數據
        await this.fetchRolePermissions(roleId);
      } catch (error) {
        console.error('Error loading role:', error.response ? error.response.data : error.message);
      }
    },
    async fetchRolePermissions(roleId) {
      try {
        const response = await axios.get(`/api/backend/role_permissions/?role_id=${roleId}`);
        this.rolePermissions = response.data;
      } catch (error) {
        console.error('Error fetching role permissions:', error);
      }
    },
    async saveRole() {
        if (!this.localRole.name) {
            alert('請輸入角色名稱');
            return;
        }
        if (!this.localRole.module) {
            alert('請選擇模組');
            return;
        }
        try {
            const roleData = {
                ...this.localRole,
                users: this.localRole.users,
                permissions: this.rolePermissions 
            };
            const response = this.isEdit
                ? await axios.put(`/api/backend/roles/${this.localRole.id}/`, roleData)
                : await axios.post('/api/backend/roles/', roleData);

            if (response.status === 200 || response.status === 201) {
                console.log('Response data:', response.data);
                alert('保存成功');
                
                // 只需發出 'role-saved' 事件，傳遞 roleId
                this.$emit('role-saved', response.data.id);
            } else {
                alert('保存失敗');
            }
        } catch (error) {
            console.error('Error saving role:', error.response ? error.response.data : error.message);
            alert('保存失敗：' + (error.response && error.response.data && error.response.data.error ? error.response.data.error : error.message));
        }
    },
    async fetchModules() {
      try {
        const response = await axios.get('/api/backend/modules/');
        this.availableModules = response.data;
      } catch (error) {
        console.error('Error fetching modules:', error);
      }
    },
    addMember() {
      this.localRole.users.push('');
    },
    removeMember(index) {
      this.localRole.users.splice(index, 1);
    },
    cancel() {
      this.$router.push('/backend/role-management');
    },
    async fetchUsers() {
      try {
        const response = await axios.get('/api/backend/users/');
        this.availableUsers = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },
    navigateToAddPermission() {
      if (this.localRole.id) {
        this.$router.push({ name: 'BackendRolePermissions', params: { roleId: this.localRole.id } });
      } else {
        alert('請先保存角色以獲取角色 ID');
      }
    },
    async deletePermission(permissionId) {
      try {
        const response = await axios.delete(`/api/backend/role_permissions/${permissionId}/`);
        if (response.status === 204) {
          // 刪除成功後從列表中移除相應權限
          this.rolePermissions = this.rolePermissions.filter(permission => permission.id !== permissionId);
          alert('刪除成功');
        } else {
          alert('刪除失敗');
        }
      } catch (error) {
        console.error('Error deleting permission:', error.response ? error.response.data : error.message);
        alert('刪除失敗：' + (error.response && error.response.data && error.response.data.error ? error.response.data.error : error.message));
      }
    }
  },
  async mounted() {
    window.scrollTo(0, 0);
    await this.fetchModules();
    await this.fetchUsers();
  },
  watch: {
    roleId: {
      handler(newVal) {
        if (newVal) {
          this.isEdit = true;
          this.loadRole(newVal);
        } else {
          this.isEdit = false;
          // 重置 localRole
          this.localRole = {
            name: '',
            module: '',
            users: [],
            is_active: false
          };
          this.rolePermissions = [];
        }
      },
      immediate: true,
    },
  },
};
</script>

<style scoped>
.role-form-container {
  width: 100%;
  max-width: 100%;
  margin: 20px auto;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: auto; 
}

.form-group input,
.form-group select,
.btn {
  font-size: 1.2em;
  padding: 10px;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1.2em; /* 增大表格字體 */
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
}

.help-text {
  color: #888;
  margin-left: 10px;
  font-size: 0.9em;
}

.btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.btn:hover {
  background-color: #0056b3;
}

.member-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.member-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.member-item select {
  flex-grow: 1;
  font-size: 1.2em;
}

.member-item button {
  margin-left: 10px;
  padding: 10px;
  font-size: 1em;
}
</style>
