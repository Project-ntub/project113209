<template>
  <TopNavbar title="角色管理" />
  <div class="main-container">
    <!-- 遮罩層，用於控制模態框的背景 -->
    <div v-if="showCreateRoleModal || showEditRoleModal" class="modal-backdrop" @click="closeAllModals"></div>

    <div class="header">
      <!-- 新增角色按鈕，只有擁有新增角色權限的用戶能看到 -->
      <button id="add-role-btn" class="btn add-role-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_add)" @click="openCreateRoleModal">
        新增角色
      </button>
      <button class="btn" @click="navigateToRoleManagement">
        角色
      </button>
      <button class="btn" @click="navigateToModuleManagement">
        模組
      </button>
    </div>
    
    <!-- 選擇模組的下拉選單 -->
    <select id="chart-module-select" v-model="selectedModule" @change="filterRolesByModule">
      <option value="all">所有模組</option>
      <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
    </select>

    <!-- 角色表格 -->
    <div class="table-container">
      <table class="role-table">
        <thead>
          <tr>
            <th>角色名稱</th>
            <th>角色狀態</th>
            <th>用戶數</th>
            <th>角色成員</th>
            <th>模組</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in filteredRoles" :key="role.id" :data-module="role.module.id">
            <td>{{ role.name }}</td>
            <td>
              <!-- 狀態切換按鈕 -->
              <label class="switch">
                <input type="checkbox" :checked="role.is_active" @change="toggleStatus(role.id, !role.is_active)">
                <span class="slider"></span>
              </label>
            </td>
            <td>{{ role.users.length }}</td>
            <td>
              <!-- 用戶下拉選單顯示角色成員 -->
              <select v-model="role.selectedUser">
                <option v-for="user in role.users" :key="user.id" :value="user.id">{{ user.username }}</option>
              </select>
            </td>
            <td>{{ role.module_name ? role.module_name : '未知模組' }}</td>
            <td>
              <!-- 編輯角色按鈕 -->
              <button class="permissions-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_edit)" @click="openEditRoleModal(role.id)">編輯角色</button>
              <!-- 刪除角色按鈕 -->
              <button class="delete-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_delete)" @click="deleteRole(role.id)">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增角色與編輯角色的模態框 -->
    <RoleModal :isVisible="showCreateRoleModal" @close="closeCreateRoleModal">
      <RoleForm @role-saved="fetchRoles" @close="closeCreateRoleModal" />
    </RoleModal>
    <RoleModal :isVisible="showEditRoleModal" @close="closeEditRoleModal">
      <RoleForm :roleId="editingRoleId" @role-saved="fetchRoles" @close="closeEditRoleModal" />
    </RoleModal>
  </div>
</template>

<script>
import axios from '@/axios';
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import RoleModal from '@/components/backend/RoleModal.vue';
import RoleForm from '@/components/backend/RoleForm.vue';

export default {
  name: 'RoleManagement',
  components: {
    TopNavbar,
    RoleModal,
    RoleForm
  },
  data() {
    return {
      permissions: [], // 存放當前用戶的權限信息
      roles: [], // 所有角色的數據
      modules: [], // 所有模組的數據
      selectedModule: 'all', // 當前選中的模組
      showCreateRoleModal: false, // 控制新增角色模態框的顯示
      showEditRoleModal: false, // 控制編輯角色模態框的顯示
      editingRoleId: null // 當前正在編輯的角色ID
    };
  },
  computed: {
    // 根據選中的模組過濾角色
    filteredRoles() {
      if (this.selectedModule === 'all') {
        return this.roles;
      }
      return this.roles.filter(role => role.module == this.selectedModule);
    }
  },
  methods: {
    // 獲取所有角色
    fetchRoles() {
      axios.get('/api/backend/roles/')
        .then(response => {
          this.roles = response.data.map(role => ({
            ...role,
            selectedUser: role.users.length ? role.users[0].id : null
          }));
        })
        .catch(error => {
          console.error('Error fetching roles:', error);
        });
    },
    // 獲取所有模組
    fetchModules() {
      axios.get('/api/backend/modules/')
        .then(response => {
          this.modules = response.data.filter(module => !module.is_deleted);
        })
        .catch(error => {
          console.error('Error fetching modules:', error);
        });
    },
    // 獲取當前用戶的權限信息
    fetchUserPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          this.permissions = response.data;  // 使用回應的數據作為權限列表
        })
        .catch(error => {
          console.error('Error fetching permissions:', error);
        });
    },
    // 關閉所有模態框
    closeAllModals() {
      this.showCreateRoleModal = false;
      this.showEditRoleModal = false;
    },
    // 打開新增角色模態框
    openCreateRoleModal() {
      this.showCreateRoleModal = true;
    },
    // 關閉新增角色模態框
    closeCreateRoleModal() {
      this.showCreateRoleModal = false;
    },
    // 打開編輯角色模態框
    openEditRoleModal(roleId) {
      this.editingRoleId = roleId;
      this.showEditRoleModal = true;
    },
    // 關閉編輯角色模態框
    closeEditRoleModal() {
      this.showEditRoleModal = false;
      this.editingRoleId = null;
    },
    // 切換角色狀態
    toggleStatus(roleId, isActive) {
      axios.post(`/api/backend/toggle_role_status/${roleId}/`, { is_active: isActive })
        .then(response => {
          if (response.data.success) {
            this.fetchRoles(); // 刷新角色列表
          } else {
            alert('切換狀態失敗');
          }
        })
        .catch(error => {
          console.error('Error toggling status:', error);
          alert('切換狀態失敗');
        });
    },
    // 導航至角色管理頁面
    navigateToRoleManagement() {
      this.$router.push('/backend/role-management');
    },
    // 導航至模組管理頁面
    navigateToModuleManagement() {
      this.$router.push('/backend/module-management');
    },
    // 刪除角色
    deleteRole(roleId) {
      if (confirm('確定要刪除此角色嗎？')) {
        axios.post(`/api/backend/delete_role/${roleId}/`)
          .then(() => {
            this.fetchRoles(); // 刪除後重新獲取角色列表
          })
          .catch(error => {
            console.error('Error deleting role:', error);
            alert('刪除角色失敗');
          });
      }
    }
  },
  mounted() {
    this.fetchRoles(); // 初始獲取角色列表
    this.fetchModules(); // 初始獲取模組列表
    this.fetchUserPermissions(); // 初始獲取當前用戶權限信息
  }
};
</script>
<style scoped src="@/assets/css/backend/RoleManagement.css"></style>
