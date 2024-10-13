<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <button class="zoom-icon" @click="openZoomModal"><i class="fas fa-search-plus"></i></button>
          <div v-if="showMenu" class="menu">
            <template v-if="!isFrontend">
              <button @click="editChart">編輯圖表</button>
              <button v-if="canExport" @click="deleteChart">刪除圖表</button>
            </template>
            <div v-if="canExport" class="export-button">
              <button @click="exportChart('csv')">匯出 CSV</button>
              <button @click="exportChart('excel')">匯出 Excel</button>
              <button @click="exportChart('pdf')">匯出 PDF</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Plotly Chart 組件處理渲染 -->
      <PlotlyChart :chartConfig="localChartConfig" />
      
      <!-- 查看圖表的視窗 -->
      <div v-if="isZoomModalVisible" class="zoom-modal-overlay" @click.self="closeZoomModal">
        <div class="zoom-modal-content">
          <PlotlyChart :chartConfig="localChartConfig" />
          <button class="close-btn" @click="closeZoomModal">×</button>
        </div>
      </div>
    </div>
    
    <!-- 編輯圖表的視窗 -->
    <ChartModal 
      v-if="!isFrontend && isEditModalVisible" 
      :isEditing="true" 
      :chartId="localChartConfig.id" 
      :fetchChartConfig="fetchChartConfigMethod"
      @close="closeEditModal" 
    />
  </div>
</template>

<script>
import axios from 'axios';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartModal from '@/components/backend/ChartModal.vue';

export default {
  components: {
    PlotlyChart,
    ChartModal
  },
  props: {
    chartConfig: Object,
    isFrontend: Boolean,
    canExport: Boolean,
    canDelete: Boolean
  },
  data() {
    return {
      showMenu: false,
      isZoomModalVisible: false,
      isEditModalVisible: false,
      localChartConfig: { ...this.chartConfig },
    };
  },
  mounted() {
    this.fetchUserPermissions();
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    openZoomModal() {
      this.isZoomModalVisible = true;
    },
    closeZoomModal() {
      this.isZoomModalVisible = false;
    },
    editChart() {
      this.isEditModalVisible = true;
      this.showMenu = false;
    },
    closeEditModal() {
      this.isEditModalVisible = false;
    },
    async deleteChart() {
      if (!this.localChartConfig.id) {
        alert('圖表ID無效，無法刪除');
        return;
      }
      const confirmation = confirm('確定要隱藏此圖表嗎？');
      if (confirmation) {
        try {
          await axios.post(`/api/backend/delete-chart/${this.localChartConfig.id}/`);
          alert('圖表已被隱藏');
          this.$emit('reload-charts');
        } catch (error) {
          console.error('隱藏圖表時出錯:', error);
          alert('隱藏失敗，請稍後再試。');
        }
      }
    },
    updateChartConfig(updatedConfig) {
      this.localChartConfig = updatedConfig;
    },
    async exportChart(format) {
      if (!this.localChartConfig.xAxisField || !this.localChartConfig.yAxisField) {
        alert('圖表配置無效，無法導出！');
        return;
      }

      try {
        const response = await axios.post('/api/backend/export-data/', {
          chartConfig: this.localChartConfig, // 確保傳遞完整的 chartConfig
          format: format
        }, { responseType: 'blob' });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.localChartConfig.name || 'exported-file'}.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error('匯出數據時出錯:', error);
        alert('匯出失敗，請檢查數據並重試。');
      }
    },
    async fetchChartConfigMethod(chartId) {
      if (!chartId) {
        console.error('chartId is undefined');
        alert('無效的圖表 ID，無法加載圖表配置');
        return null;
      }
      try {
        const response = await axios.get(`/api/backend/charts/${chartId}/`);
        const data = response.data;

        this.updateChartConfig({
          chartType: data.chart_type,
          name: data.name,
          dataSource: data.data_source,
          xAxisField: data.x_axis_field,
          yAxisField: data.y_axis_field,
          filterConditions: JSON.stringify(data.filter_conditions || '{}'),
          x_data: data.x_data || [],
          y_data: data.y_data || []
        });
        return data;
      } catch (error) {
        console.error('加載圖表配置時發生錯誤:', error);
        alert('加載圖表配置時發生錯誤，請稍後再試');
        return null;
      }
    },
    fetchUserPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          const permissions = response.data;
          console.log('User permissions:', permissions);
          // 假設每個權限都有 can_export 和 can_delete 權限
          const exportPermission = permissions.find(perm => perm.permission_name === this.localChartConfig.name);
          this.canExport = exportPermission ? exportPermission.can_export : false;
          this.canDelete = exportPermission ? exportPermission.can_delete : false;
        })
        .catch(error => {
          console.error('無法獲取權限:', error);
        });
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-header {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10;
}

.menu-button {
  position: relative;
  z-index: 11;
}

.menu-icon, .zoom-icon {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  color: black;
  padding: 8px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 50%;
  margin-right: 5px;
}

.menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #3498db;
  border: 1px solid #2980b9;
  border-radius: 5px;
  width: 150px;
  z-index: 12;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.menu button {
  display: block;
  width: 100%;
  padding: 8px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  color: white;
}

.menu button:hover {
  background-color: #2980b9;
}

.zoom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.zoom-modal-content {
  position: relative;
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 90%;
  max-width: 1200px;
  height: 90%;
  overflow: auto;
}

.plotly-chart {
  width: 100%;
  height: 100%;
}

.close-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.5);
  border: none;
  font-size: 2rem;
  cursor: pointer;
  border-radius: 50%;
  padding: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0,3);
}
</style>
