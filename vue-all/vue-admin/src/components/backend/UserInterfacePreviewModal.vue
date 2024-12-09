<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <!-- 頂部區域 -->
      <div class="modal-header">
        <h3>前台介面預覽</h3>
        <button class="close-button" @click="$emit('close')">關閉</button>
      </div>

      <!-- 選擇區域 -->
      <div class="selection-area">
        <div class="select-group">
          <label>選擇模組:</label>
          <select v-model="selectedModule" @change="fetchRoles">
            <option value="">選擇模組</option>
            <option v-for="module in modules" :key="module.id" :value="module.id">
              {{ module.name }}
            </option>
          </select>
        </div>

        <div class="select-group" v-if="selectedModule">
          <label>選擇角色:</label>
          <select v-model="selectedRole" @change="fetchRoleCharts">
            <option value="">選擇角色</option>
            <option v-for="role in roles" :key="role.id" :value="role.id">
              {{ role.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- 圖表預覽區域 -->
      <div class="frontend-preview" v-if="selectedRole">
        <div v-if="charts.length > 0" class="charts-container">
          <div v-for="chart in charts" :key="chart.id" class="chart-item">
            <ChartContainer 
              :chartConfig="chart" 
              :isFrontend="true"
              :canExport="false"
              :canDelete="false"
              :canEdit="false"
            />
          </div>
        </div>
        <div v-else class="no-charts-message">
          該角色暫無可用圖表
        </div>
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
  mounted() {
    this.fetchModules();
  },
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
        this.charts = [];
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
            // 處理過濾條件
            const filterConditions = typeof chart.filter_conditions === 'string' 
              ? JSON.parse(chart.filter_conditions || '{}') 
              : chart.filter_conditions || {};

            // 根據圖表類型處理不同的數據欄位
            let y_field = null;
            let y_fields = null;

            if (chart.chartType === 'multi_line' || chart.chartType === 'combo') {
              y_fields = chart.yAxisFields || [];
            } else {
              y_field = chart.yAxisField;
            }

            // 發送請求獲取圖表數據
            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.dataSource,
              x_field: chart.xAxisField,
              y_field: y_field,
              y_fields: y_fields,
              chart_type: chart.chartType?.toLowerCase() || 'bar',
              filter_conditions: filterConditions,
              join_fields: chart.join_fields || []
            });

            // 確保返回的數據格式正確
            return {
              ...chart,
              chartType: chart.chartType?.toLowerCase() || 'bar',
              x_data: dataResponse.data.x_data || [],
              y_data: dataResponse.data.y_data || [],
              last_updated: dataResponse.data.last_updated,
              // 添加必要的配置項
              can_export: false, // 預覽模式下禁用導出
              can_delete: false, // 預覽模式下禁用刪除
              can_edit: false,   // 預覽模式下禁用編輯
              error: null        // 初始化錯誤狀態
            };
          } catch (error) {
            console.error(`Error fetching data for chart ID ${chart.id}:`, error);
            return {
              ...chart,
              chartType: chart.chartType?.toLowerCase() || 'bar',
              x_data: [],
              y_data: [],
              last_updated: null,
              can_export: false,
              can_delete: false,
              can_edit: false,
              error: '無法獲取數據'
            };
          }
        }));

        console.log('Processed charts:', this.charts);
      } catch (error) {
        console.error('Error fetching charts for role:', error);
        this.charts = [];
      }
    },
  }
};
</script>

<style>
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

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
  width: 95%;  /* 稍微增加寬度 */
  max-width: 1400px;  /* 增加最大寬度 */
  height: 95vh;  /* 使用視窗高度而不是最大高度 */
  display: grid;  /* 改用 grid 布局 */
  grid-template-rows: auto auto auto 1fr;  /* 為不同區塊分配空間 */
  gap: 20px;
  overflow: hidden;  /* 改為 hidden，讓內部滾動 */
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
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
  width: 100%;
}

.frontend-preview > * {
  flex: 1 1 100%;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  width: 100%;
  height: 100%;
  overflow-y: auto;  /* 添加滾動條 */
  padding: 10px;
}

.chart-item {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px;
  height: 400px;  /* 固定高度 */
  display: flex;  /* 使用 flex 布局 */
  flex-direction: column;
}

.no-charts-message {
  text-align: center;
  padding: 20px;
  color: #666;
  font-style: italic;
}

.selection-area {
  display: flex;
  gap: 20px;
  padding: 15px 0;
}

.select-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  min-width: 200px;
}

label {
  font-weight: 500;
  color: #333;
}
</style>
