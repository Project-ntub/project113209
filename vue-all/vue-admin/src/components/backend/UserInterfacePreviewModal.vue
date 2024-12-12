<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>前台介面預覽</h3>
      <button class="close-button" @click="$emit('close')">關閉</button>

      <!-- 模組選擇 -->
      <div>
        <label>選擇模組:</label>
        <select v-model="selectedModule" @change="fetchRoles">
          <option value="">選擇模組</option>
          <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
        </select>
      </div>

      <!-- 角色選擇 -->
      <div v-if="selectedModule">
        <label>選擇角色:</label>
        <select v-model="selectedRole" @change="fetchRoleCharts">
          <option value="">選擇角色</option>
          <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
        </select>
      </div>

      <!-- 預覽顯示 -->
      <div class="frontend-preview" v-if="selectedRole && charts.length > 0">
        <ChartContainer 
          v-for="chart in charts" 
          :key="chart.id" 
          :chartConfig="chart" 
          :isFrontend="true" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ChartContainer from '@/Charts/ChartContainer.vue';

export default {
  name: 'UserInterfacePreviewModal',
  components: { ChartContainer },
  data() {
    return {
      selectedModule: '',
      selectedRole: '',
      modules: [],
      roles: [],
      charts: [],
    };
  },
  methods: {
    async fetchModules() {
      try {
        const response = await axios.get('/api/backend/modules/get_modules/');
        this.modules = response.data;
      } catch (error) {
        console.error('Error fetching modules:', error);
      }
    },
    async fetchRoles() {
      if (!this.selectedModule) {
        this.roles = [];
        this.selectedRole = '';
        this.charts = [];
        return;
      }
      try {
        const response = await axios.get(`/api/backend/roles/get_roles_by_module/${this.selectedModule}/`);
        this.roles = response.data;
        // 重置角色和圖表
        this.selectedRole = '';
        this.charts = [];
      } catch (error) {
        console.error('Error fetching roles:', error);
      }
    },
    async fetchRoleCharts() {
      if (!this.selectedRole) {
        this.charts = []; // 清空圖表數據
        return;
      }
      try {
        const response = await axios.get(`/api/backend/charts/preview_role/`, {
          params: { role_id: this.selectedRole }
        });
        const chartConfigs = response.data;
        console.log('Received chart configurations:', chartConfigs);

        // 為每個圖表獲取數據
        this.charts = await Promise.all(chartConfigs.map(async (chart) => {
          try {
            const filterConditions = typeof chart.filter_conditions === 'string' 
              ? JSON.parse(chart.filter_conditions || '{}') 
              : chart.filter_conditions || {};

            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.dataSource,
              x_field: chart.xAxisField,
              y_field: chart.yAxisField,
              filter_conditions: filterConditions,
              join_fields: chart.join_fields || [],
              chart_type: chart.chartType || 'bar'
            });

            return {
              ...chart,
              x_data: dataResponse.data.x_data,
              y_data: dataResponse.data.y_data,
              last_updated: dataResponse.data.last_updated,
            };
          } catch (error) {
            console.error(`Error fetching data for chart ID ${chart.id}:`, error);
            return {
              ...chart,
              x_data: [],
              y_data: [],
              last_updated: null,
              error: '無法獲取數據',
            };
          }
        }));

      } catch (error) {
        console.error('Error fetching charts for role:', error);
      }
    },
  },
  mounted() {
    this.fetchModules();
  },
};
</script>

<style>
.modal-overlay {
  position: fixed;
  z-index: 9999;  /* 確保模態框在最上層 */
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
  max-width: 800px;  /* 增加寬度以適應更多內容 */
  max-height: 80vh;
  overflow-y: auto;
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
