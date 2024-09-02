<template>
  <TopNavbar title="模組管理" />
  <div class="container" :class="{ shifted: isSidebarActive }">
    <div class="header">
      <div class="btn-group">
        <button id="add-module-btn" class="btn add-module-btn" @click="openCreateModuleModal">新增模組</button>
        <button class="btn" @click="navigateToRoleManagement">角色</button>
        <button class="btn" @click="navigateToModuleManagement">模組</button>
      </div>
    </div>
      
    <table class="module-table">
      <thead>
        <tr>
          <th>模組名稱</th>
          <th>用戶數</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="module in modules" :key="module.id">
          <td>{{ module.name }}</td>
          <td>{{ getUserCount(module.id) }}</td>
          <td>
            <button class="edit-btn" @click="openEditModuleModal(module.id, module.name)">編輯</button>
            <button class="delete-btn" @click="deleteModule(module.id)">刪除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <ModuleForm v-if="showCreateModuleModal" @close="closeCreateModuleModal" @create="createModule" />
    <ModuleForm v-if="showEditModuleModal" :moduleId="editModuleId" :moduleName="editModuleName" @close="closeEditModuleModal" @edit="editModule" />
  </div>
</template>

<script>
import axios from '@/axios'; 
import TopNavbar from '@/components/frontend/TopNavbar.vue'; // 引入前台的TopNavbar组件
import ModuleForm from '@/components/backend/ModuleForm.vue';

export default {
  name: "ModuleManagement",
  components: {
    TopNavbar,
    ModuleForm,
  },
  data() {
    return {
      modules: [],
      showCreateModuleModal: false,
      showEditModuleModal: false,
      newModuleName: "",
      editModuleName: "",
      editModuleId: null,
      isSidebarActive: false
    };
  },
  methods: {
    async loadModules() {
      try {
        const response = await axios.get('/api/backend/modules/');
        console.log('Modules from backend:', response.data);
        this.modules = response.data.filter(module => !module.is_deleted) || [];
      } catch (error) {
        console.error('Error fetching modules:', error.response ? error.response.data : error.message);
      }
    },
    openCreateModuleModal() {
      this.showCreateModuleModal = true;
    },
    closeCreateModuleModal() {
      this.showCreateModuleModal = false;
    },
    async createModule(newModule) {
      try {
        const response = await axios.post('/api/backend/modules/', newModule);
        if (response.status === 201) {
          this.loadModules();
          this.closeCreateModuleModal();
          alert("新增模組成功");
        } else {
          alert("新增模組失敗");
        }
      } catch (error) {
        console.error('Error creating module:', error.response ? error.response.data : error.message);
        alert("新增模組失敗");
      }
    },
    openEditModuleModal(id, name) {
      this.editModuleId = id;
      this.editModuleName = name;
      this.showEditModuleModal = true;
    },
    closeEditModuleModal() {
      this.showEditModuleModal = false;
    },
    async editModule(updatedModule) {
      try {
        const response = await axios.put(`/api/backend/modules/${this.editModuleId}/`, updatedModule);
        if (response.status === 200) {
          this.loadModules();
          this.closeEditModuleModal();
          alert("編輯模組成功");
        } else {
          alert("編輯模組失敗");
        }
      } catch (error) {
        console.error('Error editing module:', error.response ? error.response.data : error.message);
        alert("編輯模組失敗");
      }
    },
    async deleteModule(id) {
      try {
        const response = await axios.delete(`/api/backend/modules/${id}/`);
        console.log('Delete response:', response);
        if (response.status === 204) {
          this.loadModules();
          alert("刪除成功");
        } else {
          alert("刪除模組失敗");
          console.error('Error deleting module:', response.data.message);
        }
      } catch (error) {
        console.error('Error deleting module:', error.response ? error.response.data : error.message);
        alert("刪除模組失敗");
      }
    },
    navigateToRoleManagement() {
      this.$router.push('/backend/role-management');
    },
    navigateToModuleManagement() {
      this.$router.push('/backend/module-management');
    },
    getUserCount(moduleId) {
      const module = this.modules.find(m => m.id === moduleId);
      return module ? module.user_count : 0;
    },
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
  },
  created() {
    this.loadModules();
  }
};
</script>

<style scoped src="@/assets/css/backend/ModuleManagement.css"></style>
