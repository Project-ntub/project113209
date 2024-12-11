<!-- src/Charts/ChartContainer.vue -->
<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <!-- 菜單按鈕，包含更多操作選項 -->
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <!-- 縮放按鈕，打開縮放視窗 -->
          <button class="zoom-icon" @click="openZoomModal">
            <font-awesome-icon icon="search-plus" />
          </button>
          <!-- 菜單內容，根據權限顯示不同的操作按鈕 -->
          <div v-if="showMenu" class="menu">
            <div v-if="!isFrontend">
                <!-- 編輯和刪除按鈕，只對後台用戶顯示 -->
                <button v-if="localCanEdit" @click="editChart">編輯圖表</button>
                <button v-if="localCanDelete" @click="deleteChart">刪除圖表</button>
            </div>
            <div v-if="localCanExport" class="export-button">
                <!-- 匯出按鈕，支援多種格式 -->
                <button @click="exportChart('csv')">匯出 CSV</button>
                <button @click="exportChart('excel')">匯出 Excel</button>
                <button @click="exportChart('pdf')">匯出 PDF</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 使用 PlotlyChart 組件來渲染圖表 -->
      <PlotlyChart :chartConfig="localChartConfig" />
      
      <!-- 縮放圖表的視窗 -->
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

  <ExportFilterModal 
    v-if="isExportModalVisible"
    :chartConfig="localChartConfig"
    @close="isExportModalVisible = false"
    @export="handleExport"
  />
</template>

<script>
import axios from 'axios';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartModal from '@/components/backend/ChartModal.vue';
import ExportFilterModal from '@/components/backend/ExportFilterModal.vue';
import { mapGetters } from 'vuex';

