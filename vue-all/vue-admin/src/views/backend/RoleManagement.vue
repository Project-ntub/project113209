<template>
  <TopNavbar title="角色管理" />
  <div class="main-container">
    <div v-if="showCreateRoleModal || showEditRoleModal" class="modal-backdrop" @click="closeAllModals"></div>

    <div class="header">
      <button id="add-role-btn" class="btn add-role-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_add)" @click="openCreateRoleModal">
        新增角色
      </button>
      <button class="btn" @click="navigateToRoleManagement">角色</button>
      <button class="btn" @click="navigateToModuleManagement">模組</button>
    </div>

    <select id="chart-module-select" v-model="selectedModule" @change="filterRolesByModule">
      <option value="all">所有模組</option>
      <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
    </select>

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
              <label class="switch">
                <input type="checkbox" :checked="role.is_active" @change="toggleStatus(role.id, !role.is_active)">
                <span class="slider"></span>
              </label>
            </td>
            <td>{{ role.users.length }}</td>
            <td>
              <select v-model="role.selectedUser">
                <option v-for="user in role.users" :key="user.id" :value="user.id">{{ user.username }}</option>
              </select>
            </td>
            <td>{{ role.module_name ? role.module_name : '未知模組' }}</td>
            <td>
              <button class="permissions-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_edit)" @click="openEditRoleModal(role.id)">編輯角色</button>
              <button class="delete-btn" v-if="permissions.find(perm => perm.permission_name === '角色管理' && perm.can_delete)" @click="deleteRole(role.id)">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <RoleModal :isVisible="showCreateRoleModal" @close="closeCreateRoleModal" class="centered-modal">
      <RoleForm @role-saved="fetchRoles" @close="closeCreateRoleModal" />
    </RoleModal>
    <RoleModal :isVisible="showEditRoleModal" @close="closeEditRoleModal" class="centered-modal">
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
      permissions: [],
      roles: [],
      modules: [],
      selectedModule: 'all',
      showCreateRoleModal: false,
      showEditRoleModal: false,
      editingRoleId: null
    };
  },
  computed: {
    filteredRoles() {
      if (this.selectedModule === 'all') {
        return this.roles;
      }
      return this.roles.filter(role => role.module == this.selectedModule);
    }
  },
  methods: {
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
    fetchModules() {
      axios.get('/api/backend/modules/')
        .then(response => {
          this.modules = response.data.filter(module => !module.is_deleted);
        })
        .catch(error => {
          console.error('Error fetching modules:', error);
        });
    },
    fetchUserPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          this.permissions = response.data;
        })
        .catch(error => {
          console.error('Error fetching permissions:', error);
        });
    },
    closeAllModals() {
      this.showCreateRoleModal = false;
      this.showEditRoleModal = false;
    },
    openCreateRoleModal() {
      this.showCreateRoleModal = true;
    },
    closeCreateRoleModal() {
      this.showCreateRoleModal = false;
    },
    openEditRoleModal(roleId) {
      this.editingRoleId = roleId;
      this.showEditRoleModal = true;
    },
    closeEditRoleModal() {
      this.showEditRoleModal = false;
      this.editingRoleId = null;
    },
    toggleStatus(roleId, isActive) {
      axios.post(`/api/backend/toggle_role_status/${roleId}/`, { is_active: isActive })
        .then(response => {
          if (response.data.success) {
            this.fetchRoles();
          } else {
            alert('切換狀態失敗');
          }
        })
        .catch(error => {
          console.error('Error toggling status:', error);
          alert('切換狀態失敗');
        });
    },
    navigateToRoleManagement() {
      this.$router.push('/backend/role-management');
    },
    navigateToModuleManagement() {
      this.$router.push('/backend/module-management');
    },
    deleteRole(roleId) {
      if (confirm('確定要刪除此角色嗎？')) {
        axios.post(`/api/backend/delete_role/${roleId}/`)
          .then(() => {
            this.fetchRoles();
          })
          .catch(error => {
            console.error('Error deleting role:', error);
            alert('刪除角色失敗');
          });
      }
    }
  },
  mounted() {
    this.fetchRoles();
    this.fetchModules();
    this.fetchUserPermissions();
  }
};
</script>

<style scoped src="@/assets/css/backend/RoleManagement.css"></style>
