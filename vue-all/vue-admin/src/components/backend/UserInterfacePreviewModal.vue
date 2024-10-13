<template>
    <div class="modal-overlay">
      <div class="modal-content">
        <h3>前台介面預覽</h3>
        <button class="close-button" @click="$emit('close')">關閉</button>
  
        <!-- 部門職位和模組角色選擇 -->
        <div class="selection-container">
          <label for="division-select">選擇部門或模組:</label>
          <select id="division-select" v-model="selectedDivision" @change="fetchRolesOrPositions">
            <option value="department">依部門職位</option>
            <option value="role">依模組角色</option>
          </select>
        </div>
  
        <!-- 角色或職位選擇 -->
        <div v-if="selectedDivision === 'department'">
          <div>
            <label>選擇部門:</label>
            <select v-model="selectedDepartment" @change="fetchPositions">
              <option value="">選擇部門</option>
              <option v-for="department in departments" :key="department.id" :value="department.id">{{ department.name }}</option>
            </select>
          </div>
          <div>
            <label>選擇職位:</label>
            <select v-model="selectedPosition">
              <option value="">選擇職位</option>
              <option v-for="position in positions" :key="position.id" :value="position.id">{{ position.name }}</option>
            </select>
          </div>
        </div>
  
        <div v-if="selectedDivision === 'role'">
          <div>
            <label>選擇模組:</label>
            <select v-model="selectedModule" @change="fetchRoles">
              <option value="">選擇模組</option>
              <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
            </select>
          </div>
          <div>
            <label>選擇角色:</label>
            <select v-model="selectedRole">
              <option value="">選擇角色</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
        </div>
  
        <!-- 預覽顯示 -->
        <div class="frontend-preview">
          <component v-for="chart in roleOrPositionCharts" :is="chart" :key="chart" />
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';

  
  export default {
    name: 'UserInterfacePreviewModal',
    props: ['isVisible'],
    data() {
      return {
        selectedDivision: 'department',
        selectedModule: '',
        selectedRole: '',
        selectedDepartment: '',
        selectedPosition: '',
        modules: [],
        roles: [],
        departments: [],
        positions: []
      };
    },

    methods: {
      async fetchRolesOrPositions() {
        if (this.selectedDivision === 'department') {
          await this.fetchDepartments();
        } else {
          await this.fetchModules();
        }
      },
      async fetchModules() {
        try {
          const response = await axios.get('/api/backend/modules/');
          this.modules = response.data;
        } catch (error) {
          console.error('Error fetching modules:', error);
        }
      },
      async fetchRoles() {
        if (!this.selectedModule) return;
        try {
          const response = await axios.get(`/api/backend/get_roles_by_module/${this.selectedModule}/`);
          this.roles = response.data;
        } catch (error) {
          console.error('Error fetching roles:', error);
        }
      },
      async fetchDepartments() {
        try {
          const response = await axios.get('/api/backend/departments/');
          this.departments = response.data;
        } catch (error) {
          console.error('Error fetching departments:', error);
        }
      },
      async fetchPositions() {
        if (!this.selectedDepartment) return;
        try {
          const response = await axios.get(`/api/backend/get_positions_by_department/${this.selectedDepartment}/`);
          this.positions = response.data;
        } catch (error) {
          console.error('Error fetching positions:', error);
        }
      }
    },
    computed: {
      roleOrPositionCharts() {
        const chartsMap = {
          department: {
            '1': ['SalesChart', 'RevenueChart'], // 部門職位映射
            '2': ['InventoryChart']
          },
          role: {
            '1': ['SalesChart', 'InventoryChart'], // 模組角色映射
            '2': ['RevenueChart']
          }
        };
        if (this.selectedDivision === 'department') {
          return chartsMap.department[this.selectedPosition] || [];
        } else if (this.selectedDivision === 'role') {
          return chartsMap.role[this.selectedRole] || [];
        }
        return [];
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 80%;
    max-width: 600px;
  }
  
  .close-button {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 10px;
    cursor: pointer;
    border-radius: 5px;
  }
  
  .frontend-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
  }
  
  .frontend-preview > * {
    flex: 1 1 100%;
  }
  </style>
  