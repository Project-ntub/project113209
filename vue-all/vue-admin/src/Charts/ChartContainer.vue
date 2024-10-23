<!-- src/Charts/ChartContainer.vue -->
<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <button class="zoom-icon" @click="openZoomModal">
            <font-awesome-icon icon="search-plus" />
          </button>
          <div v-if="showMenu" class="menu">
            <div v-if="!isFrontend">
                <button v-if="localCanEdit" @click="editChart">編輯圖表</button>
                <button v-if="localCanDelete" @click="deleteChart">刪除圖表</button>
            </div>
            <div v-if="localCanExport" class="export-button">
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
      @reload-charts="$emit('reload-charts')"

    />
  </div>
</template>

<script>
import axios from 'axios';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartModal from '@/components/backend/ChartModal.vue';
import { mapGetters } from 'vuex';

export default {
  components: {
    PlotlyChart,
    ChartModal
  },
  props: {
    chartConfig: Object,
    isFrontend: Boolean,
    canExport: Boolean,
    canDelete: Boolean,
    canEdit: Boolean // 新增 canEdit prop
  },
  data() {
    return {
      showMenu: false,
      isZoomModalVisible: false,
      isEditModalVisible: false,
      localChartConfig: { ...this.chartConfig },
      // 删除以下三行，避免与 computed 中的同名属性冲突
      // localCanExport: this.canExport,
      // localCanDelete: this.canDelete,
      // localCanEdit: this.canEdit,
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    localCanEdit() {
      return this.hasPermission(this.localChartConfig.name, 'can_edit');
    },
    localCanDelete() {
      return this.hasPermission(this.localChartConfig.name, 'can_delete');
    },
    localCanExport() {
      return this.hasPermission(this.localChartConfig.name, 'can_export');
    },
  },
  methods: {
    handleReloadCharts() {
      this.$emit('reload-charts');
    },
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
      const confirmation = confirm('確定要刪除此圖表嗎？');
      if (confirmation) {
        try {
          await axios.post(`/api/backend/delete-chart/${this.localChartConfig.id}/`);
          alert('圖表已刪除');
          await this.$store.dispatch('fetchPermissions'); // 刷新权限
          this.$emit('reload-charts'); // 发出事件
        } catch (error) {
          console.error('刪除此圖表時出錯:', error);
          alert('刪除失敗，請稍後再試。');
        }
      }
    },
    updateChartConfig(updatedConfig) {
      this.localChartConfig = updatedConfig;
    },
    async exportChart(format) {
      try {
        const response = await axios.post('/api/backend/export-data/', {
          chartConfig: {
            chart_type: this.localChartConfig.chartType,
            name: this.localChartConfig.name,
            data_source: this.localChartConfig.dataSource,
            x_axis_field: this.localChartConfig.xAxisField,
            y_axis_field: this.localChartConfig.yAxisField,
            filter_conditions: this.localChartConfig.filter_conditions,
          },
          format: format,
          export_all: true  // 新增此行，设置为导出全部字段
        }, { responseType: 'blob' });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.localChartConfig.name || 'exported-file'}.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error('導出數據時出錯:', error);
        alert('導出失敗，請檢查數據並重試。');
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

        // 调用 dynamic-chart-data 以获取 x_data 和 y_data
        const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: data.data_source,
          x_field: data.x_axis_field,
          y_field: data.y_axis_field,
          filter_conditions: JSON.parse(data.filter_conditions || '{}'),
          join_fields: data.join_fields || []
        });

        const updatedConfig = {
          ...data,
          chartType: data.chart_type ? data.chart_type.toLowerCase() : 'bar', // 添加 chartType
          x_data: dataResponse.data.x_data,
          y_data: dataResponse.data.y_data,
          last_updated: dataResponse.data.last_updated ? new Date(dataResponse.data.last_updated) : null,
          can_export: this.hasPermission(data.name, 'can_export'),
          can_delete: this.hasPermission(data.name, 'can_delete'),
          can_edit: this.hasPermission(data.name, 'can_edit'),
        };

        return updatedConfig;
      } catch (error) {
        console.error('加載圖表配置時發生錯誤:', error);
        alert('加載圖表配置時發生錯誤，請稍後再試');
        return null;
      }
    },
    hasPermission(permissionName, action) {
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
    slugify(text) {
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w-]+/g, '')       // 移除不必要的字符
        .replace(/--+/g, '-')          // 移除重复的连字符
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    }
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
  color: white;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  font-size: 2rem;
  cursor: pointer;
  border-radius: 50%;
  padding: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
</style>