export default {
  components: {
    PlotlyChart,
    ChartModal,
    ExportFilterModal 
  },
  props: {
    chartConfig: Object, // 接收圖表配置
    isFrontend: Boolean, // 判斷是否為前台儀表板
    canExport: Boolean, // 是否有匯出權限
    canDelete: Boolean, // 是否有刪除權限
    canEdit: Boolean // 是否有編輯權限
  },
  data() {
    return {
      showMenu: false, // 控制菜單的顯示與隱藏
      isZoomModalVisible: false, // 控制縮放視窗的顯示與隱藏
      isEditModalVisible: false, // 控制編輯視窗的顯示與隱藏
      isExportModalVisible: false, // 控制匯出篩選視窗
      exportFormat: '', // 紀錄當前要匯出的格式
      localChartConfig: { ...this.chartConfig }, // 本地圖表配置，方便修改
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    // 計算當前用戶是否有編輯權限
    localCanEdit() {
      return this.hasPermission(this.localChartConfig.name, 'can_edit');
    },
    // 計算當前用戶是否有刪除權限
    localCanDelete() {
      return this.hasPermission(this.localChartConfig.name, 'can_delete');
    },
    // 計算當前用戶是否有匯出權限
    localCanExport() {
      return this.hasPermission(this.localChartConfig.name, 'can_export');
    },
  },
  methods: {
    handleReloadCharts() {
      // 處理重新載入圖表的事件
      this.$emit('reload-charts');
    },
    toggleMenu() {
      // 切換菜單的顯示狀態
      this.showMenu = !this.showMenu;
    },
    openZoomModal() {
      // 打開縮放視窗
      this.isZoomModalVisible = true;
    },
    closeZoomModal() {
      // 關閉縮放視窗
      this.isZoomModalVisible = false;
    },
    editChart() {
      // 打開編輯圖表的視窗，並隱藏菜單
      this.isEditModalVisible = true;
      this.showMenu = false;
    },
    closeEditModal() {
      // 關閉編輯圖表的視窗
      this.isEditModalVisible = false;
    },
    async deleteChart() {
      // 刪除圖表的函數
      if (!this.localChartConfig.id) {
        alert('圖表ID無效，無法刪除');
        return;
      }
      const confirmation = confirm('確定要刪除此圖表嗎？'); // 確認刪除
      if (confirmation) {
        try {
          // 發送刪除請求到後端
          await axios.post(`/api/backend/delete-chart/${this.localChartConfig.id}/`);
          alert('圖表已刪除');
          await this.$store.dispatch('fetchPermissions'); // 刷新權限
          this.$emit('reload-charts'); // 發出重新載入圖表的事件
        } catch (error) {
          console.error('刪除此圖表時出錯:', error);
          alert('刪除失敗，請稍後再試。');
        }
      }
    },
    updateChartConfig(updatedConfig) {
      // 更新本地圖表配置
      this.localChartConfig = updatedConfig;
    },
    async exportChart(format) {
      // 不直接匯出，先顯示篩選視窗
      this.exportFormat = format;
      this.isExportModalVisible = true;
    },
    async handleExport(filters) {
      console.log('handleExport triggered with filters:', filters);
      // 使用者在 ExportFilterModal 輸入的篩選條件
      this.isExportModalVisible = false;
      try {
        const response = await axios.post('/api/backend/export-data/', {
          chartConfig: {
            chart_type: this.localChartConfig.chartType,
            name: this.localChartConfig.name,
            data_source: this.localChartConfig.dataSource,
            x_axis_field: this.localChartConfig.xAxisField,
            y_axis_field: this.localChartConfig.yAxisField,
            filter_conditions: filters, // 使用使用者選擇的過濾條件
            // 添加新的圖表類型所需的額外配置
            labels: this.localChartConfig.labels,
            parents: this.localChartConfig.parents,
            values: this.localChartConfig.values,
          },
          format: this.exportFormat,
          export_all: true
        }, { responseType: 'blob' });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.localChartConfig.name || 'exported-file'}.${this.exportFormat}`);
        document.body.appendChild(link);
        link.click();
        link.remove();

        this.$emit('export-history', {
          chartName: this.localChartConfig.name,
          format: this.exportFormat,
          timestamp: new Date().toLocaleString()
        });
      } catch (error) {
        console.error('導出數據時出錯:', error);
        alert('導出失敗，請檢查數據並重試。');
      }
    },
    async fetchChartConfigMethod(chartId) {
      // 獲取圖表配置的方法
      if (!chartId) {
        console.error('chartId is undefined');
        alert('無效的圖表 ID，無法加載圖表配置');
        return null;
      }
      try {
        const response = await axios.get(`/api/backend/charts/${chartId}/`);
        const data = response.data;

        // 呼叫 dynamic-chart-data 以獲取 x_data 和 y_data
        const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: data.data_source,
          x_field: data.x_axis_field,
          y_field: data.y_axis_field,
          filter_conditions: JSON.parse(data.filter_conditions || '{}'),
          join_fields: data.join_fields || []
        });

        // 更新圖表配置
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
      // 檢查用戶是否有特定權限
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
    slugify(text) {
      // 將文本轉換為 slug 格式
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-') // 替換空格為連字符
        .replace(/[^\w-]+/g, '')       // 移除不必要的字符
        .replace(/--+/g, '-')          // 移除重複的連字符
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    }
  },
};
</script>

<style scoped>
/* .chart-container {
  position: relative;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* 圖表容器樣式
} */

.chart-header {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10; /* 確保標頭在最上層 */
}

.menu-button {
  position: relative;
  z-index: 11;
}

.menu-icon, .zoom-icon {
  background: rgba(255, 255, 255, 0.8); /* 按鈕背景透明度 */
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
  background-color: #3498db; /* 菜單背景色 */
  border: 1px solid #2980b9; /* 菜單邊框色 */
  border-radius: 5px;
  width: 150px;
  z-index: 12;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); /* 菜單陰影 */
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
  background-color: #2980b9; /* 滑鼠懸停時的背景色 */
}

.zoom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7); /* 縮放視窗背景色 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000; /* 確保縮放視窗在最上層 */
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
  background: rgba(0, 0, 0, 0.5); /* 關閉按鈕背景色 */
  border: none;
  font-size: 2rem;
  cursor: pointer;
  border-radius: 50%;
  padding: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
</style>
