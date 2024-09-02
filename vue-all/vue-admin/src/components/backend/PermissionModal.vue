<template>
    <div v-if="isVisible" class="modal-overlay">
      <div class="modal-content">
        <!-- Modal header with close button -->
        <div class="modal-header">
          <h3>權限設定</h3>
          <button class="close-button" @click="closeModal">X</button>
        </div>
  
        <!-- Modal body -->
        <div class="modal-body">
          <!-- Checkbox for permissions -->
          <div class="checkbox-group">
            <label>
              <input type="checkbox" v-model="allUsers" @change="handleAllUsersChange" />
              所有使用者
            </label>
            <label>
              <input type="checkbox" v-model="custom" @change="handleCustomChange" />
              自訂
            </label>
          </div>
  
          <!-- Radio buttons for division type -->
          <div class="radio-group" v-if="custom">
            <label>
              <input type="radio" value="department" v-model="divisionType" />
              依部門職位
            </label>
            <label>
              <input type="radio" value="role" v-model="divisionType" />
              依模組角色
            </label>
          </div>
  
          <!-- Module and role selection -->
          <div v-if="custom && divisionType === 'department'">
            <div class="flex-container">
              <div class="dropdown-group">
                <!-- 部門選擇 -->
                <div>
                  <label>授權的部門</label>
                  <select v-model="selectedDepartment" @change="fetchPositions">
                    <option value="">選擇部門</option>
                    <option v-for="department in departments" :key="department.id" :value="department.id">{{ department.name }}</option>
                  </select>
                </div>
                <div>
                  <label>授權的職位</label>
                  <select v-model="selectedPosition">
                    <option value="">選擇職位</option>
                    <option v-for="position in positions" :key="position.id" :value="position.id">{{ position.name }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Module and role selection -->
          <div v-if="custom && divisionType === 'role'">
            <div class="flex-container">
              <div class="dropdown-group">
                <!-- 模組選擇 -->
                <div>
                  <label>授權的模組</label>
                  <select v-model="selectedModule" @change="fetchRoles">
                    <option value="">選擇模組</option>
                    <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
                  </select>
                </div>
                <div>
                  <label>授權的角色</label>
                  <select v-model="selectedRole">
                    <option value="">選擇角色</option>
                    <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
                  </select>
                </div>
  
                <!-- New module and role inputs -->
                <div>
                  <input type="text" v-model="newModuleName" placeholder="輸入新模組名稱" />
                  <button type="button" @click="addModule">新增模組</button>
                </div>
                <div>
                  <input type="text" v-model="newRoleName" placeholder="輸入新角色名稱" />
                  <button type="button" @click="addRole">新增角色</button>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Modal footer with buttons -->
        <div class="modal-footer">
          <button @click="closeModal">取消</button>
          <button @click="savePermissions">保存</button>
        </div>
      </div>
    </div>
  </template>  
  
  <script>
  import axios from 'axios';
  
  export default {
    props: ['isVisible'],
    data() {
      return {
        allUsers: false,
        custom: false,
        divisionType: '', // Added to track the selection type
        selectedModule: '',
        selectedRole: '',
        selectedDepartment: '', // Added department selection
        selectedPosition: '',   // Added position selection
        modules: [],
        roles: [],
        departments: [], // Added department data
        positions: [],   // Added position data
        newModuleName: '',  // For tracking new module name
        newRoleName: '',    // For tracking new role name
      };
    },
    methods: {
      closeModal() {
        this.$emit('close');
      },
      savePermissions() {
        // Handle saving logic
        this.closeModal();
      },
      handleAllUsersChange() {
        if (this.allUsers) {
          this.custom = false;
          this.divisionType = ''; // Reset the division type if "All Users" is selected
        }
      },
      handleCustomChange() {
        if (this.custom) {
          this.allUsers = false;
        }
      },
      async fetchData() {
        try {
          const modulesResponse = await axios.get('/api/backend/modules/');
          this.modules = modulesResponse.data;
  
          const departmentsResponse = await axios.get('/api/backend/departments/'); // Fetch department data
          this.departments = departmentsResponse.data;
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      },
      async fetchRoles() {
        if (!this.selectedModule) {
          this.roles = [];
          return;
        }
        try {
          const rolesResponse = await axios.get(`/api/backend/get_roles_by_module/${this.selectedModule}/`);
          this.roles = rolesResponse.data;
        } catch (error) {
          console.error('Error fetching roles:', error);
        }
      },
      async fetchPositions() {
            if (!this.selectedDepartment) {
                this.positions = [];
                return;
            }
            try {
                const positionsResponse = await axios.get(`/api/backend/get_positions_by_department/${this.selectedDepartment}/`);
                console.log('Positions fetched:', positionsResponse.data); // 打印回應數據
                this.positions = positionsResponse.data;
            } catch (error) {
                console.error('Error fetching positions:', error);
            }
        },
      async addModule() {
        try {
          const response = await axios.post('/api/backend/modules/', { name: this.newModuleName });
          this.modules.push(response.data);
          this.newModuleName = ''; // Clear new module name input
          alert('模組新增成功');
        } catch (error) {
          console.error('Error adding module:', error);
          alert('模組新增失敗');
        }
      },
      async addRole() {
        if (!this.selectedModule) {
          alert('請先選擇模組');
          return;
        }
        try {
          const response = await axios.post('/api/backend/roles/', { name: this.newRoleName, module: this.selectedModule });
          this.roles.push(response.data);
          this.newRoleName = ''; // Clear new role name input
          alert('角色新增成功');
        } catch (error) {
          console.error('Error adding role:', error);
          alert('角色新增失敗');
        }
      }
    },
    mounted() {
      this.fetchData(); // Fetch data when component loads
    },
  };
  </script>
  
  <style scoped src="@/assets/css/backend/PermissionModal.css"></style>
  